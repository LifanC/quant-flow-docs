from dataclasses import dataclass
from decimal import Decimal

from quant_flow.fills.fill import Fill
from quant_flow.orders.order import OrderSide
from quant_flow.validation import validate_decimal


@dataclass(frozen=True)
class Position:
    """不可變單檔持倉；平均成本不含手續費，清空持倉後成本歸零。"""
    symbol: str
    quantity: int = 0
    average_cost: Decimal = Decimal("0")

    def __post_init__(self) -> None:
        """建立物件時檢查資料不變條件，避免無效值進入後續帳戶計算。"""
        if not isinstance(self.symbol, str) or not self.symbol.strip():
            raise ValueError("股票代號不能為空")

        if type(self.quantity) is not int or self.quantity < 0:
            raise ValueError("持有股數必須是非負整數")

        validate_decimal(
            self.average_cost, "平均成本必須是有限且非負的 Decimal",
        )

        if self.quantity == 0 and self.average_cost != 0:
            raise ValueError("空手時平均成本必須為零")

        if self.quantity > 0 and self.average_cost <= 0:
            raise ValueError("持有股票時平均成本必須大於零")

    def apply_fill(self, fill: Fill) -> "Position":
        """套用成交並回傳新持倉；買入重算加權平均，部分賣出保留平均成本。"""
        if fill.order.symbol != self.symbol:
            raise ValueError("成交股票與持倉股票不一致")

        if fill.order.side == OrderSide.BUY:
            new_quantity = self.quantity + fill.quantity

            total_cost = (
                self.average_cost * self.quantity
                + fill.gross_amount
            )

            return Position(
                symbol=self.symbol,
                quantity=new_quantity,
                average_cost=total_cost / new_quantity,
            )

        if fill.quantity > self.quantity:
            raise ValueError("賣出股數不能超過持有股數")

        remaining_quantity = self.quantity - fill.quantity

        return Position(
            symbol=self.symbol,
            quantity=remaining_quantity,
            average_cost=(
                self.average_cost
                if remaining_quantity > 0
                else Decimal("0")
            ),
        )
