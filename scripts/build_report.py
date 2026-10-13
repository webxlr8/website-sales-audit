#!/usr/bin/env python3
"""Build an agency-branded website sales audit PDF from report.json.

Usage:
  python3 build_report.py <report_dir>                       # reads <report_dir>/report.json
  python3 build_report.py <report_dir> --agency path.json    # explicit agency config
  python3 build_report.py <report_dir> --no-pdf              # HTML only

Agency branding (name, logos, colours, contacts) comes from the first of:
  --agency <file> | $WSA_AGENCY | <report_dir>/agency.json |
  ~/.config/website-sales-audit/agency.json | assets/agency.example.json

Writes <report_dir>/<slug>-audit.html, <slug>-audit.pdf and _preview.png
(thumbnail sheet of every page for visual QA). Prints any page whose
content runs into the footer (overflow > 0pt) so you can shrink visuals.
See references/report-json.md for the schema.
"""
import json, os, re, shutil, sys, time, html as H

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(SKILL, "assets")

def esc(s): return H.escape(s or "", quote=False)

SEV = {"Urgent": ("crit", "", ""), "High": ("high", "amber", "amber"), "Medium": ("med2", "blue", "blue")}
CONTENT_W_MM = 176

def find_agency(root):
    cands = []
    if "--agency" in sys.argv: cands.append(sys.argv[sys.argv.index("--agency") + 1])
    if os.environ.get("WSA_AGENCY"): cands.append(os.environ["WSA_AGENCY"])
    cands += [os.path.join(root, "agency.json"),
              os.path.expanduser("~/.config/website-sales-audit/agency.json"),
              os.path.join(ASSETS, "agency.example.json")]
    for c in cands:
        if c and os.path.exists(c):
            return os.path.abspath(c)
    raise SystemExit("No agency config found")

def hex_rgb(h):
    h = h.lstrip("#"); h = "".join(ch * 2 for ch in h) if len(h) == 3 else h
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def mix(h, t):  # mix colour h with white; t = share of white
    r, g, b = hex_rgb(h)
    return "#%02x%02x%02x" % tuple(round(c + (255 - c) * t) for c in (r, g, b))

def brand_vars(a):
    col = a.get("colors", {})
    acc = col.get("accent", "#ff6a3a")
    v = {"--accent": acc, "--accent-2": col.get("accent_2", acc), "--accent-3": col.get("accent_3", mix(acc, 0.35)),
         "--accent-ink": col.get("accent_ink", acc), "--accent-bg": col.get("accent_bg", mix(acc, 0.92)),
         "--accent-border": col.get("accent_border", mix(acc, 0.72)), "--accent-rgb": ",".join(map(str, hex_rgb(acc))),
         "--dark": col.get("dark", "#0b0b0b"), "--dark-2": col.get("dark_2", "#141414")}
    return ";".join(f"{k}:{v}" for k, v in v.items())

