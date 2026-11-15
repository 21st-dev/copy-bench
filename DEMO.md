# 2-minute demo

Run everything from the repo root. Do the setup before you go on stage. Start one run ahead of time so a finished
score is ready to show (a task takes up to ~55 min: 30 + 20 min of agent time plus grading).

## Setup (once, before the demo)

```bash
valkyrie login
valkyrie org use hackathon-non-verifiable-verifiable-1b4fb24b34

# Modal sandboxes: modal.json = {"MODAL_TOKEN_ID": "ak-...", "MODAL_TOKEN_SECRET": "as-...", "runtime": "vm"}
valkyrie secret set modal-credentials < modal.json
valkyrie provider set modal modal-credentials

# One key for the agent (Claude Code) and the judge (the tasks read the secret named anthropic-api-key)
valkyrie secret set anthropic-api-key

valkyrie agent install https://github.com/vals-ai/public-agent-registry/tree/main/examples/claude_code-v1.0.0
valkyrie dataset push copy-bench/copy-bench ./tasks --tag v1

valkyrie run start --agent claude_code-v1.0.0 --dataset copy-bench/copy-bench@v1 \
  --model anthropic/claude-opus-5-5 --provider modal \
  -s ANTHROPIC_API_KEY anthropic-api-key --slice 0:1 --concurrency 1 -l demo
```

## On stage

**1. The problem (20 s).** Open https://21st.dev/benchmarks/copy

> "We give a model 8 seconds of screen recording of a real web component, WebGL, shaders, animation, and ask it to
> rebuild it as one HTML file. 13 frontier models, 50 tasks. The best gets 86.7, most are between 35 and 70.
> Motion is where they break."

**2. One task (20 s).** Show what the agent gets:

```bash
open tasks/t84-3d-letter-rings/environment/workspace/video.mp4
```

> "That's the whole input: this video, the mouse script, and a frame tool. Step 1 it works blind, no browser.
> Step 2 the browser unlocks in the same sandbox and it can check its own work."

**3. It's a Valkyrie dataset (20 s).**

```bash
ls tasks/t84-3d-letter-rings tasks/t84-3d-letter-rings/steps
valkyrie dataset push copy-bench/copy-bench ./tasks --tag v1
```

> "13 tasks, two steps each, pushed with one command. Pushing again uploads nothing because nothing changed."

**4. A run (30 s).**

```bash
valkyrie tui
```

Open the run started before the demo, then the task, then its two steps and the verifier logs.

> "Valkyrie runs Claude Code in a Modal sandbox. After each step our grader renders the copy in headless Chromium,
> puts it next to the original at the same timestamps, and a vision judge answers a fixed 26-point checklist.
> The score is computed in code, not by the model."

**5. The score (30 s).** In the TUI, open `/logs/verifier/` of the last step: `sheet.jpg`, `judge.json`, the reward.
Or from the shell:

```bash
valkyrie run results RUN_ID
```

If the run isn't done yet, show the two example sheets in `docs/` instead:

```bash
open docs/t84-gpt-6-astra.jpg docs/t84-mimo-v2.6-pro.jpg
```

> "Same task. Left is the original, right is the copy. GPT-6 Astra nails it. MiMo gets a glow with no letters.
> Frontier models still miss this, and now anyone can measure it on Valkyrie."
