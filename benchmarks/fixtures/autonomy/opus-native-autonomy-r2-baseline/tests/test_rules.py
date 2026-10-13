import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from planner import operations as ops  # noqa: E402
from planner.model import Plan, PlannerError, parse_estimate, validate_plan  # noqa: E402
from planner.planning import rank_key, suggest  # noqa: E402

TODAY = date(2026, 10, 10)


def plan_with(*specs):
    plan = Plan()
    ops.add_project(plan, "p", "P")
    for fields in specs:
        ops.add_task(plan, "p", "t", **fields)
    return plan


class RuleTests(unittest.TestCase):
    def test_cycle_and_self_dependency_rejected(self):
        plan = plan_with({}, {}, {})
        ops.add_dependency(plan, 2, 1)
        ops.add_dependency(plan, 3, 2)
        with self.assertRaisesRegex(PlannerError, "cycle"):
            ops.add_dependency(plan, 1, 3)
        with self.assertRaisesRegex(PlannerError, "itself"):
            ops.add_dependency(plan, 1, 1)
        self.assertEqual(plan.tasks[1].depends_on, set())
        validate_plan(plan)

    def test_validate_detects_cycle_in_raw_data(self):
        plan = plan_with({}, {})
        plan.tasks[1].depends_on = {2}
        plan.tasks[2].depends_on = {1}
        with self.assertRaisesRegex(PlannerError, "cycle"):
            validate_plan(plan)

    def test_completion_guard_and_reopen_guard(self):
        plan = plan_with({}, {"depends_on": [1]})
        with self.assertRaisesRegex(PlannerError, "blocked by unfinished #1"):
            ops.complete(plan, 2)
        ops.complete(plan, 1)
        ops.complete(plan, 2)
        with self.assertRaisesRegex(PlannerError, "reopen them first"):
            ops.reopen(plan, 1)

    def test_delete_refuses_then_detaches(self):
        plan = plan_with({}, {"depends_on": [1]})
        with self.assertRaisesRegex(PlannerError, "still required by #2"):
            ops.delete_task(plan, 1)
        self.assertEqual(ops.delete_task(plan, 1, detach=True), [(2, 1)])
        validate_plan(plan)

    def test_estimates(self):
        self.assertEqual([parse_estimate(v) for v in ("90m", "1.5h", "2h30m", "2")],
                         [90, 90, 150, 120])
        for bad in ("", "abc", "-1h", "5d"):
            with self.assertRaises(PlannerError):
                parse_estimate(bad)

    def test_rank_order_criteria(self):
        plan = plan_with(
            {"priority": "urgent"},                       # 1
            {"priority": "low", "due": "2026-10-09"},     # 2 overdue beats priority
            {"priority": "urgent", "due": "2026-10-30"},  # 3 dated before undated
            {"priority": "high", "estimate_minutes": 30},  # 4 smaller estimate first
            {"priority": "high", "estimate_minutes": 60},  # 5
            {"priority": "high", "estimate_minutes": 90},  # 6 unblocks #7 -> before 4/5
            {"depends_on": [6]},                          # 7 blocked
        )
        self.assertEqual([t.id for t in suggest(plan, TODAY)], [2, 3, 1, 6, 4, 5])
        self.assertLess(rank_key(plan, plan.tasks[4], TODAY), rank_key(plan, plan.tasks[5], TODAY))

    def test_suggest_excludes_blocked_and_done(self):
        plan = plan_with({}, {"depends_on": [1]}, {})
        ops.complete(plan, 3)
        self.assertEqual([t.id for t in suggest(plan, TODAY)], [1])


if __name__ == "__main__":
    unittest.main()
