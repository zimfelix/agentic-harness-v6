# Herleitung und Pflege des Business-Profils

**Gilt bei:** Änderungen/Prüfung dieses Profils, nicht bei jeder Produktaufgabe. **Zuständigkeit:** Herkunft, Evidenz und Grenzen der Regeln. Technischer Abgleich am 2026-10-09; konkrete Projekt-/Provider-/Rechtsversionen erneut prüfen. DSGVO hier als maßgebliche Rechtsquelle verlinkt, nicht neu textuell verifiziert (Abruf lieferte keinen Inhalt).

Das Profil entstand zunächst als Harness-eigener Entwurf, nicht aus einem erprobten CRM-Standard. Die Präzisierung stützt sich auf folgende Quellen plus lokale Beobachtungen (Init-Regelverstoß, unvollständige Prüfnachweise). Technische Quellen begründen gezielte Fehlerschutzmaßnahmen; sie rechtfertigen keinen universellen Stack oder jede Pflicht für jedes Projekt.

| Thema | Quelle / übertragbarer Inhalt | Grenze |
|---|---|---|
| Explizite Vorgaben/Belege | [David Tielkes Toolkit, geprüfter Commit](https://github.com/DavidTielke/Traning-KIT-AI-for-Developers/tree/6bcb3bdc4e3017d59d4d58851742af47a70023ac): Requirements, Devdocs, UI-Tests, NDepend-Regeln | People-Manager-/C#-/UI-/Markenvorgaben nicht pauschal übernommen; keine ausgeführte Gesamtanwendung |
| Kontext und autonome Fortsetzung | [Anthropic Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents), [Long-running Harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) | Praxisempfehlungen/Web-App-Demo, kein Beweis für unsere Agentenbefolgung |
| Wiederholung/Vorgangsidentität | [AWS idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/), [Stripe](https://docs.stripe.com/api/idempotent_requests) | Providersemantik/Keylebensdauer prüfen; nicht auf SMTP übertragen |
| Lokale Mutation + Nachricht | [AWS Transactional Outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html) | Mögliche doppelte Nachrichten; weder Brokerpflicht noch Exactly-once-Ende-zu-Ende-Garantie |
| Konkurrierende Datenänderung | [PostgreSQL Transaction Isolation](https://www.postgresql.org/docs/18/transaction-iso.html) | Andere Datenbankarten haben andere Garantien; Strategie projektbezogen |
| Identität/Zugriff | [OWASP Authorization](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html) | Kein Pflicht-Authframework; Tests an tatsächlichen Grenzen |
| Fremdinhalte/Toolrechte | [OWASP Prompt Injection](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html) | Textlabel/Hook allein ist keine Sicherheitsgrenze |
| Integer-Geldrepräsentation | [MDN Number.isSafeInteger](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Number/isSafeInteger) | Sicherer Integerbereich ersetzt keine Rundungs-/Serialisierungsentscheidung |
| Lokale Termine/UTC | [RFC 5545](https://www.rfc-editor.org/rfc/rfc5545), §3.3.5/§3.8.5.3 | Anwendbare Bibliothek/Zeitzonendaten und fachliche DST-Regel prüfen |
| Personendaten | [DSGVO](https://eur-lex.europa.eu/eli/reg/2016/679/oj), insbesondere Art.5, 15, 17, 18 | Wortlaut/Anwendbarkeit, Rechtsgrundlage, Ausnahmen und Fristen fachlich bestätigen; kein Compliancebeweis |
| Rechnungsnummer | [§14 UStG](https://www.gesetze-im-internet.de/ustg_1980/__14.html), Abs.4 Nr.4 | Nur begrenzter Wortlautabgleich, keine GoBD-/Steuerrechts-Gesamtbewertung |

Pflege: Regel am konkreten Risiko begründen → passende Referenz/AK/prüfbare Grenze bestimmen → Routing/Checker/Export abgleichen → frische Agentenprobe. Neue lokale Erkenntnis zunächst in Harness-Learnings, Produktentscheidung in Projekt-Docs/Specs. Kein automatisches Wachstum des universellen Profils bei jedem CRM-Sonderfall. Verfahren innerhalb dieser Referenzen sind keine nativen Skills; Extraktion erst nach beobachteter Wiederverwendung und Vergleichsprobe.
