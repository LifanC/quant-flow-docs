from pathlib import Path

import pandas as pd

from quant_flow.fills.fill import Fill
from quant_flow.data.csv_format import write_csv


def export_reports(
    strategy: pd.DataFrame,
    benchmark: pd.DataFrame,
    strategy_metrics: dict[str, float],
    benchmark_metrics: dict[str, float],
    output_dir: Path,
) -> None:
    """建立目錄並輸出策略、基準逐日資料與績效摘要，使用雙語 CSV 欄名。"""
    output_dir.mkdir(parents=True, exist_ok=True)

    write_csv(
        strategy,
        output_dir / "strategy.csv",
        index_label="Date",
    )

    write_csv(
        benchmark,
        output_dir / "benchmark.csv",
        index_label="Date",
    )

    summary = pd.DataFrame(
        [strategy_metrics, benchmark_metrics],
        index=["moving_average", "buy_and_hold"],
    )

    write_csv(
        summary,
        output_dir / "summary.csv",
        index_label="Strategy",
    )


def export_trades(fills: list[Fill], output_path: Path) -> None:
    """輸出成交明細；Decimal 轉字串保留精度，無交易時仍輸出完整表頭。"""
    columns = [
        "Symbol",
        "Side",
        "Quantity",
        "Price",
        "Gross_Amount",
        "Fee",
        "Cash_Change",
        "Created_At",
        "Executed_At",
    ]
    records = [{
        "Symbol": fill.order.symbol,
        "Side": fill.order.side.value,
        "Quantity": fill.quantity,
        "Price": str(fill.price),
        "Gross_Amount": str(fill.gross_amount),
        "Fee": str(fill.fee),
        "Cash_Change": str(fill.cash_change),
        "Created_At": fill.order.created_at.isoformat(),
        "Executed_At": fill.executed_at.isoformat(),
    } for fill in fills]
    trades = pd.DataFrame(records, columns=columns)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_csv(trades, output_path)
