# Task: copy a web page

Recreate the original page as one HTML file, as close to it as you can.

## What you get

- `video.mp4`: a screen recording of the original page, 1280x800, 25 fps, 6 s from the load event.
- `cb-frames` (run it with Bash) pulls frames out of `video.mp4` as PNGs into `more-frames/`: `cb-frames --sheet` makes one overview picture with 16 time-labelled thumbnails over the whole video, `cb-frames --at 0.5,1.25` gives full-size 1280x800 frames at those seconds, `cb-frames --fps 25 --from 1 --to 2` every frame in a window. Open the PNGs with your file-read tool to see them as images (don't decode pixels with scripts). `cb-frames --help` shows the rest and the video's length.

## The page

The page moves on its own: animation that plays on load and/or loops.

Also in the workspace:

- `assets/`: files the original page loads, under neutral names. Use them with relative paths like `assets/envmap-01.png`:
  - `assets/envmap-01.png`: environment light atlas (PlayCanvas env-atlas layout, RGBP-encoded)

## How the capture works (the original's and yours)

- Headless Chromium, viewport 1280x800, device scale factor 1, light colour scheme, locale en-US, timezone UTC.
- Screenshot: a fresh page, after the load event, network idle (capped at 5 s) and fonts ready.
- Randomness is fixed: before any of the page's scripts run, `Math.random` is replaced by a seeded generator (mulberry32, seed 1, restarted on every load) and `Date` starts at 2026-01-01T00:00:00Z plus the real time since the page started loading. Both the original and your copy get this, so a copy that uses `Math.random` the same way as the original gets the same numbers. `performance.now()` and `requestAnimationFrame` run on the real clock.
- Recording: the page is loaded again and recorded for 6 s; time zero is the load event (real clock; with a mouse script, just after a short mouse warm-up that follows the load event). Frames are cut from that recording.

## Output

Write ONE self-contained file: `index.html` at the workspace root.

- Inline your own HTML, CSS and JS. No build step: the file is opened as is.
- Libraries only from esm.sh, unpkg.com, cdn.jsdelivr.net or cdnjs.cloudflare.com (script tags or ES module imports). No other external URLs: no images, fonts, videos or data from any other host. Local files only from `assets/`. Draw or inline anything else (CSS, SVG, canvas, data URIs), or use a close system font.
- Your file is opened in Chromium at 1280x800 and captured exactly like the original, then compared with the original's capture frame by frame.
- Don't ask questions. When something is unclear, make your best guess and finish the file.

Goal: as close as you can get to the original in layout, colour, typography, text and motion. Closeness counts, not whether you think your version looks better.

---

## Where you are

Your working directory is `/workspace`, and everything listed under "What you get" is there: `video.mp4`, `assets/`. There's no browser here and no internet (only the library CDNs): you can't open or render your page, so don't try to install one.

- Write your copy to `/workspace/index.html`.
- Hard rule: your page draws everything itself. Don't put the video, frames or screenshots (or pieces of them) into the page, as files or as data URIs. Only the images in `assets/`, if there are any, may be used as images.
- You have 30 minutes. Whatever is in `/workspace/index.html` when the time runs out is what gets graded, and no file scores zero. Write a first full version early, then improve it.
