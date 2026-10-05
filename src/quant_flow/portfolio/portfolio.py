from dataclasses import dataclass, field
from decimal import Decimal

from quant_flow.fills.fill import Fill
from quant_flow.positions.position import Position
from quant_flow.validation import validate_decimal


@dataclass
class Portfolio:
    """可變帳戶，保存 Decimal 現金與各股票持倉；每個實例有獨立字典。"""
    cash: Decimal
    positions: dict[str, Position] = field(
        default_factory=dict,
        init=False,
    )

    def __post_init__(self) -> None:
        """建立物件時檢查資料不變條件，避免無效值進入後續帳戶計算。"""
        validate_decimal(
            self.cash, "現金必須是有限且非負的 Decimal",
        )

    def apply_fill(self, fill: Fill) -> None:
        """計算新持倉與現金，全部驗證通過才更新，避免失敗時留下半套帳戶。"""
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
        """以提供的 Decimal 價格計算持股市值；零股部位不需報價。"""
        total = Decimal("0")

        for symbol, position in self.positions.items():
            if position.quantity == 0:
                continue

            if symbol not in prices:
                raise ValueError(f"缺少 {symbol} 的估值價格")

            price = prices[symbol]

            validate_decimal(
                price, f"{symbol} 的估值價格必須是有限且大於零的 Decimal", positive=True,
            )

            total += price * position.quantity

        return total

    def total_equity(
        self,
        prices: dict[str, Decimal],
    ) -> Decimal:
        """帳戶總資產等於可用現金加上全部持股市值。"""
        return self.cash + self.market_value(prices)
