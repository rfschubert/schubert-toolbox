# Contracts Documentation

This directory contains comprehensive documentation for all contracts used in the Schubert Toolbox system.

## Overview

Contracts define the interfaces that all components must implement to ensure consistency, maintainability, and extensibility across the system. They serve as the foundation for the plugin architecture and enable seamless integration between different components.

## Available Contracts

### [Contracts Overview](contracts_overview.md)
Comprehensive overview of all contracts, their philosophy, and benefits.

### [Manager Contract](manager_contract.md)
Defines the interface for manager classes that orchestrate drivers.

**Key Features:**
- Driver loading and configuration
- Driver discovery and registration
- Unified API across different domains
- Error handling and metadata management

**Implementations:**

- `FormatterManager`
- `PostalCodeManager`

### [Formatter Contract](formatter_contract.md)
Defines the interface for data formatting drivers.

**Key Features:**
- Standardized `format()` method
- Flexible configuration system
- Input validation and error handling
- Support for multiple input types

**Implementations:**
- `FormatterBrazilianPostalcodeDriver`



## Contract Benefits

### **Consistency**
All implementations follow the same patterns and interfaces, making the system predictable and easy to use.

### **Interoperability**
Components can work together seamlessly, enabling complex workflows and integrations.

### **Extensibility**
New implementations can be added without breaking existing code, supporting a plugin architecture.

### **Maintainability**
Clear interface specifications reduce coupling and make the system easier to maintain and debug.

### **Testability**
Standardized interfaces enable comprehensive testing and contract compliance verification.

## Implementation Guidelines

### For Managers
1. Inherit from `AbstractManagerContract`
2. Implement required methods (`load`, `list_drivers`, etc.)
3. Register default drivers in constructor
4. Provide domain-specific convenience methods
5. Handle errors gracefully with specific exception types

### For Formatters
1. Inherit from `AbstractFormatterContract`
2. Implement the core `format()` method
3. Set default configuration using `_set_default_config()`
4. Use `FormatterValidationError` for validation failures
5. Support method chaining in `configure()`

### For Validators
1. Inherit from the appropriate contract
2. Implement the core `validate()` method
3. Return comprehensive `ValidationResult` objects
4. Use specific error codes for different failure types
5. Include metadata for debugging and analysis

## Quick Start

### Using a Manager

```python
from managers import FormatterManager

# Create manager
manager = FormatterManager()

# Use manager methods
result = manager.format("88304053", driver="brazilian_postalcode")
print(result)  # "88304-053"
```

### Creating a New Formatter

```python
from contracts.formatter_contract import AbstractFormatterContract

class MyFormatterDriver(AbstractFormatterContract):
    @property
    def name(self) -> str:
        return "My Formatter"
    
    def format(self, value):
        return str(value).upper()
```



## Testing Contract Compliance

All implementations should include contract compliance tests:

```python
def test_implements_contract(self):
    """Test that implementation follows contract."""
    instance = MyImplementation()
    
    # Test contract compliance
    self.assertIsInstance(instance, ExpectedContract)
    
    # Test required methods exist
    required_methods = ['method1', 'method2']
    for method_name in required_methods:
        self.assertTrue(hasattr(instance, method_name))
        self.assertTrue(callable(getattr(instance, method_name)))
```

## Best Practices

1. **Always use contracts** when implementing new components
2. **Follow naming conventions** consistently
3. **Include comprehensive docstrings** for all methods
4. **Handle errors gracefully** with appropriate exception types
5. **Write contract compliance tests** for all implementations
6. **Use type hints** for better IDE support and documentation
7. **Document configuration options** clearly
8. **Provide meaningful error messages** for end users

## Architecture Integration

Contracts are integral to the Schubert Toolbox architecture:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Managers      │    │   Formatters    │    │ Postal Drivers  │
│                 │    │                 │    │                 │
│ ManagerContract │    │FormatterContract│    │ Address Lookup  │
│                 │    │                 │    │                 │
│ - load()        │    │ - format()      │    │ - get()         │
│ - list_drivers()│    │ - configure()   │    │ - configure()   │
│ - has_driver()  │    │ - get_config()  │    │ - get_config()  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## See Also

- [Manager Pattern Details](../patterns/manager_pattern_details.md)
- [Default LLM Instructions](../llms/default_llms_instructions.md)
- [API Contracts](../api_contracts/)

---

*These contracts form the foundation of the Schubert Toolbox system, ensuring consistency, maintainability, and extensibility across all components.*
