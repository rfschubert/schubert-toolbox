# CompanyManager

The CompanyManager provides unified access to Brazilian company (CNPJ) data providers, supporting both individual lookups and first-to-respond patterns for optimal performance and reliability.

## Overview

The CompanyManager follows the same architectural patterns as the PostalCodeManager, providing:

- **Unified Interface**: Single API for multiple company data providers
- **First-to-Respond**: Concurrent driver execution for maximum performance
- **Automatic Fallback**: If one driver fails, others continue
- **Address Resolution**: Automatic postal code lookup for complete addresses
- **Rate Limiting**: Built-in rate limiting for all drivers

## Quick Start

### Basic Usage

```python
from managers.company_manager import CompanyManager

manager = CompanyManager()

# Basic company lookup
company = manager.get("11.222.333/0001-81")
print(f"Company: {company.get_display_name()}")
print(f"Status: {company.status}")
print(f"Active: {company.is_active()}")
```

### First-to-Respond Pattern

```python
# Synchronous first-to-respond (recommended)
company = manager.get_first_response_sync("11.222.333/0001-81")
print(f"Fastest driver: {company.verification_source}")

# Asynchronous first-to-respond
import asyncio
company = asyncio.run(manager.get_first_response("11.222.333/0001-81"))
```

### Advanced Configuration

```python
# With specific drivers and timeout
company = manager.get_first_response_sync(
    "11.222.333/0001-81",
    drivers=["brasilapi"],  # Specify drivers to use
    timeout=5.0  # Maximum wait time
)
```

## Available Drivers

Currently supported drivers:

- **brasilapi**: BrasilAPI company data service (free, reliable, fast)
- **cnpja**: CNPJA.com company data service (free, rate limited)
- **opencnpj**: OpenCNPJ.org company data service (free, community-driven)
- **cnpjws**: CNPJ.ws company data service (free, comprehensive data, strict rate limiting)

All drivers provide comprehensive Brazilian company data with automatic fallback support through the first-to-respond pattern.

## Company Data Model

The CompanyManager returns `Company` objects with the following structure:

```python
@dataclass
class Company:
    # Basic identification
    cnpj: str                    # Formatted CNPJ
    legal_name: str             # Razão social
    trade_name: Optional[str]   # Nome fantasia
    
    # Status and registration
    status: str                 # Company status (ATIVA, SUSPENSA, etc.)
    registration_date: Optional[str]  # Data de início de atividade
    
    # Address information
    address: Optional[Address]  # Complete address (if available)
    
    # Contact information
    phone: Optional[str]        # Formatted phone number
    email: Optional[str]        # Email address
    
    # Business information
    primary_activity: Optional[str]    # CNAE principal description
    company_size: Optional[str]        # Porte da empresa
    share_capital: Optional[float]     # Capital social
    legal_nature: Optional[str]        # Natureza jurídica
    
    # Metadata
    country: Country            # Brazil by default
    is_verified: bool          # Verification status
    verification_source: str   # Driver that provided the data
    last_updated: Optional[datetime]  # Last update timestamp
```

## Methods

### Core Methods

#### `get(cnpj: str, driver_name: Optional[str] = None) -> Company`

Get company data using specified or default driver.

**Parameters:**
- `cnpj`: CNPJ number (formatted or unformatted)
- `driver_name`: Optional driver name

**Returns:** Company object

#### `get_first_response_sync(cnpj: str, drivers: Optional[List[str]] = None, timeout: float = 10.0) -> Company`

Synchronous first-to-respond lookup.

**Parameters:**
- `cnpj`: CNPJ number
- `drivers`: Optional list of driver names
- `timeout`: Maximum wait time in seconds

**Returns:** Company object from fastest driver

#### `get_first_response(cnpj: str, drivers: Optional[List[str]] = None, timeout: float = 10.0) -> Company`

Asynchronous first-to-respond lookup.

**Parameters:**
- `cnpj`: CNPJ number
- `drivers`: Optional list of driver names  
- `timeout`: Maximum wait time in seconds

**Returns:** Company object from fastest driver

### Utility Methods

#### `list_drivers() -> List[str]`

List all available company driver names.

#### `get_driver_info(driver_name: str) -> Dict[str, str]`

Get information about a specific driver.

## Error Handling

```python
from standards.core.base import ValidationError

try:
    company = manager.get_first_response_sync("00.000.000/0001-00")  # Invalid CNPJ
except ValidationError as e:
    print(f"Validation error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Performance Benefits

The first-to-respond pattern provides significant performance improvements:

```python
import time

# Traditional approach
start = time.time()
company = manager.get("11.222.333/0001-81")
traditional_time = time.time() - start

# First-to-respond approach  
start = time.time()
company = manager.get_first_response_sync("11.222.333/0001-81")
first_to_respond_time = time.time() - start

print(f"Traditional: {traditional_time:.3f}s")
print(f"First-to-respond: {first_to_respond_time:.3f}s")
# Typically shows similar or better performance with single driver
# Major benefits appear when multiple drivers are available
```

## Use Cases

**Ideal for:**
- Business applications requiring company validation
- E-commerce platforms for vendor verification
- Financial systems for due diligence
- CRM systems for company data enrichment
- Compliance and regulatory reporting

**Features:**
- Automatic CNPJ formatting and validation
- Complete company information retrieval
- Address resolution via postal code lookup
- High-performance concurrent lookups
- Comprehensive error handling
