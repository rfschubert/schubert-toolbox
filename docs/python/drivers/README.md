# Drivers Documentation

This directory contains comprehensive documentation for all driver implementations in the Schubert Toolbox system.

## Overview

Drivers are the core implementation components that perform specific tasks like data formatting, validation, and external API integration. They implement standardized contracts and can be used either directly or through managers.

## Available Documentation

### [Formatter Drivers](formatter_drivers.md)
Detailed documentation of data formatting drivers.

**Currently Available:**
- **Brazilian Postal Code Formatter**: Formats CEP to XXXXX-XXX standard

### [Postal Code Drivers](postal_code_drivers.md)
Detailed documentation of postal code lookup drivers.

**Currently Available:**
- **ViaCEP Driver**: Brazilian postal code service (viacep.com.br)
- **WideNet Driver**: WideNet postal code API (cdn.apicep.com)
- **BrasilAPI Driver**: BrasilAPI postal code service (brasilapi.com.br)

## Usage Patterns

### Direct Driver Usage
Use drivers directly when you need fine-grained control:

```python
# Direct formatter usage
from drivers.formatter.formatter_brazilian_postalcode_driver import FormatterBrazilianPostalcodeDriver

driver = FormatterBrazilianPostalcodeDriver()
driver.configure(strict_validation=False)
result = driver.format("88304053")  # "88304-053"

# Direct postal code usage
from drivers.postalcode.postalcode_viacep_driver import PostalCodeViacepDriver

driver = PostalCodeViacepDriver()
driver.configure(timeout=30, retries=5)
address = driver.get("88304-053")
```

### Manager-Orchestrated Usage
Use managers for simplified, consistent API:

```python
# Manager usage
from managers import FormatterManager, PostalCodeManager

# Formatter through manager
formatter = FormatterManager()
result = formatter.format("88304053", driver="brazilian_postalcode")

# Postal code through manager
postal = PostalCodeManager()
address = postal.get("88304-053", driver="viacep")
```

## Driver Types

### Formatter Drivers
**Purpose**: Transform input data into standardized output formats

**Characteristics:**
- Implement `FormatterContract`
- Support multiple input types (string, integer)
- Configurable validation and formatting rules
- Method chaining support
- Error handling with specific exception types

**Available Drivers:**
- `FormatterBrazilianPostalcodeDriver`: Brazilian postal code formatting

### Postal Code Drivers
**Purpose**: Lookup address information from external APIs

**Characteristics:**
- Return standardized `Address` objects
- Integrate with `FormatterManager` for consistent input formatting
- Support timeout and retry configuration
- Handle various API error conditions
- Follow DRY principle (no duplicate formatting code)

**Available Drivers:**
- `PostalCodeViacepDriver`: ViaCEP service integration
- `PostalCodeWidenetDriver`: WideNet API integration
- `PostalCodeBrasilApiDriver`: BrasilAPI service integration

## Quick Start Examples

### Formatter Driver

```python
from drivers.formatter.formatter_brazilian_postalcode_driver import FormatterBrazilianPostalcodeDriver

# Create and configure
driver = FormatterBrazilianPostalcodeDriver()
driver.configure(strict_validation=False, allow_partial=True)

# Format different inputs
examples = ["88304053", "88304-053", 88304053, "  88304053  "]
for example in examples:
    result = driver.format(example)
    print(f"{example!r} -> {result}")  # All output: "88304-053"
```

### Postal Code Driver

```python
from drivers.postalcode.postalcode_viacep_driver import PostalCodeViacepDriver

# Create and configure
driver = PostalCodeViacepDriver()
driver.configure(timeout=30, retries=3)

# Lookup address
address = driver.get("88304-053")
print(f"Address: {address.get_display_name()}")
print(f"Locality: {address.locality}")  # "Itajaí"
print(f"Region: {address.region}")      # "SC"
```

### Integration Example

```python
# Complete workflow using both driver types
from drivers.formatter.formatter_brazilian_postalcode_driver import FormatterBrazilianPostalcodeDriver
from drivers.postalcode.postalcode_viacep_driver import PostalCodeViacepDriver

# Step 1: Format postal code
formatter = FormatterBrazilianPostalcodeDriver()
formatted_code = formatter.format("88304053")  # "88304-053"

# Step 2: Lookup address
postal_driver = PostalCodeViacepDriver()
address = postal_driver.get(formatted_code)

print(f"Formatted: {formatted_code}")
print(f"Address: {address.get_display_name()}")
```

## Architecture Benefits

### **Consistency**
All drivers implement standardized contracts, ensuring predictable behavior and interfaces.

### **Interoperability**
Drivers can work together seamlessly. Postal code drivers automatically use formatter drivers for input standardization.

### **Extensibility**
New drivers can be added by implementing the appropriate contracts without breaking existing code.

### **Maintainability**
Clear separation of concerns and standardized interfaces reduce coupling and complexity.

### **Performance**
Direct driver access provides optimal performance for high-volume operations.

## When to Use Direct Drivers

### **Advantages**
- **Fine-grained control**: Access to all driver methods and configuration
- **Performance**: No manager overhead
- **Custom logic**: Implement specific error handling or fallback strategies
- **Advanced features**: Access to driver-specific functionality
- **Threading**: Better control over thread-local instances

### **Use Cases**
- High-performance bulk processing
- Custom error handling requirements
- Driver-specific feature needs
- Integration with existing threading/async code
- Complex configuration scenarios

### **Example Scenarios**
```python
# High-performance bulk processing
driver = FormatterBrazilianPostalcodeDriver()
driver.configure(strict_validation=False)

# Process thousands with same configuration
results = [driver.format(code) for code in large_dataset]

# Custom fallback logic
def custom_postal_lookup(code):
    for driver_class in [PostalCodeViacepDriver, PostalCodeBrasilApiDriver]:
        try:
            driver = driver_class()
            return driver.get(code)
        except Exception:
            continue
    raise Exception("All drivers failed")
```

## Best Practices

### 1. **Choose the Right Pattern**
- Use **direct drivers** for performance-critical or custom logic scenarios
- Use **managers** for simple tasks and consistent API usage

### 2. **Handle Errors Appropriately**
```python
from contracts.formatter_contract import FormatterValidationError

try:
    result = driver.format(user_input)
except FormatterValidationError as e:
    logger.error(f"Formatting failed: {e.message} (code: {e.error_code})")
```

### 3. **Configure Once, Use Many Times**
```python
# Configure driver once for repeated use
driver = FormatterBrazilianPostalcodeDriver()
driver.configure(strict_validation=False, allow_partial=True)

# Use configured driver multiple times
results = [driver.format(code) for code in postal_codes]
```

### 4. **Leverage Integration**
```python
# Postal code drivers automatically format input
postal_driver = PostalCodeViacepDriver()

# All these inputs work and return consistent results
address1 = postal_driver.get("88304053")      # Unformatted
address2 = postal_driver.get("88304-053")     # Formatted
address3 = postal_driver.get(88304053)        # Integer

# All return addresses with postal_code = "88304-053"
```

## See Also

- [Contracts](../contracts/) - Driver interface specifications
- [Managers](../managers/) - Manager implementations
- [Patterns](../patterns/) - Architectural patterns
- [Default LLM Instructions](../llms/default_llms_instructions.md) - Development guidelines

---

*This documentation provides comprehensive information about all driver implementations in the Schubert Toolbox system.*
