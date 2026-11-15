#!/bin/bash
# Copy Bench verifier. Renders /workspace/index.html, compares it with the original's frames, asks one vision judge.
# Reward lands in /logs/verifier/reward.json. Details: tests/grade.py.
mkdir -p /logs/verifier
/usr/bin/python3 /tests/grade.py 2>&1 | tee /logs/verifier/grade.out
if [ ! -s /logs/verifier/reward.json ]; then
  echo '{"reward": 0, "graded": 0, "grading_error": 1}' > /logs/verifier/reward.json
fi
exit 0
