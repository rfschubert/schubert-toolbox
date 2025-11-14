# CNPJ.ws Company Driver

The CNPJ.ws driver provides access to Brazilian company (CNPJ) data through the CNPJ.ws service, a comprehensive API for Brazilian business information with detailed company data including partners, activities, and complete address information.

## Overview

CNPJ.ws is a service that provides access to official Brazilian company data from government sources. The driver implements strict rate limiting to respect the API's usage policies (3 requests per minute for the public API).

**Key Features:**
- Free access to comprehensive Brazilian company data
- Strict rate limiting (20 seconds between requests)
- Detailed company information including partners and activities
- Automatic address resolution via postal code lookup
- Comprehensive error handling
- Retry logic for transient errors
- Full integration with CompanyManager

## Basic Usage

### Direct Driver Usage

```python
from drivers.company.company_cnpjws_driver import CompanyCnpjwsDriver

# Initialize driver
driver = CompanyCnpjwsDriver()

# Basic company lookup
company = driver.get("11.222.333/0001-81")
print(f"Company: {company.get_display_name()}")
print(f"Status: {company.status}")
print(f"Active: {company.is_active()}")
```

### Manager Usage (Recommended)

```python
from managers.company_manager import CompanyManager

# Initialize manager
manager = CompanyManager()

# Use specific driver
company = manager.get("11.222.333/0001-81", driver_name="cnpjws")
print(f"Company: {company.get_display_name()}")
print(f"Source: {company.verification_source}")  # "cnpjws"
```

## Configuration

The driver supports various configuration options:

```python
# Configure driver
driver = CompanyCnpjwsDriver()
driver.configure(
    timeout=30,           # Request timeout in seconds
    retries=3,           # Number of retry attempts
    rate_limit_delay=20.0, # Delay between requests (seconds)
    max_retry_delay=60.0  # Maximum retry delay
)

# Get current configuration
config = driver.get_configuration()
print(f"Timeout: {config['timeout']}")
print(f"Rate limit: {config['rate_limit_delay']}")
```

## Rate Limiting

The CNPJ.ws public API has strict rate limiting:

- **Public API**: 3 requests per minute
- **Driver default**: 20 seconds between requests
- **Configurable**: Can be adjusted via `rate_limit_delay` parameter
- **Automatic**: No manual intervention required
- **Retry logic**: Exponential backoff for rate limit errors

```python
# Configure rate limiting (be careful not to exceed API limits)
driver.configure(rate_limit_delay=25.0)  # 25 seconds between requests

# The driver will automatically wait between requests
company1 = driver.get("11.222.333/0001-81")  # Request 1
company2 = driver.get("22.333.444/0001-82")  # Waits 25 seconds, then Request 2
```

## Data Structure

The CNPJ.ws API returns very detailed data in the following format:

```json
{
  "cnpj_raiz": "11222333",
  "razao_social": "EMPRESA EXEMPLO LTDA",
  "capital_social": "10000.00",
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
    "nome_fantasia": "Empresa Exemplo",
    "situacao_cadastral": "Ativa",
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
      "nome": "Itajaí"
    },
    "estado": {
      "sigla": "SC"
    }
  }
}
```

## Error Handling

The driver handles various error conditions:

```python
from standards.core.base import ValidationError

try:
    company = driver.get("invalid-cnpj")
except ValidationError as e:
    print(f"Validation error: {e}")
    # Handle invalid CNPJ format

try:
    company = driver.get("00.000.000/0001-00")
except ValidationError as e:
    print(f"CNPJ not found: {e}")
    # Handle CNPJ not found (404)
```

## Integration with CompanyManager

The CNPJ.ws driver is automatically registered with the CompanyManager and participates in the first-to-respond pattern:

```python
from managers.company_manager import CompanyManager

manager = CompanyManager()

# First-to-respond with all drivers (including CNPJ.ws)
company = manager.get_first_response_sync("11.222.333/0001-81")
print(f"Fastest driver: {company.verification_source}")

# May return "brasilapi", "cnpja", "opencnpj", or "cnpjws" depending on response times
```

## API Limitations

- **Rate limiting**: 3 requests per minute for public API
- **Response time**: Can be slower due to comprehensive data
- **Data availability**: Comprehensive coverage of Brazilian companies
- **Free service**: No SLA guarantees

## Best Practices

1. **Use CompanyManager**: Leverage first-to-respond for better reliability
2. **Respect rate limits**: Don't override rate limiting settings
3. **Configure timeouts**: Set appropriate timeout values for your use case
4. **Handle errors**: Always wrap calls in try-catch blocks
5. **Cache results**: Consider caching company data to reduce API calls
6. **Use for detailed data**: Best for when you need comprehensive company information

## Troubleshooting

### Common Issues

**Rate limiting**
```python
# The driver automatically handles rate limiting
# If you see rate limit errors, increase the delay
driver.configure(rate_limit_delay=25.0)
```

**Timeout errors**
```python
# Increase timeout for slow connections
driver.configure(timeout=45)
```

**CNPJ not found (404)**
```python
# This is expected for CNPJs not in the database
try:
    company = driver.get("00.000.000/0001-00")
except ValidationError as e:
    print("CNPJ not found in CNPJ.ws database")
```

## API Reference

- **Base URL**: `https://publica.cnpj.ws/cnpj/{cnpj}`
- **Method**: GET
- **Format**: JSON
- **Authentication**: None required for public API
- **Rate Limit**: 3 requests per minute
- **Documentation**: https://docs.cnpj.ws/

## See Also

- [CompanyManager Documentation](../managers/company_manager.md)
- [Company Data Model](../standards/company.md)
- [BrasilAPI Driver](company_brasilapi_driver.md)
- [CNPJA Driver](company_cnpja_driver.md)
- [OpenCNPJ Driver](company_opencnpj_driver.md)
