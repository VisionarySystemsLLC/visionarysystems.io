#!/usr/bin/env python3
"""Builds the Visionary Systems static site into dist/ and an artifact variant into artifact/."""
import os, re, shutil, html

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
DIST = os.path.join(ROOT, "docs")
ART = os.path.join(ROOT, "artifact")

def fonts(prefix):
    return (f'<link rel="preload" as="font" type="font/woff2" crossorigin href="{prefix}assets/fonts/spectral-latin-400-normal.woff2">'
            f'<link rel="preload" as="font" type="font/woff2" crossorigin href="{prefix}assets/fonts/spectral-latin-500-normal.woff2">')
FONTS = fonts("")

BETA_URL = "https://research.sc/participant/login/dynamic/3AC727A6-CAA0-4049-9772-535E51EFFEBC"
REDDIT_PROFILE = "https://www.reddit.com/user/VisionarySystems/"
EMAIL = "morgan@visionarysystems.io"
SERIES_TOTAL = 8   # planned length of The Calibration Series; the published count comes from content/essays/

def mark_body(suffix):
    """The mark's masks and strokes, for use inside any SVG (the weave is identical to the kit's mark)."""
    return f'''<defs>
<mask id="rm-{suffix}"><rect width="200" height="200" fill="#fff"/><path d="M 67.3 129.44 A 44 44 0 0 0 132.7 129.44" stroke="#000" stroke-width="15" fill="none"/></mask>
<mask id="gm-{suffix}"><rect width="200" height="200" fill="#fff"/><ellipse cx="100" cy="100" rx="19" ry="79" stroke="#000" stroke-width="14" fill="none"/><path d="M 67.3 129.44 A 44 44 0 0 0 132.7 129.44" stroke="#fff" stroke-width="15" fill="none"/></mask>
</defs>
<ellipse cx="100" cy="100" rx="19" ry="79" stroke="var(--star)" stroke-width="6.5" fill="none" mask="url(#rm-{suffix})"/>
<circle cx="100" cy="100" r="44" stroke="var(--mark-gold, var(--gold))" stroke-width="10" fill="none" mask="url(#gm-{suffix})"/>'''

def mark(suffix, cls="mark", spark=False):
    # The spark rides the ring once every nine seconds and passes behind the lens where the ring does.
    orbit = "M 144 100 A 44 44 0 1 1 56 100 A 44 44 0 1 1 144 100"
    sp = (f'<g mask="url(#gm-{suffix})">'
          + "".join(f'<circle class="spark" r="{r}" fill="var(--gold-hot)" fill-opacity="{o}"><animateMotion dur="7.5s" begin="{b}s" repeatCount="indefinite" path="{orbit}"/></circle>'
                    for r, o, b in [(2.0, 0.25, -0.5), (2.8, 0.5, -0.25), (4.0, 1, 0)])
          + "</g>") if spark else ""
    return f'''<svg class="{cls}" viewBox="0 0 200 200" fill="none" aria-hidden="true" focusable="false">
{mark_body(suffix)}{sp}
</svg>'''

def observer(suffix, with_mark=True, cls="observer"):
    """The figure at the eyepiece from the brand kit, as inline SVG so it takes the page's colors."""
    sky = (f'<g class="obs-sky" transform="translate(293 17) scale(0.19)">{mark_body("ob" + suffix)}</g>') if with_mark else ""
    stars = "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}" fill-opacity="{o}"/>' for x, y, r, c, o in [
        (28, 38, 1.4, "var(--star)", 0.55), (74, 20, 1.1, "var(--star)", 0.45), (118, 52, 1.2, "var(--ion)", 0.7),
        (176, 30, 1.0, "var(--star)", 0.4), (300, 104, 1.3, "var(--star)", 0.5), (212, 64, 0.9, "var(--star)", 0.35),
        (52, 96, 1.0, "var(--gold)", 0.6), (262, 28, 1.1, "var(--ion)", 0.55), (326, 80, 0.9, "var(--star)", 0.4)])
    return f'''<figure class="{cls}" aria-hidden="true"><svg viewBox="0 0 340 236" fill="none">
{stars}{sky}
<ellipse cx="176" cy="214" rx="104" ry="6" fill="#000" fill-opacity="0.35"/>
<path d="M 92 212 L 92 158 Q 92 122 126 122 Q 160 122 160 158 L 160 212 Z" fill="var(--field-2)" stroke="var(--star)" stroke-width="5" stroke-linejoin="round"/>
<circle cx="126" cy="96" r="25" fill="var(--field-2)" stroke="var(--star)" stroke-width="5"/>
<path d="M 231 118 L 214 212 M 231 118 L 258 212" stroke="var(--mark-gold, var(--gold))" stroke-width="6" stroke-linecap="round"/>
<path d="M 190 160 L 272 77" stroke="var(--mark-gold, var(--gold))" stroke-width="9" stroke-linecap="round"/>
</svg></figure>'''

def horizon():
    """The planetary curve from the banner, drawn under the hero."""
    return '''<svg class="horizon" viewBox="0 0 1000 80" preserveAspectRatio="none" aria-hidden="true" focusable="false">
<defs><linearGradient id="hz" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5CE1FF" stop-opacity="0.11"/><stop offset="1" stop-color="#5CE1FF" stop-opacity="0"/></linearGradient></defs>
<path d="M0 80 L0 58 Q 500 -34 1000 58 L1000 80 Z" fill="url(#hz)"/>
<path d="M0 58 Q 500 -34 1000 58" fill="none" stroke="#5CE1FF" stroke-opacity="0.38" stroke-width="1" vector-effect="non-scaling-stroke"/>
</svg>'''

