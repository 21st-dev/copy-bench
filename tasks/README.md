# Copy Bench

Can a model rebuild a moving web component from a screen recording? The agent gets an 8 second video of a page
(WebGL scenes, shaders, canvas animations, mouse-driven effects) and has to write one `index.html` that looks and
moves the same.

This is the public subset: 13 of the 50 tasks. The other 37 stay private so the benchmark stays useful.

- Results, every copy next to its original: https://21st.dev/benchmarks/copy
- Method: https://21st.dev/benchmarks/copy/method
- Code and grader: https://github.com/21st-dev/copy-bench

## Results so far

16 models on all 50 tasks. The best, GPT-6.2 Astra, scores 92.4 out of 100 with a browser and 89.1 without. Most
models land between 35 and 70, and motion is the hardest of the five dimensions.

## Run it

```bash
export ANTHROPIC_API_KEY=...        # the agent and the judge both use it

harbor run -d 21st/copy-bench -a claude-code -m anthropic/claude-opus-5-5 --n-tasks 1   # one task
harbor run -d 21st/copy-bench -a claude-code -m anthropic/claude-opus-5-5 -n 4          # all 13
```

## How a task works

Two steps in the same sandbox:

1. **first** (one-shot, 30 min): the agent gets `video.mp4`, the mouse/scroll script used in the recording, and
   `cb-frames` to pull frames out of the video. There's no browser, so it copies blind.
2. **fix** (self-verified, 20 min): a headless browser gets unlocked, and the agent can open its own page, compare it
   with the recording, and fix it.

After each step the grader renders the copy in headless Chromium, replays the same input, and a vision judge rates it
against a fixed rubric: 26 criteria in five dimensions (content, layout, motion, color, typography), each rated same,
minor or major. The score is computed in code from those ratings. The task reward is the score of the last step,
from 0 to 1.

The judge uses `ANTHROPIC_API_KEY` (default `claude-opus-5-5`) or `OPENAI_API_KEY` (default `gpt-6.1-sol`); set
`COPY_BENCH_JUDGE_MODEL` for a different one. Without a key the run finishes ungraded.

## Good to know

- WebGL renders in software in the sandbox, so a correct WebGL copy can look a little different from the reference,
  which was recorded with a GPU. The judge is told.
- The leaderboard on 21st.dev uses a panel of two judges from different labs on full recordings, plus integrity
  checks that zero a copy for reusing the original's code or replaying the recording, and it was validated against
  249 hand-scored copies. This in-run grader uses the same rubric and scoring with one judge on 4 frames and no
  integrity checks, so expect close numbers, not equal ones.
