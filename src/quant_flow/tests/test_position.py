import unittest
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from quant_flow.fills.fill import Fill
from quant_flow.orders.order import Order, OrderSide
from quant_flow.positions.position import Position


class PositionTest(unittest.TestCase):
    def make_fill(
        self,
        side: OrderSide,
        quantity: int,
        price: str,
    ) -> Fill:
        created_at = datetime(
            2026, 1, 5, 6, 0,
            tzinfo=timezone.utc,
        )

        order = Order(
            symbol="2330.TW",
            side=side,
            quantity=quantity,
            created_at=created_at,
        )

        return Fill(
            order=order,
            quantity=quantity,
            price=Decimal(price),
            fee=Decimal("0"),
            executed_at=created_at + timedelta(days=1),
        )

    def test_buy_updates_average_cost(self):
        original = Position(symbol="2330.TW")

        position = original.apply_fill(
            self.make_fill(OrderSide.BUY, 100, "100")
        )
        position = position.apply_fill(
            self.make_fill(OrderSide.BUY, 100, "120")
        )

        self.assertEqual(position.quantity, 200)
        self.assertEqual(position.average_cost, Decimal("110"))

        # 原本的空手物件保持不變。
        self.assertEqual(original.quantity, 0)
        self.assertEqual(original.average_cost, Decimal("0"))

    def test_sell_preserves_cost_until_flat(self):
        position = Position(
            symbol="2330.TW",
            quantity=200,
            average_cost=Decimal("110"),
        )

        position = position.apply_fill(
            self.make_fill(OrderSide.SELL, 50, "130")
        )

        self.assertEqual(position.quantity, 150)
        self.assertEqual(position.average_cost, Decimal("110"))

        position = position.apply_fill(
            self.make_fill(OrderSide.SELL, 150, "125")
        )

        self.assertEqual(position.quantity, 0)
        self.assertEqual(position.average_cost, Decimal("0"))

    def test_reject_overselling(self):
        position = Position(
            symbol="2330.TW",
            quantity=100,
            average_cost=Decimal("110"),
        )

        with self.assertRaisesRegex(ValueError, "不能超過"):
            position.apply_fill(
                self.make_fill(OrderSide.SELL, 101, "120")
            )


if __name__ == "__main__":
    unittest.main()