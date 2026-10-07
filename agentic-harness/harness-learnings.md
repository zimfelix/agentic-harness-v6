# Harness-Learnings

**Zuständigkeit:** Harness-Schwächen, wiederkehrende Agentenfehler und Gründe beauftragter Harness-/Profil-/Tooländerungen. Bei Beobachtungen, vor Harness-Änderungen und beim Release lesen.

## Zweck und Regeln

Produktfakten gehören in Projektprofil/Docs/Specs. Hier pro Eintrag kurz: Anlass, betroffene Regel, Grund, Vorschlag/Umsetzung und Erprobungsstand. Vor Änderungen aktive Einträge prüfen, bewusste Entscheidungen nicht still zurückdrehen. Neue Regeländerungen im selben Schritt dokumentieren; universelle Änderungen nur auf Auftrag.

**Offen** = Beobachtung/Hypothese. **Lokal übernommen** = Regel/Tool geändert, Wirksamkeit ggf. noch ungeprüft. Nach beauftragtem Release gegen Zieldateien prüfen und erledigte Einträge ggf. mit Release-Verweis nach `project/learnings-archiv.md` verschieben. Export übernimmt diese Regeln, keine Einträge/Archive. Statische Checks belegen keine konstante Agentenleistung.

## Aktive Learnings

### Offen

- Mail-Prototyp: Agent las Init/Geschäftssoftware-Regeln, schrieb dennoch Produktcode bei `Pending Project Init`, ohne Projektbefüllung, Strukturentscheidung, erforderliche Docs, Soll/Prüfplan oder Tests. Auftraggeber stoppte. Beobachteter Regelverstoß; vorhandene Regeln verhinderten ihn nicht. Offen: Wirksamkeit des Vor-Code-Checks in frischer Agentensitzung. Readiness ist kein technisches Schreibverbot.
- Aus Lite erhalten: Robustheit von Spec-Status bei externen Testblockern, risikobezogener Check-/TDD-Auswahl, Fortsetzung nach Kontextverlust, Nichtumsetzung zurückgestellter Ideen und Begrenzung des Dokumentenwachstums praktisch offen. Review: `project/harness-review.md`.

### Lokal übernommen

- v4.5 führt ursprünglichen Harness und sinnvolle Lite-Regeln in einer Vorlage zusammen: kurzer Einstieg, Brief/Technik/Struktur im Init, ein Verification Loop, Bereichs-Specs/Ideas/Templates erhalten. Produktverhalten vor Code spezifizieren; begrenzte Erkundungs-Spikes ausdrücklich abgrenzen. Separate Lite-Variante entfällt; Mail-Prototyp und separate Worktrees unverändert.
- Auf ausdrücklichen Wunsch nur `profiles/`: Website und Business Software bündeln Einstieg, Referenzen, Werkzeuge und Assets. Native Skill-/Adapterordner entfernt, keine Kopiersynchronisierung. Profile werden durch `AGENTS.md` ausdrücklich geladen. Website-Stil bleibt opt-in; Geschäftssoftware-Bereiche risikobezogen wählen.
- Dokumentenvertrag/Map/Produkt-README vereinfacht; Struktur vor Code und Regression bei Refactoring erhalten. Bei jeder Harness-Änderung Definitionen, Abhängigkeiten, Ladeauslöser, Verweise, Werkzeugpfade und Export im selben Schritt abgleichen. Spec-Regeln und Template sind keine zweite Projektprofil-Definition.
- Website-Werkzeuge unter `profiles/website/tools/`, Vorschau/Inspiration unter `assets/`; relativen Vorschau-Assetpfad angepasst. Export nutzt explizite universelle Dateiliste und lehnt Produktziele ab. Prüfstand der endgültigen Profilstruktur: 17/17 Kopier-/Export-/Readiness-/Dependency-Tests einschließlich Fehlergegenproben und HTTP-Smoke der Vorschau bestanden; Strukturcheck, Shell-/JavaScript-Syntax und `git diff --check` bestanden. Einmalige Testdatei danach auf Auftrag entfernt; dauerhafter Struktur-/Readiness-Checker bleibt. Keine frische Agenten-Verhaltensprobe.
