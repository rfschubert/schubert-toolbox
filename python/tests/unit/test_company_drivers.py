"""
Unit tests for Company drivers.

These tests verify the basic functionality of company drivers without
making actual API calls.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from managers.company_manager import CompanyManager
from standards.company import Company
from standards.core.base import ValidationError


class TestCompanyDrivers(unittest.TestCase):
    """Unit tests for company drivers."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = CompanyManager()
    
    def test_manager_has_drivers(self):
        """Test that manager has registered drivers."""
        drivers = self.manager.list_drivers()
        self.assertIsInstance(drivers, list)
        self.assertGreater(len(drivers), 0, "Manager should have at least one driver")
        
        # Should have brasilapi, cnpja, opencnpj, and cnpjws drivers
        expected_drivers = ['brasilapi', 'cnpja', 'opencnpj', 'cnpjws']
        for driver in expected_drivers:
            self.assertIn(driver, drivers, f"Driver {driver} should be available")
    
    def test_all_drivers_implement_interface(self):
        """Test that all drivers implement required interface."""
        drivers = self.manager.list_drivers()
        
        for driver_name in drivers:
            with self.subTest(driver=driver_name):
                driver = self.manager.load(driver_name)
                
                # Check required methods
                self.assertTrue(hasattr(driver, 'get'), f"Driver {driver_name} should have get method")
                self.assertTrue(hasattr(driver, 'configure'), f"Driver {driver_name} should have configure method")
                self.assertTrue(hasattr(driver, 'get_configuration'), f"Driver {driver_name} should have get_configuration method")
                
                # Check name property
                self.assertTrue(hasattr(driver, 'name'), f"Driver {driver_name} should have name property")
                self.assertIsInstance(driver.name, str, f"Driver {driver_name} name should be string")
    
    def test_driver_configuration(self):
        """Test driver configuration functionality."""
        drivers = self.manager.list_drivers()
        
        for driver_name in drivers:
            with self.subTest(driver=driver_name):
                driver = self.manager.load(driver_name)
                
                # Get default configuration
                default_config = driver.get_configuration()
                self.assertIsInstance(default_config, dict)
                
                # Configure driver
                driver.configure(timeout=15)
                
                # Verify configuration changed
                new_config = driver.get_configuration()
                self.assertEqual(new_config['timeout'], 15)
    
    def test_driver_names_follow_convention(self):
        """Test that driver names follow naming convention."""
        drivers = self.manager.list_drivers()
        
        for driver_name in drivers:
            with self.subTest(driver=driver_name):
                # Driver names should be lowercase
                self.assertEqual(driver_name, driver_name.lower())
                
                # Driver names should not contain spaces
                self.assertNotIn(' ', driver_name)
    
    def test_manager_driver_configuration(self):
        """Test manager-level driver configuration."""
        # Test loading driver with configuration
        driver = self.manager.load("brasilapi", timeout=20)
        config = driver.get_configuration()
        self.assertEqual(config['timeout'], 20)
    
    def test_get_driver_info(self):
        """Test getting driver information."""
        drivers = self.manager.list_drivers()
        
        for driver_name in drivers:
            with self.subTest(driver=driver_name):
                info = self.manager.get_driver_info(driver_name)
                
                # Check required fields
                self.assertIn('name', info)
                self.assertIn('description', info)
                self.assertIn('version', info)
                self.assertIn('country', info)
                
                # Check values
                self.assertEqual(info['name'], driver_name)
                self.assertIsInstance(info['description'], str)
                self.assertIsInstance(info['version'], str)
                self.assertEqual(info['country'], 'BR')  # All company drivers should be BR
    
    @patch('requests.get')
    def test_brasilapi_driver_returns_company(self, mock_get):
        """Test that BrasilAPI driver returns Company object."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "cnpj": "11222333000181",
            "razao_social": "EMPRESA TESTE LTDA",
            "nome_fantasia": "Empresa Teste",
            "descricao_situacao_cadastral": "ATIVA",
            "municipio": "São Paulo",
            "uf": "SP",
            "cep": "01234567"
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Test driver
        driver = self.manager.load("brasilapi")
        company = driver.get("11.222.333/0001-81")
        
        # Verify Company object
        self.assertIsInstance(company, Company)
        self.assertEqual(company.cnpj, "11.222.333/0001-81")
        self.assertEqual(company.legal_name, "EMPRESA TESTE LTDA")
        self.assertEqual(company.verification_source, "brasilapi")
    
    @patch('requests.get')
    def test_cnpja_driver_returns_company(self, mock_get):
        """Test that CNPJA driver returns Company object."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "cnpj": "11222333000181",
            "company": {
                "name": "EMPRESA TESTE LTDA",
                "alias": "Empresa Teste",
                "status": "ATIVA"
            },
            "address": {
                "city": "São Paulo",
                "state": "SP",
                "zip": "01234567"
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Test driver
        driver = self.manager.load("cnpja")
        company = driver.get("11.222.333/0001-81")
        
        # Verify Company object
        self.assertIsInstance(company, Company)
        self.assertEqual(company.cnpj, "11.222.333/0001-81")
        self.assertEqual(company.legal_name, "EMPRESA TESTE LTDA")
        self.assertEqual(company.verification_source, "cnpja")

    @patch('requests.get')
    def test_opencnpj_driver_returns_company(self, mock_get):
        """Test that OpenCNPJ driver returns Company object."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "cnpj": "11222333000181",
            "razao_social": "EMPRESA TESTE LTDA",
            "nome_fantasia": "Empresa Teste",
            "situacao_cadastral": "ATIVA",
            "municipio": "São Paulo",
            "uf": "SP",
            "cep": "01234567"
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Test driver
        driver = self.manager.load("opencnpj")
        company = driver.get("11.222.333/0001-81")

        # Verify Company object
        self.assertIsInstance(company, Company)
        self.assertEqual(company.cnpj, "11.222.333/0001-81")
        self.assertEqual(company.legal_name, "EMPRESA TESTE LTDA")
        self.assertEqual(company.verification_source, "opencnpj")

    @patch('requests.get')
    def test_cnpjws_driver_returns_company(self, mock_get):
        """Test that CNPJ.ws driver returns Company object."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "cnpj_raiz": "11222333",
            "razao_social": "EMPRESA TESTE LTDA",
            "capital_social": "10000.00",
            "porte": {
                "id": "01",
                "descricao": "Microempresa"
            },
            "estabelecimento": {
                "cnpj": "11222333000181",
                "nome_fantasia": "Empresa Teste",
                "situacao_cadastral": "Ativa",
                "cidade": {
                    "nome": "São Paulo"
                },
                "estado": {
                    "sigla": "SP"
                },
                "cep": "01234567"
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Test driver
        driver = self.manager.load("cnpjws")
        company = driver.get("11.222.333/0001-81")

        # Verify Company object
        self.assertIsInstance(company, Company)
        self.assertEqual(company.cnpj, "11.222.333/0001-81")
        self.assertEqual(company.legal_name, "EMPRESA TESTE LTDA")
        self.assertEqual(company.verification_source, "cnpjws")
    
    def test_driver_error_handling(self):
        """Test driver error handling for invalid input."""
        drivers = self.manager.list_drivers()
        
        for driver_name in drivers:
            with self.subTest(driver=driver_name):
                driver = self.manager.load(driver_name)
                
                # Test with invalid CNPJ
                with self.assertRaises(ValidationError):
                    driver.get("invalid-cnpj")
                
                # Test with None
                with self.assertRaises(ValidationError):
                    driver.get(None)
                
                # Test with empty string
                with self.assertRaises(ValidationError):
                    driver.get("")


if __name__ == '__main__':
    unittest.main()
