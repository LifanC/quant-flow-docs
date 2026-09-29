import io
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd

from quant_flow.cli import parse_args
from quant_flow.data.symbols import load_symbols
from quant_flow.data.csv_format import read_csv
from quant_flow.screening import screen_symbols


class ScreeningTest(unittest.TestCase):
    def test_watchlist_formats_preserve_codes_and_deduplicate(self):
        with tempfile.TemporaryDirectory() as tmp:
            frame = pd.DataFrame({"symbol": ["0050", "2330.TW", " 2330.tw ", "", "6488.TWO"]})
            for suffix in (".csv", ".xlsx"):
                path = Path(tmp) / ("stocks" + suffix)
                if suffix == ".csv":
                    frame.to_csv(path, index=False, encoding="utf-8-sig")
                else:
                    frame.to_excel(path, index=False)
                self.assertEqual(load_symbols(path), ["0050.TW", "2330.TW", "6488.TWO"])
                self.assertEqual(parse_args(["--symbols-file", str(path)]).symbol, load_symbols(path))

    def test_invalid_list(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "stocks.csv"
            for text in ("name\n2330\n", "symbol\n\n", "symbol\nbad/code\n"):
                path.write_text(text, encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_symbols(path)

    def test_conflicting_sources(self):
        for arguments in (["--symbols-file", "x.csv", "--symbol", "AAPL"],
                          ["--symbols-file", "x.csv", "--input-csv", "prices.csv"],
                          ["--screen", "trend", "--config", "config.json"]):
            with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                parse_args(arguments)

    def test_screen_rules_and_errors(self):
        def prices(values):
            return pd.DataFrame({"Open": values, "Close": values},
                                index=pd.date_range("2026-01-01", periods=len(values)))

        with tempfile.TemporaryDirectory() as tmp:
            for rule, expected in (("trend", ["UP", "CROSS"]), ("cross", ["CROSS"])):
                args = parse_args(["--symbol", "UP", "CROSS", "SHORT", "BAD", "DOWN",
                                   "--screen", rule, "--short-window", "1", "--long-window", "3"])
                with patch("quant_flow.screening.get_prices", side_effect=[
                    prices([1, 2, 3, 4]), prices([4, 3, 2, 5]), prices([1, 2]),
                    RuntimeError("unavailable"), prices([4, 3, 2, 1]),
                ]), redirect_stdout(io.StringIO()):
                    output = screen_symbols(args, Path(tmp))
                selected = read_csv(output / "selected.csv")
                report = read_csv(output / "screening.csv")
                self.assertEqual(selected.symbol.tolist(), expected)
                self.assertEqual(report.status.tolist(), ["ok", "ok", "error", "error", "ok"])

    def test_empty_selection_still_exports_headers(self):
        args = parse_args(["--symbol", "BAD", "--screen", "trend"])
        with tempfile.TemporaryDirectory() as tmp, patch(
            "quant_flow.screening.get_prices", return_value=pd.DataFrame()
        ), redirect_stdout(io.StringIO()):
            output = screen_symbols(args, Path(tmp))
            self.assertTrue(pd.read_csv(output / "selected.csv").empty)
            self.assertEqual(read_csv(output / "screening.csv").status.tolist(), ["error"])

    def test_report_failure_continues_and_selection_can_be_reused(self):
        args = parse_args(["--symbol", "0050.TW", "2330.TW", "--screen", "trend",
                           "--short-window", "1", "--long-window", "3"])
        prices = pd.DataFrame({"Open": [1., 2., 3.], "Close": [1., 2., 3.]},
                              index=pd.date_range("2026-01-01", periods=3))
        with tempfile.TemporaryDirectory() as tmp, patch(
            "quant_flow.screening.get_prices", return_value=prices
        ), patch("quant_flow.main.run_stock", side_effect=[RuntimeError("chart failed"), None]) as report_stock, redirect_stdout(io.StringIO()) as console:
            output = screen_symbols(args, Path(tmp), report_stock=report_stock)
            self.assertEqual(report_stock.call_count, 2)
            report = read_csv(output / "screening.csv", keep_default_na=False)
            self.assertEqual(report.report_error.tolist(), ["chart failed", ""])
            self.assertEqual(load_symbols(output / "selected.csv"), args.symbol)
            self.assertIn("報表失敗 1 檔", console.getvalue())
            self.assertRegex(output.name, r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}_[0-9a-f]{8}$")
