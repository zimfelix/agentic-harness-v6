# Idee 000 – Ideas als Akte größerer Änderungen

> **Zuständigkeit:** Größere Änderungen von der ersten Idee bis zum Abschluss führen: Anlass, Umfang, betroffene Bereichs-Specs, Abhängigkeiten, Status. Kein lebender Soll-Stand (der steht in den Specs) und ohne Auftrag keine Implementierungsfreigabe.

## Wann eine Idea

- **Ja**, wenn mindestens eins zutrifft: die Änderung braucht mehrere getrennt prüfbare Schritte (Teilaufgaben) oder kann sich über mehr als eine Sitzung erstrecken; sie betrifft mehr als eine Bereichs-Spec; sie braucht eine Entscheidung des Auftraggebers oder ist noch offen (z. B. Benutzerkonto, neue Seite mit eigener Logik, Umbau der Navigation, Weg zum Livegang).
- **Nicht schon deshalb**, weil eine Änderung mehrere Dateien berührt (Code, Stil und Test einer Funktion gehören zusammen).
- **Nein:** kleine Iterationen (Text, Abstand, Farbe innerhalb bestehenden Verhaltens; kurzer Gate-Weg) und verhaltensgleiche Refactors ohne Entscheidungsbedarf. Sie laufen direkt über den Auftrag.

## Lebenszyklus

```text
Offen ──(Klärung + Auftrag)──▶ Beauftragt     (direkter Auftrag mit klarem Umfang: gleich Beauftragt) ──(umgesetzt, Gate bestanden)──▶ Umgesetzt ──▶ ideas/archiv/
  │                                │
  └────────────┬───────────────────┘
               ▼
   Zurückgestellt / Verworfen (mit Grund) ──▶ ideas/archiv/
```

- **Offen:** Klärung läuft; Lösungsansatz und Alternativen werden gesammelt. Keine Umsetzung.
- **Beauftragt:** Der Auftraggeber hat die Umsetzung freigegeben; ein direkter Umsetzungsauftrag mit klarem Umfang genügt. Neue Funktionen, betroffene Bereichs-Specs, Abhängigkeiten und Teilaufgaben stehen fest. Teilaufgaben werden einzeln umgesetzt, geprüft und abgehakt; so kann eine spätere Sitzung genau dort weitermachen.
- **Umgesetzt:** Gate bestanden, betroffene Bereichs-Specs und Docs sind nachgeführt. Datum, Ergebnis und Verweise unter „Abschluss“ eintragen, Datei nach `agentic-harness/ideas/archiv/` verschieben.
- **Zurückgestellt / Verworfen:** Grund unter „Abschluss“ eintragen, Datei ins Archiv. Zurückgestelltes wird bei der Durchsicht erneut geprüft und kann zurückgeholt werden.

Ältere Ideas mit `Draft` gelten als Offen, mit `Ready` als geklärt, aber noch nicht beauftragt.

## Zusammenspiel mit Specs

Die Idea ist die **Akte der Änderung** (warum, was, welche Bereiche, in welcher Reihenfolge). Akzeptanzkriterien und Nachweise stehen **nur** in der Bereichs-Spec (`agentic-harness/specs/S000-readme.md`). Die Idea nennt, welche Specs neu entstehen und welche AK geändert werden, ohne sie zu kopieren.

```text
Wunsch ──▶ Idea (Offen) ──Auftrag──▶ Idea (Beauftragt) ──▶ Bereichs-Spec(s) anlegen/ändern ──▶ umsetzen
                                                                                                │
           Idea (Umgesetzt) → Archiv ◀── Gate: Specs + Docs nachgeführt? Idea abgeschlossen? ◀──┘
```

## Durchsicht

Bei jedem Harness-Release und bei Meilensteinen: Sind offene Ideas noch aktuell? Ist Beauftragtes umgesetzt? Stimmt jeder Status? Erledigtes, Zurückgestelltes und Verworfenes ins Archiv. Neue Ideen nach `agentic-harness/harness/templates/idea.md` anlegen.
