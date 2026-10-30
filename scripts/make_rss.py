"""Build rss.xml (the blog's RSS feed) from every published post in posts.json.

Run from the site root after adding or editing a post:  python3 scripts/make_rss.py
"""
import json, os
from datetime import datetime, timezone
from email.utils import format_datetime
from xml.sax.saxutils import escape as e

SITE = "https://goriverstone.com"
posts = json.load(open("posts.json", encoding="utf-8"))["posts"]
posts = [p for p in posts if p.get("status", "published") == "published"]
posts.sort(key=lambda p: p["date"], reverse=True)

def rfc822(d):
    # Posts carry a date only; publish them at 9:00 AM Eastern (13:00 UTC).
    return format_datetime(datetime.strptime(d, "%Y-%m-%d").replace(hour=13, tzinfo=timezone.utc))

items = []
for p in posts:
    link = f"{SITE}/blog.html#{p['slug']}"
    img = f"{SITE}/{p['photo'].lstrip('/')}" if p.get("photo") else ""
    size = os.path.getsize(p["photo"].lstrip("/")) if img and os.path.exists(p["photo"].lstrip("/")) else 0
    items.append(f"""  <item>
    <title>{e(p['title'])}</title>
    <link>{link}</link>
    <guid isPermaLink="false">goriverstone-{e(p['slug'])}</guid>
    <pubDate>{rfc822(p['date'])}</pubDate>
    <dc:creator>{e(p.get('author', 'Riverstone Homes'))}</dc:creator>
    <category>{e(p.get('category', 'Blog'))}</category>
    <description>{e(p.get('excerpt', ''))}</description>
    <content:encoded><![CDATA[{p.get('body', '').replace(']]>', ']]]]><![CDATA[>')}]]></content:encoded>
""" + (f"""    <enclosure url="{img}" length="{size}" type="image/jpeg"/>
    <media:content url="{img}" medium="image"/>
""" if img else "") + "  </item>")

last = rfc822(posts[0]["date"]) if posts else format_datetime(datetime.now(timezone.utc))
rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:media="http://search.yahoo.com/mrss/">
<channel>
  <title>Riverstone Homes Blog</title>
  <link>{SITE}/blog.html</link>
  <atom:link href="{SITE}/rss.xml" rel="self" type="application/rss+xml"/>
  <description>New construction, building on your land and North Georgia local news from Riverstone Homes.</description>
  <language>en-us</language>
  <lastBuildDate>{last}</lastBuildDate>
  <image><url>{SITE}/images/logo.png</url><title>Riverstone Homes Blog</title><link>{SITE}/blog.html</link></image>
{chr(10).join(items)}
</channel>
</rss>
"""
open("rss.xml", "w", encoding="utf-8").write(rss)
print(f"rss.xml written with {len(items)} post(s)")
