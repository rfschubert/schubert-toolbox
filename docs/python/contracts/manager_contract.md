# Manager Contract

The Manager Contract defines the standard interface for all manager classes that orchestrate drivers in the Schubert Toolbox system.

## Overview

Managers provide a unified interface for loading, configuring, and using drivers of a specific type. They act as orchestrators that abstract the complexity of driver management while providing consistent APIs across different domains (validation, formatting, postal code lookup, etc.).

## Contract Definition

### Core Interface

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List

class ManagerContract(ABC):
    """Abstract base class defining the contract for manager classes."""
    
    @abstractmethod
    def load(self, driver_name: str, **config) -> Any:
        """
        Load and configure a driver.
        
        Args:
            driver_name: Name of the driver to load
            **config: Configuration options for the driver
            
        Returns:
            Configured driver instance
            
        Raises:
            DriverNotFoundError: If driver is not available
            DriverLoadError: If driver fails to load
        """
        pass
    
    @abstractmethod
    def list_drivers(self) -> List[str]:
        """
        List all available drivers.
        
        Returns:
            List of driver names
        """
        pass
    
    @abstractmethod
    def has_driver(self, driver_name: str) -> bool:
        """
        Check if a driver is available.
        
        Args:
            driver_name: Name of the driver to check
            
        Returns:
            True if driver is available, False otherwise
        """
        pass
    
    @abstractmethod
    def get_driver_info(self, driver_name: str) -> Dict[str, Any]:
        """
        Get metadata about a driver.
        
        Args:
            driver_name: Name of the driver
            
        Returns:
            Dictionary containing driver metadata
            
        Raises:
            DriverNotFoundError: If driver is not found
        """
        pass
    
    @abstractmethod
    def register_driver(self, name: str, driver_class: type, **metadata) -> None:
        """
        Register a new driver.
        
        Args:
            name: Driver name for registration
            driver_class: Driver class to register
            **metadata: Additional driver metadata
        """
        pass
```

## Abstract Base Implementation

The system provides `AbstractManagerContract` for easier implementation:

```python
class AbstractManagerContract(ManagerContract):
    """Abstract base class with common manager functionality."""
    
    def __init__(self):
        self._drivers: Dict[str, Dict[str, Any]] = {}
    
    def list_drivers(self) -> List[str]:
        """List all registered drivers."""
        return list(self._drivers.keys())
    
    def has_driver(self, driver_name: str) -> bool:
        """Check if driver is registered."""
        return driver_name in self._drivers
    
    def get_driver_info(self, driver_name: str) -> Dict[str, Any]:
        """Get driver metadata."""
        if not self.has_driver(driver_name):
            raise DriverNotFoundError(driver_name, self.list_drivers())
        return self._drivers[driver_name].copy()
    
    def register_driver(self, name: str, driver_class: type, **metadata) -> None:
        """Register a driver with metadata."""
        self._drivers[name] = {
            "class": driver_class,
            "name": name,
            **metadata
        }
```

## Exception Handling

Managers use specific exception types for error handling:

```python
class ManagerError(Exception):
    """Base exception for manager errors."""
    pass

class DriverNotFoundError(ManagerError):
    """Exception raised when a requested driver is not found."""
    def __init__(self, driver_name: str, available_drivers: List[str]):
        self.driver_name = driver_name
        self.available_drivers = available_drivers
        super().__init__(
            f"Driver '{driver_name}' not found. Available: {available_drivers}"
        )

class DriverLoadError(ManagerError):
    """Exception raised when a driver fails to load."""
    def __init__(self, driver_name: str, error_message: str):
        self.driver_name = driver_name
        self.error_message = error_message
        super().__init__(f"Failed to load driver '{driver_name}': {error_message}")
