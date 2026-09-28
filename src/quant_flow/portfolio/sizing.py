from decimal import Decimal

def calculate_buy_quantity(
    cash: Decimal,
    open_price: Decimal,
    fee_rate: Decimal = Decimal("0"),
    slippage_rate: Decimal = Decimal("0"),
) -> int:
    if (
        not isinstance(cash, Decimal)
        or not cash.is_finite()
        or cash < 0
    ):
        raise ValueError("現金必須是有限且非負的 Decimal")

    if (
        not isinstance(open_price, Decimal)
        or not open_price.is_finite()
        or open_price <= 0
    ):
        raise ValueError("開盤價必須是有限且大於零的 Decimal")

    for name, rate in [
        ("手續費率", fee_rate),
        ("滑價率", slippage_rate),
    ]:
        if (
            not isinstance(rate, Decimal)
            or not rate.is_finite()
            or not Decimal("0") <= rate < Decimal("1")
        ):
            raise ValueError(f"{name}必須是介於 0 到 1 之間的 Decimal")

    execution_price = open_price * (1 + slippage_rate)
    cash_per_share = execution_price * (1 + fee_rate)

    quantity = int(cash // cash_per_share)

    # 使用與成交器相同的金額計算順序，檢查邊界。
    def required_cash(shares: int) -> Decimal:
        gross_amount = execution_price * shares
        return gross_amount + gross_amount * fee_rate

    while quantity > 0 and required_cash(quantity) > cash:
        quantity -= 1

    while required_cash(quantity + 1) <= cash:
        quantity += 1

    return quantity