class R:
    def __init__(self, d, root, agency_path):
        self.d, self.root = d, root
        self.agency = json.load(open(agency_path))
        self.agency_dir = os.path.dirname(agency_path)
        self.c = d["client"]
        a = self.agency
        self.logo_on_light = self.asset(a.get("logo_on_light"))
        self.logo_on_dark = self.asset(a.get("logo_on_dark"))
        self.icon = self.asset(a.get("icon"))
        self.client_logos = [x for x in (self.asset(l) for l in a.get("client_logos", [])) if x]

    def asset(self, rel):
        """Copy an agency asset into _assets/agency/ and return its page-relative path."""
        if not rel: return None
        src = rel if os.path.isabs(rel) else os.path.join(self.agency_dir, rel)
        if not os.path.exists(src):
            print("WARNING: agency asset not found:", src); return None
        dst_dir = os.path.join(self.root, "_assets", "agency"); os.makedirs(dst_dir, exist_ok=True)
        shutil.copy(src, os.path.join(dst_dir, os.path.basename(src)))
        return "_assets/agency/" + os.path.basename(src)

    def wordmark(self, dark_bg, cls=""):
        src = self.logo_on_dark if dark_bg else self.logo_on_light
        if src: return f'<img class="{cls}" src="{src}" alt="{esc(self.agency["name"])}">'
        color = "#fff" if dark_bg else "var(--dark)"
        return f'<span class="{cls} wm" style="color:{color}">{esc(self.agency["name"])}</span>'

    # ---------- shared bits ----------
    def run(self, label):
        return f'<div class="run">{self.wordmark(False)}<span>{esc(label)}</span></div>'
    def foot(self):
        a = self.agency
        icon = f'<img src="{self.icon}" alt="">' if self.icon else ""
        return (f'<div class="foot"><span class="brand">{icon}{esc(a["name"])} · '
                f'Website Sales Audit for {esc(self.c["name"])} · Confidential</span>'
                f'<span><span style="margin-right:10pt">{esc(a["website"])}</span><span class="pn">0</span></span></div>')
    def page(self, label, inner, id_=None):
        i = f' id="{id_}"' if id_ else ""
        return f'<section class="sheet"{i}>{self.run(label)}{inner}{self.foot()}</section>'

    def img_size(self, rel):
        try:
            from PIL import Image
            return Image.open(os.path.join(self.root, rel)).size
        except Exception:
            return (1600, 1000)

    def frame(self, v, target_mm):
        f = (f'<div class="frame"><div class="bar"><i></i><i></i><i></i><span>{esc(v.get("url",""))}</span></div>'
             f'<img src="{v["img"]}" alt=""></div>')
        if v.get("full"):
            inner = f
        else:
            if v.get("width"):
                pct = v["width"]
            else:
                w, h = self.img_size(v["img"])
                pct = f'{min(100, (target_mm / (h / w)) / CONTENT_W_MM * 100):.0f}%'
            inner = f'<div class="fw" style="width:{pct}">{f}</div>'
        cap = f'<div class="cap" style="text-align:center">{v["caption"]}</div>' if v.get("caption") else ""
        return f'<div class="shot">{inner}{cap}</div>'

    def phone(self, v):
        cap = f'<div class="cap">{v["caption"]}</div>' if v.get("caption") else ""
        return f'<div><div class="phone"><img src="{v["img"]}" alt=""></div>{cap}</div>'

    def visual(self, v, target_mm, half):
        t = v.get("type", "frame")
        if t == "frame":
            return self.frame(v, target_mm)
        if t == "phones":
            w = v.get("width_mm", 28 if half else 36)
            items = "".join(f'<div style="width:{w}mm">{self.phone(p)[5:-6]}</div>' for p in v["items"])
            note = f'<div style="flex:1;align-self:center;font-size:8.6pt">{v["note"]}</div>' if v.get("note") else ""
            return f'<div class="phones" style="margin-bottom:8pt">{items}{note}</div>'
        if t == "phone_frame":  # phone + laptop frame side by side
            pw = v.get("phone_mm", 24); fw = v.get("frame_mm", 112)
            fr = (f'<div class="frame"><div class="bar"><i></i><i></i><i></i><span>{esc(v.get("url",""))}</span></div>'
                  f'<img src="{v["frame_img"]}" alt=""></div>')
            cap = f'<div class="cap" style="text-align:center">{v["caption"]}</div>' if v.get("caption") else ""
            return (f'<div class="side" style="grid-template-columns:{pw}mm {fw}mm;justify-content:center">'
                    f'{self.phone({"img": v["phone_img"]})}{fr}</div>{cap}')
        if t == "grid":
            cells = "".join(f'<div class="frame"><div class="bar"><i></i><i></i><i></i><span>{esc(x.get("url",""))}</span></div><img src="{x["img"]}" alt=""></div>' for x in v["items"])
            cap = f'<div class="cap">{v["caption"]}</div>' if v.get("caption") else ""
            return f'<div class="grid2" style="gap:8pt;margin-bottom:6pt">{cells}</div>{cap}'
        if t == "table":
            head = "".join(f"<th>{h}</th>" for h in v["head"])
            rows = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in v["rows"])
            return f'<table class="tbl-sm"><tr>{head}</tr>{rows}</table>'
        if t == "callouts":
            return '<ol class="callouts">' + "".join(f"<li>{x}</li>" for x in v["items"]) + "</ol>"
        if t == "note":
            return (f'<div class="where" style="background:#f4f4f4;border-color:#e8e8e8"><span class="k" style="color:var(--ink)">'
                    f'{v.get("title","Also")}</span>{v["html"]}</div>')
        if t == "html":
            return v["html"]
        raise ValueError("unknown visual type " + t)

    def where(self, html):
        return f'<div class="where"><span class="k">Where to see it</span>{html}</div>' if html else ""

    # ---------- issue layouts ----------
    def issue_full(self, it):
        sev, ecls, bcls = SEV[it["severity"]]
        vis = "".join(self.visual(v, it.get("target_mm", 78), False) for v in it.get("visuals", []))
        return self.page(f'PROBLEM {it["n"]} · {it["area"].upper()}', f'''
  <div class="ihead"><div class="big {bcls}">{it["n"]:02d}</div><div>
    <div class="eyebrow {ecls}">{esc(it["area"])} <span class="sev {sev}">{it["severity"]}</span></div>
    <h2 class="title">{it["title"]}</h2></div></div>
  <p class="say">{it["say"]}</p>
  {self.where(it.get("where"))}
  {vis}
  <div class="cards">
    <div class="card impact"><h4><span class="ic">!</span>Why it costs sales</h4>{it["why"]}</div>
    <div class="card us"><h4><span class="ic">✓</span>What we'll do</h4>{it["fix"]}</div>
  </div>''', f'i{it["n"]}')

    def issue_half(self, it):
        sev, ecls, ncls = SEV[it["severity"]]
        vis = "".join(self.visual(v, it.get("target_mm", 58), True) for v in it.get("visuals", []))
        return f'''<div class="mini"><div class="mh"><div class="mn {ncls}">{it["n"]:02d}</div><div><div class="eyebrow {ecls}">{esc(it["area"])} <span class="sev {sev}">{it["severity"]}</span></div><h3>{it["title"]}</h3></div></div>
<p class="say2">{it["say"]}</p>{self.where(it.get("where"))}{vis}
<div class="fixline"><span class="w"><b>Problem:</b> {it["why"]}</span><span class="u"><b>We'll fix:</b> {it["fix"]}</span></div></div>'''

    # ---------- pages ----------
    def cover(self):
        c, a = self.c, self.agency
        photo = f'style="background-image:url({c["cover_photo"]})"' if c.get("cover_photo") else ""
        logo = f'<img src="{c["logo"]}" alt="">' if c.get("logo") else ""
        return f'''<section class="sheet cover"><div class="glow"></div><div class="top">
    {self.wordmark(True, "logo")}
    <div><span class="chip">Website Sales Audit · Prepared for {esc(c["name"])}</span></div>
    <h1>{self.d.get("title_html", "Why the website<br>isn't <em>selling</em>,<br>and how we'll fix it.")}</h1>
    <p class="sub">{self.d.get("subtitle","")}</p></div>
  <div class="photo" {photo}><span class="tagk">{logo}{esc(c["site"])}</span></div>
  <div class="meta">
    <div><small>Prepared for</small>{esc(c.get("legal", c["name"]))}</div>
    <div><small>Audit date</small>{esc(self.d["date"])}</div>
    <div><small>Prepared by</small>{esc(a["name"])} · {esc(a["website"])}</div></div></section>'''

    def summary(self):
        s = self.d.get("summary", {})
        issues = self.d["issues"]
        counts = {k: sum(1 for i in issues if i["severity"] == k) for k in SEV}
        stats = s.get("stats") or [
            {"n": str(counts["Urgent"]), "label": "urgent problems that stop people from buying", "style": "dark"},
            {"n": str(counts["High"]), "label": "broken or empty pages and features", "style": "amber"},
            {"n": str(counts["Medium"]), "label": "smaller design and text problems", "style": "blue"}]
        def stat(x):
            st = x.get("style", "")
            ncol = {"amber": ' class="n amber"', "blue": ' class="n" style="color:#2563eb"'}.get(st, ' class="n"')
            return f'<div class="stat{" dark" if st=="dark" else ""}"><div{ncol}>{x["n"]}</div><div class="l">{x["label"]}</div></div>'
        rows = "".join(f'<tr><td>{i["n"]}</td><td>{i["title"]}</td><td>{i.get("where_short","")}</td><td><span class="sev {SEV[i["severity"]][0]}">{i["severity"]}</span></td></tr>' for i in issues)
        title = s.get("title", f'{len(issues)} problems are stopping sales on your website')
        lead = s.get("lead", f'We opened every page on a laptop and a phone. The first {counts["Urgent"]} problems stop people from buying today.')
        return self.page("SUMMARY", f'''<div class="eyebrow">In one page</div>
  <h2 class="title">{title}</h2><p class="lead" style="margin-bottom:8pt">{lead}</p>
  <div class="stats" style="margin-bottom:10pt">{"".join(stat(x) for x in stats)}</div>
  <table class="tbl-sm"><tr><th style="width:5%">#</th><th style="width:44%">Problem</th><th style="width:37%">Where</th><th>Level</th></tr>{rows}</table>''', "summary")

    def more(self):
        m = self.d.get("more")
        if not m: return ""
        lis = "".join(f'<li><b>{x["what"]}<span class="w">Today: {x["today"]}</span></b><span>{x["do"]}</span></li>' for x in m["items"])
        return self.page("MORE SALES", f'''<div class="eyebrow navy">After the fixes</div><h2 class="title">{m.get("title","What else will bring more sales")}</h2>
  <p class="lead">{m.get("lead","")}</p><ul class="simple">{lis}</ul>''', "more")

    def plan(self):
        p = self.d.get("plan")
        if not p: return ""
        weeks = "".join(f'<div class="week"><div class="wk">{w["label"]}</div><h4>{w["title"]}</h4><ul>{"".join(f"<li>{i}</li>" for i in w["items"])}</ul></div>' for w in p["weeks"])
        cl = p.get("closing", {})
        method = f'<p class="method" style="margin-top:12pt">{self.d["method"]}</p>' if self.d.get("method") else ""
        return self.page("PLAN", f'''<div class="eyebrow navy">Our plan</div><h2 class="title">{p.get("title","A selling website in 30 days")}</h2>
  <p class="lead">{p.get("lead","")}</p><div class="weeks">{weeks}</div>
  <div class="closing"><div><h3>{cl.get("title","Start with Week 1")}</h3><p>{cl.get("text","")}</p></div><div class="cta">{esc(self.agency["email"])}</div></div>{method}''', "plan")

    def why(self):
        a = self.agency
        fit = self.d.get("why_fit") or a.get("default_fit", [])
        stats = "".join(f'<div><b>{s["n"]}</b>{s["label"]}</div>' for s in a.get("stats", []))
        stats = f'<div class="wxstats">{stats}</div>' if stats else ""
        fits = "".join(f'<div class="fit"><div class="k">{f["k"]}</div><h4>{f["title"]}</h4>{f["text"]}</div>' for f in fit[:3])
        logos = "".join(f'<img src="{l}" alt="">' for l in self.client_logos)
        wall = f'<div class="wall"><div class="k">Brands we\'ve worked with</div><div class="row">{logos}</div></div>' if logos else ""
        return self.page("WHY " + a["name"].upper(), f'''<div class="eyebrow navy">Why {esc(a["name"])}</div>
  <h2 class="title">One team to fix it, build it and keep it running</h2><p class="lead">{a["about"]}</p>
  {stats}<div class="fitcards">{fits}</div>
  {wall}''', "why")

    def appendix(self):
        ap = self.d.get("appendix")
        if not ap: return ""
        items = []
        for g in ap["groups"]:
            for k, x in enumerate(g["items"]):
                items.append((g["name"] if k == 0 else None, g["name"], len(g["items"]), x))
        first, per = ap.get("first_page", 38), ap.get("per_page", 48)
        pages = [items[:first]] + [items[i:i+per] for i in range(first, len(items), per)]
        out = []
        for n, pg in enumerate(pages):
            body = []
            for j, (head, k, cnt, x) in enumerate(pg):
                if head or j == 0:
                    body.append(f'<h4>{esc(k)} ({cnt}){"" if head else " · cont."}</h4>')
                body.append(f'<div><a href="{x["url"]}">{esc(x["title"])}</a></div>')
            intro = (f'<div class="eyebrow navy">Appendix</div><h2 class="title">{ap["title"]}</h2>'
                     f'<p class="lead" style="font-size:9pt;margin-bottom:8pt">{ap.get("intro","")}</p>') if n == 0 else ""
            out.append(self.page("APPENDIX", intro + f'<div class="appendix">{"".join(body)}</div>', "appendix" if n == 0 else None))
        return "\n".join(out)

    def back(self):
        a, b = self.agency, self.d.get("back", {})
        return f'''<section class="sheet back"><div class="glow"></div><div class="in">
    {self.wordmark(True)}
    <h2>{b.get("title_html", "Let's get " + esc(self.c["name"]) + "<br><em>selling online</em>.")}</h2>
    <p>{b.get("text","")}</p>
    <div class="contact"><div><small>Email</small>{esc(a["email"])}</div><div><small>Phone</small>{esc(a["phone"])}</div>
      <div><small>Website</small>{esc(a["website"])}</div><div><small>Office</small>{esc(a["office"])}</div></div>
    <div class="tag">{esc(a["tagline"])}</div></div></section>'''

    def font_link(self):
        f = self.c.get("font", {"family": "Inter", "google": True})
        fam = f["family"]
        if f.get("css_url"):
            return f'<link href="{f["css_url"]}" rel="stylesheet">', fam
        if f.get("google", True):
            q = fam.replace(" ", "+")
            return f'<link href="https://fonts.googleapis.com/css2?family={q}:wght@300;400;500;600;700&display=swap" rel="stylesheet">', fam
        if f.get("face_css"):
            return f'<style>{f["face_css"]}</style>', fam
        return "", fam

    def build(self):
        issues = self.d["issues"]
        body = [self.cover(), self.summary()]
        half_buf = []
        def flush():
            if half_buf:
                ns = [i["n"] for i in half_buf]
                label = f'PROBLEMS {ns[0]}–{ns[-1]}' if len(ns) > 1 else f'PROBLEM {ns[0]}'
                body.append(self.page(label, "".join(self.issue_half(i) for i in half_buf)))
                half_buf.clear()
        for it in issues:
            if it.get("layout", "half") == "full":
                flush(); body.append(self.issue_full(it))
            else:
                half_buf.append(it)
                if len(half_buf) == 2: flush()
        flush()
        body += [self.more(), self.plan()]
        if self.d.get("include_why", True): body.append(self.why())
        body += [self.appendix(), self.back()]
        link, fam = self.font_link()
        css = open(os.path.join(ASSETS, "report.css")).read()
        return f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>{esc(self.c["name"])} Website Sales Audit</title>{link}
