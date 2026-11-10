#!/usr/bin/env python3
"""
torgpi.com site + blog generator. Zero dependencies (stdlib only) so the daily
cron cannot rot when a pip package changes. Same engine as the other T47 sites.

- Marketing pages come from content.py via pages.py (shared chrome in chrome.py).
- Reads posts/*.md with simple `key: value` frontmatter between --- fences.
- Renders only posts whose `date` is <= today (UTC). Future-dated posts stay
  invisible until their day arrives -> that is the drip.
- Emits clean URLs: blog/<slug>/index.html, blog/index.html, rss.xml,
  sitemap.xml, robots.txt
"""
import os, re, html, datetime, xml.sax.saxutils as sx
from chrome import CFG, U, E, head, header, footer, icon, ROOT
import pages
from content import SERVICES

POSTS_DIR = os.path.join(ROOT, "posts")
BLOG_DIR = os.path.join(ROOT, "blog")
TODAY = datetime.date.today()

# ---------------------------------------------------------------- frontmatter
def parse_post(path):
    raw = open(path, encoding="utf-8").read().replace("\r\n", "\n")
    if not raw.startswith("---"):
        raise ValueError(f"{path}: missing frontmatter")
    _, fm, body = raw.split("---", 2)
    meta = {}
    for line in fm.strip().split("\n"):
        if not line.strip() or line.strip().startswith("#"):
            continue
        k, _, v = line.partition(":")
        v = v.strip()
        if len(v) > 1 and v[0] == v[-1] and v[0] in "\"'":
            v = v[1:-1]
        meta[k.strip()] = v
    meta["tags"] = [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]
    meta["date"] = datetime.date.fromisoformat(meta["date"])
    meta["slug"] = meta.get("slug") or os.path.basename(path)[:-3]
    meta["body"] = body.strip()
    return meta

# ---------------------------------------------------------------- md -> html
def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\*\w])\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", t)
    return t

def md(body):
    out, i = [], 0
    lines = body.split("\n")
    while i < len(lines):
        s = lines[i].strip()
        if not s:
            i += 1; continue
        if s.startswith("### "):
            out.append(f"<h3>{inline(s[4:])}</h3>"); i += 1; continue
        if s.startswith("## "):
            out.append(f"<h2>{inline(s[3:])}</h2>"); i += 1; continue
        if s in ("---", "***"):
            out.append("<hr />"); i += 1; continue
        if s.startswith("> "):
            buf = []
            while i < len(lines) and lines[i].strip().startswith("> "):
                buf.append(lines[i].strip()[2:]); i += 1
            out.append(f"<blockquote><p>{inline(' '.join(buf))}</p></blockquote>"); continue
        if re.match(r"^[-*] ", s):
            buf = []
            while i < len(lines) and re.match(r"^[-*] ", lines[i].strip()):
                buf.append(lines[i].strip()[2:]); i += 1
            out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in buf) + "</ul>"); continue
        if re.match(r"^\d+\. ", s):
            buf = []
            while i < len(lines) and re.match(r"^\d+\. ", lines[i].strip()):
                buf.append(re.sub(r"^\d+\.\s*", "", lines[i].strip())); i += 1
            out.append("<ol>" + "".join(f"<li>{inline(x)}</li>" for x in buf) + "</ol>"); continue
        buf = []
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#{2,3} |[-*] |\d+\. |> |---$)", lines[i].strip()):
            buf.append(lines[i].strip()); i += 1
        out.append(f"<p>{inline(' '.join(buf))}</p>")
    return "\n".join(out)

# ---------------------------------------------------------------- schema
def author_ld():
    a = CFG["author"]
    return {"@type": "Person", "@id": U + "/about/#anthony", "name": a["name"], "url": a["url"],
            "jobTitle": a["jobTitle"], "sameAs": a["sameAs"]}

def article_ld(p, url):
    return [{"@type": "BlogPosting", "headline": p["title"], "description": p["description"],
             "datePublished": p["date"].isoformat(), "dateModified": p["date"].isoformat(),
             "url": url, "mainEntityOfPage": {"@type": "WebPage", "@id": url},
             "author": author_ld(), "publisher": {"@id": U + "/#org"}, "image": U + "/og-image.png",
             "keywords": ", ".join(p["tags"]), "inLanguage": "en-US"},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": U + "/"},
                {"@type": "ListItem", "position": 2, "name": "Insights", "item": U + "/blog/"},
                {"@type": "ListItem", "position": 3, "name": p["title"], "item": url}]}]

def ctabox():
    return f"""<div class="ctabox"><h2>{E(CFG['cta_head'])}</h2><p>{E(CFG['cta_copy'])}</p>
<div class="acts"><a class="btn brass" href="/contact/">{icon('lock',18)}Free Consultation</a>
<a class="btn ghost" href="tel:{CFG['phone_tel']}">{icon('phone',18)}{CFG['phone']}</a></div></div>"""