def profile_figure(short=False):
    """An illustrative profile: five coordinates, three tier rings, an uncertainty band. No real taker's data."""
    import math
    cx, cy = 360, 236
    R = 150
    axes = [("Gf", "Fluid reasoning", -90), ("Gc", "Crystallized density", -18), ("Gq", "Quantitative reasoning", 54),
            ("Gi", "Integrative, exploratory", 126), ("Gv", "Visuospatial reasoning", 198)]
    vals = [0.86, 0.62, 0.50, 0.60, 0.76]
    err  = [0.07, 0.10, 0.10, 0.15, 0.08]
    def pt(a, r):
        t = math.radians(a)
        return (cx + R * r * math.cos(t), cy + R * r * math.sin(t))
    out, tiers = [], []
    for i, (r, name) in enumerate([(0.33, "Gate"), (0.66, "Bridge"), (1.0, "Zenith")]):
        out.append(f'<circle class="ring" cx="{cx}" cy="{cy}" r="{R*r:.1f}"/>')
        # The name follows the lower arc of its ring, left to right, sitting just inside the line.
        (ax, ay), (bx, by) = pt(124, r), pt(56, r)   # the bottom sector, between the Gq and Gi axes, where the profile sits lowest
        out.append(f'<path id="tier-{i}" d="M {ax:.1f} {ay:.1f} A {R*r:.1f} {R*r:.1f} 0 0 0 {bx:.1f} {by:.1f}" fill="none"/>')
        tiers.append(f'<text class="tier" dy="-4"><textPath href="#tier-{i}" startOffset="50%" text-anchor="middle">{name}</textPath></text>')
    for (code, name, a), v in zip(axes, vals):
        x, y = pt(a, 1.0)
        cls = "axis axis-x" if code == "Gi" else "axis"
        out.append(f'<line class="{cls}" x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}"/>')
    out.extend(tiers)   # after the axes, before the band, so the names sit over the lines and under nothing
    outer = [pt(a, min(1.0, v + e)) for (_, _, a), v, e in zip(axes, vals, err)]
    inner = [pt(a, max(0.05, v - e)) for (_, _, a), v, e in zip(axes, vals, err)]
    band = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in outer) + " Z M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in inner) + " Z"
    out.append(f'<path class="band" d="{band}" fill-rule="evenodd"/>')
    shape = [pt(a, v) for (_, _, a), v in zip(axes, vals)]
    out.append('<path class="shape" d="M ' + " L ".join(f"{x:.1f} {y:.1f}" for x, y in shape) + ' Z"/>')
    for (code, name, a), (x, y) in zip(axes, shape):
        out.append(f'<circle class="{"pt-x" if code == "Gi" else "pt"}" cx="{x:.1f}" cy="{y:.1f}" r="4.2"/>')
    for code, name, a in axes:
        x, y = pt(a, 1.0)
        cos_a, sin_a = math.cos(math.radians(a)), math.sin(math.radians(a))
        anchor = "middle" if abs(cos_a) < 0.3 else ("start" if cos_a > 0 else "end")
        dx = 0 if anchor == "middle" else (14 if anchor == "start" else -14)
        if sin_a < -0.3:      # above the point: both lines sit clear of the ring
            dy_code, dy_name = -32, -14
        elif sin_a > 0.3:     # below the point
            dy_code, dy_name = 24, 42
        else:                 # beside the point
            dy_code, dy_name = -4, 14
        out.append(f'<text class="code" x="{x+dx:.1f}" y="{y+dy_code:.1f}" text-anchor="{anchor}">{code}</text>')
        out.append(f'<text x="{x+dx:.1f}" y="{y+dy_name:.1f}" text-anchor="{anchor}">{name}</text>')
    svg = f'<svg viewBox="0 0 720 440" role="img" aria-label="An illustrative profile: five coordinates plotted against the three tiers, with an uncertainty band around the line.">' + "".join(out) + "</svg>"
    cap = ("An illustrative profile, not a real taker's: one axis per coordinate, the three tiers as rings, and the uncertainty drawn in as a band."
           if short else
           "An illustrative profile, not a real taker's. Each axis is one coordinate, the rings are the three tiers, and the band around the line is the uncertainty the report carries with it. The dashed axis is the exploratory fifth coordinate.")
    return f'''<figure class="profile">{svg}
<figcaption>{cap}</figcaption></figure>'''


def header(current, prefix):
    links = [("scan", "The Scan", "scan.html"), ("visionary", "The Visionary", "visionary.html"), ("about", "About", "about.html")]
    nav = ""
    for key, label, href in links:
        cur = ' aria-current="page"' if key == current else ""
        nav += f'<a href="{prefix}{href}"{cur}>{label}</a>'
    return f'''<header class="site-header"><div class="wrap">
<a class="lockup" href="{prefix}index.html" aria-label="Visionary Systems home">{mark("h")}<span class="wordmark">Visionary <span>Systems</span></span></a>
<nav class="site-nav" aria-label="Site">{nav}</nav>
</div></header>'''

