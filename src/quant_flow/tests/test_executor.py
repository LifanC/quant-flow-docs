import unittest
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from quant_flow.orders.executor import execute_market_order
from quant_flow.orders.order import Order, OrderSide
from quant_flow.portfolio.portfolio import Portfolio


class ExecutorTest(unittest.TestCase):
    def setUp(self):
        self.created_at = datetime(
            2026, 1, 5, 6, 0,
            tzinfo=timezone.utc,
        )
        self.executed_at = (
            self.created_at + timedelta(hours=19)
        )

    def make_order(self, side: OrderSide) -> Order:
        return Order(
            symbol="2330.TW",
            side=side,
            quantity=100,
            created_at=self.created_at,
        )

    def execute(
        self,
        portfolio: Portfolio,
        side: OrderSide,
    ):
        return execute_market_order(
            portfolio=portfolio,
            order=self.make_order(side),
            open_price=Decimal("100"),
            executed_at=self.executed_at,
            fee_rate=Decimal("0.001"),
            slippage_rate=Decimal("0.001"),
        )

    def test_buy_updates_account(self):
        portfolio = Portfolio(cash=Decimal("20000"))

        fill = self.execute(portfolio, OrderSide.BUY)

        self.assertEqual(fill.quantity, 100)
        self.assertEqual(portfolio.cash, Decimal("9979.99"))
        self.assertEqual(
            portfolio.positions["2330.TW"].quantity,
            100,
        )
        self.assertEqual(
            portfolio.positions["2330.TW"].average_cost,
            Decimal("100.1"),
        )

    def test_reject_buy_when_costs_exceed_cash(self):
        portfolio = Portfolio(cash=Decimal("10000"))

        with self.assertRaisesRegex(ValueError, "資金不足"):
            self.execute(portfolio, OrderSide.BUY)

        self.assertEqual(portfolio.cash, Decimal("10000"))
        self.assertEqual(portfolio.positions, {})

    def test_reject_sell_without_position(self):
        portfolio = Portfolio(cash=Decimal("20000"))

        with self.assertRaisesRegex(ValueError, "持倉不足"):
            self.execute(portfolio, OrderSide.SELL)

        self.assertEqual(portfolio.cash, Decimal("20000"))
        self.assertEqual(portfolio.positions, {})


if __name__ == "__main__":
    unittest.main()