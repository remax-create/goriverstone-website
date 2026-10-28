"""Build the home listing cards and one page per home from data/listings.json.

- Writes homes/<slug>.html for every listing (full details, photos, links).
- Replaces the cards between <!-- LISTINGS:START --> and <!-- LISTINGS:END -->
  in index.html.
Run from the repository root: python3 scripts/make_listing_pages.py
To add, change or remove a home, edit data/listings.json and run it again.
"""
import html, json, os, re, urllib.parse

SITE = "https://goriverstone.com"
SANDRA_TEL = "+17703243680"
SANDRA_PHONE = "770-324-3680"
data = json.load(open("data/listings.json", encoding="utf-8"))["listings"]
e = lambda v: html.escape(str(v or ""), quote=True)


def specs(l, short=False):
    out = []
    if l.get("beds"): out.append(("Beds", l["beds"], "bd"))
    if l.get("baths"): out.append(("Baths", l["baths"], "ba"))
    if l.get("sqft"): out.append(("Sq ft", l["sqft"], "sq ft"))
    if l.get("acres"): out.append(("Acres", l["acres"], "ac"))
    if l.get("units"): out.append(("Homes", l["units"], ""))
    return out


def soon_visual(l, cls, big=e):
    return (f'<div class="{cls} soon-art" role="img" aria-label="{e(l["address"])}, renderings coming soon">'
            f'<svg viewBox="0 0 900 600" preserveAspectRatio="xMidYMid slice" aria-hidden="true"><use href="#contour"/></svg>'
            f'<span>Renderings coming soon</span><b>{e(l.get("type") or l["address"])}</b></div>')


# ---------- cards on the home page ----------
cards = []
for l in data:
    ph = l["photos"][0] if l["photos"] else None
    media = (f'<img src="{e(ph["src"])}" alt="{e(ph["alt"])}" loading="lazy" width="1600" height="1067">'
             if ph else soon_visual(l, "hc-soon"))
    sp = " · ".join(f'{e(v)} {u}'.strip() for _, v, u in specs(l))
    cards.append(f'''        <a class="home-card" href="homes/{e(l["slug"])}.html">
          <span class="hc-media">{media}<span class="chip {e(l["statusKind"])}">{e(l["status"])}</span></span>
          <span class="hc-body">
            <span class="hc-price">{e(l["price"])}</span>
            <span class="hc-addr">{e(l["address"])}</span>
            <span class="hc-city">{e(l["city"])}</span>
            {f'<span class="hc-specs">{sp}</span>' if sp else ''}
            <span class="hc-go">See details <svg><use href="#arrow"/></svg></span>
          </span>
        </a>''')
block = "<!-- LISTINGS:START -->\n      <div class=\"home-cards\">\n" + "\n".join(cards) + "\n      </div>\n      <!-- LISTINGS:END -->"
idx = open("index.html", encoding="utf-8").read()
idx2 = re.sub(r"<!-- LISTINGS:START -->.*?<!-- LISTINGS:END -->", lambda m: block, idx, count=1, flags=re.S)
if idx2 == idx and "<!-- LISTINGS:START -->" not in idx:
    raise SystemExit("index.html is missing the LISTINGS markers")
open("index.html", "w", encoding="utf-8").write(idx2)

# ---------- one page per home ----------
HEAD_CSS = open("scripts/listing-page.css", encoding="utf-8").read()
os.makedirs("homes", exist_ok=True)
keep = set()
for l in data:
    keep.add(l["slug"] + ".html")
    title = f'{l["address"]}, {l["city"]}'
    photos = l["photos"]
    if photos:
        thumbs = "".join(
            f'<button type="button" class="thumb{" on" if i == 0 else ""}" data-i="{i}" aria-label="Show photo {i+1}"><img src="../{e(p["src"])}" alt="" loading="lazy"></button>'
            for i, p in enumerate(photos))
        gallery = (f'<figure class="gal-main"><img id="gal-img" src="../{e(photos[0]["src"])}" alt="{e(photos[0]["alt"])}" width="1600" height="1067">'
                   f'<figcaption id="gal-cap">{e(photos[0]["alt"])}</figcaption></figure>'
                   + (f'<div class="thumbs">{thumbs}</div>' if len(photos) > 1 else ""))
    else:
        gallery = soon_visual(l, "gal-soon")
    spec_html = "".join(f'<div><dt>{k}</dt><dd>{e(v)}</dd></div>' for k, v, _ in specs(l))
    feats = "".join(f"<li>{e(f)}</li>" for f in l.get("features", []))
    topic = urllib.parse.quote(l.get("topic") or l["address"])
    btns = []
    if l.get("listingUrl"):
        btns.append(f'<a class="btn" href="{e(l["listingUrl"])}" target="_blank" rel="noopener">See the full listing <svg><use href="#arrow"/></svg></a>')
    if l.get("tourUrl"):
        btns.append(f'<a class="btn line" href="{e(l["tourUrl"])}" target="_blank" rel="noopener">3D walkthrough</a>')
    btns.append(f'<a class="btn line" href="../index.html?topic={topic}#contact">{e(l.get("cta") or "Schedule a showing")}</a>')
    maps = "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(f'{l["address"]}, {l["city"]}')
    og_img = f'{SITE}/{photos[0]["src"]}' if photos else f'{SITE}/images/hero-house.jpg'
    page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(title)} | {e(l["price"])} | Riverstone Homes</title>
