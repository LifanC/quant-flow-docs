from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from quant_flow.orders.order import Order, OrderSide


@dataclass(frozen=True)
class Fill:
    order: Order
    quantity: int
    price: Decimal
    fee: Decimal
    executed_at: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.order, Order):
            raise ValueError("order 必須是 Order")

        if type(self.quantity) is not int:
            raise ValueError("成交股數必須是整數")

        if not 0 < self.quantity <= self.order.quantity:
            raise ValueError("成交股數必須大於零且不超過委託股數")

        if (
            not isinstance(self.price, Decimal)
            or not self.price.is_finite()
            or self.price <= 0
        ):
            raise ValueError("成交價必須是有限且大於零的 Decimal")

        if (
            not isinstance(self.fee, Decimal)
            or not self.fee.is_finite()
            or self.fee < 0
        ):
            raise ValueError("費用必須是有限且非負的 Decimal")

        if not isinstance(self.executed_at, datetime):
            raise ValueError("executed_at 必須是 datetime")

        if self.executed_at.utcoffset() is None:
            raise ValueError("成交時間必須包含時區")

        if self.executed_at < self.order.created_at:
            raise ValueError("成交時間不能早於委託時間")

    @property
    def gross_amount(self) -> Decimal:
        return self.price * self.quantity

    @property
    def cash_change(self) -> Decimal:
        if self.order.side == OrderSide.BUY:
            return -(self.gross_amount + self.fee)

        return self.gross_amount - self.fee