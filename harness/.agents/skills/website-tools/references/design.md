# Design guardrails

**Responsibility:** consistency rules every design keeps, optional patterns to propose, how to work through design corrections and the consistency audit. Read when building or changing layout, components, styles or interaction. The look itself comes from the brief, the chosen direction and the client's corrections; this file prescribes none. Accessibility baseline: `SKILL.md`; sections and media: `sections.md`.

## Consistency (every design)

- One component with variants per recurring role (hero, section head, card, steps, FAQ, contact block); extract it at the second occurrence, not in a later refactor.
- Tokens for colour roles (background, text, muted, line, accent, light and dark surface, text on dark), one type scale and one spacing scale; no one-off value for a role that exists. Font sizes in `rem`, so a larger browser default works; fixed px only for lines, borders and icons. Capitals via CSS, not typed.
- The same action has the same label and button form everywhere. Link text names what happens or where it leads („Fassade streichen lassen“, „E-Mail schreiben“); arrows and symbols don't count as text.
- Width decides layout (breakpoints where the content needs them, a maximum content width); input mode decides behaviour (`hover`, `pointer`) and is never inferred from width.

## Optional patterns (propose, the client picks)

| Pattern | Fits when | Limit |
|---|---|---|
| One corner language, sharp or rounded | always worth deciding once | the whole site |
| Arrows: ↗ another page, ↓ same page | links carry arrows | decided by source and target page, not by the component |
| Fixed light–dark rhythm per section type | several surfaces | the same rhythm on every page |
| Heading emphasis by colour only | expressive headings | no italics or second font for emphasis |
| Sticky mobile action bar (call, enquiry) | the main action is a call or enquiry | covers no content or footer at the end of the page |
| Contact revealed by click (against simple scrapers) | secondary routes such as e-mail | imprint stays plain text (DE § 5 DDG, AT § 5 ECG); the main action and the phone from the JSON-LD stay visible links; a working fallback without JavaScript; headless scrapers click too |

Record chosen patterns in the project's design doc; unchosen ones don't apply.

## Working through design corrections

- Change only what was asked; offer further findings as a list.
- „Like before, only …“: restore the previous state exactly, then apply only the named change.
- After each round, say what is visibly different, with a screenshot or measured value.
- Secure a confirmed decision so it isn't lost: as a token or a measured check; in the design doc only when it is a rule for several places.

## Consistency audit

After cross-cutting changes and before handover: header, footer and repeated blocks identical on all routes · fonts actually loaded, headings on the scale · no horizontal overflow at 1440/390/320 · agreed alignments measured (about 2 px tolerance) and chosen patterns kept · buttons and links follow their components, link texts descriptive · internal links and anchors resolve (`seo-pruefen.mjs`) · no unused selectors (`css-audit.mjs`) or unlinked pages. Go-live list: `seo.md`.
