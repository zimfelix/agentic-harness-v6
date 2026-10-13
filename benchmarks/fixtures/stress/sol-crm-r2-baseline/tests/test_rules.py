import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ledger.rules import Problem, integer, tax_cents, transition


class RuleTests(unittest.TestCase):
    def test_integer_types_and_bounds(self):
        for value in (False, True, 0.0, "0", None, [], -1, 101):
            with self.subTest(value=value), self.assertRaises(Problem) as failure:
                integer(value, 0, 100)
            self.assertEqual(failure.exception.status, 400)
        for value in (0, 100):
            self.assertEqual(integer(value, 0, 100), value)

    def test_half_up(self):
        cases = ((1, 4999, 0), (1, 5000, 1), (1, 5001, 1),
                 (3, 5000, 2), (101, 1900, 19), (0, 10000, 0),
                 (100000000, 10000, 100000000), (12345, 0, 0))
        for net, bps, expected in cases:
            with self.subTest(net=net, bps=bps):
                self.assertEqual(tax_cents(net, bps), expected)

    def test_complete_state_graph(self):
        allowed = {("new", "qualified"), ("qualified", "won"), ("qualified", "lost")}
        for current in ("new", "qualified", "won", "lost"):
            for target in ("new", "qualified", "won", "lost", "unknown", ""):
                with self.subTest(current=current, target=target):
                    if (current, target) in allowed:
                        transition(current, target)
                    else:
                        with self.assertRaises(Problem) as failure:
                            transition(current, target)
                        self.assertEqual(failure.exception.status, 409)
