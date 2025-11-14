"""
Integration tests for all postal code drivers.

Tests real API calls using VCR cassettes to ensure all drivers work correctly
with the same CEP and return consistent Address objects.
"""

import unittest
import sys
import os
from pathlib import Path
import vcr

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from managers.postalcode_manager import PostalCodeManager
from standards.address import Address
from validation_base import ValidationError


class TestAllDriversIntegration(unittest.TestCase):
    """Integration tests for all postal code drivers."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = PostalCodeManager()
        self.test_cep = "88304-053"  # Itajaí, SC - known working CEP
        
        # Create cassettes directory
        self.cassettes_dir = Path(__file__).parent / "cassettes"
        self.cassettes_dir.mkdir(exist_ok=True)
    
    @vcr.use_cassette('tests/integration/cassettes/all_drivers_integration.yaml')
    def test_all_drivers_return_address_for_valid_cep(self):
        """Test that all drivers return Address objects for valid CEP."""
        drivers = self.manager.list_drivers()
        addresses = {}
        
        for driver_name in drivers:
            with self.subTest(driver=driver_name):
                try:
                    driver = self.manager.load(driver_name)
                    address = driver.get(self.test_cep)
                    
                    # Store for comparison
                    addresses[driver_name] = address
                    
                    # Verify basic requirements
                    self.assertIsInstance(address, Address, f"Driver {driver_name} should return Address")
                    self.assertIsNotNone(address.postal_code, f"Driver {driver_name} should have postal_code")
                    self.assertIsNotNone(address.country, f"Driver {driver_name} should have country")
                    self.assertEqual(address.country.code, 'BR', f"Driver {driver_name} should return BR country")
                    
                    # Verify verification status
                    self.assertTrue(address.is_verified, f"Driver {driver_name} address should be verified")
                    self.assertEqual(address.verification_source, driver_name, f"Driver {driver_name} verification source mismatch")
                    
                    print(f"PASS {driver_name}: {address.get_display_name()}")
                    
                except Exception as e:
                    self.fail(f"Driver {driver_name} failed: {str(e)}")
        
        # Verify we tested at least the expected drivers
        expected_drivers = ['viacep', 'widenet', 'brasilapi']
        for expected in expected_drivers:
            self.assertIn(expected, addresses, f"Expected driver {expected} not tested")
    
    def test_all_drivers_handle_invalid_cep_consistently(self):
        """Test that all drivers handle invalid CEPs consistently."""
        drivers = self.manager.list_drivers()
        invalid_cep = "00000-000"
        
        for driver_name in drivers:
            with self.subTest(driver=driver_name):
                driver = self.manager.load(driver_name)
                
                with self.assertRaises(ValidationError, msg=f"Driver {driver_name} should raise ValidationError for invalid CEP"):
                    driver.get(invalid_cep)
    
    def test_all_drivers_handle_malformed_cep_consistently(self):
        """Test that all drivers handle malformed CEPs consistently."""
        drivers = self.manager.list_drivers()
        malformed_ceps = ["123", "abcd-efgh", ""]
        
        for driver_name in drivers:
            driver = self.manager.load(driver_name)
            
            for malformed_cep in malformed_ceps:
                with self.subTest(driver=driver_name, cep=malformed_cep):
                    with self.assertRaises(ValidationError, msg=f"Driver {driver_name} should raise ValidationError for malformed CEP {malformed_cep}"):
                        driver.get(malformed_cep)
    
    def test_manager_fallback_functionality(self):
        """Test manager's ability to try multiple drivers."""
        # Test with default driver
        try:
            address = self.manager.get(self.test_cep)
            self.assertIsInstance(address, Address)
            print(f"PASS Manager default: {address.get_display_name()}")
        except Exception as e:
            self.fail(f"Manager default driver failed: {str(e)}")
        
        # Test with specific driver
        for driver_name in ['viacep', 'widenet', 'brasilapi']:
            if self.manager.has_driver(driver_name):
                with self.subTest(driver=driver_name):
                    try:
                        address = self.manager.get(self.test_cep, driver=driver_name)
                        self.assertIsInstance(address, Address)
                        print(f"PASS Manager {driver_name}: {address.get_display_name()}")
                    except Exception as e:
                        self.fail(f"Manager with {driver_name} driver failed: {str(e)}")
    
    def test_driver_performance_comparison(self):
        """Test and compare driver performance (using cached responses)."""
        import time
        
        drivers = self.manager.list_drivers()
        performance = {}
        
        for driver_name in drivers:
            driver = self.manager.load(driver_name)
            
            # Measure time (will be very fast due to VCR caching)
            start_time = time.time()
            try:
                address = driver.get(self.test_cep)
                end_time = time.time()
                
                performance[driver_name] = {
                    'time': end_time - start_time,
                    'success': True,
                    'address': address.get_display_name()
                }
            except Exception as e:
                end_time = time.time()
                performance[driver_name] = {
                    'time': end_time - start_time,
                    'success': False,
                    'error': str(e)
                }
        
        # Print performance results
        print("\n=== Driver Performance Comparison ===")
        for driver_name, perf in performance.items():
            if perf['success']:
                print(f"{driver_name}: {perf['time']:.4f}s - {perf['address']}")
            else:
                print(f"{driver_name}: {perf['time']:.4f}s - ERROR: {perf['error']}")
        
        # Verify at least one driver succeeded
        successful_drivers = [name for name, perf in performance.items() if perf['success']]
        self.assertGreater(len(successful_drivers), 0, "At least one driver should succeed")
    
    def test_address_consistency_across_drivers(self):
        """Test that different drivers return consistent address information."""
        drivers = self.manager.list_drivers()
        addresses = {}
        
        # Collect addresses from all drivers
        for driver_name in drivers:
            try:
                driver = self.manager.load(driver_name)
                address = driver.get(self.test_cep)
                addresses[driver_name] = address
            except Exception:
                # Skip drivers that fail
                continue
        
        if len(addresses) < 2:
            self.skipTest("Need at least 2 working drivers for consistency test")
        
        # Compare key fields across drivers
        postal_codes = set(addr.postal_code for addr in addresses.values())
        states = set(addr.administrative_area_1 for addr in addresses.values())
        cities = set(addr.locality for addr in addresses.values())
        
        # All should have the same postal code (formatted)
        self.assertEqual(len(postal_codes), 1, f"Postal codes should be consistent: {postal_codes}")
        
        # All should have the same state
        self.assertEqual(len(states), 1, f"States should be consistent: {states}")
        
        # Cities might vary slightly due to different data sources, but should be similar
        print(f"Cities returned: {cities}")
        
        # All should be verified
        for driver_name, address in addresses.items():
            self.assertTrue(address.is_verified, f"Address from {driver_name} should be verified")


if __name__ == '__main__':
    unittest.main()
