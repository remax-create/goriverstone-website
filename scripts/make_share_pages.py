"""Build share/<slug>.html for every published post in posts.json.

Each page carries the post's title, description and photo for Facebook,
LinkedIn and other link previews, then sends visitors on to blog.html#<slug>.
Run from the repository root: python3 scripts/make_share_pages.py
"""
import html, json, os

SITE = "https://goriverstone.com"
posts = json.load(open("posts.json", encoding="utf-8"))["posts"]
os.makedirs("share", exist_ok=True)
keep = set()
for p in posts:
    if p.get("status") != "published":
        continue
    slug = p["slug"]; keep.add(slug + ".html")
    e = lambda v: html.escape(str(v or ""), quote=True)
    target = f"{SITE}/blog.html#{slug}"
    page = f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(p.get('seoTitle') or p['title'])} | Riverstone Homes</title>
<meta name="description" content="{e(p.get('excerpt'))}">
<link rel="canonical" href="{e(target)}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Riverstone Homes">
<meta property="og:title" content="{e(p['title'])}">
<meta property="og:description" content="{e(p.get('excerpt'))}">
<meta property="og:url" content="{SITE}/share/{e(slug)}.html">
<meta property="og:image" content="{SITE}/{e(p.get('photo'))}">
<meta property="og:image:alt" content="{e(p.get('photoAlt'))}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(p['title'])}">
<meta name="twitter:description" content="{e(p.get('excerpt'))}">
<meta name="twitter:image" content="{SITE}/{e(p.get('photo'))}">
<meta http-equiv="refresh" content="0; url={e(target)}">
<script>location.replace({json.dumps(target)});</script>
<style>body{{font:16px system-ui,sans-serif;background:#f4f3ef;color:#18211e;display:grid;place-items:center;min-height:100vh;margin:0;padding:20px;text-align:center}}a{{color:#9c7a45}}</style>
</head><body><p>Opening <a href="{e(target)}">{e(p['title'])}</a> on the Riverstone Homes blog…</p></body></html>
"""
    open(f"share/{slug}.html", "w", encoding="utf-8").write(page)
for f in os.listdir("share"):
    if f.endswith(".html") and f not in keep:
        os.remove(os.path.join("share", f))
print("share pages:", sorted(keep))
