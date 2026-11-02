#!/usr/bin/env python3
"""Builds the Visionary Systems static site into dist/ and an artifact variant into artifact/."""
import os, re, shutil, html

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
DIST = os.path.join(ROOT, "docs")
ART = os.path.join(ROOT, "artifact")

FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Spectral:ital,wght@0,400;0,500;0,600;1,400&amp;display=swap">'

BETA_URL = "https://research.sc/participant/login/dynamic/3AC727A6-CAA0-4049-9772-535E51EFFEBC"
REDDIT_PROFILE = "https://www.reddit.com/user/VisionarySystems/"
EMAIL = "morgan@visionarysystems.io"

def mark(suffix, cls="mark"):
    return f'''<svg class="{cls}" viewBox="0 0 200 200" fill="none" aria-hidden="true" focusable="false">
<defs>
<mask id="rm-{suffix}"><rect width="200" height="200" fill="#fff"/><path d="M 67.3 129.44 A 44 44 0 0 0 132.7 129.44" stroke="#000" stroke-width="15" fill="none"/></mask>
<mask id="gm-{suffix}"><rect width="200" height="200" fill="#fff"/><ellipse cx="100" cy="100" rx="19" ry="79" stroke="#000" stroke-width="14" fill="none"/><path d="M 67.3 129.44 A 44 44 0 0 0 132.7 129.44" stroke="#fff" stroke-width="15" fill="none"/></mask>
</defs>
<ellipse cx="100" cy="100" rx="19" ry="79" stroke="var(--star)" stroke-width="6.5" fill="none" mask="url(#rm-{suffix})"/>
<circle cx="100" cy="100" r="44" stroke="var(--gold)" stroke-width="10" fill="none" mask="url(#gm-{suffix})"/>
</svg>'''

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
    return f'''<footer class="site-footer"><div class="wrap">
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
  // Deep field behind the hero, drawn once from a fixed seed so it is the same sky every visit.
  var c = document.getElementById("field");
  if (c && c.getContext) {
    var ctx = c.getContext("2d");
    function seeded(s) { return function () { s = (s * 9301 + 49297) % 233280; return s / 233280; }; }
    function draw() {
      var r = c.getBoundingClientRect();
      if (!r.width || !r.height) return;
      var dpr = Math.min(window.devicePixelRatio || 1, 2);
      c.width = Math.floor(r.width * dpr); c.height = Math.floor(r.height * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, r.width, r.height);
      var rnd = seeded(1618);
      var n = Math.round(r.width * r.height / 7000);
      for (var i = 0; i < n; i++) {
        var x = rnd() * r.width, y = rnd() * r.height, s = 0.5 + rnd() * 1.2, roll = rnd();
        ctx.beginPath(); ctx.arc(x, y, s, 0, Math.PI * 2);
        ctx.fillStyle = roll > 0.95 ? "rgba(255,184,48,0.8)" : "rgba(238,242,255," + (0.10 + rnd() * 0.40).toFixed(2) + ")";
        ctx.fill();
      }
      var pts = [[0.06, 0.28], [0.11, 0.42], [0.16, 0.36], [0.2, 0.55], [0.17, 0.72]];
      ctx.strokeStyle = "rgba(139,154,173,0.22)"; ctx.lineWidth = 0.6; ctx.beginPath();
      for (var j = 0; j < pts.length; j++) { var px = pts[j][0] * r.width, py = pts[j][1] * r.height; if (j === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py); }
      ctx.stroke();
      for (var k = 0; k < pts.length; k++) { ctx.beginPath(); ctx.arc(pts[k][0] * r.width, pts[k][1] * r.height, k === 2 ? 1.8 : 1.3, 0, Math.PI * 2); ctx.fillStyle = k === 2 ? "rgba(255,184,48,0.75)" : "rgba(238,242,255,0.6)"; ctx.fill(); }
    }
    draw();
    var t; window.addEventListener("resize", function () { clearTimeout(t); t = setTimeout(draw, 150); });
  }
})();
</script>'''

