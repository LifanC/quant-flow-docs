import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from quant_flow.cli import parse_args
from quant_flow.data.symbols import stock_args
from quant_flow.screening import screen_symbols


class WatchlistOptionsTest(unittest.TestCase):
    def test_csv_excel_screen_and_reimport(self):
        with tempfile.TemporaryDirectory() as tmp:
            frame = pd.DataFrame({
                "symbol": ["0050", "2330.TW"], "period": ["2y", ""],
                "short_window": [1, ""], "long_window": [3, ""],
                "fee_rate": [.002, ""], "slippage_rate": [0, ""],
            })
            for suffix in (".csv", ".xlsx"):
                path = Path(tmp) / ("stocks" + suffix)
                if suffix == ".csv":
                    frame.to_csv(path, index=False)
                else:
                    frame.to_excel(path, index=False)
                args = parse_args(["--symbols-file", str(path), "--screen", "trend",
                                   "--short-window", "2", "--long-window", "4"])
                first = stock_args(args, "0050.TW")
                second = stock_args(args, "2330.TW")
                self.assertEqual((first.period, first.short_window, first.long_window,
                                  first.fee_rate, first.slippage_rate), ("2y", 1, 3, .002, 0))
                self.assertEqual((second.period, second.short_window, second.long_window,
                                  second.fee_rate), ("1y", 2, 4, .001))
                prices = pd.DataFrame({"Open": [1., 2., 3., 4.], "Close": [1., 2., 3., 4.]},
                                      index=pd.date_range("2026-01-01", periods=4))
                with patch("quant_flow.screening.get_prices", return_value=prices) as fetch, patch(
                    "quant_flow.main.run_stock"
                ) as report, redirect_stdout(io.StringIO()):
                    output = screen_symbols(args, Path(tmp), report_stock=report)
                self.assertEqual([c.kwargs["period"] for c in fetch.call_args_list], ["2y", "1y"])
                self.assertEqual([c.args[0].short_window for c in report.call_args_list], [1, 2])
                self.assertEqual([c.args[0].fee_rate for c in report.call_args_list], [.002, .001])
                reused = parse_args(["--symbols-file", str(output / "selected.csv")])
                self.assertEqual(stock_args(reused, "0050.TW").long_window, 3)
                self.assertEqual(stock_args(reused, "2330.TW").short_window, 2)

    def test_invalid_options(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "stocks.csv"
            for field, value in (("period", "7y"), ("short_window", "1.5"),
                                 ("short_window", "20"), ("fee_rate", "nan"),
                                 ("fee_rate", "-1"), ("slippage_rate", "inf")):
                path.write_text(f"symbol,{field}\n2330.TW,{value}\n", encoding="utf-8")
                with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                    parse_args(["--symbols-file", str(path)])

    def test_plain_backtest_uses_individual_options(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "stocks.csv"
            path.write_text("symbol,short_window\n0050.TW,10\n2330.TW,\n", encoding="utf-8")
            args = parse_args(["--symbols-file", str(path)])
            with patch("quant_flow.main.parse_args", return_value=args), patch("quant_flow.main.run_stock") as run:
                from quant_flow.main import main
                main()
            self.assertEqual([c.args[0].short_window for c in run.call_args_list], [10, 5])
