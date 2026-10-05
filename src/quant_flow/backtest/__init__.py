"""帳戶回測、目標部位執行及舊版比例回測的公開入口。"""

from .account_simulator import run_account_backtest
from .execution import execute_target_position
from .simulator import run_backtest

__all__ = ["run_account_backtest", "execute_target_position", "run_backtest"]