<meta name="description" content="{e(l["summary"])} {e(l["price"])}. Call or text Sandra Watkins at {SANDRA_PHONE}.">
<link rel="canonical" href="{SITE}/homes/{e(l["slug"])}.html">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(title)} | {e(l["price"])}">
<meta property="og:description" content="{e(l["summary"])}">
<meta property="og:image" content="{e(og_img)}">
<meta property="og:url" content="{SITE}/homes/{e(l["slug"])}.html">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,opsz,wght@0,6..96,400;0,6..96,500;1,6..96,400&family=Hanken+Grotesk:wght@400;500;600&display=swap">
<style>
{HEAD_CSS}
</style>
</head>
<body>
<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>
  <symbol id="arrow" viewBox="0 0 16 16"><path d="M1 8h13M9 3l5 5-5 5" fill="none" stroke="currentColor" stroke-width="1.4"/></symbol>
  <symbol id="contour" viewBox="0 0 900 600"><g fill="none" stroke="currentColor" stroke-width="1.2"><path d="M40 420c90-60 160-70 250-40s170 40 260-20 190-90 320-50"/><path d="M20 470c110-70 190-80 290-45s180 45 280-15 200-95 330-55"/><path d="M60 370c80-50 140-60 220-35s150 35 240-15 180-85 300-50"/><path d="M100 320c70-40 120-50 190-30s130 30 210-10 170-80 280-50"/><path d="M150 270c60-35 100-42 160-26s110 26 180-8 150-70 250-46"/></g></symbol>
</defs></svg>
<header class="site-header"><div class="wrap">
  <a class="brand" href="../index.html" aria-label="Riverstone Homes home"><img src="../images/logo.png" alt="Riverstone Homes" width="799" height="238"></a>
  <nav class="head-links" aria-label="Main">
    <a href="../index.html#homes">All homes</a>
    <a class="cta" href="tel:{SANDRA_TEL}">Call Sandra {SANDRA_PHONE}</a>
  </nav>
</div></header>

<main>
  <div class="wrap">
    <a class="back" href="../index.html#homes">&larr; All homes for sale</a>
    <div class="top">
      <div class="gallery">{gallery}</div>
      <aside class="facts">
        <span class="chip {e(l["statusKind"])}">{e(l["status"])}</span>
        <h1>{e(l["address"])}</h1>
        <p class="where">{" · ".join(e(x) for x in [l["city"], l.get("type"), l.get("mls")] if x)}</p>
        <p class="price">{e(l["price"])}</p>
        <dl class="specs">{spec_html}</dl>
        {f'<p class="offer">{l["offer"]}</p>' if l.get("offer") else ""}
        <div class="btns">{"".join(btns)}</div>
        <div class="agent">
          <b>Sandra Watkins</b><span>RE/MAX Town &amp; Country · New Home Sales, Riverstone Homes</span>
          <a href="tel:{SANDRA_TEL}">Call or text {SANDRA_PHONE}</a>
        </div>
      </aside>
    </div>
    <div class="details">
      <section><h2>{"About these homes" if l.get("units") else "About this home"}</h2><p>{e(l["description"])}</p></section>
      {f'<section><h2>Highlights</h2><ul class="feats">{feats}</ul></section>' if feats else ""}
      {"" if not l.get("mls") else f'<section><h2>Location</h2><p>{e(l["address"])}, {e(l["city"])}</p><p><a class="text-link" href="{e(maps)}" target="_blank" rel="noopener">Open in Google Maps</a></p></section>'}
    </div>
  </div>
</main>

<section class="cta-band"><div class="wrap">
  <div><h2>Want to see it in person?</h2><p>Call or text Sandra Watkins at {SANDRA_PHONE}. She'll set up a private showing.</p></div>
  <a class="btn" href="tel:{SANDRA_TEL}">Call Sandra</a>
</div></section>
<footer class="site-footer"><div class="wrap"><span>© <span id="year">2026</span> Riverstone Homes, Inc. · North Metro Atlanta, Georgia</span><a href="../index.html">goriverstone.com</a></div></footer>
<script>
  document.getElementById("year").textContent = new Date().getFullYear();
  const P = {json.dumps([{"src": "../" + p["src"], "alt": p["alt"]} for p in photos])};
  document.querySelectorAll(".thumb").forEach(b => b.addEventListener("click", () => {{
    const p = P[+b.dataset.i]; const img = document.getElementById("gal-img");
    img.src = p.src; img.alt = p.alt; document.getElementById("gal-cap").textContent = p.alt;
    document.querySelectorAll(".thumb").forEach(t => t.classList.toggle("on", t === b));
  }}));
</script>
</body>
</html>
'''
    open(f"homes/{l['slug']}.html", "w", encoding="utf-8").write(page)
for f in os.listdir("homes"):
    if f.endswith(".html") and f not in keep:
        os.remove(os.path.join("homes", f))
print("homes:", sorted(keep))
