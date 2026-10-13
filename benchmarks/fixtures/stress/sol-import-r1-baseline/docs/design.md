# Gestaltung

**Zuständigkeit:** Übergreifende Gestaltungsregeln und bewusste Abweichungen, nur bei Oberfläche. Lesen bei sichtbaren Änderungen. Prüfgrößen/Werkzeuge in `docs/testing.md`; Website-Regeln im gewählten Profil.

## Universeller Rahmen

Farbrollen, Schrift/Quelle/Lizenz, Größenskala, wiederkehrende Bausteine und Zustände festlegen. Konkrete Werte leben in Tokens, hier nur nötige Regeln/Verweise; nicht jeden CSS-Wert abschreiben. Gewählter Entwurf und Auftraggeber gehen vor optionalen Stilvorschlägen. Eine Entscheidung ersetzt die alte Regel.

Wiederkehrende Rollen nutzen gemeinsame Bausteine; Aussehen im Zielmedium belegen (`harness/verification.md`). Ohne UI als nicht relevant markieren, keine Gestaltungsregeln erfinden.

## Projektspezifische Befüllung

Keine grafische Oberfläche. Jeder CLI-Aufruf schreibt genau einen JSON-Wert, auch Hilfe/Argumentfehler. Run-Berichte behalten die vorgegebenen Felder; rejected_groups signalisiert Teilannahme, interrupted eine Wiederaufnahme. Fehlerobjekte für Whole-file/Input-, Konflikt- und Betriebsfehler haben status und reason. README erklärt Exitcodes und Zustände.
