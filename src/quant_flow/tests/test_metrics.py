import unittest

import pandas as pd

from quant_flow.performance.metrics import (
    calculate_drawdown,
    calculate_metrics,
)

class MetricsTest(unittest.TestCase):
    def test_return_and_drawdown(self):
        equity = pd.Series([1.0, 1.2, 0.9, 1.1])

        metrics = calculate_metrics(equity)

        self.assertAlmostEqual(metrics["total_return"], 0.1)
        self.assertAlmostEqual(metrics["max_drawdown"], -0.25)

    def test_initial_loss_counts_as_drawdown(self):
        equity = pd.Series([0.98, 0.99])

        metrics = calculate_metrics(equity)

        self.assertAlmostEqual(metrics["total_return"], -0.01)
        self.assertAlmostEqual(metrics["max_drawdown"], -0.02)

    def test_drawdown_series(self):
        equity = pd.Series([1.0, 1.2, 0.9, 1.1, 1.3])

        actual = calculate_drawdown(equity)

        expected = pd.Series([
            0.0,
            0.0,
            -0.25,
            1.1 / 1.2 - 1,
            0.0,
        ])

        pd.testing.assert_series_equal(
            actual,
            expected,
            check_exact=False,
            rtol=1e-10,
            atol=1e-12,
        )


if __name__ == "__main__":
    unittest.main()