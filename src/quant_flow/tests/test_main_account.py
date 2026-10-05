import io
import json
import tempfile
import unittest
from argparse import Namespace
from contextlib import redirect_stdout
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from quant_flow import main as main_module
from quant_flow.reporting.exporter import export_trades
from quant_flow.cli import parse_args
from quant_flow.data.csv_format import read_csv
from quant_flow.data.providers.csv_provider import load_prices
from quant_flow.reporting.comparison import collect_results


class MainAccountTest(unittest.TestCase):
    def test_screen_exports_original_bilingual_reports_and_image(self):
        prices = pd.DataFrame(
            {"Open": [100., 110., 120., 130.], "Close": [100., 110., 120., 130.]},
            index=pd.date_range("2026-01-05", periods=4, freq="B", tz="Asia/Taipei"),
        )
        args = parse_args(["--symbol", "2330.TW", "DOWN", "--screen", "trend",
                           "--short-window", "1", "--long-window", "3"])
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            with (
                patch.object(main_module, "parse_args", return_value=args),
                patch.object(main_module, "__file__", str(root / "src/quant_flow/main.py")),
                patch("quant_flow.screening.get_prices", side_effect=[prices, prices.iloc[::-1].set_axis(prices.index)]),
                patch.object(main_module, "get_prices") as redownload,
                redirect_stdout(io.StringIO()),
            ):
                main_module.main()
            redownload.assert_not_called()
            runs = list((root / "outputs").iterdir())
            self.assertEqual(len(runs), 1)
            reports = [run for run in runs[0].iterdir() if run.is_dir()]
            self.assertEqual({json.loads((run / "config.json").read_text("utf-8"))["symbol"]
                              for run in reports}, {"2330.TW", "DOWN"})
            for run in reports:
                self.assertEqual((run / "equity.png").read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
                self.assertIn("Cash（現金）", pd.read_csv(run / "strategy.csv").columns)
            report = reports[0]
            selection = next(run for run in runs if (run / "selected.csv").exists())
            self.assertEqual(read_csv(selection / "selected.csv").symbol.tolist(), ["2330.TW"])
            self.assertIn("symbol（股票代碼）", pd.read_csv(selection / "selected.csv").columns)
            self.assertIn("Cash（現金）", pd.read_csv(report / "strategy.csv").columns)
            self.assertEqual((report / "equity.png").read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
            for name in ("benchmark.csv", "summary.csv", "trades.csv", "benchmark_trades.csv",
                         "input_prices.csv", "中文說明.md"):
                self.assertTrue((report / name).is_file(), name)

    def test_multiple_stocks_export_separate_replayable_runs(self):
        prices = pd.DataFrame(
            {"Open": [100., 110., 120., 90., 80., 120.],
             "Close": [100., 110., 120., 90., 80., 120.]},
            index=pd.date_range("2026-01-05", periods=6, freq="B", tz="Asia/Taipei"),
        )
        args = parse_args([
            "--symbol", "EMPTY", "2330.TW", "0050.TW",
            "--short-window", "2", "--long-window", "3",
        ])
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            with (
                patch.object(main_module, "parse_args", return_value=args),
                patch.object(main_module, "__file__", str(root / "src/quant_flow/main.py")),
                patch.object(main_module, "get_prices", side_effect=[pd.DataFrame(), prices, prices * 2]) as download,
                redirect_stdout(io.StringIO()),
            ):
                main_module.main()
            self.assertEqual(
                [call.args[0] for call in download.call_args_list],
                ["EMPTY", "2330.TW", "0050.TW"],
            )
            batches = list((root / "outputs").iterdir())
            self.assertEqual(len(batches), 1)
            runs = list(batches[0].iterdir())
            self.assertEqual(len(runs), 2)
            symbols = set()
            for run in runs:
                config = json.loads((run / "config.json").read_text("utf-8"))
                symbol = config["symbol"]
                self.assertEqual(run.name, symbol)
                symbols.add(symbol)
                self.assertEqual(config["initial_cash"], "100000")
                trades = read_csv(run / "benchmark_trades.csv")
                self.assertEqual(set(trades["Symbol"]), {symbol})
                replay = parse_args(["--config", str(run / "config.json")])
                self.assertEqual(replay.symbol, [symbol])
                saved = load_prices(replay.input_csv)
                self.assertEqual(saved["Open"].iloc[0], 100 if symbol == "2330.TW" else 200)
                self.assertTrue((run / "equity.png").is_file())
            self.assertEqual(symbols, {"2330.TW", "0050.TW"})
            comparison = collect_results(root / "outputs")
            self.assertEqual(set(comparison["symbol"]), symbols)

    def test_csv_run_exports_account_history_and_reconcilable_trades(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "prices.csv"
            prices = pd.DataFrame(
                {
                    "Open": [100.0, 110.0, 120.0, 90.0, 80.0, 120.0],
                    "Close": [100.0, 110.0, 120.0, 90.0, 80.0, 120.0],
                },
                index=pd.date_range(
                    "2026-01-05", periods=6, freq="B", tz="Asia/Taipei"
                ),
            )
            prices.to_csv(source, index_label="Date")
            args = Namespace(
                screen=None,
                symbol=["2330.TW"], input_csv=source, period="1y",
                short_window=2, long_window=3,
                fee_rate=0.001, slippage_rate=0.001,
            )

            with (
                patch.object(main_module, "parse_args", return_value=args),
                patch.object(
                    main_module, "__file__",
                    str(root / "src" / "quant_flow" / "main.py"),
                ),
                patch.object(main_module, "get_prices") as download,
                redirect_stdout(io.StringIO()),
            ):
                main_module.main()

            download.assert_not_called()
            runs = list((root / "outputs").iterdir())
            self.assertEqual(len(runs), 1)
            run_dir = runs[0] / "2330.TW"
            for filename in (
                "strategy.csv", "benchmark.csv", "summary.csv",
                "trades.csv", "benchmark_trades.csv", "input_prices.csv",
                "config.json", "equity.png",
            ):
                self.assertTrue((run_dir / filename).is_file(), filename)

            config = json.loads((run_dir / "config.json").read_text("utf-8"))
            self.assertEqual(config["engine"], "account_v1")
            self.assertEqual(config["initial_cash"], "100000")
            self.assertEqual((run_dir / "equity.png").read_bytes()[:8], b"\x89PNG\r\n\x1a\n")

            for history_name, trades_name in (
                ("strategy.csv", "trades.csv"),
                ("benchmark.csv", "benchmark_trades.csv"),
            ):
                history = read_csv(run_dir / history_name)
                trades = read_csv(run_dir / trades_name, dtype=str)
                self.assertFalse(trades.empty)
                cash_change = sum(
                    (Decimal(value) for value in trades["Cash_Change"]),
                    Decimal("0"),
                )
                self.assertAlmostEqual(
                    float(Decimal(config["initial_cash"]) + cash_change),
                    history["Cash"].iloc[-1],
                    places=8,
                )
                expected_quantity = sum(
                    int(row.Quantity) * (1 if row.Side == "BUY" else -1)
                    for row in trades.itertuples()
                )
                self.assertEqual(expected_quantity, history["Quantity"].iloc[-1])
                self.assertAlmostEqual(
                    history["Total_Equity"].iloc[-1],
                    history["Cash"].iloc[-1] + history["Market_Value"].iloc[-1],
                    places=8,
                )

    def test_empty_trades_export_preserves_headers(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "nested" / "trades.csv"
            export_trades([], path)
            trades = pd.read_csv(path)
            self.assertTrue(trades.empty)
            self.assertEqual(
                trades.columns.tolist(),
                ["Symbol（股票代碼）", "Side（買賣方向）", "Quantity（股數）",
                 "Price（成交價）", "Gross_Amount（成交金額）", "Fee（手續費）",
                 "Cash_Change（現金變動）", "Created_At（訂單建立時間）",
                 "Executed_At（成交時間）"],
            )


if __name__ == "__main__":
    unittest.main()
