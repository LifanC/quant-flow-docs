from datetime import datetime
from decimal import Decimal

from quant_flow.fills.fill import Fill
from quant_flow.orders.executor import execute_market_order
from quant_flow.orders.order import Order, OrderSide
from quant_flow.portfolio.portfolio import Portfolio
from quant_flow.portfolio.sizing import calculate_buy_quantity


def execute_target_position(
    portfolio: Portfolio,
    symbol: str,
    target: int,
    open_price: Decimal,
    opened_at: datetime,
    fee_rate: Decimal = Decimal("0"),
    slippage_rate: Decimal = Decimal("0"),
) -> Fill | None:
    if type(target) is not int or target not in (0, 1):
        raise ValueError("目標持倉必須是整數 0 或 1")

    position = portfolio.positions.get(symbol)
    held_quantity = (
        position.quantity if position is not None else 0
    )

    if target == 1:
        if held_quantity > 0:
            return None

        quantity = calculate_buy_quantity(
            cash=portfolio.cash,
            open_price=open_price,
            fee_rate=fee_rate,
            slippage_rate=slippage_rate,
        )

        if quantity == 0:
            return None

        side = OrderSide.BUY

    else:
        if held_quantity == 0:
            return None

        quantity = held_quantity
        side = OrderSide.SELL

    order = Order(
        symbol=symbol,
        side=side,
        quantity=quantity,
        created_at=opened_at,
    )

    return execute_market_order(
        portfolio=portfolio,
        order=order,
        open_price=open_price,
        executed_at=opened_at,
        fee_rate=fee_rate,
        slippage_rate=slippage_rate,
    )