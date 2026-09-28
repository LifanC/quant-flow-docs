import unittest

import pandas as pd

from quant_flow.data.normalizer import normalize_prices

class NormalizerTest(unittest.TestCase):
    def test_sort_dates_without_changing_input(self):
        prices = pd.DataFrame(
            {
                "Open": ["110", "100"],
                "Close": ["112", "102"],
            },
            index=pd.to_datetime([
                "2026-01-06",
                "2026-01-05",
            ]),
        )

        original = prices.copy(deep=True)

        result = normalize_prices(prices)

        self.assertTrue(result.index.is_monotonic_increasing)
        self.assertEqual(result["Open"].tolist(), [100.0, 110.0])

        pd.testing.assert_frame_equal(prices, original)

    def test_reject_missing_price(self):
        prices = pd.DataFrame(
            {
                "Open": [100.0, None],
                "Close": [102.0, 103.0],
            },
            index=pd.to_datetime([
                "2026-01-05",
                "2026-01-06",
            ]),
        )

        with self.assertRaisesRegex(ValueError, "Open 包含缺失價格"):
            normalize_prices(prices)


if __name__ == "__main__":
    unittest.main()