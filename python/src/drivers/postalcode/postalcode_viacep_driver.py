"""
ViaCEP postal code driver.

Driver for ViaCEP API (https://viacep.com.br/) following the Manager Pattern.
Based on: https://github.com/BrasilAPI/cep-promise/blob/master/src/services/viacep.js

Usage:
    # Direct usage
    driver = PostalCodeViacepDriver()
    address = driver.get("88304-053")

    # Manager usage
    manager = PostalCodeManager()
    driver = manager.load("viacep")
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


class PostalCodeViacepDriver:
    """
    ViaCEP postal code lookup driver.

    Implements the postal code driver interface:
    - get(postal_code: str) -> Address
    - configure(**kwargs) -> Self
    - get_config() -> Dict[str, Any]
    """

    def __init__(self):
        """Initialize ViaCEP driver with default configuration."""
        self.name = "ViaCEP"
        self._base_url = "https://viacep.com.br/ws"
        self._default_config = {"timeout": 10, "retries": 3, "format": "json"}
        self._config = self._default_config.copy()

        # Initialize formatter for postal code formatting
        self._formatter_manager = FormatterManager()

        logger.debug("PostalCodeViacepDriver initialized")

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
            clean_cep = self._formatter_manager.format(postal_code, driver="brazilian_postalcode")
            # Remove dash for API call (ViaCEP expects XXXXXXXX format)
            clean_cep_for_api = clean_cep.replace("-", "")
        except Exception as e:
            raise ValidationError(
                f"Invalid postal code format: {e!s}", error_code="POSTAL_CODE_INVALID_FORMAT"
            )

        # Make API request
        url = f"{self._base_url}/{clean_cep_for_api}/json/"

        try:
            logger.debug("Requesting ViaCEP API: %s", url)
            response = requests.get(
                url, timeout=self._config["timeout"], headers={"User-Agent": "Schubert-Toolbox/1.0"}
            )
            response.raise_for_status()

            data = response.json()

            # Check for API error response
            if data.get("erro"):
                raise ValidationError(
                    f"Postal code not found: {postal_code}", error_code="POSTAL_CODE_NOT_FOUND"
                )

            # Convert ViaCEP response to Address object
            address = self._convert_to_address(data, clean_cep)

            logger.debug("Successfully retrieved address for CEP: %s", postal_code)
            return address

        except requests.exceptions.RequestException as e:
            logger.error("ViaCEP API request failed: %s", e)
            raise ValidationError(
                f"Failed to lookup postal code: {e!s}", error_code="POSTAL_CODE_API_ERROR"
            )
        except ValueError as e:
            logger.error("ViaCEP API response parsing failed: %s", e)
            raise ValidationError(
                f"Invalid API response: {e!s}", error_code="POSTAL_CODE_INVALID_RESPONSE"
            )

    def configure(self, **kwargs) -> "PostalCodeViacepDriver":
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
                logger.debug("ViaCEP driver configured: %s = %s", key, value)
            else:
                logger.warning("Unknown configuration option: %s", key)

        return self

    def get_config(self) -> dict[str, Any]:
        """Get current driver configuration."""
        return self._config.copy()

    def reset_config(self) -> "PostalCodeViacepDriver":
        """Reset configuration to defaults."""
        self._config = self._default_config.copy()
        logger.debug("ViaCEP driver configuration reset to defaults")
        return self

    def _convert_to_address(self, data: dict[str, Any], original_postal_code: str) -> Address:
        """
        Convert ViaCEP API response to Address object.

        ViaCEP response format:
        {
            "cep": "88304-053",
            "logradouro": "Rua Deputado Antônio Edu Vieira",
            "complemento": "",
            "bairro": "Pantanal",
            "localidade": "Florianópolis",
            "uf": "SC",
            "ibge": "4205407",
            "gia": "",
            "ddd": "48",
            "siafi": "8105"
        }
        """
        # Use formatted postal code (already formatted by FormatterManager)
        formatted_cep = original_postal_code

        # Create Brazil country object
        brazil = Country(code="BR", alpha3="BRA", numeric="076", name="Brazil", local_name="Brasil")

        # Create Address object
        address = Address(
            # Street information
            street_name=data.get("logradouro") or None,
            unit=data.get("complemento") or None,
            # Geographic areas
            neighborhood=data.get("bairro") or None,
            locality=data.get("localidade") or None,  # City
            administrative_area_1=data.get("uf") or None,  # State
            # Postal information
            postal_code=formatted_cep,
            # Country
            country=brazil,
            # Verification
            is_verified=True,
            verification_source="viacep",
        )

        # Add ViaCEP specific components
        if data.get("ibge"):
            address.add_component("ibge_code", data["ibge"])

        if data.get("ddd"):
            address.add_component("area_code", data["ddd"])

        if data.get("siafi"):
            address.add_component("siafi_code", data["siafi"])

        # Mark as verified and set timestamp
        address.mark_as_verified("viacep")

        return address
