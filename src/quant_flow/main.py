from quant_flow.backtest import run_account_backtest
from quant_flow.data import normalize_prices, stock_args, write_csv
from quant_flow.data.providers import get_prices, load_prices
from quant_flow.signals import generate_trade_events
from quant_flow.strategy import calculate_signals
from quant_flow.performance import calculate_metrics
from quant_flow.reporting import (
    export_reports, export_trades, save_equity_chart, export_chinese_guide,
)
from quant_flow.cli import parse_args
from quant_flow.screening import screen_symbols

from pathlib import Path
from datetime import datetime
from decimal import Decimal
from uuid import uuid4
import json
import re
from argparse import Namespace


def main() -> None:
    """解析設定並執行選股或逐檔回測；各股票使用獨立帳戶與報表目錄。"""
    args = parse_args()
    output_root = Path(__file__).resolve().parents[2] / "outputs"
    if getattr(args, "screen", None):
        screen_symbols(args, output_root, report_stock=run_stock)
        return
    batch_dir = output_root / f"{datetime.now():%Y-%m-%d_%H-%M-%S}_{uuid4().hex[:8]}"
    for stock_symbol in dict.fromkeys(args.symbol):
        run_stock(stock_args(args, stock_symbol),
                  stock_symbol,
                  output_root=batch_dir)


def run_stock(args: Namespace,
              stock_symbol: str,
              *,
              prices=None,
              output_root=None) -> None:

    """完成單檔股票的資料、策略、帳戶回測與報表流程。

    prices 可由選股流程傳入，以重用下載資料；未提供時讀取 CSV 或 Yahoo。
    策略與買進持有使用相同初始資金、費率及股價，便於公平比較。"""
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

    for label, metrics in [("均線策略", strategy_metrics), ("買進持有", benchmark_metrics)]:
        print(f"\n{label}")
        print(f"累積報酬：{metrics['total_return']:.2%}")
        print(f"最大回撤：{metrics['max_drawdown']:.2%}")

    return_difference = (strategy_metrics["total_return"] -
                         benchmark_metrics["total_return"])

    print(f"\n策略與基準報酬差：{return_difference * 100:.2f} 個百分點")

    output_dir = _report_directory(stock_symbol, output_root)

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

    write_csv(
        prices,
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
            "source_file":
            (str(args.input_csv.resolve()) if using_csv else None),
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


def _report_directory(stock_symbol: str, output_root: Path | None) -> Path:
    """產生報表路徑；批次內使用股票代號，遇到重複名稱才加時間與亂數。"""
    project_root = Path(__file__).resolve().parents[2]

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    safe_symbol = re.sub(r"[^A-Za-z0-9._^-]", "_", stock_symbol)
    run_id = f"{safe_symbol}_{timestamp}_{uuid4().hex[:8]}"

    output_dir = project_root / "outputs" / run_id
    if output_root is not None:
        output_dir = output_root / (safe_symbol.strip(".") or "stock")
        if output_dir.exists():
            output_dir = output_root / run_id

    return output_dir


if __name__ == "__main__":
    main()
