"""
OpenCNPJ.org Company Driver for Brazilian CNPJ lookups.

This driver provides company data lookup using the OpenCNPJ.org service,
which offers free access to Brazilian company information.
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Any, Dict, Optional

import requests
import urllib3

from managers.formatter_manager import FormatterManager
from managers.postalcode_manager import PostalCodeManager
from standards.address.address import Address
from standards.core.base import Country, ValidationError
from standards.company import Company

logger = logging.getLogger(__name__)


class CompanyOpencnpjDriver:
    """
    OpenCNPJ.org driver for Brazilian company (CNPJ) data lookup.
    
    This driver uses the OpenCNPJ.org service to retrieve company information
    from official Brazilian government sources. It implements rate limiting
    to respect the API's usage policies.
    
    Features:
    - Free access to official company data
    - Built-in rate limiting (1 request per second)
    - Automatic address resolution using postal code lookup
    - Comprehensive error handling
    - Retry logic for transient errors
    
    API Documentation: https://opencnpj.org/
    """
    
    def __init__(self):
        """Initialize OpenCNPJ company driver with default configuration."""
        self._driver_name = "OpenCNPJ"
        self._base_url = "https://api.opencnpj.org"
        self._default_config = {
            "timeout": 30, 
            "retries": 3, 
            "format": "json",
            "rate_limit_delay": 1.0,  # 1 second between requests
            "max_retry_delay": 5.0    # Maximum delay for exponential backoff
        }
        self._config = self._default_config.copy()
        
        # Rate limiting
        self._last_request_time = 0
        
        # Initialize formatter for CNPJ validation and formatting
        self._formatter_manager = FormatterManager()
        
        # Initialize postal code manager for address resolution
        self._postalcode_manager = PostalCodeManager()

        # Disable SSL warnings for OpenCNPJ API (certificate issues)
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    @property
    def name(self) -> str:
        """Get the display name of the driver."""
        return self._driver_name
    
    def configure(self, **kwargs) -> "CompanyOpencnpjDriver":
        """
        Configure the driver with custom settings.
        
        Args:
            timeout: Request timeout in seconds (default: 30)
            retries: Number of retry attempts (default: 3)
            rate_limit_delay: Delay between requests in seconds (default: 1.0)
            max_retry_delay: Maximum retry delay in seconds (default: 5.0)
            **kwargs: Additional configuration options
        """
        self._config.update(kwargs)
        logger.debug("OpenCNPJ company driver configured: %s", self._config)
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
            driver = CompanyOpencnpjDriver()
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
                
                logger.debug("Requesting OpenCNPJ API: %s (attempt %d)", api_url, attempt + 1)
                response = requests.get(
                    api_url,
                    headers={
                        "User-Agent": "Schubert-Toolbox/1.0",
                        "Accept": "application/json"
                    },
                    timeout=self._config["timeout"],
                    verify=False  # Disable SSL verification for OpenCNPJ API
                )
                
                # Handle CNPJ not found (404) - don't retry
                if response.status_code == 404:
                    logger.debug(f"CNPJ not found: {cnpj}")
                    raise ValidationError(f"CNPJ not found: {formatted_cnpj}")
                
                # Handle rate limiting (429) - retry with backoff
                if response.status_code == 429:
                    retry_delay = min(
                        self._config["rate_limit_delay"] * (2 ** attempt),
                        self._config["max_retry_delay"]
                    )
                    logger.warning(f"Rate limited, waiting {retry_delay}s before retry {attempt + 1}")
                    time.sleep(retry_delay)
                    continue
                
                response.raise_for_status()

                # Parse JSON response
                company_data = response.json()
                
                # Convert to Company object
                company = self._convert_to_company(company_data, formatted_cnpj)

                logger.debug("Successfully retrieved company data for CNPJ: %s", cnpj)
                return company

            except requests.exceptions.RequestException as e:
                if attempt == self._config["retries"] - 1:  # Last attempt
                    logger.error("OpenCNPJ API request failed after %d attempts: %s", self._config["retries"], e)
                    raise ValidationError(f"Failed to lookup CNPJ: {e!s}")
                else:
                    logger.warning("OpenCNPJ API request failed (attempt %d): %s", attempt + 1, e)
                    time.sleep(1)  # Brief delay before retry
            except (ValueError, KeyError) as e:
                logger.error("OpenCNPJ API response parsing failed: %s", e)
                raise ValidationError(f"Invalid API response: {e!s}")
        
        # Should not reach here
        raise ValidationError("Failed to lookup CNPJ after all retries")

    def _convert_to_company(self, data: Dict[str, Any], formatted_cnpj: str) -> Company:
        """
        Convert OpenCNPJ API response to Company object.

        OpenCNPJ API response format (based on Receita Federal structure):
        {
            "cnpj": "11222333000181",
            "razao_social": "EMPRESA EXEMPLO LTDA",
            "nome_fantasia": "Empresa Exemplo",
            "situacao_cadastral": "ATIVA",
            "data_inicio_atividade": "2020-01-01",
            "natureza_juridica": "206-2 - Sociedade Empresária Limitada",
            "porte": "MICROEMPRESA",
            "logradouro": "RUA DAS FLORES",
            "numero": "123",
            "complemento": "SALA 1",
            "bairro": "CENTRO",
            "municipio": "ITAJAÍ",
            "uf": "SC",
            "cep": "88304053",
            "telefone_1": "(47) 3333-4444",
            "email": "contato@empresa.com.br",
            "atividade_principal": {
                "codigo": "6201-5/00",
                "descricao": "Desenvolvimento de programas de computador sob encomenda"
            },
            "capital_social": "10000.00"
        }
        """
        # Check if company was found
        if not data or "cnpj" not in data:
            raise ValidationError(f"CNPJ not found: {formatted_cnpj}")

        # Create Brazil country object
        brazil = Country(code="BR", alpha3="BRA", numeric="076", name="Brazil", local_name="Brasil")

        # Parse company status
        status = data.get("situacao_cadastral", "UNKNOWN")

        # Build address if available
        address = self._build_address(data, brazil)

        # Get phone number
        phone = data.get("telefone_1") or data.get("telefone_2")

        # Get email
        email = data.get("email")

        # Get primary activity
        atividade_principal = data.get("atividade_principal", {})
        primary_activity = None
        if isinstance(atividade_principal, dict):
            primary_activity = atividade_principal.get("descricao")
        elif isinstance(atividade_principal, str):
            primary_activity = atividade_principal

        # Parse share capital
        share_capital = data.get("capital_social")
        if share_capital:
            try:
                # Remove currency symbols and convert to float
                share_capital_str = str(share_capital).replace("R$", "").replace(".", "").replace(",", ".")
                share_capital = float(share_capital_str)
            except (ValueError, TypeError):
                share_capital = None

        # Get company size
        company_size = data.get("porte")

        # Create Company object
        company = Company(
            # Basic identification
            cnpj=formatted_cnpj,
            legal_name=data.get("razao_social") or "Unknown Company",
            trade_name=data.get("nome_fantasia"),

            # Status and registration
            status=status,
            registration_date=data.get("data_inicio_atividade"),

            # Address
            address=address,

            # Contact information
            phone=phone,
            email=email,

            # Business information
            primary_activity=primary_activity,
            company_size=company_size,
            share_capital=share_capital,
            legal_nature=data.get("natureza_juridica"),

            # Metadata
            country=brazil,
            is_verified=True,
            verification_source="opencnpj",
            last_updated=datetime.now()
        )

        return company

    def _build_address(self, data: Dict[str, Any], country: Country) -> Optional[Address]:
        """
        Build Address object from OpenCNPJ data.

        If postal code is available but address is incomplete,
        attempts to resolve full address using postal code lookup.
        """
        # Extract address components
        street = data.get("logradouro", "")
        number = data.get("numero", "")
        complement = data.get("complemento", "")
        district = data.get("bairro", "")
        city = data.get("municipio", "")
        state = data.get("uf", "")
        postal_code = data.get("cep", "")

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
        if complement:
            street_parts.append(complement)

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
                    verification_source="opencnpj"
                )

                address.mark_as_verified("opencnpj")
                return address
            except Exception as e:
                logger.debug(f"Failed to create Address object: {e}")
                return None

        return None
