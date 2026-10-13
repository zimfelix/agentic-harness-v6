#!/bin/sh
# Synthetic end-to-end demo. Every step is a separate process using the same
# state file, so later steps prove that state survives a restart.
# Usage: sh examples/demo.sh   (writes only to .scratch/demo/ in the repo)
set -eu
cd "$(dirname "$0")/.."
DIR=.scratch/demo
rm -rf "$DIR" && mkdir -p "$DIR"
p() { echo "\$ planner $*"; python3 planner.py --data "$DIR/planner.json" --today 2026-10-10 "$@"; echo; }
fails() { echo "\$ planner $*   (expected to fail)"; if python3 planner.py --data "$DIR/planner.json" --today 2026-10-10 "$@"; then echo "UNEXPECTED SUCCESS"; exit 1; fi; echo; }

echo "== build two synthetic projects with a dependency chain"
p project add "Example Bakery Website" --description "Synthetic demo client"
p project add Admin
p task add p1 "Gather requirements" --priority high --estimate 2h
p task add p1 "Wireframes" --estimate 4h --after t1
p task add p1 "Write page copy" --estimate 3h --after t1
p task add p1 "Build pages" --estimate 10h --after t2,t3
p task add p1 "Launch" --priority critical --estimate 1h --due 2026-10-20 --after t4
p task add Admin "Collect receipts" --estimate 1h30m --due 2026-10-11
p task add Admin "File quarterly figures" --priority high --estimate 2h --due 2026-10-15 --after t6
p task add Admin "Update portfolio" --priority low

echo "== completion rules"
fails task done t4
p task done t1

echo "== fresh invocations read the saved state"
p overview
p blocked
p next

echo "== cycles are rejected"
fails task depend t2 t5
fails task depend t2 t2

echo "== deleting a referenced task is refused"
fails task delete t6

echo "== malformed import leaves the state intact"
cp "$DIR/planner.json" "$DIR/before.json"
printf '{"format": "local-planner", "schema_version": 1, "projects": [' > "$DIR/broken.json"
fails import "$DIR/broken.json" --replace
python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); d["tasks"][0]["depends_on"]=["t5"]; d["tasks"][1]["depends_on"].append("t99"); json.dump(d,open(sys.argv[2],"w"))' examples/sample-project.json "$DIR/cyclic.json"
fails import "$DIR/cyclic.json" --replace
cmp "$DIR/before.json" "$DIR/planner.json"
echo "state file byte-identical after failed imports" && echo

echo "== backup, damage, restore"
p backup
p export --out "$DIR/export-before.json"
p task done t6
p project delete Admin --yes --detach
printf 'garbage' > "$DIR/planner.json"
fails overview
p restore "$(ls "$DIR"/backups/*-manual.json)"
p export --out "$DIR/export-after.json"
cmp "$DIR/export-before.json" "$DIR/export-after.json"
echo "restored state identical to the state at backup time" && echo
p next --limit 10
