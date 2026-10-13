#!/usr/bin/env python3
"""Capture annotated evidence screenshots from a JSON list of shots.

Usage: python3 shoot.py <report_dir> shots.json [name ...]

Each shot (all keys optional except name/url):
{
  "name": "pdp_top",                 # -> <report_dir>/shots/pdp_top.png
  "device": "desktop" | "mobile",    # 1440x900 @1.5x, or iPhone 13
  "url": "https://site.com/products/x",
  "wait": 3,
  "steps": [                          # run in order before marking
    {"hover": "css selector"}, {"click": "css selector"}, {"click_text": "Add to Cart"},
    {"press": "Escape"}, {"type": "sofa bed"}, {"wait": 2},
    {"scroll_y": 1500}, {"scroll_to_text": "Visit Our Store", "offset": 120}
  ],
  "mark": [                           # numbered red boxes, in order 1,2,3...
    {"text": "3-5 days International"},          # yellow highlight + box around its block
    {"text": "Our Story", "hl": false, "up": 1}, # no highlight, box one level up
    {"wa": true},                                # floating WhatsApp / chat button
    {"button": "Add to Cart"},                   # visible button starting with this text
    {"selector": "select"}
  ],
  "full_page": false
}
Prints what each mark found (True/False). False = not found -> adjust and re-run
just that shot. Always Read the PNG afterwards to confirm the box is where you think.
"""
import json, os, sys, time
from playwright.sync_api import sync_playwright

JS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "mark.js")).read()

def run_shot(ctx, s, out):
    pg = ctx.new_page()
    pg.goto(s["url"], wait_until="load", timeout=60000); time.sleep(s.get("wait", 3))
    for st in s.get("steps", []):
        try:
            if "hover" in st: pg.locator(st["hover"]).first.hover(); time.sleep(1)
            elif "click" in st: pg.locator(st["click"]).first.click(force=True); time.sleep(st.get("after", 3))
            elif "click_text" in st: pg.get_by_role("button", name=st["click_text"]).first.click(); time.sleep(st.get("after", 6))
            elif "press" in st: pg.keyboard.press(st["press"]); time.sleep(1)
            elif "type" in st: pg.keyboard.type(st["type"]); time.sleep(st.get("after", 3))
            elif "wait" in st: time.sleep(st["wait"])
            elif "scroll_y" in st: pg.evaluate(f"window.scrollTo(0,{st['scroll_y']})"); time.sleep(1.5)
            elif "scroll_to_text" in st:
                pg.add_script_tag(content=JS)
                pg.evaluate("([t,o])=>{const n=__mk.findText(t,false); if(n){n.parentElement.scrollIntoView({block:'start'}); window.scrollBy(0,-o);}}",
                            [st["scroll_to_text"], st.get("offset", 150)]); time.sleep(1.5)
        except Exception as e:
            print("   step failed", st, str(e)[:100])
    pg.add_script_tag(content=JS)
    for m in s.get("mark", []):
        if "text" in m: r = pg.evaluate("([t,o])=>__mk.text(t,o)", [m["text"], {k: v for k, v in m.items() if k != "text"}])
        elif m.get("wa"): r = pg.evaluate("__mk.wa()")
        elif "button" in m: r = pg.evaluate("t=>__mk.btn(t)", m["button"])
        elif "selector" in m: r = pg.evaluate("q=>__mk.sel(q)", m["selector"])
        else: r = "?"
        print("   mark", m, "->", r)
    path = os.path.join(out, s["name"] + ".png")
    pg.screenshot(path=path, full_page=s.get("full_page", False)); pg.close()
    print("   saved", path)

def main():
    root, spec = sys.argv[1], json.load(open(sys.argv[2]))
    names = sys.argv[3:]
    out = os.path.join(root, "shots"); os.makedirs(out, exist_ok=True)
    with sync_playwright() as p:
        try: b = p.chromium.launch(channel="chrome", headless=True)
        except Exception: b = p.chromium.launch(headless=True)
        dk = b.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=1.5)
        mb = b.new_context(**p.devices["iPhone 13"])
        for s in spec:
            if names and s["name"] not in names: continue
            print(s["name"])
            try: run_shot(mb if s.get("device") == "mobile" else dk, s, out)
            except Exception as e: print("   FAILED", str(e)[:150])
        b.close()

if __name__ == "__main__":
    main()
