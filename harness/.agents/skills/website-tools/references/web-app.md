# Web applications

**Responsibility:** security and operations basics once a site has server code, login, stored or sent form data, or user content. Read before building or changing those parts; a static brochure site does not need it. Roles, tenants, permissions and audit live in the `business-software` skill (`references/rechte-und-nachvollziehbarkeit.md`); don't repeat them here or in the project.

## Boundaries to protect

- **Output:** render through the framework's escaping templates; no raw HTML from users, mails or CMS fields without a sanitizer. Set a Content-Security-Policy where the stack allows it.
- **Input:** validate on the server against an explicit shape and size limit; client checks are convenience only. Parameterised queries or the ORM; no SQL, shell or file paths built from request strings.
- **Sessions and login:** use the framework session or an established auth library, no own password hashing or crypto. Cookies `HttpOnly`, `Secure`, `SameSite`; CSRF protection for cookie-authenticated state changes; rate-limit login and public forms. HTTPS only.
- **Secrets and configuration:** environment variables or the host's secret store; `.env` ignored by git, a committed `.env.example` without values. Never in client bundles, logs, error pages or the repository. Separate development and production values.
- **Dependencies:** commit the lockfile; add a package only for a real need. Run the ecosystem's audit (e.g. `npm audit`, `pip-audit`) after adding packages and before a release; treat major upgrades as a change with its own check.
- **Deployment:** record environments, host, deploy and rollback steps and where logs are, in `PROJECT.md` or one focused operations doc. Back up before a production migration; migrations move forward. No deploy or production data change without explicit authorization.

## Checks

Test at the HTTP boundary with synthetic data: anonymous and wrong-user access, missing CSRF token, invalid and oversized input, and a `<script>` payload that must come back escaped. Check cookie flags and security headers on the real build or staging, not only in development mode. These checks do not replace a penetration test; don't call the application "secure" because they pass.
