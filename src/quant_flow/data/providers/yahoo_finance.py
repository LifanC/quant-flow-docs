import pandas as pd
import yfinance as yf


def get_prices(
    stock_symbol: str,
    period: str = "1mo",
) -> pd.DataFrame:
    stock = yf.Ticker(stock_symbol)
    return stock.history(period=period, auto_adjust=False)