def page(title, body, current, prefix="", description=""):
    desc = f'<meta name="description" content="{html.escape(description)}">' if description else ""
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(title)}</title>
{desc}
{FONTS}
<link rel="stylesheet" href="{prefix}style.css">
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

def subscribe_block():
    return f'''<div class="subscribe">
<h2>The first issue</h2>
<p>The Visionary launches in March 2027. The simplest way to hear about the first issue is to follow <a href="{REDDIT_PROFILE}" rel="noopener">u/VisionarySystems</a>, where every piece is announced. If you would rather get one email when it goes out, send a note to the address below and you will be added by hand.</p>
<div class="contact"><code id="issue-email">{EMAIL}</code><button type="button" data-copy="{EMAIL}" data-target="issue-email">Copy</button></div>
<p class="note">Your address is used for that one note and nothing else.</p>
</div>'''

def essay_list(prefix):
    items = ""
    for i, e in enumerate(ESSAYS, start=1):
        items += f'''<li><span class="num">{i} of {len(ESSAYS)}</span>
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
        essays.append({"slug": slug, "title": meta["title"], "date": meta["date"], "link": meta["link"],
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
        for k in range(n):
            cx = left + 10 + k * step
            out.append(f'<circle cx="{cx}" cy="{y}" r="7" fill="none" stroke="var(--gold)" stroke-width="2"/>')
        out.append(f'<text x="{W}" y="{y+5}" text-anchor="end" fill="var(--slate)" font-size="12.5" font-family="Spectral, Georgia, serif">{rng}</text>')
        if i < 2:
            thr = "13 of 26 correct to continue" if i == 0 else "8 of 16 correct to continue"
            ty = y + 48
            out.append(f'<line x1="{left}" x2="{W}" y1="{ty-14}" y2="{ty-14}" stroke="var(--line)" stroke-width="1"/>')
            out.append(f'<text x="{left+10}" y="{ty+4}" fill="var(--slate)" font-size="12.5" font-style="italic" font-family="Spectral, Georgia, serif">{thr}</text>')
        y += 92 if i < 2 else 0
    H = y + 40
    svg = f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="The three tiers of the Scan: The Gate with 16 items, The Bridge with 10, and The Zenith with 10, with the thresholds to advance between them.">' + "".join(out) + "</svg>"
    return f'''<figure class="tiermap">{svg}
<figcaption>Each ring is one item. The ranges are design targets, stated in IQ points with SD = 15. They are what the calibration is testing, not what it has established.</figcaption></figure>'''

# ---------- Pages ----------

def index_page(prefix=""):
    body = f'''<section class="hero">
<canvas id="field" aria-hidden="true"></canvas>
<div class="wrap">
<div class="hero-text">
<h1>What tests can and can't tell you.</h1>
<p class="lede">Visionary Systems is a small psychometrics observatory in Greenville, South Carolina. It builds the Visionary Psychometric Scan, an untimed reasoning instrument now in beta calibration, and it publishes The Visionary, a magazine written from inside that calibration.</p>
<div class="actions">
<a class="button button-primary" href="{prefix}scan.html">How the Scan works</a>
<a class="button button-ghost" href="{prefix}visionary.html#subscribe">Get the first issue</a>
</div>
</div>
<div class="hero-mark">{mark("hero")}</div>
</div>
</section>

<section class="band"><div class="wrap">
<div class="band-head">
<h2>The Visionary Psychometric Scan</h2>
<p class="kicker">Beta 2.0, in calibration since July 2026</p>
</div>
<div class="facts">
<div class="fact"><div class="value">36 items, untimed</div><div class="label">Eight options each, paper and pencil allowed, adaptive after the first tier</div></div>
<div class="fact"><div class="value">Five coordinates</div><div class="label">Fluid, crystallized, visuospatial, quantitative, and integrative reasoning</div></div>
<div class="fact"><div class="value">Three tiers</div><div class="label">The Gate, The Bridge, and The Zenith, each harder than the last</div></div>
</div>
<div class="prose">
<p>The Scan measures reasoning in a high and narrow band and says so. It sets no clock, requires no outside knowledge, and reports the shape of your reasoning rather than a single number. Most people who start it will not clear The Gate, and the report is written with that in mind: the floor of the instrument is not the floor of the person.</p>
<p><a href="{prefix}scan.html">Read how the Scan is built, what it measures, and how to take the Beta.</a></p>
</div>
</div></section>

