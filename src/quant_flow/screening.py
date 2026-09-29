"""Screen the latest available daily bars using the existing MA strategy."""
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import pandas as pd

from quant_flow.data.normalizer import normalize_prices
from quant_flow.data.csv_format import write_csv
from quant_flow.data.providers.yahoo_finance import get_prices
from quant_flow.strategy.moving_average import calculate_signals


def screen_symbols(args, output_root: Path, report_stock=None) -> Path:
    output = output_root / f"{datetime.now():%Y-%m-%d_%H-%M-%S}_{uuid4().hex[:8]}"
    output.mkdir(parents=True, exist_ok=False)
    rows = []
    for symbol in args.symbol:
        print(f"選股分析：{symbol}")
        row = {"symbol": symbol, "selected": False, "status": "error",
               "date": "", "close": None, "short_ma": None, "long_ma": None,
               "rule": args.screen, "reason": "", "report_error": ""}
        try:
            prices = normalize_prices(get_prices(symbol, period=args.period))
            required = args.long_window + (args.screen == "cross")
            if len(prices) < required:
                raise ValueError(f"資料不足：需要至少 {required} 筆")
            signals = calculate_signals(prices, args.short_window, args.long_window)
            last = signals.iloc[-1]
            selected = bool(last["Signal"])
            if args.screen == "cross":
                selected = selected and not bool(signals.iloc[-2]["Signal"])
            row.update(selected=selected, status="ok", date=signals.index[-1].isoformat(),
                       close=last["Close"], short_ma=last["SMA_Short"],
                       long_ma=last["SMA_Long"], reason="符合條件" if selected else "未符合條件")
            if report_stock is not None:
                try:
                    report_stock(args, symbol, prices=prices, output_root=output)
                except Exception as exc:
                    row["report_error"] = str(exc)
                    print(f"{symbol}：報表產生失敗：{exc}")
        except Exception as exc:
            row["reason"] = str(exc)
            print(f"{symbol}：{exc}")
        rows.append(row)
    frame = pd.DataFrame(rows)
    write_csv(frame, output / "screening.csv")
    write_csv(frame.loc[frame["selected"]], output / "selected.csv")
    print(f"選出 {int(frame['selected'].sum())} 檔；資料失敗 {int((frame['status'] == 'error').sum())} 檔；"
          f"報表失敗 {int(frame['report_error'].ne('').sum())} 檔。結果：{output}")
    return output
