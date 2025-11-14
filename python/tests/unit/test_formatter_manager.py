"""
Unit tests for FormatterManager and formatter drivers.

Tests that the FormatterManager can instantiate formatter drivers correctly
and that all drivers implement the required interface.
"""

import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from managers.formatter_manager import FormatterManager
from drivers.formatter.formatter_brazilian_postalcode_driver import FormatterBrazilianPostalcodeDriver
from contracts.manager_contract import ManagerContract, DriverNotFoundError
from contracts.formatter_contract import FormatterContract, FormatterValidationError


class TestFormatterManager(unittest.TestCase):
    """Unit tests for FormatterManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = FormatterManager()
    
    def test_manager_implements_contract(self):
        """Test that FormatterManager implements ManagerContract."""
        self.assertIsInstance(self.manager, ManagerContract)
    
    def test_manager_has_drivers(self):
        """Test that FormatterManager has registered drivers."""
        drivers = self.manager.list_drivers()
        
        # Should have at least the Brazilian postal code formatter
        self.assertIn('brazilian_postalcode', drivers)
        self.assertGreaterEqual(len(drivers), 1)
    
    def test_manager_can_load_drivers(self):
        """Test that manager can load all registered drivers."""
        drivers = self.manager.list_drivers()
        
        for driver_name in drivers:
            with self.subTest(driver=driver_name):
                # Should not raise exception
                driver = self.manager.load(driver_name)
                
                # Should return a driver instance
                self.assertIsNotNone(driver)
                
                # Should have required methods
                self.assertTrue(hasattr(driver, 'format'))
                self.assertTrue(hasattr(driver, 'configure'))
                self.assertTrue(hasattr(driver, 'get_config'))
                self.assertTrue(hasattr(driver, 'name'))
    
    def test_manager_format_method(self):
        """Test manager's format method."""
        # Test with specific driver
        formatted = self.manager.format("88304053", driver="brazilian_postalcode")
        self.assertEqual(formatted, "88304-053")
        
        # Test with default driver
        self.manager.set_default_driver("brazilian_postalcode")
        formatted = self.manager.format("88304053")
        self.assertEqual(formatted, "88304-053")
    
    def test_manager_bulk_format(self):
        """Test manager's bulk format method."""
        values = ["88304053", "01310100", "20040020"]
        expected = ["88304-053", "01310-100", "20040-020"]
        
        formatted = self.manager.bulk_format(values, driver="brazilian_postalcode")
        self.assertEqual(formatted, expected)
    
    def test_manager_cache_functionality(self):
        """Test manager's cache functionality."""
        # Enable cache
        result = self.manager.enable_cache(True)
        self.assertEqual(result, self.manager)  # Method chaining
        
        # Format value (should cache)
        formatted1 = self.manager.format("88304053", driver="brazilian_postalcode")
        
        # Check cache stats
        stats = self.manager.get_cache_stats()
        self.assertTrue(stats['enabled'])
        self.assertEqual(stats['size'], 1)
        
        # Format same value (should use cache)
        formatted2 = self.manager.format("88304053", driver="brazilian_postalcode")
        self.assertEqual(formatted1, formatted2)
        
        # Clear cache
        self.manager.clear_cache()
        stats = self.manager.get_cache_stats()
        self.assertEqual(stats['size'], 0)
    
    def test_manager_error_handling(self):
        """Test manager error handling."""
        # Test with non-existent driver
        with self.assertRaises(DriverNotFoundError):
            self.manager.load("nonexistent_driver")
        
        # Test with invalid driver name in format
        with self.assertRaises(DriverNotFoundError):
            self.manager.format("88304053", driver="nonexistent_driver")
    
    def test_manager_is_valid_format(self):
        """Test manager's is_valid_format method."""
        # Valid values
        self.assertTrue(self.manager.is_valid_format("88304053", driver="brazilian_postalcode"))
        self.assertTrue(self.manager.is_valid_format(88304053, driver="brazilian_postalcode"))
        
        # Invalid values
        self.assertFalse(self.manager.is_valid_format("", driver="brazilian_postalcode"))
        self.assertFalse(self.manager.is_valid_format("abc", driver="brazilian_postalcode"))


