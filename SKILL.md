---
name: website-sales-audit
description: Audit a live website (e-commerce, Shopify, WooCommerce, any storefront or business site) for everything that hurts sales (broken checkout, theme template leftovers, fake urgency, broken or empty pages, mobile layout bugs, typos, contradicting policies, trust gaps) and produce a polished, agency-branded PDF report with annotated screenshots, a "Where to see it" click path for every problem, the client's own font and logo, a 30-day plan and a "Why us" page. Use this whenever the user asks to audit, review, check or analyse a website to increase sales or conversions, find UI/UX or CRO issues, or prepare a website audit, report, proposal or pitch document for a client or prospect, e.g. "audit this site and tell me what to fix", "find all the issues with screenshots so I can show the client", "make an audit PDF for this store", even if they don't mention a skill or a PDF.
---

# Website sales audit → client-ready PDF

Output: an A4 PDF in **the agency's branding** (logo, accent colour, contact back cover) that uses **the client's own font and logo**. Every problem shows a screenshot with red numbered boxes, a "Where to see it" click path with a clickable link, one line on why it costs sales, and one line on what the agency will do. The client should understand the problems in two minutes and want to hire the agency to fix them.

Example: `docs/preview.png`, rendered from `examples/demo/report.json` (a fictional store).

## Before you start
- **Agency branding:** the builder looks for `~/.config/website-sales-audit/agency.json` (schema in `assets/agency.example.json`; a full real example is `examples/agency-webxlr8/`). If it doesn't exist, ask the user once for agency name, website, email, phone, city, accent colour, logos (one for light and one for dark backgrounds) and 2–4 credibility stats, then save the config there. Without it, reports say "Your Agency".
- Ask only what you can't infer: the client URL and, if unclear, the client's display name. Default the date to today.
- Make a report folder in the user's working directory, e.g. `<cwd>/<client-slug>-audit/`, with `img/` and `shots/` subfolders.
- Tools: Python 3 with `playwright`, `Pillow`, `pypdfium2` (`pip install playwright pillow pypdfium2`). Scripts use installed Chrome if present, otherwise Playwright's Chromium (`python3 -m playwright install chromium`). Run scripts by their full path inside this skill folder.
- Safety: test checkout only up to the payment step. Never type personal or payment details, never submit forms, never place orders. Adding a test item to the cart is fine.

## Workflow

### 1. Brand + recon
```bash
python3 scripts/brand.py https://client.com <report_dir>
```
This gives you the platform, fonts, colours, logo candidates (downloaded to `img/`), contact links, and on Shopify `products.json`.
- **Look at the downloaded logo.** If it's white-on-transparent or tiny, find a better one, e.g. the og image or a crop from a screenshot.
- Report font = the client's most-used real font family. Google font → `{"google": true}`. Otherwise use `css_url` pointing at a stylesheet with its @font-face, or fall back to a close Google font and say so.
- Cover photo = a strong product or lifestyle image from their site, saved as `img/cover_photo.jpg`.
- On Shopify, mine `products.json` for facts: product count, share permanently discounted, options (fabric/size/colour), empty `product_type`, title typos.

### 2. Crawl everything (desktop + mobile)
```bash
python3 scripts/crawl.py https://client.com <report_dir> --max 60
```
Run it in the background. It screenshots every page at 1440px and iPhone size and flags 404s, horizontal scroll, broken images, demo/placeholder text and missing H1. Meanwhile, explore interactions with Playwright or a browser: menus, mobile menu, search (real + nonsense term), quick view, wishlist, compare, filters, add to cart, cart drawer, checkout up to payment, sticky mobile bars, floating chat buttons, footer links.

### 3. Look at every page
Use `scripts/sheets.py` (`long` for one full page, `grid` for many page tops) and look at the sheets. Work through `references/checklist.md` section by section. Note candidate findings in `<report_dir>/findings.md`: what, where (URL + clicks), device, evidence.

### 4. Verify every finding
A wrong claim in front of a prospect loses the deal, so before anything goes in the report:
- Re-check text at full resolution. Thumbnails produce false typos.
- Re-shoot at viewport size anything that might be an animation or a full-page capture artefact.
- Measure instead of guessing (popup `scrollHeight` vs `clientHeight`, a viewer counter across 3 reloads, delivery times on every page).
- Drop anything you can't stand behind. See "Verification rules" in the checklist.

### 5. Capture annotated evidence
Write `<report_dir>/shots.json` (format in the `scripts/shoot.py` docstring), then:
```bash
python3 scripts/shoot.py <report_dir> <report_dir>/shots.json          # all shots
python3 scripts/shoot.py <report_dir> <report_dir>/shots.json pdp_top  # one shot
```
Marks draw numbered red boxes and highlight the exact words in yellow. Look at every PNG to confirm the boxes landed in the right place. For things mark.js can't reach (text inside images, overlays, "content is cut off here"), use `scripts/img.py`. Crop and compress into `img/` with `img.py --crop ... --width 1400` (mobile `--width 700`). Crop tight: the reader should spot the problem in two seconds.

### 6. Write report.json
Follow `references/report-json.md` (schema) and `references/writing-style.md` (voice). In short:
- Order: Urgent (`layout: "full"`, own page) → High → Medium (`"half"`, two per page). 12–20 problems is a good report.
- Each issue: `say` (what's wrong, 1–2 sentences), `where` (click path + example link), visuals, `why` (1 line), `fix` (1 line, outcome only, never how-to steps).
- `more`: up to ~10 "missing today → what it should be" growth items. `plan`: 4 weeks, Week 1 = urgent fixes. `why_fit`: 3 cards linking the agency's experience to this client's problems.
- Appendix only when a long list genuinely helps the client.

### 7. Build and QA
```bash
python3 scripts/build_report.py <report_dir>
```
Check all of these:
- `AGENCY CONFIG` points at the right file.
- `FONTS LOADED` includes the client font.
- `OVERFLOW` is `none`. If not, shrink that page's visuals (width / target_mm / tighter crop) and rebuild.
- Look at `_preview.png`, then render 2–3 dense pages larger (pypdfium2) and inspect them: boxes visible, nothing cropped, no half-empty pages.
- Don't add CSS `box-shadow`, `filter`, `backdrop-filter` or `background-clip:text`. Some PDF viewers (e.g. macOS Preview) render them as grey boxes.

### 8. Deliver
Share the PDF (send the file if a file-sending tool exists, otherwise give the path). In chat give: problem count by severity, the top urgent ones in a line each, anything assumed (contacts, font fallback), and anything checked and deliberately left out.

## Files
- `scripts/brand.py`: brand, platform and product feed extraction
- `scripts/crawl.py`: desktop + mobile full-page crawl with automatic checks
- `scripts/sheets.py`: contact sheets for reviewing screenshots
- `scripts/shoot.py` + `scripts/mark.js`: annotated evidence screenshots from a JSON spec
- `scripts/img.py`: crop, resize and annotate images (boxes, "cut off here" lines, labels)
- `scripts/build_report.py`: report.json + agency config → HTML → PDF, with overflow check and preview
- `assets/report.css`: document design (brand colours and fonts injected at build time)
- `assets/agency.example.json`: agency config template
- `examples/agency-webxlr8/`: a complete real agency config with logos
- `examples/demo/`: fictional demo store, report.json, screenshots and the built PDF
- `references/checklist.md`: what to inspect, plus verification rules
- `references/writing-style.md`: voice and rules for client-facing text
- `references/report-json.md`: report.json schema
