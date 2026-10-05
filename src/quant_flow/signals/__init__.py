"""將策略目標轉為交易事件的公開入口。"""

from .signal import generate_trade_events

__all__ = ["generate_trade_events"]
