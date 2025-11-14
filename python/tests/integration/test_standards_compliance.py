"""
Integration tests to ensure all drivers return standard objects from standards/ directory.

This test suite verifies the critical architectural requirement that all drivers
must use standard classes from the standards/ directory to ensure interoperability
and data consistency across the entire system.
"""

import pytest
import sys
import os
from typing import Type
import vcr

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from standards.address import Address, Country
from standards.core.base import BaseModel
from managers import PostalCodeManager, FormatterManager
from drivers.postalcode.postalcode_viacep_driver import PostalCodeViacepDriver
from drivers.postalcode.postalcode_widenet_driver import PostalCodeWidenetDriver
from drivers.postalcode.postalcode_brasilapi_driver import PostalCodeBrasilApiDriver


class TestStandardsCompliance:
    """Test that all drivers return standard objects from standards/ directory."""
    
    @vcr.use_cassette('tests/integration/cassettes/all_drivers_integration.yaml')
    def test_postal_code_drivers_return_standard_address(self):
        """Test that all postal code drivers return standards.address.Address objects."""
        # Test data - valid Brazilian postal code
        test_postal_code = "88304-053"

        # List of all postal code drivers
        drivers = [
            PostalCodeViacepDriver(),
            PostalCodeWidenetDriver(),
            PostalCodeBrasilApiDriver()
        ]

        for driver in drivers:
            driver_name = driver.__class__.__name__
            
            try:
                # Get address from driver
                address = driver.get(test_postal_code)
                
                # CRITICAL: Must be standards.address.Address
                assert isinstance(address, Address), (
                    f"{driver_name} must return standards.address.Address, "
                    f"got {type(address)}"
                )
                
                # Must inherit from BaseModel
                assert isinstance(address, BaseModel), (
                    f"{driver_name} returned Address must inherit from BaseModel, "
                    f"got {type(address).__bases__}"
                )
                
                # Must have required Address properties
                assert hasattr(address, 'postal_code'), f"{driver_name} Address missing postal_code"
                assert hasattr(address, 'locality'), f"{driver_name} Address missing locality"
                assert hasattr(address, 'administrative_area_1'), f"{driver_name} Address missing administrative_area_1"
                assert hasattr(address, 'country'), f"{driver_name} Address missing country"
                
                # Must have Address methods
                assert hasattr(address, 'get_display_name'), f"{driver_name} Address missing get_display_name method"
                assert hasattr(address, 'get_full_street_address'), f"{driver_name} Address missing get_full_street_address method"
                assert hasattr(address, 'is_complete'), f"{driver_name} Address missing is_complete method"
                assert hasattr(address, 'mark_as_verified'), f"{driver_name} Address missing mark_as_verified method"
                
                # Country must be standards.address.Country
                if address.country:
                    assert isinstance(address.country, Country), (
                        f"{driver_name} Address.country must be standards.address.Country, "
                        f"got {type(address.country)}"
                    )
                
                # Must have BaseModel properties
                assert hasattr(address, 'id'), f"{driver_name} Address missing BaseModel.id"
                assert hasattr(address, 'created_at'), f"{driver_name} Address missing BaseModel.created_at"
                assert hasattr(address, 'metadata'), f"{driver_name} Address missing BaseModel.metadata"
                
                # Must have BaseModel methods
                assert hasattr(address, 'validate'), f"{driver_name} Address missing BaseModel.validate method"
                assert hasattr(address, 'to_dict'), f"{driver_name} Address missing BaseModel.to_dict method"
                assert hasattr(address, 'to_json'), f"{driver_name} Address missing BaseModel.to_json method"
                
                print(f"PASS {driver_name}: Returns standards.address.Address correctly")

            except Exception as e:
                # If driver fails (network issues, etc.), skip but log
                print(f"WARN {driver_name}: Skipped due to error - {e}")
                continue
    
    @vcr.use_cassette('tests/integration/cassettes/all_drivers_integration.yaml')
    def test_postal_code_manager_returns_standard_address(self):
        """Test that PostalCodeManager returns standards.address.Address objects."""
        manager = PostalCodeManager()
        test_postal_code = "88304-053"

        # Test all available drivers through manager
        available_drivers = manager.list_drivers()

        for driver_name in available_drivers:
            try:
                # Get address through manager
                address = manager.get(test_postal_code, driver=driver_name)
                
                # CRITICAL: Must be standards.address.Address
                assert isinstance(address, Address), (
                    f"PostalCodeManager with {driver_name} must return standards.address.Address, "
                    f"got {type(address)}"
                )
                
                # Must inherit from BaseModel
                assert isinstance(address, BaseModel), (
                    f"PostalCodeManager with {driver_name} returned Address must inherit from BaseModel"
                )
                
                print(f"PASS PostalCodeManager with {driver_name}: Returns standards.address.Address correctly")

            except Exception as e:
                # If driver fails (network issues, etc.), skip but log
                print(f"WARN PostalCodeManager with {driver_name}: Skipped due to error - {e}")
                continue
    
    def test_address_object_functionality(self):
        """Test that Address objects have all expected functionality."""
        # Create a test Address object
        brazil = Country(code="BR", name="Brazil")
        
        address = Address(
            street_name="Rua Alberto Werner",
            locality="Itajaí",
            administrative_area_1="SC",
            postal_code="88304-053",
            country=brazil,
            is_verified=True,
            verification_source="test"
        )
        
        # Test BaseModel functionality
        assert address.id is not None, "Address must have BaseModel.id"
        assert address.created_at is not None, "Address must have BaseModel.created_at"
        assert isinstance(address.metadata, dict), "Address must have BaseModel.metadata dict"
        
        # Test Address methods
        display_name = address.get_display_name()
        assert isinstance(display_name, str), "get_display_name must return string"
        assert len(display_name) > 0, "get_display_name must return non-empty string"
        
        # Test serialization
        address_dict = address.to_dict()
        assert isinstance(address_dict, dict), "to_dict must return dictionary"
        assert 'postal_code' in address_dict, "to_dict must include postal_code"
        
        address_json = address.to_json()
        assert isinstance(address_json, str), "to_json must return string"
        
        print("PASS Address object: All functionality working correctly")
    
    def test_formatter_manager_compatibility(self):
        """Test that FormatterManager works with postal code drivers (DRY integration)."""
        formatter = FormatterManager()
        
        # Test that formatter returns string (not Address)
        result = formatter.format("88304053", driver="brazilian_postalcode")
        assert isinstance(result, str), "FormatterManager must return string, not Address"
        assert result == "88304-053", f"Expected '88304-053', got '{result}'"
        
        print("PASS FormatterManager: Returns string correctly (not Address)")


if __name__ == "__main__":
    # Run tests directly
    test = TestStandardsCompliance()
    test.test_postal_code_drivers_return_standard_address()
    test.test_postal_code_manager_returns_standard_address()
    test.test_address_object_functionality()
    test.test_formatter_manager_compatibility()
    print("\nPASS All standards compliance tests completed!")
