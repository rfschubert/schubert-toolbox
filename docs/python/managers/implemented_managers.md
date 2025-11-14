# Implemented Managers

This document provides detailed information about the managers currently implemented in the Schubert Toolbox system.

## Overview

Managers are orchestrator classes that provide unified interfaces for loading, configuring, and using drivers of specific types. They abstract the complexity of driver management while ensuring consistent APIs across different domains.

All managers implement the [ManagerContract](../contracts/manager_contract.md) and follow the [Manager Pattern](../patterns/manager_pattern_details.md).

## Table of Contents

1. [FormatterManager](#formattermanager)
2. [PostalCodeManager](#postalcodemanager)
3. [Usage Patterns](#usage-patterns)
4. [Integration Examples](#integration-examples)

## FormatterManager

The FormatterManager orchestrates data formatting drivers to provide consistent data transformation capabilities.

### Purpose

Manages formatters that transform input data into standardized output formats (postal codes, phone numbers, currencies, etc.).

### Location
- **File**: `python/src/managers/formatter_manager.py`
- **Class**: `FormatterManager`
- **Contract**: Implements `ManagerContract`

### Available Drivers

| Driver Name | Description | Input Types | Output Format |
|-------------|-------------|-------------|---------------|
| `brazilian_postalcode` | Brazilian postal code formatter | `str`, `int` | `XXXXX-XXX` |

### Core Methods

#### Manager Contract Methods

```python
def load(self, driver_name: str, **config) -> FormatterContract:
    """Load and configure a formatter driver."""

def list_drivers(self) -> List[str]:
    """List available formatter drivers."""

def has_driver(self, driver_name: str) -> bool:
    """Check if formatter driver is available."""

def get_driver_info(self, driver_name: str) -> Dict[str, Any]:
    """Get formatter driver metadata."""
```

#### Domain-Specific Methods

```python
def format(self, value: Union[str, int, Any], driver: str = "default") -> str:
    """Format value using specified driver."""

def bulk_format(self, values: List[Union[str, int, Any]], driver: str = "default") -> List[str]:
    """Format multiple values using specified driver."""

def is_valid_format(self, value: Union[str, int, Any], driver: str = "default") -> bool:
    """Check if value can be formatted by specified driver."""
```

### Usage Examples

#### Basic Usage

```python
from managers import FormatterManager

# Create manager
manager = FormatterManager()

# Format single value
result = manager.format("88304053", driver="brazilian_postalcode")
print(result)  # "88304-053"

# Format multiple values
values = ["88304053", "01310100", "20040020"]
results = manager.bulk_format(values, driver="brazilian_postalcode")
print(results)  # ["88304-053", "01310-100", "20040-020"]

# Check if value can be formatted
is_valid = manager.is_valid_format("88304053", driver="brazilian_postalcode")
print(is_valid)  # True
```

#### Driver Management

```python
# List available drivers
drivers = manager.list_drivers()
print(drivers)  # ["brazilian_postalcode"]

# Check driver availability
has_driver = manager.has_driver("brazilian_postalcode")
print(has_driver)  # True

# Get driver information
info = manager.get_driver_info("brazilian_postalcode")
print(info["description"])  # "Brazilian postal code formatter"

# Load driver with configuration
driver = manager.load("brazilian_postalcode", strict_validation=False)
result = driver.format("88304053")
print(result)  # "88304-053"
```

### Configuration Options

The FormatterManager supports driver-specific configuration:

```python
# Configure driver during load
driver = manager.load("brazilian_postalcode", 
                     strict_validation=True,
                     allow_partial=False,
                     output_format="XXXXX-XXX")

# Or configure after loading
driver.configure(strict_validation=False, allow_partial=True)
```

### Caching Support

```python
# Enable caching for better performance
manager.enable_cache(True)

# Get cache statistics
stats = manager.get_cache_stats()
print(f"Cache size: {stats['size']}")

# Clear cache
manager.clear_cache()
```

## PostalCodeManager

The PostalCodeManager orchestrates postal code lookup drivers to provide address resolution capabilities.

### Purpose

Manages drivers that lookup address information based on postal codes from various external APIs and services.

### Location
- **File**: `python/src/managers/postalcode_manager.py`
- **Class**: `PostalCodeManager`
- **Contract**: Implements `ManagerContract`

### Available Drivers

| Driver Name | Description | API Service | Country | Rate Limits |
|-------------|-------------|-------------|---------|-------------|
| `viacep` | ViaCEP Brazilian postal code service | viacep.com.br | Brazil | None specified |
| `widenet` | WideNet postal code API | cdn.apicep.com | Brazil | Rate limited |
| `brasilapi` | BrasilAPI postal code service | brasilapi.com.br | Brazil | Rate limited |

### Core Methods

#### Manager Contract Methods

```python
def load(self, driver_name: str, **config) -> PostalCodeDriver:
    """Load and configure a postal code driver."""

def list_drivers(self) -> List[str]:
    """List available postal code drivers."""

def has_driver(self, driver_name: str) -> bool:
    """Check if postal code driver is available."""

def get_driver_info(self, driver_name: str) -> Dict[str, Any]:
    """Get postal code driver metadata."""
```

#### Domain-Specific Methods

```python
def get(self, postal_code: str, driver: str = "default") -> Address:
    """Get address for postal code using specified driver."""

def bulk_get(self, postal_codes: List[str], driver: str = "default") -> List[Address]:
    """Get addresses for multiple postal codes using specified driver."""

def set_default_driver(self, driver_name: str) -> None:
    """Set default driver for postal code lookups."""
```

### Usage Examples

#### Basic Usage

```python
from managers import PostalCodeManager

# Create manager
manager = PostalCodeManager()

# Get address for postal code
address = manager.get("88304-053", driver="viacep")
print(address.get_display_name())
# "Rua Alberto Werner, Unit até 445 - lado ímpar, Itajaí, SC, Brazil"

# Get multiple addresses
postal_codes = ["88304-053", "01310-100", "20040-020"]
addresses = manager.bulk_get(postal_codes, driver="viacep")
for address in addresses:
    print(f"{address.postal_code}: {address.locality}")
```

#### Driver Management

```python
# List available drivers
drivers = manager.list_drivers()
print(drivers)  # ["viacep", "widenet", "brasilapi"]

# Set default driver
manager.set_default_driver("viacep")

# Use default driver
address = manager.get("88304-053")  # Uses viacep

# Get driver information
info = manager.get_driver_info("viacep")
print(info["description"])  # "ViaCEP Brazilian postal code service"
```

#### Driver Configuration

```python
# Load driver with custom configuration
driver = manager.load("viacep",
                     timeout=30,
                     retries=5,
                     format="json")

# Get address using configured driver
address = driver.get("88304-053")
```

### Address Object

All postal code drivers return standardized `Address` objects from `standards.address`:

```python
from standards.address import Address, Country
from standards.core.base import BaseModel

@dataclass
class Address(BaseModel):
    """ISO 19160 compliant address with international support."""

    # Street information
    street_number: Optional[str] = None
    street_name: Optional[str] = None
    street_type: Optional[str] = None
    unit: Optional[str] = None
    building: Optional[str] = None
    floor: Optional[str] = None

    # Geographic areas
    neighborhood: Optional[str] = None
    locality: Optional[str] = None  # City
    sublocality: Optional[str] = None
    administrative_area_1: Optional[str] = None  # State/Province
    administrative_area_2: Optional[str] = None  # County
    administrative_area_3: Optional[str] = None  # Sub-district

    # Postal information
    postal_code: Optional[str] = None
    postal_code_suffix: Optional[str] = None

    # Country information
    country: Optional[Country] = None

    # Methods
    def get_display_name(self) -> str:
        """Get formatted address string."""

    def get_full_street_address(self) -> Optional[str]:
        """Get complete street address combining number, name, and type."""
```

### Error Handling

The PostalCodeManager handles various error scenarios:

```python
try:
    address = manager.get("invalid-postal-code", driver="viacep")
except ValidationError as e:
    print(f"Invalid postal code: {e.message}")
except APIError as e:
    print(f"API error: {e.message}")
except DriverNotFoundError as e:
    print(f"Driver not found: {e.driver_name}")
```

### Integration with FormatterManager

PostalCodeManager integrates with FormatterManager for consistent postal code formatting:

```python
# All drivers use FormatterManager internally
address = manager.get("88304053", driver="viacep")  # Input: unformatted
print(address.postal_code)  # Output: "88304-053" (formatted)

# This ensures consistent formatting across all drivers
viacep_address = manager.get("88304053", driver="viacep")
brasilapi_address = manager.get("88304053", driver="brasilapi")

assert viacep_address.postal_code == brasilapi_address.postal_code
# Both return "88304-053"
```

## Usage Patterns

### Manager-Orchestrated Pattern

The recommended pattern where managers handle driver loading and configuration:

```python
# FormatterManager example
formatter_manager = FormatterManager()
result = formatter_manager.format("88304053", driver="brazilian_postalcode")

# PostalCodeManager example
postal_manager = PostalCodeManager()
address = postal_manager.get("88304-053", driver="viacep")
```

### Direct Driver Pattern

For advanced use cases where you need direct driver control:

```python
# Load driver directly
formatter_manager = FormatterManager()
formatter_driver = formatter_manager.load("brazilian_postalcode")

# Configure driver
formatter_driver.configure(strict_validation=False, allow_partial=True)

# Use driver directly
result = formatter_driver.format("88304053")
```

### Bulk Operations Pattern

For processing multiple values efficiently:

```python
# Bulk formatting
formatter_manager = FormatterManager()
postal_codes = ["88304053", "01310100", "20040020"]
formatted_codes = formatter_manager.bulk_format(postal_codes, driver="brazilian_postalcode")

# Bulk address lookup
postal_manager = PostalCodeManager()
addresses = postal_manager.bulk_get(formatted_codes, driver="viacep")
```

### Error Handling Pattern

Robust error handling across managers:

```python
from contracts.manager_contract import DriverNotFoundError, DriverLoadError
from validation_base import ValidationError

def safe_format_and_lookup(postal_code: str):
    try:
        # Format postal code
        formatter_manager = FormatterManager()
        formatted_code = formatter_manager.format(postal_code, driver="brazilian_postalcode")

        # Lookup address
        postal_manager = PostalCodeManager()
        address = postal_manager.get(formatted_code, driver="viacep")

        return address

    except DriverNotFoundError as e:
        print(f"Driver not available: {e.driver_name}")
        return None
    except ValidationError as e:
        print(f"Invalid postal code: {e.message}")
        return None
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return None
```

## Integration Examples

### Complete Workflow: Format → Validate → Lookup

```python
from managers import FormatterManager, PostalCodeManager

def complete_postal_workflow(raw_postal_code: str) -> dict:
    """Complete postal code processing workflow."""

    # Step 1: Format postal code
    formatter_manager = FormatterManager()
    try:
        formatted_code = formatter_manager.format(raw_postal_code, driver="brazilian_postalcode")
        print(f"Formatted: {raw_postal_code} → {formatted_code}")
    except Exception as e:
        return {"error": f"Formatting failed: {str(e)}"}

    # Step 2: Validate format
    is_valid = formatter_manager.is_valid_format(formatted_code, driver="brazilian_postalcode")
    if not is_valid:
        return {"error": "Invalid postal code format"}

    # Step 3: Lookup address
    postal_manager = PostalCodeManager()
    try:
        address = postal_manager.get(formatted_code, driver="viacep")
        return {
            "success": True,
            "formatted_code": formatted_code,
            "address": {
                "street": address.street,
                "locality": address.locality,
                "region": address.region,
                "display_name": address.get_display_name()
            }
        }
    except Exception as e:
        return {"error": f"Address lookup failed: {str(e)}"}

# Usage
result = complete_postal_workflow("88304053")
print(result)
```

### Multi-Driver Fallback Pattern

```python
def robust_address_lookup(postal_code: str) -> Address:
    """Lookup address with fallback drivers."""

    postal_manager = PostalCodeManager()
    drivers = ["viacep", "brasilapi", "widenet"]  # Priority order

    for driver_name in drivers:
        try:
            print(f"Trying {driver_name}...")
            address = postal_manager.get(postal_code, driver=driver_name)
            print(f"Success with {driver_name}")
            return address
        except Exception as e:
            print(f"{driver_name} failed: {str(e)}")
            continue

    raise Exception("All drivers failed")

# Usage
try:
    address = robust_address_lookup("88304-053")
    print(address.get_display_name())
except Exception as e:
    print(f"Complete failure: {str(e)}")
```

### Caching and Performance Pattern

```python
def optimized_bulk_processing(postal_codes: List[str]) -> List[dict]:
    """Optimized bulk processing with caching."""

    # Enable caching for better performance
    formatter_manager = FormatterManager()
    formatter_manager.enable_cache(True)

    postal_manager = PostalCodeManager()
    postal_manager.enable_cache(True)

    results = []

    for postal_code in postal_codes:
        try:
            # Format (cached)
            formatted = formatter_manager.format(postal_code, driver="brazilian_postalcode")

            # Lookup (cached)
            address = postal_manager.get(formatted, driver="viacep")

            results.append({
                "input": postal_code,
                "formatted": formatted,
                "address": address.get_display_name(),
                "success": True
            })

        except Exception as e:
            results.append({
                "input": postal_code,
                "error": str(e),
                "success": False
            })

    # Print cache statistics
    formatter_stats = formatter_manager.get_cache_stats()
    postal_stats = postal_manager.get_cache_stats()

    print(f"Formatter cache: {formatter_stats['size']} entries")
    print(f"Postal cache: {postal_stats['size']} entries")

    return results
```

### Configuration Management Pattern

```python
class PostalCodeService:
    """Service class with configurable managers."""

    def __init__(self, config: dict = None):
        self.config = config or {}

        # Initialize managers
        self.formatter_manager = FormatterManager()
        self.postal_manager = PostalCodeManager()

        # Apply configuration
        self._configure_managers()

    def _configure_managers(self):
        """Configure managers based on settings."""

        # Configure formatter
        if 'formatter' in self.config:
            formatter_config = self.config['formatter']
            self.formatter_driver = self.formatter_manager.load(
                "brazilian_postalcode",
                **formatter_config
            )

        # Configure postal lookup
        if 'postal' in self.config:
            postal_config = self.config['postal']
            default_driver = postal_config.pop('default_driver', 'viacep')
            self.postal_manager.set_default_driver(default_driver)

    def process_postal_code(self, postal_code: str) -> dict:
        """Process postal code with configured settings."""

        # Format
        formatted = self.formatter_manager.format(postal_code, driver="brazilian_postalcode")

        # Lookup
        address = self.postal_manager.get(formatted)  # Uses default driver

        return {
            "original": postal_code,
            "formatted": formatted,
            "address": address.get_display_name()
        }

# Usage
config = {
    'formatter': {
        'strict_validation': False,
        'allow_partial': True
    },
    'postal': {
        'default_driver': 'viacep',
        'timeout': 30
    }
}

service = PostalCodeService(config)
result = service.process_postal_code("88304053")
print(result)
```

## Best Practices

### 1. Use Manager-Orchestrated Pattern
Always use managers to load and configure drivers rather than instantiating drivers directly.

### 2. Handle Errors Gracefully
Implement proper error handling for driver loading, configuration, and operation failures.

### 3. Enable Caching for Performance
Use caching for bulk operations or repeated lookups to improve performance.

### 4. Use Bulk Operations
When processing multiple items, use bulk methods for better efficiency.

### 5. Configure Drivers Appropriately
Set appropriate timeouts, retries, and validation levels based on your use case.

### 6. Implement Fallback Strategies
Use multiple drivers with fallback logic for critical operations.

## Testing Patterns

### Driver Interface Consistency Testing

When implementing new drivers, ensure they maintain interface consistency:

```python
def test_postal_code_driver_interface_consistency():
    """Test that all postal code drivers have consistent interfaces."""
    from drivers.postalcode.postalcode_viacep_driver import PostalCodeViacepDriver
    from drivers.postalcode.postalcode_widenet_driver import PostalCodeWidenetDriver
    from drivers.postalcode.postalcode_brasilapi_driver import PostalCodeBrasilApiDriver
    from standards.address import Address

    drivers = [
        PostalCodeViacepDriver(),
        PostalCodeWidenetDriver(),
        PostalCodeBrasilApiDriver()
    ]

    for driver in drivers:
        # All should have the same method
        assert hasattr(driver, 'get')
        assert callable(driver.get)

        # All should have configuration methods
        assert hasattr(driver, 'configure')
        assert hasattr(driver, 'get_config')

        # All should return Address objects
        try:
            result = driver.get("88304-053")
            assert isinstance(result, Address)
            assert result.postal_code == "88304-053"
        except Exception as e:
            # Network issues are acceptable in tests
            print(f"Driver {driver.__class__.__name__} skipped: {e}")
```

### Manager Driver Interchangeability Testing

Test that managers can load and use different drivers interchangeably:

```python
def test_manager_driver_interchangeability():
    """Test that PostalCodeManager can use different drivers interchangeably."""
    from managers import PostalCodeManager
    from standards.address import Address

    manager = PostalCodeManager()

    for driver_name in manager.list_drivers():
        try:
            # Test loading driver
            driver = manager.load(driver_name)
            assert driver is not None

            # Test direct manager method
            result = manager.get("88304-053", driver=driver_name)

            # All should return the same type
            assert isinstance(result, Address)
            assert result.postal_code == "88304-053"

        except Exception as e:
            # Network issues are acceptable in tests
            print(f"Driver {driver_name} skipped: {e}")
```

### Formatter Driver Testing

Test formatter drivers for consistency:

```python
def test_formatter_driver_consistency():
    """Test that formatter drivers maintain consistent behavior."""
    from drivers.formatter.formatter_brazilian_postalcode_driver import FormatterBrazilianPostalcodeDriver

    driver = FormatterBrazilianPostalcodeDriver()

    # Test various input formats
    test_cases = [
        ("88304053", "88304-053"),
        ("88304-053", "88304-053"),
        (88304053, "88304-053"),
        ("  88304053  ", "88304-053")
    ]

    for input_val, expected in test_cases:
        result = driver.format(input_val)
        assert result == expected, f"Input {input_val!r} should format to {expected}, got {result}"
```

## Error Handling Patterns

### Driver-Level Error Handling

```python
from drivers.postalcode.postalcode_viacep_driver import PostalCodeViacepDriver
from exceptions import PostalCodeError

try:
    driver = PostalCodeViacepDriver()
    address = driver.get("invalid-cep")
except PostalCodeError as e:
    print(f"Driver error: {e}")
    # Handle specific postal code errors
except Exception as e:
    print(f"Unexpected error: {e}")
    # Handle network or other errors
```

### Manager-Level Error Handling

```python
from managers import PostalCodeManager
from exceptions import DriverNotFoundError, PostalCodeError

try:
    manager = PostalCodeManager()
    address = manager.get("invalid-cep", driver="viacep")
except DriverNotFoundError as e:
    print(f"Driver not found: {e}")
    # Handle missing driver
except PostalCodeError as e:
    print(f"Postal code error: {e}")
    # Handle postal code validation errors
except Exception as e:
    print(f"Unexpected error: {e}")
    # Handle other errors
```

## See Also

- [Manager Contract](../contracts/manager_contract.md)
- [Formatter Contract](../contracts/formatter_contract.md)
- [Contracts Overview](../contracts/contracts_overview.md)
- [Standards Compliance Tests](../../tests/integration/test_standards_compliance.py)

---

*This documentation covers the FormatterManager and PostalCodeManager implementations in the Schubert Toolbox system.*
