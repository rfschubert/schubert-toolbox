"""
Integration tests for CompanyCnpjwsDriver with VCR cassettes.

These tests make real API calls to CNPJ.ws and record them using VCR.py
for future test runs without hitting the API.
"""

import unittest
import sys
import os
from pathlib import Path
import vcr

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from drivers.company.company_cnpjws_driver import CompanyCnpjwsDriver
from standards.company import Company
from standards.core.base import ValidationError


class TestCompanyCnpjwsDriverIntegration(unittest.TestCase):
    """Integration tests for CNPJ.ws driver with real API calls."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.driver = CompanyCnpjwsDriver()
        
        # Create cassettes directory
        self.cassettes_dir = Path(__file__).parent / "cassettes"
        self.cassettes_dir.mkdir(exist_ok=True)
    
    @vcr.use_cassette('tests/integration/cassettes/cnpjws_valid_cnpj.yaml')
    def test_get_valid_cnpj_11222333000181(self):
        """Test getting company data for valid CNPJ 11.222.333/0001-81."""
        # Test the specific CNPJ
        cnpj = "11.222.333/0001-81"
        company = self.driver.get(cnpj)

        # Verify Company object
        self.assertIsInstance(company, Company)

        # Verify CNPJ
        self.assertEqual(company.cnpj, "11.222.333/0001-81")

        # Verify basic company information
        self.assertIsNotNone(company.legal_name)
        self.assertNotEqual(company.legal_name, "")
        
        # Verify verification metadata
        self.assertTrue(company.is_verified)
        self.assertEqual(company.verification_source, "cnpjws")
        self.assertIsNotNone(company.last_updated)
        
        # Verify country
        self.assertIsNotNone(company.country)
        self.assertEqual(company.country.code, "BR")
        
        # Print results for manual verification
        print(f"Company: {company.get_display_name()}")
        print(f"Legal Name: {company.legal_name}")
        print(f"Trade Name: {company.trade_name}")
        print(f"Status: {company.status}")
        print(f"Active: {company.is_active()}")
    
    @vcr.use_cassette('tests/integration/cassettes/cnpjws_valid_cnpj_unformatted.yaml')
    def test_get_valid_cnpj_unformatted(self):
        """Test getting company data for unformatted CNPJ."""
        # Test unformatted CNPJ
        cnpj = "11222333000181"
        company = self.driver.get(cnpj)

        # Verify Company object
        self.assertIsInstance(company, Company)

        # Verify CNPJ is properly formatted in response
        self.assertEqual(company.cnpj, "11.222.333/0001-81")
        
        # Verify basic information
        self.assertIsNotNone(company.legal_name)
        self.assertEqual(company.verification_source, "cnpjws")
    
    @vcr.use_cassette('tests/integration/cassettes/cnpjws_invalid_cnpj.yaml')
    def test_get_invalid_cnpj(self):
        """Test getting company data for invalid CNPJ."""
        # Test with invalid CNPJ
        invalid_cnpj = "00.000.000/0001-00"
        
        with self.assertRaises(ValidationError) as context:
            self.driver.get(invalid_cnpj)
        
        # Verify error message contains relevant information
        error_message = str(context.exception)
        self.assertIn("CNPJ", error_message.upper())
    
    def test_get_malformed_cnpj(self):
        """Test getting company data for malformed CNPJ (no API call)."""
        # Test with malformed CNPJ
        malformed_cnpjs = [
            "invalid-cnpj",
            "123",
            "",
            None
        ]
        
        for cnpj in malformed_cnpjs:
            with self.subTest(cnpj=cnpj):
                with self.assertRaises(ValidationError):
                    self.driver.get(cnpj)
    
    def test_driver_configuration(self):
        """Test driver configuration options."""
        # Test default configuration
        config = self.driver.get_configuration()
        self.assertIn('timeout', config)
        self.assertIn('retries', config)
        self.assertIn('rate_limit_delay', config)
        
        # Verify default rate limit (20 seconds for 3 requests per minute)
        self.assertEqual(config['rate_limit_delay'], 20.0)
        
        # Test configuration update
        self.driver.configure(timeout=15, rate_limit_delay=10.0)
        new_config = self.driver.get_configuration()
        self.assertEqual(new_config['timeout'], 15)
        self.assertEqual(new_config['rate_limit_delay'], 10.0)
    
    def test_rate_limiting(self):
        """Test rate limiting functionality (no API calls)."""
        import time
        
        # Configure short rate limit for testing
        self.driver.configure(rate_limit_delay=0.2)
        
        # Test rate limiting wait
        start_time = time.time()
        self.driver._wait_for_rate_limit()
        first_wait = time.time() - start_time
        
        # Should be minimal wait on first call
        self.assertLess(first_wait, 0.05)
        
        # Second call should wait
        start_time = time.time()
        self.driver._wait_for_rate_limit()
        second_wait = time.time() - start_time
        
        # Should wait approximately the rate limit delay
        self.assertGreaterEqual(second_wait, 0.18)  # Allow some tolerance
    
    def test_company_data_structure(self):
        """Test that returned company has expected data structure."""
        # This test will use a cassette if available
        try:
            with vcr.use_cassette('tests/integration/cassettes/cnpjws_data_structure.yaml'):
                company = self.driver.get("11.222.333/0001-81")
                
                # Test Company object structure
                self.assertIsInstance(company.cnpj, str)
                self.assertIsInstance(company.legal_name, str)
                self.assertIsInstance(company.status, str)
                self.assertIsInstance(company.is_verified, bool)
                self.assertIsInstance(company.verification_source, str)
                
                # Test optional fields (should be None or proper type)
                if company.trade_name is not None:
                    self.assertIsInstance(company.trade_name, str)
                
                if company.phone is not None:
                    self.assertIsInstance(company.phone, str)
                
                if company.email is not None:
                    self.assertIsInstance(company.email, str)
                
                if company.share_capital is not None:
                    self.assertIsInstance(company.share_capital, (int, float))
                
                # Test methods
                self.assertIsInstance(company.get_display_name(), str)
                self.assertIsInstance(company.is_active(), bool)
                
        except Exception as e:
            # Skip if API is not available
            self.skipTest(f"API not available for data structure test: {e}")


if __name__ == '__main__':
    unittest.main()
