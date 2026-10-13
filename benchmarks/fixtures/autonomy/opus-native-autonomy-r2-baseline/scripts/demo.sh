#!/bin/sh
# Synthetic end-to-end demo on a throwaway database in .demo/ (inside the project).
set -u
cd "$(dirname "$0")/.."
rm -rf .demo && mkdir .demo
export PLANNER_DB=.demo/planner.db
P=./planner
TODAY=2026-10-10
step() { printf '\n### %s\n' "$*"; }
same() { if cmp -s "$1" "$2"; then echo "CHECK OK: state identical"; else echo "CHECK FAILED: state differs"; exit 1; fi; }
snap() { $P export - | grep -v exported_at > "$1"; }

step "1. import the synthetic fixture (2 projects, 7 tasks, chain 1->2->3->4, #1 done)"
$P import examples/synthetic-portfolio.json
$P task add dash-tool "Write user notes" --estimate 45m --after 7

step "2. fresh invocation reads saved state: overview"
$P overview --today $TODAY

step "3. blocked tasks cannot be completed"
$P blocked
$P task done 3; echo "exit=$?"

step "4. cycle is rejected (#2 waiting for #4 would close 2->3->4->2)"
$P dep add 2 4; echo "exit=$?"

step "5. next suggestion: only ready tasks (no blocked, no done)"
$P next --today $TODAY --limit 10

step "6. malformed import leaves state intact"
snap .demo/before.json
printf '{"format": "local-work-planner", "version": 1, "projects": [], "tasks": [{"id": 1, "project": "nope"' > .demo/broken.json
$P import .demo/broken.json; echo "exit=$?"
$P import examples/synthetic-portfolio.json; echo "exit=$?  (re-import of existing projects)"
snap .demo/after.json; same .demo/before.json .demo/after.json

step "7. backup, change things, restore the same state"
$P backup .demo/backup.json
$P task done 2
$P task delete 8
$P restore .demo/backup.json --yes
snap .demo/restored.json; same .demo/before.json .demo/restored.json

step "8. completing work moves the suggestion along"
$P task done 2
$P next --today $TODAY --project bakery-site
