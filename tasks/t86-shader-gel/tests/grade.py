#!/usr/bin/env python3
"""Copy Bench verifier: render the agent's /workspace/index.html, put it next to the original, ask one vision judge.

Runs inside the task sandbox after each step (tests/test.sh calls it). Standard library only.

  1. No index.html -> reward 0.
  2. No judge key (ANTHROPIC_API_KEY / OPENAI_API_KEY empty) -> reward 1 for "a file exists", graded=0. Ungraded mode,
     said so in grade.log, so a run without the secret still finishes.
  3. Otherwise: unpack Chromium from the image's encrypted archive into a temp dir, serve /workspace, capture the copy
     at the same timestamps as the reference frames in tests/ref/ (capture.mjs, same viewport + input script as the
     original), build one contact sheet (original left, copy right, one row per timestamp), ask the judge the fixed
     checklist, score it in code (v10: same / minor / major per check), reward = overall / 100.
     Any failure after the key check (no browser, capture crash, judge error) -> reward 0 and the reason in grade.log,
     so breaking the grader never pays.

Writes /logs/verifier/reward.json ({"reward": .., per-dimension scores, "graded": 0|1}), judge.json, sheet.jpg.
"""
import base64, functools, glob, http.server, json, os, re, shutil, socketserver, subprocess, sys, tempfile, threading
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
WS = Path(os.environ.get("CB_WORKSPACE", "/workspace"))
OUT = Path(os.environ.get("CB_OUT", "/logs/verifier"))
BLOB = Path("/usr/lib/locale/C.utf8/LC_COLLATE.cache")
STEP = os.environ.get("CB_STEP", "")
LOG = []

sys.path.insert(0, str(HERE))
from checklist import CHECKS, STILL_CHECK, WEIGHTS, PENALTY  # noqa: E402


def log(msg):
    LOG.append(msg)
    print(msg, flush=True)


def finish(reward, extra=None):
    OUT.mkdir(parents=True, exist_ok=True)
    data = {"reward": round(float(reward), 4), **(extra or {})}
    (OUT / "reward.json").write_text(json.dumps(data))
    (OUT / "grade.log").write_text("\n".join(LOG) + "\n")
    print(json.dumps(data))
    sys.exit(0)


def export_copy():
    """Keep the copy (and the assets it uses) in the verifier logs, like the lab's export step."""
    OUT.mkdir(parents=True, exist_ok=True)
    shutil.copy(WS / "index.html", OUT / "index.html")
    assets = WS / "assets"
    if assets.is_dir():
        shutil.copytree(assets, OUT / "assets", dirs_exist_ok=True)


def find_chrome(tmp):
    if os.environ.get("CB_CHROME"):  # local testing only (the sandbox never sets it)
        return os.environ["CB_CHROME"]
    """Fresh copy of the image's Chromium, decrypted from the archive with the key in tests/ (never from the
    agent-writable /opt/ab, which the agent could have swapped)."""
    key = HERE / "browser.key"
    if not BLOB.is_file() or not key.is_file():
        raise RuntimeError("the browser archive or its key is missing")
    dec = subprocess.run(["openssl", "enc", "-d", "-aes-256-cbc", "-pbkdf2", "-pass", f"file:{key}", "-in", str(BLOB)],
                         capture_output=True, check=True).stdout
    subprocess.run(["tar", "-C", str(tmp), "-xzf", "-"], input=dec, check=True)
    found = [p for p in glob.glob(f"{tmp}/opt/ab/pw/**/chrome", recursive=True) if os.path.isfile(p)]
    if not found:
        raise RuntimeError("no chrome binary in the browser archive")
    return found[0]


def serve(root):
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    handler = functools.partial(Quiet, directory=str(root))
    httpd = socketserver.ThreadingTCPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


