#!/usr/bin/env python3
"""Renders the link-preview images and the Reddit assets with the site's own fonts and mark.

    python3 tools/og.py            # essays + site card into src/assets/og and src/assets, Reddit assets into brand/

Needs Playwright with Chromium. Each image is an HTML page screenshotted at its exact size, so the type is
the self-hosted Spectral and the mark is the same SVG the site uses. Run it again whenever an essay is added;
then run build.py so docs/ picks up the new files.
"""
import asyncio, html, os, random, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import build  # noqa: E402

PORT = 8766
OG_DIR = os.path.join(ROOT, "src", "assets", "og")
BRAND_DIR = os.path.join(ROOT, "brand")

NAVY, NAVY_0, NAVY_2 = "#0A1628", "#0A1020", "#132340"
GOLD, GOLD_HOT, ION, STAR, SLATE = "#FFB830", "#FFCB5C", "#5CE1FF", "#EEF2FF", "#8B9AAD"

CSS = f"""
@font-face {{ font-family: "Spectral"; font-weight: 400; src: url("src/assets/fonts/spectral-latin-400-normal.woff2") format("woff2"); }}
@font-face {{ font-family: "Spectral"; font-weight: 500; src: url("src/assets/fonts/spectral-latin-500-normal.woff2") format("woff2"); }}
@font-face {{ font-family: "Spectral"; font-weight: 600; src: url("src/assets/fonts/spectral-latin-600-normal.woff2") format("woff2"); }}
@font-face {{ font-family: "Spectral SC"; font-weight: 500; src: url("src/assets/fonts/spectral-sc-latin-500-normal.woff2") format("woff2"); }}
:root {{ --star: {STAR}; --gold: {GOLD}; --gold-hot: {GOLD_HOT}; --ion: {ION}; --mark-gold: {GOLD}; }}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; }}
body {{ font-family: "Spectral", Georgia, serif; color: {STAR}; background: {NAVY}; position: relative; overflow: hidden; }}
.sky, .aurora {{ position: absolute; inset: 0; }}
.aurora {{ background: radial-gradient(50% 70% at 82% 40%, rgba(255,184,48,0.17), transparent 68%), radial-gradient(42% 60% at 6% 100%, rgba(92,225,255,0.14), transparent 68%); }}
.horizon {{ position: absolute; left: 0; right: 0; bottom: 0; width: 100%; display: block; }}
.lockup {{ display: flex; align-items: center; gap: 0.6em; }}
.lockup svg {{ display: block; }}
.wordmark {{ font-weight: 600; letter-spacing: 0.18em; text-transform: uppercase; white-space: nowrap; }}
.wordmark span {{ color: {SLATE}; font-weight: 400; }}
.caps {{ font-family: "Spectral SC", "Spectral", serif; font-weight: 500; letter-spacing: 0.1em; color: {ION}; }}
.glow {{ filter: drop-shadow(0 0 22px rgba(255,184,48,0.35)) drop-shadow(0 0 60px rgba(255,184,48,0.14)); }}
"""


def stars_svg(w, h, seed, density=9000, ion=0.10, gold=0.05, clear=0.0):
    """A seeded star field. `clear` keeps a circle at the center (a fraction of the width) empty."""
    rnd = random.Random(seed)
    n = round(w * h / density)
    out = []
    for _ in range(n):
        x, y, s = rnd.random() * w, rnd.random() * h, 0.6 + rnd.random() * 1.3
        roll = rnd.random()
        if clear and ((x - w / 2) ** 2 + (y - h / 2) ** 2) ** 0.5 < clear * w:
            continue
        if roll > 1 - gold:
            c, a = GOLD, 0.8
        elif roll > 1 - gold - ion:
            c, a = ION, 0.7
        else:
            c, a = STAR, 0.12 + rnd.random() * 0.42
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{s:.2f}" fill="{c}" fill-opacity="{a:.2f}"/>')
    return f'<svg class="sky" width="{w}" height="{h}" viewBox="0 0 {w} {h}">' + "".join(out) + "</svg>"


