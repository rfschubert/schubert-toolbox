"""
Integration tests for ValidatorManager.

These tests focus on testing ValidatorManager integration with
real validators and the complete validation workflow.
"""

import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from managers.validator_manager import ValidatorManager
from drivers import ValidatorDriver
from contracts.manager_contract import DriverNotFoundError, DriverLoadError
from contracts.validator_contract import ValidatorContract
from validation_base import ValidationResult, ValidationError


class TestValidatorManagerIntegration(unittest.TestCase):
    """Integration tests for ValidatorManager with real validators."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = ValidatorManager()
    
    def test_manager_loads_real_email_validator(self):
        """Test that manager loads real EmailValidator and it works."""
        # Load email validator
        email_validator = self.manager.load("email")
        
        # Verify it's a ValidatorContract
        self.assertIsInstance(email_validator, ValidatorContract)
        
        # Test it can validate
        result = email_validator.validate("test@example.com")
        self.assertIsInstance(result, ValidationResult)
        self.assertTrue(result.is_valid)
    
    def test_manager_loads_real_cpf_validator(self):
        """Test that manager loads real CPFValidator and it works."""
        # Load CPF validator
        cpf_validator = self.manager.load("cpf")
        
        # Verify it's a ValidatorContract
        self.assertIsInstance(cpf_validator, ValidatorContract)
        
        # Test it can validate
        result = cpf_validator.validate("12345678901")
        self.assertIsInstance(result, ValidationResult)
        # Note: This might be invalid CPF, but should return a result
    
    def test_manager_validate_method_with_enum(self):
        """Test manager validate() method with ValidatorDriver enum."""
        # Test valid email
        result = self.manager.validate("test@example.com", ValidatorDriver.EMAIL)
        self.assertIsInstance(result, ValidationResult)
        self.assertTrue(result.is_valid)
        
        # Test invalid email
        result = self.manager.validate("invalid-email", ValidatorDriver.EMAIL)
        self.assertIsInstance(result, ValidationResult)
        self.assertFalse(result.is_valid)
    
    def test_manager_validate_or_raise_method(self):
        """Test manager validate_or_raise() convenience method."""
        # Valid data should return result
        result = self.manager.validate_or_raise("test@example.com", ValidatorDriver.EMAIL)
        self.assertIsInstance(result, ValidationResult)
        self.assertTrue(result.is_valid)
        
        # Invalid data should raise ValidationError
        with self.assertRaises(ValidationError):
            self.manager.validate_or_raise("invalid-email", ValidatorDriver.EMAIL)
    
    def test_manager_bulk_validate_method(self):
        """Test manager bulk_validation() method."""
        validations = [
            ("test@example.com", ValidatorDriver.EMAIL),
            ("12345678901", ValidatorDriver.CPF),
            ("invalid-email", ValidatorDriver.EMAIL)
        ]
        
        results = self.manager.bulk_validation(validations, halt_on_failure=False)
        
        self.assertEqual(len(results), 3)
        self.assertTrue(results[0].is_valid)  # Valid email
        # CPF might be valid or invalid, but should have result
        self.assertFalse(results[2].is_valid)  # Invalid email
    
    def test_manager_bulk_validate_or_raise_method(self):
        """Test manager bulk_validate_or_raise() method."""
        # All valid data should work
        try:
            results = self.manager.bulk_validate_or_raise([
                ("test@example.com", ValidatorDriver.EMAIL)
            ])
            self.assertEqual(len(results), 1)
            self.assertTrue(results[0].is_valid)
        except ValidationError:
            self.fail("bulk_validate_or_raise should not raise for valid data")
        
        # Invalid data should raise on first failure
        with self.assertRaises(ValidationError):
            self.manager.bulk_validate_or_raise([
                ("test@example.com", ValidatorDriver.EMAIL),
                ("invalid-email", ValidatorDriver.EMAIL)  # This should fail
            ])
    
    def test_manager_chain_validation_integration(self):
        """Test manager chain_validation() integration."""
        chain = self.manager.chain_validation("test@example.com")
        
        # Load validators and add to chain
        email_validator = self.manager.load("email")
        
        results = (
            chain.validate(email_validator)
            .halt_on_failure(False)
            .execute()
        )
        
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].is_valid)
        self.assertTrue(chain.is_valid())
    
    def test_manager_with_validator_configuration(self):
        """Test manager loading validators with configuration."""
        # Load email validator with configuration
        email_validator = self.manager.load("email", strict_mode=True)
        
        # Verify configuration was applied
        config = email_validator.get_config()
        self.assertIn('strict_mode', config)
        self.assertTrue(config['strict_mode'])
        
        # Test validation still works
        result = email_validator.validate("test@example.com")
        self.assertTrue(result.is_valid)
    
    def test_manager_cache_integration(self):
        """Test manager caching integration."""
        # Enable cache
        self.manager.enable_cache(True)
        
        # First validation (should be cached)
        result1 = self.manager.validate("test@example.com", ValidatorDriver.EMAIL)
        
        # Second validation (should come from cache)
        result2 = self.manager.validate("test@example.com", ValidatorDriver.EMAIL)
        
        # Results should be equivalent
        self.assertEqual(result1.is_valid, result2.is_valid)
        self.assertEqual(result1.validator_name, result2.validator_name)
        
        # Cache should have entries
        stats = self.manager.get_cache_stats()
        self.assertTrue(stats['enabled'])
        self.assertGreater(stats['size'], 0)
    
    def test_manager_error_handling_integration(self):
        """Test manager error handling with real scenarios."""
        # Test loading non-existent driver
        with self.assertRaises(DriverNotFoundError) as context:
            self.manager.load("nonexistent_driver")
        
        self.assertEqual(context.exception.driver_name, "nonexistent_driver")
        self.assertIsInstance(context.exception.available_drivers, list)
        self.assertGreater(len(context.exception.available_drivers), 0)
    
    def test_manager_driver_registration_integration(self):
        """Test manager driver registration and usage."""
        # Create a simple mock validator
        class MockValidator:
            def __init__(self):
                self.name = "Mock"
            
            def validate(self, data):
                from validation_base import ValidationResult
                return ValidationResult(
                    is_valid=True,
                    validator_name=self.name,
                    data=data,
                    message="Mock validation passed"
                )
            
            def configure(self, **kwargs):
                return self
            
            def get_config(self):
                return {}
            
            def reset_config(self):
                return self
            
            def supports_data_type(self, data_type):
                return True
            
            def get_supported_config_keys(self):
                return []
        
        # Register mock validator
        self.manager.register_driver("mock", MockValidator, description="Mock validator")
        
        # Verify it's registered
        self.assertTrue(self.manager.has_driver("mock"))
        
        # Load and use it
        mock_validator = self.manager.load("mock")
        result = mock_validator.validate("test_data")
        
        self.assertTrue(result.is_valid)
        self.assertEqual(result.validator_name, "Mock")
        
        # Clean up
        self.manager.unregister_driver("mock")
        self.assertFalse(self.manager.has_driver("mock"))
    
    def test_end_to_end_validation_workflow(self):
        """Test complete end-to-end validation workflow."""
        # Scenario: Validate user registration data
        user_data = {
            'email': 'user@example.com',
            'backup_email': 'backup@example.com'
        }
        
        validation_results = []
        
        # Validate each field
        for field, value in user_data.items():
            try:
                result = self.manager.validate_or_raise(value, ValidatorDriver.EMAIL)
                validation_results.append((field, True, result.details.get('clean_value')))
            except ValidationError as e:
                validation_results.append((field, False, str(e)))
        
        # All should be valid
        self.assertEqual(len(validation_results), 2)
        self.assertTrue(all(result[1] for result in validation_results))
        
        # Check cleaned values
        self.assertEqual(validation_results[0][2], 'user@example.com')
        self.assertEqual(validation_results[1][2], 'backup@example.com')


if __name__ == '__main__':
    unittest.main()