```

## Implementation Example

Here's a complete example of implementing a manager:

```python
class PostalCodeManager(AbstractManagerContract):
    """Manager for postal code lookup drivers."""

    def __init__(self):
        super().__init__()
        self._default_driver: Optional[str] = None
        self._cache: Dict[str, Any] = {}
        self._cache_enabled: bool = False

        # Register default drivers
        self._register_default_drivers()

    def _register_default_drivers(self) -> None:
        """Register default postal code drivers."""
        try:
            from drivers.postalcode.postalcode_viacep_driver import PostalCodeViacepDriver
            self.register_driver(
                "viacep",
                PostalCodeViacepDriver,
                description="ViaCEP Brazilian postal code service",
                version="1.0.0",
                country="BR"
            )
        except ImportError as e:
            logger.warning("Failed to register ViaCEP driver: %s", e)

    def load(self, driver_name: str, **config) -> Any:
        """Load and configure a postal code driver."""
        if not self.has_driver(driver_name):
            raise DriverNotFoundError(driver_name, self.list_drivers())

        try:
            driver_info = self._drivers[driver_name]
            driver_class = driver_info["class"]

            # Instantiate driver
            driver_instance = driver_class()

            # Apply configuration if provided
            if config:
                driver_instance.configure(**config)

            return driver_instance

        except Exception as e:
            raise DriverLoadError(driver_name, str(e))

    # Domain-specific methods
    def get(self, postal_code: str, driver: str = "default") -> Address:
        """Get address for postal code using specified driver."""
        if driver == "default":
            driver = self._default_driver or self.list_drivers()[0]

        driver_instance = self.load(driver)
        return driver_instance.get(postal_code)

    def set_default_driver(self, driver_name: str) -> None:
        """Set default driver for postal code lookups."""
        if not self.has_driver(driver_name):
            raise DriverNotFoundError(driver_name, self.list_drivers())
        self._default_driver = driver_name
```

## Usage Patterns

### Manager-Orchestrated Usage

```python
# Create manager
manager = PostalCodeManager()

# Load specific driver
driver = manager.load("viacep")
result = driver.get("88304-053")

# Load with configuration
driver = manager.load("viacep", timeout=30, retries=5)
result = driver.get("88304-053")
```

### Direct Manager Methods

```python
# Use manager convenience methods
result = manager.get("88304-053", driver="viacep")

# Set default driver
manager.set_default_driver("viacep")
result = manager.get("88304-053")  # Uses default driver
```

### Driver Discovery

```python
# List available drivers
drivers = manager.list_drivers()  # ['viacep', 'widenet', 'brasilapi']

# Check driver availability
has_viacep = manager.has_driver("viacep")  # True

# Get driver information
info = manager.get_driver_info("viacep")
# {'class': PostalCodeViacepDriver, 'name': 'viacep', 'description': '...'}
```

## Manager Types



### FormatterManager
Manages formatting drivers for data standardization.

```python
manager = FormatterManager()
result = manager.format("88304053", driver="brazilian_postalcode")
```

### PostalCodeManager
Manages postal code lookup drivers for address resolution.

```python
manager = PostalCodeManager()
address = manager.get("88304-053", driver="viacep")
```

## Advanced Features

### Caching Support

```python
class PostalCodeManager(AbstractManagerContract):
    def enable_cache(self, enabled: bool = True) -> 'PostalCodeManager':
        """Enable or disable result caching."""
        self._cache_enabled = enabled
        if not enabled:
            self._cache.clear()
        return self

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            'enabled': self._cache_enabled,
            'size': len(self._cache),
            'keys': list(self._cache.keys())
        }
```

### Bulk Operations

```python
def bulk_get(self, postal_codes: List[str], driver: str = "default") -> List[Address]:
    """Get addresses for multiple postal codes."""
    addresses = []
    for postal_code in postal_codes:
        try:
            address = self.get(postal_code, driver)
            addresses.append(address)
        except Exception as e:
            # Handle errors gracefully
            error_address = Address(postal_code=postal_code, error=str(e))
            addresses.append(error_address)
    return addresses
