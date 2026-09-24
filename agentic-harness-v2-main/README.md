# Agentic Harness V2 – Workflow

Diese README ist bewusst kurz: Erst die Grafik lesen, danach bei Bedarf die genannte Datei öffnen.

```mermaid
flowchart TD
    A([Start: Agent bekommt Aufgabe]) --> B[AGENTS.md lesen<br/>Startpunkt, Grenzen und Verweise]
    B --> C[harness/rules/universal/core.md<br/>entscheidet: welcher Pfad ist nötig?]

    C --> D{Projekt schon initialisiert?}
    D -->|Nein, Pflicht vor erster Umsetzung| E[harness/templates/project-init.md<br/>Projekt einmal sauber klären]
    E --> F[harness/rules/project-specific/project.md<br/>Ziel, Grenzen, Start, Gate-Einstieg]
    F --> G[optional: passende project-specific/*.md<br/>nur benötigte Regeln aktivieren]
    G --> C
    D -->|Ja| H{Aufgabe groß oder unklar?}

    H -->|Ja, optionaler Klärpfad| I[harness/rules/universal/ideas.md<br/>Dialogregeln für offene Vorhaben]
    I --> J[harness/templates/idea.md<br/>Form der Idea]
    J --> K[ideas/IXXX-...<br/>Problem, Nutzen, Umfang, offene Punkte]
    K --> L{Bestätigt + separater Umsetzungsauftrag?}
    L -->|Nein| M([Stop: nur geklärt, kein Code])
    L -->|Ja| N[harness/templates/story.md<br/>kleine prüfbare Story ableiten]

    H -->|Nein, Auftrag ist konkret| O{Ändert Nutzerverhalten?}
    O -->|Ja, Pflicht| N
    O -->|Nein: Doku/Bugfix/Refactor| P[kleinste passende Änderung<br/>bestehende Regeln beachten]

    N --> Q[specs/SXXX-...<br/>AK, Nicht-Umfang, Nachweise]
    Q --> P
    P --> R[harness/rules/universal/quality.md<br/>passende Nachweise nach Risiko wählen]
    R --> S[Quality Gate ausführen<br/>z. B. scripts/verify.py + Projektchecks]
    S --> T{AK erfüllt und Gate grün?}
    T -->|Nein| U[Korrigieren<br/>Code, Test oder Spec gezielt anpassen]
    U --> R
    T -->|Ja| V[Spec auf Implemented setzen<br/>kurz zusammenfassen]
    V --> W[optional: learning-state.md<br/>nur auf ausdrücklichen Speicherauftrag]
    W --> X([Fertig])

    classDef required fill:#e7f3ff,stroke:#1b6ca8,stroke-width:1px;
    classDef optional fill:#fff7df,stroke:#b07d00,stroke-width:1px;
    classDef stop fill:#eeeeee,stroke:#666,stroke-width:1px;
    class B,C,E,F,N,Q,R,S,V required;
    class G,I,J,K,W optional;
    class A,M,X stop;
```

**Legende:** Blau = normalerweise Pflicht im passenden Fall, Gelb = optional/bedarfsgeladen, Grau = Start oder Ende. Der Core ist die Weiche: Er entscheidet, ob Project Init, Idea, Spec oder direkt eine kleine Änderung genügt.

## Mini-Kommentar je Markdown-Datei

| Datei | Verantwortung |
|---|---|
| `AGENTS.md` | Einstiegskarte für Agenten; verweist auf die passenden Regeln, ohne den Core zu duplizieren. |
| `README.md` | Visuelle Orientierung über Workflow und Zuständigkeiten. |
| `learning-state.md` | Manuelle Sammlung bestätigter Erkenntnisse; nur auf ausdrücklichen Speicherauftrag pflegen. |
| `harness/rules/universal/core.md` | Universeller Ablauf und Entscheidung, wann Idea, Spec und Gate nötig sind. |
| `harness/rules/universal/ideas.md` | Regeln zur Klärung größerer oder unklarer Vorhaben vor einer Umsetzung. |
| `harness/rules/universal/quality.md` | Auswahlhilfe für passende Nachweise nach Risiko; keine Projektbefehle. |
| `harness/rules/project-specific/project.md` | Konkretes Projektprofil mit Ziel, Grenzen, Startweg und Gate-Einstieg. |
| `harness/rules/project-specific/code.md` | Projektweite Code- und Architekturkonventionen, falls benötigt. |
| `harness/rules/project-specific/python.md` | Python-Regeln für Projekte oder Aufgaben mit Python-Code. |
| `harness/rules/project-specific/web.md` | Web-Regeln für UI, Browser, Netzwerk und Accessibility, falls relevant. |
| `harness/rules/project-specific/testing.md` | Projektspezifische Testwerkzeuge, Fixtures, Testdaten und Konventionen. |
| `harness/rules/project-specific/quality-matrix.md` | Zuordnung von Projektbereichen zu Qualitätsnachweisen, wenn mehrere Risiken erklärt werden müssen. |
| `harness/templates/project-init.md` | Leitfaden für die einmalige Initialisierung eines konkreten Projekts. |
| `harness/templates/idea.md` | Vorlage für eine Idea: Problem, Nutzen, Umfang, Entscheidungen und offene Punkte. |
| `harness/templates/story.md` | Vorlage für eine prüfbare Story mit Akzeptanzkriterien und Nachweisen. |
| `ideas/I001-harness-v2.md` | Konkrete übergeordnete Idea zur Weiterentwicklung des Harness. |
| `specs/S001-starter-kit-init-and-quality-gate.md` | Umgesetzte Spec für Starter-Kit-Initialisierung und neutrales Quality Gate. |
