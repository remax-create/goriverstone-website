#!/usr/bin/env python3
"""Build Riverstone landing pages from data/landing_pages.json.

Each page is a list of blocks (hero, steps, checks, two, cards, specs, gallery,
plans, faq, contact). Shared styles live in scripts/landing-page.css and are
inlined into every page. Paths are root-relative ("/images/...") so pages can
live in sub-folders such as /plans/.

Run from the repo root:  python3 scripts/make_landing_pages.py
"""
import json, os, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS = open(os.path.join(ROOT, 'scripts', 'landing-page.css')).read()
DATA = json.load(open(os.path.join(ROOT, 'data', 'landing_pages.json')))
SITE = 'https://goriverstone.com'
E = lambda s: html.escape(s or '', quote=True)

TOPICS = ["Building on my land", "Finding land to build on", "The Hemlock Falls plan", "121 Cypress Court",
          "104 Bob White Drive", "Riverstone Commons townhomes", "A custom home or plan", "A barndominium",
          "A room addition", "A basement finish", "A garage or pole barn", "A building consultation", "Something else"]

ARROW = '<svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M2 8h11M9 4l4 4-4 4"/></svg>'
DL = '<svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M8 2v9M4 7.5 8 11.5l4-4M2.5 14h11"/></svg>'


def btn(b, cls='btn'):
    icon = DL if b.get('download') else ARROW
    ext = ' target="_blank" rel="noopener"' if b.get('download') or b['href'].startswith('http') else ''
    return f'<a class="{cls}{" " + b["style"] if b.get("style") else ""}" href="{E(b["href"])}"{ext}>{icon if b.get("download") else ""}{E(b["text"])}{"" if b.get("download") else " " + icon}</a>'


def head_block(title, label, text):
    out = '<div class="sec-head">'
    if label: out += f'<span class="label">{E(label)}</span>'
    if title: out += f'<h2>{E(title)}</h2>'
    if text: out += f'<p>{E(text)}</p>'
    return out + '</div>'


