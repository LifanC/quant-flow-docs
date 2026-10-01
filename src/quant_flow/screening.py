"""Screen the latest available daily bars using the existing MA strategy."""
from quant_flow.data.normalizer import normalize_prices
from quant_flow.data.csv_format import write_csv
from quant_flow.data.providers.yahoo_finance import get_prices
from quant_flow.strategy.moving_average import calculate_signals
from quant_flow.data.symbols import stock_args, PARAMETERS
from quant_flow.backtest.account_simulator import run_account_backtest
from quant_flow.data.providers.yahoo_finance import get_prices
from quant_flow.signals.signal import generate_trade_events
from quant_flow.strategy.moving_average import calculate_signals
from quant_flow.data.normalizer import normalize_prices
from quant_flow.performance.metrics import calculate_metrics
from quant_flow.reporting.exporter import export_reports, export_trades
from quant_flow.data.providers.csv_provider import load_prices
from quant_flow.reporting.charts import save_equity_chart
from quant_flow.reporting.guide import export_chinese_guide
from quant_flow.data.csv_format import write_csv

from pathlib import Path
from datetime import datetime
from decimal import Decimal
from uuid import uuid4
import json
import re
from argparse import Namespace

import pandas as pd

def screen_symbols(args, output_root: Path) -> Path:
    if getattr(args, "screen", None):
        output = output_root / f"{datetime.now():%Y-%m-%d_%H-%M-%S}_{uuid4().hex[:8]}"
        output.mkdir(parents=True, exist_ok=False)
        rows = []
        for symbol in args.symbol:
            effective = stock_args(args, symbol)
            print(f"選股分析：{symbol}")
            row = {"symbol": symbol, "selected": False, "status": "error",
                "date": "", "close": None, "short_ma": None, "long_ma": None,
                "rule": args.screen, "reason": "", "report_error": ""}
            row.update({name: getattr(effective, name) for name in PARAMETERS})
            try:
                prices = normalize_prices(get_prices(symbol, period=effective.period))
                required = effective.long_window + (args.screen == "cross")
                if len(prices) < required:
                    raise ValueError(f"資料不足：需要至少 {required} 筆")
                signals = calculate_signals(prices, effective.short_window, effective.long_window)
                last = signals.iloc[-1]
                selected = bool(last["Signal"])
                if args.screen == "cross":
                    selected = selected and not bool(signals.iloc[-2]["Signal"])
                row.update(selected=selected, status="ok", date=signals.index[-1].isoformat(),
                        close=last["Close"], short_ma=last["SMA_Short"],
                        long_ma=last["SMA_Long"], reason="符合條件" if selected else "未符合條件")
                if report_stock is not None:
                    try:
                        report_stock(effective, symbol, prices=prices, output_root=output)
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
    else:
        for stock_symbol in dict.fromkeys(args.symbol):
            report_stock(stock_args(args, stock_symbol), stock_symbol, output_root=output)

def report_stock(args: Namespace, stock_symbol: str, *, prices=None, output_root=None) -> None:

    if prices is not None:
        prices = prices.copy()
    elif args.input_csv is not None:
        print(f"讀取本機資料：{args.input_csv}")
        prices = load_prices(args.input_csv)
    else:
        print(f"下載股價：{stock_symbol}")
        prices = get_prices(stock_symbol, period=args.period)

    if prices.empty:
        print(f"{stock_symbol}：沒有取得股價資料，略過")
        return

    prices = normalize_prices(prices)

    signals = calculate_signals(
        prices,
        short_window=args.short_window,
        long_window=args.long_window,
    )

    events = generate_trade_events(signals)

    initial_cash = Decimal("100000")
    fee_rate = Decimal(str(args.fee_rate))
    slippage_rate = Decimal(str(args.slippage_rate))

    result, fills = run_account_backtest(
        signals=events,
        symbol=stock_symbol,
        initial_cash=initial_cash,
        fee_rate=fee_rate,
        slippage_rate=slippage_rate,
    )

    benchmark_signals = prices.copy()
    benchmark_signals["Signal"] = 1

    benchmark, benchmark_fills = run_account_backtest(
        signals=benchmark_signals,
        symbol=stock_symbol,
        initial_cash=initial_cash,
        fee_rate=fee_rate,
        slippage_rate=slippage_rate,
    )

    columns = [
        "Open",
        "Target",
        "Quantity",
        "Cash",
        "Market_Value",
        "Total_Equity",
        "Equity",
    ]

    print(f"股票：{stock_symbol}")
    print(result[columns].tail(10))

    strategy_metrics = calculate_metrics(result["Equity"])
    benchmark_metrics = calculate_metrics(benchmark["Equity"])

    print("\n均線策略")
    print(f"累積報酬：{strategy_metrics['total_return']:.2%}")
    print(f"最大回撤：{strategy_metrics['max_drawdown']:.2%}")

    print("\n買進持有")
    print(f"累積報酬：{benchmark_metrics['total_return']:.2%}")
    print(f"最大回撤：{benchmark_metrics['max_drawdown']:.2%}")

    return_difference = (
        strategy_metrics["total_return"] - benchmark_metrics["total_return"]
    )

    print(f"\n策略與基準報酬差：{return_difference * 100:.2f} 個百分點")

    project_root = Path(__file__).resolve().parents[2]

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    safe_symbol = re.sub(r"[^A-Za-z0-9._^-]", "_", stock_symbol)
    run_id = f"{safe_symbol}_{timestamp}_{uuid4().hex[:8]}"

    output_dir = project_root / "outputs" / run_id
    if output_root is not None:
        output_dir = output_root / (safe_symbol.strip(".") or "stock")
        if output_dir.exists():
            output_dir = output_root / run_id

    export_reports(
        strategy=result,
        benchmark=benchmark,
        strategy_metrics=strategy_metrics,
        benchmark_metrics=benchmark_metrics,
        output_dir=output_dir,
    )

    export_trades(fills, output_dir / "trades.csv")
    export_trades(benchmark_fills, output_dir / "benchmark_trades.csv")

    save_equity_chart(
        strategy=result,
        benchmark=benchmark,
        stock_symbol=stock_symbol,
        output_path=output_dir / "equity.png",
    )

    write_csv(prices,
        output_dir / "input_prices.csv",
        index_label="Date",
    )

    using_csv = args.input_csv is not None

    run_config = {
        "engine": "account_v1",
        "initial_cash": str(initial_cash),
        "symbol": stock_symbol,
        "period": None if using_csv else args.period,
        "short_window": args.short_window,
        "long_window": args.long_window,
        "fee_rate": args.fee_rate,
        "slippage_rate": args.slippage_rate,
        "data": {
            "source": "csv" if using_csv else "yfinance",
            "source_file": (
                str(args.input_csv.resolve())
                if using_csv
                else None
            ),
            "auto_adjust": None if using_csv else False,
            "file": "input_prices.csv",
            "rows": len(prices),
            "first_timestamp": prices.index[0].isoformat(),
            "last_timestamp": prices.index[-1].isoformat(),
        },
    }

    config_path = output_dir / "config.json"

    config_path.write_text(
        json.dumps(
            run_config,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    export_chinese_guide(output_dir)

    print(f"\n報表已輸出至：{output_dir}")