```

## Testing Contract Compliance

All manager implementations should include contract compliance tests:

```python
def test_manager_implements_contract(self):
    """Test that manager implements ManagerContract."""
    manager = MyManager()

    # Test contract compliance
    self.assertIsInstance(manager, ManagerContract)

    # Test required methods
    required_methods = ['load', 'list_drivers', 'has_driver', 'get_driver_info', 'register_driver']
    for method_name in required_methods:
        self.assertTrue(hasattr(manager, method_name))
        self.assertTrue(callable(getattr(manager, method_name)))

    # Test driver management
    drivers = manager.list_drivers()
    self.assertIsInstance(drivers, list)

    if drivers:
        driver_name = drivers[0]
        self.assertTrue(manager.has_driver(driver_name))

        info = manager.get_driver_info(driver_name)
        self.assertIsInstance(info, dict)

        driver = manager.load(driver_name)
        self.assertIsNotNone(driver)
```

## Best Practices

1. **Always inherit from AbstractManagerContract** for common functionality
2. **Register drivers in constructor** using `_register_default_drivers()`
3. **Handle import errors gracefully** when registering drivers
4. **Use specific exception types** (DriverNotFoundError, DriverLoadError)
5. **Provide domain-specific convenience methods** (get, validate, format, etc.)
6. **Support configuration** when loading drivers
7. **Include metadata** when registering drivers
8. **Implement caching** for expensive operations
9. **Support bulk operations** where appropriate
10. **Write comprehensive tests** including contract compliance

## Driver Registration Patterns

### Static Registration

```python
def _register_default_drivers(self) -> None:
    """Register default drivers at initialization."""
    self.register_driver("driver1", Driver1Class, version="1.0.0")
    self.register_driver("driver2", Driver2Class, version="1.0.0")
```

### Dynamic Registration

```python
def _register_default_drivers(self) -> None:
    """Dynamically discover and register drivers."""
    import pkgutil
    import importlib

    for _, name, _ in pkgutil.iter_modules(['drivers/mytype']):
        try:
            module = importlib.import_module(f'drivers.mytype.{name}')
            driver_class = getattr(module, f'{name.title()}Driver')
            self.register_driver(name, driver_class)
        except (ImportError, AttributeError) as e:
            logger.warning("Failed to register %s: %s", name, e)
```

### Conditional Registration

```python
def _register_default_drivers(self) -> None:
    """Register drivers based on availability."""
    # Register core drivers
    self.register_driver("basic", BasicDriver)

    # Register optional drivers
    try:
        import optional_dependency
        self.register_driver("advanced", AdvancedDriver)
    except ImportError:
        logger.info("Advanced driver not available (missing dependency)")
```

## Integration Patterns

### Cross-Manager Integration

```python
class PostalCodeManager(AbstractManagerContract):
    def __init__(self):
        super().__init__()
        # Use FormatterManager for postal code formatting
        self._formatter_manager = FormatterManager()

    def get(self, postal_code: str, driver: str = "default") -> Address:
        # Format postal code before lookup
        formatted_code = self._formatter_manager.format(
            postal_code,
            driver="brazilian_postalcode"
        )

        # Use formatted code for lookup
        driver_instance = self.load(driver)
        return driver_instance.get(formatted_code)
```

### Plugin Architecture

```python
class PluginManager(AbstractManagerContract):
    def register_plugin(self, plugin_path: str) -> None:
        """Register drivers from external plugin."""
        spec = importlib.util.spec_from_file_location("plugin", plugin_path)
        plugin = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(plugin)

        # Register all drivers from plugin
        for name, driver_class in plugin.get_drivers().items():
            self.register_driver(name, driver_class, source="plugin")
```

## See Also

- [Formatter Contract](formatter_contract.md)
- [Validator Contract](validator_contract.md)
- [Contracts Overview](contracts_overview.md)


---

*This contract ensures consistency and interoperability across all manager implementations in the Schubert Toolbox system.*