def block(b, page):
    t = b['type']
    if t == 'hero':
        acts = ''.join(btn(x, 'btn') if i == 0 else btn(dict(x, style='line')) for i, x in enumerate(b.get('buttons', [])))
        return (f'<section class="hero"><div class="ph"><img src="{E(b["image"])}" alt="{E(b.get("alt",""))}" fetchpriority="high"></div>'
                f'<div class="wrap"><span class="label">{E(b["label"])}</span><h1>{E(b["title"])}</h1>'
                f'<p class="lede">{E(b["lede"])}</p><div class="acts">{acts}</div></div></section>')
    cls = 'sec alt' if b.get('alt') else 'sec'
    sid = f' id="{E(b["id"])}"' if b.get('id') else ''
    head = head_block(b.get('title'), b.get('label'), b.get('text'))
    if t == 'steps':
        items = ''.join(f'<li><h3>{E(s[0])}</h3><p>{E(s[1])}</p></li>' for s in b['items'])
        return f'<section class="{cls}"{sid}><div class="wrap">{head}<ol class="steps">{items}</ol></div></section>'
    if t == 'checks':
        items = ''.join(f'<li><b>{E(s[0])}</b>' + (f'<span>{E(s[1])}</span>' if len(s) > 1 and s[1] else '') + '</li>' for s in b['items'])
        foot = f'<p style="margin-top:2rem">{btn(b["button"], "btn dark")}</p>' if b.get('button') else ''
        return f'<section class="{cls}"{sid}><div class="wrap">{head}<ul class="checks">{items}</ul>{foot}</div></section>'
    if t == 'two':
        paras = ''.join(f'<p>{p}</p>' for p in b['paras'])  # paras may hold simple inline links
        acts = ''.join(btn(x, 'btn dark') if i == 0 else btn(x, 'btn line') for i, x in enumerate(b.get('buttons', [])))
        img = f'<img src="{E(b["image"])}" alt="{E(b.get("alt",""))}" loading="lazy">' if b.get('image') else ''
        txt = (f'<div class="prose">' + (f'<span class="label">{E(b["label"])}</span>' if b.get('label') else '') +
               f'<h2 style="font-size:clamp(1.9rem,3.6vw,2.7rem)">{E(b["title"])}</h2>{paras}' +
               (f'<div class="acts" style="display:flex;flex-wrap:wrap;gap:.8rem;padding-top:.4rem">{acts}</div>' if acts else '') + '</div>')
        inner = img + txt if b.get('image_first') else txt + img
        return f'<section class="{cls}"{sid}><div class="wrap two{"" if img else " solo"}">{inner}</div></section>'
    if t == 'cards':
        cards = ''.join(
            f'<a class="card" href="{E(c["href"])}"' + (' target="_blank" rel="noopener"' if c["href"].endswith('.pdf') else '') +
            f'><span class="k">{E(c["kicker"])}</span><h3>{E(c["title"])}</h3><p>{E(c["text"])}</p><span class="go">{E(c.get("go","Learn more"))} &rarr;</span></a>'
            for c in b['items'])
        return f'<section class="{cls}"{sid}><div class="wrap">{head}<div class="cards">{cards}</div></div></section>'
    if t == 'specs':
        sp = ''.join(f'<div><b>{E(v)}</b><span>{E(l)}</span></div>' for v, l in b['items'])
        note = f'<p class="fine" style="margin-top:.8rem">{E(b["note"])}</p>' if b.get('note') else ''
        return f'<section class="sec" style="padding-block:clamp(2rem,4vw,3rem)"{sid}><div class="wrap"><div class="specs">{sp}</div>{note}</div></section>'
    if t == 'gallery':
        items = ''.join(
            f'<button type="button" class="{"first" if i == 0 and len(b["items"]) >= 3 else ""}" data-full="{E(g["src"])}" data-cap="{E(g.get("caption",""))}" aria-label="View larger: {E(g.get("alt",""))}">'
            f'<img src="{E(g["src"])}" alt="{E(g.get("alt",""))}" loading="lazy">' + (f'<span class="cap">{E(g["caption"])}</span>' if g.get('caption') else '') + '</button>'
            for i, g in enumerate(b['items']))
        note = f'<p class="fine" style="margin-top:1rem">{E(b["note"])}</p>' if b.get('note') else ''
        return f'<section class="{cls}"{sid}><div class="wrap">{head}<div class="gallery">{items}</div>{note}</div></section>'
    if t == 'plans':
        f1 = b['floors'][0]
        fig = lambda f: (f'<figure><button type="button" class="zoom" data-full="{E(f["img"])}" data-cap="{E(f["label"])}" aria-label="View larger: {E(f["alt"])}"><img src="{E(f["img"])}" alt="{E(f["alt"])}" loading="lazy" style="aspect-ratio:auto;object-fit:contain"></button><figcaption><b>{E(f["label"])}</b><span>{E(f["note"])}</span></figcaption></figure>')
        key = ''.join(f'<span><i style="background:{c}{";border-style:dashed;border-color:#9c7a45" if n.startswith("Optional") else ""}"></i>{E(n)}</span>' for n, c in b['key'])
        hl = ''.join(f'<li><b>{E(h)}</b></li>' for h in b.get('highlights', []))
        side = ''.join(fig(f) for f in b['floors'][1:])
        side += f'<div><span class="label">Color key</span><div class="key" style="margin-top:.8rem">{key}</div></div>'
        if hl: side += f'<div><span class="label">Highlights</span><ul class="checks" style="grid-template-columns:1fr;margin-top:1rem">{hl}</ul></div>'
        if b.get('button'): side += f'<div>{btn(b["button"], "btn dark")}</div>'
        credit = f'<p class="fine" style="margin-top:1.5rem">{E(b["credit"])}</p>' if b.get('credit') else ''
        return f'<section class="{cls}"{sid}><div class="wrap">{head}<div class="plans">{fig(f1)}<div class="side">{side}</div></div>{credit}</div></section>'
    if t == 'faq':
        qs = ''.join(f'<details><summary>{E(q)}</summary><div class="a">{a}</div></details>' for q, a in b['items'])
        return f'<section class="{cls}"{sid}><div class="wrap">{head}<div class="faq">{qs}</div></div></section>'
    if t == 'contact':
        opts = ''.join(f'<option{" selected" if o == b["topic"] else ""}>{E(o)}</option>' for o in TOPICS)
        return f'''<section class="contact" id="contact"><div class="wrap">
  <div class="copy"><span class="label">{E(b.get("label","Free build consultation"))}</span><h2>{E(b["title"])}</h2><p>{E(b["text"])}</p>
    <dl class="reach"><div><dt>Call Riverstone</dt><dd><a href="tel:+17065146637">706-514-6637</a></dd></div><div><dt>Email</dt><dd>info@goriverstone.com</dd></div><div><dt>New home sales, Sandra Watkins</dt><dd><a href="tel:+17703243680">770-324-3680</a></dd></div></dl></div>
  <form class="inquiry" id="inquiry" name="contact" method="POST" data-netlify="true" netlify-honeypot="company-website">
    <input type="hidden" name="form-name" value="contact">
    <p class="hp"><label for="company-website">Leave this empty</label><input id="company-website" name="company-website" tabindex="-1" autocomplete="off"></p>
    <div class="field"><label for="f-name">Name</label><input id="f-name" name="name" autocomplete="name" required></div>
    <div class="field"><label for="f-phone">Phone</label><input id="f-phone" name="phone" type="tel" autocomplete="tel"></div>
    <div class="field full"><label for="f-email">Email</label><input id="f-email" name="email" type="email" autocomplete="email" required></div>
    <div class="field full"><label for="f-topic">I'm interested in</label><select id="f-topic" name="topic">{opts}</select></div>
    <div class="field full"><label for="f-msg">Message</label><textarea id="f-msg" name="message" placeholder="{E(b.get("placeholder",""))}"></textarea></div>
    <div class="field full"><button class="btn" type="submit">Send message {ARROW}</button></div>
    <p class="form-status" id="form-status" role="status"></p>
  </form></div></section>'''
    raise ValueError(t)


