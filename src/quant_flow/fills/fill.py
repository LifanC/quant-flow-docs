from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from quant_flow.orders.order import Order, OrderSide
from quant_flow.validation import validate_decimal


@dataclass(frozen=True)
class Fill:
    """不可變成交紀錄；允許部分成交，但成交股數不得超過原委託。"""
    order: Order
    quantity: int
    price: Decimal
    fee: Decimal
    executed_at: datetime

    def __post_init__(self) -> None:
        """建立物件時檢查資料不變條件，避免無效值進入後續帳戶計算。"""
        if not isinstance(self.order, Order):
            raise ValueError("order 必須是 Order")

        if type(self.quantity) is not int:
            raise ValueError("成交股數必須是整數")

        if not 0 < self.quantity <= self.order.quantity:
            raise ValueError("成交股數必須大於零且不超過委託股數")

        validate_decimal(
            self.price, "成交價必須是有限且大於零的 Decimal", positive=True,
        )

        validate_decimal(
            self.fee, "費用必須是有限且非負的 Decimal",
        )

        if not isinstance(self.executed_at, datetime):
            raise ValueError("executed_at 必須是 datetime")

        if self.executed_at.utcoffset() is None:
            raise ValueError("成交時間必須包含時區")

        if self.executed_at < self.order.created_at:
            raise ValueError("成交時間不能早於委託時間")

    @property
    def gross_amount(self) -> Decimal:
        """成交總額（價格乘股數），尚未扣除或加上手續費。"""
        return self.price * self.quantity

    @property
    def cash_change(self) -> Decimal:
        """回傳帳戶現金增減：買入扣總額與費用，賣出收總額並扣費用。"""
        if self.order.side == OrderSide.BUY:
            return -(self.gross_amount + self.fee)

        return self.gross_amount - self.fee
