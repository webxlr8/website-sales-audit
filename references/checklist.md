# What to check (sales-focused website audit)

Work through every section. A finding only goes in the report if you saw it yourself, at full size, and can say exactly where it is.

## 1. Can people buy at all? (highest priority)
- Add a product to cart → open checkout → scroll to payment. Stop there; never enter details or place an order. Look for "can't accept payments", missing methods, errors.
- Shopify: `/policies/refund-policy`, `/policies/shipping-policy`, `/policies/terms-of-service`, `/policies/privacy-policy`. 404s matter, because payment gateways check them.
- Cart: free-shipping bar maths, totals, upsells, anything covering Checkout.
- Mobile sticky "Add to Cart" bars: truncated price or variant text, buttons hidden under floating chat/WhatsApp widgets.
- Quick view or quick add popups: is Add to Cart visible without scrolling inside the popup? Measure `scrollHeight` against `clientHeight` before claiming.

## 2. Template leftovers and wrong text
- Theme demo text: "clothing", "fashion", "$", "Lorem", "Your content", "Example product", "Tell your brand's story", blog intros from the demo.
- Shipping/returns tabs and delivery boxes on product pages: compare them with the FAQ and policy pages. Contradictions are a strong finding: list each page and what it says.
- Typos in the announcement bar, headings, product titles and search suggestions.
- Contact details: count distinct phone numbers, emails (Gmail vs domain) and WhatsApp numbers across header, footer, Contact page and floating buttons.

## 3. Trust
- Fake urgency: "X people viewing" (reload 3 times and record the numbers), "Only N left" on made-to-order items, countdowns that reset.
- Reviews: count them. "Be the first to write a review" everywhere = zero social proof.
- Testimonials, About and Showroom pages: empty pages or a title with no content.
- Permanent "sale" on most products (count from products.json: `compare_at_price` vs `price`).
- Old seasonal content (festival posts, expired sales) on the homepage.

## 4. Broken things
- Header icons (wishlist, account, compare), menu items, footer links: open every one. Record 404s and blank pages.
- Blog: do article titles link anywhere? Is `/blogs/news` (Shopify) empty or showing demo text?
- "Order tracking" pages that don't track.
- Search: try a real term and a nonsense term. Check suggestion quality.
- Forms: newsletter, contact (don't submit). Check that they exist and look right.

## 5. Layout and design (desktop 1440 and mobile 390)
- Hero/banner: text baked into images that gets cropped at some widths; mobile hero too tall (products not visible until the 3rd scroll).
- Floating buttons covering text or buttons on mobile.
- Horizontal scroll on mobile (crawl flags `HSCROLL`).
- Duplicate headings (page title repeated as the first heading), walls of tiny text, pages with no images.
- Category pages: filters present? Products per page, orphan last row, sort options.
- Product page: gallery size vs whitespace, dimensions shown, variant pickers (size/colour/material), instalments shown, delivery estimate.

## 6. Findability and measurement (keep short in the report)
- `<title>` and meta description on the homepage, empty H1, product titles stuffed with keywords.
- Speed: measure LCP in the browser (PerformanceObserver), request count, oversized hero images. PageSpeed API quota often fails; say so rather than guessing.
- Tracking: GA4 / Google Ads / Meta pixel tags in the source. Only say "not found in the theme"; it may be installed via an app.

## Verification rules (learned the hard way)
- Low-res thumbnails lie. A "typo" seen on a contact sheet can be correct at full size. Zoom in or open the full image before reporting text.
- Animations: a chart that looks empty in a full-page shot may animate on scroll. Re-shoot at viewport size after scrolling to it and waiting 3–5s.
- Full-page mobile captures can repeat the header or the whole page. Treat them as capture artefacts, not site bugs.
- Pages that look "empty" may be intentional landing pages (e.g. a "Trending" page made of banners). Leave them out unless they clearly look broken to a shopper.
- Describe precisely. "Add to Cart is hidden below the popup edge" (verified with measurements) beats "customers can't see Add to Cart".
- Don't publish what you can't stand behind. Drop a finding rather than overstate it.
