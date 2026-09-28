import unittest
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from quant_flow.backtest.execution import execute_target_position
from quant_flow.orders.order import OrderSide
from quant_flow.portfolio.portfolio import Portfolio


class ExecutionTest(unittest.TestCase):
    def test_enter_hold_and_exit(self):
        portfolio = Portfolio(cash=Decimal("10000"))
        opened_at = datetime(
            2026, 1, 6, 1, 0,
            tzinfo=timezone.utc,
        )

        buy = execute_target_position(
            portfolio=portfolio,
            symbol="2330.TW",
            target=1,
            open_price=Decimal("100"),
            opened_at=opened_at,
        )

        self.assertIsNotNone(buy)
        self.assertEqual(buy.order.side, OrderSide.BUY)
        self.assertEqual(buy.quantity, 100)
        self.assertEqual(portfolio.cash, Decimal("0"))

        hold = execute_target_position(
            portfolio=portfolio,
            symbol="2330.TW",
            target=1,
            open_price=Decimal("105"),
            opened_at=opened_at + timedelta(days=1),
        )

        self.assertIsNone(hold)
        self.assertEqual(
            portfolio.positions["2330.TW"].quantity,
            100,
        )

        sell = execute_target_position(
            portfolio=portfolio,
            symbol="2330.TW",
            target=0,
            open_price=Decimal("110"),
            opened_at=opened_at + timedelta(days=2),
        )

        self.assertIsNotNone(sell)
        self.assertEqual(sell.order.side, OrderSide.SELL)
        self.assertEqual(portfolio.cash, Decimal("11000"))
        self.assertEqual(
            portfolio.positions["2330.TW"].quantity,
            0,
        )

    def test_skip_when_cash_is_insufficient_for_one_share(self):
        portfolio = Portfolio(cash=Decimal("50"))

        fill = execute_target_position(
            portfolio=portfolio,
            symbol="2330.TW",
            target=1,
            open_price=Decimal("100"),
            opened_at=datetime(
                2026, 1, 6, 1, 0,
                tzinfo=timezone.utc,
            ),
        )

        self.assertIsNone(fill)
        self.assertEqual(portfolio.cash, Decimal("50"))
        self.assertEqual(portfolio.positions, {})


if __name__ == "__main__":
    unittest.main()