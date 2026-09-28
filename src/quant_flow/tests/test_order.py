import unittest
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

from quant_flow.orders.order import Order, OrderSide


class OrderTest(unittest.TestCase):
    def test_create_buy_order(self):
        order = Order(
            symbol="2330.TW",
            side=OrderSide.BUY,
            quantity=100,
            created_at=datetime(
                2026, 1, 5, 6, 0,
                tzinfo=timezone.utc,
            ),
        )

        self.assertEqual(order.symbol, "2330.TW")
        self.assertEqual(order.side, OrderSide.BUY)
        self.assertEqual(order.quantity, 100)

        with self.assertRaises(FrozenInstanceError):
            order.quantity = 200

    def test_reject_invalid_quantity(self):
        for quantity in [0, -1, 1.5, True]:
            with self.subTest(quantity=quantity):
                with self.assertRaisesRegex(ValueError, "正整數"):
                    Order(
                        symbol="2330.TW",
                        side=OrderSide.BUY,
                        quantity=quantity,
                        created_at=datetime.now(timezone.utc),
                    )

    def test_reject_time_without_timezone(self):
        with self.assertRaisesRegex(ValueError, "時區"):
            Order(
                symbol="2330.TW",
                side=OrderSide.BUY,
                quantity=100,
                created_at=datetime(2026, 1, 5, 14, 0),
            )


if __name__ == "__main__":
    unittest.main()