<section class="band band-raised"><div class="wrap">
<div class="band-head">
<h2>The Visionary</h2>
<p class="kicker">Launching March 2027</p>
</div>
<div class="prose">
<p>The Visionary writes about psychometrics, norming, and the questions an instrument raises while it is being built. It launches in March 2027. Until then, The Calibration Series runs here as its precursor: one piece a month about building and calibrating the Scan, posted first on r/cognitiveTesting, where the arguments get tested in the comments, and archived here with its original date.</p>
</div>
<div style="margin-top:1.6rem">{essay_list(prefix)}</div>
<p style="margin-top:1.4rem"><a href="{prefix}visionary.html">About the publication, The Scrolls, and how to subscribe.</a></p>
</div></section>

<section class="band"><div class="wrap">
<div class="band-head">
<h2>Calibration, in public</h2>
<p class="kicker">As of the September calibration note</p>
</div>
<div class="facts">
<div class="fact"><div class="value">47</div><div class="label">people had started the Beta</div></div>
<div class="fact"><div class="value">8</div><div class="label">had completed all 36 items</div></div>
<div class="fact"><div class="value">6</div><div class="label">had reached The Zenith, and all 6 finished</div></div>
</div>
<div class="prose">
<p>Where people stop, how long items take, and what the data says the design got wrong are published as the calibration goes, rather than after it. Nobody publishes their norming in real time; this project does, because the error bars are the product.</p>
<p><a href="{prefix}essays/calibration-remarks.html">Read the September calibration note.</a></p>
</div>
</div></section>'''
    return page("Visionary Systems", body, "home", prefix,
                "Visionary Systems builds the Visionary Psychometric Scan, an untimed reasoning instrument in beta calibration, and publishes The Visionary.")

def scan_page(prefix=""):
    body = f'''<section class="band"><div class="wrap">
<div class="band-head">
<h1>The Visionary Psychometric Scan</h1>
<p class="lede">An untimed, adaptive reasoning battery built for the high range, in beta calibration since July 2026.</p>
</div>
<div class="prose">
<p>The Scan is 36 items long, with eight options per item. It is administered online, on a computer, with paper and pencil allowed and no clock of any kind. It adapts after the first tier, so most takers see fewer than 36 items. It asks for no outside knowledge, and its report describes the shape of a person's reasoning rather than producing one number to rank them by.</p>
</div>

<h2 style="margin-top:2.6rem">What it measures</h2>
<dl class="coords">
<div><dt>Fluid reasoning <small>Gf</small></dt><dd>Finding the rule in material you have never seen before, and applying it.</dd></div>
<div><dt>Crystallized density <small>Gc</small></dt><dd>Precision with concepts you already hold: arbitrating between near meanings and reading structure in passages. Breadth of knowledge is deliberately not what this coordinate counts.</dd></div>
<div><dt>Visuospatial reasoning <small>Gv</small></dt><dd>Holding and transforming spatial structure without a clock running.</dd></div>
<div><dt>Quantitative reasoning <small>Gq</small></dt><dd>Reasoning about quantity and relation, with arithmetic kept out of the way as far as the format allows.</dd></div>
<div><dt>Integrative intelligence <small>Gi, exploratory</small></dt><dd>Reasoning across domains at once. This coordinate is treated as exploratory until the calibration data earns it more than that, and it will be reported as such.</dd></div>
</dl>

<h2 style="margin-top:2.6rem">How it is built</h2>
<div class="prose">
<p>The items climb through three tiers. The Gate starts near average difficulty and climbs quickly, so most takers strain from the first items. Clearing it opens The Bridge, and clearing that opens The Zenith. During the Beta, advancement is decided on total score; the intended design advances takers domain by domain, and that is one of the changes the calibration will inform.</p>
</div>
{tiermap()}

