# SEO by design

**Responsibility:** technical and on-page search rules for websites, the go-live list and outdated advice not to reintroduce. Read for head tags, routes, redirects, sitemap, robots, structured data, AI crawlers, a second language or go-live. Which pages exist and what each must prove: `page-plan.md`. Values (site URL, business data, page plan) live in the project, never here. Sources: Google Search Central unless noted; checked 2026-11.

## What a rule can achieve

```text
crawl ──▶ index ──▶ rank ──▶ snippet/click ──▶ AI citation ──▶ enquiry
└─ technique: guaranteed ─┘   └ content + reputation ┘  └ presentation ┘   └ trust ┘
```

Confirmed ranking inputs are relevance/helpfulness, spam-policy compliance and, weakly, Core Web Vitals. Most technical rules are eligibility (crawl, index) or presentation (snippet). Off-site signals (business profile, reviews, mentions) decide local and AI visibility to a large part. Never promise rankings, positions or AI mentions.

Classes say how `tools/seo-pruefen.mjs` treats a rule: **H** fails the check · **W** warns · **J** cannot be checked by the tool; agent or client judge. *House rule* marks a consistency default that Google recommends but does not require. A passing check is not compliance with the J rules.

## Crawl and index

- **H** Every indexable page is reachable by `<a href>` links from `/` (no orphans); internal links and fragments resolve. **W** more than three clicks deep; links not in the canonical URL form.
- **J** All indexable text and navigation are in the delivered HTML; JavaScript only enhances. Many AI crawlers execute no JavaScript, and Google may skip rendering for non-200 responses. The tool reads generated HTML only and cannot see what scripts add.
- **H** One production URL (`seo.siteUrl`) feeds canonical, sitemap and `og:url`; exactly one `<link rel="canonical">` in `<head>`, absolute, https, self-referencing, in the project's slash form (`seo.schraegstrich`). **J** JSON-LD `@id`s use the same URL.
- **H** (`--live`) http, the other host form and the other slash form redirect permanently (301/308) to it; temporary redirects (302/307) are not used as a canonical signal. **W** `/index.html` answering 200 (canonical covers it) or redirect chains.
- **H** `noindex` via meta robots or `X-Robots-Tag`, never combined with a robots.txt `Disallow` for the same URL (the crawler never sees it). Google also honours robots meta in `<body>`; generate it in `<head>`.
- **H** (`--live`) The production home page and sitemap URLs are not `noindex`; robots.txt neither blocks `/` for Google nor answers 5xx/429 (Google then treats the site as blocked).
- **J** Preview/prototype is protected per environment (HTTP auth or `X-Robots-Tag: noindex`); production output inherits no preview `noindex`. Error and thank-you pages may stay `noindex` (`seo.sonderseiten`).
- **H** *House rule:* `sitemap.xml` exists and lists exactly the canonical indexable pages. **W** identical `lastmod` everywhere (use real content dates or omit), `priority`/`changefreq` (ignored); the ping endpoint is gone.
- **H** *House rule:* `robots.txt` exists with a `Sitemap:` line. **W** rules that block CSS, JS or images; `noindex` or `crawl-delay` lines (unsupported by Google).
- **H** (`--live`) Unknown URLs return a real 404, not a soft 404. **J** The error page speaks the site language and links onward.

## On the page

- **J** Search terms count only in visible content: title, H1 and headings, body text, link text, image alt text, URL. The meta keywords tag is not used; hidden text and keyword stuffing are spam. Write the way customers speak; Google understands inflections and synonyms, so no repetition is needed.
- **H** Each indexable page has exactly one non-empty `<title>`, unique across the site and not just „Startseite“/„Home“; *house rule:* a meta description. **J** Title names the page topic first, brand last, no stale year. **W** Title over about 60 or description outside about 50–160 characters: pixel heuristics, Google sets no limit, may rewrite and builds snippets mainly from page content.
- **W** Not exactly one H1 (house rule; Google requires no heading count). Generic link text („hier“, „mehr“). URLs with capitals or underscores. **J** Short, stable URLs grouped in folders by topic.
- **H** `<html lang>`, `meta viewport`, `alt` on every image (empty for decoration). **W** `width`/`height` missing, the first content image lazy-loaded (LCP), more than one `fetchpriority="high"`. **J** AVIF/WebP with `srcset`.
- **H** *House rule:* favicon linked from the home page and present. **W** No file in a format Google lists (ICO, PNG, GIF, JPEG, BMP; not SVG, WebP or AVIF) or under 48 × 48 px; square required.
- **H** `og:url` equals the canonical when present. **W** Missing `og:title`, `og:description`, `og:image`, `og:url`.

