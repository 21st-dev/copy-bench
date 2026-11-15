#!/usr/bin/env node
// Capture a page the way the original was captured: headless Chromium at 1280x800, DPR 1, light scheme,
// en-US, UTC. Time zero = the load event. steps.json drives the mouse / scroll; screenshots land at --times (ms).
// Zero dependencies: Node 22 (global WebSocket) talks to Chromium over the DevTools protocol.
//
//   node capture.mjs --chrome /path/to/chrome --url http://127.0.0.1:8000/index.html \
//        --steps steps.json --times 1000,3000,5000,7000 --out shots/
import { spawn } from "node:child_process";
import { mkdtempSync, readFileSync, writeFileSync, existsSync, mkdirSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const arg = (k, d) => { const i = process.argv.indexOf(`--${k}`); return i > 0 ? process.argv[i + 1] : d; };
const chromePath = arg("chrome"), url = arg("url"), out = arg("out", "shots");
const times = arg("times", "1000,3000,5000,7000").split(",").map(Number);
const steps = arg("steps") && existsSync(arg("steps")) ? JSON.parse(readFileSync(arg("steps"), "utf8")) : [];
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
mkdirSync(out, { recursive: true });

const profile = mkdtempSync(join(tmpdir(), "cbv-profile-"));
const gl = process.platform === "darwin" ? ["--use-angle=metal"] : ["--use-angle=swiftshader", "--enable-unsafe-swiftshader"];
const chrome = spawn(chromePath, [
  "--headless=new", "--no-sandbox", "--disable-dev-shm-usage", "--remote-debugging-port=0", `--user-data-dir=${profile}`,
  "--window-size=1280,800", "--hide-scrollbars", "--force-device-scale-factor=1", "--no-first-run",
  "--no-default-browser-check", "--mute-audio", "--lang=en-US", ...gl, "about:blank",
], { stdio: "ignore", env: { ...process.env, TZ: "UTC" } });

const kill = () => { try { chrome.kill("SIGKILL"); } catch {} try { rmSync(profile, { recursive: true, force: true }); } catch {} };
const fail = (m) => { console.error(`capture: ${m}`); kill(); process.exit(1); };
setTimeout(() => fail("timed out after 120 s"), 120000).unref();

let port;
for (let i = 0; i < 100 && !port; i++) {
  const f = join(profile, "DevToolsActivePort");
  if (existsSync(f)) port = readFileSync(f, "utf8").split("\n")[0].trim();
  else await sleep(100);
}
if (!port) fail("Chromium did not start");
const list = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
const pageWs = list.find((t) => t.type === "page")?.webSocketDebuggerUrl;
if (!pageWs) fail("no page target");

const ws = new WebSocket(pageWs);
await new Promise((r, j) => { ws.onopen = r; ws.onerror = () => j(new Error("ws error")); });
let id = 0; const pending = new Map(); const listeners = [];
ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) { const p = pending.get(m.id); pending.delete(m.id); m.error ? p.j(new Error(m.error.message)) : p.r(m.result); }
  else if (m.method) listeners.forEach((l) => l(m));
};
const send = (method, params = {}) => new Promise((r, j) => { const i = ++id; pending.set(i, { r, j }); ws.send(JSON.stringify({ id: i, method, params })); });
const once = (method) => new Promise((r) => { const l = (m) => { if (m.method === method) { listeners.splice(listeners.indexOf(l), 1); r(m); } }; listeners.push(l); });

await send("Page.enable");
await send("Emulation.setDeviceMetricsOverride", { width: 1280, height: 800, deviceScaleFactor: 1, mobile: false });
await send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: "light" }] });
await send("Emulation.setTimezoneOverride", { timezoneId: "UTC" }).catch(() => {});
await send("Emulation.setLocaleOverride", { locale: "en-US" }).catch(() => {});

const loaded = once("Page.loadEventFired");
await send("Page.navigate", { url });
await loaded;
const t0 = Date.now();
const now = () => Date.now() - t0;

// Input script (same verbs as the original capture: move / scroll / click / down / up / wait).
let mx = 640, my = 400, down = false;
const mouse = (type, extra = {}) => send("Input.dispatchMouseEvent", { type, x: mx, y: my, button: down || type !== "mouseMoved" ? "left" : "none", buttons: down ? 1 : 0, ...extra }).catch(() => {});
async function runSteps() {
  for (const s of steps) {
    const wait = (s.at_ms ?? 0) - now();
    if (wait > 0) await sleep(wait);
    if (s.do === "move") {
      const n = Math.max(1, s.steps ?? 10), dt = (s.ms ?? n * 16) / n, x0 = mx, y0 = my;
      for (let k = 1; k <= n; k++) { mx = x0 + ((s.x - x0) * k) / n; my = y0 + ((s.y - y0) * k) / n; await mouse("mouseMoved"); await sleep(dt); }
    } else if (s.do === "scroll") {
      if (s.y !== undefined) await send("Runtime.evaluate", { expression: `window.scrollTo(0, ${Number(s.y)})` }).catch(() => {});
      else await send("Input.dispatchMouseEvent", { type: "mouseWheel", x: mx, y: my, deltaX: s.dx ?? 0, deltaY: s.dy ?? 0 }).catch(() => {});
    } else if (s.do === "click") {
      if (s.x !== undefined) { mx = s.x; my = s.y; }
      down = true; await mouse("mousePressed", { clickCount: 1 }); down = false; await mouse("mouseReleased", { clickCount: 1 });
    } else if (s.do === "down") { down = true; await mouse("mousePressed", { clickCount: 1 }); }
    else if (s.do === "up") { down = false; await mouse("mouseReleased", { clickCount: 1 }); }
  }
}
const input = runSteps();

const shots = [];
for (const t of times) {
  const wait = t - now();
  if (wait > 0) await sleep(wait);
  const at = now();
  const { data } = await send("Page.captureScreenshot", { format: "jpeg", quality: 85 });
  const file = join(out, `${String(t).padStart(5, "0")}ms.jpg`);
  writeFileSync(file, Buffer.from(data, "base64"));
  shots.push({ target_ms: t, shot_ms: at, file });
}
await Promise.race([input, sleep(500)]);
writeFileSync(join(out, "capture.json"), JSON.stringify({ url, shots }, null, 1));
ws.close(); kill();
process.exit(0);
