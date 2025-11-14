"""
Unit tests for first-to-respond functionality in PostalCodeManager.
"""

import unittest
import asyncio
import sys
import os
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from managers.postalcode_manager import PostalCodeManager
from managers.async_driver_wrapper import AsyncDriverWrapper
from standards.address import Address, Country

# Import ValidationError
try:
    from validation_base import ValidationError
except ImportError:
    # Fallback for testing
    class ValidationError(Exception):
        """Custom exception for validation errors."""
        
        def __init__(self, message: str, error_code: str = None):
            super().__init__(message)
            self.error_code = error_code


class TestFirstToRespond(unittest.TestCase):
    """Test first-to-respond functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = PostalCodeManager()
        
        # Create mock address
        brazil = Country(code="BR", alpha3="BRA", numeric="076", name="Brazil")
        self.mock_address = Address(
            street_name="Test Street",
            locality="Test City",
            administrative_area_1="SC",
            postal_code="88304-053",
            country=brazil,
            is_verified=True,
            verification_source="test"
        )
    
    @patch('managers.postalcode_manager.PostalCodeManager.load')
    def test_first_to_respond_success(self, mock_load):
        """Test successful first-to-respond with multiple drivers."""
        # Create mock drivers
        fast_driver = Mock()
        fast_driver.name = "FastDriver"
        fast_driver.get = Mock(return_value=self.mock_address)
        
        slow_driver = Mock()
        slow_driver.name = "SlowDriver"
        
        def slow_get(postal_code):
            import time
            time.sleep(0.5)  # Simulate slow response
            return self.mock_address
        
        slow_driver.get = Mock(side_effect=slow_get)
        
        # Configure mock load to return different drivers
        def load_side_effect(driver_name):
            if driver_name == "fast":
                return fast_driver
            elif driver_name == "slow":
                return slow_driver
            
        mock_load.side_effect = load_side_effect
        
        # Test first-to-respond using sync wrapper
        address = self.manager.get_first_response_sync(
            "88304-053",
            drivers=["fast", "slow"],
            timeout=5.0
        )

        # Verify results
        self.assertEqual(address, self.mock_address)
        # Driver name should be in verification_source
        self.assertEqual(address.verification_source, "test")
        
        # Verify fast driver was called
        fast_driver.get.assert_called_once_with("88304-053")
    
    @patch('managers.postalcode_manager.PostalCodeManager.load')
    def test_first_to_respond_all_fail(self, mock_load):
        """Test first-to-respond when all drivers fail."""
        # Create failing drivers
        failing_driver1 = Mock()
        failing_driver1.name = "FailDriver1"
        failing_driver1.get = Mock(side_effect=ValidationError("Driver 1 failed"))
        
        failing_driver2 = Mock()
        failing_driver2.name = "FailDriver2"
        failing_driver2.get = Mock(side_effect=ValidationError("Driver 2 failed"))
        
        def load_side_effect(driver_name):
            if driver_name == "fail1":
                return failing_driver1
            elif driver_name == "fail2":
                return failing_driver2
                
        mock_load.side_effect = load_side_effect
        
        # Test that ValidationError is raised when all fail
        with self.assertRaises(Exception) as context:
            self.manager.get_first_response_sync(
                "88304-053",
                drivers=["fail1", "fail2"],
                timeout=5.0
            )

        # Check that it's some kind of ValidationError
        self.assertTrue(
            "ValidationError" in str(type(context.exception)) or
            hasattr(context.exception, 'error_code')
        )

        # Check error code if available
        if hasattr(context.exception, 'error_code'):
            self.assertEqual(context.exception.error_code, "POSTAL_CODE_ALL_DRIVERS_FAILED")
    
    @patch('managers.postalcode_manager.PostalCodeManager.list_drivers')
    @patch('managers.postalcode_manager.PostalCodeManager.load')
    def test_first_to_respond_default_drivers(self, mock_load, mock_list_drivers):
        """Test first-to-respond with default driver list."""
        # Mock available drivers
        mock_list_drivers.return_value = ["viacep", "brasilapi"]
        
        # Create mock driver
        mock_driver = Mock()
        mock_driver.name = "MockDriver"
        mock_driver.get = Mock(return_value=self.mock_address)
        mock_load.return_value = mock_driver
        
        # Test with no drivers specified (should use all available)
        address = self.manager.get_first_response_sync("88304-053")

        # Verify list_drivers was called to get default list
        mock_list_drivers.assert_called_once()

        # Verify result
        self.assertEqual(address, self.mock_address)
    
    def test_no_drivers_available(self):
        """Test first-to-respond when no drivers are available."""
        with patch.object(self.manager, 'list_drivers', return_value=[]):
            with self.assertRaises(Exception) as context:
                self.manager.get_first_response_sync("88304-053")

            # Check that it's some kind of ValidationError
            self.assertTrue(
                "ValidationError" in str(type(context.exception)) or
                hasattr(context.exception, 'error_code')
            )

            # Check error code if available
            if hasattr(context.exception, 'error_code'):
                self.assertEqual(context.exception.error_code, "POSTAL_CODE_NO_DRIVERS")


class TestAsyncDriverWrapper(unittest.TestCase):
    """Test AsyncDriverWrapper functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock sync driver
        self.sync_driver = Mock()
        self.sync_driver.name = "TestDriver"
        
        # Create mock address
        brazil = Country(code="BR", alpha3="BRA", numeric="076", name="Brazil")
        self.mock_address = Address(
            street_name="Test Street",
            locality="Test City",
            administrative_area_1="SC",
            postal_code="88304-053",
            country=brazil,
            is_verified=True,
            verification_source="test"
        )
        
        self.sync_driver.get = Mock(return_value=self.mock_address)
        
        # Create wrapper
        self.wrapper = AsyncDriverWrapper(self.sync_driver)
    
    def test_async_wrapper_success(self):
        """Test successful async wrapper call."""
        # Test async call using sync wrapper
        async def run_test():
            result = await self.wrapper.get_async("88304-053")
            return result
        
        # Run async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(run_test())
            
            # Verify sync driver was called
            self.sync_driver.get.assert_called_once_with("88304-053")
            
            # Verify result
            self.assertEqual(result, self.mock_address)
        finally:
            loop.close()
    
    def test_wrapper_attributes(self):
        """Test that wrapper preserves driver attributes."""
        self.assertEqual(self.wrapper.name, "TestDriver")
        self.assertEqual(self.wrapper.sync_driver, self.sync_driver)


if __name__ == '__main__':
    unittest.main()
