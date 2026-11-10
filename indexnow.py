"""Notify Bing (IndexNow) about pages published by the last commit.
Run after the publish commit is pushed. Only newly added post pages are submitted (daily rebuilds touch every page)."""
import json, os, subprocess, sys, urllib.request
ROOT = os.path.dirname(os.path.abspath(__file__))
CFG = json.load(open(os.path.join(ROOT, "site.json"), encoding="utf-8"))
KEY = open(os.path.join(ROOT, "indexnow-key.txt")).read().strip()
base = CFG["url"].rstrip("/")
host = base.split("://", 1)[1]
try:
    changed = subprocess.check_output(["git", "diff", "--name-only", "--diff-filter=A", "HEAD~1", "HEAD"], cwd=ROOT, text=True).split()
except subprocess.CalledProcessError:
    changed = []
urls = set()
for f in changed:
    if f.startswith("blog/") and f.endswith("/index.html"):
        urls.add(f"{base}/{f[:-len('index.html')]}")
if urls:
    urls.add(f"{base}/blog/")  # index lists the new post
if not urls:
    print("IndexNow: nothing new to submit"); sys.exit(0)
body = json.dumps({"host": host, "key": KEY, "keyLocation": f"{base}/{KEY}.txt", "urlList": sorted(urls)}).encode()
req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body, headers={"Content-Type": "application/json; charset=utf-8"})
try:
    with urllib.request.urlopen(req, timeout=20) as r:
        print("IndexNow:", r.status, len(urls), "URLs")
except Exception as e:  # never fail the publish job over a ping
    print("IndexNow skipped:", e)
