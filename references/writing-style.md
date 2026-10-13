# Writing style for the client report

The reader is a business owner, not a developer. The document is a sales pitch: it shows them clearly what is wrong, proves it with screenshots, and makes the agency the obvious team to fix it.

## Rules
- **Short and plain.** One idea per sentence, about 20 words max. No jargon: say "the page that opens when you click the heart icon", not "`/pages/wishlist` returns 404". Put technical paths only inside links.
- **Always say where.** Every problem gets a "Where to see it" box with the click path (`Open any product → click Add to Cart → click Checkout`) and a clickable example link. The client must be able to reproduce it in 30 seconds.
- **Every problem has a screenshot.** Box the exact spot with a red numbered marker and highlight the exact words in yellow. If you can't screenshot it, use a "Where / What it says" table (e.g. contradicting delivery times).
- **Say what's wrong, not how to fix it.** "We'll fix:" states the outcome in one line ("Move the WhatsApp button and fix the bottom bar"). Never give Shopify admin paths or step-by-step instructions, because that hands the project away.
- **Business impact in one line.** "Why it costs sales": lost orders, lost trust, wasted ad money. No invented percentages or revenue numbers.
- **Honest numbers only.** Counts you measured ("166 of 166 product pages", "0 reviews", "4.8 s"). Quote the site's own words in quotes.
- **Severity:** Urgent = stops buying or creates legal risk (payments, false policies, fake urgency, blocked buy buttons). High = broken or empty features and contradictions. Medium = design, typos, polish. Usually 3–5 Urgent, then High, then Medium. 12–20 problems total is a good report.
- **Be respectful.** Lead the summary with what's good ("Your website looks good, but…"). Never mock the current agency or theme.
- **Legal mentions (optional, one clause, no lecture).** Only cite rules that apply where the client sells, and only if you're sure. Examples: India, CCPA Dark Patterns Guidelines 2023 and Consumer Protection (E-Commerce) Rules 2020. EU, Unfair Commercial Practices Directive (fake urgency, fake scarcity). UK, Consumer Protection from Unfair Trading Regulations / DMCC Act 2024. US, FTC Act Section 5 (deceptive practices). If unsure, leave it out.
- **Local context.** Use the client's currency, payment options (e.g. Razorpay/UPI and EMI in India, Klarna or Afterpay in the EU/US/AU, Stripe or PayPal elsewhere) and spelling.

## Example problem (half layout)
- Title: `Quick view popup is cut off`
- Say: `The Quick view popup is too short. Only half of it shows: the fabric choices and Add to Cart button are hidden below the edge.`
- Where: `Open Sofa → move the mouse over a product → click the eye icon`
- Problem: `Most shoppers never find Add to Cart in the popup.`
- We'll fix: `Resize the popup so everything, including Add to Cart, is visible.`
