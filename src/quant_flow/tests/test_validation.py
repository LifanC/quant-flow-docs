"""共用驗證需在所有金額呼叫端維持相同的型別及邊界保護。"""
from decimal import Decimal
import unittest

from quant_flow.validation import validate_decimal


class DecimalValidationTest(unittest.TestCase):
    def test_rejects_invalid_amounts_with_callers_message(self):
        for value in [0.1, None, Decimal('NaN'), Decimal('sNaN'),
                      Decimal('Infinity'), Decimal('-Infinity'), Decimal('-1')]:
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, '^金額錯誤$'):
                    validate_decimal(value, '金額錯誤')

    def test_cash_and_price_have_different_zero_boundaries(self):
        validate_decimal(Decimal('0'), '現金錯誤')
        validate_decimal(Decimal('0.01'), '價格錯誤', positive=True)
        with self.assertRaisesRegex(ValueError, '價格錯誤'):
            validate_decimal(Decimal('0'), '價格錯誤', positive=True)

    def test_rate_includes_zero_and_excludes_one(self):
        for value in ['0', '0.999999']:
            validate_decimal(Decimal(value), '費率錯誤', below_one=True)
        for value in ['-0.01', '1', '1.01']:
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, '費率錯誤'):
                    validate_decimal(Decimal(value), '費率錯誤', below_one=True)
