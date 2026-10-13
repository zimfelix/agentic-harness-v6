# Codekonventionen

**Zuständigkeit:** Nicht bereits durch Code oder Werkzeuge ausgedrückte Konventionen und technische Schulden. Lesen bei Codeänderungen/Refactoring, Struktur aus `docs/architecture.md` beachten.

## Universeller Rahmen

Nur geltende Konventionen für den gewählten Stack festhalten. Ausführbare Regeln in Formatter/Linter/Typprüfung statt Prosa. Gemeinsame Werte einmal definieren; Regeln ersetzen, nicht mit Sonderfällen übersteuern. Refactorings folgen Core und Projekt-Regression, nicht einer ungeprüften Behauptung „sauberer“.

## Projektspezifische Befüllung

- Python 3 standard library only; no third-party imports, no network modules.
- Domain rules raise `PlannerError` with a user-readable message; the CLI prints `error: …` to stderr and exits 1 (argparse usage errors exit 2). No silent fallbacks.
- Mutations happen on an in-memory `Plan` inside `Store.transaction()`; never write SQL for domain changes outside `store.py`.
- Every mutating command must leave `validate_plan` passing; add new invariants there, not as per-command special cases.
- Technical debt: full-state rewrite per write (fine for hundreds of tasks, not for tens of thousands); no linter/type checker available under the stdlib-only constraint.
