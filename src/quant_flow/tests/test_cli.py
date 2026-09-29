import json
import tempfile
import unittest
from pathlib import Path
from quant_flow.cli import parse_args
import io
from contextlib import redirect_stderr


class CliTest(unittest.TestCase):
    def test_symbols(self):
        self.assertEqual(parse_args([]).symbol, ["2330.TW"])
        self.assertEqual(parse_args(["--symbol", "0050.TW"]).symbol, ["0050.TW"])
        args = parse_args(["--symbol", "2330.TW", "0050.TW", "--period", "2y"])
        self.assertEqual(args.symbol, ["2330.TW", "0050.TW"])
        self.assertEqual(args.period, "2y")

    def test_multiple_symbols_reject_single_source(self):
        for option in ("--input-csv", "--config"):
            with self.subTest(option=option), redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as caught:
                    parse_args(["--symbol", "2330.TW", "0050.TW", option, "source"])
                self.assertEqual(caught.exception.code, 2)

    def test_config_loads_parameters_and_csv_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = Path(temp_dir)

            csv_path = run_dir / "input_prices.csv"
            csv_path.write_text(
                "Date,Open,Close\n2026-01-05,100,101\n",
                encoding="utf-8",
            )

            config = {
                "symbol": "0050.TW",
                "period": "2y",
                "short_window": 10,
                "long_window": 30,
                "fee_rate": 0.002,
                "slippage_rate": 0.0005,
                "data": {
                    "file": "input_prices.csv",
                },
            }

            config_path = run_dir / "config.json"
            config_path.write_text(
                json.dumps(config),
                encoding="utf-8",
            )

            args = parse_args([
                "--config",
                str(config_path),
            ])

            self.assertEqual(args.symbol, ["0050.TW"])
            self.assertEqual(args.short_window, 10)
            self.assertEqual(args.long_window, 30)
            self.assertAlmostEqual(args.fee_rate, 0.002)
            self.assertAlmostEqual(args.slippage_rate, 0.0005)

            self.assertEqual(
                args.input_csv.resolve(),
                csv_path.resolve(),
            )

            self.assertIsNone(args.period)

    def test_reject_invalid_windows(self):
        error_output = io.StringIO()

        with redirect_stderr(error_output):
            with self.assertRaises(SystemExit) as caught:
                parse_args([
                    "--short-window", "30",
                    "--long-window", "10",
                ])

        self.assertEqual(caught.exception.code, 2)

        self.assertIn(
            "均線週期必須符合",
            error_output.getvalue(),
        )

    def test_reject_negative_fee(self):
        error_output = io.StringIO()

        with redirect_stderr(error_output):
            with self.assertRaises(SystemExit) as caught:
                parse_args([
                    "--fee-rate", "-0.001",
                ])

        self.assertEqual(caught.exception.code, 2)

        self.assertIn(
            "費率必須非負",
            error_output.getvalue(),
        )

    def test_reject_invalid_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"

            # 刻意寫入不完整的 JSON。
            config_path.write_text(
                '{"symbol":',
                encoding="utf-8",
            )

            error_output = io.StringIO()

            with redirect_stderr(error_output):
                with self.assertRaises(SystemExit) as caught:
                    parse_args([
                        "--config",
                        str(config_path),
                    ])

            self.assertEqual(caught.exception.code, 2)
            self.assertIn(
                "無法載入設定檔",
                error_output.getvalue(),
            )

    def test_reject_missing_csv(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"

            config = {
                "symbol": "2330.TW",
                "short_window": 5,
                "long_window": 20,
                "fee_rate": 0.001,
                "slippage_rate": 0.001,
                "data": {
                    "file": "missing_prices.csv",
                },
            }

            config_path.write_text(
                json.dumps(config),
                encoding="utf-8",
            )

            # 故意不建立 missing_prices.csv。
            error_output = io.StringIO()

            with redirect_stderr(error_output):
                with self.assertRaises(SystemExit) as caught:
                    parse_args([
                        "--config",
                        str(config_path),
                    ])

            self.assertEqual(caught.exception.code, 2)
            self.assertIn(
                "找不到股價檔案",
                error_output.getvalue(),
            )

if __name__ == "__main__":
    unittest.main()
