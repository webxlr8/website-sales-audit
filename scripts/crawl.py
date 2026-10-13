#!/usr/bin/env python3
"""Crawl a site on desktop (1440px) and mobile (iPhone 13), screenshot every page,
and run automatic checks.

Usage:
  python3 crawl.py https://client.com <report_dir> [--max 60] [--only desk|mob] [--search sofa]

URL list = homepage + sitemap pages/collections + a few products (one per
collection if Shopify products.json exists in report_dir) + search/cart/login.
Add extra URLs (one per line) in <report_dir>/extra_urls.txt.

Output: <report_dir>/crawl/{desk,mob}_NN_slug.jpg (full page) and results_*.json.
Then run sheets.py to view them. Full-page shots can have capture artefacts
(repeated header, unplayed animations) - confirm anything suspicious with
shoot.py at viewport size before reporting it.
"""
import json, os, re, sys, time, urllib.request
from playwright.sync_api import sync_playwright

UA = {"User-Agent": "Mozilla/5.0 (Macintosh) Chrome/128"}
SEARCH = sys.argv[sys.argv.index("--search") + 1] if "--search" in sys.argv else None

def fetch(u):
    try: return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30).read().decode("utf-8", "ignore")
    except Exception: return ""

def urls_for(base, root, mx):
    urls = [base + "/"]
    sm = fetch(base + "/sitemap.xml")
    subs = [u.replace("&amp;", "&") for u in re.findall(r"<loc>([^<]+)</loc>", sm)]
    for sub in subs:
        if any(k in sub for k in ("pages", "collections", "page-sitemap", "category", "post-sitemap")):
            urls += re.findall(r"<loc>([^<]+)</loc>", fetch(sub))
    if not subs:
        urls += [u for u in re.findall(r"<loc>([^<]+)</loc>", sm) if "/products/" not in u][:40]
    pj = os.path.join(root, "products.json")
    if os.path.exists(pj):
        seen = set()
        for p in json.load(open(pj)).get("products", []):
            k = next((t for t in p.get("tags", []) if t.startswith("collection:")), p.get("product_type") or "x")
            if k not in seen:
                seen.add(k); urls.append(f"{base}/products/{p['handle']}")
    else:
        prod = [u for sub in subs if "product" in sub for u in re.findall(r"<loc>([^<]+)</loc>", fetch(sub))]
        urls += prod[:6]
    term = SEARCH or "shop"
    urls += [f"{base}/search?q={term}", base + "/search?q=xyzabc", base + "/cart", base + "/account/login", base + "/this-page-should-404"]
    ex = os.path.join(root, "extra_urls.txt")
    if os.path.exists(ex): urls += [l.strip() for l in open(ex) if l.strip()]
    out = []
    for u in urls:
        if u not in out and not re.search(r"\.(jpg|png|webp|pdf|xml)(\?|$)", u): out.append(u)
    return out[:mx]

CHECK = r"""() => {
  const W = innerWidth, res = {docW: document.documentElement.scrollWidth, W, H: document.documentElement.scrollHeight, title: document.title};
  res.brokenImgs = [...document.images].filter(i => i.complete && i.naturalWidth === 0 && i.getBoundingClientRect().width > 0 && !i.src.startsWith('data:')).map(i => i.src.slice(0,120));
  res.h1 = [...document.querySelectorAll('h1')].map(h => h.innerText.trim().slice(0,60));
  const txt = document.body.innerText.toLowerCase();
  const bad = ['lorem','ipsum','your content','tell your brand','add a description','image with text','talk about your brand','no related products',"couldn't load",'oops','not found','no products',"can't find",'coming soon','example product','collection title','placeholder','test product','dummy','under construction'];
  res.badText = bad.filter(b => txt.includes(b));
  res.metaDesc = (document.querySelector('meta[name=description]')||{}).content || '';
  res.deadLinks = [...document.querySelectorAll('a[href="#"],a[href=""]')].filter(a => a.getBoundingClientRect().width > 0 && a.innerText.trim()).map(a => a.innerText.trim().slice(0,30)).slice(0,8);
  return res;
}"""

def main():
    base, root = sys.argv[1].rstrip("/"), sys.argv[2]
    mx = int(sys.argv[sys.argv.index("--max")+1]) if "--max" in sys.argv else 60
    only = sys.argv[sys.argv.index("--only")+1] if "--only" in sys.argv else None
    out = os.path.join(root, "crawl"); os.makedirs(out, exist_ok=True)
    urls = urls_for(base, root, mx)
    print(len(urls), "urls"); open(os.path.join(out, "urls.txt"), "w").write("\n".join(urls))
    with sync_playwright() as p:
        try: b = p.chromium.launch(channel="chrome", headless=True)
        except Exception: b = p.chromium.launch(headless=True)
        for tag, ctx in [("desk", b.new_context(viewport={"width": 1440, "height": 900})), ("mob", b.new_context(**p.devices["iPhone 13"]))]:
            if only and tag != only: continue
            results = []
            for i, u in enumerate(urls):
                pg = ctx.new_page(); errs = []
                pg.on("console", lambda m: errs.append(m.text[:140]) if m.type == "error" else None)
                try:
                    r = pg.goto(u, wait_until="load", timeout=60000); st = r.status if r else None
                except Exception as e:
                    st = "ERR " + str(e)[:60]
                time.sleep(2.5)
                try:
                    h = pg.evaluate("document.documentElement.scrollHeight")
                    for y in range(0, min(h, 20000), 700): pg.evaluate(f"window.scrollTo(0,{y})"); time.sleep(0.1)
                    pg.evaluate("window.scrollTo(0,0)"); time.sleep(0.8)
                    info = pg.evaluate(CHECK)
                except Exception as e:
                    info = {"err": str(e)[:100]}
                slug = re.sub(r"[^a-z0-9]+", "-", u.replace(base, "").lower()).strip("-") or "home"
                shot = os.path.join(out, f"{tag}_{i:02d}_{slug[:60]}.jpg")
                try: pg.screenshot(path=shot, full_page=True, type="jpeg", quality=55)
                except Exception as e: info["shoterr"] = str(e)[:80]
                info.update(url=u, status=st, console=errs[:6], shot=shot); results.append(info); pg.close()
                flags = [f"STATUS {st}"] if st != 200 else []
                if info.get("docW", 0) > info.get("W", 0): flags.append(f"HSCROLL {info['docW']}>{info['W']}")
                if info.get("brokenImgs"): flags.append(f"BROKENIMG {len(info['brokenImgs'])}")
                if info.get("badText"): flags.append("TEXT " + ",".join(info["badText"]))
                if info.get("h1") in ([], [""]): flags.append("NO-H1")
                print(tag, i, u.replace(base, "") or "/", " ; ".join(flags), flush=True)
            json.dump(results, open(os.path.join(out, f"results_{tag}.json"), "w"), indent=1)
        b.close()

if __name__ == "__main__":
    main()
