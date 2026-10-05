"""股價來源的公開入口；匯入只載入函式，呼叫 get_prices 才下載資料。"""

from .csv_provider import load_prices
from .yahoo_finance import get_prices

__all__ = ["load_prices", "get_prices"]
