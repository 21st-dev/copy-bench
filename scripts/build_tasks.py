#!/usr/bin/env python3
"""Build tasks/ (the Valkyrie dataset) from the private Copy Bench lab checkout. Read-only on the lab.

  python3 scripts/build_tasks.py --lab ~/Develop/21/21st-lab/copy-bench

Each task: the lab's two-step Harbor task (harbor-2step/<id>-video) with solutions dropped, one shared tests/ folder
(grader/ + 4 reference frames + the input script + task metadata) and a task.toml Valkyrie validates.
"""
import argparse, json, shutil, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IDS = ["t84", "t19", "t20", "t31", "t48", "t49", "t52", "t71", "t86", "t87", "t88", "t67", "t72"]
REF_MS = [1000, 3000, 5000, 7000]
GRADER = ["grade.py", "capture.mjs", "checklist.py", "prompt.md", "test.sh"]
ALLOWED_HOSTS = ["openrouter.ai", "api.anthropic.com", "api.openai.com", "generativelanguage.googleapis.com",
                 "api.x.ai", "esm.sh", "unpkg.com", "cdn.jsdelivr.net", "cdnjs.cloudflare.com"]

TOML = """schema_version = "1.4"
multi_step_reward_strategy = "final"

[task]
name = "copy-bench/{tid}"
version = "1.0.0"
description = "Copy a moving web page from an 8 s screen recording into one index.html, then check it in a browser and fix it."
keywords = ["ui-copy", "frontend", "{kind}", "video", "two-step"]

[metadata]
copy_bench_id = "{tid}"
kind = "{kind}"
motion = "{motion}"
source = "{source}"

[verifier]
timeout_sec = 600.0
environment_mode = "shared"

[verifier.env]
# The judge key comes from a run secret. Missing secret -> empty -> ungraded mode (reward 1 if index.html exists).
ANTHROPIC_API_KEY = "${{anthropic-api-key:-}}"
OPENAI_API_KEY = "${{openai-api-key:-}}"
JUDGE_MODEL = "${{copy-bench-judge-model:-}}"

[agent]
timeout_sec = 1800.0
network_mode = "allowlist"
allowed_hosts = {hosts}

[environment]
network_mode = "public"
build_timeout_sec = 1800.0
workdir = "/workspace"
cpus = 2
memory_mb = 4096

# Step 1, one-shot: 30 min, no browser in the sandbox.
[[steps]]
name = "first"

[steps.agent]
timeout_sec = 1800.0

[steps.verifier.env]
CB_STEP = "first"

# Step 2, self-verified: same sandbox, the browser is unpacked by steps/fix/workdir/setup.sh, 20 min.
[[steps]]
name = "fix"

[steps.agent]
timeout_sec = 1200.0

[steps.verifier.env]
CB_STEP = "fix"
"""

SETUP = """#!/bin/bash
# Step 2 setup: stop anything left over from step 1, unpack the browser, then remove the key and this file.
# The encrypted archive stays in place: the verifier decrypts its own fresh copy from it.
set -e
cd "$(dirname "$0")"
for n in claude codex gemini grok opencode goose aider pi mini-swe-agent terminus; do pkill -9 -f "(^|/)$n( |$)" 2>/dev/null || true; done
pkill -9 -f "node .*(claude|codex|gemini|opencode)" 2>/dev/null || true
sleep 1
openssl enc -d -aes-256-cbc -pbkdf2 -pass file:.k -in /usr/lib/locale/C.utf8/LC_COLLATE.cache | tar -C / -xzf -
ln -sf /opt/ab/agent-browser /usr/local/bin/agent-browser
rm -f .k setup.sh
mkdir -p shots
agent-browser --version >/dev/null
"""


def build(lab: Path, out: Path, short: str) -> dict:
    src = next((lab / "harbor-2step").glob(f"{short}-*-video"))
    tid = src.name.removesuffix("-video")
    task = json.loads((next((lab / "tasks").glob(f"{short}-*")) / "task.json").read_text())
    lab_task = lab / "tasks" / task["id"]
    dst = out / tid
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True)

    shutil.copytree(src / "environment", dst / "environment")
    for step in ("first", "fix"):
        (dst / "steps" / step).mkdir(parents=True)
        shutil.copy(src / "steps" / step / "instruction.md", dst / "steps" / step / "instruction.md")
    wd = dst / "steps" / "fix" / "workdir"
    wd.mkdir()
    shutil.copy(src / "steps" / "fix" / "workdir" / ".k", wd / ".k")
    (wd / "setup.sh").write_text(SETUP)
    (wd / "setup.sh").chmod(0o755)

    tests = dst / "tests"
    tests.mkdir()
    for f in GRADER:
        shutil.copy(ROOT / "grader" / f, tests / f)
    (tests / "test.sh").chmod(0o755)
    shutil.copy(src / "steps" / "fix" / "workdir" / ".k", tests / "browser.key")
    steps = src / "environment" / "workspace" / "steps.json"
    (tests / "steps.json").write_text(steps.read_text() if steps.is_file() else "[]\n")
    (tests / "ref").mkdir()
    frames = {int(p.stem.split("_")[1].removesuffix("ms")): p for p in (lab_task / "ref" / "frames").glob("*ms.png")}
    for want in REF_MS:  # nearest reference frame (a few recordings are shorter than 8 s)
        ms = min(frames, key=lambda t: abs(t - want))
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(frames[ms]), "-q:v", "3",
                        str(tests / "ref" / f"{ms:05d}ms.jpg")], check=True)
    meta = {"id": tid, "kind": task.get("kind"), "motion": task.get("motion"),
            "moves": task.get("motion") != "static", "note": task.get("notes", ""),
            "varies": task.get("nondeterministic") or ""}
    (tests / "meta.json").write_text(json.dumps(meta, indent=1))

    (dst / "task.toml").write_text(TOML.format(tid=tid, kind=task.get("kind"), motion=task.get("motion"),
                                               source=task.get("source", ""), hosts=json.dumps(ALLOWED_HOSTS)))
    return {"id": tid, "kind": task.get("kind"), "motion": task.get("motion"), "source": task.get("source")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lab", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=ROOT / "tasks")
    a = ap.parse_args()
    a.out.mkdir(exist_ok=True)
    rows = [build(a.lab, a.out, s) for s in IDS]
    print(json.dumps(rows, indent=1))


if __name__ == "__main__":
    main()