<h2 style="margin-top:2.6rem">Three choices that set it apart</h2>
<div class="prose">
<h3>No clock</h3>
<p>Timing constraints reward speed, and speed is not the ability the Scan exists to measure. Removing the clock and allowing a scratchpad takes cognitive proficiency out of the equation as far as a reasoning instrument can, which matters most for people with uneven profiles, whose reasoning often needs more time to show up than a timed format allows. The costs are real, and they are stated: fixation on a hard item, the opportunity to consult a model, and fatigue over a long session. <a href="{prefix}essays/speed-is-not-ability.html">The full argument is in the publication.</a></p>
<h3>No outside knowledge</h3>
<p>Nothing on the Scan rewards having read the right book. Where a coordinate touches language, it tests inference from the material in front of you rather than recall of material you brought with you.</p>
<h3>A fifth coordinate</h3>
<p>Integrative intelligence, meaning reasoning across domains, is included as a coordinate because the ability seems real and underexamined. It ships labeled exploratory, and it stays labeled that way until the data says otherwise.</p>
</div>

<h2 style="margin-top:2.6rem">Taking the Beta</h2>
<div class="prose">
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
</div>

<h2 style="margin-top:2.6rem">What it cannot tell you yet</h2>
<div class="prose">
<p>The Scan is not a clinical instrument and is not designed for selection decisions by employers, schools, or anyone else. Its norms are provisional and will be published as provisional, with the sample described and the error bars visible, until the data earns stronger claims. Resistance to language models is treated as an open problem under test rather than a feature, which is why process-level checks run on every session. A technical report will be published alongside version 1.0.</p>
</div>

<h2 style="margin-top:2.6rem">Calibration notes</h2>
<div class="prose">
<p>As of the September calibration note, 47 people had started the Beta, 8 had finished, and 6 had reached The Zenith. Most people who stop do so on the forms before the first item or at the second item, which is the instrument's floor doing what it was designed to do and also a sign that the on-ramp is too long. Both facts are published, because that is the point.</p>
<p><a href="{prefix}essays/calibration-remarks.html">The September calibration note has the full numbers.</a></p>
</div>
</div></section>'''
    return page("The Visionary Psychometric Scan", body, "scan", prefix,
                "An untimed, adaptive reasoning battery for the high range, in beta calibration. What it measures, how it is built, and how to take the Beta.")

def visionary_page(prefix=""):
    body = f'''<section class="band"><div class="wrap">
<div class="band-head">
<h1>The Visionary</h1>
<p class="lede">A magazine about psychometrics, written from inside an instrument's calibration.</p>
</div>
<div class="prose">
<p>Most writing about intelligence testing is written by people who have never had to norm anything. The Visionary is written by someone who is in the middle of it, with the dropout tables and the item statistics on the desk. It covers what tests can and can't tell you, which parts of the field's orthodoxy survive contact with data, and what the Scan's own calibration turns up as it goes.</p>
<p>The Visionary launches in March 2027. The Calibration Series is its precursor: one piece a month about building and calibrating the Scan, posted first on r/cognitiveTesting, where the arguments get tested in the comments, and archived here. The series runs until launch, and the launch builds on it.</p>
</div>

<h2 style="margin-top:2.4rem">The Calibration Series</h2>
<div style="margin-top:1.2rem">{essay_list(prefix)}</div>

<h2 style="margin-top:2.6rem">The Scrolls</h2>
<div class="prose">
<p>Each quarter, The Visionary reads one text alongside its readers and writes toward it. That companion canon is called The Scrolls, and its first entry is named with the first issue.</p>
</div>

<div id="subscribe" style="margin-top:2.6rem">{subscribe_block()}</div>
</div></section>'''
    return page("The Visionary", body, "visionary", prefix,
                "The Visionary is a magazine about psychometrics, written from inside the calibration of an untimed reasoning instrument. Launching March 2027, with The Calibration Series as its precursor.")

def about_page(prefix=""):
    body = f'''<section class="band"><div class="wrap">
