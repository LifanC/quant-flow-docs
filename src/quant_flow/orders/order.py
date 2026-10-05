from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class OrderSide(Enum):
    """委託方向；使用列舉避免自由字串造成方向判斷錯誤。"""
    BUY = "BUY"
    SELL = "SELL"


@dataclass(frozen=True)
class Order:
    """不可變委託：股票代號、方向、正整數股數及含時區的建立時間。"""
    symbol: str
    side: OrderSide
    quantity: int
    created_at: datetime

    def __post_init__(self) -> None:
        """建立物件時檢查資料不變條件，避免無效值進入後續帳戶計算。"""
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