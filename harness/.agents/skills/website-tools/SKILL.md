---
name: website-tools
description: Plan, build and review websites — fast design drafts, section catalog, SEO by design (page plan per search intent, titles, headings, canonical, sitemap.xml, robots.txt, structured data/JSON-LD, local SEO, AI-search crawlers, go-live), content, responsive usability, web-app security/operations basics and release gates — with optional static-build SEO and Brave-based layout checks, screenshots and local preview. Use for websites and small web apps with login, forms or a backend; not a complete dynamic SPA/auth/CRM test suite.
compatibility: Optional bundled scripts require Node.js 22.19+; browser-based ones also Brave; persistent preview service requires macOS. No npm packages.
---

# Website work

Use for an actual website; a business API does not automatically need website machinery.

Record the chosen visual direction, real content/contact routes, rights and target devices in PROJECT or a focused design doc. References express taste, not universal requirements. Never invent testimonials, figures, certifications or legal details; a form without working delivery says so.

For a new site, a redesign or design directions, read `references/drafts.md`; for sections, hero media, shop modes and media budgets, read `references/sections.md`; for components, consistency, optional style patterns (e.g. contact revealed by click), design corrections and the consistency audit, read `references/design.md`.

Baseline for every page: header, footer and repeated blocks come from one source; shared components/tokens for known shared roles, following the chosen framework's layout; licensed fonts verified as actually loaded; visible focus; navigation operable by keyboard and touch; anchors land below a sticky header; hover effects only under `(hover: hover)` and nothing reachable only by hover; touch targets at least 24 × 24 px; form fields at least 16 px on touch devices; no motion under `prefers-reduced-motion: reduce` and a pause control for anything moving on its own for more than 5 s. Verify responsive layout and contrast. Inspect the changed page/state in the real browser; a narrow viewport alone does not prove touch interaction.

Plan search visibility before building: a short page plan before any draft, the full one with client proof before go-live; one page per real search intent; drafts may use marked placeholders, indexable pages may not. For new pages, service, location or product pages and local search, read `references/page-plan.md`. For head tags, routes, redirects, sitemap, robots, structured data, AI crawlers or go-live, read `references/seo.md` and check the build with `tools/seo-pruefen.mjs`. A new static site without a chosen framework starts from `assets/starter/`: one site config generates these parts (setup in `references/tooling.md`).

For reusable static-site checks/screenshots/preview, read `references/tooling.md` only when using or setting up those tools. Browser-based scripts need Brave; none replaces dynamic application/authentication tests. Use existing equivalent framework tools instead when they fit better. No mandatory custom build system.

For server code, login, stored or sent form data or user content, read `references/web-app.md` before building or changing those parts.

Before publication, confirm actual content/legal/assets approvals, contact delivery, host/domain, the go-live list in `references/seo.md` and the agreed compatibility checks. Keep incomplete production gates visible; don't impose a full release audit on every small visual iteration.