## Structured data

- **H** JSON-LD parses. LocalBusiness and its subtypes have `name` and `address`; `dayOfWeek` uses English schema.org days; no `aggregateRating`/`review` about the own business (self-serving, not eligible). The phone in JSON-LD appears visibly on the site (**W** for the street).
- **J** Markup states only what pages visibly say and comes from the same project data as imprint and footer. No embedded review widgets for stars (also self-serving).
- Use Organization or the most specific LocalBusiness subtype (phone international, **W** otherwise), WebSite (site name) and BreadcrumbList (rich result desktop only since 2025-01). Event, JobPosting, Product/Offer or VideoObject only when they really exist.
- **W** FAQPage or HowTo markup: no rich result any more (FAQ ended 2026-05-07). FAQ content with real questions stays useful.
- **J** Rich Results Test by hand after deploy (no official API). Markup has no documented ranking bonus; it aids understanding and display.

## Speed, privacy and law (DACH)

- **J** Field targets for Core Web Vitals: LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1. Lab scores (Lighthouse) are not field data; relevance comes first. Video and image-sequence budgets: `sections.md`.
- **H** Fonts self-hosted: no Google Fonts via link, script, `@import` or `url()` (JavaScript-added fonts need a browser check). No http subresources. **W** Third-party embeds found: load only after consent when they transfer data (DE § 25 TDDDG, AT § 165 Abs. 3 TKG 2021). Verify Search Console by DNS, which needs no script.
- **H** *with `seo.pflichtLinks`:* imprint and privacy linked from every page. **J** Imprint as plain HTML, never revealed by click (DE § 5 DDG; AT § 5 ECG plus Offenlegung § 25 MedienG).
- **J** Prices to consumers are final prices including VAT (DE PAngV, AT PrAG), also for „ab“ prices; a small business exempt from VAT says so. Photos or videos generated or altered by AI that look real are labelled as such and never presented as the client's real work or team (transparency rules of the EU AI Act; check the current state).

## AI search

- Google AI Overviews and AI Mode use the normal index: no extra requirements, no special schema, no `llms.txt` (Google ignores it). The guide's core is non-commodity content: own experience, facts and proof.
- **J** robots.txt AI policy is a client decision. Preset A: allow all. Preset B, search yes and training no: allow `OAI-SearchBot`, `Claude-SearchBot`, `PerplexityBot`; disallow `GPTBot`, `ClaudeBot`, `Applebot-Extended`, `CCBot`, `Google-Extended` (also ends Gemini app grounding, not Search). Search Console's generative-AI setting removes a site from AI Overviews/AI Mode; it does not control training. Check that CDN/WAF bot blocking (e.g. Cloudflare defaults) does not override the decision.
- Never: LLM-only or hidden text, mass „AI pages“, paid llms.txt services, AI visibility guarantees.

## Second language (only when needed)

- **H** `hreflang` reciprocal, self-referencing, valid codes, targets in the build. **J** `lang` per page; separate `de-DE`/`de-AT` only when content really differs.

## Go-live

1. `node <skill>/tools/seo-pruefen.mjs --livegang` without hard failures (it treats remaining `noindex` as information); J questions answered.
2. Build for production without `noindex`, deploy, then `--live`.
3. Search Console as domain property (DNS), submit the sitemap; Bing Webmaster Tools (import from Search Console; Bing feeds Copilot and other AI search); IndexNow optional (not used by Google).
4. Rich Results Test for home and one service page; business profile links to the site with identical name, address and phone (`page-plan.md`).
5. Afterwards monthly: Search Console indexing and queries per page; pages whose titles Google rewrites or that stay unindexed are content questions first.

## Outdated — don't reintroduce

| Claim | Status |
|---|---|
| FAQ/HowTo markup earns extra space | HowTo removed 2023, FAQ ended 2026-05-07 |
| `llms.txt` improves AI visibility | Google ignores it; almost never fetched |
| Google limits titles to 60 / descriptions to 155 characters | no limit; truncation by pixel width |
| One keyword per page, cannibalisation panic | one main intent per page |
| City pages need X % unique text or 300 words | folklore; usefulness and doorway patterns count |
| Meta keywords, `priority`/`changefreq`, sitemap ping | ignored or removed |
| E-E-A-T is a ranking factor | a rater framework; trust matters, no score |
| Own star ratings via markup or widget | not eligible (self-serving) |
| FID as Core Web Vital | replaced by INP 2024-03-12 |
| Schema markup or statistics sprinkling boosts AI citations | no controlled evidence |
| Dynamic rendering | deprecated workaround (2024) |
| Lighthouse 100 = SEO success | lab test, not ranking |
