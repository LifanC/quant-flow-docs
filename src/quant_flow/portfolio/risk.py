from quant_flow.fills.fill import Fill
from quant_flow.orders.order import OrderSide
from quant_flow.portfolio.portfolio import Portfolio


def validate_fill(
    portfolio: Portfolio,
    fill: Fill,
) -> None:
    if fill.order.side == OrderSide.BUY:
        required_cash = -fill.cash_change

        if required_cash > portfolio.cash:
            raise ValueError(
                f"資金不足：需要 {required_cash}，"
                f"目前只有 {portfolio.cash}"
            )

    else:
        position = portfolio.positions.get(fill.order.symbol)
        available_quantity = (
            position.quantity if position is not None else 0
        )

        if fill.quantity > available_quantity:
            raise ValueError(
                f"持倉不足：要賣出 {fill.quantity} 股，"
                f"目前只有 {available_quantity} 股"
            )