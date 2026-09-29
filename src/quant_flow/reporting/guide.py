from pathlib import Path


def export_chinese_guide(output_dir: Path) -> None:
    """在帳戶回測輸出旁附上中文欄位說明。"""
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "中文說明.md").write_text(
        """# 回測輸出中文說明

本資料夾是一檔股票的一次獨立回測，股票代碼與實際參數請查看 config.json。
多檔股票各自計算資金與績效，分別輸出至不同資料夾。
CSV 欄名以「英文（中文）」呈現，例如 Cash（現金）；以下用英文欄名對照說明。
股價重播及比較工具同時接受舊版英文欄名與新版中英欄名。

## 檔案用途

| 檔案 | 中文說明 |
| --- | --- |
| input_prices.csv | 本次使用的股價資料，可供離線重播 |
| strategy.csv | 均線策略每日持股、現金與淨值 |
| benchmark.csv | 買進持有基準每日持股、現金與淨值 |
| trades.csv | 均線策略的模擬成交紀錄 |
| benchmark_trades.csv | 買進持有基準的模擬成交紀錄 |
| summary.csv | 策略與基準的累積報酬、最大回撤 |
| config.json | 股票、回測參數及資料來源 |
| equity.png | 淨值與回撤曲線圖 |

## 每日帳戶欄位（strategy.csv、benchmark.csv）

| 欄位 | 中文說明 |
| --- | --- |
| Date | 模擬開盤時間，台灣時間每日 09:00 |
| Open | 當日開盤價，尚未加上滑價 |
| Target | 前一筆訊號決定的目標：1 為持股，0 為空手；首筆為 0 |
| Quantity | 當日交易後實際持有股數 |
| Cash | 當日交易並扣除費用後的剩餘現金 |
| Market_Value | 持股市值＝Quantity × Open |
| Total_Equity | 帳戶總資產＝Cash + Market_Value |
| Equity | 標準化淨值＝Total_Equity ÷ 初始資金；1.12 代表累積報酬 12% |

帳戶以當日開盤價估值。Target 是目標方向，實際持股仍取決於可用資金。

## 成交欄位（trades.csv、benchmark_trades.csv）

| 欄位 | 中文說明 |
| --- | --- |
| Symbol | 股票代碼 |
| Side | BUY 為買進，SELL 為賣出 |
| Quantity | 本筆成交股數 |
| Price | 含滑價的每股成交價格 |
| Gross_Amount | 成交金額＝Quantity × Price，未含手續費 |
| Fee | 本筆手續費 |
| Cash_Change | 現金變動，買進為負、賣出為正，已計入手續費 |
| Created_At | 訂單建立時間，含時區 |
| Executed_At | 模擬成交時間，含時區 |

股數以股為單位；價格與金額沿用輸入股價的貨幣單位，程式不做匯率換算。
沒有成交時，成交檔只保留欄位標題。

## 績效欄位（summary.csv）

| 欄位或值 | 中文說明 |
| --- | --- |
| Strategy | 策略名稱 |
| moving_average | 均線策略 |
| buy_and_hold | 買進持有基準 |
| total_return | 累積報酬率；0.12 代表 12%，-0.05 代表 -5% |
| max_drawdown | 最大回撤；-0.25 代表從先前高點最大下跌 25%，0 代表沒有回撤 |

報酬率是整段資料期間的結果，未換算成年化報酬。

## 股價欄位（input_prices.csv）

Date 為股價資料時間，Open 為開盤價，Close 為收盤價，兩個價格欄位為必要輸入。
其他欄位依資料來源保留，常見有 High（最高價）、Low（最低價）、Volume（成交量）、
Dividends（股利）、Stock Splits（拆股比例）。股利與拆股不會另行計入帳戶現金或股數。

## 設定欄位（config.json）

| 欄位 | 中文說明 |
| --- | --- |
| engine | 回測引擎；account_v1 為帳戶回測 |
| initial_cash | 本次初始資金 |
| symbol | 本次股票代碼 |
| period | 下載期間，如 2y 為兩年；使用 CSV 時為 null |
| short_window / long_window | 短／長均線使用的資料筆數（日線即交易日數） |
| fee_rate | 手續費率；0.001 代表 0.1% |
| slippage_rate | 滑價率；買進加價、賣出減價；0.001 代表 0.1% |
| data.source | 股價來源：yfinance 或 csv |
| data.source_file | 輸入 CSV 的來源路徑；網路下載時為 null |
| data.auto_adjust | 下載時是否自動調整價格；使用 CSV 時為 null |
| data.file | 保存的股價檔名，路徑相對於 config.json 所在資料夾 |
| data.rows | 股價資料筆數 |
| data.first_timestamp / data.last_timestamp | 股價起始／結束時間 |

目前重播會讀取保存的股價、股票代碼、均線與費率；engine 與 initial_cash 為紀錄用途，
重播仍使用程式目前的帳戶引擎及固定初始資金 100000。

## 彙整比較（outputs/comparison.csv）

執行 quant-flow-compare 後產生。
run_id 為輸出資料夾名稱，symbol 為股票代碼，short_window／long_window 為均線週期，
fee_rate／slippage_rate 為費率，data_start／data_end 為資料起訖，data_rows 為筆數。
strategy_return／benchmark_return 為策略／基準累積報酬，strategy_mdd／benchmark_mdd
為策略／基準最大回撤；return_difference 為策略減去基準的報酬差，0.03 代表多 3 個百分點。
""",
        encoding="utf-8",
    )
