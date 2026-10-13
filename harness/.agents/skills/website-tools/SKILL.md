---
name: website-tools
description: Plan and review website content, responsive usability and release gates, with optional Brave-based static-build screenshots, checks and local preview. Use for website work, not as a complete dynamic SPA/auth/CRM test suite.
compatibility: Optional bundled scripts require Node.js 22.19+ and Brave; persistent preview service requires macOS. No npm packages.
---

# Website work

Use for an actual website; a business API does not automatically need website machinery.

Record the chosen visual direction, real content/contact routes, rights and target devices in PROJECT or a focused design doc. References express taste, not universal requirements. No invented testimonials, legal claims or working form delivery.

Use shared components/tokens for known shared roles; follow the chosen framework's layout. Verify navigation, focus, responsive layout, contrast and meaningful touch targets. Inspect the changed page/state in the real browser; a narrow viewport alone does not prove touch interaction.

For reusable static-site checks/screenshots/preview, read `references/tooling.md` only when using or setting up those tools. Its scripts need Node.js and Brave and do NOT replace dynamic application/authentication tests. Use existing equivalent framework tools instead when they fit better. No mandatory custom build system.

Before publication, confirm actual content/legal/assets approvals, contact delivery, host/domain/indexing and the agreed compatibility checks. Keep incomplete production gates visible; don't impose a full release audit on every small visual iteration.
