"""Bilingual CSV headers at the file boundary; internal columns stay English."""
from pathlib import Path

import pandas as pd

TRANSLATIONS = {
    "Date": "日期",
    "Open": "開盤價",
    "High": "最高價",
    "Low": "最低價",
    "Close": "收盤價",
    "Adj Close": "調整後收盤價",
    "Volume": "成交量",
    "Dividends": "股利",
    "Stock Splits": "拆股比例",
    "Capital Gains": "資本利得",
    "Target": "目標持倉",
    "Quantity": "股數",
    "Cash": "現金",
    "Market_Value": "持股市值",
    "Total_Equity": "總資產",
    "Equity": "標準化淨值",
    "Symbol": "股票代碼",
    "Side": "買賣方向",
    "Price": "成交價",
    "Gross_Amount": "成交金額",
    "Fee": "手續費",
    "Cash_Change": "現金變動",
    "Created_At": "訂單建立時間",
    "Executed_At": "成交時間",
    "Strategy": "策略",
    "total_return": "累積報酬率",
    "max_drawdown": "最大回撤",
    "run_id": "執行編號",
    "symbol": "股票代碼",
    "short_window": "短均線週期",
    "long_window": "長均線週期",
    "fee_rate": "手續費率",
    "slippage_rate": "滑價率",
    "data_start": "資料開始時間",
    "data_end": "資料結束時間",
    "data_rows": "資料筆數",
    "strategy_return": "策略報酬率",
    "strategy_mdd": "策略最大回撤",
    "benchmark_return": "基準報酬率",
    "benchmark_mdd": "基準最大回撤",
    "return_difference": "報酬率差",
    "selected": "是否入選",
    "status": "處理狀態",
    "date": "資料日期",
    "close": "收盤價",
    "short_ma": "短期均線",
    "long_ma": "長期均線",
    "rule": "選股條件",
    "reason": "原因",
    "report_error": "報表錯誤",
}
HEADERS = {key: f"{key}（{value}）" for key, value in TRANSLATIONS.items()}


def write_csv(data: pd.DataFrame,
              path: Path,
              *,
              index_label: str | None = None) -> None:
    """僅在檔案輸出邊界轉換雙語表頭；UTF-8 BOM 方便 Excel 顯示中文。

    只有指定 index_label 才保存索引，避免清單意外多出流水號欄位。"""
    data.rename(columns=HEADERS).to_csv(
        path,
        index=index_label is not None,
        index_label=HEADERS.get(index_label, index_label),
        encoding="utf-8-sig",
    )


def read_csv(path: Path,
             *,
             index_col: str | None = None,
             **kwargs) -> pd.DataFrame:
    """讀取一般或雙語 CSV 並還原英文欄名，拒絕還原後的重複欄位。"""
    data = pd.read_csv(path, encoding="utf-8-sig", **kwargs)
    data = data.rename(columns={value: key for key, value in HEADERS.items()})
    if data.columns.duplicated().any():
        raise ValueError("CSV 包含重複的中英文欄位")
    return data.set_index(index_col) if index_col is not None else data
