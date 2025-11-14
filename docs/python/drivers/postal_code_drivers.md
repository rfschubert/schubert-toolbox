# Postal Code Drivers

This document provides detailed information about all postal code drivers available in the Schubert Toolbox system.

## Overview

Postal code drivers are responsible for looking up address information based on postal codes from various external APIs and services. They can be used either directly or through the [PostalCodeManager](../managers/implemented_managers.md#postalcodemanager).

All drivers integrate with the [FormatterManager](../managers/implemented_managers.md#formattermanager) to ensure consistent postal code formatting, following the DRY principle.

## Usage Patterns

### 1. Direct Driver Usage
Use drivers directly when you need fine-grained control over API configuration and behavior.

```python
from drivers.postalcode.postalcode_viacep_driver import PostalCodeViacepDriver

# Create driver instance
driver = PostalCodeViacepDriver()

# Configure driver
driver.configure(timeout=30, retries=5)

# Use driver
address = driver.get("88304-053")
print(address.get_display_name())
```

### 2. Manager-Orchestrated Usage
Use the PostalCodeManager for simplified driver management and fallback capabilities.

```python
from managers import PostalCodeManager

# Create manager
manager = PostalCodeManager()

# Use manager methods
address = manager.get("88304-053", driver="viacep")
print(address.get_display_name())

# Set default driver
manager.set_default_driver("viacep")
address = manager.get("88304-053")  # Uses default driver
```

## Available Drivers

### ViaCEP Driver

Integrates with the ViaCEP Brazilian postal code service (viacep.com.br).

#### Driver Information
- **Class**: `PostalCodeViacepDriver`
- **File**: `python/src/drivers/postalcode/postalcode_viacep_driver.py`
- **Manager Name**: `viacep`
- **API URL**: `https://viacep.com.br/ws`
- **Country**: Brazil
- **Rate Limits**: None specified
- **Response Format**: JSON

#### Configuration Options

```python
driver.configure(
    timeout=10,        # Request timeout in seconds
    retries=3,         # Number of retry attempts
    format='json'      # Response format (json only)
)
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `timeout` | `int` | `10` | Request timeout in seconds |
| `retries` | `int` | `3` | Number of retry attempts |
| `format` | `str` | `'json'` | Response format |

#### Usage Examples

##### Basic Usage

```python
from drivers.postalcode.postalcode_viacep_driver import PostalCodeViacepDriver

# Create and use driver
driver = PostalCodeViacepDriver()
address = driver.get("88304-053")

print(f"Street Name: {address.street_name}")
print(f"Locality: {address.locality}")
print(f"Administrative Area 1: {address.administrative_area_1}")
print(f"Postal Code: {address.postal_code}")
print(f"Full Address: {address.get_display_name()}")

# Output:
# Street Name: Rua Alberto Werner
# Locality: Itajaí
# Administrative Area 1: SC
# Postal Code: 88304-053
# Full Address: Rua Alberto Werner, Unit até 445 - lado ímpar, Itajaí, SC, Brazil
```

##### Configuration Example

```python
# Configure for production use
driver = PostalCodeViacepDriver()
driver.configure(
    timeout=30,     # Longer timeout for production
    retries=5,      # More retries for reliability
    format='json'   # Explicit format specification
)

# Get configuration
config = driver.get_config()
print("Current config:", config)
```

### WideNet Driver

Integrates with the WideNet postal code API (cdn.apicep.com).

#### Driver Information
- **Class**: `PostalCodeWidenetDriver`
- **File**: `python/src/drivers/postalcode/postalcode_widenet_driver.py`
- **Manager Name**: `widenet`
- **API URL**: `https://cdn.apicep.com/file/apicep`
- **Country**: Brazil
- **Rate Limits**: Yes (429 errors common)
- **Response Format**: JSON

#### Configuration Options

Same as ViaCEP driver:

```python
driver.configure(
    timeout=10,        # Request timeout in seconds
    retries=3,         # Number of retry attempts
    format='json'      # Response format
)
```

#### Usage Examples

```python
from drivers.postalcode.postalcode_widenet_driver import PostalCodeWidenetDriver

# Create driver with error handling
driver = PostalCodeWidenetDriver()

try:
    address = driver.get("88304-053")
    print(address.get_display_name())
except Exception as e:
    print(f"WideNet API error: {e}")
    # Common: "429 Client Error: Too Many Requests"
```

### BrasilAPI Driver

Integrates with the BrasilAPI postal code service (brasilapi.com.br).

#### Driver Information
- **Class**: `PostalCodeBrasilApiDriver`
- **File**: `python/src/drivers/postalcode/postalcode_brasilapi_driver.py`
- **Manager Name**: `brasilapi`
- **API URL**: `https://brasilapi.com.br/api/cep/v1`
- **Country**: Brazil
- **Rate Limits**: Yes (moderate)
- **Response Format**: JSON

#### Configuration Options

Same as other drivers:

```python
driver.configure(
    timeout=10,        # Request timeout in seconds
    retries=3,         # Number of retry attempts
    format='json'      # Response format
)
```

#### Usage Examples

```python
from drivers.postalcode.postalcode_brasilapi_driver import PostalCodeBrasilApiDriver

# Create and use driver
driver = PostalCodeBrasilApiDriver()
address = driver.get("88304-053")

print(f"Address: {address.get_display_name()}")
print(f"Locality: {address.locality}")
```

## Address Object Structure

All postal code drivers return standardized `Address` objects:

```python
from standards.address import Address, Country
from standards.core.base import BaseModel

@dataclass
class Address(BaseModel):
    """
    ISO 19160 compliant address with international support.
    Based on schemas/address.json schema definition.
    """

    # Street information
    street_number: Optional[str] = None
    street_name: Optional[str] = None
    street_type: Optional[str] = None  # Street, Avenue, Road, etc.
    unit: Optional[str] = None  # Apartment, suite, unit number
    building: Optional[str] = None  # Building name or number
    floor: Optional[str] = None  # Floor number

    # Geographic areas
    neighborhood: Optional[str] = None  # District, suburb, neighborhood
    locality: Optional[str] = None  # City, town, village
    sublocality: Optional[str] = None  # Sub-city area
    administrative_area_1: Optional[str] = None  # State, province, region
    administrative_area_2: Optional[str] = None  # County, district
    administrative_area_3: Optional[str] = None  # Sub-district

    # Postal information
    postal_code: Optional[str] = None
    postal_code_suffix: Optional[str] = None

    # Country information
    country: Optional[Country] = None

    # Address classification and verification
    address_type: AddressType = AddressType.RESIDENTIAL
    status: AddressStatus = AddressStatus.ACTIVE
    is_verified: bool = False
    verified_at: Optional[datetime] = None
    verification_source: Optional[str] = None

    def get_display_name(self) -> str:
        """Get a human-readable display name for the address."""

    def get_full_street_address(self) -> Optional[str]:
        """Get complete street address combining number, name, and type."""

    def is_complete(self) -> bool:
        """Check if address has sufficient information for delivery."""

    def mark_as_verified(self, source: Optional[str] = None) -> None:
        """Mark address as verified."""
```

### Address Properties

```python
address = driver.get("88304-053")

# Access individual properties
print(f"Postal Code: {address.postal_code}")              # "88304-053"
print(f"Street Name: {address.street_name}")              # "Rua Alberto Werner"
print(f"Unit: {address.unit}")                           # "Unit até 445 - lado ímpar"
print(f"Locality: {address.locality}")                   # "Itajaí"
print(f"Administrative Area 1: {address.administrative_area_1}")  # "SC"
print(f"Country: {address.country.name}")                # "Brazil"

# Get formatted display
print(f"Full: {address.get_display_name()}")
# "Rua Alberto Werner, Unit até 445 - lado ímpar, Itajaí, SC, Brazil"

# Get full street address
print(f"Street: {address.get_full_street_address()}")
# "Rua Alberto Werner"
```

## Advanced Usage Patterns

### Error Handling with Direct Drivers

```python
from validation_base import ValidationError

def safe_address_lookup(postal_code: str, driver_class):
    """Safely lookup address with comprehensive error handling."""

    try:
        driver = driver_class()
        driver.configure(timeout=30, retries=3)

        address = driver.get(postal_code)
        return {
            "success": True,
            "address": address,
            "driver": driver.name
        }

    except ValidationError as e:
        return {
            "success": False,
            "error": "Invalid postal code",
            "message": e.message,
            "error_code": e.error_code
        }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Timeout",
            "message": "API request timed out"
        }
    except requests.exceptions.HTTPError as e:
        return {
            "success": False,
            "error": "HTTP Error",
            "message": str(e),
            "status_code": e.response.status_code if e.response else None
        }
    except Exception as e:
        return {
            "success": False,
            "error": "Unknown Error",
            "message": str(e)
        }

# Usage
from drivers.postalcode.postalcode_viacep_driver import PostalCodeViacepDriver

result = safe_address_lookup("88304-053", PostalCodeViacepDriver)
if result["success"]:
    print(f"Address: {result['address'].get_display_name()}")
else:
    print(f"Error: {result['error']} - {result['message']}")
```

### Multi-Driver Fallback Pattern

```python
def robust_address_lookup(postal_code: str):
    """Lookup address with automatic fallback between drivers."""

    # Import all drivers
    from drivers.postalcode.postalcode_viacep_driver import PostalCodeViacepDriver
    from drivers.postalcode.postalcode_brasilapi_driver import PostalCodeBrasilApiDriver
    from drivers.postalcode.postalcode_widenet_driver import PostalCodeWidenetDriver

    # Define fallback order (most reliable first)
    drivers = [
        ("ViaCEP", PostalCodeViacepDriver),
        ("BrasilAPI", PostalCodeBrasilApiDriver),
        ("WideNet", PostalCodeWidenetDriver)
    ]

    for driver_name, driver_class in drivers:
        try:
            print(f"Trying {driver_name}...")
            driver = driver_class()
            driver.configure(timeout=15, retries=2)

            address = driver.get(postal_code)
            print(f"Success with {driver_name}")
            return {
                "success": True,
                "address": address,
                "driver_used": driver_name
            }

        except Exception as e:
            print(f"✗ {driver_name} failed: {str(e)}")
            continue

    return {
        "success": False,
        "error": "All drivers failed",
        "drivers_tried": [name for name, _ in drivers]
    }

# Usage
result = robust_address_lookup("88304-053")
if result["success"]:
    print(f"Address: {result['address'].get_display_name()}")
    print(f"Driver used: {result['driver_used']}")
else:
    print(f"Failed with all drivers: {result['drivers_tried']}")
```

### Bulk Processing with Direct Drivers

```python
def bulk_address_lookup(postal_codes: list, driver_class, max_workers=5):
    """Process multiple postal codes with threading."""

    import concurrent.futures
    import threading

    # Thread-local driver instances
    thread_local = threading.local()

    def get_driver():
        if not hasattr(thread_local, 'driver'):
            thread_local.driver = driver_class()
            thread_local.driver.configure(timeout=20, retries=2)
        return thread_local.driver

    def lookup_single(postal_code):
        try:
            driver = get_driver()
            address = driver.get(postal_code)
            return {
                "postal_code": postal_code,
                "success": True,
                "address": address
            }
        except Exception as e:
            return {
                "postal_code": postal_code,
                "success": False,
                "error": str(e)
            }

    # Process in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(lookup_single, postal_codes))

    return results

# Usage
postal_codes = ["88304-053", "01310-100", "20040-020"]
results = bulk_address_lookup(postal_codes, PostalCodeViacepDriver)

for result in results:
    if result["success"]:
        print(f"SUCCESS {result['postal_code']}: {result['address'].locality}")
    else:
        print(f"ERROR {result['postal_code']}: {result['error']}")
```

## Manager vs Direct Usage Comparison

### When to Use Direct Driver Access

**Advantages:**
- **Fine-grained control**: Direct access to all driver methods and configuration
- **Performance**: No manager overhead for high-volume operations
- **Custom error handling**: Handle specific API errors differently
- **Advanced configuration**: Access to driver-specific settings
- **Threading control**: Manage thread-local instances for parallel processing

**Use Cases:**
- High-performance bulk processing
- Custom fallback logic
- Specific API error handling requirements
- Integration with existing threading/async code
- Driver-specific feature requirements

**Example:**
```python
# Direct usage for custom fallback logic
def custom_lookup_with_fallback(postal_code: str):
    # Try ViaCEP first (most reliable)
    try:
        viacep = PostalCodeViacepDriver()
        viacep.configure(timeout=10, retries=1)  # Fast fail
        return viacep.get(postal_code)
    except Exception:
        pass

    # Try BrasilAPI with different config
    try:
        brasilapi = PostalCodeBrasilApiDriver()
        brasilapi.configure(timeout=20, retries=3)  # More patient
        return brasilapi.get(postal_code)
    except Exception:
        pass

    # Last resort: WideNet with very patient config
    widenet = PostalCodeWidenetDriver()
    widenet.configure(timeout=30, retries=5)
    return widenet.get(postal_code)
```

### When to Use Manager-Orchestrated Access

**Advantages:**
- **Simplicity**: Easy-to-use unified API
- **Consistency**: Same interface across all drivers
- **Built-in fallback**: Automatic driver fallback with `bulk_get`
- **Caching**: Automatic result caching for performance
- **Driver discovery**: Dynamic driver selection
- **Standardized error handling**: Consistent error management
- **Integration**: Works seamlessly with FormatterManager

**Use Cases:**
- Simple address lookups
- Applications requiring caching
- Dynamic driver selection
- Integration with other managers
- Standardized error handling needs

**Example:**
```python
# Manager usage for simple, reliable lookups
manager = PostalCodeManager()

# Set preferred driver
manager.set_default_driver("viacep")

# Enable caching for performance
manager.enable_cache(True)

# Simple lookup with automatic formatting
address = manager.get("88304053")  # Automatically formatted to "88304-053"

# Bulk lookup with automatic fallback
postal_codes = ["88304053", "01310100", "20040020"]
addresses = manager.bulk_get(postal_codes)  # Handles errors gracefully
```

## Integration with FormatterManager

All postal code drivers automatically integrate with FormatterManager to ensure consistent postal code formatting:

### Automatic Formatting

```python
# All drivers accept various input formats
test_inputs = [
    "88304053",      # No formatting
    "88304-053",     # Already formatted
    "88.304-053",    # With dots
    "  88304053  ",  # With spaces
    88304053         # Integer
]

driver = PostalCodeViacepDriver()

for input_code in test_inputs:
    address = driver.get(input_code)
    print(f"Input: {input_code!r} -> Output: {address.postal_code}")

# All outputs will be: "88304-053"
```

### DRY Principle Applied

The integration eliminates code duplication:

```python
# Before integration (duplicated formatting logic in each driver)
# Each driver had its own _clean_postal_code, _validate_postal_code, _format_postal_code

# After integration (DRY principle applied)
# All drivers use FormatterManager internally:

class PostalCodeViacepDriver:
    def __init__(self):
        self._formatter_manager = FormatterManager()  # Single source of truth

    def get(self, postal_code):
        # Use centralized formatting
        formatted_cep = self._formatter_manager.format(
            postal_code,
            driver="brazilian_postalcode"
        )
        # Continue with API call using formatted CEP
```

## Performance Considerations

### Direct Driver Performance

```python
import time

# Direct driver - optimal for repeated use with same configuration
driver = PostalCodeViacepDriver()
driver.configure(timeout=10, retries=2)

start_time = time.time()
addresses = []
for i in range(100):  # Smaller number due to API calls
    try:
        address = driver.get(f"8830405{i % 10}")
        addresses.append(address)
    except Exception:
        pass

direct_time = time.time() - start_time
print(f"Direct driver: {direct_time:.3f}s for {len(addresses)} successful lookups")
```

### Manager Performance with Caching

```python
# Manager with caching - good for repeated lookups
manager = PostalCodeManager()
manager.enable_cache(True)

start_time = time.time()
addresses = []
postal_codes = [f"8830405{i % 3}" for i in range(100)]  # Repeated codes for cache hits

for code in postal_codes:
    try:
        address = manager.get(code, driver="viacep")
        addresses.append(address)
    except Exception:
        pass

manager_time = time.time() - start_time
cache_stats = manager.get_cache_stats()

print(f"Manager with cache: {manager_time:.3f}s for {len(addresses)} lookups")
print(f"Cache hits: {cache_stats['size']} entries")
```

### Bulk Operations Performance

```python
# Bulk operations - most efficient for large datasets
postal_codes = ["88304-053", "01310-100", "20040-020"] * 10  # 30 codes

start_time = time.time()
addresses = manager.bulk_get(postal_codes, driver="viacep")
bulk_time = time.time() - start_time

successful = [addr for addr in addresses if addr is not None]
print(f"Bulk operation: {bulk_time:.3f}s for {len(successful)} successful lookups")
```

## Best Practices

### 1. Choose the Right Usage Pattern
- **Direct driver**: For performance-critical, custom logic, or driver-specific features
- **Manager**: For simple tasks, caching needs, and consistent API usage

### 2. Handle API Errors Gracefully
```python
# Always handle common API errors
try:
    address = driver.get(postal_code)
except requests.exceptions.Timeout:
    logger.warning(f"API timeout for {postal_code}")
    return None
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 429:
        logger.warning(f"Rate limited for {postal_code}")
        time.sleep(1)  # Brief pause before retry
    return None
except ValidationError as e:
    logger.error(f"Invalid postal code {postal_code}: {e.message}")
    return None
```

### 3. Configure Timeouts Appropriately
```python
# Production configuration
driver.configure(
    timeout=30,     # Generous timeout for production
    retries=3,      # Reasonable retry count
    format='json'   # Explicit format
)
```

### 4. Use Caching for Repeated Lookups
```python
# Enable caching when using manager
manager = PostalCodeManager()
manager.enable_cache(True)

# Cache will store results and avoid repeated API calls
for postal_code in frequently_used_codes:
    address = manager.get(postal_code)  # Cached after first call
```

### 5. Implement Fallback Strategies
```python
# Use multiple drivers for reliability
def reliable_lookup(postal_code: str):
    manager = PostalCodeManager()

    # Try drivers in order of preference
    for driver_name in ["viacep", "brasilapi", "widenet"]:
        try:
            return manager.get(postal_code, driver=driver_name)
        except Exception as e:
            logger.warning(f"{driver_name} failed for {postal_code}: {e}")
            continue

    raise Exception("All postal code services failed")
```

### 6. Validate Input Before API Calls
```python
# Pre-validate to avoid unnecessary API calls
from managers import FormatterManager

formatter = FormatterManager()

def lookup_with_validation(postal_code: str):
    # Validate format first
    if not formatter.is_valid_format(postal_code, driver="brazilian_postalcode"):
        raise ValidationError("Invalid postal code format")

    # Format for consistency
    formatted_code = formatter.format(postal_code, driver="brazilian_postalcode")

    # Proceed with lookup
    manager = PostalCodeManager()
    return manager.get(formatted_code)
```

## See Also

- [PostalCodeManager](../managers/implemented_managers.md#postalcodemanager) - Manager documentation
- [FormatterManager](../managers/implemented_managers.md#formattermanager) - Formatting integration
- [Formatter Drivers](formatter_drivers.md) - Related formatter drivers
- [Contracts Overview](../contracts/contracts_overview.md) - System contracts

---

*This documentation covers all postal code drivers available in the Schubert Toolbox system.*
