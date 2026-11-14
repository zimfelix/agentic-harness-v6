# Static website tools

`<skill>` and paths below refer to the website-tools directory (the parent of `references/`), not this Markdown file's directory. Run scripts with the PRODUCT ROOT as working directory. Read this guide, not every script; inspect source only when debugging/changing tooling.

## Choose the smallest useful procedure

- New/changed visible area: build via the project's actual build command, check relevant routes/sizes, inspect a screenshot and test interaction at the actual app boundary.
- Behavior-preserving Markup/CSS refactor: compare before/after screenshots and, where useful, computed styles for affected routes/states. Whole-site matrix for shared foundations/releases, not every edit.
- Preview: `node <skill>/tools/serve.mjs`; temporary local preview, not production hosting. Verify HTTP/current build before handing over a URL.

Configuration: `website.config.mjs` in the product root exports overrides. Defaults: source `src`, output `dist`, build `node scripts/build.mjs`, port 4173, widths 1440/390/320. Override for the actual stack rather than building a custom stack around these defaults. `ORDNER=path` serves a static draft without a build. `routen` declares the expected nonempty static-route set; without it separately compare discovery with the required routes. `bereit` is an optional JS readiness predicate; `warteMs` bounds waits.

Commands (substitute the actual skill path):

```sh
node <skill>/tools/pruefen.mjs
node <skill>/tools/screens.mjs /tmp/new-empty-screens
node <skill>/tools/screens.mjs --compare /tmp/before /tmp/after
node <skill>/tools/style-snapshot.mjs /tmp/current-styles.json
node <skill>/tools/style-snapshot.mjs --compare /tmp/before.json /tmp/current-styles.json
node <skill>/tools/device-preview.mjs
node <skill>/tools/seo-pruefen.mjs              # static SEO rules on the build, no browser
node <skill>/tools/seo-pruefen.mjs --livegang   # as if noindex were removed: what blocks go-live
node <skill>/tools/seo-pruefen.mjs --live       # after deploy: redirects, real 404, sitemap URLs (GET only)
```

SEO checker settings live under `seo` in `website.config.mjs`: `siteUrl` (production URL, one source for canonical, sitemap and `og:url`), `schraegstrich` (`'immer'` for `/leistung/`, `'nie'` for `/leistung`), `sonderseiten` (error/thank-you routes that may stay noindex), `platzhalter` (regex strings), `pflichtLinks` (e.g. imprint and privacy routes). It reads only generated HTML; content injected by JavaScript needs a browser check. Its rules and classes are explained in `references/seo.md`.

## Starter for a new static site

`<skill>/assets/starter/` is copied once at project start and then belongs to the project; the skill never updates it: `cp -Rn <skill>/assets/starter/. .` in the empty product root. Use it when no framework is chosen; an existing framework generates the same outputs itself.

```text
src/site.config.mjs ─┐  facts, page list, AI-crawler preset
src/seiten/*.mjs ────┼─▶ scripts/build.mjs [--produktion] ─▶ dist/: pages with head, canonical, OG, JSON-LD, breadcrumbs,
src/layout.mjs ──────┘   (generators: scripts/seo.mjs)            sitemap.xml, robots.txt, 404.html, fallback favicon
```

- Business facts, routes, titles, descriptions, H1, intent and proof (`beleg`) live only in `src/site.config.mjs`; layout, templates and CSS hold structure and design, which come from the brief and corrections. One more entry with `vorlage: 'leistung'` adds a service page; start page, 404 and the other service pages link it.
- `npm run build` is the preview: every page `noindex`, otherwise identical to production, so `seo-pruefen.mjs --livegang` on it shows the real go-live blockers. `npm run build:prod` drops `noindex` and fails on marked placeholders, missing intent or proof, an example `siteUrl` or missing image files.
- `npm test` runs the starter's own generator tests and works in CI without this skill (CI: `npm test && npm run build:prod`); `seo-pruefen.mjs` stays the independent audit before handover and go-live. A public preview additionally needs host protection (HTTP auth or `X-Robots-Tag: noindex`); the starter writes no host configuration.

Use an empty screenshot output directory. Comparisons require matching nonempty route/state sets; changed baselines need deliberate review. Style hashes are supplemental evidence, not a pixel/behavior proof. CSS helpers (`css-audit.mjs`, `unused-css.mjs`) identify candidates; don't delete selectors blindly.

Browser must be Brave: `BRAVE_PATH` may choose its executable; never silently substitute Chrome. A single Brave run does not establish Safari/mobile/screenreader compatibility. Failed navigation/readiness/build is failed evidence, not a screenshot success. Preview reports stale/failed builds as 503 and `/_geraete/stand` reports actuality; device preview assets are internal, not copied into production. LAN exposure and persistent macOS service installation require explicit approval.

Design inspiration is collected per project, never in this skill: read `references/inspiration.md` only when recording or using inspiration. No screenshots or image collection needs to be loaded for ordinary code work.
