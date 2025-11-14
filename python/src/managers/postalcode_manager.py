"""
PostalCode Manager for orchestrating postal code lookup drivers.

This manager provides a unified interface for managing postal code lookup drivers
following the Manager Pattern documented in docs/patterns/manager_pattern_details.md.
"""

import logging
from typing import Any, Dict, List, Optional, Union

from contracts.manager_contract import (
    AbstractManagerContract,
    ManagerContract,
    DriverNotFoundError,
    DriverLoadError
)
from standards.address import Address
from utils.logging_security import sanitize_cache_key, sanitize_user_input, sanitize_error_message

logger = logging.getLogger(__name__)


class PostalCodeManager(AbstractManagerContract):
    """
    Manager for postal code lookup drivers.
    
    Provides unified interface for loading and using postal code drivers
    that return Address objects. All drivers must implement the same interface:
    - get(postal_code: str) -> Address
    - configure(**kwargs) -> Self
    - get_config() -> Dict[str, Any]
    
    Example usage:
        # Manager-orchestrated usage
        manager = PostalCodeManager()
        driver = manager.load("viacep")
        address = driver.get("01310-100")
        
        # Direct manager method
        address = manager.get("01310-100", driver="viacep")
    """
    
    def __init__(self):
        """Initialize PostalCodeManager with empty driver registry."""
        super().__init__()
        self._drivers: Dict[str, Dict[str, Any]] = {}
        self._default_driver: Optional[str] = None
        self._cache: Dict[str, Any] = {}
        self._cache_enabled: bool = False

        # Register default drivers
        self._register_default_drivers()

        logger.debug("PostalCodeManager initialized")

    def _register_default_drivers(self) -> None:
        """Register default postal code drivers."""
        # Register ViaCEP driver
        try:
            from drivers.postalcode.postalcode_viacep_driver import PostalCodeViacepDriver
            self.register_driver(
                "viacep",
                PostalCodeViacepDriver,
                description="ViaCEP Brazilian postal code service",
                version="1.0.0",
                country="BR"
            )
            logger.debug("Registered ViaCEP driver")
        except ImportError as e:
            logger.warning("Failed to register ViaCEP driver: %s", e)

        # Register WideNet driver
        try:
            from drivers.postalcode.postalcode_widenet_driver import PostalCodeWidenetDriver
            self.register_driver(
                "widenet",
                PostalCodeWidenetDriver,
                description="WideNet Brazilian postal code service",
                version="1.0.0",
                country="BR"
            )
            logger.debug("Registered WideNet driver")
        except ImportError as e:
            logger.warning("Failed to register WideNet driver: %s", e)

        # Register BrasilAPI driver
        try:
            from drivers.postalcode.postalcode_brasilapi_driver import PostalCodeBrasilApiDriver
            self.register_driver(
                "brasilapi",
                PostalCodeBrasilApiDriver,
                description="BrasilAPI Brazilian postal code service",
                version="1.0.0",
                country="BR"
            )
            logger.debug("Registered BrasilAPI driver")
        except ImportError as e:
            logger.warning("Failed to register BrasilAPI driver: %s", e)

    def load(self, driver_name: str, **config) -> Any:
        """
        Load and configure a postal code driver.

        Args:
            driver_name: Name of the driver to load
            **config: Configuration options for the driver

        Returns:
            Configured driver instance that implements postal code interface

        Raises:
            DriverNotFoundError: If driver is not available
            DriverLoadError: If driver fails to load
        """
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

            logger.debug("Loaded postal code driver: %s", driver_name)
            return driver_instance

        except Exception as e:
            logger.error("Failed to load driver %s: %s", driver_name, e)
            raise DriverLoadError(driver_name, str(e))

    def get(self, postal_code: str, driver: str = "default") -> Address:
        """
        Get address for postal code using specified driver.
        
        Args:
            postal_code: Postal code to lookup
            driver: Driver name to use (defaults to default driver)
            
        Returns:
            Address object with postal code information
            
        Raises:
            DriverNotFoundError: If driver is not available
            PostalCodeError: If postal code lookup fails
        """
        if driver == "default":
            if not self._default_driver:
                available = self.list_drivers()
                if not available:
                    raise DriverNotFoundError("default", available)
                driver = available[0]  # Use first available driver
            else:
                driver = self._default_driver
        
        # Check cache first
        cache_key = f"{driver}:{postal_code}"
        if self._cache_enabled and cache_key in self._cache:
            # Security: Sanitize cache key to prevent log injection
            safe_cache_key = sanitize_cache_key(cache_key)
            logger.debug("Returning cached result for %s", safe_cache_key)
            return self._cache[cache_key]
        
        # Load driver and get address
        driver_instance = self.load(driver)
        address = driver_instance.get(postal_code)
        
        # Cache result
        if self._cache_enabled:
            self._cache[cache_key] = address
            # Security: Sanitize cache key to prevent log injection
            safe_cache_key = sanitize_cache_key(cache_key)
            logger.debug("Cached result for %s", safe_cache_key)
        
        return address
    
    def get_or_raise(self, postal_code: str, driver: str = "default") -> Address:
        """
        Get address or raise exception on failure.
        
        Args:
            postal_code: Postal code to lookup
            driver: Driver name to use
            
        Returns:
            Address object
            
        Raises:
            PostalCodeError: If postal code is invalid or lookup fails
        """
        address = self.get(postal_code, driver)
        
        # Validate address completeness
        if not address.is_complete():
            from validation_base import ValidationError
            raise ValidationError(
                f"Incomplete address returned for postal code: {postal_code}",
                error_code="POSTAL_CODE_INCOMPLETE_ADDRESS"
            )
        
        return address
    
    def bulk_get(self, postal_codes: List[str], driver: str = "default") -> List[Address]:
        """
        Get addresses for multiple postal codes.
        
        Args:
            postal_codes: List of postal codes to lookup
            driver: Driver name to use
            
        Returns:
            List of Address objects
        """
        addresses = []
        for postal_code in postal_codes:
            try:
                address = self.get(postal_code, driver)
                addresses.append(address)
            except Exception as e:
                # Security: Sanitize user input and error message to prevent log injection
                safe_postal_code = sanitize_user_input(postal_code)
                safe_error = sanitize_error_message(e)
                logger.warning("Failed to get address for %s: %s", safe_postal_code, safe_error)
                # Create empty address with error info
                error_address = Address(
                    postal_code=postal_code,
                    formatted_address=f"Error: {str(e)}"
                )
                addresses.append(error_address)
        
        return addresses
    
    def set_default_driver(self, driver_name: str) -> None:
        """
        Set default driver for postal code lookups.
        
        Args:
            driver_name: Name of driver to set as default
            
        Raises:
            DriverNotFoundError: If driver is not available
        """
        if not self.has_driver(driver_name):
            raise DriverNotFoundError(driver_name, self.list_drivers())
        
        self._default_driver = driver_name
        logger.info("Default driver set to: %s", driver_name)
    
    def get_default_driver(self) -> Optional[str]:
        """Get current default driver name."""
        return self._default_driver
    
    def enable_cache(self, enabled: bool = True) -> 'PostalCodeManager':
        """
        Enable or disable result caching.
        
        Args:
            enabled: Whether to enable caching
            
        Returns:
            Self for method chaining
        """
        self._cache_enabled = enabled
        if not enabled:
            self._cache.clear()
            logger.debug("Cache disabled and cleared")
        else:
            logger.debug("Cache enabled")
        
        return self
    
    def clear_cache(self) -> 'PostalCodeManager':
        """
        Clear cached results.
        
        Returns:
            Self for method chaining
        """
        self._cache.clear()
        logger.debug("Cache cleared")
        return self
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        return {
            'enabled': self._cache_enabled,
            'size': len(self._cache),
            'keys': list(self._cache.keys())
        }
