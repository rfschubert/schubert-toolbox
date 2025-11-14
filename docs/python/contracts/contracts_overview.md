# Contracts Overview

This document provides a comprehensive overview of all contracts used in the Schubert Toolbox system to ensure consistency, maintainability, and extensibility across all components.

## Table of Contents

1. [Manager Contract](#manager-contract)
2. [Formatter Contract](#formatter-contract)
3. [Contract Benefits](#contract-benefits)
4. [Implementation Guidelines](#implementation-guidelines)

## Contract Philosophy

Contracts in the Schubert Toolbox serve as **interface specifications** that ensure:

- **Consistency**: All implementations follow the same patterns
- **Interoperability**: Components can work together seamlessly
- **Extensibility**: New implementations can be added without breaking existing code
- **Maintainability**: Clear expectations for all developers
- **Testability**: Standardized interfaces enable comprehensive testing

## Manager Contract

The Manager Contract defines the interface for all manager classes that orchestrate drivers.

### Purpose
Managers provide a unified interface for loading, configuring, and using drivers of a specific type (formatters, postal code lookups, etc.).

### Key Interface Methods

```python
class ManagerContract(ABC):
    @abstractmethod
    def load(self, driver_name: str, **config) -> Any:
        """Load and configure a driver"""
        
    @abstractmethod
    def list_drivers(self) -> List[str]:
        """List available drivers"""
        
    @abstractmethod
    def has_driver(self, driver_name: str) -> bool:
        """Check if driver is available"""
        
    @abstractmethod
    def get_driver_info(self, driver_name: str) -> Dict[str, Any]:
        """Get driver metadata"""
        
    @abstractmethod
    def register_driver(self, name: str, driver_class: type, **metadata) -> None:
        """Register a new driver"""
```

### Implementation Classes
- `PostalCodeManager`: Manages postal code lookup drivers
- `FormatterManager`: Manages data formatting drivers

### Usage Pattern

```python
# Manager-orchestrated usage
manager = PostalCodeManager()
driver = manager.load("viacep")
result = driver.get("88304-053")

# Direct manager method
result = manager.get("88304-053", driver="viacep")
```

## Formatter Contract

The Formatter Contract ensures all formatter drivers provide consistent data formatting capabilities.

### Purpose
Formatters transform input data into standardized output formats (e.g., postal codes, phone numbers, currencies).

### Key Interface Methods

```python
class FormatterContract(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Get formatter display name"""
        
    @abstractmethod
    def format(self, value: Union[str, int, Any]) -> str:
        """Format input value - CORE METHOD"""
        
    @abstractmethod
    def configure(self, **kwargs) -> 'FormatterContract':
        """Configure formatter options"""
        
    @abstractmethod
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
```

### Optional Methods with Default Implementation

```python
def reset_config(self) -> 'FormatterContract':
    """Reset to default configuration"""
    
def is_valid_format(self, value: Union[str, int, Any]) -> bool:
    """Check if value can be formatted"""
    
def get_supported_types(self) -> list:
    """Get supported input types"""
    
def get_output_format(self) -> str:
    """Get output format description"""
```

### Implementation Classes
- `FormatterBrazilianPostalcodeDriver`: Formats Brazilian postal codes (CEP)

### Usage Pattern

```python
# Direct usage
formatter = FormatterBrazilianPostalcodeDriver()
result = formatter.format("88304053")  # Returns "88304-053"

# Manager usage
manager = FormatterManager()
result = manager.format("88304053", driver="brazilian_postalcode")
```



## Contract Benefits

### 1. **Consistency Across Components**
- All managers implement the same interface
- All formatters have the same core methods
- All postal code drivers return standardized Address objects
- Predictable behavior for developers

### 2. **Interoperability**
- Components can be swapped without code changes
- Managers can work with any compliant driver
- Easy integration between different subsystems

### 3. **Extensibility**
- New drivers can be added by implementing contracts
- Existing code continues to work with new implementations
- Framework-agnostic design allows multiple backends

### 4. **Maintainability**
- Clear interface specifications
- Reduced coupling between components
- Easier to test and debug
- Self-documenting code structure

### 5. **Error Handling**
- Standardized exception types
- Consistent error reporting
- Predictable failure modes

## Implementation Guidelines

### Creating a New Manager

1. **Inherit from AbstractManagerContract**
```python
class MyManager(AbstractManagerContract):
    def __init__(self):
        super().__init__()
        self._register_default_drivers()
```

2. **Implement Required Methods**
```python
def load(self, driver_name: str, **config) -> Any:
    # Load and configure driver

def _register_default_drivers(self) -> None:
    # Register available drivers
```

3. **Add Domain-Specific Methods**
```python
def my_domain_method(self, data, driver="default"):
    # Domain-specific functionality
```

### Creating a New Formatter Driver

1. **Inherit from AbstractFormatterContract**
```python
class MyFormatterDriver(AbstractFormatterContract):
    @property
    def name(self) -> str:
        return "My Formatter"
```

2. **Implement Core Format Method**
```python
def format(self, value: Union[str, int, Any]) -> str:
    # Core formatting logic
    return formatted_value
```

3. **Set Default Configuration**
```python
def __init__(self):
    super().__init__()
    self._set_default_config({
        'option1': 'default_value',
        'option2': True
    })
```



## Contract Compliance Testing

All implementations should include tests that verify contract compliance:

```python
def test_implements_contract(self):
    """Test that driver implements required contract."""
    driver = MyDriver()

    # Test contract compliance
    self.assertIsInstance(driver, ExpectedContract)

    # Test required methods exist
    required_methods = ['method1', 'method2', 'method3']
    for method_name in required_methods:
        self.assertTrue(hasattr(driver, method_name))
        self.assertTrue(callable(getattr(driver, method_name)))
```

## Best Practices

1. **Always implement contracts completely**
2. **Use type hints for better IDE support**
3. **Include comprehensive docstrings**
4. **Handle errors gracefully with standard exceptions**
5. **Write contract compliance tests**
6. **Follow naming conventions consistently**
7. **Document configuration options clearly**

## See Also


- [Default LLM Instructions](../llms/default_llms_instructions.md)
- [API Contracts](../api_contracts/)

---

*This documentation is part of the Schubert Toolbox project and follows the architectural principles defined in the system.*
