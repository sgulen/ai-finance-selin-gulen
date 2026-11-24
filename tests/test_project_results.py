import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from project_results import build_scenario


class ProjectResultsTests(unittest.TestCase):
    def test_equal_weight_is_equal_and_fully_invested(self):
        equal_weight = build_scenario()["portfolios"][0]
        self.assertAlmostEqual(sum(equal_weight["weights"].values()), 1.0)
        self.assertEqual(set(equal_weight["weights"].values()), {0.25})

    def test_benchmark_uses_declared_weights(self):
        benchmark = build_scenario()["portfolios"][1]
        self.assertEqual(benchmark["weights"]["LQD"], 0.40)
        self.assertEqual(benchmark["weights"]["ACWI"], 0.60)
        self.assertAlmostEqual(sum(benchmark["weights"].values()), 1.0)

    def test_known_answer_from_bundled_prices(self):
        constrained = build_scenario()["portfolios"][2]
        self.assertAlmostEqual(constrained["weights"]["BIL"], 0.60)
        self.assertAlmostEqual(constrained["weights"]["IEF"], 0.00)
        self.assertAlmostEqual(constrained["weights"]["LQD"], 0.00)
        self.assertAlmostEqual(constrained["weights"]["ACWI"], 0.40)
        self.assertEqual(constrained["verdict"], "PASS")

    def test_impossible_objective_has_no_feasible_portfolio(self):
        constrained = build_scenario(objective=1.0)["portfolios"][2]
        self.assertEqual(constrained["verdict"], "FAIL")
        self.assertFalse(constrained["weights"])


if __name__ == "__main__":
    unittest.main()
