# Sources and limits

Read for profile maintenance, not every product task. Risk references are adapted from Agentic Harness v6.1; the candidate does not inherit a claim of superior model performance.

- [Idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/) and [Stripe keys](https://docs.stripe.com/api/idempotent_requests): confirm the actual provider contract and retention period.
- [Transactional outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html): does not guarantee universal exactly-once effects.
- [PostgreSQL isolation](https://www.postgresql.org/docs/18/transaction-iso.html): choose concurrency behavior for the actual database.
- [OWASP authorization](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html): enforce rights at authoritative boundaries.
- [Safe integers](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Number/isSafeInteger), [RFC 5545](https://www.rfc-editor.org/rfc/rfc5545): representation does not decide business rounding or local-time semantics.
- [GDPR](https://eur-lex.europa.eu/eli/reg/2016/679/oj), [German VAT law §14](https://www.gesetze-im-internet.de/ustg_1980/__14.html): relevant legal requirements need qualified confirmation; tests are not legal approval.

These are targeted engineering constraints, not a mandatory stack. Verify current provider/library/legal specifics in each real project.
