# Harness-Learnings – übertragbare Beobachtungen

> - **Typ:** Lernnotiz
> - **Status:** Noch keine Beobachtungen.
> - **Zuständigkeit:** Beim Einsatz in diesem Projekt beobachtete Stärken, Schwächen und Unklarheiten des universellen Harnesses für eine spätere Prüfung festhalten.
> - **Gilt bei:** Wenn bei Project Init, Umsetzung, Rückfragen oder Verifikation eine möglicherweise projektübergreifende Harness-Erkenntnis entsteht.
> - **Ladebeziehungen:** Bei diesem Auslöser über `AGENTS.md` lesen; für eine konkrete Beobachtung nur die betroffene Harness-Datei hinzuziehen. Format und neue Ladewege nach `agentic-harness/document-contract.md` und `agentic-harness/harness-map.md` prüfen.
> - **Nicht zuständig:** Produktfakten, projektspezifische Regeln oder eine automatische Änderung am Quell-Harness.

## Abgrenzung

Hier landen **Kandidaten für universelle Verbesserungen**, keine Gesprächsprotokolle und keine bestätigten Regeln. Gewählter Stack, Produktgrenzen und konkrete Befehle gehören in `agentic-harness/harness/project.md` und die betroffenen `agentic-harness/docs/`-Dateien. Pro Beobachtung: Anlass, betroffene Datei oder Rolle, warum sie für andere Projekte relevant ist, Vorschlag bzw. Umsetzung und Status.

**Lebenszyklus:** Die Liste wächst im Projekt und wird dort nicht geleert. Jeder Eintrag beginnt mit seinem Status:

```text
Beobachtung ──▶ Offen ──▶ (Auftrag) universelle Datei geändert ──▶ Lokal übernommen
                                                                        │
Release in die Vorlage: steht die Regel noch so in der Zieldatei? ◀─────┘
        ├─ ja   ──▶ In Vorlage vX.Y   (bleibt hier als Spur)
        └─ nein ──▶ nachziehen oder zurück auf Offen
```

- **Offen:** Kandidat, keine universelle Datei geändert.
- **Lokal übernommen:** in die genannte universelle Datei oder das Profil eingearbeitet, aber noch nicht in der Vorlage.
- **In Vorlage vX.Y:** beim Release gegengeprüft und exportiert.

Beim Release prüft der Agent jeden Eintrag mit „Lokal übernommen“ gegen die genannte Zieldatei, denn eine übernommene Regel kann später wieder geändert worden sein (`agentic-harness/README.md`, „Harness weiterentwickeln“). Die Vorlage selbst startet mit leerer Liste: Der Export übernimmt nur diesen Abschnitt.

## Beobachtungen

Noch keine Beobachtungen.
