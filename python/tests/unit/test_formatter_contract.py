"""
Unit tests for FormatterContract to ensure contract compliance.

Tests that the FormatterContract works correctly and can be used
to create standardized formatter drivers.
"""

import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from contracts.formatter_contract import (
    FormatterContract, 
    AbstractFormatterContract, 
    FormatterError,
    FormatterValidationError,
    FormatterConfigurationError
)
from drivers.formatter.formatter_brazilian_postalcode_driver import FormatterBrazilianPostalcodeDriver


class TestFormatterContract(unittest.TestCase):
    """Unit tests for FormatterContract."""
    
    def test_formatter_contract_is_abstract(self):
        """Test that FormatterContract cannot be instantiated directly."""
        with self.assertRaises(TypeError):
            FormatterContract()
    
    def test_abstract_formatter_contract_can_be_subclassed(self):
        """Test that AbstractFormatterContract can be subclassed."""
        
        class TestFormatter(AbstractFormatterContract):
            def format(self, value):
                return str(value).upper()
        
        formatter = TestFormatter()
        
        # Test that it implements the contract
        self.assertIsInstance(formatter, FormatterContract)
        
        # Test default implementations work
        self.assertIsInstance(formatter.name, str)
        self.assertIsInstance(formatter.get_config(), dict)
        self.assertIsInstance(formatter.get_supported_types(), list)
        self.assertIsInstance(formatter.get_output_format(), str)
        
        # Test format method works
        result = formatter.format("test")
        self.assertEqual(result, "TEST")
    
    def test_formatter_contract_methods_are_abstract(self):
        """Test that required methods are abstract in FormatterContract."""
        
        class IncompleteFormatter(FormatterContract):
            # Missing format method implementation
            @property
            def name(self):
                return "Incomplete"
            
            def configure(self, **kwargs):
                return self
            
            def get_config(self):
                return {}
        
        # Should not be able to instantiate without implementing format
        with self.assertRaises(TypeError):
            IncompleteFormatter()
    
    def test_brazilian_postalcode_driver_implements_contract(self):
        """Test that Brazilian postal code driver implements FormatterContract."""
        driver = FormatterBrazilianPostalcodeDriver()
        
        # Test contract compliance
        self.assertIsInstance(driver, FormatterContract)
        self.assertIsInstance(driver, AbstractFormatterContract)
        
        # Test all contract methods exist and are callable
        contract_methods = ['format', 'configure', 'get_config', 'reset_config', 'is_valid_format']
        for method_name in contract_methods:
            self.assertTrue(hasattr(driver, method_name))
            self.assertTrue(callable(getattr(driver, method_name)))
        
        # Test contract properties
        self.assertIsInstance(driver.name, str)
        self.assertEqual(driver.name, "Brazilian Postal Code")
        
        # Test contract method implementations
        config = driver.get_config()
        self.assertIsInstance(config, dict)
        
        supported_types = driver.get_supported_types()
        self.assertIsInstance(supported_types, list)
        self.assertIn(str, supported_types)
        self.assertIn(int, supported_types)
        
        output_format = driver.get_output_format()
        self.assertIsInstance(output_format, str)
        
        # Test format method (core contract requirement)
        result = driver.format("88304053")
        self.assertEqual(result, "88304-053")
        
        # Test is_valid_format method
        self.assertTrue(driver.is_valid_format("88304053"))
        self.assertFalse(driver.is_valid_format("invalid"))
    
    def test_formatter_exceptions(self):
        """Test formatter exception classes."""
        # Test base exception
        error = FormatterError("Test error", "TEST_CODE")
        self.assertEqual(str(error), "Test error")
        self.assertEqual(error.error_code, "TEST_CODE")
        
        # Test validation exception
        validation_error = FormatterValidationError("Validation failed", "VALIDATION_ERROR")
        self.assertIsInstance(validation_error, FormatterError)
        self.assertEqual(str(validation_error), "Validation failed")
        self.assertEqual(validation_error.error_code, "VALIDATION_ERROR")
        
        # Test configuration exception
        config_error = FormatterConfigurationError("Config error", "CONFIG_ERROR")
        self.assertIsInstance(config_error, FormatterError)
        self.assertEqual(str(config_error), "Config error")
        self.assertEqual(config_error.error_code, "CONFIG_ERROR")
    
    def test_contract_ensures_consistent_interface(self):
        """Test that contract ensures consistent interface across formatters."""
        
        # Create a mock formatter using the contract
        class MockFormatter(AbstractFormatterContract):
            def format(self, value):
                return f"MOCK:{value}"
        
        mock_formatter = MockFormatter()
        brazilian_formatter = FormatterBrazilianPostalcodeDriver()
        
        # Both should have the same interface
        common_methods = ['format', 'configure', 'get_config', 'reset_config', 'is_valid_format']
        
        for method_name in common_methods:
            # Both should have the method
            self.assertTrue(hasattr(mock_formatter, method_name))
            self.assertTrue(hasattr(brazilian_formatter, method_name))
            
            # Both methods should be callable
            self.assertTrue(callable(getattr(mock_formatter, method_name)))
            self.assertTrue(callable(getattr(brazilian_formatter, method_name)))
        
        # Both should implement FormatterContract
        self.assertIsInstance(mock_formatter, FormatterContract)
        self.assertIsInstance(brazilian_formatter, FormatterContract)
        
        # Both should have name property
        self.assertIsInstance(mock_formatter.name, str)
        self.assertIsInstance(brazilian_formatter.name, str)
        
        # Test that format method works on both
        mock_result = mock_formatter.format("test")
        self.assertEqual(mock_result, "MOCK:test")
        
        brazilian_result = brazilian_formatter.format("88304053")
        self.assertEqual(brazilian_result, "88304-053")


if __name__ == '__main__':
    unittest.main()
