#!/usr/bin/env python3
"""Static consistency/readiness checks, not an enforcement layer or product test."""
import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ('architecture', 'code', 'testing', 'design')
REQUIRED = ('AGENTS.md', 'document-contract.md', 'harness-learnings.md', 'harness/core.md',
            'harness/project.md', 'harness/init.md', 'harness/verification.md',
            'harness/templates/idea.md', 'harness/templates/spec.md', 'harness/templates/project.md', 'ideas/I000-readme.md',
            'specs/S000-readme.md', 'tools/export-harness.sh',
            'profiles/business-software/profile.md', 'profiles/website/profile.md')
FIELDS = ('Ziel und Nutzer', 'Reifegrad', 'Erstes Ergebnis und Nicht-Ziele', 'Erfolgskriterium',
          'Risiken, Grenzen und Freigaben', 'Ausgangslage', 'Stack und Struktur',
          'Standards und Qualitätsziele', 'Prüfstrategie', 'Projekt-Docs')


def check(root=ROOT, ready=False):
    root = Path(root)
    errors = []
    for name in (*REQUIRED, *(f'docs/{d}.md' for d in DOCS)):
        if not (root / name).is_file():
            errors.append(f'Pflichtdatei fehlt: {name}')
    for legacy in ('.agents', '.claude', 'skills'):
        if (root / legacy).exists() or (root / legacy).is_symlink():
            errors.append(f'Parallele Profil-/Skill-Ablage nicht erlaubt: {legacy}')
    for path in root.rglob('*.md'):
        if '.git' in path.parts or path.is_symlink():
            continue
        text = path.read_text()
        # Concrete root paths inside backticks, plus explicit markdown links.
        candidates = re.findall(r'`((?:harness|docs|tools|profiles|skills|ideas|specs|\.agents|\.claude)/[^`\s]+\.(?:md|py|sh|html))`', text)
        for target in candidates:
            if any(mark in target for mark in ('<', '{', 'xxx', 'nnn', '*', '...')) or target.startswith('docs/decisions/'):
                continue  # Documented examples or project-only artifacts.
            if not (root / target).exists():
                errors.append(f'{path.relative_to(root)}: Ziel fehlt: {target}')
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', text):
            if '://' in target or target.startswith('#'):
                continue
            if not (path.parent / target.split('#')[0]).exists():
                errors.append(f'{path.relative_to(root)}: Link fehlt: {target}')
        if path.name == 'profile.md':
            if '**Gilt bei:**' not in text or '**Zuständigkeit:**' not in text:
                errors.append(f'Profil-Auslöser/Zuständigkeit fehlt: {path.relative_to(root)}')
            for target in re.findall(r'`(references/[^`\s]+\.md)`', text):
                if not (path.parent / target).exists():
                    errors.append(f'Profil-Referenz fehlt: {target}')
    for path in (root / 'profiles').rglob('*.mjs'):
        text = path.read_text()
        imports = re.findall(r"from ['\"](\.[^'\"]+)['\"]", text)
        assets = re.findall(r"new URL\(['\"](\.[^'\"]+)['\"], import.meta.url\)", text)
        for target in imports + assets:
            if not (path.parent / target).exists():
                errors.append(f'{path.relative_to(root)}: Werkzeug-Abhängigkeit fehlt: {target}')
    if ready and (root / 'harness/project.md').exists():
        text = (root / 'harness/project.md').read_text()
        for field in FIELDS:
            match = re.search(r'^- \*\*' + re.escape(field) + r':\*\* (.+)$', text, re.M)
            if not match or re.match(r'(?i)(offen|noch offen|\[|–)', match[1]):
                errors.append(f'Init-Feld fehlt/offen: {field}')
        profiles = re.search(r'^- \*\*Profile:\*\* (.+)$', text, re.M)
        if not profiles or profiles[1].startswith('keine gewählt;'):
            errors.append('Profil-Auswahl noch ungeprüft')
        for name in DOCS:
            path = root / f'docs/{name}.md'
            if not path.exists():
                continue
            content = path.read_text().partition('## Projektspezifische Befüllung')[2].strip()
            if not content or content.startswith('Noch offen'):
                errors.append(f'Doc nicht ausgefüllt/abgewählt: docs/{name}.md')
            if name == 'architecture' and content.lower().startswith('nicht relevant'):
                errors.append('Dateistruktur/Architektur vor Produktcode erforderlich')
    return list(dict.fromkeys(errors))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ready', action='store_true', help='zusätzlich erforderliche Init-Einträge prüfen')
    args = parser.parse_args()
    errors = check(ready=args.ready)
    if errors:
        for error in errors:
            print('FEHLER:', error)
        raise SystemExit(1)
    print('Struktur konsistent' + ('; Init-Einträge vorhanden (fachliches Go separat prüfen)' if args.ready else ''))


if __name__ == '__main__':
    main()
