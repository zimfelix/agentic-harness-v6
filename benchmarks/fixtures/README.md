# Synthetic generated products — evidence, not template content

These are product extracts from the frozen comparison, kept so acceptance can be replayed WITHOUT another model call. All data/tokens/providers are test-only. No sessions, credentials or global agent configuration are included. One machine-local backup path in a saved demo-output JSON was replaced with `<temporary-demo-directory>` for publication; executable product code is unchanged.

- `stress/`: initial CRM/import/dispatch code; CRM uses the saved pre-change code. Both dispatch repetitions retained, including the first lean failure. Specs in dispatch extracts may contain the later intentionally blocked provider criterion; source code was unchanged by that phase.
- `autonomy/`: corrected-environment Sol/Opus work planners. Executable modes preserved.

Unchanged harness resources, project instructions and global data are deliberately omitted. References to omitted harness files in extracted docs are NOT delivery defects; consult the frozen manifests/original repository for those resources. The fixtures themselves are not copied by `tools/export.py`.

```sh
# 40 independent planner outcomes, all own suites, no model calls:
PYTHONDONTWRITEBYTECODE=1 python3 benchmarks/verify_planners.py --output /tmp/planner-results.json

# A selected stress sample, no model calls:
PYTHONDONTWRITEBYTECODE=1 python3 benchmarks/oracle.py dispatch \
  benchmarks/fixtures/stress/sol-dispatch-r1-lean /tmp/dispatch-acceptance --seed 1
```

Oracle exits nonzero for failures OR incomplete evidence. Inspect `outcome`: dispatch has two intentionally `inconclusive` coverage areas, not product failures. First lean dispatch additionally has one actual provider-conflict/status failure; do not 'fix' this fixture to change history.

The products are examples, not audited production libraries. Python 3.14.7/Node 26.8.1/macOS were the actual test environment; full OS/runtime matrices and real providers were not validated.
