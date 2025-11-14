"""
Unit tests for postal code drivers.

Tests that all drivers implement the PostalCodeDriver interface correctly
and that the PostalCodeManager can instantiate all of them.
Uses VCR cassettes to avoid real API calls during testing.
"""

import unittest
import sys
import os
from pathlib import Path
import vcr

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from managers.postalcode_manager import PostalCodeManager
from standards.address import Address, Country
# Import ValidationError from one of the drivers (they all have the same local class)
from drivers.postalcode.postalcode_viacep_driver import ValidationError


class TestPostalCodeDrivers(unittest.TestCase):
    """Unit tests for postal code drivers and manager integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = PostalCodeManager()
        
        # Create cassettes directory
        self.cassettes_dir = Path(__file__).parent.parent / "integration" / "cassettes"
        self.cassettes_dir.mkdir(parents=True, exist_ok=True)
    
    def test_manager_has_drivers(self):
        """Test that PostalCodeManager has registered drivers."""
        drivers = self.manager.list_drivers()
        
        # Should have at least the basic drivers
        expected_drivers = ['viacep', 'widenet', 'brasilapi']
        
        for driver_name in expected_drivers:
            with self.subTest(driver=driver_name):
                self.assertIn(driver_name, drivers, f"Driver '{driver_name}' not found in manager")
        
        self.assertGreaterEqual(len(drivers), 3, "Manager should have at least 3 drivers")
    
    def test_all_drivers_implement_interface(self):
        """Test that all drivers implement the required interface."""
        drivers = self.manager.list_drivers()
        
        required_methods = ['get', 'configure', 'get_config']
        
        for driver_name in drivers:
            with self.subTest(driver=driver_name):
                # Load driver
                driver = self.manager.load(driver_name)
                
                # Check required methods exist
                for method_name in required_methods:
                    self.assertTrue(
                        hasattr(driver, method_name),
                        f"Driver '{driver_name}' missing method '{method_name}'"
                    )
                    self.assertTrue(
                        callable(getattr(driver, method_name)),
                        f"Driver '{driver_name}' method '{method_name}' is not callable"
                    )
                
                # Check driver has name attribute
                self.assertTrue(hasattr(driver, 'name'), f"Driver '{driver_name}' missing 'name' attribute")
                self.assertIsInstance(driver.name, str, f"Driver '{driver_name}' name should be string")
    
    def test_driver_configuration(self):
        """Test that all drivers support configuration."""
        drivers = self.manager.list_drivers()
        
        for driver_name in drivers:
            with self.subTest(driver=driver_name):
                driver = self.manager.load(driver_name)
                
                # Get initial config
                initial_config = driver.get_config()
                self.assertIsInstance(initial_config, dict, f"Driver '{driver_name}' config should be dict")
                
                # Test configure method returns self (method chaining)
                result = driver.configure(timeout=30)
                self.assertEqual(result, driver, f"Driver '{driver_name}' configure should return self")
                
                # Test configuration was applied
                new_config = driver.get_config()
                self.assertEqual(new_config['timeout'], 30, f"Driver '{driver_name}' timeout not configured")
    
    @vcr.use_cassette('tests/integration/cassettes/viacep_valid_cep.yaml')
    def test_viacep_driver_returns_address(self):
        """Test that ViaCEP driver returns Address object."""
        driver = self.manager.load('viacep')
        address = driver.get('88.304-053')
        
        # Verify return type
        self.assertIsInstance(address, Address)
        
        # Verify address has required fields
        self.assertIsNotNone(address.postal_code)
        self.assertIsNotNone(address.locality)
        self.assertIsNotNone(address.administrative_area_1)
        self.assertIsNotNone(address.country)
        
        # Verify country is Brazil
        self.assertEqual(address.country.code, 'BR')
        
        # Verify verification status
        self.assertTrue(address.is_verified)
        self.assertEqual(address.verification_source, 'viacep')
    
    def test_driver_error_handling(self):
        """Test that drivers handle invalid postal codes correctly."""
        drivers = self.manager.list_drivers()
        
        invalid_ceps = [
            "",           # Empty
            "123",        # Too short
            "123456789",  # Too long
            "abcd-efgh",  # Non-numeric
        ]
        
        for driver_name in drivers:
            driver = self.manager.load(driver_name)
            
            for invalid_cep in invalid_ceps:
                with self.subTest(driver=driver_name, cep=invalid_cep):
                    with self.assertRaises(Exception) as context:
                        driver.get(invalid_cep)
                    # Should raise some kind of ValidationError (could be local or imported)
                    self.assertTrue(
                        "ValidationError" in str(type(context.exception)) or
                        "validation" in str(context.exception).lower() or
                        "invalid" in str(context.exception).lower() or
                        "format" in str(context.exception).lower()
                    )
    
    def test_manager_can_load_all_drivers(self):
        """Test that manager can successfully load all registered drivers."""
        drivers = self.manager.list_drivers()
        
        for driver_name in drivers:
            with self.subTest(driver=driver_name):
                # Should not raise exception
                driver = self.manager.load(driver_name)
                
                # Should return a driver instance
                self.assertIsNotNone(driver)
                
                # Should have the expected name (normalize both sides for comparison)
                normalized_driver_name = driver.name.lower().replace(' ', '').replace('-', '')
                normalized_expected_name = driver_name.replace('_', '').replace('-', '')
                self.assertEqual(normalized_driver_name, normalized_expected_name)
    
    def test_manager_driver_configuration(self):
        """Test that manager can configure drivers during load."""
        drivers = self.manager.list_drivers()
        
        for driver_name in drivers:
            with self.subTest(driver=driver_name):
                # Load with configuration
                driver = self.manager.load(driver_name, timeout=60, retries=5)
                
                # Verify configuration was applied
                config = driver.get_config()
                self.assertEqual(config['timeout'], 60)
                self.assertEqual(config['retries'], 5)
    
    def test_driver_names_follow_convention(self):
        """Test that driver names follow the expected convention."""
        drivers = self.manager.list_drivers()
        
        # Expected driver names based on our implementations
        expected_names = {
            'viacep': 'ViaCEP',
            'widenet': 'WideNet', 
            'brasilapi': 'BrasilAPI'
        }
        
        for driver_name in drivers:
            if driver_name in expected_names:
                with self.subTest(driver=driver_name):
                    driver = self.manager.load(driver_name)
                    expected_display_name = expected_names[driver_name]
                    self.assertEqual(driver.name, expected_display_name)


if __name__ == '__main__':
    unittest.main()
