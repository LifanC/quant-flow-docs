import pandas as pd
import yfinance as yf


def get_prices(
    stock_symbol: str,
    period: str = "1mo",
) -> pd.DataFrame:
    """下載指定期間的 Yahoo 日線；auto_adjust=False 保留未自動調整價格。"""
    stock = yf.Ticker(stock_symbol)
    return stock.history(period=period, auto_adjust=False)