def constellation(w, h, pts, seed_color=STAR):
    path = " ".join(("M" if i == 0 else "L") + f" {x*w:.1f} {y*h:.1f}" for i, (x, y) in enumerate(pts))
    dots = "".join(f'<circle cx="{x*w:.1f}" cy="{y*h:.1f}" r="{1.9 if i == 2 else 1.4}" fill="{GOLD if i == 2 else (ION if i == len(pts)-1 else STAR)}" fill-opacity="0.7"/>' for i, (x, y) in enumerate(pts))
    return f'<path d="{path}" fill="none" stroke="{SLATE}" stroke-opacity="0.28" stroke-width="0.7"/>{dots}'


def horizon(height):
    return build.horizon().replace('class="horizon"', f'class="horizon" style="height:{height}px"')


def lockup(mark_px, text_px, suffix):
    return (f'<div class="lockup"><svg width="{mark_px}" height="{mark_px}" viewBox="0 0 200 200" fill="none">{build.mark_body(suffix)}</svg>'
            f'<div class="wordmark" style="font-size:{text_px}px">Visionary <span>Systems</span></div></div>')


def essay_card(e, index):
    title = html.escape(e["title"])
    return f"""<!doctype html><html><head><meta charset="utf-8"><base href="http://127.0.0.1:{PORT}/"><style>{CSS}
body {{ width: 1200px; height: 630px; }}
.frame {{ position: absolute; inset: 0; padding: 56px 64px 52px; display: flex; flex-direction: column; }}
.title {{ font-weight: 500; line-height: 1.12; letter-spacing: -0.01em; max-width: 1000px; text-wrap: balance; margin-top: 22px; }}
.meta {{ margin-top: auto; display: flex; justify-content: space-between; align-items: baseline; color: {SLATE}; font-size: 24px; }}
.rule {{ position: absolute; left: 64px; right: 64px; top: 0; height: 2px; background: linear-gradient(90deg, {GOLD}, {ION}); box-shadow: 0 0 14px rgba(92,225,255,0.35); }}
</style></head><body>
<div class="aurora"></div>{stars_svg(1200, 630, 1618 + index)}{horizon(70)}
<div class="frame">
<div class="rule"></div>
{lockup(44, 20, "og")}
<div class="caps" style="font-size:24px;margin-top:64px">The Calibration Series, {index} of {build.SERIES_TOTAL}</div>
<div class="title" id="title" style="font-size:66px">{title}</div>
<div class="meta"><span>{e["date"]}</span><span>visionarysystems.io</span></div>
</div></body></html>"""


def site_card():
    return f"""<!doctype html><html><head><meta charset="utf-8"><base href="http://127.0.0.1:{PORT}/"><style>{CSS}
body {{ width: 1200px; height: 630px; }}
.frame {{ position: absolute; inset: 0; padding: 0 72px; display: grid; grid-template-columns: 300px 1fr; gap: 56px; align-items: center; }}
.tag {{ font-weight: 500; font-size: 58px; line-height: 1.1; letter-spacing: -0.01em; margin-top: 18px; text-wrap: balance; }}
.sub {{ color: {SLATE}; font-size: 24px; margin-top: 26px; }}
</style></head><body>
<div class="aurora"></div>{stars_svg(1200, 630, 1618)}{horizon(70)}
<div class="frame">
<svg class="glow" width="300" height="300" viewBox="0 0 200 200" fill="none">{build.mark_body("og")}</svg>
<div>
<div class="wordmark" style="font-size:30px">Visionary <span>Systems</span></div>
<div class="tag">What tests can and can't tell you.</div>
<div class="sub">The Visionary Psychometric Scan, in beta calibration, and The Visionary, launching March 2027.</div>
</div></div></body></html>"""