def contact_sheet(pairs, out):
    """pairs: [(label, ref.jpg, copy.jpg)] -> one JPEG, each row = ORIGINAL | COPY at 640x400, labelled."""
    font = next((f for f in ["/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                             "/System/Library/Fonts/Supplemental/Arial Bold.ttf"] if os.path.exists(f)), None)
    ff = f"fontfile='{font}':" if font else ""
    inputs, chains = [], []
    for i, (label, ref, cp) in enumerate(pairs):
        inputs += ["-i", ref, "-i", cp]
        for side, j, name in (("o", 2 * i, "ORIGINAL"), ("c", 2 * i + 1, "COPY")):
            chains.append(f"[{j}:v]scale=640:400,drawtext={ff}text='{name} {label}':x=8:y=8:fontsize=20:"
                          f"fontcolor=white:box=1:boxcolor=black@0.7:boxborderw=4[{side}{i}]")
        chains.append(f"[o{i}][c{i}]hstack=inputs=2[r{i}]")
    rows = "".join(f"[r{i}]" for i in range(len(pairs)))
    chains.append(f"{rows}vstack=inputs={len(pairs)}[out]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(chains),
                    "-map", "[out]", "-q:v", "3", str(out)], check=True)


def checklist(mode):
    out = {d: list(c) for d, c in CHECKS.items() if d != "motion"}
    out["motion"] = list(CHECKS["motion"]) if mode == "full" else [STILL_CHECK]
    return out


def make_prompt(meta, labels, mode):
    lines = []
    for d, checks in checklist(mode).items():
        lines.append(f"  {d}:")
        lines += [f"  - {cid}: {text}" for cid, text in checks]
    note, varies = meta.get("note", ""), meta.get("varies", "")
    task_note = f"What the original is (from the task author): {note}" if note else ""
    if varies:
        task_note += (f"\nWhat differs between any two loads of this original, even the original against itself: "
                      f"{varies.strip().rstrip('.')}. Differences of that kind are not differences in any dimension.")
    return (HERE / "prompt.md").read_text().format(
        timestamps=", ".join(labels), checklist="\n".join(lines), task_note=task_note)


def call_judge(prompt, image_b64):
    akey, okey = os.environ.get("ANTHROPIC_API_KEY", ""), os.environ.get("OPENAI_API_KEY", "")
    if akey:
        model = os.environ.get("JUDGE_MODEL") or "claude-opus-5-5"
        body = {"model": model, "max_tokens": 4000, "messages": [{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image_b64}},
            {"type": "text", "text": prompt}]}]}
        req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=json.dumps(body).encode(), headers={
            "x-api-key": akey, "anthropic-version": "2023-06-01", "content-type": "application/json"})
        with urllib.request.urlopen(req, timeout=240) as r:
            resp = json.load(r)
        text = "".join(b.get("text", "") for b in resp.get("content", []) if b.get("type") == "text")
    else:
        model = os.environ.get("JUDGE_MODEL") or "gpt-6.1-sol"
        body = {"model": model, "response_format": {"type": "json_object"}, "messages": [{"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}}]}]}
        req = urllib.request.Request("https://api.openai.com/v1/chat/completions", data=json.dumps(body).encode(),
                                     headers={"authorization": f"Bearer {okey}", "content-type": "application/json"})
        with urllib.request.urlopen(req, timeout=240) as r:
            resp = json.load(r)
        text = resp["choices"][0]["message"]["content"]
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise RuntimeError(f"the judge returned no JSON: {text[:300]}")
    return model, json.loads(m.group(0))


def score(res, mode):
    """v10 scoring from the lab grader: each dimension = 100 - 15 per minor - 40 per major (n/a skipped)."""
    ids = {c.get("id"): c for c in res.get("checks", []) if isinstance(c, dict)}
    dims = {}
    for d, checks in checklist(mode).items():
        r = [ids.get(cid, {}).get("result", "major") for cid, _ in checks]
        app = [x for x in r if x != "n/a"]
        dims[d] = None if not app else max(0, 100 - sum(PENALTY.get(x, 40) for x in app))
    if mode == "still" and dims.get("motion") == 100:
        dims["motion"] = None
    used = {k: w for k, w in WEIGHTS.items() if dims.get(k) is not None}
    overall = round(sum(dims[k] * w for k, w in used.items()) / sum(used.values()), 1) if used else 0.0
    return dims, overall


def main():
    meta = json.loads((HERE / "meta.json").read_text())
    kind_key = f"kind_{meta.get('kind', 'other')}"
    if not (WS / "index.html").is_file() or (WS / "index.html").stat().st_size == 0:
        log("no /workspace/index.html: reward 0")
        finish(0, {"graded": 0, kind_key: 0})
    export_copy()
    dry = os.environ.get("CB_JUDGE_DRY_RUN") == "1"  # local testing: everything but the paid judge call
    if not dry and not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("OPENAI_API_KEY")):
        log("UNGRADED: no judge key (set ANTHROPIC_API_KEY or OPENAI_API_KEY through [verifier.env] from a run secret). "
            "Reward is 1 because index.html exists. Score the exported copy offline instead.")
        finish(1, {"graded": 0})
    refs = sorted(glob.glob(str(HERE / "ref" / "*ms.jpg")))
    times = [int(re.search(r"(\d+)ms", Path(p).name).group(1)) for p in refs]
    mode = "full" if meta.get("moves", True) else "still"
    tmp = Path(tempfile.mkdtemp(prefix="cbv-"))
    try:
        chrome = find_chrome(tmp)
        site = tmp / "site"
        shutil.copytree(WS, site, ignore=shutil.ignore_patterns("video.mp4", "more-frames", "shots", "node_modules"))
        httpd = serve(site)
        shots = tmp / "shots"
        cap = subprocess.run(["node", str(HERE / "capture.mjs"), "--chrome", chrome, "--url",
                              f"http://127.0.0.1:{httpd.server_address[1]}/index.html", "--steps", str(HERE / "steps.json"),
                              "--times", ",".join(map(str, times)), "--out", str(shots)],
                             capture_output=True, text=True, timeout=180)
        httpd.shutdown()
        if cap.returncode != 0:
            raise RuntimeError(f"capture failed: {cap.stderr[-500:]}")
        timing = json.loads((shots / "capture.json").read_text())["shots"]
        log("captured: " + ", ".join(f"{s['target_ms']}ms (shot at {s['shot_ms']})" for s in timing))
        labels = [f"{t / 1000:g} s" for t in times]
        pairs = [(lab, ref, str(shots / Path(ref).name)) for lab, ref in zip(labels, refs)]
        contact_sheet(pairs, OUT / "sheet.jpg")
        for p in shots.glob("*.jpg"):
            shutil.copy(p, OUT / f"copy-{p.name}")
        prompt = make_prompt(meta, labels, mode)
        (OUT / "prompt.txt").write_text(prompt)
        if dry:
            log("dry run: sheet and prompt written, judge not called")
            finish(0, {"graded": 0, "dry_run": 1})
        model, res = call_judge(prompt, base64.b64encode((OUT / "sheet.jpg").read_bytes()).decode())
        dims, overall = score(res, mode)
        (OUT / "judge.json").write_text(json.dumps({"model": model, "step": STEP, "mode": mode, "dims": dims,
                                                    "overall": overall, "answer": res}, indent=1))
        log(f"judge {model}: overall {overall} dims {dims}")
        extra = {"graded": 1, kind_key: overall / 100}
        extra.update({d: v / 100 for d, v in dims.items() if v is not None})
        finish(overall / 100, extra)
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001
        log(f"GRADING FAILED, reward 0: {type(e).__name__}: {e}")
        finish(0, {"graded": 0, "grading_error": 1, kind_key: 0})
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
