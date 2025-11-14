"""
Integration tests for PostalCodeViacepDriver with VCR cassettes.

These tests make real API calls to ViaCEP and record them using VCR.py
for future test runs without hitting the API.
"""

import unittest
import sys
import os
from pathlib import Path
import vcr

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from drivers.postalcode.postalcode_viacep_driver import PostalCodeViacepDriver
from standards.address import Address, Country
from standards.core.base import ValidationError


class TestPostalCodeViacepDriverIntegration(unittest.TestCase):
    """Integration tests for ViaCEP driver with real API calls."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.driver = PostalCodeViacepDriver()
        
        # Create cassettes directory
        self.cassettes_dir = Path(__file__).parent / "cassettes"
        self.cassettes_dir.mkdir(exist_ok=True)
    
    @vcr.use_cassette('tests/integration/cassettes/viacep_valid_cep.yaml')
    def test_get_valid_cep_88304053(self):
        """Test getting address for valid CEP 88304-053 (Itajaí, SC)."""
        # Test the specific CEP requested
        cep = "88.304-053"
        address = self.driver.get(cep)

        # Verify Address object
        self.assertIsInstance(address, Address)

        # Verify postal code
        self.assertEqual(address.postal_code, "88304-053")

        # Verify location (Itajaí, SC)
        self.assertEqual(address.locality, "Itajaí")
        self.assertEqual(address.administrative_area_1, "SC")
        
        # Verify country
        self.assertIsNotNone(address.country)
        self.assertEqual(address.country.code, "BR")
        self.assertEqual(address.country.name, "Brazil")
        
        # Verify verification status
        self.assertTrue(address.is_verified)
        self.assertEqual(address.verification_source, "viacep")
        
        # Verify address completeness
        self.assertTrue(address.is_complete())
        
        # Log address details
        print(f"Address: {address.get_display_name()}")
        print(f"Street: {address.street_name}")
        print(f"Neighborhood: {address.neighborhood}")
        print(f"City: {address.locality}")
        print(f"State: {address.administrative_area_1}")
        print(f"Postal Code: {address.postal_code}")
    
    @vcr.use_cassette('tests/integration/cassettes/viacep_different_formats.yaml')
    def test_get_different_cep_formats(self):
        """Test different CEP input formats."""
        test_cases = [
            "88304053",      # No formatting
            "88304-053",     # With dash
            "88.304-053",    # With dot and dash
            "88 304 053",    # With spaces
        ]
        
        for cep_format in test_cases:
            with self.subTest(cep_format=cep_format):
                address = self.driver.get(cep_format)
                
                # All should return the same address
                self.assertEqual(address.postal_code, "88304-053")
                self.assertEqual(address.locality, "Itajaí")
                self.assertEqual(address.administrative_area_1, "SC")
    
    @vcr.use_cassette('tests/integration/cassettes/viacep_invalid_cep.yaml')
    def test_get_invalid_cep(self):
        """Test getting address for invalid CEP."""
        with self.assertRaises(ValidationError) as context:
            self.driver.get("00000-000")
        
        self.assertEqual(context.exception.error_code, "POSTAL_CODE_NOT_FOUND")
    
    @vcr.use_cassette('tests/integration/cassettes/viacep_malformed_cep.yaml')
    def test_get_malformed_cep(self):
        """Test getting address for malformed CEP."""
        invalid_ceps = [
            "",           # Empty
            "123",        # Too short
            "123456789",  # Too long
            "abcd-efgh",  # Non-numeric
        ]
        
        for invalid_cep in invalid_ceps:
            with self.subTest(invalid_cep=invalid_cep):
                with self.assertRaises(ValidationError):
                    self.driver.get(invalid_cep)
    
    def test_driver_configuration(self):
        """Test driver configuration methods."""
        # Test initial config
        config = self.driver.get_config()
        self.assertIn('timeout', config)
        self.assertEqual(config['timeout'], 10)
        
        # Test configure method
        result = self.driver.configure(timeout=30, retries=5)
        self.assertEqual(result, self.driver)  # Method chaining
        
        # Verify configuration applied
        new_config = self.driver.get_config()
        self.assertEqual(new_config['timeout'], 30)
        self.assertEqual(new_config['retries'], 5)
        
        # Test reset config
        self.driver.reset_config()
        reset_config = self.driver.get_config()
        self.assertEqual(reset_config['timeout'], 10)  # Back to default
    
    def test_driver_name(self):
        """Test driver name property."""
        self.assertEqual(self.driver.name, "ViaCEP")
    
    @vcr.use_cassette('tests/integration/cassettes/viacep_address_components.yaml')
    def test_address_components(self):
        """Test that ViaCEP specific components are added to address."""
        address = self.driver.get("88304-053")
        
        # Check for ViaCEP specific components
        ibge_component = address.get_component_by_type('ibge_code')
        self.assertIsNotNone(ibge_component)
        
        area_code_component = address.get_component_by_type('area_code')
        self.assertIsNotNone(area_code_component)
        
        # Verify component values
        self.assertIsNotNone(ibge_component.value)
        self.assertIsNotNone(area_code_component.value)


if __name__ == '__main__':
    unittest.main()
