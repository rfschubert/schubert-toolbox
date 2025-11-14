"""
WideNet postal code driver.

Driver for WideNet API (https://cdn.apicep.com/) following the Manager Pattern.
Based on: https://github.com/BrasilAPI/cep-promise/blob/master/src/services/widenet.js

Usage:
    # Direct usage
    driver = PostalCodeWidenetDriver()
    address = driver.get("88304-053")
    
    # Manager usage
    manager = PostalCodeManager()
    driver = manager.load("widenet")
    address = driver.get("88304-053")
"""

import logging
import re
from typing import Any, Dict, Optional
import requests

from standards.address import Address, Country
from validation_base import ValidationError
from managers.formatter_manager import FormatterManager

logger = logging.getLogger(__name__)


class PostalCodeWidenetDriver:
    """
    WideNet postal code lookup driver.
    
    Implements the postal code driver interface:
    - get(postal_code: str) -> Address
    - configure(**kwargs) -> Self
    - get_config() -> Dict[str, Any]
    """
    
    def __init__(self):
        """Initialize WideNet driver with default configuration."""
        self.name = "WideNet"
        self._base_url = "https://cdn.apicep.com/file/apicep"
        self._default_config = {
            'timeout': 10,
            'retries': 3,
            'format': 'json'
        }
        self._config = self._default_config.copy()

        # Initialize formatter for postal code formatting
        self._formatter_manager = FormatterManager()

        logger.debug("PostalCodeWidenetDriver initialized")
    
    def get(self, postal_code: str) -> Address:
        """
        Get address information for Brazilian postal code (CEP).
        
        Args:
            postal_code: Brazilian postal code (CEP) in format XXXXX-XXX or XXXXXXXX
            
        Returns:
            Address object with postal code information
            
        Raises:
            ValidationError: If postal code is invalid or not found
        """
        # Format and validate postal code using FormatterManager
        try:
            formatted_cep = self._formatter_manager.format(postal_code, driver="brazilian_postalcode")
        except Exception as e:
            raise ValidationError(f"Invalid postal code format: {str(e)}", error_code="POSTAL_CODE_INVALID_FORMAT")
        
        # Make API request
        url = f"{self._base_url}/{formatted_cep}.json"
        
        try:
            logger.debug("Requesting WideNet API: %s", url)
            response = requests.get(
                url,
                timeout=self._config['timeout'],
                headers={'Accept': 'application/json'}
            )

            # Handle HTTP errors but check response content first
            if response.status_code == 400:
                try:
                    data = response.json()
                    if data.get('ok') is False:
                        raise ValidationError(
                            f"Postal code not found: {postal_code}",
                            error_code="POSTAL_CODE_NOT_FOUND"
                        )
                except ValueError:
                    # If JSON parsing fails, treat as API error
                    pass

            response.raise_for_status()

            data = response.json()

            # Check for API error response
            if data.get('ok') is False or data.get('status') != 200:
                raise ValidationError(
                    f"Postal code not found: {postal_code}",
                    error_code="POSTAL_CODE_NOT_FOUND"
                )

            # Convert WideNet response to Address object
            address = self._convert_to_address(data, formatted_cep)

            logger.debug("Successfully retrieved address for CEP: %s", postal_code)
            return address

        except requests.exceptions.RequestException as e:
            logger.error("WideNet API request failed: %s", e)
            raise ValidationError(
                f"Failed to lookup postal code: {str(e)}",
                error_code="POSTAL_CODE_API_ERROR"
            )
        except ValueError as e:
            logger.error("WideNet API response parsing failed: %s", e)
            raise ValidationError(
                f"Invalid API response: {str(e)}",
                error_code="POSTAL_CODE_INVALID_RESPONSE"
            )
    
    def configure(self, **kwargs) -> 'PostalCodeWidenetDriver':
        """
        Configure driver options.
        
        Args:
            timeout: Request timeout in seconds
            retries: Number of retry attempts
            format: Response format (json only supported)
            
        Returns:
            Self for method chaining
        """
        for key, value in kwargs.items():
            if key in self._default_config:
                self._config[key] = value
                logger.debug("WideNet driver configured: %s = %s", key, value)
            else:
                logger.warning("Unknown configuration option: %s", key)
        
        return self
    
    def get_config(self) -> Dict[str, Any]:
        """Get current driver configuration."""
        return self._config.copy()
    
    def reset_config(self) -> 'PostalCodeWidenetDriver':
        """Reset configuration to defaults."""
        self._config = self._default_config.copy()
        logger.debug("WideNet driver configuration reset to defaults")
        return self

    def _convert_to_address(self, data: Dict[str, Any], original_postal_code: str) -> Address:
        """
        Convert WideNet API response to Address object.

        WideNet response format:
        {
            "ok": true,
            "code": "88304-053",
            "state": "SC",
            "city": "Itajaí",
            "district": "Centro",
            "address": "Rua Alberto Werner",
            "status": 200
        }
        """
        # Use formatted postal code (already formatted by FormatterManager)
        formatted_cep = original_postal_code

        # Create Brazil country object
        brazil = Country(
            code="BR",
            alpha3="BRA",
            numeric="076",
            name="Brazil",
            local_name="Brasil"
        )

        # Create Address object
        address = Address(
            # Street information
            street_name=data.get('address') or None,

            # Geographic areas
            neighborhood=data.get('district') or None,
            locality=data.get('city') or None,  # City
            administrative_area_1=data.get('state') or None,  # State

            # Postal information
            postal_code=formatted_cep,

            # Country
            country=brazil,

            # Verification
            is_verified=True,
            verification_source="widenet"
        )

        # Mark as verified and set timestamp
        address.mark_as_verified('widenet')

        return address