<div class="band-head">
<h1>About</h1>
<p class="lede">Visionary Systems is a one-person psychometrics company in Greenville, South Carolina, founded in 2026.</p>
</div>
<div class="prose">
<p>The company builds one instrument, the Visionary Psychometric Scan, and publishes one magazine, The Visionary. Both run on the same conviction: measurement earns trust by showing its error bars, treating a score of 105 with the same rigor as a score of 130, and telling people plainly what a result cannot say about them.</p>

<h2>The founder</h2>
<p>The founder goes by Morgan. He came to psychometrics the way most of its enthusiasts do, by finding the testing communities online in early 2025 and reading past the point of casual interest. The Scan began as a question about what the standard batteries leave out, particularly for people with uneven profiles, and became an instrument when no existing test answered it.</p>

<h2>How this is made</h2>
<p>The Scan's items were built with AI assistance and vetted by hand; they are original to the instrument and drawn from no existing test. The writing is drafted with an AI assistant as well. The arguments, the verification, and the decisions are the founder's, and anything on this site that can be checked is meant to be.</p>

<h2>Contact</h2>
<p>Questions about the Scan, the publication, or the calibration are welcome. Replies come from a person.</p>
<div class="contact"><code id="contact-email">{EMAIL}</code><button type="button" data-copy="{EMAIL}" data-target="contact-email">Copy</button></div>
<p style="margin-top:1.2rem">The founder also writes as <a href="{REDDIT_PROFILE}" rel="noopener">u/VisionarySystems</a> on Reddit, where the calibration series was first published.</p>
</div>
</div></section>'''
    return page("About Visionary Systems", body, "about", prefix,
                "Visionary Systems is a one-person psychometrics company in Greenville, South Carolina, founded in 2026.")

def essay_page(e, index):
    prefix = "../"
    paras = "\n".join(f"<p>{p}</p>" for p in e["paras"])
    body = f'''<article>
<header class="essay-head"><div class="wrap">
<div class="prose">
<p class="series">The Calibration Series, {index} of {len(ESSAYS)}</p>
<h1>{html.escape(e["title"])}</h1>
<p class="meta">{e["date"]}. Originally posted to <a href="{e["link"]}" rel="noopener">r/cognitiveTesting</a>, where the discussion took place.</p>
</div>
</div></header>
<div class="essay-body"><div class="wrap"><div class="prose">
{paras}
</div></div></div>
<footer class="essay-foot"><div class="wrap"><div class="prose">
<p>Part of <a href="{prefix}visionary.html">The Visionary</a>. The instrument discussed here is the <a href="{prefix}scan.html">Visionary Psychometric Scan</a>, in beta calibration.</p>
</div></div></footer>
</article>'''
    return page(e["title"], body, "visionary", prefix, e["summary"])

# ---------- Build ----------

def build():
    for d in (DIST, ART):
        if os.path.isdir(d):
            shutil.rmtree(d)
        os.makedirs(os.path.join(d, "essays"))
    css = open(os.path.join(SRC, "style.css"), encoding="utf-8").read()

    pages = {
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

    # Artifact variant: same pages, except index is published without a document skeleton
    # (the Artifact tool wraps it) and with the stylesheet inlined.
    for name, content in pages.items():
        if name == "index.html":
            m = re.search(r"<body>\s*(.*?)\s*</body>", content, re.S)
            inner = m.group(1)
            art = ("<title>Visionary Systems</title>\n"
                   '<meta name="claude:viewport-fit-sides" content="cover">\n'
                   + FONTS + "\n<style>\n" + css + "\n</style>\n" + inner + "\n")
            content = art
        with open(os.path.join(ART, name), "w", encoding="utf-8") as f:
            f.write(content)
    shutil.copy(os.path.join(SRC, "style.css"), os.path.join(ART, "style.css"))
    print("built", len(pages), "pages")

if __name__ == "__main__":
    build()
