# Dokumentenvertrag

**Gilt bei:** Markdown anlegen/befüllen/verdichten oder Dateirollen, Pfade und Ladewege ändern. Regelt Dokumentpflege, nicht Produktablauf oder Architektur.

## Eine Zuständigkeit, ein erreichbarer Auslöser

- Vor dem Anlegen prüfen: Passt das Wissen in Code/Konfiguration, Projektprofil, Spec oder vorhandene Doc? Nur dauerhaft benötigtes Wissen dokumentieren, nicht Offensichtliches oder ausführbare Werte doppeln.
- Neue Doc nur bei eigenständigem, wiederholt benötigtem Thema. Keine Pflicht zu zusätzlichen Dokumenten/Ordnern; gewählte Profile dürfen risikobezogen konkrete Docs verlangen.
- Steuerungs-/Projekt-Docs beginnen mit Titel und kurzem **Zuständigkeit/Gilt bei**-Hinweis. Nur notwendige direkte Leseverweise und Abgrenzungen ergänzen. Kein obligatorischer sechsteiliger Metakopf. Profile benennen Zuständigkeit und Leseauslöser; Ideas/Specs nutzen ihr Template; menschliche READMEs keinen Agenten-Metakopf.
- Neue Projekt-Docs über konkreten Auslöser in `AGENTS.md` erreichbar machen. Beispielauslöser für eine bei Bedarf angelegte Datenschutz-Doc: „bei Personendaten, Auskunft oder Löschung“. Eine separate Landkarte ist nicht erforderlich; Einstieg plus lokale Verweise müssen ausreichen.
- Ein Leseverweis ist keine Änderungsfreigabe. Universelle Harness-Regeln/Profile/Werkzeuge grundsätzlich nur im zentralen v6-Vorlagen-Repository ändern, außerhalb ausschließlich mit konkretem Ausnahmeauftrag. Projektbefüllung, Projektkonfiguration und projektspezifische Ergänzungen bleiben erlaubt; Vorschläge zur Vorlage lokal mit Kontext sammeln.

## Ablage und Quelle der Wahrheit

| Wissen | Ort |
|---|---|
| Bestätigter Brief, Arbeitsmodus/Delegation, Grenzen, Profile, Befehle, letzter Prüfstatus, Init-Go | `harness/project.md` |
| Lebendes beauftragtes Verhalten, AK, Prüfplan und letzte Nachweise | Bereichs-Spec unter `specs/` |
| Größeres/offenes Vorhaben, Alternativen, Teilaufgaben | Idea unter `ideas/` |
| Struktur, Fachmodell, Schnittstellen, Betrieb, Ort von Secrets (nie Werte) | `docs/architecture.md` |
| Nicht technisch abbildbare Codekonventionen / technische Schulden | `docs/code.md` |
| Teststrategie, Regression, Umgebungen und Prüfgrößen | `docs/testing.md` |
| Übergreifende Gestaltung / bewusste Abweichungen | `docs/design.md`; konkrete Tokens im Code referenzieren |
| Eigenständiges Projektthema | Fachlich passende Doc unter `docs/`, nur bei Bedarf; zusätzliche Docs sind rein projektspezifisch |
| Harness-Beobachtungen/Änderungsgründe | Lokale `harness-learnings.md` mit Quellprojekt, Harness-Stand, Auftrag, Soll/Ist, Belegen und offenen Fragen; Wochenreview/Übernahme auf Auftrag im zentralen v6-Repository |
| Verlauf und einzelne Prüfläufe | Git und Übergabe; kein Gesprächsprotokoll in geltenden Regeln |

## Profile als einzige Quelle

Projektarten liegen ausschließlich unter `profiles/<name>/`: `profile.md` ist der Einstieg, `references/` enthält bedarfsgeladene Fachregeln, `tools/` die passenden Werkzeuge und `assets/` das Zubehör. Keine zweite Skill-Quelle oder Adapterverzeichnisse.

Bei „Profil/Skill aktualisieren“ die entsprechende Quelle unter `profiles/` bearbeiten. Eine Synchronisierung entfällt. Profile werden ausdrücklich über die Auslöser in `AGENTS.md` geladen, nicht durch native Skill-Erkennung. Auswahl und Bereiche stehen in `harness/project.md`; Bereichsnamen/Routing werden im jeweiligen Profil definiert. Bedarfsverfahren dürfen in Referenzen stehen, sind aber keine nativ erkannten Skills. Herkunft/Evidenz eines Profils bei Bedarf in dessen Referenzen, nicht als neues Produktregelwerk. Bei neuen Profilen/Umbenennungen Routing, Projektzuordnung, Verweise und Export gemeinsam abgleichen.

## Pflege

Geltenden Stand ersetzen, nicht „früher/jetzt“-Absätze anhängen. Je AK letzter gültiger Nachweis; offene Fragen nicht als entschieden darstellen. Beim Verdichten bestätigte Grenzen/Entscheidungen erhalten oder an die zuständige Stelle verschieben. Richtgrößen: Projektprofil/Projekt-Doc etwa 6 KB, Spec etwa 15 KB/15 AK. Erst verdichten, dann eigenständige Themen trennen; keine harte Byte-Sperre.

**Bei jeder Harness-Änderung** vorab betroffene Abhängigkeiten suchen: Regeln, Rollen, Status/Definitionen, Namen, Pfade und Links. Alle abhängigen Stellen im selben Schritt mitführen: `AGENTS.md`, Core/Init/Verification, Projektgerüst, Profile, Templates, Spec-/Idea-Definitionen, direkte Verweise, Werkzeug-Imports/Assets, Zubehörübersichten und Exportliste. Nur tatsächlich Betroffenes ändern, nicht alle Docs laden. Danach reale Ziele, Definitionen und Kopier-/Exportverhalten prüfen; `python3 tools/check-harness.py` prüft konkrete Verweise und Werkzeugpfade. Keine Änderung als abgeschlossen melden, solange relevante Abhängigkeiten ungeklärt oder kaputt sind.

## Trennung für Export

`harness/project.md` und die vier mitgelieferten Docs behalten die Überschrift `## Projektspezifische Befüllung`; oberhalb stehen nur universelle Hinweise, darunter der Produktstand. Export setzt den Produktteil zurück. Ein bewusst nicht relevanter Bereich bekommt einen kurzen Grund, keine leere Scheindokumentation.

`AGENTS.md` trennt Projektverweise unter `## Projektspezifische Ergänzungen`. Learnings trennen Regeln und Einträge (`## Aktive Learnings`). Export übernimmt keine konkreten Ideas/Specs, neuen Projekt-Docs, Produkt-README, Produktdaten oder Learnings-Einträge. Aus dem Vorlagen-Repository werden nur Inhalte unter `agentic-harness/` verwendet, nicht dessen Root-README oder `tests/`; die Start-README im Export wird neu erzeugt. Die exportierte `harness-learnings.md` enthält die Sammel-/Auswertungsregeln und leere Eintragsbereiche. Entscheidend ist die explizite Exportliste in `tools/export-harness.sh`, nicht ein mitwachsendes `docs/*`-Glob.
