"""Read a watchlist without dropping leading zeroes from stock codes."""
from pathlib import Path
from argparse import Namespace
import re

import pandas as pd
from quant_flow.data.csv_format import HEADERS


PARAMETERS = {"period": str, "short_window": int, "long_window": int,
              "fee_rate": float, "slippage_rate": float}


def stock_args(args, symbol: str) -> Namespace:
    return Namespace(**(vars(args) | getattr(args, "stock_options", {}).get(symbol, {})))


def load_symbols(path: Path, column: str = "symbol") -> list[str]:
    return list(load_watchlist(path, column))


def load_watchlist(path: Path, column: str = "symbol") -> dict[str, dict]:
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
    if frame.columns.duplicated().any():
        raise ValueError("股票清單包含重複欄位")
    symbols = {}
    for index, row in frame.iterrows():
        value = row[column]
        symbol = str(value).strip().upper()
        if not symbol:
            continue
        if not re.fullmatch(r"[A-Z0-9^][A-Z0-9.^=-]*", symbol):
            raise ValueError(f"無效股票代號：{symbol}")
        if symbol.isdigit():
            symbol += ".TW"
        if symbol not in symbols:
            options = {}
            for name, convert in PARAMETERS.items():
                field = name if name in frame.columns else HEADERS.get(name, name)
                raw = str(row.get(field, "")).strip()
                if raw:
                    try:
                        options[name] = convert(raw)
                    except ValueError as exc:
                        raise ValueError(f"第 {index + 2} 列 {symbol}：{name} 格式錯誤：{raw}") from exc
            symbols[symbol] = options
    if not symbols:
        raise ValueError("股票清單沒有有效代號")
    return symbols
