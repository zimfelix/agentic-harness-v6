# Sections and parameters

**Responsibility:** a project-neutral catalog of page sections with their parameters, the search and cost consequence of each choice, and limits for heavy media. Read when planning a page, a draft direction or a new section. It removes structural decisions so drafting time goes into the design direction; it prescribes no texts, colours or layouts. Every section is optional unless the page plan needs it.

## Intake parameters and their consequences

| Parameter | Options | Consequence |
|---|---|---|
| Business type | service · products/shop · both | page types and structured-data types (`seo.md`) |
| Local scope | one location · service area · delivery region · remote | address data, area page, business profile (`page-plan.md`) |
| Size | landing page · landing page + service pages · multi-page site | one page covers one main intent plus region; each further important offer needs its own page to be found |
| Hero media | none (type-led) · photo · split text + image · video loop · video once · scroll sequence · illustration | weight and LCP, pause and reduced-motion duties (limits below) |
| Featured items | 0 · 2–3 products or projects | only items with their own URL can rank; real items only, otherwise omit |
| Shop mode | contact order · external shop link · embedded widget · own product pages | external: rankings go to the platform; widget: products not crawlable on the own domain; own pages: each needs unique text, Product/Offer data, prices incl. VAT, terms, withdrawal and shipping information (legal review) |
| Proof | reviews · qualifications · memberships · press · references | real and dated only; no self-written review markup; reference pages are indexable |
| Contact | phone · form · e-mail · booking link · messenger link | a form states honestly what happens on submit; an external booking link moves conversions off-site |
| Motion tier | 0 none · 1 CSS only · 2 JS per page · 3 avoid | tier 2 needs a JS budget; content always stays in the HTML |
| AI-generated media | none · labelled | realistic AI photos/videos are labelled and never shown as real work or team (`seo.md`) |

## Home skeleton (default)

A starting point for local businesses, not a requirement: ● usually present · ○ optional · ◐ usual for local businesses. The brief or the direction may drop, merge or reorder any block.

```text
● header        4–6 links, phone or main CTA; one source for all pages
● hero          H1 = offer + place, main CTA, phone as second route, media per parameter
○ fact strip    3–4 hard, true facts (years, area, qualification, delivery)
● offer         service cards → service pages, or 1–3 lead products with prices → product pages
● proof         dated reviews with source and check notice, references, qualifications
○ process       3–5 real steps
● story/people  real names and photos; the strongest trust signal of small businesses
◐ area/location area list or address, hours, directions; map as link or click-to-load
○ prices · FAQ (5–12 real questions, <details>) · gallery · seasonal (only if maintained)
● contact       one sentence, main CTA, second route, hours
● footer        name, address, phone, legal links, consent settings
```

Recipes: craftsman — hero, services, references, process, area, about, prices, FAQ, contact. Producer/shop — hero, featured products, origin story, where to buy or shop, seasonal, contact. Small agency — hero, services, work, process, team, contact.

## Sections

| Section | Parameters | Constraints |
|---|---|---|
| Header | items ≤ 6 · services submenu (only with ≥ 2 services) · CTA · sticky · mobile drawer/overlay | keyboard and tap operable; anchors land below a sticky header (`scroll-margin-top`) |
| Hero | media (see intake) · proof strip below | the H1 stays real text in the HTML; contrast checked on the actual image or video frame |
| Offer overview | 3–6 items · cards/rows/list · „ab“ prices | one page per real intent (`page-plan.md`) |
| Featured items | 2–3 · products or projects · link to all | real items with their own pages |
| References | grid/gallery/before–after · filter only from about 8 items | date, place, customer consent |
| About/team | owner portrait · team · origin story | real people and qualifications |
| Area/location | list of places · address, hours, directions | map embeds only after consent |
| Prices | ranges · „ab“ · on request | consumer prices incl. VAT |
| Contact block | heading, one sentence, CTA, second route · form yes/no | no form that only pretends to send |
| Legal pages, 404 | — | plain HTML; 404 with status 404 and onward links |

## Heavy media limits

These are starting budgets for mid-range phones, not proven thresholds; record deviations in the project.

- **Photo hero** (when strong, licensed, high-resolution photos exist): responsive sources sized for the real display, a scrim only where text contrast needs it, and check cropping across viewports.
- **Video hero:** ≤ 2.5 MB desktop and ≤ 1 MB in a separate portrait mobile file, 6–12 s, no audio, `muted playsinline`; poster ≤ 100 KB and preloaded, so poster or H1 is the LCP element; one playback mechanism, never a second download of the same file; save-data and reduced motion show the poster only.
- **Scroll sequence** (frames or video scrubbed on scroll): motion tier 2. At most about 120–180 frames of ≤ 40 KB (mobile ≤ 25 KB); key frames first, the rest only when the section approaches, never the whole sequence for idle visitors. Pinned length ≤ 300–400 svh with a way to skip; chapter text in the HTML and shown as normal sections without JavaScript or under reduced motion. Lab scores hide this cost because a canvas is not the LCP element: measure transferred bytes.
- **Anything moving on its own for more than 5 s** (loop video, marquee, carousel) has a visible pause control (WCAG 2.2.2).
