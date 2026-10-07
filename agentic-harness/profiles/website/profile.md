# Profil Website

**Gilt bei:** Website-Init, sichtbaren Änderungen, neuen Seiten, Markup/CSS-Refactoring und Livegang, wenn gewählt; in anderen UI-Projekten nur auf Auftrag. **Zuständigkeit:** Website-Regeln; optionale Gestaltung und Nachweise in Bedarfsreferenzen.

Projektwerte/Abweichungen in `docs/design.md`, Struktur/Betrieb in `docs/architecture.md`, Prüfgrößen/Werkzeuge in `docs/testing.md`, Auswahl in `harness/project.md`. Core und Verification nicht wiederholen. Abgeleitet aus einem Website-Projekt; breitere Erprobung offen.

## Bedarfsreferenzen

| Anlass | Lesen |
|---|---|
| Stil-Vorschläge gewünscht | `references/stil.md` (nur auf Wahl, kein Standard) |
| Init/neue Seiten, Struktur oder Deployment wählen | `references/baukasten.md` |
| Erste Seite, Markup/CSS-Refactor, Meilenstein, Veröffentlichung | `references/nachweis.md` |
| Webtools einrichten/ändern | `profiles/website/README.md` |
| Gestaltungsrichtungen erkunden | `profiles/website/assets/inspiration/README.md`, dann passende Einträge |

## Init-Fragen

Nur offene, für den ersten Schritt relevante Fragen ergänzen: Seiten/Navigation, Sprache/Ansprache, Inhalte/Freigaben, echte Kontaktwege/Formularversand, Firmendaten/Rechtsseiten, Bild-/Schriftrechte, Marke/gewählter Entwurf, Domain/Hosting/Indexierung und Veröffentlichung. Pflichtregeln versus optionale Stil-/Baukastenteile ausdrücklich unterscheiden.

## Pflichtregeln

- Gleiche Rahmen (Header/Footer/Kontaktblock) aus einer Quelle. Gleichartige Abschnitte als gemeinsame Bausteine, bei bekannter Gleichheit ab zweitem Vorkommen. Keine gemeinsamen Gestaltungsbausteine zwischen noch ungewählten Vergleichsvarianten.
- Nur vorgesehene Routen ausliefern; Konzepte intern und `noindex`, nach Wahl archivieren/löschen.
- Schriften mit belegter Lizenz und tatsächlicher Ladeprüfung. Eine Größenskala, benannte Ausnahmen; Farben als Rollen/Tokens mit lesbarem Kontrast. Großbuchstaben per CSS.
- Abstände aus einer Skala; verbindliche Ausrichtungen bei Projekt-Prüfgrößen messen. Einzelwerte im Code, nicht doppelt dokumentieren.
- Gleiche Button-/Linkrollen verhalten sich gleich; Linktext benennt das Ziel. Sichtbarer Fokus, tastatur-/touchbedienbare Navigation, Anker sichtbar unter Sticky-Headern.
- Breite steuert Layout; `hover`/`pointer` steuern Bedienart. Keine Funktion nur per Hover; Hover-Effekte unter `@media (hover: hover)`. Inhalt mit Höchstbreite, Umbrüche nach Inhalt, nicht Gerätenamen.
- Tippflächen mindestens 24×24 CSS-px oder gemäß WCAG 2.2 2.5.8 ausreichend getrennt; Buttons/Menüs möglichst 44 px. Formularschrift mindestens 16 px gegen iOS-Eingabezoom. `prefers-reduced-motion: reduce` beachten.
- Bilder/Material nur mit Freigabe, Quellenliste aktuell. Keine erfundenen Referenzen/Rechtsangaben; Prototyp sichtbar als Entwurf und `noindex`. Ungeprüfte Kontaktwege markieren, Formulare ohne Server erklären ihr Verhalten. Vorbilder sind keine Freigabe zum Kopieren fremder Inhalte.
- Sichtbare Ergebnisse im Browser messen und per Screenshot beurteilen. Kleine Iteration gezielt prüfen; zusätzliche Nachweise nur nach Anlass aus `references/nachweis.md`.
