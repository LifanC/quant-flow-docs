from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"


@dataclass(frozen=True)
class Order:
    symbol: str
    side: OrderSide
    quantity: int
    created_at: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.symbol, str) or not self.symbol.strip():
            raise ValueError("股票代號不能為空")

        if not isinstance(self.side, OrderSide):
            raise ValueError("side 必須使用 OrderSide")

        if type(self.quantity) is not int or self.quantity <= 0:
            raise ValueError("委託股數必須是正整數")

        if not isinstance(self.created_at, datetime):
            raise ValueError("created_at 必須是 datetime")

        if self.created_at.utcoffset() is None:
            raise ValueError("委託時間必須包含時區")