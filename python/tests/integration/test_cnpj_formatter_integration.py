"""
Unit tests for Brazilian CNPJ Formatter with integrated parsing functionality.

Tests the enhanced CNPJ formatter that includes cleaning, validation, and formatting
capabilities, replacing the need for separate CNPJParser functionality.
"""

import unittest

from drivers.formatter.formatter_brazilian_cnpj_driver import FormatterBrazilianCnpjDriver
from standards.core.base import ValidationError


class TestCnpjFormatterIntegration(unittest.TestCase):
    """Test CNPJ formatter with integrated parsing and validation."""

    def setUp(self):
        """Set up test fixtures."""
        self.formatter = FormatterBrazilianCnpjDriver()

    def test_clean_method_various_formats(self):
        """Test clean method with various input formats."""
        test_cases = [
            ("15.280.995/0001-69", "15280995000169"),
            ("15280995000169", "15280995000169"),
            ("  15 280 995 0001 69  ", "15280995000169"),
            ("15-280-995-0001-69", "15280995000169"),
            ("15.280.995.0001.69", "15280995000169"),
            ("CNPJ: 15.280.995/0001-69", "15280995000169"),
            ("15/280/995/0001/69", "15280995000169"),
        ]

        for input_cnpj, expected in test_cases:
            with self.subTest(input_cnpj=input_cnpj):
                result = self.formatter.clean(input_cnpj)
                self.assertEqual(result, expected)

    def test_format_method_consistency(self):
        """Test format method produces consistent output."""
        test_inputs = [
            "15.280.995/0001-69",
            "15280995000169",
            "  15 280 995 0001 69  ",
            "CNPJ: 15.280.995/0001-69",
        ]

        expected = "15.280.995/0001-69"

        for input_cnpj in test_inputs:
            with self.subTest(input_cnpj=input_cnpj):
                result = self.formatter.format(input_cnpj)
                self.assertEqual(result, expected)

    def test_is_valid_method(self):
        """Test is_valid method for various inputs."""
        valid_cases = [
            "15.280.995/0001-69",
            "15280995000169",
            "  15 280 995 0001 69  ",
        ]

        invalid_cases = [
            "",
            "123",
            "1234567890123",  # 13 digits
            "123456789012345",  # 15 digits
            "abcd.efg.hij/klmn-op",
            None,
        ]

        for valid_cnpj in valid_cases:
            with self.subTest(cnpj=valid_cnpj):
                self.assertTrue(self.formatter.is_valid(valid_cnpj))

        for invalid_cnpj in invalid_cases:
            with self.subTest(cnpj=invalid_cnpj):
                self.assertFalse(self.formatter.is_valid(invalid_cnpj))

    def test_strict_validation_mode(self):
        """Test strict validation mode behavior."""
        strict_formatter = FormatterBrazilianCnpjDriver().configure(strict_validation=True)

        # Valid CNPJ should work
        result = strict_formatter.clean("15.280.995/0001-69")
        self.assertEqual(result, "15280995000169")

        # Invalid CNPJ should raise exception
        with self.assertRaises(ValidationError):
            strict_formatter.clean("123")

        with self.assertRaises(ValidationError):
            strict_formatter.clean("")

        with self.assertRaises(ValidationError):
            strict_formatter.clean(None)

    def test_non_strict_validation_mode(self):
        """Test non-strict validation mode behavior."""
        lenient_formatter = FormatterBrazilianCnpjDriver().configure(strict_validation=False)

        # Empty input should return empty string
        self.assertEqual(lenient_formatter.clean(""), "")
        self.assertEqual(lenient_formatter.clean(None), "")

        # Short input should be padded
        result = lenient_formatter.clean("123")
        self.assertEqual(result, "00000000000123")

    def test_integration_with_company_drivers(self):
        """Test that the formatter integrates properly with company drivers."""
        from managers.formatter_manager import FormatterManager

        manager = FormatterManager()
        formatter = manager.load("brazilian_cnpj")

        # Test that the formatter has the new methods
        self.assertTrue(hasattr(formatter, 'clean'))
        self.assertTrue(hasattr(formatter, 'is_valid'))
        self.assertTrue(hasattr(formatter, 'format'))

        # Test functionality
        test_cnpj = "15.280.995/0001-69"
        clean_result = formatter.clean(test_cnpj)
        format_result = formatter.format(test_cnpj)
        valid_result = formatter.is_valid(test_cnpj)

        self.assertEqual(clean_result, "15280995000169")
        self.assertEqual(format_result, "15.280.995/0001-69")
        self.assertTrue(valid_result)


if __name__ == '__main__':
    unittest.main()
