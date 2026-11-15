# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Copy Bench dataset score, offline. It follows Valkyrie's metric.py contract, but the hosted Valkyrie refuses custom
scoring, so it lives here instead of in tasks/. Hosted runs report the plain mean of "reward", which is the same headline.
  uv run --script scripts/metric.py -i rewards.jsonl -o score.json
Each input line is one task's rewards (or null when the task errored). The headline is "reward": the mean over all
tasks, errors count as 0 (Valkyrie shows it x100). Also reported: the mean of each checklist dimension (content,
layout, color, typography, motion) over graded tasks, the mean per task kind (kind_3d, kind_shader, ...) and the share
of tasks that were really judged (graded_share; below 1 means some ran without the judge secret)."""
import argparse, json

ap = argparse.ArgumentParser()
ap.add_argument("-i", required=True)
ap.add_argument("-o", required=True)
a = ap.parse_args()

rows = [json.loads(line) for line in open(a.i) if line.strip()]
n = len(rows) or 1
out = {"reward": sum((r or {}).get("reward", 0.0) for r in rows) / n,
       "graded_share": sum((r or {}).get("graded", 0.0) for r in rows) / n}
keys = sorted({k for r in rows if r for k in r if k not in ("reward", "graded", "grading_error")})
for k in keys:
    vals = [r[k] for r in rows if r and k in r]
    out[k] = sum(vals) / len(vals)
json.dump(out, open(a.o, "w"), indent=1)
