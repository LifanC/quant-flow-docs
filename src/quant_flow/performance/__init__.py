"""淨值績效與舊版買進持有基準的公開入口。"""

from .benchmark import run_buy_and_hold
from .metrics import calculate_drawdown, calculate_metrics

__all__ = ["calculate_drawdown", "calculate_metrics", "run_buy_and_hold"]
