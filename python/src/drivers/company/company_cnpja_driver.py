"""
CNPJA.com Company Driver for Brazilian CNPJ lookups.

This driver provides company data lookup using the CNPJA.com service,
which offers free access to Brazilian company information with rate limiting.
"""

import asyncio
import logging
import re
import time
from datetime import datetime
from typing import Any, Dict, Optional

import requests

from managers.formatter_manager import FormatterManager
from managers.postalcode_manager import PostalCodeManager
from standards.address.address import Address
from standards.core.base import Country, ValidationError
from standards.company import Company

logger = logging.getLogger(__name__)


class CompanyCnpjaDriver:
    """
    CNPJA.com driver for Brazilian company (CNPJ) data lookup.
    
    This driver uses the CNPJA.com service to retrieve company information
    from official Brazilian government sources. It implements rate limiting
    to respect the API's usage policies.
    
    Features:
    - Free access to official company data
    - Built-in rate limiting (1 request per 2 seconds)
    - Automatic address resolution using postal code lookup
    - Comprehensive error handling
    - Retry logic for rate limit errors
    
    API Documentation: https://cnpja.com/api
    """
    
    def __init__(self):
        """Initialize CNPJA company driver with default configuration."""
        self._driver_name = "CNPJA"
        self._base_url = "https://open.cnpja.com/office"
        self._default_config = {
            "timeout": 30, 
            "retries": 3, 
            "format": "json",
            "rate_limit_delay": 2.0,  # 2 seconds between requests
            "max_retry_delay": 10.0   # Maximum delay for exponential backoff
        }
        self._config = self._default_config.copy()
        
        # Rate limiting
        self._last_request_time = 0
        
        # Initialize formatter for CNPJ validation and formatting
        self._formatter_manager = FormatterManager()
        
        # Initialize postal code manager for address resolution
        self._postalcode_manager = PostalCodeManager()
    
    @property
    def name(self) -> str:
        """Get the display name of the driver."""
        return self._driver_name
    
    def configure(self, **kwargs) -> "CompanyCnpjaDriver":
        """
        Configure the driver with custom settings.
        
        Args:
            timeout: Request timeout in seconds (default: 30)
            retries: Number of retry attempts (default: 3)
            rate_limit_delay: Delay between requests in seconds (default: 2.0)
            max_retry_delay: Maximum retry delay in seconds (default: 10.0)
            **kwargs: Additional configuration options
        """
        self._config.update(kwargs)
        logger.debug("CNPJA company driver configured: %s", self._config)
        return self
    
    def get_configuration(self) -> Dict[str, Any]:
        """Get current driver configuration."""
        return self._config.copy()
    
    def _wait_for_rate_limit(self):
        """Wait for rate limit if necessary."""
        current_time = time.time()
        time_since_last_request = current_time - self._last_request_time
        
        if time_since_last_request < self._config["rate_limit_delay"]:
            sleep_time = self._config["rate_limit_delay"] - time_since_last_request
            logger.debug(f"Rate limiting: waiting {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self._last_request_time = time.time()
    
    def get(self, cnpj: str) -> Company:
        """
        Retrieve company data for the given CNPJ.
        
        Args:
            cnpj: CNPJ number (can be formatted or unformatted)
            
        Returns:
            Company: Company data object with comprehensive information
            
        Raises:
            ValidationError: If CNPJ is invalid or lookup fails
            
        Example:
            driver = CompanyCnpjaDriver()
            company = driver.get("11.222.333/0001-81")
            print(f"Company: {company.get_display_name()}")
            print(f"Status: {company.status}")
        """
        # Clean and validate CNPJ using integrated formatter
        try:
            formatter = self._formatter_manager.load("brazilian_cnpj")
            clean_cnpj = formatter.clean(cnpj)
            formatted_cnpj = formatter.format(cnpj)
        except Exception as e:
            logger.error("CNPJ validation failed: %s", e)
            raise ValidationError(f"Invalid CNPJ format: {cnpj}")
        
        # Make API request with rate limiting and retries
        for attempt in range(self._config["retries"]):
            try:
                # Apply rate limiting
                self._wait_for_rate_limit()
                
                # Make API request
                api_url = f"{self._base_url}/{clean_cnpj}"
                
                logger.debug("Requesting CNPJA API: %s (attempt %d)", api_url, attempt + 1)
                response = requests.get(
                    api_url,
                    headers={
                        "User-Agent": "Schubert-Toolbox/1.0",
                        "Accept": "application/json"
                    },
                    timeout=self._config["timeout"]
                )
                
                # Handle rate limiting
                if response.status_code == 429:
                    retry_delay = min(
                        self._config["rate_limit_delay"] * (2 ** attempt),
                        self._config["max_retry_delay"]
                    )
                    logger.warning(f"Rate limited, waiting {retry_delay}s before retry {attempt + 1}")
                    time.sleep(retry_delay)
                    continue

                # Handle CNPJ not found (404) - don't retry
                if response.status_code == 404:
                    logger.debug(f"CNPJ not found: {cnpj}")
                    raise ValidationError(f"CNPJ not found: {formatted_cnpj}")

                # Handle API blocked/forbidden (403) - don't retry
                if response.status_code == 403:
                    logger.warning(f"CNPJA API blocked (403): {cnpj}")
                    raise ValidationError(f"CNPJA API temporarily blocked: {formatted_cnpj}")

                response.raise_for_status()

                # Parse JSON response
                company_data = response.json()
                
                # Convert to Company object
                company = self._convert_to_company(company_data, formatted_cnpj)

                logger.debug("Successfully retrieved company data for CNPJ: %s", cnpj)
                return company

            except requests.exceptions.RequestException as e:
                if attempt == self._config["retries"] - 1:  # Last attempt
                    logger.error("CNPJA API request failed after %d attempts: %s", self._config["retries"], e)
                    raise ValidationError(f"Failed to lookup CNPJ: {e!s}")
                else:
                    logger.warning("CNPJA API request failed (attempt %d): %s", attempt + 1, e)
                    time.sleep(1)  # Brief delay before retry
            except (ValueError, KeyError) as e:
                logger.error("CNPJA API response parsing failed: %s", e)
                raise ValidationError(f"Invalid API response: {e!s}")
        
        # Should not reach here
        raise ValidationError("Failed to lookup CNPJ after all retries")

    def _convert_to_company(self, data: Dict[str, Any], formatted_cnpj: str) -> Company:
        """
        Convert CNPJA API response to Company object.

        CNPJA API response format:
        {
            "cnpj": "11222333000181",
            "company": {
                "name": "EMPRESA EXEMPLO LTDA",
                "alias": "Empresa Exemplo",
                "founded": "2020-01-01",
                "status": "ATIVA",
                "nature": {
                    "code": "2062",
                    "description": "Sociedade Empresária Limitada"
                },
                "size": {
                    "acronym": "ME",
                    "description": "Microempresa"
                }
            },
            "address": {
                "street": "Rua das Flores",
                "number": "123",
                "details": "Sala 1",
                "district": "Centro",
                "city": "Itajaí",
                "state": "SC",
                "zip": "88304053"
            },
            "phones": [
                {
                    "area": "47",
                    "number": "33334444"
                }
            ],
            "emails": [
                "contato@empresa.com.br"
            ],
            "activities": [
                {
                    "code": "6201500",
                    "description": "Desenvolvimento de programas de computador sob encomenda",
                    "primary": true
                }
            ],
            "capital": 10000.00
        }
        """
        # Check if company was found - support both old and new API formats
        if not data or ("cnpj" not in data and "taxId" not in data):
            raise ValidationError(f"CNPJ not found: {formatted_cnpj}")

        # Create Brazil country object
        brazil = Country(code="BR", alpha3="BRA", numeric="076", name="Brazil", local_name="Brasil")

        # Extract company information - handle both old and new API formats
        company_info = data.get("company", {})
        address_info = data.get("address", {})

        # Handle different API response formats
        if "cnpj" in data:
            # Old format
            company_name = company_info.get("name", "Unknown Company")
            trade_name = company_info.get("alias")
            status = company_info.get("status", "UNKNOWN")
            registration_date = company_info.get("founded")
        else:
            # New format (taxId)
            company_name = company_info.get("name", "Unknown Company")
            trade_name = data.get("alias")

            # Status mapping for new format
            status_info = data.get("status", {})
            if isinstance(status_info, dict):
                status = status_info.get("text", "UNKNOWN")
            else:
                status = str(status_info) if status_info else "UNKNOWN"

            registration_date = data.get("founded")

        # Build address if available
        address = self._build_address(address_info, brazil)

        # Build phone number
        phone = self._build_phone_number(data.get("phones", []))

        # Get primary email - handle both formats
        emails = data.get("emails", [])
        if emails and isinstance(emails[0], dict):
            # New format: array of objects
            email = emails[0].get("address")
        elif emails:
            # Old format: array of strings
            email = emails[0]
        else:
            email = None

        # Get primary activity - handle both formats
        if "cnpj" in data:
            # Old format
            activities = data.get("activities", [])
            primary_activity = None
            for activity in activities:
                if activity.get("primary", False):
                    primary_activity = activity.get("description")
                    break
            if not primary_activity and activities:
                primary_activity = activities[0].get("description")
        else:
            # New format
            main_activity = data.get("mainActivity", {})
            primary_activity = main_activity.get("text") if main_activity else None

        # Parse share capital - handle both formats
        if "cnpj" in data:
            # Old format
            share_capital = data.get("capital")
        else:
            # New format uses "equity"
            share_capital = company_info.get("equity")

        if share_capital:
            try:
                share_capital = float(share_capital)
            except (ValueError, TypeError):
                share_capital = None

        # Get company size and legal nature - handle both formats
        if "cnpj" in data:
            # Old format
            size_info = company_info.get("size", {})
            company_size = size_info.get("description") if size_info else None

            nature_info = company_info.get("nature", {})
            legal_nature = nature_info.get("description") if nature_info else None
        else:
            # New format
            size_info = company_info.get("size", {})
            company_size = size_info.get("text") if size_info else None

            nature_info = company_info.get("nature", {})
            legal_nature = nature_info.get("text") if nature_info else None

        # Create Company object
        company = Company(
            # Basic identification
            cnpj=formatted_cnpj,
            legal_name=company_name,
            trade_name=trade_name,

            # Status and registration
            status=status,
            registration_date=registration_date,

            # Address
            address=address,

            # Contact information
            phone=phone,
            email=email,

            # Business information
            primary_activity=primary_activity,
            company_size=company_size,
            share_capital=share_capital,
            legal_nature=legal_nature,

            # Metadata
            country=brazil,
            is_verified=True,
            verification_source="cnpja",
            last_updated=datetime.now()
        )

        return company

    def _build_phone_number(self, phones: list) -> Optional[str]:
        """Build formatted phone number from CNPJA data - handles both old and new formats."""
        if not phones:
            return None

        # Get first phone
        phone_info = phones[0]

        # Handle both old and new formats
        if "type" in phone_info:
            # New format: {"type": "LANDLINE", "area": "19", "number": "33135680"}
            area = phone_info.get("area")
            number = phone_info.get("number")
        else:
            # Old format: {"area": "47", "number": "33334444"}
            area = phone_info.get("area")
            number = phone_info.get("number")

        if area and number:
            # Remove any non-digit characters
            area_clean = re.sub(r'[^\d]', '', str(area))
            number_clean = re.sub(r'[^\d]', '', str(number))

            if len(area_clean) == 2 and len(number_clean) >= 8:
                # Format as (XX) XXXX-XXXX or (XX) XXXXX-XXXX
                if len(number_clean) == 8:
                    return f"({area_clean}) {number_clean[:4]}-{number_clean[4:]}"
                elif len(number_clean) == 9:
                    return f"({area_clean}) {number_clean[:5]}-{number_clean[5:]}"
                else:
                    return f"({area_clean}) {number_clean}"

        return None

    def _build_address(self, address_info: Dict[str, Any], country: Country) -> Optional[Address]:
        """
        Build Address object from CNPJA data.

        If postal code is available but address is incomplete,
        attempts to resolve full address using postal code lookup.
        """
        # Extract address components
        street = address_info.get("street", "")
        number = address_info.get("number", "")
        details = address_info.get("details", "")
        district = address_info.get("district", "")
        city = address_info.get("city", "")
        state = address_info.get("state", "")
        postal_code = address_info.get("zip", "")

        # Format postal code if available
        formatted_postal_code = None
        if postal_code:
            try:
                formatter = self._formatter_manager.load("brazilian_postalcode")
                formatted_postal_code = formatter.format(postal_code)
            except Exception:
                formatted_postal_code = postal_code

        # Build street address
        street_parts = []
        if street:
            street_parts.append(street)
        if number:
            street_parts.append(number)
        if details:
            street_parts.append(details)

        full_street = ", ".join(street_parts) if street_parts else None

        # If we have postal code but missing address details, try to resolve
        if formatted_postal_code and (not full_street or not city or not state):
            try:
                logger.debug(f"Attempting to resolve address for postal code: {formatted_postal_code}")
                resolved_address = asyncio.run(
                    self._postalcode_manager.get_first_response(formatted_postal_code)
                )

                # Use resolved data to fill missing information
                if not full_street and resolved_address.street_name:
                    full_street = resolved_address.street_name
                if not district and resolved_address.neighborhood:
                    district = resolved_address.neighborhood
                if not city and resolved_address.locality:
                    city = resolved_address.locality
                if not state and resolved_address.administrative_area_1:
                    state = resolved_address.administrative_area_1

                logger.debug(f"Successfully resolved address for postal code: {formatted_postal_code}")

            except Exception as e:
                logger.debug(f"Failed to resolve address for postal code {formatted_postal_code}: {e}")

        # Create Address object if we have sufficient information
        if full_street or city or formatted_postal_code:
            try:
                address = Address(
                    street_name=full_street,
                    neighborhood=district or None,
                    locality=city or None,
                    administrative_area_1=state or None,
                    postal_code=formatted_postal_code,
                    country=country,
                    is_verified=True,
                    verification_source="cnpja"
                )

                address.mark_as_verified("cnpja")
                return address
            except Exception as e:
                logger.debug(f"Failed to create Address object: {e}")
                return None

        return None