class TestFormatterBrazilianPostalcodeDriver(unittest.TestCase):
    """Unit tests for FormatterBrazilianPostalcodeDriver."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.driver = FormatterBrazilianPostalcodeDriver()
    
    def test_driver_implements_formatter_contract(self):
        """Test that driver implements FormatterContract."""
        # Check that driver implements the contract
        self.assertIsInstance(self.driver, FormatterContract)

        # Check required methods from contract
        required_methods = ['format', 'configure', 'get_config', 'reset_config', 'is_valid_format']
        for method_name in required_methods:
            self.assertTrue(hasattr(self.driver, method_name))
            self.assertTrue(callable(getattr(self.driver, method_name)))

        # Check name property
        self.assertTrue(hasattr(self.driver, 'name'))
        self.assertIsInstance(self.driver.name, str)
        self.assertEqual(self.driver.name, "Brazilian Postal Code")

        # Check contract methods work
        supported_types = self.driver.get_supported_types()
        self.assertIsInstance(supported_types, list)

        output_format = self.driver.get_output_format()
        self.assertIsInstance(output_format, str)
    
    def test_format_string_inputs(self):
        """Test formatting various string inputs."""
        test_cases = [
            ("88304053", "88304-053"),
            ("88304-053", "88304-053"),
            ("88.304-053", "88304-053"),
            ("88 304 053", "88304-053"),
            ("88.304.053", "88304-053"),
            ("  88304053  ", "88304-053"),  # With spaces
        ]
        
        for input_value, expected in test_cases:
            with self.subTest(input=input_value):
                result = self.driver.format(input_value)
                self.assertEqual(result, expected)
    
    def test_format_integer_input(self):
        """Test formatting integer input."""
        result = self.driver.format(88304053)
        self.assertEqual(result, "88304-053")

        # Test with another 8-digit number
        result = self.driver.format(20040020)
        self.assertEqual(result, "20040-020")


    def test_format_integer_with_leading_zeros(self):
        """Test formatting integer that would have leading zeros as string."""
        # Test with 7-digit number (would be "01310100" as string with leading zero)
        # Brazilian CEPs must have exactly 8 digits - 7 digits is invalid
        with self.assertRaises(FormatterValidationError) as context:
            self.driver.format(1310100)

        # Should raise validation error for invalid length
        self.assertEqual(context.exception.error_code, "FORMATTER_INVALID_LENGTH")
        self.assertIn("must have exactly 8 digits", str(context.exception))

        # Test with proper 8-digit CEP (with leading zero when converted to string)
        # 01310100 as integer becomes 1310100, but we need to test with string "01310100"
        result = self.driver.format("01310100")
        self.assertEqual(result, "01310-100")  # Properly formatted 8-digit CEP
    
    def test_format_invalid_inputs(self):
        """Test formatting invalid inputs."""
        invalid_inputs = [
            "",           # Empty string
            "   ",        # Only spaces
            "abc",        # Non-numeric
            "123",        # Too short
            "123456789",  # Too long
            None,         # None value
        ]
        
        for invalid_input in invalid_inputs:
            with self.subTest(input=invalid_input):
                with self.assertRaises(FormatterValidationError):
                    self.driver.format(invalid_input)
    
    def test_driver_configuration(self):
        """Test driver configuration."""
        # Get initial config
        initial_config = self.driver.get_config()
        self.assertIsInstance(initial_config, dict)
        self.assertTrue(initial_config['strict_validation'])
        
        # Configure driver
        result = self.driver.configure(strict_validation=False, allow_partial=True)
        self.assertEqual(result, self.driver)  # Method chaining
        
        # Verify configuration applied
        new_config = self.driver.get_config()
        self.assertFalse(new_config['strict_validation'])
        self.assertTrue(new_config['allow_partial'])
        
        # Test that partial CEPs are now invalid (allow_partial is deprecated)
        # Brazilian CEPs must have exactly 8 digits to be valid
        with self.assertRaises(FormatterValidationError) as context:
            self.driver.format("88304")

        self.assertEqual(context.exception.error_code, "FORMATTER_INVALID_LENGTH")
        self.assertIn("must have exactly 8 digits", str(context.exception))
        
        # Reset config
        self.driver.reset_config()
        reset_config = self.driver.get_config()
        self.assertTrue(reset_config['strict_validation'])  # Back to default
    
    def test_is_valid_format_method(self):
        """Test is_valid_format method."""
        # Valid formats
        valid_inputs = ["88304053", "88304-053", "88.304-053", 88304053]
        for valid_input in valid_inputs:
            with self.subTest(input=valid_input):
                self.assertTrue(self.driver.is_valid_format(valid_input))
        
        # Invalid formats
        invalid_inputs = ["", "abc", "123", "123456789", None]
        for invalid_input in invalid_inputs:
            with self.subTest(input=invalid_input):
                self.assertFalse(self.driver.is_valid_format(invalid_input))


if __name__ == '__main__':
    unittest.main()
