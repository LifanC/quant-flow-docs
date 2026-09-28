import unittest
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from quant_flow.fills.fill import Fill
from quant_flow.orders.order import Order, OrderSide


class FillTest(unittest.TestCase):
    def setUp(self):
        self.created_at = datetime(
            2026, 1, 5, 6, 0,
            tzinfo=timezone.utc,
        )
        self.executed_at = self.created_at + timedelta(days=1)

    def make_order(self, side: OrderSide) -> Order:
        return Order(
            symbol="2330.TW",
            side=side,
            quantity=100,
            created_at=self.created_at,
        )

    def test_cash_change(self):
        cases = [
            (OrderSide.BUY, Decimal("-10010")),
            (OrderSide.SELL, Decimal("9990")),
        ]

        for side, expected in cases:
            with self.subTest(side=side):
                fill = Fill(
                    order=self.make_order(side),
                    quantity=100,
                    price=Decimal("100"),
                    fee=Decimal("10"),
                    executed_at=self.executed_at,
                )

                self.assertEqual(
                    fill.gross_amount,
                    Decimal("10000"),
                )
                self.assertEqual(fill.cash_change, expected)

    def test_reject_quantity_above_order(self):
        with self.assertRaisesRegex(ValueError, "成交股數"):
            Fill(
                order=self.make_order(OrderSide.BUY),
                quantity=101,
                price=Decimal("100"),
                fee=Decimal("10"),
                executed_at=self.executed_at,
            )

    def test_reject_execution_before_order(self):
        with self.assertRaisesRegex(ValueError, "不能早於"):
            Fill(
                order=self.make_order(OrderSide.BUY),
                quantity=100,
                price=Decimal("100"),
                fee=Decimal("10"),
                executed_at=self.created_at - timedelta(seconds=1),
            )


if __name__ == "__main__":
    unittest.main()