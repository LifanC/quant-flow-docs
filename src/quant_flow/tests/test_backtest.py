import unittest

import pandas as pd

from quant_flow.backtest.simulator import run_backtest

class BacktestTest(unittest.TestCase):
    def test_trade_timing(self):
        signals = pd.DataFrame(
            {
                "Open": [100.0, 110.0, 121.0, 110.0, 220.0],
                "Signal": [1, 1, 0, 0, 0],
            }
        )

        result = run_backtest(signals)

        self.assertEqual(
            result["Position"].tolist(),
            [0, 1, 1, 0, 0],
        )

        expected_returns = [
            0.0,
            0.0,
            121.0 / 110.0 - 1,
            110.0 / 121.0 - 1,
            0.0,
        ]

        for actual, expected in zip(
            result["Strategy_Return"],
            expected_returns,
        ):
            self.assertAlmostEqual(actual, expected)

        self.assertAlmostEqual(
            result["Equity"].iloc[-1],
            1.0,
        )

    def test_transaction_costs(self):
        signals = pd.DataFrame(
            {
                "Open": [100.0, 110.0, 121.0, 110.0, 220.0],
                "Signal": [1, 1, 0, 0, 0],
            }
        )

        result = run_backtest(
            signals,
            fee_rate=0.001,
            slippage_rate=0.001,
        )

        self.assertEqual(
            result["Turnover"].tolist(),
            [0, 1, 0, 1, 0],
        )

        # 買賣價格相同，但進出各扣一次 0.2% 成本。
        expected_equity = (1 - 0.002) ** 2

        self.assertAlmostEqual(
            result["Equity"].iloc[-1],
            expected_equity,
        )


if __name__ == "__main__":
    unittest.main()