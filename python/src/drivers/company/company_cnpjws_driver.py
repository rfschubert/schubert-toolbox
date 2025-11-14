"""
CNPJ.ws Company Driver for Brazilian CNPJ lookups.

This driver provides company data lookup using the CNPJ.ws service,
which offers free access to Brazilian company information with strict rate limiting.
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


class CompanyCnpjwsDriver:
    """
    CNPJ.ws driver for Brazilian company (CNPJ) data lookup.
    
    This driver uses the CNPJ.ws public API to retrieve company information
    from official Brazilian government sources. It implements strict rate limiting
    to respect the API's usage policies (3 requests per minute).
    
    Features:
    - Free access to comprehensive company data
    - Built-in rate limiting (20 seconds between requests)
    - Automatic address resolution using postal code lookup
    - Comprehensive error handling
    - Retry logic for transient errors
    - Detailed company information including partners and activities
    
    API Documentation: https://docs.cnpj.ws/
    """
    
    def __init__(self):
        """Initialize CNPJ.ws company driver with default configuration."""
        self._driver_name = "CNPJ.ws"
        self._base_url = "https://publica.cnpj.ws/cnpj"
        self._default_config = {
            "timeout": 30, 
            "retries": 3, 
            "format": "json",
            "rate_limit_delay": 20.0,  # 20 seconds between requests (3 per minute)
            "max_retry_delay": 60.0    # Maximum delay for exponential backoff
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
    
    def configure(self, **kwargs) -> "CompanyCnpjwsDriver":
        """
        Configure the driver with custom settings.
        
        Args:
            timeout: Request timeout in seconds (default: 30)
            retries: Number of retry attempts (default: 3)
            rate_limit_delay: Delay between requests in seconds (default: 20.0)
            max_retry_delay: Maximum retry delay in seconds (default: 60.0)
            **kwargs: Additional configuration options
        """
        self._config.update(kwargs)
        logger.debug("CNPJ.ws company driver configured: %s", self._config)
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
            driver = CompanyCnpjwsDriver()
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
                
                logger.debug("Requesting CNPJ.ws API: %s (attempt %d)", api_url, attempt + 1)
                response = requests.get(
                    api_url,
                    headers={
                        "User-Agent": "Schubert-Toolbox/1.0",
                        "Accept": "application/json"
                    },
                    timeout=self._config["timeout"]
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
                    logger.error("CNPJ.ws API request failed after %d attempts: %s", self._config["retries"], e)
                    raise ValidationError(f"Failed to lookup CNPJ: {e!s}")
                else:
                    logger.warning("CNPJ.ws API request failed (attempt %d): %s", attempt + 1, e)
                    time.sleep(2)  # Brief delay before retry
            except (ValueError, KeyError) as e:
                logger.error("CNPJ.ws API response parsing failed: %s", e)
                raise ValidationError(f"Invalid API response: {e!s}")
        
        # Should not reach here
        raise ValidationError("Failed to lookup CNPJ after all retries")

    def _convert_to_company(self, data: Dict[str, Any], formatted_cnpj: str) -> Company:
        """
        Convert CNPJ.ws API response to Company object.

        CNPJ.ws API response format:
        {
            "cnpj_raiz": "11222333",
            "razao_social": "EMPRESA EXEMPLO LTDA",
            "capital_social": "10000.00",
            "responsavel_federativo": "",
            "atualizado_em": "2025-11-08T03:00:00.000Z",
            "porte": {
                "id": "01",
                "descricao": "Microempresa"
            },
            "natureza_juridica": {
                "id": "2062",
                "descricao": "Sociedade Empresária Limitada"
            },
            "estabelecimento": {
                "cnpj": "11222333000181",
                "cnpj_raiz": "11222333",
                "cnpj_ordem": "0001",
                "cnpj_digito_verificador": "81",
                "tipo": "Matriz",
                "nome_fantasia": "Empresa Exemplo",
                "situacao_cadastral": "Ativa",
                "data_situacao_cadastral": "2020-01-01",
                "data_inicio_atividade": "2020-01-01",
                "tipo_logradouro": "RUA",
                "logradouro": "DAS FLORES",
                "numero": "123",
                "complemento": "SALA 1",
                "bairro": "CENTRO",
                "cep": "88304053",
                "ddd1": "47",
                "telefone1": "33334444",
                "email": "contato@empresa.com.br",
                "atividade_principal": {
                    "id": "6201700",
                    "descricao": "Desenvolvimento de programas de computador sob encomenda"
                },
                "cidade": {
                    "id": 1234,
                    "nome": "Itajaí",
                    "ibge_id": 420540
                },
                "estado": {
                    "id": 24,
                    "nome": "Santa Catarina",
                    "sigla": "SC",
                    "ibge_id": 42
                }
            }
        }
        """
        # Check if company was found
        if not data or "estabelecimento" not in data:
            raise ValidationError(f"CNPJ not found: {formatted_cnpj}")

        # Create Brazil country object
        brazil = Country(code="BR", alpha3="BRA", numeric="076", name="Brazil", local_name="Brasil")

        # Extract establishment information
        estabelecimento = data.get("estabelecimento", {})

        # Parse company status
        status = estabelecimento.get("situacao_cadastral", "UNKNOWN")

        # Build address if available
        address = self._build_address(estabelecimento, brazil)

        # Build phone number
        phone = self._build_phone_number(estabelecimento)

        # Get email
        email = estabelecimento.get("email")

        # Get primary activity
        atividade_principal = estabelecimento.get("atividade_principal", {})
        primary_activity = atividade_principal.get("descricao") if atividade_principal else None

        # Parse share capital
        share_capital = data.get("capital_social")
        if share_capital:
            try:
                share_capital = float(share_capital)
            except (ValueError, TypeError):
                share_capital = None

        # Get company size
        porte = data.get("porte", {})
        company_size = porte.get("descricao") if porte else None

        # Get legal nature
        natureza_juridica = data.get("natureza_juridica", {})
        legal_nature = natureza_juridica.get("descricao") if natureza_juridica else None

        # Create Company object
        company = Company(
            # Basic identification
            cnpj=formatted_cnpj,
            legal_name=data.get("razao_social") or "Unknown Company",
            trade_name=estabelecimento.get("nome_fantasia"),

            # Status and registration
            status=status,
            registration_date=estabelecimento.get("data_inicio_atividade"),

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
            verification_source="cnpjws",
            last_updated=datetime.now()
        )

        return company

    def _build_phone_number(self, estabelecimento: Dict[str, Any]) -> Optional[str]:
        """Build formatted phone number from CNPJ.ws data."""
        ddd = estabelecimento.get("ddd1")
        telefone = estabelecimento.get("telefone1")

        if ddd and telefone:
            # Remove any non-digit characters
            ddd_clean = re.sub(r'[^\d]', '', str(ddd))
            telefone_clean = re.sub(r'[^\d]', '', str(telefone))

            if len(ddd_clean) == 2 and len(telefone_clean) >= 8:
                # Format as (XX) XXXX-XXXX or (XX) XXXXX-XXXX
                if len(telefone_clean) == 8:
                    return f"({ddd_clean}) {telefone_clean[:4]}-{telefone_clean[4:]}"
                elif len(telefone_clean) == 9:
                    return f"({ddd_clean}) {telefone_clean[:5]}-{telefone_clean[5:]}"
                else:
                    return f"({ddd_clean}) {telefone_clean}"

        return None

    def _build_address(self, estabelecimento: Dict[str, Any], country: Country) -> Optional[Address]:
        """
        Build Address object from CNPJ.ws data.

        If postal code is available but address is incomplete,
        attempts to resolve full address using postal code lookup.
        """
        # Extract address components
        tipo_logradouro = estabelecimento.get("tipo_logradouro", "")
        logradouro = estabelecimento.get("logradouro", "")
        numero = estabelecimento.get("numero", "")
        complemento = estabelecimento.get("complemento", "")
        bairro = estabelecimento.get("bairro", "")
        cep = estabelecimento.get("cep", "")

        # Get city and state from nested objects
        cidade_obj = estabelecimento.get("cidade", {})
        estado_obj = estabelecimento.get("estado", {})

        city = cidade_obj.get("nome", "") if cidade_obj else ""
        state = estado_obj.get("sigla", "") if estado_obj else ""

        # Format postal code if available
        formatted_postal_code = None
        if cep:
            try:
                formatter = self._formatter_manager.load("brazilian_postalcode")
                formatted_postal_code = formatter.format(cep)
            except Exception:
                formatted_postal_code = cep

        # Build street address
        street_parts = []
        if tipo_logradouro and logradouro:
            street_parts.append(f"{tipo_logradouro} {logradouro}")
        elif logradouro:
            street_parts.append(logradouro)

        if numero:
            street_parts.append(numero)
        if complemento:
            street_parts.append(complemento)

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
                if not bairro and resolved_address.neighborhood:
                    bairro = resolved_address.neighborhood
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
                    neighborhood=bairro or None,
                    locality=city or None,
                    administrative_area_1=state or None,
                    postal_code=formatted_postal_code,
                    country=country,
                    is_verified=True,
                    verification_source="cnpjws"
                )

                address.mark_as_verified("cnpjws")
                return address
            except Exception as e:
                logger.debug(f"Failed to create Address object: {e}")
                return None

        return None
