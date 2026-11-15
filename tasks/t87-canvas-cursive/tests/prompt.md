You are grading how closely a COPY of a web page reproduces the ORIGINAL. Someone was asked to rebuild the original
as exactly as they could. Your job is fidelity, not taste: how close is the copy to the original? Never judge which one
looks better, cleaner or more modern. A copy that "improves" on the original is a worse copy.

Both pages were rendered the same way (headless Chromium, viewport 1280x800) and captured on the same timeline that
starts at the page's load event, with the same mouse / scroll script. The attached image is one contact sheet: each row
is one timestamp ({timestamps}), with the ORIGINAL on the left and the COPY on the right, at the same scale. Positions
inside the two panels are directly comparable.

{task_note}

Expected noise, which is NOT a difference: both captures run in real time, so a moving element can be slightly out of
phase between the two sides. Grade the kind, path and speed of motion, not frame-exact alignment. Random or procedural
texture (grain, noise, particles) never lands on the same pixels in two renders; compare its character. The original's
frames come from a compressed video and may show a red dot with a white ring: that is the capture tool's mouse cursor,
not part of the page. Anti-aliasing and sub-pixel text rendering don't count. The original was recorded with GPU
rendering; the copy was rendered in a sandbox where WebGL runs in software, so small differences in shading, bloom or
smoothness of WebGL / shader content are expected rendering noise, not copy errors. A blank or missing scene is not
noise.

Answer every check below with how much the copy differs from the original on that point. Use the check's id.
- "same": you find no difference for this check.
- "minor": a real difference you only see when you compare the two closely; it wouldn't change what a user perceives.
- "major": a user would notice it without the original next to it. Something missing (an element, a text, an effect,
  motion that doesn't happen) or a different kind of motion is always major. A blank or broken copy is major everywhere.
- "n/a": only where the check says so, or when the original has nothing the check is about (no text at all: text and
  typography checks are n/a). A copy that lacks something the original has is major, not n/a.
When unsure between minor and major, ask: would someone who only ever saw the copy notice that it's wrong? Yes is major.

{checklist}

Then list every concrete visible difference as short issues ("headline is green instead of blue", "rings spin about
3x slower"). Priority when things conflict: content first, then layout, then style (color, typography), then motion.

Reply with JSON only, no prose around it, in this shape:
{{"checks": [{{"id": "c1", "result": "same|minor|major|n/a", "note": "evidence"}}, ...], "issues": ["..."]}}
