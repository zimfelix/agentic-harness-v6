#!/usr/bin/env python3
"""Static consistency/readiness checks, not an enforcement layer or product test."""
import argparse
import os
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
          'Risiken, Grenzen und Freigaben', 'Ausgangslage', 'Arbeitsmodus und Autonomie', 'Stack und Struktur',
          'Standards und Qualitätsziele', 'Prüfstrategie', 'Projekt-Docs')


def field(text, name):
    matches = re.findall(r'^- \*\*' + re.escape(name) + r':\*\* (.+)$', text, re.M)
    return matches[0].strip() if len(matches) == 1 else ''


def unresolved(value):
    return not value or bool(re.match(r'(?i)(offen|noch offen|noch nicht|ausstehend|nicht erteilt|keine freigabe|pending|\[|–|—|tbd)', value))


def profile_errors(root, value):
    if unresolved(value) or value.startswith('keine gewählt;'):
        return ['Profil-Auswahl noch ungeprüft']
    no_profile = re.fullmatch(r'keine \(([^()]+)\)', value)
    if no_profile:
        return ['Profil-Abwahl noch offen'] if unresolved(no_profile[1].strip()) else []
    errors, seen = [], set()
    for selection in value.split('|'):
        name, _, body = selection.strip().partition(':')
        path = root / 'profiles' / name / 'profile.md'
        if not re.fullmatch(r'[a-z0-9-]+', name) or not path.is_file():
            errors.append(f'Unbekanntes Profil/Format: {name}')
            continue
        if name in seen:
            errors.append(f'Profil doppelt gewählt: {name}')
        seen.add(name)
        # Bereichsnamen aus der maßgeblichen Profiltabelle, kein zweiter Katalog im Checker.
        section = path.read_text().partition('## Auswahl und Leseauslöser')[2].split('## Grundschutz')[0]
        areas = set(re.findall(r'^\| ([^|]+?) \|', section, re.M)) - {'Bereich'}
        if not areas:
            if body.strip() not in ('', 'gewählt'):
                errors.append(f'Profil ohne Bereichsformat: {name}')
            continue
        active, marker, inactive = body.partition('; abgewählt:')
        selected = [a.strip() for a in active.split(',') if a.strip()]
        excluded = []
        if marker:
            # Kommas innerhalb einer Begründung trennen keinen Bereich.
            for item in re.split(r',\s*(?![^()]*\))', inactive.strip()):
                match = re.fullmatch(r'([^()]+?)\s*\(([^()]+)\)', item.strip())
                if not match or unresolved(match[2].strip()):
                    errors.append(f'Abwahl braucht Bereich und Grund: {name}: {item}')
                else:
                    excluded.append(match[1].strip())
        if not selected:
            errors.append(f'Keine Bereiche gewählt: {name}')
        used = selected + excluded
        unknown = set(used) - areas
        missing = areas - set(used)
        if unknown: errors.append(f'Unbekannte Bereiche: {name}: {", ".join(sorted(unknown))}')
        if missing: errors.append(f'Bereiche nicht eingeordnet: {name}: {", ".join(sorted(missing))}')
        if len(used) != len(set(used)): errors.append(f'Bereich doppelt/gewählt und abgewählt: {name}')
    return errors


def check(root=ROOT, ready=False, go=False):
    root = Path(root)
    errors = []
    for name in (*REQUIRED, *(f'docs/{d}.md' for d in DOCS)):
        if not (root / name).is_file():
            errors.append(f'Pflichtdatei fehlt: {name}')
    for legacy in ('.agents', '.claude', 'skills'):
        if (root / legacy).exists() or (root / legacy).is_symlink():
            errors.append(f'Parallele Profil-/Skill-Ablage nicht erlaubt: {legacy}')
    markdown = []
    for directory, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in {'.git', '.idea', '.venv', 'venv', 'node_modules', 'dist', 'build', '__pycache__'}
                   and not (Path(directory) / d).is_symlink()]
        markdown.extend(Path(directory) / f for f in files if f.endswith('.md'))
    for path in markdown:
        if path.is_symlink(): continue
        text = path.read_text()
        # Concrete root paths inside backticks, plus explicit markdown links.
        candidates = re.findall(r'`((?:harness|docs|tools|profiles|skills|ideas|specs|\.agents|\.claude)/[^`\s]+\.(?:md|py|sh|html|mjs))`', text)
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
    if (ready or go) and (root / 'harness/project.md').exists():
        text = (root / 'harness/project.md').read_text()
        for name in FIELDS:
            if unresolved(field(text, name)):
                errors.append(f'Init-Feld fehlt/offen: {name}')
        errors.extend(profile_errors(root, field(text, 'Profile')))
        if go:
            statuses = re.findall(r'^\*\*Status:\*\* (.+)$', text, re.M)
            if statuses != ['Init abgeschlossen']:
                errors.append('Init-Go: Status nicht eindeutig Init abgeschlossen')
            if unresolved(field(text, 'Init-Go')):
                errors.append('Init-Go fehlt/offen')
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
    parser.add_argument('--ready', action='store_true', help='Init-Voraussetzungen/Auswahl vor Go prüfen')
    parser.add_argument('--go', action='store_true', help='zusätzlich dokumentierten Init-Go/Status prüfen, keine fachliche Abnahme')
    args = parser.parse_args()
    errors = check(ready=args.ready, go=args.go)
    if errors:
        for error in errors:
            print('FEHLER:', error)
        raise SystemExit(1)
    print('Struktur konsistent' + ('; Init-Go dokumentiert (fachliche Wahrheit/Schreibrechte nicht geprüft)' if args.go else
          '; Init-Voraussetzungen eingetragen (fachliches Go separat)' if args.ready else ''))


if __name__ == '__main__':
    main()
