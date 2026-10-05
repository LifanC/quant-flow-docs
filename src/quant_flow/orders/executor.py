from datetime import datetime
from decimal import Decimal

from quant_flow.fills.fill import Fill
from quant_flow.fills.simulator import simulate_market_order
from quant_flow.orders.order import Order
from quant_flow.portfolio.portfolio import Portfolio
from quant_flow.portfolio.risk import validate_fill


def execute_market_order(
    portfolio: Portfolio,
    order: Order,
    open_price: Decimal,
    executed_at: datetime,
    fee_rate: Decimal = Decimal("0"),
    slippage_rate: Decimal = Decimal("0"),
) -> Fill:
    """先模擬成交與驗證資金／持股，成功後才一次更新帳戶並回傳成交。"""
    candidate_fill = simulate_market_order(
        order=order,
        open_price=open_price,
        executed_at=executed_at,
        fee_rate=fee_rate,
        slippage_rate=slippage_rate,
    )

    validate_fill(portfolio, candidate_fill)

    portfolio.apply_fill(candidate_fill)

    return candidate_fill