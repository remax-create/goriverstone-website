"""Move blog drafts Sandra approved on /review.html into posts.json.

Run by .github/workflows/publish-approved.yml every few minutes (and safe to run
by hand from the site root). Reads approvals from https://goriverstone.com/api/blog?view=decisions,
moves each approved draft from drafts/pending.json into posts.json, saves a copy
of the decisions to drafts/decisions.json (the drafting task reads change notes
there), and rebuilds the share pages and rss.xml. Prints PUBLISHED: <title> lines.
"""
import json, subprocess, sys, urllib.request

import os
URL = os.environ.get("DECISIONS_URL", "https://goriverstone.com/api/blog?view=decisions")

def load(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default

def dump(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
        f.write("\n")

req = urllib.request.Request(URL, headers={"user-agent": "riverstone-publisher"})
decisions = json.load(urllib.request.urlopen(req, timeout=30)).get("decisions", {})

pending = load("drafts/pending.json", {"posts": []})
site = load("posts.json", {"posts": []})
have = {p["slug"] for p in site["posts"]}

keep, published = [], []
for d in pending["posts"]:
    dec = decisions.get(d["slug"]) or {}
    rev = d.get("rev") or d.get("date") or "1"
    if dec.get("decision") == "approved" and str(dec.get("rev")) == str(rev):
        if d["slug"] not in have:
            post = {k: v for k, v in d.items() if k != "rev"}
            post["status"] = "published"
            post["date"] = dec.get("date") or post["date"]
            site["posts"].insert(0, post)
            published.append(post["title"])
    else:
        keep.append(d)

old_dec = load("drafts/decisions.json", {})
if decisions != old_dec:
    dump("drafts/decisions.json", decisions)

if published:
    pending["posts"] = keep
    dump("drafts/pending.json", pending)
    dump("posts.json", site)
    subprocess.run([sys.executable, "scripts/make_share_pages.py"], check=True)
    subprocess.run([sys.executable, "scripts/make_rss.py"], check=True)
for t in published:
    print("PUBLISHED:", t)
