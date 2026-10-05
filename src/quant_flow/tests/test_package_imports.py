"""套件入口必須提供原物件，且不同匯入起點不能引發循環依賴。"""
import importlib
import subprocess
import sys
import unittest


class PackageImportsTest(unittest.TestCase):
    def test_public_exports_are_original_objects(self):
        exports = {
            "orders": {"Order": "order", "OrderSide": "order"},
            "fills": {"Fill": "fill", "simulate_market_order": "simulator"},
            "positions": {"Position": "position"},
            "portfolio": {"Portfolio": "portfolio", "validate_fill": "risk",
                          "calculate_buy_quantity": "sizing"},
            "strategy": {"calculate_signals": "moving_average"},
            "signals": {"generate_trade_events": "signal"},
            "backtest": {"run_account_backtest": "account_simulator",
                         "execute_target_position": "execution", "run_backtest": "simulator"},
            "performance": {"calculate_drawdown": "metrics", "calculate_metrics": "metrics",
                            "run_buy_and_hold": "benchmark"},
            "data": {"normalize_prices": "normalizer", "read_csv": "csv_format",
                     "write_csv": "csv_format", "load_symbols": "symbols",
                     "load_watchlist": "symbols", "stock_args": "symbols"},
            "data.providers": {"get_prices": "yahoo_finance", "load_prices": "csv_provider"},
            "reporting": {"save_equity_chart": "charts", "export_reports": "exporter",
                          "export_trades": "exporter", "export_chinese_guide": "guide"},
        }
        for package, names in exports.items():
            entry = importlib.import_module(f"quant_flow.{package}")
            self.assertEqual(set(entry.__all__), set(names))
            for name, module in names.items():
                with self.subTest(package=package, name=name):
                    original = importlib.import_module(f"quant_flow.{package}.{module}")
                    self.assertIs(getattr(entry, name), getattr(original, name))

    def test_import_order_in_fresh_interpreters(self):
        # 已載入模組會遮蔽循環匯入，因此每個起點需獨立 Python 程序。
        for first in ["fills.fill", "orders.executor", "portfolio.risk", "backtest"]:
            with self.subTest(first=first):
                result = subprocess.run(
                    [sys.executable, "-c",
                     f"import quant_flow.{first}; import quant_flow.main"],
                    capture_output=True, text=True, timeout=30,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, "")
