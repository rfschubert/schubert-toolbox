# Managers Documentation

This directory contains comprehensive documentation for all manager implementations in the Schubert Toolbox system.

## Overview

Managers are orchestrator classes that provide unified interfaces for loading, configuring, and using drivers of specific types. They abstract the complexity of driver management while ensuring consistent APIs across different domains.

All managers implement the [ManagerContract](../contracts/manager_contract.md) and follow established architectural patterns.

## Available Documentation

### [Implemented Managers](implemented_managers.md)
Detailed documentation of currently implemented managers.

**Currently Documented:**
- **FormatterManager**: Data formatting and transformation
- **PostalCodeManager**: Address lookup and resolution

## Manager Types

### FormatterManager
**Purpose**: Transform input data into standardized output formats

**Capabilities:**
- Format postal codes, phone numbers, currencies
- Support multiple input types (string, integer)
- Configurable validation and formatting rules
- Bulk formatting operations
- Caching for performance

**Available Drivers:**
- `brazilian_postalcode`: Brazilian postal code formatting (XXXXX-XXX)

### PostalCodeManager
**Purpose**: Lookup address information based on postal codes

**Capabilities:**
- Multiple API service integration
- Fallback driver support
- Bulk address lookups
- Consistent address object format
- Integration with FormatterManager

**Available Drivers:**
- `viacep`: ViaCEP Brazilian postal code service
- `widenet`: WideNet postal code API
- `brasilapi`: BrasilAPI postal code service

## Quick Start

### FormatterManager

```python
from managers import FormatterManager

# Create manager
manager = FormatterManager()

# Format postal code
result = manager.format("88304053", driver="brazilian_postalcode")
print(result)  # "88304-053"

# Bulk formatting
codes = ["88304053", "01310100", "20040020"]
results = manager.bulk_format(codes, driver="brazilian_postalcode")
```

### PostalCodeManager

```python
from managers import PostalCodeManager

# Create manager
manager = PostalCodeManager()

# Lookup address
address = manager.get("88304-053", driver="viacep")
print(address.get_display_name())

# Bulk lookup
codes = ["88304-053", "01310-100", "20040-020"]
addresses = manager.bulk_get(codes, driver="viacep")
```

## Integration Patterns

### Complete Workflow

```python
from managers import FormatterManager, PostalCodeManager

# Format postal code
formatter = FormatterManager()
formatted_code = formatter.format("88304053", driver="brazilian_postalcode")

# Lookup address
postal = PostalCodeManager()
address = postal.get(formatted_code, driver="viacep")

print(f"{formatted_code}: {address.locality}")
# "88304-053: Itajaí"
```

### Error Handling

```python
try:
    result = manager.format("invalid", driver="brazilian_postalcode")
except ValidationError as e:
    print(f"Validation failed: {e.message}")
except DriverNotFoundError as e:
    print(f"Driver not found: {e.driver_name}")
```

### Configuration

```python
# Load driver with configuration
driver = manager.load("brazilian_postalcode", 
                     strict_validation=False,
                     allow_partial=True)

# Use configured driver
result = driver.format("88304")
```

## Architecture Benefits

### **Consistency**
All managers provide the same interface patterns, making the system predictable and easy to use.

### **Interoperability**
Managers can work together seamlessly, enabling complex workflows and integrations.

### **Extensibility**
New drivers can be added without breaking existing code, supporting a plugin architecture.

### **Maintainability**
Clear separation of concerns and standardized interfaces reduce coupling and complexity.

### **Performance**
Built-in caching, bulk operations, and efficient driver management optimize performance.

## Best Practices

1. **Use Manager-Orchestrated Pattern**: Always use managers to load drivers
2. **Handle Errors Gracefully**: Implement proper error handling
3. **Enable Caching**: Use caching for bulk operations
4. **Use Bulk Operations**: Process multiple items efficiently
5. **Configure Appropriately**: Set timeouts and validation levels
6. **Implement Fallbacks**: Use multiple drivers for reliability

## Future Managers

The following managers are planned for future implementation:


- **PersonManager**: Person data management and operations
- **CurrencyManager**: Currency formatting and conversion
- **DateTimeManager**: Date and time formatting and parsing

## See Also

- [Manager Contract](../contracts/manager_contract.md)
- [Contracts Overview](../contracts/contracts_overview.md)
- [Implemented Managers](implemented_managers.md)
- [Default LLM Instructions](../llms/default_llms_instructions.md)

---

*This documentation provides comprehensive information about all manager implementations in the Schubert Toolbox system.*
