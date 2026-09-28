import unittest
from decimal import Decimal

import pandas as pd

from quant_flow.backtest.account_simulator import run_account_backtest
from quant_flow.orders.order import OrderSide


class AccountSimulatorTest(unittest.TestCase):
    def test_trade_timing_and_account_history(self):
        data = pd.DataFrame(
            {
                "Open": [100.0, 110.0, 121.0, 110.0, 220.0],
                "Close": [101.0, 112.0, 120.0, 111.0, 221.0],
                "Signal": [1, 1, 0, 0, 0],
            },
            index=pd.date_range(
                "2026-01-05",
                periods=5,
                freq="B",
                tz="Asia/Taipei",
            ),
        )

        history, fills = run_account_backtest(
            signals=data,
            symbol="2330.TW",
            initial_cash=Decimal("10000"),
        )

        self.assertEqual(
            history["Quantity"].tolist(),
            [0, 90, 90, 0, 0],
        )

        self.assertEqual(
            history["Cash"].tolist(),
            [10000.0, 100.0, 100.0, 10000.0, 10000.0],
        )

        self.assertEqual(
            history["Total_Equity"].tolist(),
            [10000.0, 10000.0, 10990.0, 10000.0, 10000.0],
        )

        self.assertEqual(len(fills), 2)
        self.assertEqual(fills[0].order.side, OrderSide.BUY)
        self.assertEqual(fills[1].order.side, OrderSide.SELL)

        self.assertEqual(
            fills[0].executed_at,
            history.index[1].to_pydatetime(),
        )
        self.assertEqual(
            fills[1].executed_at,
            history.index[3].to_pydatetime(),
        )

        self.assertAlmostEqual(history["Equity"].iloc[-1], 1.0)


if __name__ == "__main__":
    unittest.main()