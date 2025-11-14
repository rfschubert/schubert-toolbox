"""
Formatter Manager for orchestrating data formatting drivers.

This manager provides a unified interface for managing formatter drivers
following the Manager Pattern documented in docs/patterns/manager_pattern_details.md.
"""

import logging
from typing import Any

from contracts.manager_contract import (
    AbstractManagerContract,
    DriverLoadError,
    DriverNotFoundError,
)
from utils.logging_security import sanitize_cache_key


logger = logging.getLogger(__name__)


class FormatterManager(AbstractManagerContract):
    """
    Manager for formatter drivers.

    Provides unified interface for loading and using formatter drivers
    that format data values. All drivers must implement the same interface:
    - format(value: Union[str, int, Any]) -> str
    - configure(**kwargs) -> Self
    - get_config() -> Dict[str, Any]

    Example usage:
        # Manager-orchestrated usage
        manager = FormatterManager()
        driver = manager.load("brazilian_postalcode")
        formatted = driver.format("88304053")

        # Direct manager method
        formatted = manager.format("88304053", driver="brazilian_postalcode")
    """

    def __init__(self):
        """Initialize FormatterManager with empty driver registry."""
        super().__init__()
        self._drivers: dict[str, dict[str, Any]] = {}
        self._default_driver: str | None = None
        self._cache: dict[str, Any] = {}
        self._cache_enabled: bool = False

        # Register default drivers
        self._register_default_drivers()

        logger.debug("FormatterManager initialized")

    def _register_default_drivers(self) -> None:
        """Register default formatter drivers."""
        # Register Brazilian Postal Code formatter
        try:
            from drivers.formatter.formatter_brazilian_postalcode_driver import (
                FormatterBrazilianPostalcodeDriver,
            )

            self.register_driver(
                "brazilian_postalcode",
                FormatterBrazilianPostalcodeDriver,
                description="Brazilian postal code formatter (CEP)",
                version="1.0.0",
                country="BR",
            )
            logger.debug("Registered Brazilian Postal Code formatter")
        except ImportError as e:
            logger.warning("Failed to register Brazilian Postal Code formatter: %s", e)

    def load(self, driver_name: str, **config) -> Any:
        """
        Load and configure a formatter driver.

        Args:
            driver_name: Name of the driver to load
            **config: Configuration options for the driver

        Returns:
            Configured driver instance that implements formatter interface

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

            logger.debug("Loaded formatter driver: %s", driver_name)
            return driver_instance

        except Exception as e:
            logger.error("Failed to load driver %s: %s", driver_name, e)
            raise DriverLoadError(driver_name, str(e))

    def format(self, value: str | int | Any, driver: str = "default") -> str:
        """
        Format value using specified driver.

        Args:
            value: Value to format
            driver: Driver name to use (defaults to default driver)

        Returns:
            Formatted string value

        Raises:
            DriverNotFoundError: If driver is not available
            ValidationError: If value cannot be formatted
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
        cache_key = f"{driver}:{value!s}"
        if self._cache_enabled and cache_key in self._cache:
            # Security: Sanitize cache key to prevent log injection
            safe_cache_key = sanitize_cache_key(cache_key)
            logger.debug("Returning cached result for %s", safe_cache_key)
            return self._cache[cache_key]

        # Load driver and format value
        driver_instance = self.load(driver)
        formatted_value = driver_instance.format(value)

        # Cache result
        if self._cache_enabled:
            self._cache[cache_key] = formatted_value
            # Security: Sanitize cache key to prevent log injection
            safe_cache_key = sanitize_cache_key(cache_key)
            logger.debug("Cached result for %s", safe_cache_key)

        return formatted_value

    def bulk_format(self, values: list[str | int | Any], driver: str = "default") -> list[str]:
        """
        Format multiple values using specified driver.

        Args:
            values: List of values to format
            driver: Driver name to use

        Returns:
            List of formatted string values
        """
        formatted_values = []
        for value in values:
            try:
                formatted = self.format(value, driver)
                formatted_values.append(formatted)
            except Exception as e:
                logger.warning("Failed to format value %s: %s", value, e)
                # Add original value as string if formatting fails
                formatted_values.append(str(value))

        return formatted_values

    def set_default_driver(self, driver_name: str) -> None:
        """
        Set default driver for formatting.

        Args:
            driver_name: Name of driver to set as default

        Raises:
            DriverNotFoundError: If driver is not available
        """
        if not self.has_driver(driver_name):
            raise DriverNotFoundError(driver_name, self.list_drivers())

        self._default_driver = driver_name
        logger.info("Default formatter driver set to: %s", driver_name)

    def get_default_driver(self) -> str | None:
        """Get current default driver name."""
        return self._default_driver

    def enable_cache(self, enabled: bool = True) -> "FormatterManager":
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
            logger.debug("Formatter cache disabled and cleared")
        else:
            logger.debug("Formatter cache enabled")

        return self

    def clear_cache(self) -> "FormatterManager":
        """
        Clear cached results.

        Returns:
            Self for method chaining
        """
        self._cache.clear()
        logger.debug("Formatter cache cleared")
        return self

    def get_cache_stats(self) -> dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        return {
            "enabled": self._cache_enabled,
            "size": len(self._cache),
            "keys": list(self._cache.keys()),
        }

    def is_valid_format(self, value: str | int | Any, driver: str = "default") -> bool:
        """
        Check if value can be formatted by specified driver.

        Args:
            value: Value to check
            driver: Driver name to use

        Returns:
            True if value can be formatted, False otherwise
        """
        try:
            driver_instance = self.load(driver)
            if hasattr(driver_instance, "is_valid_format"):
                return driver_instance.is_valid_format(value)
            else:
                # Try to format and see if it succeeds
                driver_instance.format(value)
                return True
        except Exception:
            return False
