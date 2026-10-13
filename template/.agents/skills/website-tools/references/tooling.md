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
```

Use an empty screenshot output directory. Comparisons require matching nonempty route/state sets; changed baselines need deliberate review. Style hashes are supplemental evidence, not a pixel/behavior proof. CSS helpers (`css-audit.mjs`, `unused-css.mjs`) identify candidates; don't delete selectors blindly.

Browser must be Brave: `BRAVE_PATH` may choose its executable; never silently substitute Chrome. A single Brave run does not establish Safari/mobile/screenreader compatibility. Failed navigation/readiness/build is failed evidence, not a screenshot success. Preview reports stale/failed builds as 503 and `/_geraete/stand` reports actuality; device preview assets are internal, not copied into production. LAN exposure and persistent macOS service installation require explicit approval.

Optional visual references: `assets/inspiration/README.md`, then only selected cards/images. They are examples of particular preferences, never a required style. No screenshots or image collection needs to be loaded for ordinary code work.
