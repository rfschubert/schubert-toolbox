# Formatter Contract

The Formatter Contract defines the standard interface for all data formatting drivers in the Schubert Toolbox system.

## Overview

Formatters are responsible for transforming input data into standardized output formats. They ensure consistent data presentation across the entire system while supporting various input types and configuration options.

## Contract Definition

### Core Interface

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, Union

class FormatterContract(ABC):
    """Abstract base class defining the contract for formatter drivers."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get the display name of the formatter."""
        pass
    
    @abstractmethod
    def format(self, value: Union[str, int, Any]) -> str:
        """
        Format the input value according to the formatter's rules.
        
        Args:
            value: Value to be formatted
            
        Returns:
            Formatted string value
            
        Raises:
            FormatterValidationError: If value cannot be formatted
        """
        pass
    
    @abstractmethod
    def configure(self, **kwargs) -> 'FormatterContract':
        """
        Configure the formatter with options.
        
        Args:
            **kwargs: Configuration options specific to the formatter
            
        Returns:
            Self for method chaining
        """
        pass
    
    @abstractmethod
    def get_config(self) -> Dict[str, Any]:
        """
        Get current formatter configuration.
        
        Returns:
            Dictionary containing current configuration options
        """
        pass
```

### Optional Methods with Default Implementation

```python
def reset_config(self) -> 'FormatterContract':
    """Reset configuration to defaults."""
    return self

def is_valid_format(self, value: Union[str, int, Any]) -> bool:
    """Check if value can be formatted by this formatter."""
    try:
        self.format(value)
        return True
    except Exception:
        return False

def get_supported_types(self) -> list:
    """Get list of supported input types."""
    return [str, int]

def get_output_format(self) -> str:
    """Get description of the output format."""
    return "Formatted string"
```

## Abstract Base Implementation

The system provides `AbstractFormatterContract` for easier implementation:

```python
class AbstractFormatterContract(FormatterContract):
    """Abstract base class with common formatter functionality."""
    
    def __init__(self):
        self._default_config: Dict[str, Any] = {}
        self._config: Dict[str, Any] = {}
    
    def configure(self, **kwargs) -> 'AbstractFormatterContract':
        for key, value in kwargs.items():
            if key in self._default_config:
                self._config[key] = value
        return self
    
    def get_config(self) -> Dict[str, Any]:
        return self._config.copy()
    
    def reset_config(self) -> 'AbstractFormatterContract':
        self._config = self._default_config.copy()
        return self
    
    def _set_default_config(self, config: Dict[str, Any]) -> None:
        """Set default configuration for the formatter."""
        self._default_config = config.copy()
        self._config = config.copy()
```

## Exception Handling

Formatters use specific exception types for error handling:

```python
class FormatterError(Exception):
    """Base exception for formatter errors."""
    def __init__(self, message: str, error_code: str = None):
        super().__init__(message)
        self.error_code = error_code

class FormatterValidationError(FormatterError):
    """Exception raised when input value cannot be formatted."""
    pass

class FormatterConfigurationError(FormatterError):
    """Exception raised when formatter configuration is invalid."""
    pass
```

## Implementation Example

Here's a complete example of implementing a formatter driver:

```python
class FormatterBrazilianPostalcodeDriver(AbstractFormatterContract):
    """Brazilian postal code formatter driver."""

    def __init__(self):
        super().__init__()
        self._set_default_config({
            'strict_validation': True,
            'allow_partial': False,
            'output_format': 'XXXXX-XXX'
        })

    @property
    def name(self) -> str:
        return "Brazilian Postal Code"

    def format(self, value: Union[str, int, Any]) -> str:
        """Format Brazilian postal code to XXXXX-XXX format."""
        if value is None:
            raise FormatterValidationError(
                "Postal code value is required",
                error_code="FORMATTER_VALUE_REQUIRED"
            )

        # Clean input
        clean_value = self._clean_postal_code(value)

        # Validate if strict validation is enabled
        if self._config['strict_validation']:
            self._validate_postal_code(clean_value)

        # Format to XXXXX-XXX
        return self._apply_format(clean_value)

    def _clean_postal_code(self, value: Union[str, int]) -> str:
        """Clean postal code removing non-numeric characters."""
        str_value = str(value).strip()
        clean = re.sub(r'[^0-9]', '', str_value)

        if not clean:
            raise FormatterValidationError(
                "Postal code must contain numeric digits",
                error_code="FORMATTER_NO_DIGITS"
            )

        return clean

    def _validate_postal_code(self, postal_code: str) -> None:
        """Validate Brazilian postal code format."""
        if len(postal_code) != 8:
            raise FormatterValidationError(
                f"Brazilian postal code must have 8 digits, got {len(postal_code)}",
                error_code="FORMATTER_INVALID_LENGTH"
            )

    def _apply_format(self, postal_code: str) -> str:
        """Apply formatting to clean postal code."""
        if len(postal_code) == 8:
            return f"{postal_code[:5]}-{postal_code[5:]}"
        return postal_code
