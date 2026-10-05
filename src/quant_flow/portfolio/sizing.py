from decimal import Decimal

from quant_flow.validation import validate_decimal

def calculate_buy_quantity(
    cash: Decimal,
    open_price: Decimal,
    fee_rate: Decimal = Decimal("0"),
    slippage_rate: Decimal = Decimal("0"),
) -> int:
    """計算包含買方滑價與手續費後，現金可負擔的最大整數股數。

    先按每股成本估算，再以成交器的運算順序校正 Decimal 邊界。
    兩個校正迴圈不可直接刪除，否則有限精度可能導致超買或少買一股。"""
    validate_decimal(
        cash, "現金必須是有限且非負的 Decimal",
    )

    validate_decimal(
        open_price, "開盤價必須是有限且大於零的 Decimal", positive=True,
    )

    for name, rate in [
        ("手續費率", fee_rate),
        ("滑價率", slippage_rate),
    ]:
        validate_decimal(rate, f"{name}必須是介於 0 到 1 之間的 Decimal", below_one=True)

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
