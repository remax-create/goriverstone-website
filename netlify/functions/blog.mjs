// Riverstone blog approvals.
// Drafts live in drafts/pending.json in the repo (bundled into this function at
// build time). Sandra approves them on /review.html; decisions are kept in
// Netlify Blobs, and approved posts show on the public blog right away.
// A GitHub Action (.github/workflows/publish-approved.yml) then writes them into
// posts.json, rebuilds share pages and rss.xml, and removes the draft.
import { pbkdf2Sync, timingSafeEqual } from "node:crypto";
import { getStore } from "@netlify/blobs";
import bundled from "../../drafts/pending.json" with { type: "json" };

const SALT = "859ea06217914363e4cbb84ad47087fb";
const HASH = "7585eba9184ce3fb0ab3678e0afc7b50719bc1c16a7ecd13d7d9d68911dba592";
const SITE = "https://goriverstone.com";

const json = (data, status = 200, extra = {}) =>
  new Response(JSON.stringify(data), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store", ...extra },
  });

export function keyOk(key) {
  if (!key || typeof key !== "string" || key.length > 200) return false;
  const env = globalThis.process?.env?.REVIEW_KEY;
  if (env) {
    const a = Buffer.from(key), b = Buffer.from(env);
    if (a.length === b.length && timingSafeEqual(a, b)) return true;
  }
  const h = pbkdf2Sync(key.trim().toLowerCase(), SALT, 600000, 32, "sha256");
  return timingSafeEqual(h, Buffer.from(HASH, "hex"));
}

const todayET = () =>
  new Intl.DateTimeFormat("en-CA", { timeZone: "America/New_York", year: "numeric", month: "2-digit", day: "2-digit" }).format(new Date());

const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

export function draftsFrom(src) {
  const out = {};
  for (const p of (src && src.posts) || []) if (p && p.slug) out[p.slug] = { ...p, rev: p.rev || p.date || "1" };
  return out;
}

async function load(store, drafts) {
  const s = await store.get("decisions", { type: "json" });
  return { drafts, decisions: (s && typeof s === "object") ? s : {} };
}

export function approvedPosts(state) {
  return Object.values(state.drafts)
    .filter(p => state.decisions[p.slug]?.decision === "approved" && state.decisions[p.slug]?.rev === p.rev)
    .map(p => ({ ...p, status: "published", date: state.decisions[p.slug].date || p.date }));
}

function sharePage(p) {
  const url = `${SITE}/share/${p.slug}.html`, target = `${SITE}/blog.html#${p.slug}`, img = `${SITE}/${p.photo}`;
  return `<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${esc(p.seoTitle || p.title)} | Riverstone Homes</title>
<meta name="description" content="${esc(p.excerpt)}">
<link rel="canonical" href="${url}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Riverstone Homes">
<meta property="og:title" content="${esc(p.title)}">
<meta property="og:description" content="${esc(p.excerpt)}">
<meta property="og:url" content="${url}">
<meta property="og:image" content="${img}">
<meta property="og:image:secure_url" content="${img}">
<meta property="og:image:type" content="image/jpeg">
<meta property="og:image:alt" content="${esc(p.photoAlt)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="${esc(p.title)}">
<meta name="twitter:description" content="${esc(p.excerpt)}">
<meta name="twitter:image" content="${img}">
<script>location.replace(${JSON.stringify(target)});</script>
<style>body{font:16px system-ui,sans-serif;background:#f4f3ef;color:#18211e;display:grid;place-items:center;min-height:100vh;margin:0;padding:20px;text-align:center}a{color:#9c7a45}</style>
</head><body><p>Opening <a href="${target}">${esc(p.title)}</a> on the Riverstone Homes blog…</p></body></html>`;
}

const SLUG = /^[a-z0-9][a-z0-9-]{0,120}$/;

export async function handle(req, store, drafts = draftsFrom(bundled)) {
  const url = new URL(req.url);

  if (req.method === "GET") {
    const share = url.searchParams.get("share") || (url.pathname.startsWith("/share/") ? url.pathname.slice(7) : "");
    if (share) {
      const slug = share.replace(/\.html$/, "").replace(/^.*\//, "");
      const p = approvedPosts(await load(store, drafts)).find(x => x.slug === slug);
      if (!p) return new Response("Not found", { status: 404, headers: { "content-type": "text/plain" } });
      return new Response(sharePage(p), { headers: { "content-type": "text/html; charset=utf-8", "cache-control": "public, max-age=60" } });
    }
    if (url.searchParams.get("view") === "decisions") {
      // Public: approvals and change notes, read by the GitHub Action and the drafting task.
      return json({ decisions: (await load(store, drafts)).decisions });
    }
    if (url.searchParams.get("view") === "review") {
      if (!keyOk(req.headers.get("x-review-key"))) return json({ error: "wrong password" }, 401);
      return json(await load(store, drafts));
    }
    return json({ posts: approvedPosts(await load(store, drafts)) }, 200, { "cache-control": "public, max-age=15" });
  }

  if (req.method !== "POST") return json({ error: "method" }, 405);
  let body;
  try { body = await req.json(); } catch { return json({ error: "bad json" }, 400); }
  if (!keyOk(req.headers.get("x-review-key") || body.key)) return json({ error: "wrong password" }, 401);

  const state = await load(store, drafts);
  const save = () => store.setJSON("decisions", state.decisions);
  const { action } = body;
  const slug = body.slug || body.post?.slug;
  if (action !== "check" && !SLUG.test(slug || "")) return json({ error: "bad slug" }, 400);

  if (action === "check") return json({ ok: true });

  if (action === "approve") {
    const p = state.drafts[slug];
    if (!p) return json({ error: "no such draft" }, 404);
    state.decisions[slug] = { decision: "approved", note: String(body.note || ""), rev: p.rev, date: todayET(), ts: Date.now() };
  } else if (action === "changes") {
    const p = state.drafts[slug];
    if (!p) return json({ error: "no such draft" }, 404);
    const note = String(body.note || "").trim();
    if (!note) return json({ error: "note required" }, 400);
    state.decisions[slug] = { decision: "changes", note, rev: p.rev, ts: Date.now() };
  } else {
    return json({ error: "unknown action" }, 400);
  }
  await save();
  return json({ ok: true, state });
}

export default async (req) => {
  const store = getStore({ name: "riverstone-blog", consistency: "strong" });
  return handle(req, store);
};

export const config = { path: "/api/blog" };