def footer(prefix):
    return f'''<footer class="site-footer">{horizon()}<div class="wrap">
<div>
<a class="lockup" href="{prefix}index.html" aria-label="Visionary Systems home">{mark("f")}<span class="wordmark">Visionary <span>Systems</span></span></a>
<div class="colophon">
<p>Provisional. Norms in calibration.</p>
<p>Visionary Systems LLC, Greenville, South Carolina. &copy; 2026.</p>
<p>Written and run by <a href="{prefix}about.html">one person</a>, with an AI assistant for drafting. The arguments, the verification, and the instrument are his.</p>
</div>
</div>
<nav aria-label="Footer">
<a href="{prefix}scan.html">The Visionary Psychometric Scan</a>
<a href="{prefix}visionary.html">The Visionary</a>
<a href="{prefix}about.html">About and contact</a>
<a href="{REDDIT_PROFILE}" rel="noopener">u/VisionarySystems on Reddit</a>
</nav>
</div></footer>'''

SCRIPT = r'''<script>
(function () {
  // Subscribe form: until the list is connected, explain instead of posting nowhere.
  var form = document.getElementById("subscribe-form");
  if (form) {
    form.addEventListener("submit", function (e) {
      if (form.getAttribute("action").indexOf("YOUR-BUTTONDOWN-USERNAME") !== -1) {
        e.preventDefault();
        var n = document.getElementById("subscribe-notice");
        if (n) { n.hidden = false; n.focus && n.focus(); }
      }
    });
  }
  // Copy buttons for the contact address.
  var buttons = document.querySelectorAll("[data-copy]");
  Array.prototype.forEach.call(buttons, function (b) {
    b.addEventListener("click", function () {
      var text = b.getAttribute("data-copy");
      var done = function () { b.textContent = "Copied"; setTimeout(function () { b.textContent = "Copy"; }, 1800); };
      var fallback = function () {
        var el = document.getElementById(b.getAttribute("data-target"));
        if (!el) return;
        var r = document.createRange(); r.selectNodeContents(el);
        var s = window.getSelection(); s.removeAllRanges(); s.addRange(r);
        b.textContent = "Selected";
        setTimeout(function () { b.textContent = "Copy"; }, 1800);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, fallback);
      } else { fallback(); }
    });
  });
  // Deep field behind the hero, laid out from a fixed seed so it is the same sky every visit.
  // A few stars twinkle; the loop runs only while the hero is on screen and motion is allowed.
  var c = document.getElementById("field");
  if (c && c.getContext) {
    var ctx = c.getContext("2d"), stars = [], W = 0, H = 0, pts = [], pivot = { x: 0, y: 0 };
    var motion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: no-preference)").matches;
    var OMEGA = 0.0092; // radians per second: one turn of the sky in about eleven minutes
    function seeded(s) { return function () { s = (s * 9301 + 49297) % 233280; return s / 233280; }; }
    function layout() {
      var r = c.getBoundingClientRect();
      if (!r.width || !r.height) return false;
      var dpr = Math.min(window.devicePixelRatio || 1, 2);
      W = r.width; H = r.height;
      c.width = Math.floor(W * dpr); c.height = Math.floor(H * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      // The sky turns around the mark, so the stars are laid out in a disc around it that covers the canvas at every angle.
      var m = document.querySelector(".hero-mark .mark"), mr = m && m.getBoundingClientRect();
      pivot = mr ? { x: mr.left + mr.width / 2 - r.left, y: mr.top + mr.height / 2 - r.top } : { x: W * 0.72, y: H * 0.5 };
      var far = 0, cs = [[0, 0], [W, 0], [0, H], [W, H]];
      for (var q = 0; q < 4; q++) far = Math.max(far, Math.hypot(cs[q][0] - pivot.x, cs[q][1] - pivot.y));
      var rnd = seeded(1618), n = Math.round(Math.PI * far * far / 7000);
      stars = [];
      for (var i = 0; i < n; i++) {
        var roll = rnd(), rad = far * Math.sqrt(rnd()), th = rnd() * 6.283, s = 0.5 + rnd() * 1.2, a = 0.10 + rnd() * 0.40;
        var col = roll > 0.95 ? "255,184,48" : roll > 0.85 ? "92,225,255" : "238,242,255";
        if (roll > 0.85) a = 0.75;
        stars.push({ x: rad * Math.cos(th), y: rad * Math.sin(th), s: s, c: col, a: a, tw: rnd() < 0.4, ph: rnd() * 6.283, rate: 0.8 + rnd() * 1.8 });
      }
      pts = [[0.06, 0.28], [0.11, 0.42], [0.16, 0.36], [0.2, 0.55], [0.17, 0.72]].map(function (p) { return [p[0] * W - pivot.x, p[1] * H - pivot.y]; });
      return true;
    }
    function draw(t) {
      ctx.clearRect(0, 0, W, H);
      ctx.save();
      ctx.translate(pivot.x, pivot.y);
      ctx.rotate(motion ? (t / 1000) * OMEGA : 0);
      for (var i = 0; i < stars.length; i++) {
        var st = stars[i], a = st.a, sz = st.s;
        if (st.tw && t) { var w = Math.sin(t / 1000 * st.rate + st.ph); a = st.a * (0.5 + 0.5 * w); sz = st.s * (0.9 + 0.2 * w); }
        ctx.beginPath(); ctx.arc(st.x, st.y, sz, 0, 6.283);
        ctx.fillStyle = "rgba(" + st.c + "," + a.toFixed(3) + ")"; ctx.fill();
      }
      ctx.strokeStyle = "rgba(92,225,255,0.26)"; ctx.lineWidth = 0.7; ctx.beginPath();
      for (var j = 0; j < pts.length; j++) { if (j === 0) ctx.moveTo(pts[j][0], pts[j][1]); else ctx.lineTo(pts[j][0], pts[j][1]); }
      ctx.stroke();
      for (var k = 0; k < pts.length; k++) { ctx.beginPath(); ctx.arc(pts[k][0], pts[k][1], k === 2 ? 1.8 : 1.3, 0, 6.283); ctx.fillStyle = k === 2 ? "rgba(255,184,48,0.75)" : k === 4 ? "rgba(92,225,255,0.7)" : "rgba(238,242,255,0.6)"; ctx.fill(); }
      ctx.restore();
    }
    var visible = true, running = false, last = 0;
    function loop(t) {
      if (!running) return;
      if (t - last > 33) { last = t; draw(t); }
      requestAnimationFrame(loop);
    }
    function start() { if (motion && visible && !document.hidden && !running) { running = true; requestAnimationFrame(loop); } }
    function stop() { running = false; }
    if (layout()) draw(0);
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (es) { visible = es[0].isIntersecting; visible ? start() : stop(); }).observe(c);
    }
    document.addEventListener("visibilitychange", function () { document.hidden ? stop() : start(); });
    start();
    var tm; window.addEventListener("resize", function () { clearTimeout(tm); tm = setTimeout(function () { if (layout()) draw(0); }, 150); });
  }
  // Sections rise into place as they enter the view.
  var reveals = document.querySelectorAll(".section, .essay-head .wrap, .notfound .wrap");
  if ("IntersectionObserver" in window && reveals.length) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); } });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    Array.prototype.forEach.call(reveals, function (el) { el.classList.add("reveal"); io.observe(el); });
  }
  // Reading progress on essay pages.
  var bar = document.querySelector(".progress span");
  if (bar) {
    var ticking = false;
    function measure() {
      var d = document.documentElement, max = d.scrollHeight - d.clientHeight;
      bar.style.transform = "scaleX(" + (max > 0 ? Math.min(1, d.scrollTop / max) : 0).toFixed(4) + ")";
      ticking = false;
    }
    window.addEventListener("scroll", function () { if (!ticking) { ticking = true; requestAnimationFrame(measure); } }, { passive: true });
    measure();
  }
  // Paper or navy on essay pages, remembered in this browser only.
  var toggles = document.querySelectorAll("[data-theme-toggle]");
  function label(b) { b.textContent = document.documentElement.getAttribute("data-theme") === "paper" ? "Read on navy" : "Read on paper"; }
  Array.prototype.forEach.call(toggles, function (b) {
    label(b);
    b.addEventListener("click", function () {
      var paper = document.documentElement.getAttribute("data-theme") === "paper";
      if (paper) document.documentElement.removeAttribute("data-theme"); else document.documentElement.setAttribute("data-theme", "paper");
      try { localStorage.setItem("vs-theme", paper ? "navy" : "paper"); } catch (e) {}
      Array.prototype.forEach.call(toggles, label);
    });
  });
})();
</script>'''

