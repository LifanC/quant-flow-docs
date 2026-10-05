from pathlib import Path

import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib.ticker import PercentFormatter
from matplotlib import font_manager
from matplotlib.text import Text

from quant_flow.performance.metrics import calculate_drawdown


def save_equity_chart(
    strategy: pd.DataFrame,
    benchmark: pd.DataFrame,
    stock_symbol: str,
    output_path: Path,
) -> None:
    """輸出共用日期軸的淨值與回撤 PNG，選用可用中文字型。

    使用 Agg 畫布，不需開啟視窗，也不修改 matplotlib 全域字型設定。"""
    figure = Figure(figsize=(10, 8), layout="constrained")
    FigureCanvasAgg(figure)

    equity_axes, drawdown_axes = figure.subplots(
        nrows=2,
        ncols=1,
        sharex=True,
        gridspec_kw={"height_ratios": [2, 1]},
    )

    datasets = [
        ("Moving Average（均線策略）", strategy, "tab:blue"),
        ("Buy and Hold（買進持有）", benchmark, "tab:orange"),
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

    equity_axes.set_title(f"{stock_symbol} - Strategy Comparison（策略比較）")
    equity_axes.set_ylabel("Equity（淨值）\ninitial（初始值）= 1.0")
    equity_axes.grid(True, alpha=0.3)
    equity_axes.legend()

    drawdown_axes.axhline(
        y=0.0,
        color="gray",
        linestyle="--",
        linewidth=1,
    )

    drawdown_axes.set_xlabel("Date（日期）")
    drawdown_axes.set_ylabel("Drawdown（回撤）")
    drawdown_axes.yaxis.set_major_formatter(PercentFormatter(xmax=1.0))
    drawdown_axes.grid(True, alpha=0.3)

    available = {font.name for font in font_manager.fontManager.ttflist}
    candidates = [
        "Microsoft JhengHei", "Noto Sans CJK TC", "PingFang TC",
        "Microsoft YaHei", "SimHei", "Arial Unicode MS"
    ]
    family = next((name for name in candidates if name in available),
                  "sans-serif")
    for label in figure.findobj(Text):
        label.set_fontfamily([family, "DejaVu Sans"])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=150)
