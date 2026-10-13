#!/usr/bin/env python3
"""Extract a client's brand from their live website.

Usage: python3 brand.py https://client.com <report_dir>

Prints platform, fonts, colours, logo/og-image candidates and saves
<report_dir>/brand.json plus downloaded logo / og image into <report_dir>/img/.
Always LOOK at the downloaded logo before using it (it may be white-on-transparent).
"""
import re, sys, os, json, collections, urllib.request, urllib.parse, html as H

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/128 Safari/537.36"}

def get(u, binary=False):
    r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30)
    b = r.read()
    return b if binary else b.decode("utf-8", "ignore")

def main():
    url, out = sys.argv[1].rstrip("/"), sys.argv[2]
    os.makedirs(os.path.join(out, "img"), exist_ok=True)
    base = "{0.scheme}://{0.netloc}".format(urllib.parse.urlparse(url))
    s = get(url + "/")
    res = {"url": url}
    res["title"] = H.unescape((re.findall(r"<title>(.*?)</title>", s, re.S) or [""])[0].strip())
    gen = []
    for k, pat in [("Shopify", r"cdn\.shopify\.com|Shopify\.theme"), ("WooCommerce", r"woocommerce"), ("WordPress", r"wp-content"),
                   ("Wix", r"wixstatic|_wix"), ("Squarespace", r"squarespace"), ("Webflow", r"webflow"), ("Next.js", r"_next/"), ("Astro", r"/_astro/")]:
        if re.search(pat, s, re.I): gen.append(k)
    res["platform"] = gen
    css = s
    for c in re.findall(r'href="([^"]+\.css[^"]*)"', s)[:12]:
        u = urllib.parse.urljoin(base + "/", H.unescape(c))
        try: css += get(u)
        except Exception: pass
    fams = collections.Counter(f.strip().strip("'\"") for f in re.findall(r"font-family:\s*([^;,}\"]+)", css))
    res["fonts"] = [f for f, _ in fams.most_common(8) if f and not f.startswith("var(") and f.lower() not in ("inherit", "initial", "sans-serif", "serif", "monospace")]
    res["font_vars"] = sorted(set(re.findall(r"--[\w-]*font[\w-]*:\s*([^;}]{1,60})", css)))[:10]
    res["google_fonts"] = sorted(set(re.findall(r"fonts\.googleapis\.com/css2?\?family=([^\"'&:]+)", css)))
    res["font_face"] = sorted(set(m.strip().strip("'\"") for m in re.findall(r"@font-face\s*\{[^}]*?font-family:\s*([^;]+);", css)))
    cols = collections.Counter(x.lower() for x in re.findall(r"#[0-9a-fA-F]{6}\b", css))
    res["colors"] = [c for c, _ in cols.most_common(14)]
    res["color_vars"] = sorted(set(re.findall(r"--[\w-]*(?:primary|accent|brand|heading|button)[\w-]*:\s*(#[0-9a-fA-F]{3,6})", css)))[:12]
    logos = []
    for tag in re.findall(r"<img[^>]+>", s):
        if re.search(r"logo", tag, re.I):
            m = re.search(r'src="([^"]+)"', tag)
            if m: logos.append(urllib.parse.urljoin(base + "/", H.unescape(m.group(1))))
    res["logo_candidates"] = list(dict.fromkeys(logos))[:5]
    og = re.findall(r'property="og:image"\s+content="([^"]+)"', s)
    res["og_image"] = og[0] if og else None
    fav = re.findall(r'<link[^>]+rel="(?:shortcut )?icon"[^>]+href="([^"]+)"', s)
    res["favicon"] = urllib.parse.urljoin(base + "/", fav[0]) if fav else None
    res["contacts"] = sorted(set(re.findall(r"(?:tel:|mailto:|wa\.me/)[^\"'?]+", s)))[:10]
    saved = []
    for i, u in enumerate(res["logo_candidates"][:2] + ([res["og_image"]] if res["og_image"] else [])):
        try:
            u2 = re.sub(r"width=\d+", "width=1200", u)
            b = get(u2, True)
            ext = ".png" if b[:4] == b"\x89PNG" else ".svg" if b.lstrip()[:4] in (b"<svg", b"<?xm") else ".jpg"
            name = ("client_logo%d" % i if i < len(res["logo_candidates"][:2]) else "og_image") + ext
            open(os.path.join(out, "img", name), "wb").write(b); saved.append("img/" + name)
        except Exception as e:
            saved.append(f"FAILED {u}: {e}")
    res["saved"] = saved
    if "Shopify" in gen:
        try:
            pj = json.loads(get(base + "/products.json?limit=250"))
            res["shopify_products"] = len(pj.get("products", []))
            json.dump(pj, open(os.path.join(out, "products.json"), "w"))
        except Exception as e:
            res["shopify_products"] = f"failed: {e}"
    json.dump(res, open(os.path.join(out, "brand.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))

if __name__ == "__main__":
    main()
