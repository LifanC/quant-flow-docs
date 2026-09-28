from dataclasses import dataclass, field
from decimal import Decimal

from quant_flow.fills.fill import Fill
from quant_flow.positions.position import Position


@dataclass
class Portfolio:
    cash: Decimal
    positions: dict[str, Position] = field(
        default_factory=dict,
        init=False,
    )

    def __post_init__(self) -> None:
        if (
            not isinstance(self.cash, Decimal)
            or not self.cash.is_finite()
            or self.cash < 0
        ):
            raise ValueError("現金必須是有限且非負的 Decimal")

    def apply_fill(self, fill: Fill) -> None:
        symbol = fill.order.symbol

        current_position = self.positions.get(
            symbol,
            Position(symbol=symbol),
        )

        # 先計算，不修改目前帳戶。
        new_position = current_position.apply_fill(fill)
        new_cash = self.cash + fill.cash_change

        if new_cash < 0:
            raise ValueError("現金不足，無法套用成交")

        # 驗證通過後才更新。
        self.cash = new_cash
        self.positions[symbol] = new_position

    def market_value(
        self,
        prices: dict[str, Decimal],
    ) -> Decimal:
        total = Decimal("0")

        for symbol, position in self.positions.items():
            if position.quantity == 0:
                continue

            if symbol not in prices:
                raise ValueError(f"缺少 {symbol} 的估值價格")

            price = prices[symbol]

            if (
                not isinstance(price, Decimal)
                or not price.is_finite()
                or price <= 0
            ):
                raise ValueError(
                    f"{symbol} 的估值價格必須是有限且大於零的 Decimal"
                )

            total += price * position.quantity

        return total

    def total_equity(
        self,
        prices: dict[str, Decimal],
    ) -> Decimal:
        return self.cash + self.market_value(prices)
