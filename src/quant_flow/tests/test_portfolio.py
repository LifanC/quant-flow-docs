import unittest
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from quant_flow.fills.fill import Fill
from quant_flow.orders.order import Order, OrderSide
from quant_flow.portfolio.portfolio import Portfolio


class PortfolioTest(unittest.TestCase):
    def make_fill(
        self,
        side: OrderSide,
        quantity: int,
        price: str,
        fee: str = "10",
    ) -> Fill:
        created_at = datetime(
            2026, 1, 5, 6, 0,
            tzinfo=timezone.utc,
        )

        return Fill(
            order=Order(
                symbol="2330.TW",
                side=side,
                quantity=quantity,
                created_at=created_at,
            ),
            quantity=quantity,
            price=Decimal(price),
            fee=Decimal(fee),
            executed_at=created_at + timedelta(days=1),
        )

    def test_buy_and_sell_update_account(self):
        portfolio = Portfolio(cash=Decimal("20000"))

        portfolio.apply_fill(
            self.make_fill(OrderSide.BUY, 100, "100")
        )

        self.assertEqual(portfolio.cash, Decimal("9990"))
        self.assertEqual(
            portfolio.positions["2330.TW"].quantity,
            100,
        )

        portfolio.apply_fill(
            self.make_fill(OrderSide.SELL, 100, "110")
        )

        self.assertEqual(portfolio.cash, Decimal("20980"))
        self.assertEqual(
            portfolio.positions["2330.TW"].quantity,
            0,
        )

    def test_insufficient_cash_keeps_account_unchanged(self):
        portfolio = Portfolio(cash=Decimal("10000"))

        # 股款 10000，加上費用 10，超過可用現金。
        with self.assertRaisesRegex(ValueError, "現金不足"):
            portfolio.apply_fill(
                self.make_fill(OrderSide.BUY, 100, "100")
            )

        self.assertEqual(portfolio.cash, Decimal("10000"))
        self.assertEqual(portfolio.positions, {})

    def test_overselling_keeps_account_unchanged(self):
        portfolio = Portfolio(cash=Decimal("20000"))

        portfolio.apply_fill(
            self.make_fill(OrderSide.BUY, 100, "100")
        )

        original_cash = portfolio.cash
        original_position = portfolio.positions["2330.TW"]

        with self.assertRaisesRegex(ValueError, "不能超過"):
            portfolio.apply_fill(
                self.make_fill(OrderSide.SELL, 101, "110")
            )

        self.assertEqual(portfolio.cash, original_cash)
        self.assertEqual(
            portfolio.positions["2330.TW"],
            original_position,
        )

    def test_equity_uses_current_price(self):
        portfolio = Portfolio(cash=Decimal("20000"))

        portfolio.apply_fill(
            self.make_fill(OrderSide.BUY, 100, "100")
        )

        prices = {"2330.TW": Decimal("110")}

        self.assertEqual(
            portfolio.market_value(prices),
            Decimal("11000"),
        )
        self.assertEqual(
            portfolio.total_equity(prices),
            Decimal("20990"),
        )

        # 估值不應修改現金或平均成本。
        self.assertEqual(portfolio.cash, Decimal("9990"))
        self.assertEqual(
            portfolio.positions["2330.TW"].average_cost,
            Decimal("100"),
        )

    def test_reject_missing_price_for_open_position(self):
        portfolio = Portfolio(cash=Decimal("20000"))

        portfolio.apply_fill(
            self.make_fill(OrderSide.BUY, 100, "100")
        )

        with self.assertRaisesRegex(ValueError, "缺少 2330"):
            portfolio.total_equity({})

    def test_closed_position_does_not_require_price(self):
        portfolio = Portfolio(cash=Decimal("20000"))

        portfolio.apply_fill(
            self.make_fill(OrderSide.BUY, 100, "100")
        )
        portfolio.apply_fill(
            self.make_fill(OrderSide.SELL, 100, "110")
        )

        self.assertEqual(
            portfolio.market_value({}),
            Decimal("0"),
        )
        self.assertEqual(
            portfolio.total_equity({}),
            Decimal("20980"),
        )


if __name__ == "__main__":
    unittest.main()