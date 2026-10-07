# Projekt – projektspezifische Harness-Dateien

Dieser Ordner trennt, was nur zu diesem Projekt gehört (Ausgangsbeschreibung, erledigte Learnings), vom universellen Harness:

```text
project/
├─ README.md            ← universell: diese Anleitung und die Gliederung für den Brief; wandert in jede Vorlage
├─ brief.md             ← projektspezifisch: Beschreibung des Auftraggebers; wird nie exportiert
├─ learnings-archiv.md  ← projektspezifisch: erledigte Harness-Learnings (siehe harness-learnings.md); wird nie exportiert
└─ <thema>.md          ← projektspezifisch, bei Bedarf: weitere Projekt-Docs (Kriterium: document-contract.md); nie exportiert
```

## Wie der Brief entsteht

Ablauf („Erzählen → Konkretisieren“) und Themen zum Erzählen stehen an einer Stelle: in der `README.md` im Projektordner (Root), Abschnitt „Projektstart mit dem Agentic Harness“. Dieser Abschnitt ist universell und steht in jedem Projekt unter Titel und lokaler Adresse in der README.
