import unittest
from decimal import Decimal

from quant_flow.portfolio.sizing import calculate_buy_quantity

class SizingTest(unittest.TestCase):
    def test_exact_budget_without_costs(self):
        quantity = calculate_buy_quantity(
            cash=Decimal("10000"),
            open_price=Decimal("100"),
        )

        self.assertEqual(quantity, 100)

    def test_quantity_accounts_for_costs(self):
        cash = Decimal("10000")
        fee_rate = Decimal("0.001")
        slippage_rate = Decimal("0.001")

        quantity = calculate_buy_quantity(
            cash=cash,
            open_price=Decimal("100"),
            fee_rate=fee_rate,
            slippage_rate=slippage_rate,
        )

        self.assertEqual(quantity, 99)

        execution_price = Decimal("100") * (1 + slippage_rate)

        gross_amount = execution_price * quantity
        required_cash = gross_amount + gross_amount * fee_rate

        next_gross_amount = execution_price * (quantity + 1)
        next_required_cash = (
            next_gross_amount + next_gross_amount * fee_rate
        )

        self.assertLessEqual(required_cash, cash)
        self.assertGreater(next_required_cash, cash)

    def test_cannot_afford_one_share(self):
        quantity = calculate_buy_quantity(
            cash=Decimal("50"),
            open_price=Decimal("100"),
        )

        self.assertEqual(quantity, 0)


if __name__ == "__main__":
    unittest.main()