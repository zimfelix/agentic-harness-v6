# Fast drafts

**Responsibility:** the intake and procedure for a new website or a redesign: from a short brief to two or three distinct, checked first drafts. Read at the start of a website project or when design directions are to be explored. Sections and parameters: `sections.md`; pages and proof: `page-plan.md`.

## Intake

One message, at most seven questions; anything unanswered becomes a default recorded as an assumption in PROJECT.

1. Business, place and the **main action** of a visitor: call, enquiry, visit, order or booking.
2. Services or products in the order the client wants them, with prices or ranges, and for each how often it is asked for and how much it matters to the business.
3. Audience, form of address (Sie/du), language and region (e.g. de-DE, de-AT).
4. Existing material: logo, colours, fonts, own photos and videos (quality, rights), references, team photos.
5. Must-show facts: hours, area served, address and parking, shop or booking link; who delivers contact messages.
6. Taste: two or three sites liked or disliked and why, or a position on four axes — warm–cool, calm–lively, traditional–contemporary, airy–dense.
7. Deadline, domain, hosting or shop platform; who approves texts, images and publication.

**Defaults:** Sie, de-DE; size per `sections.md` (a landing page unless several offers need their own pages); `noindex` until go-live; WCAG 2.2 AA; self-hosted fonts; motion tier 0–1; no third-party embeds; visibly marked placeholders; one main CTA above the fold and phone or contact reachable on mobile.

## Procedure

```text
intake ─▶ page plan (page-plan.md): offers ranked, search terms in customers' words, proof per page
          the client confirms ranking and wording
       ─▶ 2–3 directions in text: one-sentence idea + axis values, ≥ 3 axes different
          colours from the client's material (logo, product, place, photos), never from earlier projects
       ─▶ client picks one or more ─▶ per direction one static draft in entwuerfe/<name>/
          first screen + 2–3 key sections + footer, real content; order, H1 and headings from the page plan
       ─▶ checks: ORDNER=entwuerfe pruefen.mjs · screenshots 1440/390 · contrast on real images
       ─▶ present side by side ─▶ STOP for the client's choice
       ─▶ the chosen draft becomes the base and keeps its design; the others go to the project archive
```

**Axes** that make drafts differ without taste rules (record per draft as a short direction card): type class (serif, grotesque, humanist, slab; one or two families) · colour source (brand, photo, product, neutral plus accent, dark) · density · hero media · shape language (sharp, soft, mixed) · image treatment (full-bleed, framed, cut-out, none) · motion tier · surface rhythm (one surface, light–dark alternation).

Drafts share only content and measuring tools, never components or styles; merge into shared components only after the choice. Drafts stay internal and `noindex`. Liked references from the client go to the project's inspiration collection (`inspiration.md`), never into this skill.

## Speed with quality

Real content first, the section catalog for structure, the baseline hard checks of `pruefen.mjs`, measured contrast on the real image and one review at 390 px width. From the chosen draft on, build with the project's site data as the single source (a static site without a framework: the starter in `tooling.md`) and run `seo-pruefen.mjs` before every handover. When the brief already fixes one direction, e.g. a single landing page from one prompt, skip the direction step (not the page plan) and draft directly in the starter: its preview is `noindex` and may carry marked placeholders.
