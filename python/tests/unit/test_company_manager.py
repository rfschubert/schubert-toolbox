"""
Unit tests for CompanyManager.

These tests verify the CompanyManager functionality including
first-to-respond patterns and driver management.
"""

import unittest
import sys
import os
import asyncio
from unittest.mock import Mock, patch, AsyncMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from managers.company_manager import CompanyManager
from standards.company import Company
from standards.core.base import ValidationError


class TestCompanyManager(unittest.TestCase):
    """Unit tests for CompanyManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = CompanyManager()
        
        # Create mock company object
        self.mock_company = Company(
            cnpj="11.222.333/0001-81",
            legal_name="Test Company Ltd",
            trade_name="Test Company",
            status="ATIVA",
            verification_source="test"
        )
    
    def test_manager_initialization(self):
        """Test manager initialization."""
        self.assertIsInstance(self.manager, CompanyManager)
        self.assertTrue(hasattr(self.manager, '_drivers'))
        self.assertTrue(hasattr(self.manager, '_thread_pool'))
    
    def test_list_drivers(self):
        """Test listing available drivers."""
        drivers = self.manager.list_drivers()
        self.assertIsInstance(drivers, list)
        self.assertGreater(len(drivers), 0)
        
        # Should have both brasilapi and cnpja
        expected_drivers = ['brasilapi', 'cnpja']
        for driver in expected_drivers:
            self.assertIn(driver, drivers)
    
    def test_get_driver_info(self):
        """Test getting driver information."""
        drivers = self.manager.list_drivers()
        
        for driver_name in drivers:
            with self.subTest(driver=driver_name):
                info = self.manager.get_driver_info(driver_name)
                
                self.assertIsInstance(info, dict)
                self.assertIn('name', info)
                self.assertIn('description', info)
                self.assertIn('version', info)
                self.assertIn('country', info)
                
                self.assertEqual(info['name'], driver_name)
                self.assertEqual(info['country'], 'BR')
    
    def test_load_driver(self):
        """Test loading drivers."""
        drivers = self.manager.list_drivers()
        
        for driver_name in drivers:
            with self.subTest(driver=driver_name):
                driver = self.manager.load(driver_name)
                
                # Check driver has required methods
                self.assertTrue(hasattr(driver, 'get'))
                self.assertTrue(hasattr(driver, 'configure'))
                self.assertTrue(hasattr(driver, 'name'))
    
    def test_load_driver_with_config(self):
        """Test loading driver with configuration."""
        driver = self.manager.load("brasilapi", timeout=15)
        config = driver.get_configuration()
        self.assertEqual(config['timeout'], 15)
    
    def test_load_nonexistent_driver(self):
        """Test loading non-existent driver."""
        with self.assertRaises(ValidationError):
            self.manager.load("nonexistent")
    
    @patch('drivers.company.company_brasilapi_driver.CompanyBrasilApiDriver.get')
    def test_get_basic(self, mock_get):
        """Test basic get functionality."""
        mock_get.return_value = self.mock_company
        
        company = self.manager.get("11.222.333/0001-81")
        
        self.assertEqual(company, self.mock_company)
        mock_get.assert_called_once_with("11.222.333/0001-81")
    
    @patch('drivers.company.company_brasilapi_driver.CompanyBrasilApiDriver.get')
    def test_get_with_specific_driver(self, mock_get):
        """Test get with specific driver."""
        mock_get.return_value = self.mock_company
        
        company = self.manager.get("11.222.333/0001-81", driver_name="brasilapi")
        
        self.assertEqual(company, self.mock_company)
        mock_get.assert_called_once_with("11.222.333/0001-81")
    
    def test_get_no_drivers_available(self):
        """Test get when no drivers are available."""
        # Create manager with no drivers
        empty_manager = CompanyManager()
        empty_manager._drivers = {}
        
        with self.assertRaises(ValidationError) as context:
            empty_manager.get("11.222.333/0001-81")
        
        self.assertIn("No company drivers available", str(context.exception))


class TestCompanyManagerFirstToRespond(unittest.TestCase):
    """Tests for first-to-respond functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = CompanyManager()
        
        # Create mock company
        self.mock_company = Company(
            cnpj="11.222.333/0001-81",
            legal_name="Test Company Ltd",
            status="ATIVA",
            verification_source="test"
        )
    
    @patch('managers.company_manager.CompanyManager.load')
    def test_first_to_respond_success(self, mock_load):
        """Test successful first-to-respond."""
        # Mock driver that returns company
        mock_driver = Mock()
        mock_driver.get.return_value = self.mock_company
        mock_driver.name = "test"
        mock_load.return_value = mock_driver
        
        # Test first-to-respond using sync wrapper
        company = self.manager.get_first_response_sync(
            "11.222.333/0001-81",
            drivers=["test"],
            timeout=5.0
        )
        
        # Verify results
        self.assertEqual(company, self.mock_company)
        self.assertEqual(company.verification_source, "test")
    
    @patch('managers.company_manager.CompanyManager.load')
    def test_first_to_respond_all_fail(self, mock_load):
        """Test first-to-respond when all drivers fail."""
        # Mock driver that raises exception
        mock_driver = Mock()
        mock_driver.get.side_effect = ValidationError("Driver failed")
        mock_driver.name = "fail"
        mock_load.return_value = mock_driver
        
        # Test that ValidationError is raised when all fail
        with self.assertRaises(Exception):
            self.manager.get_first_response_sync(
                "11.222.333/0001-81",
                drivers=["fail"],
                timeout=5.0
            )
    
    @patch('managers.company_manager.CompanyManager.list_drivers')
    @patch('managers.company_manager.CompanyManager.load')
    def test_first_to_respond_default_drivers(self, mock_load, mock_list_drivers):
        """Test first-to-respond with default drivers."""
        # Mock available drivers
        mock_list_drivers.return_value = ["test"]
        
        # Mock driver
        mock_driver = Mock()
        mock_driver.get.return_value = self.mock_company
        mock_driver.name = "test"
        mock_load.return_value = mock_driver
        
        # Test with no drivers specified (should use all available)
        company = self.manager.get_first_response_sync("11.222.333/0001-81")
        
        # Verify list_drivers was called to get default list
        mock_list_drivers.assert_called_once()
        
        # Verify result
        self.assertEqual(company, self.mock_company)
    
    def test_no_drivers_available(self):
        """Test first-to-respond with no drivers available."""
        # Create manager with no drivers
        empty_manager = CompanyManager()
        empty_manager._drivers = {}
        
        with self.assertRaises(ValidationError) as context:
            empty_manager.get_first_response_sync("11.222.333/0001-81")
        
        self.assertIn("No company drivers available", str(context.exception))


if __name__ == '__main__':
    unittest.main()
