# Company Drivers

Company drivers provide access to Brazilian legal entity (CNPJ) data from various providers. These drivers follow the same architectural patterns as postal code drivers, ensuring consistency and reliability.

## Overview

Company drivers are designed to:

- **Retrieve comprehensive company data** from Brazilian government sources
- **Provide consistent interfaces** across different data providers
- **Handle automatic formatting** and validation of CNPJ numbers
- **Support address resolution** via postal code lookup when needed
- **Enable high-performance lookups** through the first-to-respond pattern

## Available Drivers

| Driver | API | Status | Performance | Características |
|--------|-----|--------|-------------|----------------|
| **BrasilAPI** | brasilapi.com.br | ✅ Ativo | ~0.06s | Rápido, confiável |
| **OpenCNPJ** | api.opencnpj.org | ✅ Ativo | ~0.03s | Mais rápido, SSL customizado |
| **CNPJA** | open.cnpja.com | ✅ Ativo | ~0.51s | Dados detalhados |
| **CNPJ.ws** | cnpj.ws | ✅ Ativo | ~2.2s | Rate limiting |

### BrasilAPI Company Driver

**Driver Name:** `brasilapi`
**Provider:** BrasilAPI (https://brasilapi.com.br/)
**Cost:** Free
**Rate Limits:** Moderate (community-friendly)
**Performance:** ~0.06s (rápido)
**Data Source:** Official Brazilian government data

#### Features

- **Free access** to official company data
- **Comprehensive information** including business activities, status, and contact details
- **Automatic address resolution** using postal code lookup when address is incomplete
- **Rate limiting friendly** with reasonable request limits
- **High reliability** backed by official government sources

#### Usage

```python
from drivers.company.company_brasilapi_driver import CompanyBrasilApiDriver

# Direct driver usage
driver = CompanyBrasilApiDriver()
company = driver.get("11.222.333/0001-81")

print(f"Company: {company.get_display_name()}")
print(f"Legal Name: {company.legal_name}")
print(f"Trade Name: {company.trade_name}")
print(f"Status: {company.status}")
print(f"Activity: {company.primary_activity}")
```

#### Configuration

```python
# Configure driver settings
driver.configure(
    timeout=30,  # Request timeout in seconds
    retries=3    # Number of retry attempts
)

# Get current configuration
config = driver.get_configuration()
print(f"Current config: {config}")
```

#### Data Provided

The BrasilAPI driver provides comprehensive company information:

**Basic Information:**
- CNPJ (formatted)
- Legal name (razão social)
- Trade name (nome fantasia)
- Company status (situação cadastral)
- Registration date (data de início de atividade)

**Address Information:**
- Complete address when available
- Automatic postal code resolution for missing address details
- City, state, and postal code
- Neighborhood information

**Business Information:**
- Primary business activity (CNAE principal)
- Company size classification (porte)
- Share capital (capital social)
- Legal nature code (natureza jurídica)

**Contact Information:**
- Phone number (formatted)
- Email address (when available)

#### Example Response

```python
company = driver.get("11.222.333/0001-81")

# Basic information
print(f"CNPJ: {company.cnpj}")
print(f"Legal Name: {company.legal_name}")
print(f"Trade Name: {company.trade_name}")
print(f"Status: {company.status}")
print(f"Active: {company.is_active()}")

# Business information
print(f"Activity: {company.primary_activity}")
print(f"Size: {company.company_size}")
print(f"Capital: {company.share_capital}")

# Contact information
if company.phone:
    print(f"Phone: {company.phone}")
if company.email:
    print(f"Email: {company.email}")

# Address information
if company.address:
    print(f"Address: {company.get_full_address()}")

# Metadata
print(f"Source: {company.verification_source}")
print(f"Last Updated: {company.last_updated}")
```

## Manager Integration

Company drivers are designed to work seamlessly with the CompanyManager:

```python
from managers.company_manager import CompanyManager

manager = CompanyManager()

# List available drivers
drivers = manager.list_drivers()
print(f"Available drivers: {drivers}")

# Get driver information
info = manager.get_driver_info("brasilapi")
print(f"Driver info: {info}")

# Use specific driver
company = manager.get("11.222.333/0001-81", driver_name="brasilapi")

# First-to-respond pattern
company = manager.get_first_response_sync("11.222.333/0001-81")
```

## Error Handling

Company drivers provide comprehensive error handling:

```python
from standards.core.base import ValidationError

try:
    company = driver.get("invalid-cnpj")
except ValidationError as e:
    print(f"Validation error: {e}")
except Exception as e:
    print(f"API error: {e}")
```

**Common Error Scenarios:**
- Invalid CNPJ format
- CNPJ not found in database
- API request failures
- Network timeouts
- Rate limiting (future)

## Performance Characteristics

**BrasilAPI Driver Performance:**
- **Average Response Time:** ~60-100ms
- **Success Rate:** >99% for valid CNPJs
- **Rate Limits:** Community-friendly (no strict limits currently)
- **Reliability:** High (backed by official data sources)

## Future Drivers

The architecture is prepared for additional drivers:

**Planned Drivers:**
- **Receita Federal**: Official government API (when available)
- **CNPJ.ws**: Premium commercial service
- **ReceitaWS**: Alternative commercial service
- **International**: Support for other countries' business registries

## Best Practices

### Performance Optimization

```python
# Use first-to-respond for best performance
company = manager.get_first_response_sync(cnpj)

# Configure appropriate timeouts
driver.configure(timeout=10)  # Reasonable timeout

# Cache results when appropriate (implement at application level)
```

### Error Handling

```python
def safe_company_lookup(cnpj: str) -> Optional[Company]:
    try:
        return manager.get_first_response_sync(cnpj, timeout=5.0)
    except ValidationError as e:
        logger.warning(f"Invalid CNPJ {cnpj}: {e}")
        return None
    except Exception as e:
        logger.error(f"Company lookup failed for {cnpj}: {e}")
        return None
```

### Data Validation

```python
def validate_company_data(company: Company) -> bool:
    """Validate essential company data."""
    if not company.cnpj or not company.legal_name:
        return False
    
    if not company.is_active():
        logger.warning(f"Company {company.cnpj} is not active: {company.status}")
        return False
    
    return True
```

## Integration Examples

### E-commerce Vendor Verification

```python
def verify_vendor(cnpj: str) -> dict:
    """Verify vendor company information."""
    try:
        company = manager.get_first_response_sync(cnpj)
        
        return {
            "valid": True,
            "active": company.is_active(),
            "name": company.get_display_name(),
            "legal_name": company.legal_name,
            "activity": company.primary_activity,
            "address": company.get_full_address(),
            "verification_source": company.verification_source
        }
    except Exception as e:
        return {
            "valid": False,
            "error": str(e)
        }
```

### CRM Data Enrichment

```python
def enrich_company_data(cnpj: str) -> dict:
    """Enrich CRM with company data."""
    company = manager.get_first_response_sync(cnpj)
    
    return {
        "cnpj": company.cnpj,
        "legal_name": company.legal_name,
        "trade_name": company.trade_name,
        "status": company.status,
        "activity": company.primary_activity,
        "size": company.company_size,
        "phone": company.phone,
        "email": company.email,
        "address": company.to_dict().get("address"),
        "last_verified": company.last_updated
    }
```

## Additional Drivers (Updated 2024.11)

### OpenCNPJ Company Driver

**Driver Name:** `opencnpj`
**Provider:** OpenCNPJ (https://api.opencnpj.org/)
**Cost:** Free
**Performance:** ~0.03s (mais rápido)
**SSL:** Configuração customizada (verify=False)
**Status:** ✅ Ativo

#### Features

- **Performance máxima** - Driver mais rápido disponível
- **SSL handling automático** - Contorna problemas de certificado
- **Dados completos** com sócios e atividades
- **Warning suppression** - Remove avisos de SSL
- **Rate limiting moderado** - Permite consultas frequentes

#### Usage

```python
from drivers.company.company_opencnpj_driver import CompanyOpencnpjDriver

driver = CompanyOpencnpjDriver()
company = driver.get("15.280.995/0001-69")
print(f"Company: {company.get_display_name()}")
```

### CNPJA Company Driver

**Driver Name:** `cnpja`
**Provider:** CNPJA (https://open.cnpja.com/)
**Cost:** Free
**Performance:** ~0.51s (moderado)
**Data Quality:** Muito detalhados
**Status:** ✅ Ativo

#### Features

- **Dados muito detalhados** incluindo capital social
- **API moderna** com estrutura JSON rica
- **Informações de porte** e classificação da empresa
- **Status Simples Nacional** e MEI
- **Dados de sócios** com qualificação detalhada

#### Usage

```python
from drivers.company.company_cnpja_driver import CompanyCnpjaDriver

driver = CompanyCnpjaDriver()
company = driver.get("15.280.995/0001-69")
print(f"Capital: R$ {company.share_capital:,.2f}")
```

### CNPJ.ws Company Driver

**Driver Name:** `cnpjws`
**Provider:** CNPJ.ws (https://cnpj.ws/)
**Cost:** Free
**Performance:** ~2.2s (rate limiting)
**Rate Limiting:** Agressivo
**Status:** ✅ Ativo

#### Features

- **Rate limiting robusto** com backoff exponencial
- **Dados completos** incluindo histórico da empresa
- **Retry logic inteligente** com diferentes delays
- **Error handling específico** para diferentes tipos de erro

#### Usage

```python
from drivers.company.company_cnpjws_driver import CompanyCnpjwsDriver

driver = CompanyCnpjwsDriver()
company = driver.get("15.280.995/0001-69")
print(f"Activities: {len(company.secondary_activities)}")
```

## Performance Comparison

| Driver | Tempo Médio | Uso Recomendado |
|--------|-------------|-----------------|
| **OpenCNPJ** | ~0.03s | First-to-respond, consultas frequentes |
| **BrasilAPI** | ~0.06s | Backup confiável, dados oficiais |
| **CNPJA** | ~0.51s | Dados detalhados, análises |
| **CNPJ.ws** | ~2.2s | Fallback, dados históricos |

## CompanyManager Features

### First-to-Respond Pattern

```python
from managers.company_manager import CompanyManager

manager = CompanyManager()
company = manager.get_first_response_sync("15.280.995/0001-69", timeout=5.0)
print(f"Winner: {company.verification_source}")  # Usually "opencnpj"
```

### Error Handling

- **SSL Errors**: Configuração automática (OpenCNPJ)
- **Rate Limiting**: Backoff exponencial automático
- **Network Errors**: Retry com delays progressivos
- **API Errors**: Tratamento específico por código de erro
- **Validation Errors**: Integração com FormatterManager
