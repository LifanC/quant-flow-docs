"""帳戶共用的 Decimal 驗證；呼叫端保留各自的錯誤訊息。"""

from decimal import Decimal


def validate_decimal(
    value: Decimal,
    message: str,
    *,
    positive: bool = False,
    below_one: bool = False,
) -> None:
    """驗證有限的非負金額，或限定為正價格、介於 [0, 1) 的費率。

    先確認型別與有限性，再比較大小，避免 NaN 引發 Decimal 比較例外。
    不自動轉換 float，讓呼叫端明確掌握金額精度。
    """
    if not isinstance(value, Decimal) or not value.is_finite():
        raise ValueError(message)
    if value < 0 or (positive and value == 0):
        raise ValueError(message)
    if below_one and value >= 1:
        raise ValueError(message)