# ---------------------------------------------------------------- render
def render_post(p):
    path = f"/blog/{p['slug']}/"
    url = U + path
    a = CFG["author"]
    tags = ('<div class="tags">' + "".join(f'<span class="tagp">{E(t)}</span>' for t in p["tags"]) + "</div>") if p["tags"] else ""
    body = f"""<div class="wrap ahead">
  <div class="crumbs" style="color:var(--faint)"><a href="/">Home</a> / <a href="/blog/">Insights</a></div>
  <span class="kicker">{E(p.get('kicker','Insights'))}</span>
  <h1>{E(p['title'])}</h1>
  <div class="meta"><span>By {a['name']}</span><span>·</span>
  <time datetime="{p['date'].isoformat()}">{p['date'].strftime('%B %-d, %Y')}</time>
  <span>·</span><span>{p['readtime']} min read</span></div>
</div>
<div class="wrap"><article class="post">{md(p['body'])}</article>{tags}
<div class="bio"><div class="av">{a['initials']}</div><div><b>{a['name']}</b>
<p>{a['bio']} <a href="/about/">More about our agency →</a></p></div></div>
{ctabox()}
<a class="backlink" href="/blog/">← All insights</a></div><div style="height:60px"></div>"""
    doc = head(f"{p['title']} | Ross and Gibson PI", p["description"], path, article_ld(p, url), og_type="article") + header("/blog/") + body + footer(SERVICES)
    d = os.path.join(BLOG_DIR, p["slug"]); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(doc)

def render_index(posts):
    path = "/blog/"
    ld = {"@type": "Blog", "name": f"{CFG['name']} — Insights", "url": U + path, "description": CFG["blog_desc"],
          "publisher": {"@id": U + "/#org"},
          "blogPost": [{"@type": "BlogPosting", "headline": p["title"], "url": f"{U}/blog/{p['slug']}/",
                        "datePublished": p["date"].isoformat()} for p in posts[:20]]}
    items = "".join(f"""<a class="item" href="/blog/{p['slug']}/"><div class="d">{p['date'].strftime('%B %-d, %Y')} · {p['readtime']} min read</div>
<h2>{E(p['title'])}</h2><p>{E(p['description'])}</p><span class="more">Read →</span></a>""" for p in posts) or \
        '<p style="color:var(--muted);padding:40px 0">First articles publishing shortly.</p>'
    body = f"""<section class="phero"><div class="container"><div class="crumbs"><a href="/">Home</a> / Insights</div>
<span class="kicker">Insights</span><h1>{E(CFG['blog_head'])}</h1><p class="lead">{E(CFG['blog_desc'])}</p></div></section>
<div class="wrap plist">{items}{ctabox()}</div><div style="height:60px"></div>"""
    doc = head(f"Insights | Private Investigation Guides | Ross and Gibson PI", CFG["blog_desc"], path, ld) + header("/blog/") + body + footer(SERVICES)
    os.makedirs(BLOG_DIR, exist_ok=True)
    open(os.path.join(BLOG_DIR, "index.html"), "w", encoding="utf-8").write(doc)

def render_feeds(posts, page_paths):
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    items = "".join(f"""<item><title>{sx.escape(p['title'])}</title>
<link>{U}/blog/{p['slug']}/</link>
<guid isPermaLink="true">{U}/blog/{p['slug']}/</guid>
<description>{sx.escape(p['description'])}</description>
<pubDate>{datetime.datetime.combine(p['date'], datetime.time(13,0,tzinfo=datetime.timezone.utc)).strftime('%a, %d %b %Y %H:%M:%S +0000')}</pubDate>
</item>""" for p in posts[:30])
    open(os.path.join(ROOT, "rss.xml"), "w", encoding="utf-8").write(
f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
<title>{sx.escape(CFG['name'])} — Insights</title>
<link>{U}/blog/</link>
<description>{sx.escape(CFG['blog_desc'])}</description>
<language>en-us</language><lastBuildDate>{now}</lastBuildDate>
{items}</channel></rss>""")
    pri = lambda p: "1.0" if p == "/" else ("0.9" if p.startswith("/services/") or p == "/contact/" else "0.7")
    urls = [(U + p, pri(p), "monthly") for p in page_paths]
    urls += [(U + "/blog/", "0.8", "daily")]
    urls += [(f"{U}/blog/{p['slug']}/", "0.6", "monthly") for p in posts]
    body = "".join(f"<url><loc>{u}</loc><changefreq>{c}</changefreq><priority>{pr}</priority></url>" for u, pr, c in urls)
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write(
        f"""<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{body}</urlset>""")
    open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8").write(
        f"User-agent: *\nAllow: /\n\nSitemap: {U}/sitemap.xml\n")

# ---------------------------------------------------------------- main
def main():
    os.makedirs(POSTS_DIR, exist_ok=True)
    allp = [parse_post(os.path.join(POSTS_DIR, f)) for f in sorted(os.listdir(POSTS_DIR)) if f.endswith(".md")]
    for p in allp:
        words = len(re.sub(r"[#*`>\[\]()-]", " ", p["body"]).split())
        p["readtime"] = max(2, round(words / 220))
    live = sorted([p for p in allp if p["date"] <= TODAY], key=lambda p: p["date"], reverse=True)
    queued = [p for p in allp if p["date"] > TODAY]
    for p in live:
        render_post(p)
    render_index(live)
    page_paths = pages.render_all(live)
    render_feeds(live, page_paths)
    print(f"[{CFG['name']}] pages={len(page_paths)} live={len(live)} queued={len(queued)} today={TODAY}")
    if queued:
        nxt = min(queued, key=lambda p: p["date"])
        print(f"  next: {nxt['date']} — {nxt['title']}")

if __name__ == "__main__":
    main()
