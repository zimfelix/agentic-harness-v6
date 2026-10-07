# Bereichs-Specs

**Zuständigkeit:** Lebender beauftragter Soll-Stand, AK und aktuelle Nachweise. Keine Ist-Architektur oder Gesprächsprotokolle.

- Neues/geändertes Produktverhalten vor Umsetzung spezifizieren, auch im Produkt-Prototyp. Erkundungs-Spike folgt der abgegrenzten Init-Ausnahme. Verhaltensgleiche Refactors, Doku und kleine Gestaltungsiterationen brauchen keine künstliche Spec.
- Bestehenden zusammenhängenden Bereich aktualisieren; unabhängig beauftragbare/prüfbare Funktion als eigene Spec. Nicht eine Spec je Datei/Textkorrektur.
- Template: `harness/templates/spec.md`. IDs fortlaufend, nicht neu nummerieren. Beauftragte Idea verlinken, AK nicht in der Idea duplizieren.
- `Modified`: neu, Soll geändert oder Erfüllung nicht vollständig belegt. `Implemented`: sämtliche geltenden AK mit gültigem Nachweis und erforderliche Pflicht-/Regressionstests bestanden (`harness/verification.md`). Fehlende Umgebung/Checks sind Blocker, keine Erfüllung.
- Ein AK hat ein unabhängig prüfbares Ergebnis. Mehrere unabhängig scheiternde Aussagen teilen. Pixel/Farb-/Schriftregeln in Design/Tokens, nicht als AK-Liste.
- Je AK letzter gültiger Nachweis: Prüfziel, Test/Schritte, geprüfter Stand (Commit oder „uncommittet, Datum“), Ergebnis. Bei Solländerung Nachweis ersetzen. Unveränderte AK müssen bei betroffener Regression erneut belegt werden; alte Nachweise nicht blind übernehmen.
- Prüfplan vor Umsetzung festlegen, Arbeitsstand vor Übergabe aktualisieren. Nicht ausführbare Checks gesondert nennen.
- Richtgröße etwa 15 KB/15 AK. Zuerst verdichten; unabhängig prüfbare Gruppen bei Bedarf trennen, Verweise/AK-IDs erhalten. Bei vollständig entfallenem Bereich archivieren und Verweise nachführen.
- Bei Änderungen an Spec-Format, Definitionen oder Statusregeln alle abhängigen Templates, Core-/Init-/Verification-Regeln und Verweise im selben Schritt abgleichen (`document-contract.md`). Konkrete Spec-Abhängigkeiten stehen in der jeweiligen Spec; Projektbrief/Architektur ersetzen nicht deren Soll.
