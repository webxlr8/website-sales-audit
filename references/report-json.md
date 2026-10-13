# report.json schema

`scripts/build_report.py <report_dir>` reads `<report_dir>/report.json`. All image paths are relative to `<report_dir>` (usually `img/...`). A full working example is `examples/demo/report.json` (a fictional store); `docs/preview.png` shows what it renders to.

Text fields accept small HTML: `<b>`, `<a href>`, `<br>`, `<em>`, `<ul><li>`. Inside "where" use `<span class="path">Open X <i>→</i> click <b>Y</b></span>` for click paths.

## Top level

| Key | Required | Notes |
|---|---|---|
| `client` | yes | see below |
| `date` | yes | "12 October 2026" |
| `subtitle` | yes | 1–2 plain sentences under the cover headline |
| `title_html` | no | default `Why the website<br>isn't <em>selling</em>,<br>and how we'll fix it.` |
| `issues` | yes | list, in priority order (Urgent → High → Medium) |
| `summary` | no | `{title, lead, stats:[{n,label,style: dark|amber|blue}]}`. Defaults count issues by severity. |
| `more` | no | "What else will bring more sales" page: `{title, lead, items:[{what, today, do}]}`. Max ~10 items. |
| `plan` | no | `{title, lead, weeks:[{label, title, items[]}], closing:{title, text}}`. 4 weeks. |
| `method` | no | one sentence: how we checked. Printed under the plan. |
| `why_fit` | no | 3 cards on the "Why us" page `[{k, title, text}]`. Tailor to this client (e.g. "Fixes problem 1"). Defaults come from the agency config `default_fit`. |
| `include_why` | no | default true |
| `appendix` | no | `{title, intro, groups:[{name, items:[{title, url}]}], first_page:38, per_page:48}`. Only when a list genuinely helps the client (e.g. every affected URL). |
| `back` | no | `{title_html, text}` for the dark back cover |
| `pdf_name` | no | default `<agency-slug>-<client-slug>-website-audit.pdf` |

## client

```json
{
  "name": "Oakline Home",
  "legal": "Oakline Home Ltd, Portland",
  "site": "oaklinehome.example",
  "url": "https://oaklinehome.example",
  "logo": "img/client_logo0.png",
  "cover_photo": "img/cover_photo.jpg",
  "font": {"family": "Lora", "google": true}
}
```

`font` options: `{"family": "X", "google": true}` (Google Fonts), `{"family": "X", "css_url": "https://..."}` (any stylesheet with @font-face), or `{"family": "X", "face_css": "@font-face{...}"}`. The builder prints `FONTS LOADED:`; if the client font isn't listed, the PDF silently used a fallback, so fix it.

## issue

```json
{
  "n": 4, "severity": "Urgent|High|Medium", "area": "Buy buttons",
  "layout": "full|half",          // full = own page (use for Urgent); half = two per page (default)
  "title": "WhatsApp button covers \"Add to Cart\"",
  "where_short": "Product page, mobile",   // summary table column
  "say": "One or two plain sentences: what is wrong.",
  "where": "Click path + clickable example URL (see above)",
  "visuals": [ ... ],
  "why": "One line: why it costs sales.",
  "fix": "One line: what the agency will do (outcome, not how-to).",
  "target_mm": 58                  // optional: image height target (half default 58, full 78)
}
```

Half-layout issues are paired in order, so put two half issues next to each other. A full issue between them forces the first one onto its own page.

## visuals (rendered in order)

| type | fields | use for |
|---|---|---|
| `frame` | `img, url, caption?, width?("70%"), full?` | desktop screenshot in a browser frame. Width auto-sized from aspect ratio unless given. |
| `phones` | `items:[{img, caption?}], note?, width_mm?` | 1–3 mobile screenshots in phone frames, side by side |
| `phone_frame` | `phone_img, frame_img, url, phone_mm?(24), frame_mm?(112), caption?` | mobile + desktop of the same issue |
| `grid` | `items:[{img,url}], caption?` | two desktop shots side by side |
| `table` | `head[], rows[[...]]` | "Your website says / The truth", or "Where / What it says" |
| `callouts` | `items[]` | numbered list matching the red numbers in a screenshot |
| `note` | `title, html` | grey box for a related finding (e.g. policy pages) |
| `html` | `html` | escape hatch |

## Fitting pages

The builder prints `OVERFLOW (page, pt into footer)`. For any page listed: shrink `width` on the biggest frame, lower `target_mm`, crop the screenshot tighter with `img.py`, or shorten `say`. Then rebuild. Never ship with overflow.

## Agency config (`~/.config/website-sales-audit/agency.json`)

```json
{
  "name": "Your Agency", "website": "youragency.com", "email": "hello@youragency.com",
  "phone": "+1 555 0100", "office": "City, Country", "tagline": "Websites that sell.",
  "about": "One or two sentences about the agency (Why-us page).",
  "colors": {"accent": "#4f46e5", "accent_2": "#4338ca", "accent_3": "#818cf8", "accent_ink": "#4338ca", "dark": "#0f172a"},
  "logo_on_light": "logo-dark.png", "logo_on_dark": "logo-white.png", "icon": "icon.png",
  "stats": [{"n": "100+", "label": "brands served"}],
  "default_fit": [{"k": "Online stores", "title": "Store builds", "text": "..."}],
  "client_logos": ["clients/brand-a.png"]
}
```
Paths are relative to the config file. Everything except `name` is optional. Missing logos fall back to a text wordmark, and missing stats or client logos hide those blocks. `accent_2` and `accent_3` are the gradient stops on the cover stripe. Only list client logos you're allowed to show. Lookup order: `--agency <file>`, `$WSA_AGENCY`, `<report_dir>/agency.json`, `~/.config/website-sales-audit/agency.json`, `assets/agency.example.json`.