```

## Usage Patterns

### Direct Usage

```python
# Create formatter instance
formatter = FormatterBrazilianPostalcodeDriver()

# Configure if needed
formatter.configure(strict_validation=False, allow_partial=True)

# Format values
result = formatter.format("88304053")  # Returns "88304-053"
result = formatter.format(88304053)    # Returns "88304-053"
result = formatter.format("88.304-053") # Returns "88304-053"

# Check if value can be formatted
is_valid = formatter.is_valid_format("88304053")  # Returns True
```

### Manager Usage

```python
# Use through FormatterManager
manager = FormatterManager()

# Format using specific driver
result = manager.format("88304053", driver="brazilian_postalcode")

# Bulk formatting
values = ["88304053", "01310100", "20040020"]
results = manager.bulk_format(values, driver="brazilian_postalcode")

# Check validity
is_valid = manager.is_valid_format("88304053", driver="brazilian_postalcode")
```

## Configuration Options

Formatters support flexible configuration through the `configure()` method:

```python
formatter.configure(
    strict_validation=True,    # Enable strict validation
    allow_partial=False,       # Allow partial values
    output_format='XXXXX-XXX', # Output format pattern
    custom_option='value'      # Custom formatter-specific options
)

# Get current configuration
config = formatter.get_config()

# Reset to defaults
formatter.reset_config()
```

## Testing Contract Compliance

All formatter implementations should include contract compliance tests:

```python
def test_formatter_implements_contract(self):
    """Test that formatter implements FormatterContract."""
    formatter = MyFormatterDriver()

    # Test contract compliance
    self.assertIsInstance(formatter, FormatterContract)

    # Test required methods
    required_methods = ['format', 'configure', 'get_config', 'name']
    for method_name in required_methods:
        self.assertTrue(hasattr(formatter, method_name))
        self.assertTrue(callable(getattr(formatter, method_name)))

    # Test core functionality
    result = formatter.format("test_value")
    self.assertIsInstance(result, str)

    # Test configuration
    formatter.configure(test_option=True)
    config = formatter.get_config()
    self.assertIsInstance(config, dict)
```

## Best Practices

1. **Always inherit from AbstractFormatterContract** for common functionality
2. **Use specific exception types** (FormatterValidationError, etc.)
3. **Support method chaining** by returning self from configure()
4. **Validate input thoroughly** before formatting
5. **Document configuration options** in docstrings
6. **Handle edge cases gracefully** (None, empty strings, etc.)
7. **Use type hints** for better IDE support
8. **Write comprehensive tests** including contract compliance
9. **Follow naming conventions** (FormatterXxxDriver)
10. **Keep formatting logic focused** and single-purpose

## Integration with Managers

Formatters are designed to work seamlessly with FormatterManager:

```python
# Manager automatically registers compliant formatters
manager = FormatterManager()

# All registered formatters implement FormatterContract
for driver_name in manager.list_drivers():
    driver = manager.load(driver_name)
    assert isinstance(driver, FormatterContract)
```

## See Also

- [Manager Contract](manager_contract.md)
- [Validator Contract](validator_contract.md)
- [Contracts Overview](contracts_overview.md)
- [Manager Pattern Details](../patterns/manager_pattern_details.md)

---

*This contract ensures consistency and interoperability across all formatter implementations in the Schubert Toolbox system.*
