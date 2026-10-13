# Gestaltung

**Zuständigkeit:** Übergreifende Gestaltungsregeln und bewusste Abweichungen, nur bei Oberfläche. Lesen bei sichtbaren Änderungen. Prüfgrößen/Werkzeuge in `docs/testing.md`; Website-Regeln im gewählten Profil.

## Universeller Rahmen

Farbrollen, Schrift/Quelle/Lizenz, Größenskala, wiederkehrende Bausteine und Zustände festlegen. Konkrete Werte leben in Tokens, hier nur nötige Regeln/Verweise; nicht jeden CSS-Wert abschreiben. Gewählter Entwurf und Auftraggeber gehen vor optionalen Stilvorschlägen. Eine Entscheidung ersetzt die alte Regel.

Wiederkehrende Rollen nutzen gemeinsame Bausteine; Aussehen im Zielmedium belegen (`harness/verification.md`). Ohne UI als nicht relevant markieren, keine Gestaltungsregeln erfinden.

## Projektspezifische Befüllung

Keine grafische Oberfläche. CLI: argparse-Hilfe, lesbare JSON-Berichte auf stdout (auch maschinenlesbar), Fehler auf stderr mit Exit 2. Übersicht zeigt blocked/ready/done und konkrete unerledigte Voraussetzungen, Aufwandssummen und Fortschritt. Keine Farbe/Terminalabhängigkeit; Validierungsmeldungen nennen betroffene IDs. Prüfung im echten CLI, kein Screenshot erforderlich.