SCRIPT = '''<script>
(function () {
  var form = document.getElementById('inquiry'), status = document.getElementById('form-status');
  if (form) form.addEventListener('submit', async function (e) {
    e.preventDefault(); status.textContent = 'Sending\\u2026';
    try {
      var res = await fetch('/', { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: new URLSearchParams(new FormData(form)).toString() });
      if (!res.ok) throw new Error(res.status);
      form.reset(); status.textContent = 'Thank you. We received your message and will be in touch soon.';
    } catch (err) { status.textContent = 'Something went wrong sending your message. Please call 706-514-6637 or email info@goriverstone.com.'; }
  });
  var lb = document.getElementById('lb');
  if (lb) {
    document.addEventListener('click', function (e) {
      var b = e.target.closest('.gallery button, button.zoom');
      if (b) { lb.querySelector('img').src = b.dataset.full; lb.querySelector('img').alt = b.getAttribute('aria-label').replace('View larger: ', ''); lb.querySelector('p').textContent = b.dataset.cap || ''; lb.showModal(); return; }
      if (e.target === lb || e.target.closest('.x')) lb.close();
    });
  }
})();
</script>'''


def page_html(p):
    url = SITE + p['path']
    blocks = ''.join(block(b, p) for b in p['blocks'])
    lb = '<dialog class="lb" id="lb" aria-label="Photo"><button class="x" type="button" aria-label="Close">&times;</button><img src="" alt=""><p></p></dialog>' if any(b['type'] in ('gallery', 'plans') for b in p['blocks']) else ''
    schema = json.dumps(p['schema']) if p.get('schema') else None
    nav = ''.join(f'<a href="{h}">{E(t)}</a>' for t, h in DATA['footer_nav'])
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{E(p["title"])}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="description" content="{E(p["description"])}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:title" content="{E(p["title"])}">
<meta property="og:description" content="{E(p["description"])}">
<meta property="og:image" content="{SITE}{E(p["og_image"])}">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/images/logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,opsz,wght@0,6..96,400;0,6..96,500;1,6..96,400&family=Hanken+Grotesk:wght@400;500;600&display=swap">
<style>
{CSS}</style>
{f'<script type="application/ld+json">{schema}</script>' if schema else ''}
<!-- Metricool -->
<script>function loadScript(a){{var b=document.getElementsByTagName("head")[0],c=document.createElement("script");c.type="text/javascript",c.src="https://tracker.metricool.com/resources/be.js",c.onreadystatechange=a,c.onload=a,b.appendChild(c)}}loadScript(function(){{beTracker.t({{hash:"c912cd182a3a69c45b610171e4c84dee"}})}});</script>
</head>
<body>
<header class="site-header"><div class="wrap">
  <a class="brand" href="/" aria-label="Riverstone Homes home"><img src="/images/logo.png" alt="Riverstone Homes" width="799" height="238"></a>
  <nav class="head-links" aria-label="Main"><a href="/">Home</a><a href="/build-on-your-land.html">Build on your land</a><a href="/downloads.html">Downloads</a><a class="cta" href="#contact">Start Your Build</a></nav>
</div></header>
<main>
{blocks}
</main>
<footer class="site-footer"><div class="wrap"><span>&copy; <span id="year">2026</span> Riverstone Homes, Inc. &middot; 6446 Joe Frank Harris Pkwy, Adairsville, GA 30103 &middot; 706-514-6637</span><nav aria-label="Footer">{nav}</nav></div></footer>
{lb}
{SCRIPT}
<script>document.getElementById("year").textContent = new Date().getFullYear();</script>
</body>
</html>
'''


for p in DATA['pages']:
    out = os.path.join(ROOT, p['path'].lstrip('/'))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w').write(page_html(p))
    print('wrote', p['path'])
