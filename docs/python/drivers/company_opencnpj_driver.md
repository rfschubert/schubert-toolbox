# OpenCNPJ Company Driver

The OpenCNPJ driver provides access to Brazilian company (CNPJ) data through the OpenCNPJ.org service, a free and community-driven API for Brazilian business information.

## Overview

OpenCNPJ.org is a free service that provides access to official Brazilian company data from government sources. The driver implements rate limiting and comprehensive error handling to ensure reliable operation.

**Key Features:**
- Free access to Brazilian company data
- Rate limiting (1 request per second)
- Automatic address resolution via postal code lookup
- Comprehensive error handling
- Retry logic for transient errors
- Full integration with CompanyManager

## Basic Usage

### Direct Driver Usage

```python
from drivers.company.company_opencnpj_driver import CompanyOpencnpjDriver

# Initialize driver
driver = CompanyOpencnpjDriver()

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
company = manager.get("11.222.333/0001-81", driver_name="opencnpj")
print(f"Company: {company.get_display_name()}")
print(f"Source: {company.verification_source}")  # "opencnpj"
```

## Configuration

The driver supports various configuration options:

```python
# Configure driver
driver = CompanyOpencnpjDriver()
driver.configure(
    timeout=20,           # Request timeout in seconds
    retries=3,           # Number of retry attempts
    rate_limit_delay=1.0, # Delay between requests (seconds)
    max_retry_delay=5.0  # Maximum retry delay
)

# Get current configuration
config = driver.get_configuration()
print(f"Timeout: {config['timeout']}")
print(f"Rate limit: {config['rate_limit_delay']}")
```

## Data Structure

The OpenCNPJ API returns data in the following format:

```json
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

## Rate Limiting

The driver implements automatic rate limiting:

- **Default delay**: 1 second between requests
- **Configurable**: Can be adjusted via `rate_limit_delay` parameter
- **Automatic**: No manual intervention required
- **Retry logic**: Exponential backoff for rate limit errors

```python
# Configure rate limiting
driver.configure(rate_limit_delay=2.0)  # 2 seconds between requests

# The driver will automatically wait between requests
company1 = driver.get("11.222.333/0001-81")  # Request 1
company2 = driver.get("22.333.444/0001-82")  # Waits 2 seconds, then Request 2
```

## Integration with CompanyManager

The OpenCNPJ driver is automatically registered with the CompanyManager and participates in the first-to-respond pattern:

```python
from managers.company_manager import CompanyManager

manager = CompanyManager()

# First-to-respond with all drivers (including OpenCNPJ)
company = manager.get_first_response_sync("11.222.333/0001-81")
print(f"Fastest driver: {company.verification_source}")

# May return "brasilapi", "cnpja", or "opencnpj" depending on response times
```

## API Limitations

- **Rate limiting**: 1 request per second (configurable)
- **Data availability**: May not have all CNPJs in database
- **Response time**: Variable depending on server load
- **Free service**: No SLA guarantees

## Best Practices

1. **Use CompanyManager**: Leverage first-to-respond for better reliability
2. **Configure timeouts**: Set appropriate timeout values for your use case
3. **Handle errors**: Always wrap calls in try-catch blocks
4. **Respect rate limits**: Don't override rate limiting unless necessary
5. **Cache results**: Consider caching company data to reduce API calls

## Troubleshooting

### Common Issues

**CNPJ not found (404)**
```python
# This is expected for CNPJs not in the database
try:
    company = driver.get("00.000.000/0001-00")
except ValidationError as e:
    print("CNPJ not found in OpenCNPJ database")
```

**Rate limiting**
```python
# Increase delay if hitting rate limits frequently
driver.configure(rate_limit_delay=2.0)
```

**Timeout errors**
```python
# Increase timeout for slow connections
driver.configure(timeout=30)
```

## API Reference

- **Base URL**: `https://api.opencnpj.org/cnpj/{cnpj}`
- **Method**: GET
- **Format**: JSON
- **Authentication**: None required
- **Documentation**: https://opencnpj.org/

## See Also

- [CompanyManager Documentation](../managers/company_manager.md)
- [Company Data Model](../standards/company.md)
- [BrasilAPI Driver](company_brasilapi_driver.md)
- [CNPJA Driver](company_cnpja_driver.md)
