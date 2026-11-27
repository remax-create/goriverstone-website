"""Build share/<slug>.html for every published post in posts.json.

Each page is the full article (crawlable by Google, BlogPosting schema) with
Facebook/LinkedIn preview tags. Styles are copied from blog.html so the article
looks the same as on the blog. Also adds the article URLs to sitemap.xml.
Run from the repository root: python3 scripts/make_share_pages.py
"""
import html, json, os, re, urllib.parse
from datetime import date

SITE = "https://goriverstone.com"
posts = json.load(open("posts.json", encoding="utf-8"))["posts"]
blog = open("blog.html", encoding="utf-8").read()
STYLE = re.search(r"<style>.*?</style>", blog, re.S).group(0)
IC = dict(re.findall(r"^\s+(fb|li|x|pin|mail): '(.*?)',?$", blog, re.M))
os.makedirs("share", exist_ok=True)
keep = set()
e = lambda v: html.escape(str(v or ""), quote=True)


def dims(photo):
    try:
        from PIL import Image
        w, h = Image.open(photo).size
        return w, h
    except Exception:
        return None


def fix_links(body):
    def rep(m):
        attr, url = m.group(1), m.group(2)
        if re.match(r"^(https?:|mailto:|tel:|#|/)", url):
            return m.group(0)
        b = re.match(r"^blog\.html#(.+)$", url)
        if b:
            return f'{attr}="/share/{b.group(1)}.html"'
        return f'{attr}="/{url}"'
    return re.sub(r'(href|src)="([^"]+)"', rep, body)


def share_bar(p, cls=""):
    url = f"{SITE}/share/{p['slug']}.html"
    u, t, img = (urllib.parse.quote(x, safe="") for x in (url, p["title"], f"{SITE}/{p.get('photo','')}"))
    mail = "mailto:?subject=" + t + "&body=" + urllib.parse.quote(p["title"] + "\n\n" + url, safe="")
    return (f'<div class="share {cls}"><span>Share this post</span>'
            f'<a href="https://www.facebook.com/sharer/sharer.php?u={u}" target="_blank" rel="noopener" aria-label="Share on Facebook">{IC.get("fb","")}</a>'
            f'<a href="https://www.linkedin.com/sharing/share-offsite/?url={u}" target="_blank" rel="noopener" aria-label="Share on LinkedIn">{IC.get("li","")}</a>'
            f'<a href="https://x.com/intent/post?url={u}&amp;text={t}" target="_blank" rel="noopener" aria-label="Share on X">{IC.get("x","")}</a>'
            f'<a href="https://pinterest.com/pin/create/button/?url={u}&amp;media={img}&amp;description={t}" target="_blank" rel="noopener" aria-label="Save to Pinterest">{IC.get("pin","")}</a>'
            f'<a href="{e(mail)}" aria-label="Share by email">{IC.get("mail","")}</a>'
            '<span class="acts"><a class="act go" href="/start.html?topic=A%20building%20consultation">Start your build</a><a class="act" href="tel:+17703243680">Call us</a></span></div>')


def fmt(iso):
    d = date.fromisoformat(iso)
    return d.strftime("%B ") + str(d.day) + d.strftime(", %Y")


initials = lambda n: "".join(w[0] for w in str(n or "").split())[:2].upper()
published = sorted([p for p in posts if p.get("status") == "published"], key=lambda p: p["date"], reverse=True)

for p in published:
    slug = p["slug"]; keep.add(slug + ".html")
    url = f"{SITE}/share/{slug}.html"
    img = f"{SITE}/{p.get('photo')}"
    d = dims(p.get("photo"))
    ld = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": p["title"][:110],
          "description": p.get("excerpt", ""), "image": [img], "datePublished": p["date"], "dateModified": p["date"],
          "author": {"@type": "Person", "name": p.get("author", "Riverstone Homes"), "jobTitle": p.get("authorRole", "")},
          "publisher": {"@type": "Organization", "name": "Riverstone Homes", "url": SITE,
                        "logo": {"@type": "ImageObject", "url": f"{SITE}/images/logo.png"}},
          "mainEntityOfPage": {"@type": "WebPage", "@id": url}, "url": url,
          "articleSection": p.get("category", ""), "keywords": p.get("focusPhrase", "")}
    others = [o for o in published if o["slug"] != slug][:3]
    more = "".join(f'<li><a href="/share/{e(o["slug"])}.html">{e(o["title"])}</a></li>' for o in others)
    sources = ""
    if p.get("sources"):
        sources = '<div class="sources"><h3>Sources</h3><ul>' + "".join(
            f'<li><a href="{e(s["url"])}" target="_blank" rel="noopener">{e(s["title"])}</a></li>' for s in p["sources"]) + "</ul></div>"
    page = f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(p.get('seoTitle') or p['title'])} | Riverstone Homes</title>
