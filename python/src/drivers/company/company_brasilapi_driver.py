"""
BrasilAPI Company Driver for Brazilian CNPJ lookups.

This driver provides company data lookup using the BrasilAPI service,
which offers free access to Brazilian company information from official sources.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, Optional

import requests

# Driver without contract inheritance for simplicity
from managers.formatter_manager import FormatterManager
from managers.postalcode_manager import PostalCodeManager
from standards.address.address import Address
from standards.core.base import Country, ValidationError
from standards.company import Company

logger = logging.getLogger(__name__)


class CompanyBrasilApiDriver:
    """
    BrasilAPI driver for Brazilian company (CNPJ) data lookup.
    
    This driver uses the BrasilAPI service to retrieve company information
    from official Brazilian government sources. It provides comprehensive
    company data including registration details, address, and business activities.
    
    Features:
    - Free access to official company data
    - Automatic address resolution using postal code lookup
    - Comprehensive error handling
    - Rate limiting friendly
    
    API Documentation: https://brasilapi.com.br/docs#tag/CNPJ
    """
    
    def __init__(self):
        """Initialize BrasilAPI company driver with default configuration."""
        self.name = "BrasilAPI"
        self._base_url = "https://brasilapi.com.br/api/cnpj/v1"
        self._default_config = {"timeout": 30, "retries": 3, "format": "json"}
        self._config = self._default_config.copy()
        
        # Initialize formatter for CNPJ validation and formatting
        self._formatter_manager = FormatterManager()
        
        # Initialize postal code manager for address resolution
        self._postalcode_manager = PostalCodeManager()
    
    def configure(self, **kwargs) -> None:
        """
        Configure the driver with custom settings.
        
        Args:
            timeout: Request timeout in seconds (default: 30)
            retries: Number of retry attempts (default: 3)
            **kwargs: Additional configuration options
        """
        self._config.update(kwargs)
        logger.debug("BrasilAPI company driver configured: %s", self._config)
    
    def get_configuration(self) -> Dict[str, Any]:
        """Get current driver configuration."""
        return self._config.copy()
    
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
            driver = CompanyBrasilApiDriver()
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
        
        # Make API request
        api_url = f"{self._base_url}/{clean_cnpj}"
        
        try:
            logger.debug("Requesting BrasilAPI: %s", api_url)
            response = requests.get(
                api_url,
                headers={
                    "User-Agent": "Schubert-Toolbox/1.0",
                    "Accept": "application/json"
                },
                timeout=self._config["timeout"]
            )
            response.raise_for_status()

            # Parse JSON response
            company_data = response.json()
            
            # Convert to Company object
            company = self._convert_to_company(company_data, formatted_cnpj)

            logger.debug("Successfully retrieved company data for CNPJ: %s", cnpj)
            return company

        except requests.exceptions.RequestException as e:
            logger.error("BrasilAPI request failed: %s", e)
            raise ValidationError(f"Failed to lookup CNPJ: {e!s}")
        except (ValueError, KeyError) as e:
            logger.error("BrasilAPI response parsing failed: %s", e)
            raise ValidationError(f"Invalid API response: {e!s}")

    def _convert_to_company(self, data: Dict[str, Any], formatted_cnpj: str) -> Company:
        """
        Convert BrasilAPI response to Company object.

        BrasilAPI response format:
        {
            "cnpj": "11222333000181",
            "identificador_matriz_filial": 1,
            "descricao_matriz_filial": "Matriz",
            "razao_social": "EMPRESA EXEMPLO LTDA",
            "nome_fantasia": "Empresa Exemplo",
            "situacao_cadastral": 2,
            "descricao_situacao_cadastral": "Ativa",
            "data_situacao_cadastral": "2020-01-01",
            "motivo_situacao_cadastral": 0,
            "nome_cidade_exterior": null,
            "codigo_natureza_juridica": 2062,
            "data_inicio_atividade": "2020-01-01",
            "cnae_fiscal": 6201500,
            "cnae_fiscal_descricao": "Desenvolvimento de programas de computador sob encomenda",
            "descricao_tipo_logradouro": "Rua",
            "logradouro": "Das Flores",
            "numero": "123",
            "complemento": "Sala 1",
            "bairro": "Centro",
            "cep": "88304053",
            "uf": "SC",
            "codigo_municipio": 4208203,
            "municipio": "Itajaí",
            "ddd_telefone_1": "47",
            "telefone_1": "33334444",
            "ddd_telefone_2": null,
            "telefone_2": null,
            "ddd_fax": null,
            "fax": null,
            "correio_eletronico": "contato@empresa.com.br",
            "qualificacao_do_responsavel": 10,
            "capital_social": 10000.00,
            "porte": "05",
            "descricao_porte": "Demais",
            "opcao_pelo_simples": false,
            "data_opcao_pelo_simples": null,
            "data_exclusao_do_simples": null,
            "opcao_pelo_mei": false,
            "situacao_especial": null,
            "data_situacao_especial": null,
            "qsa": [...]
        }
        """
        # Check if company was found
        if not data or "cnpj" not in data:
            raise ValidationError(f"CNPJ not found: {formatted_cnpj}")

        # Create Brazil country object
        brazil = Country(code="BR", alpha3="BRA", numeric="076", name="Brazil", local_name="Brasil")

        # Parse company status
        status = data.get("descricao_situacao_cadastral", "UNKNOWN")

        # Build address if available
        address = self._build_address(data, brazil)

        # Build phone number
        phone = self._build_phone_number(data)

        # Parse share capital
        share_capital = None
        if data.get("capital_social"):
            try:
                share_capital = float(data["capital_social"])
            except (ValueError, TypeError):
                pass

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
            email=data.get("correio_eletronico"),

            # Business information
            primary_activity=data.get("cnae_fiscal_descricao"),
            company_size=data.get("descricao_porte"),
            share_capital=share_capital,
            legal_nature=data.get("codigo_natureza_juridica"),

            # Metadata
            country=brazil,
            is_verified=True,
            verification_source="brasilapi",
            last_updated=datetime.now()
        )

        # Mark as verified and set timestamp
        company.mark_as_verified("brasilapi")

        return company

    def _build_phone_number(self, data: Dict[str, Any]) -> Optional[str]:
        """Build formatted phone number from BrasilAPI data."""
        ddd = data.get("ddd_telefone_1")
        phone = data.get("telefone_1")

        if ddd and phone:
            # Remove any non-digit characters
            ddd_clean = re.sub(r'[^\d]', '', str(ddd))
            phone_clean = re.sub(r'[^\d]', '', str(phone))

            if len(ddd_clean) == 2 and len(phone_clean) >= 8:
                return f"({ddd_clean}) {phone_clean}"

        return None

    def _build_address(self, data: Dict[str, Any], country: Country) -> Optional[Address]:
        """
        Build Address object from BrasilAPI data.

        If postal code is available but address is incomplete,
        attempts to resolve full address using postal code lookup.
        """
        # Extract address components
        street_type = data.get("descricao_tipo_logradouro", "")
        street_name = data.get("logradouro", "")
        street_number = data.get("numero", "")
        complement = data.get("complemento", "")
        neighborhood = data.get("bairro", "")
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
        if street_type:
            street_parts.append(street_type)
        if street_name:
            street_parts.append(street_name)

        full_street = " ".join(street_parts) if street_parts else None

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
                if not neighborhood and resolved_address.neighborhood:
                    neighborhood = resolved_address.neighborhood
                if not city and resolved_address.locality:
                    city = resolved_address.locality
                if not state and resolved_address.administrative_area_1:
                    state = resolved_address.administrative_area_1

                logger.debug(f"Successfully resolved address for postal code: {formatted_postal_code}")

            except Exception as e:
                logger.debug(f"Failed to resolve address for postal code {formatted_postal_code}: {e}")

        # Create Address object if we have sufficient information
        if full_street or city or formatted_postal_code:
            # Build complete street address with number and complement
            complete_street = full_street
            if street_number:
                complete_street = f"{complete_street}, {street_number}" if complete_street else street_number
            if complement:
                complete_street = f"{complete_street}, {complement}" if complete_street else complement

            try:
                address = Address(
                    street_name=complete_street,
                    neighborhood=neighborhood or None,
                    locality=city or None,
                    administrative_area_1=state or None,
                    postal_code=formatted_postal_code,
                    country=country,
                    is_verified=True,
                    verification_source="brasilapi"
                )

                address.mark_as_verified("brasilapi")
                return address
            except Exception as e:
                logger.debug(f"Failed to create Address object: {e}")
                return None

        return None
