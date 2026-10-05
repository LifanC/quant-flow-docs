# 程式閱讀指南

本次整理保留命令列參數、回測規則、報表格式與既有錯誤訊息。各主要函式的中文 docstring 說明輸入用途、輸出及需要保留的計算細節。

## 使用套件入口

各子套件的 `__init__.py` 集中提供公開類別與函式，呼叫端不用記住內部檔名：

```python
from decimal import Decimal
from quant_flow.portfolio import Portfolio, calculate_buy_quantity
from quant_flow.orders import Order, OrderSide
from quant_flow.strategy import calculate_signals
from quant_flow.backtest import run_account_backtest

account = Portfolio(cash=Decimal("100000"))
quantity = calculate_buy_quantity(account.cash, Decimal("100"))
```

`from .portfolio import Portfolio` 中的點表示從同一套件內匯入。`__all__` 列出預定公開的名稱，並控制 `from 套件 import *` 的匯入範圍；一般使用時建議明確列出需要的名稱。

根套件只提供說明；委託執行器仍從 `quant_flow.orders.executor` 匯入，以避免模型與帳戶互相載入。比較工具保留在 `quant_flow.reporting.comparison`。原本的完整模組路徑仍可使用，套件內部也可直接匯入實作模組。

匯入套件會載入所需模組，但不會下載股價、執行回測或產生報表；這些工作需要明確呼叫函式。

## 建議閱讀順序

1. `cli.py`：解析命令列、設定檔及股票清單，驗證每檔實際使用的參數。
2. `main.py`：串接資料、策略、回測與報表。`run_stock` 負責單檔流程，`_report_directory` 負責報表路徑。
3. `data/normalizer.py`、`data/symbols.py`：驗證價格與日期、保留股票代號的前導零，套用每檔參數。
4. `strategy/moving_average.py`、`signals/signal.py`：收盤後產生目標訊號及訊號變化事件。
5. `backtest/account_simulator.py`、`backtest/execution.py`：把前一天訊號延後至當天開盤，決定買入或清倉。
6. `portfolio/sizing.py`、`orders/executor.py`、`fills/simulator.py`：計算整數股數、模擬滑價與費用、檢查風控並更新帳戶。
7. `portfolio/portfolio.py`、`positions/position.py`：管理現金與持倉；驗證成功後才套用成交。
8. `performance/metrics.py`、`reporting/`：計算報酬與回撤，輸出 CSV、圖表及重播設定。

選股流程另從 `screening.py` 閱讀：`trend` 判斷最新均線多頭，`cross` 還要確認前一天不是多頭；各檔錯誤分別記錄。

`main()` 使用模式對應表分派：`screen=None` 執行 `_run_batch`，`trend` 或 `cross` 執行 `_run_screen`。命令列解析器保證提供這個欄位，因此呼叫端自行建立 Namespace 時也需提供 `screen`。

`run_stock()` 不受模式分派影響，仍可由選股流程或其他程式直接呼叫。`_load_stock_prices` 集中處理傳入資料、CSV 與 Yahoo 的來源優先順序，`_price_source_config` 集中建立報表來源設定；主回測流程只保留空資料提前返回的檢查。必要的來源與安全判斷仍保留在負責該工作的函式內。

## 重構內容與計算注意事項

- `validation.py` 集中驗證 Decimal 型別、有限性與上下限；呼叫端仍提供原本的錯誤訊息。
- 帳戶回測改為依日期、開盤價與延後一天的訊號逐筆走訪，避免每次讀取整列及前一列訊號。市值只計算一次，再加現金取得總資產。
- 主程式共用策略與基準的績效列印邏輯，報表路徑由獨立函式處理。
- 金額運算使用 Decimal；匯出成交時轉成字串保留精度，逐日報表才轉為 float。
- 買入股數的校正迴圈保留，因為 Decimal 的有限精度與乘法順序可能影響一股的邊界。
- 首日空手、下一交易日 09:00 開盤成交，每日按開盤價估值，結束時不強制平倉。
- `backtest/simulator.py` 與 `performance/benchmark.py` 是舊版比例模型，仍保留相容性；命令列主流程使用帳戶模型。

## 驗證方式

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s src/quant_flow/tests
```

測試包含既有回測、風控、選股與報表整合，以及新增的共用驗證邊界案例；不需要下載市場資料。
