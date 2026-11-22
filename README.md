# Copy Bench

Copy Bench measures how well models rebuild complex web components from a screen recording: WebGL, shaders and multi-step interactive animations.

Results, with every copy next to its original: **https://21st.dev/benchmarks/copy**
Method: **https://21st.dev/benchmarks/copy/method**

## How it works

Copy Bench measures how well a model can rebuild a moving web component from a screen recording. The agent gets an
8 second video of a page (WebGL scenes, shaders, canvas animations, mouse-driven effects) and has to write one
`index.html` that looks and moves the same.

This repo is a public subset of Copy Bench (13 of the 50 tasks), packaged as a
[Harbor](https://harborframework.com) dataset you can run as is:
[`21st/copy-bench`](https://hub.harborframework.com/datasets/21st/copy-bench).

## Why frontier models still get it wrong

We ran 16 models on all 50 tasks (800 copies per step, 1,600 in total). The best model gets 92.4 out of 100 when it can
check its work in a browser, and 89.1 when it can't. Most models land between 35 and 70. The hard part is motion:
models get the colors and the layout roughly right, then miss how fast things spin, how a shape morphs, what happens
under the mouse, or what a shader actually looks like over time.

| Model | Harness | One-shot | Self-verified |
|---|---|---:|---:|
| GPT-6.2 Astra | Codex | 89.1 | 92.4 |
| GPT-6.2 Sol | Codex | 84.1 | 88.4 |
| GPT-6 Astra | Codex | 76.9 | 86.7 |
| GPT-6.1 Sol | Codex | 75.6 | 82.2 |
| Claude Fable 5.2 | Claude Code | 62.4 | 69.0 |
| Gemini 4 Carbon | Gemini CLI | 57.0 | 67.2 |
| GPT-6 Sol | Codex | 57.3 | 64.5 |
| Claude Opus 5.5 | Claude Code | 50.1 | 59.1 |
| Qwen 4 Max | Qwen Code | 45.4 | 54.4 |
| Muse Wonder 1.0 | Muse Code | 41.3 | 51.9 |
| Qwen 3.8 Max Prime | Qwen Code | 41.2 | 50.1 |
| Kimi K3.1 Pro | Kimi Code | 34.6 | 46.6 |
| MiniMax M3 | MiniMax Code | 33.3 | 41.9 |
| Grok 4.7 | Grok Build | 30.3 | 39.2 |
| Claude Sonnet 5.5 | Claude Code | 28.1 | 35.8 |
| MiMo V2.6 Pro | MiMo | 16.4 | 18.9 |

![One-shot vs self-verified score per model](docs/results.png)

Scores are on all 50 tasks, the mean of two judges from different labs (GPT-6.1 Sol and Claude Opus 5.5). Letting the
model look at its own page in a browser raised the score on 507 of 799 copies and lowered it on 124.

Each model ran in its maker's own agent harness (Codex, Claude Code, Gemini CLI, ...), because that's how people
actually use these models for frontend work, and it keeps us from handicapping a model with a harness it wasn't tuned
for. On Harbor the same tasks run with any agent it ships, for example Claude Code or Codex.

## Failure modes

- **Rebuilding the wrong thing, confidently.** Weaker copies get the vibe and miss the content. Below, the same
  task (Neon Loop, 3D rings of letters) copied by GPT-6 Astra and by MiMo V2.6 Pro, as the in-run grader sees it.
  MiMo's copy is a blown-out glow with no letters at all. Some models also rebuild a famous demo they remember
  instead of what the video shows.
- **Checking your own work doesn't always help.** Self-verifying raised the score on 507 of 799 copies, but lowered
  it on 124: the model "fixes" things that were right, or breaks the page while editing.
- **Copies that never render.** 155 of the 1,600 steps hit the time limit, and 31 left no `index.html` at all.

GPT-6 Astra (close copy):

![GPT-6 Astra copy of t84](docs/t84-gpt-6-astra.jpg)

MiMo V2.6 Pro (letters gone, only the glow is left):

![MiMo V2.6 Pro copy of t84](docs/t84-mimo-v2.6-pro.jpg)

## How the published scores were judged

The numbers above come from our offline evaluation, described in full on the
[method page](https://21st.dev/benchmarks/copy/method). In short:

- **Analytic rubric.** Fidelity is split into 26 criteria in five dimensions: content, layout, motion, color and
  typography. A judge rates each criterion `same`, `minor` or `major`, and code computes the score. The model never
  picks a number.
- **A panel of two LLM judges.** GPT-6.1 Sol and Claude Opus 5.5 rate every copy from side-by-side frames of the
  original and the copy, and we report their mean. The judges come from two labs because a judge favors its own
  family: on GPT copies the GPT judge scores 3.8 points above the Claude judge. Across all copies the two correlate
  at 0.89 and sit 10 points apart on average.
- **Integrity checks.** A score only counts if the copy was built from what the model saw. Reused code, replayed
  pixels (an embedded video or flipped frames) and a missing file score zero. No copy replayed the recording. Four
  copies scored zero for reused code: with nothing fetched, Gemini 4 Carbon turned in a flocking simulation whose
  code matches 90% of the open-source original.
- **Human validation.** We scored 249 copies by hand. The judges' average matches those scores at 0.84, closer than
  either judge alone.

The grader that ships in this repo is a lighter version of that setup: see [Known limits](#known-limits).

## Task anatomy

Every task has two steps that run in the same sandbox:

1. **first** (one-shot, 30 min): the agent gets `video.mp4`, `steps.json` (the mouse/scroll script used during the
   recording) and `cb-frames` (a small tool that pulls frames out of the video). There is no browser, so the agent
   can't render its page.
2. **fix** (self-verified, 20 min): a headless browser (`agent-browser`) gets unlocked, and the agent can open its own
   page, compare it with the recording, and fix it.

```
tasks/
  dataset.toml              pins the 13 tasks by digest
  t84-3d-letter-rings/
    task.toml               two steps, time limits, network allowlist, judge keys
    environment/            Dockerfile, the video, steps.json, cb-frames
    steps/first/instruction.md
    steps/fix/instruction.md
    steps/fix/workdir/      setup.sh that unlocks the browser for step 2
    tests/                  the grader (only uploaded at grading time, the agent never sees it)
      test.sh, grade.py, capture.mjs, prompt.md, checklist.py
      ref/                  4 reference frames from the original's recording
```

The browser is in the image from the start, but encrypted. Its key only shows up in step 2, so step 1 really is blind.

During the agent's turn the network is an allowlist: model APIs (so the agent can think) and four library CDNs
(esm.sh, unpkg, jsdelivr, cdnjs, so it can use three.js or GSAP like the originals do). Nothing else. Most originals
are public, so open internet would let an agent download the source instead of copying it from the video.

## How scoring works

After each step, `tests/grade.py` runs inside the sandbox:

1. No `index.html` gets 0.
2. It serves the workspace, opens the copy in headless Chromium at 1280x800, replays the same mouse/scroll script,
   and takes screenshots at the same 4 timestamps as the reference frames.
3. It builds one contact sheet (original on the left, copy on the right, one row per timestamp) and asks one vision
   judge a fixed rubric: content, layout, color, typography, motion (26 criteria, each rated `same`, `minor`,
   `major` or `n/a`).
4. The score is computed in code, not by the model: each dimension is 100 minus 15 per minor and 40 per major,
   overall is a weighted mean (content 25%, layout 25%, motion 20%, color 15%, typography 15%).
   Reward = overall / 100.

The task reward is the score of the last step (self-verified). The one-shot score is recorded in the step results.
`/logs/verifier/` keeps the copy, the sheet, the judge's answer (`judge.json`) and a log.

The judge key comes from your shell:

| Variable | What it does |
|---|---|
| `ANTHROPIC_API_KEY` | judge with Claude (default `claude-opus-5-5`) |
| `OPENAI_API_KEY` | judge with GPT (default `gpt-6.1-sol`), used when there's no Anthropic key |
| `COPY_BENCH_JUDGE_MODEL` | a different judge model |

Without a key the run still finishes but isn't judged: reward 1 if `index.html` exists, and `graded` is 0 in
`reward.json`. If grading breaks for any other reason (for example the agent deleted the browser), the reward is 0,
so breaking the grader never pays.

The dataset score is the mean reward over the tasks. `reward.json` also carries the per-dimension scores (`content`,
`layout`, ...) and the task kind (`kind_3d`, ...); `scripts/metric.py` does that breakdown offline from exported
rewards.

## Run it on Harbor

```bash
export ANTHROPIC_API_KEY=...        # the agent and the judge both use it

# one task
harbor run -d 21st/copy-bench -a claude-code -m anthropic/claude-opus-5-5 --n-tasks 1

# all 13
harbor run -d 21st/copy-bench -a claude-code -m anthropic/claude-opus-5-5 -n 4
```

From a checkout of this repo, swap `-d 21st/copy-bench` for `-p tasks`. The image builds for linux/amd64 and
arm64, and the first build takes a few minutes.

## Known limits

- **WebGL renders in software in the sandbox.** The reference recordings were made on macOS with GPU rendering.
  In a Linux sandbox Chromium draws WebGL and shaders with SwiftShader, so a correct WebGL copy can look a little
  different from the reference (shading, bloom, smoothness). The judge prompt says so, and the per-task note about
  what varies between loads of the original is passed through. Our published results were captured on the same
  machine for both sides, so they don't have this problem.
- **One judge, 4 frames, no integrity checks.** The published results use two judges on full recordings, and zero a
  copy that reuses the original's code or replays the recording. The in-run grader here uses the same rubric and
  the same scoring with one judge on 4 frames, and it does not run the integrity checks. Expect its numbers to be
  close to ours, not equal.
- **The verifier shares the sandbox with the agent.** It decrypts its own copy of Chromium and calls system binaries
  by absolute path, but a determined agent running as root could still tamper with the sandbox.
- No reference solutions are included (the originals' source isn't redistributed), so there's no oracle run.

## What's in this subset

13 of the 50 tasks: 7 components from the 21st.dev catalog and 6 open-source demos under permissive licenses (MIT or
Apache-2.0). See [ATTRIBUTION.md](ATTRIBUTION.md). The other 37 tasks are held out so the benchmark stays useful.

`scripts/build_tasks.py` rebuilds `tasks/` from our internal lab checkout, and `harbor sync tasks` pins the digests
in `dataset.toml`.

## License

Code (grader, scripts, metric) is MIT, see [LICENSE](LICENSE). The task recordings show components from 21st.dev and
open-source demos. They're included for evaluation only, under the terms listed in [ATTRIBUTION.md](ATTRIBUTION.md).
