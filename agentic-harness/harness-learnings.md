# Harness-Learnings – Agentic-Coding-Learnings

> - **Typ:** Lernnotiz
> - **Status:** Noch keine Einträge.
> - **Zuständigkeit:** Harness-Schwächen und wiederkehrende Agentenfehler bis zur Lösung festhalten; Harness-Änderungen mit Grund dokumentieren (Regeln unten).
> - **Gilt bei:** einer Harness-Schwäche oder einem wiederholten Agentenfehler; **vor jeder Änderung** an einer universellen Harness-Datei, einem Profil oder einem Werkzeug; beim Release.
> - **Ladebeziehungen:** Über `AGENTS.md`; für einen Eintrag nur die betroffene Harness-Datei hinzuziehen. Archiv: `agentic-harness/project/learnings-archiv.md`. Release: `agentic-harness/README.md` („Harness weiterentwickeln“).

## Zweck und Regeln

**Was hier hineingehört:** Agentic-Coding-Learnings, also Erkenntnisse über den Harness und über die Arbeit des Agenten, nicht über das Produkt:

- Der Agent schafft etwas wiederholt nicht oder macht denselben Fehler mehrfach (z. B. widersprüchliche Stände, eine Prüfung, die nichts findet).
- Eine Regel, ein Ablauf oder ein Werkzeug des Harness fehlt, ist unklar oder führt in die Irre.
- Eine Änderung an einer universellen Harness-Datei, einem Profil oder einem Werkzeug wurde vorgenommen.

Pro Eintrag: Anlass, betroffene Datei oder Rolle, warum es über dieses Projekt hinaus wichtig ist, Vorschlag oder Umsetzung, Status. Produktfakten gehören in `agentic-harness/harness/project.md` und `agentic-harness/docs/`.

**Vor jeder Harness-Änderung:** Zuerst die aktiven Einträge hier lesen. Widerspricht die geplante Änderung einem Eintrag „Lokal übernommen“, wird eine bewusste Entscheidung vielleicht zurückgedreht: erst klären, nicht stillschweigend überschreiben.

**Nach jeder Harness-Änderung:** Im selben Schritt einen Eintrag „Lokal übernommen“ mit Grund anlegen oder einen offenen Eintrag umstellen. So bleibt die Änderung auch für Sitzungen ohne Gesprächsverlauf (z. B. nach `/clear`) nachvollziehbar.

**Lebenszyklus:**

```text
Beobachtung ──▶ Offen ──▶ universelle Datei geändert ──▶ Lokal übernommen
                                                              │
Release in die Vorlage: steht die Regel noch so in der Zieldatei? ◀┘
        ├─ ja   ──▶ In Vorlage vX.Y ──▶ verschoben nach agentic-harness/project/learnings-archiv.md
        └─ nein ──▶ nachziehen oder zurück auf Offen
```

- **Offen:** Kandidat oder wiederkehrender Fehler, keine universelle Datei geändert.
- **Lokal übernommen:** in die genannte Datei eingearbeitet, aber noch nicht in der Vorlage.
- **In Vorlage vX.Y:** beim Release gegengeprüft, exportiert und ins Archiv verschoben (dort mit diesem Status vorangestellt).

Der Status ergibt sich aus dem Unterabschnitt unter „Aktive Learnings“; ändert er sich, wandert der Eintrag in den passenden Unterabschnitt.

Die Vorlage startet ohne Einträge: Der Export übernimmt nur Kopf und diesen Abschnitt. Das Archiv ist Projektgeschichte und wird nie exportiert.

## Aktive Learnings

### Offen

Keine.

### Lokal übernommen

Keine.
