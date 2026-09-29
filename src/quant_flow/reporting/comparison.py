import json
from pathlib import Path

import pandas as pd
from quant_flow.data.csv_format import read_csv, write_csv


def collect_results(outputs_dir: Path) -> pd.DataFrame:
    records = []

    for config_path in sorted(outputs_dir.rglob("config.json")):
        run_dir = config_path.parent
        summary_path = run_dir / "summary.csv"

        if not summary_path.is_file():
            print(f"略過：{run_dir.name} 缺少 summary.csv")
            continue

        config = json.loads(
            config_path.read_text(encoding="utf-8")
        )

        summary = read_csv(
            summary_path,
            index_col="Strategy",
        )

        strategy = summary.loc["moving_average"]
        benchmark = summary.loc["buy_and_hold"]
        data_info = config.get("data", {})

        records.append({
            "run_id": run_dir.relative_to(outputs_dir).as_posix(),
            "symbol": config["symbol"],
            "short_window": config["short_window"],
            "long_window": config["long_window"],
            "fee_rate": config["fee_rate"],
            "slippage_rate": config["slippage_rate"],
            "data_start": data_info.get("first_timestamp"),
            "data_end": data_info.get("last_timestamp"),
            "data_rows": data_info.get("rows"),
            "strategy_return": strategy["total_return"],
            "strategy_mdd": strategy["max_drawdown"],
            "benchmark_return": benchmark["total_return"],
            "benchmark_mdd": benchmark["max_drawdown"],
            "return_difference": (
                strategy["total_return"]
                - benchmark["total_return"]
            ),
        })

    return pd.DataFrame(records)


def main() -> None:
    project_root = Path(__file__).resolve().parents[3]
    outputs_dir = project_root / "outputs"

    if not outputs_dir.is_dir():
        print("尚未找到 outputs 資料夾，請先執行回測")
        return

    comparison = collect_results(outputs_dir)

    if comparison.empty:
        print("沒有可彙整的回測結果")
        return

    output_path = outputs_dir / "comparison.csv"

    write_csv(comparison, output_path)

    columns = [
        "run_id",
        "symbol",
        "short_window",
        "long_window",
        "strategy_return",
        "strategy_mdd",
    ]

    print(comparison[columns].to_string(index=False))
    print(f"\n比較表已輸出至：{output_path}")


if __name__ == "__main__":
    main()