<meta name="description" content="{e(p.get('excerpt'))}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Riverstone Homes">
<meta property="og:title" content="{e(p['title'])}">
<meta property="og:description" content="{e(p.get('excerpt'))}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{img}">
<meta property="og:image:secure_url" content="{img}">
<meta property="og:image:type" content="image/jpeg">
{f'<meta property="og:image:width" content="{d[0]}"><meta property="og:image:height" content="{d[1]}">' if d else ''}
<meta property="og:image:alt" content="{e(p.get('photoAlt'))}">
<meta property="article:published_time" content="{e(p['date'])}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(p['title'])}">
<meta name="twitter:description" content="{e(p.get('excerpt'))}">
<meta name="twitter:image" content="{img}">
<link rel="icon" href="/images/logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,opsz,wght@0,6..96,400;0,6..96,500;1,6..96,400&family=Hanken+Grotesk:wght@400;500;600&display=swap">
<link rel="alternate" type="application/rss+xml" title="Riverstone Homes Blog" href="{SITE}/rss.xml">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
{STYLE}
<style>.more-posts{{margin:2.5rem 0 1rem}}.more-posts h3{{font-family:var(--f-display,Georgia,serif);font-weight:400;font-size:1.4rem;margin:0 0 .6rem}}.more-posts ul{{margin:0;padding-left:1.1rem;display:grid;gap:.4rem}}</style>
</head>
<body>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="/index.html" aria-label="Riverstone Homes home"><img src="/images/logo.png" alt="Riverstone Homes" width="799" height="238"></a>
    <nav class="head-links" aria-label="Blog">
      <a class="home" href="/index.html">Home</a>
      <a href="/blog.html">Blog</a>
      <a href="/videos.html">Videos</a>
      <a class="cta" href="/start.html?topic=A%20building%20consultation">Start Your Build</a>
    </nav>
  </div>
</header>
<main>
  <article>
    <header class="article-head"><div class="wrap narrow">
      <a class="back" href="/blog.html">&larr; All posts</a>
      <div class="meta"><span class="cat">{e(p.get('category'))}</span><span><time datetime="{e(p['date'])}">{fmt(p['date'])}</time></span><span>{e(p.get('readMins'))} min read</span></div>
      <h1>{e(p['title'])}</h1>
      <p class="dek">{e(p.get('excerpt'))}</p>
      <div class="byline"><div class="mono" aria-hidden="true">{e(initials(p.get('author')))}</div><div><b>{e(p.get('author'))}</b><span>{e(p.get('authorRole'))}</span></div></div>
      {share_bar(p)}
    </div></header>
    <div class="wrap narrow">
      <figure class="hero-ph"><img src="/{e(p.get('photo'))}" alt="{e(p.get('photoAlt'))}" width="1600" height="1067">{f'<figcaption>{e(p.get("photoCaption"))}</figcaption>' if p.get('photoCaption') else ''}</figure>
      <div class="prose">{fix_links(p['body'])}</div>
      {share_bar(p, 'share-end')}
      {sources}
      {f'<nav class="more-posts" aria-label="More posts"><h3>More from the blog</h3><ul>{more}</ul></nav>' if more else ''}
    </div>
  </article>
</main>
<section class="cta-band">
  <div class="wrap">
    <div><h2>Thinking about building? Let's talk it through.</h2><p>Free building consultation, on your land or ours. Or call Sandra at 770-324-3680.</p></div>
    <div class="band-acts"><a class="btn" href="/start.html?topic=A%20building%20consultation">Start your build</a><a class="btn line" href="tel:+17703243680">Call us 770-324-3680</a></div>
  </div>
</section>
<footer class="site-footer">
  <div class="wrap"><span>© {date.today().year} Riverstone Homes, Inc. · North Metro Atlanta, Georgia</span><a href="/index.html">goriverstone.com</a></div>
</footer>
<script src="/js/site.js" defer></script>
</body></html>
"""
    open(f"share/{slug}.html", "w", encoding="utf-8").write(page)
for f in os.listdir("share"):
    if f.endswith(".html") and f not in keep:
        os.remove(os.path.join("share", f))

# sitemap: keep one <url> per published article
sm = open("sitemap.xml", encoding="utf-8").read()
sm = re.sub(r"\s*<url><loc>https://goriverstone\.com/share/[^<]+</loc>(?:<lastmod>[^<]*</lastmod>)?</url>", "", sm)
entries = "".join(f"\n  <url><loc>{SITE}/share/{p['slug']}.html</loc><lastmod>{p['date']}</lastmod></url>" for p in published)
sm = sm.replace("</urlset>", entries + "\n</urlset>")
open("sitemap.xml", "w", encoding="utf-8").write(sm)
print("share pages:", sorted(keep))
