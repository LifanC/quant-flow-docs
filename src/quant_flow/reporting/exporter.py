from pathlib import Path

import pandas as pd

from quant_flow.fills.fill import Fill

def export_reports(
    strategy: pd.DataFrame,
    benchmark: pd.DataFrame,
    strategy_metrics: dict[str, float],
    benchmark_metrics: dict[str, float],
    output_dir: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    strategy.to_csv(
        output_dir / "strategy.csv",
        index_label="Date",
        encoding="utf-8-sig",
    )

    benchmark.to_csv(
        output_dir / "benchmark.csv",
        index_label="Date",
        encoding="utf-8-sig",
    )

    summary = pd.DataFrame(
        [strategy_metrics, benchmark_metrics],
        index=["moving_average", "buy_and_hold"],
    )

    summary.to_csv(
        output_dir / "summary.csv",
        index_label="Strategy",
        encoding="utf-8-sig",
    )


def export_trades(fills: list[Fill], output_path: Path) -> None:
    columns = [
        "Symbol", "Side", "Quantity", "Price", "Gross_Amount",
        "Fee", "Cash_Change", "Created_At", "Executed_At",
    ]
    records = [
        {
            "Symbol": fill.order.symbol,
            "Side": fill.order.side.value,
            "Quantity": fill.quantity,
            "Price": str(fill.price),
            "Gross_Amount": str(fill.gross_amount),
            "Fee": str(fill.fee),
            "Cash_Change": str(fill.cash_change),
            "Created_At": fill.order.created_at.isoformat(),
            "Executed_At": fill.executed_at.isoformat(),
        }
        for fill in fills
    ]
    trades = pd.DataFrame(records, columns=columns)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    trades.to_csv(output_path, index=False, encoding="utf-8-sig")
