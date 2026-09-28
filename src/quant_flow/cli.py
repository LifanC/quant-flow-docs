import argparse
from pathlib import Path
import json

def parse_args(
    argv: list[str] | None = None,
) -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--symbol",
        default="2330.TW",
    )

    parser.add_argument(
        "--period",
        default="1y",
        choices=["1mo", "3mo", "6mo", "1y", "2y", "5y"],
    )

    parser.add_argument(
        "--short-window",
        type=int,
        default=5,
    )

    parser.add_argument(
        "--long-window",
        type=int,
        default=20,
    )

    parser.add_argument(
        "--fee-rate",
        type=float,
        default=0.001,
    )

    parser.add_argument(
        "--slippage-rate",
        type=float,
        default=0.001,
    )

    parser.add_argument(
        "--input-csv",
        type=Path,
        default=None,
        help="使用既有股價 CSV，略過網路下載",
    )

    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="讀取先前執行的設定與股價",
    )

    args = parser.parse_args(argv)

    if args.config is not None:
        try:
            config_path = args.config.resolve()

            config = json.loads(
                config_path.read_text(encoding="utf-8")
            )

            args.symbol = config["symbol"]
            args.short_window = int(config["short_window"])
            args.long_window = int(config["long_window"])
            args.fee_rate = float(config["fee_rate"])
            args.slippage_rate = float(config["slippage_rate"])

            args.input_csv = (
                config_path.parent / config["data"]["file"]
            )

            # 使用保存的 CSV，不再使用相對期間下載。
            args.period = None

            if not args.input_csv.is_file():
                parser.error(f"找不到股價檔案：{args.input_csv}")

        except (OSError, ValueError, KeyError, TypeError) as exc:
            parser.error(f"無法載入設定檔：{exc}")

    if not (
        0 < args.short_window < args.long_window
    ):
        parser.error("均線週期必須符合：0 < 短均線 < 長均線")

    if not (
        0 <= args.fee_rate < 1
        and 0 <= args.slippage_rate < 1
        and args.fee_rate + args.slippage_rate < 1
    ):
        parser.error("費率必須非負，且合計小於 1")

    return args