<style>:root{{--font:"{fam}";{brand_vars(self.agency)}}}\n.wm{{font-weight:700;letter-spacing:.02em;font-size:13pt}} .cover .wm{{font-size:22pt}} .back .in > .wm{{font-size:24pt}}\n{css}</style></head><body>
{"".join(b for b in body if b)}
</body></html>'''

def main():
    root = os.path.abspath(sys.argv[1])
    d = json.load(open(os.path.join(root, "report.json")))
    dst = os.path.join(root, "_assets")
    if os.path.exists(dst): shutil.rmtree(dst)
    agency_path = find_agency(root)
    print("AGENCY CONFIG", agency_path)
    if agency_path.endswith("agency.example.json"):
        print("WARNING: using the placeholder agency. Create ~/.config/website-sales-audit/agency.json (see README).")
    r = R(d, root, agency_path)
    slug = re.sub(r"[^a-z0-9]+", "-", d["client"]["name"].lower()).strip("-")
    out_html = os.path.join(root, f"{slug}-audit.html")
    open(out_html, "w").write(r.build())
    print("HTML", out_html)
    if "--no-pdf" in sys.argv: return
    from playwright.sync_api import sync_playwright
    aslug = re.sub(r"[^a-z0-9]+", "-", r.agency["name"].lower()).strip("-")
    out_pdf = os.path.join(root, d.get("pdf_name", f"{aslug}-{slug}-website-audit.pdf"))
    with sync_playwright() as pw:
        try: b = pw.chromium.launch(channel="chrome", headless=True)
        except Exception: b = pw.chromium.launch(headless=True)
        pg = b.new_page()
        pg.goto("file://" + out_html, wait_until="networkidle"); pg.evaluate("document.fonts.ready"); time.sleep(1.5)
        pg.evaluate("""()=>{const sh=[...document.querySelectorAll('.sheet')];sh.forEach((s,i)=>{const p=s.querySelector('.foot .pn');if(p)p.textContent=i+1})}""")
        over = pg.evaluate("""()=>[...document.querySelectorAll('.sheet')].map((s,i)=>{const f=s.querySelector('.foot');if(!f)return null;const lim=f.getBoundingClientRect().top;let mx=0;
          s.querySelectorAll('*').forEach(e=>{if(e.closest('.foot')||e.closest('.run'))return;const r=e.getBoundingClientRect();if(r.height>0)mx=Math.max(mx,r.bottom)});
          return [i+1,Math.round(mx-lim)]}).filter(x=>x&&x[1]>-2)""")
        fonts = pg.evaluate("[...new Set([...document.fonts].filter(f=>f.status=='loaded').map(f=>f.family))].join(', ')")
        pg.pdf(path=out_pdf, format="A4", print_background=True, prefer_css_page_size=True)
        b.close()
    print("PDF", out_pdf)
    print("FONTS LOADED:", fonts or "none (fallback in use!)")
    print("OVERFLOW (page, pt into footer):", over if over else "none")
    try:
        import pypdfium2 as p
        from PIL import Image
        doc = p.PdfDocument(out_pdf)
        ims = [doc[i].render(scale=34/72).to_pil() for i in range(len(doc))]
        w, h = ims[0].size; cols = 6; rows = (len(ims)+cols-1)//cols
        S = Image.new("RGB", (w*cols, h*rows), "#888")
        for i, im in enumerate(ims): S.paste(im, ((i % cols)*w, (i//cols)*h))
        S.save(os.path.join(root, "_preview.png")); print("PREVIEW", os.path.join(root, "_preview.png"), len(ims), "pages")
    except Exception as e:
        print("preview skipped:", e)

if __name__ == "__main__":
    main()
