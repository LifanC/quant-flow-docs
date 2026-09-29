import tempfile
import unittest
from pathlib import Path

import pandas as pd

from quant_flow.backtest.simulator import run_backtest
from quant_flow.data.normalizer import normalize_prices
from quant_flow.data.providers.csv_provider import load_prices
from quant_flow.strategy.moving_average import calculate_signals
from quant_flow.data.csv_format import write_csv

class CsvReplayTest(unittest.TestCase):
    def test_csv_replay_matches_original(self):
        prices = pd.DataFrame(
            {
                "Open": [100.0, 102.0, 104.0, 102.0, 100.0, 103.0],
                "Close": [101.0, 103.0, 105.0, 101.0, 99.0, 104.0],
            },
            index=pd.date_range(
                start="2026-01-05",
                periods=6,
                freq="B",
                tz="Asia/Taipei",
                name="Date",
            ),
        )

        original = normalize_prices(prices)

        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "input_prices.csv"

            original.to_csv(
                csv_path,
                index_label="Date",
                encoding="utf-8-sig",
            )

            restored = normalize_prices(load_prices(csv_path))

            write_csv(original, csv_path, index_label="Date")
            self.assertEqual(
                pd.read_csv(csv_path).columns.tolist(),
                ["Date（日期）", "Open（開盤價）", "Close（收盤價）"],
            )
            bilingual = normalize_prices(load_prices(csv_path))
            pd.testing.assert_frame_equal(restored, bilingual)

        original_result = self.run_strategy(original)
        restored_result = self.run_strategy(restored)

        # CSV 讀取器統一為 UTC，因此先對齊時區再比較。
        expected = original_result["Equity"].copy()
        expected.index = expected.index.tz_convert("UTC")

        pd.testing.assert_series_equal(
            expected,
            restored_result["Equity"],
            check_freq=False,
            check_exact=False,
            rtol=1e-10,
            atol=1e-12,
        )

    def run_strategy(self, prices: pd.DataFrame) -> pd.DataFrame:
        signals = calculate_signals(
            prices,
            short_window=2,
            long_window=3,
        )

        return run_backtest(
            signals,
            fee_rate=0.001,
            slippage_rate=0.001,
        )


if __name__ == "__main__":
    unittest.main()
