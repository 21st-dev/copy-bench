# Task: copy a web page

Recreate the original page as one HTML file, as close to it as you can.

## What you get

- `video.mp4`: a screen recording of the original page, 1280x800, 25 fps, 8 s from the load event.
- `cb-frames` (run it with Bash) pulls frames out of `video.mp4` as PNGs into `more-frames/`: `cb-frames --sheet` makes one overview picture with 16 time-labelled thumbnails over the whole video, `cb-frames --at 0.5,1.25` gives full-size 1280x800 frames at those seconds, `cb-frames --fps 25 --from 1 --to 2` every frame in a window. Open the PNGs with your file-read tool to see them as images (don't decode pixels with scripts). `cb-frames --help` shows the rest and the video's length.

## The page

The page reacts to the mouse.

Also in the workspace:

- `assets/`: the raster images the original page shows, under neutral names. Use them with relative paths like `assets/image-01.jpg`.
- `steps.json`: the input script (mouse, keyboard, scroll) that drives the page during the capture (below).

## How the capture works (the original's and yours)

- Headless Chromium, viewport 1280x800, device scale factor 1, light colour scheme, locale en-US, timezone UTC.
- Screenshot: a fresh page, after the load event, network idle (capped at 5 s) and fonts ready.
- Recording: the page is loaded again and recorded for 8 s; time zero is the load event (real clock; with a mouse script, just after a short mouse warm-up that follows the load event). Frames are cut from that recording.
- During the recording `steps.json` drives the input. Each step has `at_ms` (ms after time zero) and `do`: `move` = move the mouse to `x,y` (viewport px) in `steps` small hops; `scroll` with `y` = set the window scroll to `y`, with `dx,dy` = a mouse-wheel turn; `click` = click at `x,y`; `key` = press and release the key `key`; `keydown` / `keyup` = hold / release `key` (a held key sends one keydown and no auto-repeat; names as in KeyboardEvent.key, e.g. `ArrowLeft`, `a`, `Space` = the space bar, `Enter`); `wait` = nothing.
- The red dot with a white ring is the mouse cursor, drawn by the capture tool on top of the page. It isn't part of the page: don't draw it.
- Keys go to the page itself (the focused document; nothing is clicked first unless `steps.json` says so). The small dark badge in the bottom-left corner lists the keys being held (blue) or just pressed (red); it is drawn by the capture tool on top of the page. It isn't part of the page: don't draw it.
- The screenshot is taken without any mouse, keyboard or scroll input.

## Output

Write ONE self-contained file: `index.html` at the workspace root.

- Inline your own HTML, CSS and JS. No build step: the file is opened as is.
- Libraries only from esm.sh, unpkg.com, cdn.jsdelivr.net or cdnjs.cloudflare.com (script tags or ES module imports). No other external URLs: no images, fonts, videos or data from any other host. Local files only from `assets/`. Draw or inline anything else (CSS, SVG, canvas, data URIs), or use a close system font.
- Your file is opened in Chromium at 1280x800 and captured exactly like the original, then compared with the original's capture frame by frame.
- Don't ask questions. When something is unclear, make your best guess and finish the file.

Goal: as close as you can get to the original in layout, colour, typography, text and motion. Closeness counts, not whether you think your version looks better.

---

## Where you are

Your working directory is `/workspace`, and everything listed under "What you get" is there: `video.mp4`, `steps.json`, `assets/`. There's no browser here and no internet (only the library CDNs): you can't open or render your page, so don't try to install one.

- Write your copy to `/workspace/index.html`.
- Hard rule: your page draws everything itself. Don't put the video, frames or screenshots (or pieces of them) into the page, as files or as data URIs. Only the images in `assets/`, if there are any, may be used as images.
- You have 30 minutes. Whatever is in `/workspace/index.html` when the time runs out is what gets graded, and no file scores zero. Write a first full version early, then improve it.
