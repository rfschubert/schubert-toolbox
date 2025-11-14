# Formatter Drivers

This document provides detailed information about all formatter drivers available in the Schubert Toolbox system.

## Overview

Formatter drivers are responsible for transforming input data into standardized output formats. They implement the [FormatterContract](../contracts/formatter_contract.md) and can be used either directly or through the [FormatterManager](../managers/implemented_managers.md#formattermanager).

## Usage Patterns

### 1. Direct Driver Usage
Use drivers directly when you need fine-grained control over configuration and behavior.

```python
from drivers.formatter.formatter_brazilian_postalcode_driver import FormatterBrazilianPostalcodeDriver

# Create driver instance
driver = FormatterBrazilianPostalcodeDriver()

# Configure driver
driver.configure(strict_validation=False, allow_partial=True)

# Use driver
result = driver.format("88304053")
print(result)  # "88304-053"
```

### 2. Manager-Orchestrated Usage
Use the FormatterManager for simplified driver management and consistent API.

```python
from managers import FormatterManager

# Create manager
manager = FormatterManager()

# Use manager methods
result = manager.format("88304053", driver="brazilian_postalcode")
print(result)  # "88304-053"

# Load driver with configuration
driver = manager.load("brazilian_postalcode", strict_validation=False)
result = driver.format("88304053")
```

## Available Drivers

### Brazilian Postal Code Formatter

Formats Brazilian postal codes (CEP) to the standard XXXXX-XXX format.

#### Driver Information
- **Class**: `FormatterBrazilianPostalcodeDriver`
- **File**: `python/src/drivers/formatter/formatter_brazilian_postalcode_driver.py`
- **Manager Name**: `brazilian_postalcode`
- **Contract**: Implements `FormatterContract`

#### Input Types
- `str`: String postal codes with or without formatting
- `int`: Integer postal codes (will be zero-padded if needed)

#### Output Format
- **Standard**: `XXXXX-XXX` (e.g., "88304-053")
- **Always returns**: String with exactly 9 characters (8 digits + 1 dash)

#### Configuration Options

```python
driver.configure(
    strict_validation=True,    # Require exactly 8 digits
    allow_partial=False,       # Allow partial CEPs (5-7 digits)
    output_format='XXXXX-XXX'  # Output format pattern
)
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `strict_validation` | `bool` | `True` | Require exactly 8 digits |
| `allow_partial` | `bool` | `False` | Allow 5-7 digit CEPs |
| `output_format` | `str` | `'XXXXX-XXX'` | Output format pattern |

#### Usage Examples

##### Basic Usage

```python
from drivers.formatter.formatter_brazilian_postalcode_driver import FormatterBrazilianPostalcodeDriver

# Create driver
driver = FormatterBrazilianPostalcodeDriver()

# Format different input types
examples = [
    "88304053",      # String without formatting
    "88304-053",     # String with formatting
    "88.304-053",    # String with dots and dash
    "  88304053  ",  # String with spaces
    88304053,        # Integer
]

for example in examples:
    result = driver.format(example)
    print(f"{example!r} -> {result}")

# Output:
# '88304053' -> 88304-053
# '88304-053' -> 88304-053
# '88.304-053' -> 88304-053
# '  88304053  ' -> 88304-053
# 88304053 -> 88304-053
```

##### Configuration Examples

```python
# Strict validation (default)
driver = FormatterBrazilianPostalcodeDriver()
driver.configure(strict_validation=True)

try:
    result = driver.format("88304")  # Only 5 digits
except FormatterValidationError as e:
    print(f"Error: {e.message}")  # "Brazilian postal code must have 8 digits"

# Lenient validation
driver.configure(strict_validation=False, allow_partial=True)
result = driver.format("88304")  # Works with partial CEP
print(result)  # "88304-000" (padded)
```

##### Validation Methods

```python
# Check if value can be formatted
is_valid = driver.is_valid_format("88304053")
print(is_valid)  # True

is_valid = driver.is_valid_format("invalid")
print(is_valid)  # False

# Get supported types
types = driver.get_supported_types()
print(types)  # [<class 'str'>, <class 'int'>]

# Get output format description
format_desc = driver.get_output_format()
print(format_desc)  # "Formatted string"
```

#### Error Handling

The driver raises specific exceptions for different error conditions:

```python
from contracts.formatter_contract import FormatterValidationError

try:
    result = driver.format(None)
except FormatterValidationError as e:
    print(f"Error: {e.message}")
    print(f"Code: {e.error_code}")

# Common error codes:
# - FORMATTER_VALUE_REQUIRED: Value is None or empty
# - FORMATTER_NO_DIGITS: No numeric digits found
# - FORMATTER_INVALID_LENGTH: Wrong number of digits
# - FORMATTER_INVALID_FORMAT: Invalid format
```

## Advanced Usage Patterns

### Bulk Formatting with Direct Driver

```python
# Process multiple values efficiently
driver = FormatterBrazilianPostalcodeDriver()
postal_codes = ["88304053", "01310100", "20040020", "invalid", 12345678]

results = []
for code in postal_codes:
    try:
        formatted = driver.format(code)
        results.append({"input": code, "output": formatted, "success": True})
    except FormatterValidationError as e:
        results.append({"input": code, "error": e.message, "success": False})

for result in results:
    if result["success"]:
        print(f"SUCCESS {result['input']} -> {result['output']}")
    else:
        print(f"ERROR {result['input']} -> {result['error']}")
```

### Configuration Management

```python
# Save and restore configuration
driver = FormatterBrazilianPostalcodeDriver()

# Get default configuration
default_config = driver.get_config()
print("Default config:", default_config)

# Apply custom configuration
driver.configure(strict_validation=False, allow_partial=True)
custom_config = driver.get_config()
print("Custom config:", custom_config)

# Reset to defaults
driver.reset_config()
reset_config = driver.get_config()
print("Reset config:", reset_config)

# Verify reset worked
assert reset_config == default_config
```

### Method Chaining

```python
# Configure and use in a single chain
result = (FormatterBrazilianPostalcodeDriver()
          .configure(strict_validation=False, allow_partial=True)
          .format("88304"))

print(result)  # "88304-000"
```

### Integration with Validation

```python
def safe_format_postal_code(value, strict=True):
    """Safely format postal code with validation."""

    driver = FormatterBrazilianPostalcodeDriver()
    driver.configure(strict_validation=strict)

    # Pre-validation
    if not driver.is_valid_format(value):
        return {
            "success": False,
            "error": "Invalid format",
            "input": value
        }

    try:
        formatted = driver.format(value)
        return {
            "success": True,
            "input": value,
            "output": formatted,
            "config": driver.get_config()
        }
    except FormatterValidationError as e:
        return {
            "success": False,
            "error": e.message,
            "error_code": e.error_code,
            "input": value
        }

# Usage
result = safe_format_postal_code("88304053")
print(result)
```

## Manager vs Direct Usage Comparison

### When to Use Direct Driver Access

**Advantages:**
- **Fine-grained control**: Direct access to all driver methods
- **Performance**: No manager overhead
- **Configuration persistence**: Driver keeps configuration between calls
- **Method chaining**: Fluent interface support
- **Advanced features**: Access to driver-specific methods

**Use Cases:**
- High-performance bulk processing
- Complex configuration requirements
- Driver-specific functionality needed
- Long-running processes with persistent configuration

**Example:**
```python
# Direct usage for bulk processing
driver = FormatterBrazilianPostalcodeDriver()
driver.configure(strict_validation=False, allow_partial=True)

# Process thousands of records with same configuration
for batch in large_dataset:
    formatted_batch = [driver.format(code) for code in batch]
    process_batch(formatted_batch)
```

### When to Use Manager-Orchestrated Access

**Advantages:**
- **Simplicity**: Easy to use API
- **Consistency**: Same interface across all drivers
- **Driver discovery**: List and load drivers dynamically
- **Bulk operations**: Built-in bulk methods
- **Caching**: Automatic result caching
- **Error handling**: Standardized error management

**Use Cases:**
- Simple formatting tasks
- Dynamic driver selection
- Integration with other managers
- Applications requiring caching
- Standardized error handling

**Example:**
```python
# Manager usage for simple tasks
manager = FormatterManager()

# Simple formatting
result = manager.format("88304053", driver="brazilian_postalcode")

# Bulk formatting with caching
manager.enable_cache(True)
results = manager.bulk_format(postal_codes, driver="brazilian_postalcode")

# Dynamic driver selection
available_drivers = manager.list_drivers()
for driver_name in available_drivers:
    if manager.is_valid_format("88304053", driver=driver_name):
        result = manager.format("88304053", driver=driver_name)
        break
```

## Performance Considerations

### Direct Driver Performance

```python
import time

# Direct driver - optimal for repeated use
driver = FormatterBrazilianPostalcodeDriver()
driver.configure(strict_validation=False)

start_time = time.time()
for i in range(10000):
    result = driver.format(f"8830405{i % 10}")
direct_time = time.time() - start_time

print(f"Direct driver: {direct_time:.3f}s for 10,000 operations")
```

### Manager Performance

```python
# Manager - good for varied usage
manager = FormatterManager()

start_time = time.time()
for i in range(10000):
    result = manager.format(f"8830405{i % 10}", driver="brazilian_postalcode")
manager_time = time.time() - start_time

print(f"Manager: {manager_time:.3f}s for 10,000 operations")
```

### Bulk Operations Performance

```python
# Bulk operations - most efficient for large datasets
postal_codes = [f"8830405{i % 10}" for i in range(10000)]

# Manager bulk operation
start_time = time.time()
results = manager.bulk_format(postal_codes, driver="brazilian_postalcode")
bulk_time = time.time() - start_time

print(f"Bulk operation: {bulk_time:.3f}s for 10,000 operations")
```

## Best Practices

### 1. Choose the Right Usage Pattern
- **Direct driver**: For performance-critical or configuration-heavy scenarios
- **Manager**: For simple tasks and consistent API usage

### 2. Handle Errors Appropriately
```python
# Always handle FormatterValidationError
try:
    result = driver.format(user_input)
except FormatterValidationError as e:
    logger.error(f"Formatting failed: {e.message} (code: {e.error_code})")
    return None
```

### 3. Configure Once, Use Many Times
```python
# Configure driver once for repeated use
driver = FormatterBrazilianPostalcodeDriver()
driver.configure(strict_validation=False, allow_partial=True)

# Use configured driver multiple times
results = [driver.format(code) for code in postal_codes]
```

### 4. Use Validation Before Formatting
```python
# Pre-validate to avoid exceptions
if driver.is_valid_format(user_input):
    result = driver.format(user_input)
else:
    handle_invalid_input(user_input)
```

### 5. Leverage Bulk Operations
```python
# Use bulk operations for better performance
manager = FormatterManager()
results = manager.bulk_format(large_dataset, driver="brazilian_postalcode")
```

## See Also

- [Formatter Contract](../contracts/formatter_contract.md) - Interface specification
- [FormatterManager](../managers/implemented_managers.md#formattermanager) - Manager documentation
- [Postal Code Drivers](postal_code_drivers.md) - Related postal code drivers
- [Contracts Overview](../contracts/contracts_overview.md) - System contracts

---

*This documentation covers all formatter drivers available in the Schubert Toolbox system.*
