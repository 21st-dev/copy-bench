# Round 2: check your copy in a browser and fix it

`/workspace/index.html` is the copy you just wrote without being able to open it. Now you have a browser. Open your page, compare it with the original you were given (`video.mp4`), and fix what differs.

- **`agent-browser`** is a headless browser you drive from the shell (the browser CLI Plato's Web Clone Bench gives its agents). Serve the workspace first (`python3 -m http.server 8000 >/dev/null 2>&1 &`), then for example `agent-browser set viewport 1280 800`, `agent-browser open http://localhost:8000/index.html`, `agent-browser screenshot shots/a.png`, `agent-browser record start shots/take.webm --contact-sheet` and `agent-browser record stop`; `mouse`, `scroll`, `press` and `wait` drive the page the way `steps.json` does. `agent-browser --help` and `agent-browser skills get core` show the rest.
- `cb-frames` still works on the original's recording `video.mp4` (`cb-frames --sheet`, `--at`, `--fps`), so you can put the original's frames next to your page at the same times. It only reads `video.mp4`.
- The original page itself isn't here: only the files you were given. This machine draws WebGL in software and has other fonts than the grading machine, so trust layout, colour and motion more than exact glyph shapes.
- Hard rule: your page draws everything itself. Don't put the video, frames or screenshots (or pieces of them) into the page, as files or as data URIs. Only the images in `assets/`, if there are any, may be used as images.
- Edit `/workspace/index.html` in place. If your first version is already as close as you can get, leave it.
- You have 20 minutes. Whatever is in `/workspace/index.html` when the time runs out is what gets graded.

For reference, the task from round 1, unchanged:

---

# Task: copy a web page

Recreate the original page as one HTML file, as close to it as you can.

## What you get

- `video.mp4`: a screen recording of the original page, 1280x800, 25 fps, 8 s from the load event.
- `cb-frames` (run it with Bash) pulls frames out of `video.mp4` as PNGs into `more-frames/`: `cb-frames --sheet` makes one overview picture with 16 time-labelled thumbnails over the whole video, `cb-frames --at 0.5,1.25` gives full-size 1280x800 frames at those seconds, `cb-frames --fps 25 --from 1 --to 2` every frame in a window. Open the PNGs with your file-read tool to see them as images (don't decode pixels with scripts). `cb-frames --help` shows the rest and the video's length.

## The page

The page moves on its own: animation that plays on load and/or loops.

## How the capture works (the original's and yours)

- Headless Chromium, viewport 1280x800, device scale factor 1, light colour scheme, locale en-US, timezone UTC.
- Screenshot: a fresh page, after the load event, network idle (capped at 5 s) and fonts ready, taken 8 s after the load event (the end of the recording); no input.
- Recording: the page is loaded again and recorded for 8 s; time zero is the load event (real clock; with a mouse script, just after a short mouse warm-up that follows the load event). Frames are cut from that recording.

## Output

Write ONE self-contained file: `index.html` at the workspace root.

- Inline your own HTML, CSS and JS. No build step: the file is opened as is.
- Libraries only from esm.sh, unpkg.com, cdn.jsdelivr.net or cdnjs.cloudflare.com (script tags or ES module imports). No other external URLs: no images, fonts, videos or data from any other host. Local files only from `assets/`. Draw or inline anything else (CSS, SVG, canvas, data URIs), or use a close system font.
- Your file is opened in Chromium at 1280x800 and captured exactly like the original, then compared with the original's capture frame by frame.
- Don't ask questions. When something is unclear, make your best guess and finish the file.

Goal: as close as you can get to the original in layout, colour, typography, text and motion. Closeness counts, not whether you think your version looks better.
