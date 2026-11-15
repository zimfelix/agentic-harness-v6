# Page plan, proof and local search

**Responsibility:** decide which pages exist, which search intent each serves and what real client proof it carries: a short version before any draft, the full one before the finished site goes live; local search work outside the website. Read for a new site, new pages, service, location or product pages and local SEO. Technical rules: `seo.md`.

## Principle

One page per real search intent (Search Intent: what the searcher wants, e.g. „Baum fällen lassen“ ≠ „Baumpflege“), carrying proof only the client has. **No client facts, no indexable page:** drafts may use visibly marked placeholders (`noindex`), but an empty proof field blocks the page at go-live instead of being filled with generic text; `seo-pruefen.mjs --livegang` fails on placeholders. Subpages catch existing demand; they create none. Demand and prominence come from the client's reputation (business profile, reviews, mentions), which the site supports but cannot replace.

```text
client facts ──▶ search terms ──▶ ranking, intents ──▶ page plan (proof per page) ──▶ client review ──▶ design + build
     ▲                                              │ proof empty?
     └────────────── ask the client ◀───────────────┘ → placeholder in the draft; before go-live fill, merge or drop
```

## Steps

**Short version before a draft** (minutes, from the brief): steps 2 and 3, and title, H1 and link texts worded as in step 5; no client loop yet, gaps stay marked placeholders. **Full plan** for the finished site: all steps, proof per page, confirmed by the client before go-live.

1. **Collect client facts** (table below). Missing facts become questions, never invented text.
2. **Collect search terms cheaply:** the words end customers use for jobs and products (ask the client what callers say; trade terms such as „Fassadenbeschichtung“ are rarely typed), Google autocomplete and „People also ask“, competitors' page names, Keyword Planner ranges; after launch, Search Console queries. No invented search volumes.
3. **Rank the offers.** Compare the client's order with demand (search terms, frequent enquiries), business value and available proof. Where they disagree, say so with the reason and propose an order; the client decides. The ranking sets home order, navigation and build order; an offer without demand or proof becomes a section, not the lead.
4. **Group by intent.** Each main intent gets one page; two intents get two pages only if the client offers both as relevant services, otherwise a section. Several own pages ranking for one query are not a problem in themselves; near-duplicates are.
5. **Fill the page plan and word it:** title, H1, first sentence and link text carry the page's main search term in the customers' words; the trade term may follow in the text („Fassade streichen lassen“, then „Beschichtung mit Silikonharzfarbe“). Review ranking and wording with the client before the finished pages are built, adopt corrections and repeat until confirmed; after launch, revisit with Search Console queries. Record it in the project (e.g. `harness/docs/page-plan.md`).
6. **Link deliberately:** home → every main page; service ↔ related services, matching references and contact; references → their service; descriptive anchor text; breadcrumbs from depth 2.

Page plan template (copy into the project, fill there):

| Route | Type | Main intent (searcher's words) | Title | H1 | Proof from the client | Links in / out | CTA | Schema | Status |
|---|---|---|---|---|---|---|---|---|---|

## Location and variant pages

Google's spam policies name city or region pages that funnel users to one page as doorway abuse, and mass pages without added value (also AI-generated) as scaled content abuse. Before any location, variant or programmatic page, all three must be yes:

1. Is the page substantially its own when the place name is removed?
2. Does it carry at least three local facts from client data (jobs done there, reviews from there, travel time, local regulations or building stock)?
3. Does a local visitor find something here that the service page lacks?

Otherwise: no page; one service-area page listing the real area plus references that name their towns. Programmatic pages only when each page has its own real data (catalog, directory).

## Content that earns trust and citations

- **Service or product page:** what, for whom, process, price range or „ab“ prices, duration, area or delivery, own photos of real work, questions customers actually ask, contact.
- **About:** real people, qualifications (e.g. master craftsman, guild), photos, origin of products.
- **References/projects:** date, place, task, photos, customer consent; they carry place names naturally.
- **Entity description:** the company in one and in three sentences, consistent everywhere; quotable for search and AI answers.
- Never invent reviews, staff, projects, numbers or certifications. AI-written text is reviewed by a human before publishing.

## Local search outside the website (hand over to the client)

- **Google Business Profile** decides the map pack (Google: relevance, distance, prominence; not purchasable): exact primary category, services, real service area, hours, photos, regular updates. Business name without added keywords (guideline violation, risks suspension).
- **Same name, address and phone** everywhere: website, JSON-LD, business profile, Bing Places, Apple Business Connect, relevant directories and trade associations.
- **Reviews:** ask every customer, no incentives, no filtering of unhappy customers, no staff reviews. A site that shows reviews must say whether and how they are checked (DE § 5b Abs. 3 UWG; AT UWG annex 23b/c). Show external reviews as a static, dated excerpt with link rather than a third-party widget (consent, speed, not eligible for stars anyway).

## Client data

| Fact | Needed for | Without it |
|---|---|---|
| Services/products actually offered, with priority | one page each | no page |
| Real service or delivery area, locations with staff | area page, business profile | one area page only |
| Reference projects with photos, date, place, consent | references, local proof | no location pages |
| Prices or ranges | trust, non-commodity content | „Preis auf Anfrage“ |
| Qualifications, team names and photos | about page, entity data | leave empty, invent nothing |
| Real customer questions | FAQ section | no FAQ |
| Access to business profile, Search Console, Bing | monitoring, consistency | go-live without monitoring |
| Legal entity, register and chamber details | imprint, JSON-LD | no go-live |
