"""
Unit tests for EmailValidator.

These tests focus on testing EmailValidator in isolation,
testing individual methods and edge cases.
"""

import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from drivers.validator_contact_driver import EmailValidator
from contracts.validator_contract import ValidatorContract
from validation_base import ValidationResult, ValidationError, ValidationSeverity


class TestEmailValidatorUnit(unittest.TestCase):
    """Unit tests for EmailValidator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = EmailValidator()
    
    def test_validator_inherits_from_base_validator(self):
        """Test that EmailValidator inherits from BaseValidator."""
        from validation_base import BaseValidator
        self.assertIsInstance(self.validator, BaseValidator)
    
    def test_validator_implements_validator_contract(self):
        """Test that EmailValidator implements ValidatorContract."""
        self.assertIsInstance(self.validator, ValidatorContract)
    
    def test_validator_initialization(self):
        """Test EmailValidator initialization."""
        validator = EmailValidator()
        self.assertEqual(validator.name, "Email")
        self.assertIsInstance(validator._config, dict)
        self.assertIsInstance(validator._default_config, dict)
    
    def test_validator_has_email_pattern(self):
        """Test that EmailValidator has compiled email pattern."""
        self.assertTrue(hasattr(EmailValidator, '_EMAIL_PATTERN'))
        import re
        self.assertIsInstance(EmailValidator._EMAIL_PATTERN, re.Pattern)
    
    def test_validate_method_exists_and_callable(self):
        """Test that validate method exists and is callable."""
        self.assertTrue(hasattr(self.validator, 'validate'))
        self.assertTrue(callable(self.validator.validate))
    
    def test_validate_returns_validation_result(self):
        """Test that validate() always returns ValidationResult."""
        test_cases = [
            "valid@example.com",
            "invalid-email",
            None,
            "",
            123
        ]
        
        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                result = self.validator.validate(test_case)
                self.assertIsInstance(result, ValidationResult)
                self.assertEqual(result.validator_name, "Email")
    
    def test_validate_valid_email_basic(self):
        """Test validation of basic valid email."""
        result = self.validator.validate("test@example.com")
        
        self.assertTrue(result.is_valid)
        self.assertEqual(result.validator_name, "Email")
        self.assertIn("valid", result.message.lower())
        self.assertIn('clean_value', result.details)
        self.assertIn('local_part', result.details)
        self.assertIn('domain', result.details)
    
    def test_validate_email_case_normalization(self):
        """Test that email is normalized to lowercase."""
        result = self.validator.validate("  USER@EXAMPLE.COM  ")
        
        self.assertTrue(result.is_valid)
        self.assertEqual(result.details['clean_value'], 'user@example.com')
        self.assertEqual(result.details['local_part'], 'user')
        self.assertEqual(result.details['domain'], 'example.com')
    
    def test_validate_email_parts_extraction(self):
        """Test that email parts are correctly extracted."""
        result = self.validator.validate("user.name+tag@sub.domain.com")
        
        self.assertTrue(result.is_valid)
        self.assertEqual(result.details['local_part'], 'user.name+tag')
        self.assertEqual(result.details['domain'], 'sub.domain.com')
    
    def test_validate_empty_email(self):
        """Test validation of empty email."""
        result = self.validator.validate("")
        
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "EMAIL_REQUIRED")
        self.assertIn("required", result.message.lower())
    
    def test_validate_none_email(self):
        """Test validation of None email."""
        result = self.validator.validate(None)
        
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "EMAIL_REQUIRED")
    
    def test_validate_invalid_format_no_at(self):
        """Test validation of email without @ symbol."""
        result = self.validator.validate("invalid-email")
        
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "EMAIL_INVALID_FORMAT")
    
    def test_validate_invalid_format_no_domain(self):
        """Test validation of email without domain."""
        result = self.validator.validate("user@")
        
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "EMAIL_INVALID_FORMAT")
    
    def test_validate_local_part_too_long(self):
        """Test validation of email with local part too long (>64 chars)."""
        long_local = "a" * 65 + "@example.com"
        result = self.validator.validate(long_local)
        
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "EMAIL_LOCAL_TOO_LONG")
        self.assertIn('local_length', result.details)
        self.assertEqual(result.details['local_length'], 65)
    
    def test_validate_domain_too_long(self):
        """Test validation of email with domain too long (>253 chars)."""
        long_domain = "user@" + "a" * 250 + ".com"
        result = self.validator.validate(long_domain)
        
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "EMAIL_DOMAIN_TOO_LONG")
        self.assertIn('domain_length', result.details)
    
    def test_validate_consecutive_dots(self):
        """Test validation of email with consecutive dots."""
        result = self.validator.validate("user..name@example.com")
        
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "EMAIL_CONSECUTIVE_DOTS")
    
    def test_validate_local_part_starts_with_dot(self):
        """Test validation of email with local part starting with dot."""
        result = self.validator.validate(".user@example.com")
        
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "EMAIL_LOCAL_DOT_POSITION")
    
    def test_validate_local_part_ends_with_dot(self):
        """Test validation of email with local part ending with dot."""
        result = self.validator.validate("user.@example.com")
        
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "EMAIL_LOCAL_DOT_POSITION")
    
    def test_supports_data_type_method(self):
        """Test supports_data_type() method."""
        self.assertTrue(self.validator.supports_data_type(str))
        self.assertFalse(self.validator.supports_data_type(int))
        self.assertFalse(self.validator.supports_data_type(list))
        self.assertFalse(self.validator.supports_data_type(dict))
    
    def test_get_supported_config_keys_method(self):
        """Test get_supported_config_keys() method."""
        keys = self.validator.get_supported_config_keys()
        
        self.assertIsInstance(keys, list)
        self.assertIn('strict_mode', keys)
        self.assertIn('allow_smtputf8', keys)
    
    def test_configure_method(self):
        """Test configure() method."""
        result = self.validator.configure(strict_mode=True, allow_smtputf8=False)
        
        # Test method chaining
        self.assertEqual(result, self.validator)
        
        # Test configuration is stored
        config = self.validator.get_config()
        self.assertTrue(config['strict_mode'])
        self.assertFalse(config['allow_smtputf8'])
    
    def test_get_config_method(self):
        """Test get_config() method."""
        # Set some configuration
        self.validator.configure(strict_mode=True)
        
        config = self.validator.get_config()
        
        self.assertIsInstance(config, dict)
        self.assertIn('strict_mode', config)
        self.assertTrue(config['strict_mode'])
    
    def test_reset_config_method(self):
        """Test reset_config() method."""
        # Configure validator
        self.validator.configure(strict_mode=True, allow_smtputf8=True)
        
        # Reset configuration
        result = self.validator.reset_config()
        
        # Test method chaining
        self.assertEqual(result, self.validator)
        
        # Test configuration is reset to defaults
        config = self.validator.get_config()
        self.assertEqual(config, self.validator._default_config)
    
    def test_validation_result_has_raise_for_validation(self):
        """Test that ValidationResult has raise_for_validation method."""
        result = self.validator.validate("test@example.com")
        
        self.assertTrue(hasattr(result, 'raise_for_validation'))
        self.assertTrue(callable(result.raise_for_validation))
    
    def test_raise_for_validation_valid_email(self):
        """Test raise_for_validation() with valid email."""
        result = self.validator.validate("test@example.com")
        
        # Should not raise exception
        try:
            result.raise_for_validation()
        except ValidationError:
            self.fail("raise_for_validation() should not raise for valid email")
    
    def test_raise_for_validation_invalid_email(self):
        """Test raise_for_validation() with invalid email."""
        result = self.validator.validate("invalid-email")
        
        # Should raise ValidationError
        with self.assertRaises(ValidationError) as context:
            result.raise_for_validation()
        
        # Check exception details
        self.assertEqual(context.exception.error_code, result.error_code)
        self.assertEqual(context.exception.message, result.message)
        self.assertEqual(context.exception.severity, result.severity)


if __name__ == '__main__':
    unittest.main()
