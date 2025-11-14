"""
BrasilAPI postal code driver.

Driver for BrasilAPI (https://brasilapi.com.br/) following the Manager Pattern.
Based on: https://github.com/BrasilAPI/cep-promise/blob/master/src/services/brasilapi.js

Usage:
    # Direct usage
    driver = PostalCodeBrasilApiDriver()
    address = driver.get("88304-053")

    # Manager usage
    manager = PostalCodeManager()
    driver = manager.load("brasilapi")
    address = driver.get("88304-053")
"""

import logging
from typing import Any

import requests

from managers.formatter_manager import FormatterManager
from standards.address import Address, Country


# Local ValidationError class (temporary until validation_base is available)
class ValidationError(Exception):
    """Custom exception for validation errors."""

    def __init__(self, message: str, error_code: str = None):
        super().__init__(message)
        self.error_code = error_code


logger = logging.getLogger(__name__)


class PostalCodeBrasilApiDriver:
    """
    BrasilAPI postal code lookup driver.

    Implements the postal code driver interface:
    - get(postal_code: str) -> Address
    - configure(**kwargs) -> Self
    - get_config() -> Dict[str, Any]
    """

    def __init__(self):
        """Initialize BrasilAPI driver with default configuration."""
        self.name = "BrasilAPI"
        self._base_url = "https://brasilapi.com.br/api/cep/v1"
        self._default_config = {"timeout": 10, "retries": 3, "format": "json"}
        self._config = self._default_config.copy()

        # Initialize formatter for postal code formatting
        self._formatter_manager = FormatterManager()

        logger.debug("PostalCodeBrasilApiDriver initialized")

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
            formatted_cep = self._formatter_manager.format(
                postal_code, driver="brazilian_postalcode"
            )
            # Remove dash for API call (BrasilAPI expects XXXXXXXX format)
            clean_cep_for_api = formatted_cep.replace("-", "")
        except Exception as e:
            raise ValidationError(
                f"Invalid postal code format: {e!s}", error_code="POSTAL_CODE_INVALID_FORMAT"
            )

        # Make API request
        url = f"{self._base_url}/{clean_cep_for_api}"

        try:
            logger.debug("Requesting BrasilAPI: %s", url)
            response = requests.get(
                url,
                timeout=self._config["timeout"],
                headers={"Content-Type": "application/json;charset=utf-8"},
            )

            # BrasilAPI returns 404 for not found CEPs
            if response.status_code == 404:
                raise ValidationError(
                    f"Postal code not found: {postal_code}", error_code="POSTAL_CODE_NOT_FOUND"
                )

            response.raise_for_status()
            data = response.json()

            # Convert BrasilAPI response to Address object
            address = self._convert_to_address(data, formatted_cep)

            logger.debug("Successfully retrieved address for CEP: %s", postal_code)
            return address

        except requests.exceptions.RequestException as e:
            logger.error("BrasilAPI request failed: %s", e)
            raise ValidationError(
                f"Failed to lookup postal code: {e!s}", error_code="POSTAL_CODE_API_ERROR"
            )
        except ValueError as e:
            logger.error("BrasilAPI response parsing failed: %s", e)
            raise ValidationError(
                f"Invalid API response: {e!s}", error_code="POSTAL_CODE_INVALID_RESPONSE"
            )

    def configure(self, **kwargs) -> "PostalCodeBrasilApiDriver":
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
                logger.debug("BrasilAPI driver configured: %s = %s", key, value)
            else:
                logger.warning("Unknown configuration option: %s", key)

        return self

    def get_config(self) -> dict[str, Any]:
        """Get current driver configuration."""
        return self._config.copy()

    def reset_config(self) -> "PostalCodeBrasilApiDriver":
        """Reset configuration to defaults."""
        self._config = self._default_config.copy()
        logger.debug("BrasilAPI driver configuration reset to defaults")
        return self

    def _convert_to_address(self, data: dict[str, Any], original_postal_code: str) -> Address:
        """
        Convert BrasilAPI response to Address object.

        BrasilAPI response format:
        {
            "cep": "88304053",
            "state": "SC",
            "city": "Itajaí",
            "neighborhood": "Centro",
            "street": "Rua Alberto Werner"
        }
        """
        # Use formatted postal code (already formatted by FormatterManager)
        formatted_cep = original_postal_code

        # Create Brazil country object
        brazil = Country(code="BR", alpha3="BRA", numeric="076", name="Brazil", local_name="Brasil")

        # Create Address object
        address = Address(
            # Street information
            street_name=data.get("street") or None,
            # Geographic areas
            neighborhood=data.get("neighborhood") or None,
            locality=data.get("city") or None,  # City
            administrative_area_1=data.get("state") or None,  # State
            # Postal information
            postal_code=formatted_cep,
            # Country
            country=brazil,
            # Verification
            is_verified=True,
            verification_source="brasilapi",
        )

        # Mark as verified and set timestamp
        address.mark_as_verified("brasilapi")

        return address