SITE = "https://visionarysystems.io"

def page(title, body, current, prefix="", description="", path="index.html", image="assets/og-image.png", themed=False):
    desc = html.escape(description) if description else "Visionary Systems builds the Visionary Psychometric Scan and publishes The Visionary."
    url = f"{SITE}/{path}" if path != "index.html" else f"{SITE}/"
    theme = '<script>try{if(localStorage.getItem("vs-theme")==="paper")document.documentElement.setAttribute("data-theme","paper")}catch(e){}</script>\n' if themed else ""
    head = '<script>document.documentElement.classList.add("js")</script>\n' + theme + f'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(title)}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#0A1628">
<link rel="canonical" href="{url}">
<link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml">
<link rel="icon" href="{prefix}assets/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="{prefix}assets/apple-touch-icon.png">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Visionary Systems">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/{image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{html.escape(title)}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{SITE}/{image}">
{fonts(prefix)}
<link rel="stylesheet" href="{prefix}style.css">'''
    return f'''<!doctype html>
<html lang="en">
<head>
{head}
</head>
<body>
{header(current, prefix)}
<main>
{body}
</main>
{footer(prefix)}
{SCRIPT}
</body>
</html>
'''

# ---------- Shared blocks ----------

def section(rail, content, attrs=""):
    """One rail-grid section: heading and label on the left, content on the right."""
    return f'<div class="wrap section"{attrs}>\n<div class="rail">{rail}</div>\n<div class="content">{content}</div>\n</div>'

def rail(h2, kicker=None):
    k = f'\n<p class="kicker">{kicker}</p>' if kicker else ""
    return f'<h2>{h2}</h2>{k}'

def page_head(eyebrow, h1, lede="", aside=""):
    l = f'\n<p class="lede">{lede}</p>' if lede else ""
    return f'<div class="wrap page-head">\n<div><p class="eyebrow">{eyebrow}</p>\n<h1>{h1}</h1>{l}</div>\n{aside}\n</div>'

def subscribe_block():
    return f'''<div class="subscribe">
<p>The Visionary launches in March 2027. The simplest way to hear about the first issue is to follow <a href="{REDDIT_PROFILE}" rel="noopener">u/VisionarySystems</a>, where every piece is announced. If you would rather get one email when it goes out, send a note to the address below and you will be added by hand.</p>
<div class="contact"><code id="issue-email">{EMAIL}</code><button type="button" data-copy="{EMAIL}" data-target="issue-email">Copy</button></div>
<p class="note">Your address is used for that one note and nothing else.</p>
</div>'''

def essay_list(prefix):
    items = ""
    for i, e in enumerate(ESSAYS, start=1):
        items += f'''<li><span class="num">{i} of {SERIES_TOTAL}</span>
<a class="title" href="{prefix}essays/{e["slug"]}.html">{html.escape(e["title"])}</a>
<div class="meta">{e["date"]}</div>
<p class="summary">{e["summary"]}</p></li>'''
    return f'<ol class="essays">{items}</ol>'

# ---------- Essays ----------
# One file per essay in content/essays/, named NN-slug.md. Header lines (title, date, link, summary),
# then a line of three dashes, then paragraphs separated by blank lines. Inline HTML is allowed.

CONTENT = os.path.join(ROOT, "content", "essays")

def load_essays():
    essays = []
    for name in sorted(os.listdir(CONTENT)):
        if not name.endswith(".md"):
            continue
        text = open(os.path.join(CONTENT, name), encoding="utf-8").read()
        head, _, body = text.partition("\n---\n")
        meta = {}
        for line in head.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        paras = [" ".join(p.split()) for p in re.split(r"\n\s*\n", body.strip()) if p.strip()]
        slug = re.sub(r"^\d+-", "", name[:-3])
        # A one-letter word such as the g in "measures of g" stays on the line of the word before it.
        title = re.sub(r" (g) ", "\u00a0\\1 ", meta["title"])
        essays.append({"slug": slug, "title": title, "date": meta["date"], "link": meta["link"],
                       "summary": meta["summary"], "paras": paras})
    return essays

ESSAYS = load_essays()

# ---------- Tier map SVG ----------

def tiermap():
    # Rows top to bottom: Zenith (10), Bridge (10), Gate (16). Rings drawn left to right.
    rows = [
        ("The Zenith", 10, "items 27 to 36", "intended range 145 to 160"),
        ("The Bridge", 10, "items 17 to 26", "intended range 130 to 145"),
        ("The Gate", 16, "items 1 to 16", "intended range 100 to 130"),
    ]
    W = 760
    left = 150
    step = 26
    out = []
    y = 34
    for i, (name, n, items, rng) in enumerate(rows):
        out.append(f'<text x="0" y="{y+5}" fill="var(--star)" font-size="16" font-family="Spectral, Georgia, serif">{name}</text>')
        out.append(f'<text x="0" y="{y+24}" fill="var(--slate)" font-size="12.5" font-family="Spectral, Georgia, serif">{items}</text>')
        stroke, alpha = [("var(--gold-hot)", "1"), ("var(--gold)", "0.85"), ("var(--gold)", "0.62")][i]
        for k in range(n):
            cx = left + 10 + k * step
            out.append(f'<circle cx="{cx}" cy="{y}" r="7" fill="none" stroke="{stroke}" stroke-opacity="{alpha}" stroke-width="2"/>')
        out.append(f'<text x="{W}" y="{y+5}" text-anchor="end" fill="var(--slate)" font-size="12.5" font-family="Spectral, Georgia, serif">{rng}</text>')
        if i < 2:
            thr = "13 of 26 correct to continue" if i == 0 else "8 of 16 correct to continue"
            ty = y + 48
            out.append(f'<line x1="{left}" x2="{W}" y1="{ty-14}" y2="{ty-14}" stroke="var(--ion)" stroke-opacity="0.45" stroke-width="1"/>')
            out.append(f'<text x="{left+10}" y="{ty+4}" fill="var(--ion)" font-size="12.5" font-style="italic" font-family="Spectral, Georgia, serif">{thr}</text>')
        y += 92 if i < 2 else 0
    H = y + 40
    svg = f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="The three tiers of the Scan: The Gate with 16 items, The Bridge with 10, and The Zenith with 10, with the thresholds to advance between them.">' + "".join(out) + "</svg>"
    return f'''<figure class="tiermap">{svg}
<figcaption>Each ring is one item. The ranges are design targets, stated in IQ points with SD = 15. They are what the calibration is testing, not what it has established.</figcaption></figure>'''

# ---------- Pages ----------

def index_page(prefix=""):
    body = f'''<section class="hero">
<canvas id="field" aria-hidden="true"></canvas>
{horizon()}
<div class="wrap">
<div class="hero-text">
<h1>What tests can and can't tell you.</h1>
<p class="lede">Visionary Systems is a small psychometrics observatory in Greenville, South Carolina. It builds the Visionary Psychometric Scan, an untimed reasoning instrument now in beta calibration, and it publishes The Visionary, a publication written from inside that calibration.</p>
<div class="actions">
<a class="button button-primary" href="{prefix}scan.html">How the Scan works</a>
<a class="button button-ghost" href="{prefix}visionary.html#subscribe">Get the first issue</a>
</div>
</div>
<div class="hero-mark">{mark("hero", spark=True)}</div>
</div>
</section>

<section class="band">
{section(rail("The Visionary Psychometric Scan", "Beta 2.0, in calibration since July 2026"), f'''<div class="facts">
<div class="fact"><div class="value">36 items, untimed</div><div class="label">Eight options each, paper and pencil allowed, adaptive after the first tier</div></div>
<div class="fact"><div class="value">Five coordinates</div><div class="label">Fluid, crystallized, visuospatial, quantitative, and integrative reasoning</div></div>
<div class="fact"><div class="value">Three tiers</div><div class="label">The Gate, The Bridge, and The Zenith, each harder than the last</div></div>
</div>
<div class="prose">
<p>The Scan measures reasoning in a high and narrow band and says so. It sets no clock, requires no outside knowledge, and reports the shape of your reasoning rather than a single number. Most people who start it will not clear The Gate, and the report is written with that in mind: the floor of the instrument is not the floor of the person.</p>
<p><a href="{prefix}scan.html">Read how the Scan is built, what it measures, and how to take the Beta.</a></p>
</div>''')}
</section>

<section class="band band-raised">
{section(rail("The Visionary", "Launching March 2027"), f'''<div class="prose">
<p>The Visionary writes about psychometrics, norming, and the questions an instrument raises while it is being built. It launches in March 2027. Until then, The Calibration Series runs here as its precursor: a series of pieces about building and calibrating the Scan, posted first on r/cognitiveTesting, where the arguments get tested in the comments, and archived here with their original dates.</p>
</div>
{essay_list(prefix)}
<p><a href="{prefix}visionary.html">About the publication, The Scrolls, and how to subscribe.</a></p>''')}
</section>

<section class="band">
{section(rail("Calibration, in public", "As of the September calibration note"), f'''<div class="facts">
<div class="fact"><div class="value">47</div><div class="label">people had started the Beta</div></div>
<div class="fact"><div class="value">8</div><div class="label">had completed all 36 items</div></div>
<div class="fact"><div class="value">6</div><div class="label">had reached The Zenith, and all 6 finished</div></div>
</div>
<div class="prose">
<p>Where people stop, how long items take, and what the data says the design got wrong are published as the calibration goes, rather than after it. Nobody publishes their norming in real time; this project does, because the error bars are the product.</p>
<p><a href="{prefix}essays/calibration-remarks.html">Read the September calibration note.</a></p>
</div>''')}
</section>'''
    return page("Visionary Systems", body, "home", prefix,
                "Visionary Systems builds the Visionary Psychometric Scan, an untimed reasoning instrument in beta calibration, and publishes The Visionary.", "index.html")

def scan_page(prefix=""):
    body = f'''<section class="band band-page">
{page_head("The instrument", "The Visionary Psychometric Scan", "An untimed, adaptive reasoning battery built for the high range, in beta calibration since July 2026.", profile_figure(short=True))}
{section('<p class="kicker">Beta 2.0, in calibration since July 2026</p>', f'''<div class="prose">
<p>The Scan is 36 items long, with eight options per item. It is administered online, on a computer, with paper and pencil allowed and no clock of any kind. It adapts after the first tier, so most takers see fewer than 36 items. It asks for no outside knowledge, and its report describes the shape of a person's reasoning rather than producing one number to rank them by.</p>
</div>''')}

{section(rail("What it measures", "Five coordinates"), '''<dl class="coords">
<div><dt>Fluid reasoning <small>Gf</small></dt><dd>Finding the rule in material you have never seen before, and applying it.</dd></div>
<div><dt>Crystallized density <small>Gc</small></dt><dd>Precision with concepts you already hold: arbitrating between near meanings and reading structure in passages. Breadth of knowledge is deliberately not what this coordinate counts.</dd></div>
<div><dt>Visuospatial reasoning <small>Gv</small></dt><dd>Holding and transforming spatial structure without a clock running.</dd></div>
<div><dt>Quantitative reasoning <small>Gq</small></dt><dd>Reasoning about quantity and relation, with arithmetic kept out of the way as far as the format allows.</dd></div>
<div><dt>Integrative intelligence <small>Gi, exploratory</small></dt><dd>Reasoning across domains at once. This coordinate is treated as exploratory until the calibration data earns it more than that, and it will be reported as such.</dd></div>
</dl>''')}

{section(rail("How it is built", "Three tiers, 36 items"), f'''<div class="prose">
<p>The items climb through three tiers. The Gate starts near average difficulty and climbs quickly, so most takers strain from the first items. Clearing it opens The Bridge, and clearing that opens The Zenith. During the Beta, advancement is decided on total score; the intended design advances takers domain by domain, and that is one of the changes the calibration will inform.</p>
</div>
{tiermap()}''')}

{section(rail("Three choices that set it apart"), f'''<div class="choices">
<div><h3>No clock</h3>
<p>Timing constraints reward speed, and speed is not the ability the Scan exists to measure. Removing the clock and allowing a scratchpad takes cognitive proficiency out of the equation as far as a reasoning instrument can, which matters most for people with uneven profiles, whose reasoning often needs more time to show up than a timed format allows. The costs are real, and they are stated: fixation on a hard item, the opportunity to consult a model, and fatigue over a long session. <a href="{prefix}essays/speed-is-not-ability.html">The full argument is in the publication.</a></p></div>
<div><h3>No outside knowledge</h3>
<p>Nothing on the Scan rewards having read the right book. Where a coordinate touches language, it tests inference from the material in front of you rather than recall of material you brought with you.</p></div>
<div><h3>A fifth coordinate</h3>
<p>Integrative intelligence, meaning reasoning across domains, is included as a coordinate because the ability seems real and underexamined. It ships labeled exploratory, and it stays labeled that way until the data says otherwise.</p></div>
</div>''')}

{section(rail("Taking the Beta", "Open through the winter"), f'''<div class="prose">
<p>The Beta is open through the winter. It is hard from the first items, most people will not clear The Gate, and it takes 45 to 90 minutes on a computer. A quiet hour, a sheet of paper, and a willingness to be stumped are the whole kit.</p>
<ul class="rules">
<li>You must be 18 or older.</li>
<li>Work alone, without search engines, AI tools, or calculators.</li>
<li>Use a computer. Phones do not render the items well.</li>
<li>Please do not discuss specific item content with anyone afterward.</li>
</ul>
<p>Beta takers receive a preliminary profile report by email. Because the norms are exactly what this phase is building, the report describes the shape of your reasoning instead of a population-relative score, and every Beta taker receives an updated report once the norms mature.</p>
<div class="actions">
<a class="button button-primary" href="{BETA_URL}" rel="noopener">Take the Beta</a>
</div>
<p style="margin-top:1.4rem">The floor of the instrument is not the floor of the person. If your session ends early, the report will say exactly that.</p>
</div>''')}

{section(rail("What it cannot tell you yet"), '''<div class="prose">
<p>The Scan is not a clinical instrument and is not designed for selection decisions by employers, schools, or anyone else. Its norms are provisional and will be published as provisional, with the sample described and the error bars visible, until the data earns stronger claims. Resistance to language models is treated as an open problem under test rather than a feature, which is why process-level checks run on every session. A technical report will be published alongside version 1.0.</p>
</div>''')}

{section(rail("Calibration notes", "As of September 2026"), f'''<div class="prose">
<p>As of the September calibration note, 47 people had started the Beta, 8 had finished, and 6 had reached The Zenith. Most people who stop do so on the forms before the first item or at the second item, which is the instrument's floor doing what it was designed to do and also a sign that the on-ramp is too long. Both facts are published, because that is the point.</p>
<p><a href="{prefix}essays/calibration-remarks.html">The September calibration note has the full numbers.</a></p>
</div>''')}
</section>'''
    return page("The Visionary Psychometric Scan", body, "scan", prefix,
                "An untimed, adaptive reasoning battery for the high range, in beta calibration. What it measures, how it is built, and how to take the Beta.", "scan.html")

def visionary_page(prefix=""):
    body = f'''<section class="band band-page">
{page_head("The publication", "The Visionary", "A publication on psychometrics, written from inside an instrument's calibration.", observer("pub"))}
{section('<p class="kicker">Launching March 2027</p>', '''<div class="prose">
<p>Most writing about intelligence testing is written by people who have never had to norm anything. The Visionary is written by someone who is in the middle of it, with the dropout tables and the item statistics on the desk. It covers what tests can and can't tell you, which parts of the field's orthodoxy survive contact with data, and what the Scan's own calibration turns up as it goes.</p>
<p>The Visionary launches in March 2027. The Calibration Series is its precursor: a series of pieces about building and calibrating the Scan, posted first on r/cognitiveTesting, where the arguments get tested in the comments, and archived here. The series runs until launch, and the launch builds on it.</p>
<p>Visionaries are those who care to look through the instrument, to see beyond.</p>
</div>''')}

{section(rail("The Calibration Series", f"{len(ESSAYS)} of {SERIES_TOTAL} published"), essay_list(prefix))}

{section(rail("The Scrolls", "A companion canon"), '''<div class="prose">
<p>Each quarter, The Visionary reads one text alongside its readers and writes toward it. That companion canon is called The Scrolls, and its first entry is named with the first issue.</p>
</div>''')}

{section(rail("The first issue", "March 2027"), subscribe_block(), ' id="subscribe"')}
</section>'''
    return page("The Visionary", body, "visionary", prefix,
                "The Visionary is a publication on psychometrics, written from inside the calibration of an untimed reasoning instrument. Launching March 2027, with The Calibration Series as its precursor.", "visionary.html")

def about_page(prefix=""):
    body = f'''<section class="band band-page">
{page_head("The company", "About", "Visionary Systems is a one-person psychometrics observatory in Greenville, South Carolina, founded in 2026.", '''<div class="facts">
<div class="fact"><div class="value">2026</div><div class="label">founded</div></div>
<div class="fact"><div class="value">Greenville</div><div class="label">South Carolina</div></div>
<div class="fact"><div class="value">One instrument</div><div class="label">the Visionary Psychometric Scan</div></div>
<div class="fact"><div class="value">One periodical</div><div class="label">The Visionary</div></div>
</div>''')}
{section('<p class="kicker">One conviction</p>', '''<div class="prose">
<p>The company builds one instrument, the Visionary Psychometric Scan, and publishes one periodical, The Visionary. Both run on the same conviction: measurement earns trust by showing its error bars, treating a score of 105 with the same rigor as a score of 130, and telling people plainly what a result cannot say about them.</p>
</div>''')}

{section(rail("The founder") + observer("abt"), '''<div class="prose">
<p>The founder goes by Morgan. He came to psychometrics the way most of its enthusiasts do, by finding the testing communities online in early 2025 and reading past the point of casual interest. The Scan began as a question about what the standard batteries leave out, particularly for people with uneven profiles, and became an instrument when no existing test answered it.</p>
</div>''')}

{section(rail("How this is made"), '''<div class="prose">
<p>The Scan's items were built with AI assistance and vetted by hand; they are original to the instrument and drawn from no existing test. The writing is drafted with an AI assistant as well. The arguments, the verification, and the decisions are the founder's, and anything on this site that can be checked is meant to be.</p>
</div>''')}

{section(rail("Contact"), f'''<div class="prose">
<p>Questions about the Scan, the publication, or the calibration are welcome. Replies come from a person.</p>
<div class="contact"><code id="contact-email">{EMAIL}</code><button type="button" data-copy="{EMAIL}" data-target="contact-email">Copy</button></div>
<p style="margin-top:1.2rem">The founder also writes as <a href="{REDDIT_PROFILE}" rel="noopener">u/VisionarySystems</a> on Reddit, where The Calibration Series is first published.</p>
</div>''')}
</section>'''
    return page("About Visionary Systems", body, "about", prefix,
                "Visionary Systems is a one-person psychometrics observatory in Greenville, South Carolina, founded in 2026.", "about.html")

def notfound_page():
    # Served by GitHub Pages for any missing path, at any depth, so every link is absolute.
    body = f'''<section class="notfound"><div class="wrap">
{observer("nf", with_mark=False)}
<h1>Nothing at this address.</h1>
<p>The page may have moved when the site was rebuilt. <a href="/">The home page</a> has everything that exists.</p>
</div></section>'''
    return page("Page not found", body, "none", "/", "Nothing at this address.", "404.html")

def series_nav(current_slug, prefix):
    items = ""
    for e in ESSAYS:
        cur = ' aria-current="page"' if e["slug"] == current_slug else ""
        items += f'<li><a href="{prefix}essays/{e["slug"]}.html"{cur}>{html.escape(e["title"])}</a></li>'
    return f'<p class="rail-label">In this series</p><ol class="series-nav">{items}</ol>'

def essay_page(e, index):
    prefix = "../"
    paras = "\n".join(f"<p>{p}</p>" for p in e["paras"])
    body = f'''<div class="progress" aria-hidden="true"><span></span></div>
<article>
<header class="essay-head"><div class="wrap">
<div class="topline"><p class="eyebrow">The Calibration Series, {index} of {SERIES_TOTAL}</p>
<button type="button" class="theme-toggle" data-theme-toggle aria-label="Switch between the navy and paper themes">Read on paper</button></div>
<h1>{html.escape(e["title"])}</h1>
<p class="meta">{e["date"]}. Originally posted to <a href="{e["link"]}" rel="noopener">r/cognitiveTesting</a>, where the discussion took place.</p>
</div></header>
<div class="essay-body">
{section(series_nav(e["slug"], prefix), f'<div class="prose">\n{paras}\n</div>')}
</div>
<footer class="essay-foot">
{section("", f'''<div class="prose">
<p>Part of <a href="{prefix}visionary.html">The Visionary</a>. The instrument discussed here is the <a href="{prefix}scan.html">Visionary Psychometric Scan</a>, in beta calibration.</p>
</div>''')}
</footer>
</article>'''
    return page(e["title"], body, "visionary", prefix, e["summary"], f"essays/{e['slug']}.html",
                image=f"assets/og/{e['slug']}.png", themed=True)

# ---------- Build ----------

def build():
    for d in (DIST, ART):
        if os.path.isdir(d):
            shutil.rmtree(d)
        os.makedirs(os.path.join(d, "essays"))
    css = open(os.path.join(SRC, "style.css"), encoding="utf-8").read()

    pages = {
        "404.html": notfound_page(),
        "index.html": index_page(),
        "scan.html": scan_page(),
        "visionary.html": visionary_page(),
        "about.html": about_page(),
    }
    for i, e in enumerate(ESSAYS, start=1):
        pages[f"essays/{e['slug']}.html"] = essay_page(e, i)

    for name, content in pages.items():
        with open(os.path.join(DIST, name), "w", encoding="utf-8") as f:
            f.write(content)
    shutil.copy(os.path.join(SRC, "style.css"), os.path.join(DIST, "style.css"))
    open(os.path.join(DIST, "CNAME"), "w").write("visionarysystems.io\n")
    open(os.path.join(DIST, ".nojekyll"), "w").write("")
    shutil.copytree(os.path.join(SRC, "assets"), os.path.join(DIST, "assets"))
    open(os.path.join(DIST, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    urls = [n for n in pages if n != "404.html"]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for n in urls:
        loc = f"{SITE}/" if n == "index.html" else f"{SITE}/{n}"
        sm.append(f"  <url><loc>{loc}</loc></url>")
    sm.append("</urlset>")
    open(os.path.join(DIST, "sitemap.xml"), "w").write("\n".join(sm) + "\n")

    # Artifact variant: same pages, except index is published without a document skeleton
    # (the Artifact tool wraps it) and with the stylesheet inlined.
    for name, content in pages.items():
        if name == "index.html":
            m = re.search(r"<body>\s*(.*?)\s*</body>", content, re.S)
            inner = m.group(1)
            art = ("<title>Visionary Systems</title>\n"
                   '<meta name="claude:viewport-fit-sides" content="cover">\n'
                   + "<style>\n" + css + "\n</style>\n" + inner + "\n")
            content = art
        with open(os.path.join(ART, name), "w", encoding="utf-8") as f:
            f.write(content)
    shutil.copy(os.path.join(SRC, "style.css"), os.path.join(ART, "style.css"))
    shutil.copytree(os.path.join(SRC, "assets"), os.path.join(ART, "assets"))
    print("built", len(pages), "pages")

if __name__ == "__main__":
    build()
