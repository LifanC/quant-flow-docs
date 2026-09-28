from pathlib import Path

import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib.ticker import PercentFormatter

from quant_flow.performance.metrics import calculate_drawdown

def save_equity_chart(
    strategy: pd.DataFrame,
    benchmark: pd.DataFrame,
    stock_symbol: str,
    output_path: Path,
) -> None:
    figure = Figure(figsize=(10, 8), layout="constrained")
    FigureCanvasAgg(figure)

    equity_axes, drawdown_axes = figure.subplots(
        nrows=2,
        ncols=1,
        sharex=True,
        gridspec_kw={"height_ratios": [2, 1]},
    )

    datasets = [
        ("Moving Average", strategy, "tab:blue"),
        ("Buy and Hold", benchmark, "tab:orange"),
    ]

    for label, data, color in datasets:
        equity = data["Equity"]

        drawdown = calculate_drawdown(equity)

        equity_axes.plot(
            data.index,
            equity,
            label=label,
            color=color,
            linewidth=1.8,
        )

        drawdown_axes.plot(
            data.index,
            drawdown,
            label=label,
            color=color,
            linewidth=1.4,
        )

    equity_axes.axhline(
        y=1.0,
        color="gray",
        linestyle="--",
        linewidth=1,
    )

    equity_axes.set_title(f"{stock_symbol} - Strategy Comparison")
    equity_axes.set_ylabel("Equity (initial = 1.0)")
    equity_axes.grid(True, alpha=0.3)
    equity_axes.legend()

    drawdown_axes.axhline(
        y=0.0,
        color="gray",
        linestyle="--",
        linewidth=1,
    )

    drawdown_axes.set_xlabel("Date")
    drawdown_axes.set_ylabel("Drawdown")
    drawdown_axes.yaxis.set_major_formatter(
        PercentFormatter(xmax=1.0)
    )
    drawdown_axes.grid(True, alpha=0.3)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=150)