---
name: testing
description: Plan, write and review tests that prove behaviour at real boundaries instead of mirroring the implementation. Use when planning or adding tests, deciding on TDD or mocks, reviewing a suite, or when tests pass but the feature may still be broken.
---

# Tests that prove behaviour

A good test fails when the feature breaks and stays green when the code is refactored without changing behaviour. Test what a user or caller observes at a public boundary: CLI output, API response, written file, UI state, emitted event.

## Choose the smallest convincing set

| Level | Use when | Does not prove alone |
|---|---|---|
| Unit | pure logic, branches, calculations, parsers | integration with files, DB, network, UI |
| Integration | real persistence, processes, files, several components | the full user flow |
| Contract | two sides of an API, format or event must stay compatible | internal correctness of either side |
| End-to-end / smoke | the main flow must work across the real boundaries | rare failure paths |

At least one check sits at the boundary where the user experiences the feature. Add failure-path tests only for risks that exist (bad input, data loss, permissions, timeouts). Lint, typecheck, build and coverage are supporting signals, not behaviour proof. No empty suites or tests for trivial getters/config.

## Mocks and test doubles

- Allowed at boundaries you do not own or cannot run cheaply: network, paid/external APIs, audio, clock, randomness, OS dialogs, hardware.
- Prefer real local equivalents: temp directories, SQLite, a local server, the real CLI as a subprocess.
- Never mock your own modules to make a test possible or green. Do not assert private functions or internal call order. If a double is used, state in one line what the test therefore does not prove.

## Red flags: tests that only test the code

- The test repeats the implementation step by step, or breaks on a rename/refactor with unchanged behaviour.
- It checks that a mock was called, but not the observable outcome.
- Expected values were copied from the current output without checking that the output is correct. Pinning an exact external contract (command line, file format, protocol message) is fine when the test name says so; it still does not prove the effect (e.g. that a sound plays).
- A failing test was edited to match new behaviour without asking whether the new behaviour is wanted.
- Only the happy path, or a coverage number as the goal.

## TDD: when it pays off

- **Always for bugs:** reproduce the bug as a failing test at the real boundary first, then fix.
- **Good fit:** clearly specified, quickly testable behaviour (rules, parsers, data transformations, API contracts).
- **Skip test-first** for exploratory work, visual design or prototypes; add a behaviour test once the shape is settled.
- Challenge every new test once: break the code or revert the fix and confirm the test fails for the right reason.

## Token budget

Run the tests for the changed behaviour first; run the full suite before handoff or after changes to shared foundations. Keep passing output compact and read only failures. Change the hypothesis after repeated failures instead of rerunning.

## Stop and discuss instead of forcing it

- A test is only possible with heavy mocking of own code: that is a design signal; propose a seam or a real local dependency.
- Acceptance is unclear or a failing test contradicts the spec: ask, do not silently adapt the test.
- Two hypotheses failed: report what was tried and the blocker.

## Manual checks

Name exactly what only a human can verify (visual result, sound, real device, third-party UI), record steps and expected result, and never report it as passed without confirmation.