def reddit_banner(w=1600, h=480, mark=124, text=58):
    """Profile banner. 1600x480 (10:3) is what the new profile page shows whole; the lockup sits in the
    middle band so a wider surface that crops top and bottom (5:1) still keeps it."""
    left = constellation(w, h, [(0.05, 0.18), (0.11, 0.36), (0.16, 0.30), (0.20, 0.52), (0.17, 0.74)])
    right = constellation(w, h, [(0.95, 0.20), (0.90, 0.34), (0.85, 0.30), (0.80, 0.54), (0.84, 0.76)])
    return f"""<!doctype html><html><head><meta charset="utf-8"><base href="http://127.0.0.1:{PORT}/"><style>{CSS}
body {{ width: {w}px; height: {h}px; background: {NAVY}; }}
.aurora {{ background: radial-gradient(28% 90% at 50% 50%, rgba(255,184,48,0.10), transparent 70%), radial-gradient(30% 80% at 4% 100%, rgba(92,225,255,0.10), transparent 70%), radial-gradient(30% 80% at 96% 100%, rgba(92,225,255,0.08), transparent 70%); }}
.frame {{ position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; }}
.wordmark {{ letter-spacing: 0.2em; }}
</style></head><body>
<div class="aurora"></div>{stars_svg(w, h, 2718, density=8000, ion=0.09, gold=0.05)}
<svg class="sky" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{left}{right}</svg>
{horizon(round(h / 6))}
<div class="frame">{lockup(mark, text, "rb")}</div>
</body></html>"""


def reddit_avatar():
    return f"""<!doctype html><html><head><meta charset="utf-8"><base href="http://127.0.0.1:{PORT}/"><style>{CSS}
body {{ width: 512px; height: 512px; background: {NAVY_0}; }}
.frame {{ position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; }}
</style></head><body>
{stars_svg(512, 512, 3141, density=12000, ion=0.14, gold=0.06, clear=0.3)}
<div class="frame"><svg class="glow" width="372" height="372" viewBox="0 0 200 200" fill="none">{build.mark_body("ra")}</svg></div>
</body></html>"""


FIT = """async () => {
  await document.fonts.ready;
  const t = document.getElementById('title');
  if (t) { let fs = parseFloat(getComputedStyle(t).fontSize);
    while ((t.scrollHeight > 300 || t.scrollWidth > 1000) && fs > 34) { fs -= 2; t.style.fontSize = fs + 'px'; } }
  return true; }"""


TMP = os.path.join(ROOT, "tools", ".og-tmp")   # served alongside the fonts so they load same-origin


async def render(page, html_str, w, h, out):
    os.makedirs(TMP, exist_ok=True)
    name = os.path.basename(out).replace(".png", ".html")
    with open(os.path.join(TMP, name), "w", encoding="utf-8") as f:
        f.write(html_str)
    await page.set_viewport_size({"width": w, "height": h})
    await page.goto(f"http://127.0.0.1:{PORT}/tools/.og-tmp/{name}", wait_until="load")
    await page.evaluate(FIT)
    await page.wait_for_timeout(150)
    await page.screenshot(path=out, clip={"x": 0, "y": 0, "width": w, "height": h})
    print("wrote", os.path.relpath(out, ROOT))


async def main():
    from playwright.async_api import async_playwright
    os.makedirs(OG_DIR, exist_ok=True)
    os.makedirs(BRAND_DIR, exist_ok=True)
    server = subprocess.Popen([sys.executable, "-m", "http.server", str(PORT), "--bind", "127.0.0.1"], cwd=ROOT,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(0.8)
    try:
        async with async_playwright() as p:
            exe = "/usr/bin/google-chrome" if os.path.exists("/usr/bin/google-chrome") else None
            b = await p.chromium.launch(executable_path=exe) if exe else await p.chromium.launch()
            ctx = await b.new_context(device_scale_factor=1)
            page = await ctx.new_page()
            for i, e in enumerate(build.ESSAYS, start=1):
                await render(page, essay_card(e, i), 1200, 630, os.path.join(OG_DIR, f"{e['slug']}.png"))
            await render(page, site_card(), 1200, 630, os.path.join(ROOT, "src", "assets", "og-image.png"))
            await render(page, reddit_banner(), 1600, 480, os.path.join(BRAND_DIR, "reddit-banner-1600x480.png"))
            await render(page, reddit_banner(1920, 384, 118, 58), 1920, 384, os.path.join(BRAND_DIR, "reddit-banner-1920x384.png"))
            await render(page, reddit_avatar(), 512, 512, os.path.join(BRAND_DIR, "reddit-avatar-512.png"))
            await b.close()
    finally:
        server.terminate()
        for f in os.listdir(TMP):
            os.remove(os.path.join(TMP, f))
        os.rmdir(TMP)


if __name__ == "__main__":
    asyncio.run(main())
