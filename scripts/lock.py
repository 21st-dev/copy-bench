"""Write tasks/dataset.toml (task names + digests; no metric.py, the hosted Valkyrie refuses custom scoring) and run the CLI's own pre-push checks.

Run it with the Python that ships with the Valkyrie CLI, so the digests match what `valkyrie dataset push` computes:

  ~/.local/share/uv/tools/valkyrie-cli/bin/python scripts/lock.py
"""
import sys, tempfile, tomllib
from pathlib import Path

from valkyrie.sdk.dataset_manifest import check_digests, check_script, lock_folders, read_manifest
from valkyrie.sdk.task_archive import find_task_folders, pack_task, task_problems
from valkyrie.sdk.task_content import left_out, task_digest

ROOT = Path(__file__).resolve().parent.parent / "tasks"
folders = find_task_folders(ROOT)
bad = False
tasks = []
for tid, path in folders.items():
    problems = task_problems(path)
    skipped = left_out(path)
    name = tomllib.loads((path / "task.toml").read_text())["task"]["name"]
    digest = task_digest(path)
    with tempfile.TemporaryDirectory() as tmp:
        pack_task(path, Path(tmp) / "t.zip")
        size = (Path(tmp) / "t.zip").stat().st_size
    print(f"{tid}: {'OK' if not problems else 'PROBLEMS ' + str(problems)}; {size / 1e6:.1f} MB packed; "
          f"left out: {skipped or 'nothing'}")
    bad |= bool(problems)
    tasks.append((name, digest))

lines = ['[dataset]', 'name = "copy-bench/copy-bench"', 'version = "v1"',
         'description = "Copy Bench public subset: copy a moving web page from a screen recording, one-shot then self-verified in a browser."',
         'keywords = ["ui-copy", "frontend", "vision", "multi-step"]', '',
         '[[dataset.authors]]', 'name = "21st.dev"', '']
for name, digest in tasks:
    lines += ["[[tasks]]", f'name = "{name}"', f'digest = "{digest}"', ""]
(ROOT / "dataset.toml").write_text("\n".join(lines))

manifest = read_manifest(ROOT)
check_script(manifest, None)
locked = lock_folders(manifest, folders, ROOT)
check_digests(locked, {tid: task_digest(p) for tid, p in locked.folders.items()})
print(f"dataset.toml: {len(locked.folders)} tasks locked, unlisted: {locked.unlisted or 'none'}, tag: {locked.tag}")
sys.exit(1 if bad else 0)
