import unittest

import pandas as pd

from quant_flow.performance.benchmark import run_buy_and_hold

class BenchmarkTest(unittest.TestCase):
    def test_buy_once_and_hold(self):
        prices = pd.DataFrame(
            {
                "Open": [100.0, 110.0, 121.0, 121.0],
            }
        )

        result = run_buy_and_hold(
            prices,
            fee_rate=0.001,
            slippage_rate=0.001,
        )

        self.assertEqual(
            result["Position"].tolist(),
            [0, 1, 1, 1],
        )

        self.assertEqual(
            result["Turnover"].tolist(),
            [0, 1, 0, 0],
        )

        expected_equity = (1 - 0.002) * (121.0 / 110.0)

        self.assertAlmostEqual(
            result["Equity"].iloc[-1],
            expected_equity,
        )


if __name__ == "__main__":
    unittest.main()