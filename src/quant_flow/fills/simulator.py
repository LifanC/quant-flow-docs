from datetime import datetime
from decimal import Decimal

from quant_flow.fills.fill import Fill
from quant_flow.orders.order import Order, OrderSide


def simulate_market_order(
    order: Order,
    open_price: Decimal,
    executed_at: datetime,
    fee_rate: Decimal = Decimal("0"),
    slippage_rate: Decimal = Decimal("0"),
) -> Fill:
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
            raise ValueError(
                f"{name}必須是介於 0（含）到 1（不含）的 Decimal"
            )

    if not isinstance(executed_at, datetime):
        raise ValueError("成交時間必須是 datetime")

    if executed_at.utcoffset() is None:
        raise ValueError("成交時間必須包含時區")

    if executed_at < order.created_at:
        raise ValueError("成交時間不能早於委託時間")

    if order.side == OrderSide.BUY:
        price = open_price * (1 + slippage_rate)
    else:
        price = open_price * (1 - slippage_rate)

    gross_amount = price * order.quantity
    fee = gross_amount * fee_rate

    return Fill(
        order=order,
        quantity=order.quantity,
        price=price,
        fee=fee,
        executed_at=executed_at,
    )