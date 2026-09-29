"""Read a watchlist without dropping leading zeroes from stock codes."""
from pathlib import Path
import re

import pandas as pd
from quant_flow.data.csv_format import HEADERS


def load_symbols(path: Path, column: str = "symbol") -> list[str]:
    if path.suffix.lower() == ".csv":
        frame = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    elif path.suffix.lower() == ".xlsx":
        frame = pd.read_excel(path, dtype=str, keep_default_na=False, engine="openpyxl")
    else:
        raise ValueError("股票清單僅支援 .csv 或 .xlsx")
    frame.columns = frame.columns.str.strip()
    if column not in frame.columns and HEADERS.get(column) in frame.columns:
        column = HEADERS[column]
    if column not in frame.columns:
        raise ValueError(f"找不到股票代號欄位：{column}")
    symbols = []
    for value in frame[column]:
        symbol = str(value).strip().upper()
        if not symbol:
            continue
        if not re.fullmatch(r"[A-Z0-9^][A-Z0-9.^=-]*", symbol):
            raise ValueError(f"無效股票代號：{symbol}")
        if symbol.isdigit():
            symbol += ".TW"
        if symbol not in symbols:
            symbols.append(symbol)
    if not symbols:
        raise ValueError("股票清單沒有有效代號")
    return symbols
