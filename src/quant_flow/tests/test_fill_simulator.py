import unittest
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from quant_flow.fills.simulator import simulate_market_order
from quant_flow.orders.order import Order, OrderSide


class FillSimulatorTest(unittest.TestCase):
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

    def test_buy_price_and_fee(self):
        fill = simulate_market_order(
            order=self.make_order(OrderSide.BUY),
            open_price=Decimal("100"),
            executed_at=self.executed_at,
            fee_rate=Decimal("0.001"),
            slippage_rate=Decimal("0.001"),
        )

        self.assertEqual(fill.quantity, 100)
        self.assertEqual(fill.price, Decimal("100.1"))
        self.assertEqual(fill.fee, Decimal("10.01"))
        self.assertEqual(
            fill.cash_change,
            Decimal("-10020.01"),
        )

    def test_sell_price_and_fee(self):
        fill = simulate_market_order(
            order=self.make_order(OrderSide.SELL),
            open_price=Decimal("100"),
            executed_at=self.executed_at,
            fee_rate=Decimal("0.001"),
            slippage_rate=Decimal("0.001"),
        )

        self.assertEqual(fill.price, Decimal("99.9"))
        self.assertEqual(fill.fee, Decimal("9.99"))
        self.assertEqual(
            fill.cash_change,
            Decimal("9980.01"),
        )

    def test_reject_execution_before_order(self):
        with self.assertRaisesRegex(ValueError, "不能早於"):
            simulate_market_order(
                order=self.make_order(OrderSide.BUY),
                open_price=Decimal("100"),
                executed_at=self.created_at - timedelta(seconds=1),
            )


if __name__ == "__main__":
    unittest.main()