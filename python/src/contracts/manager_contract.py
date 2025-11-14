"""
Manager contracts defining the interface all managers must implement.

This module provides the contracts (interfaces) that ensure all managers
have consistent behavior with driver loading and management capabilities.
"""

from abc import ABC, abstractmethod
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ManagerContract(Protocol):
    """
    Main contract that all managers must implement.

    This contract ensures that all managers have a consistent interface
    for loading and managing drivers, providing a unified way to access
    different types of functionality across the system.

    Contract Requirements:
    1. Must have a load() method that accepts driver names and returns drivers
    2. Must maintain an internal dict of available drivers
    3. Must provide methods to list and check available drivers
    4. Must handle driver loading errors gracefully
    5. Must be thread-safe for concurrent access
    """

    def load(self, driver_name: str, **config) -> Any:
        """
        Load a driver by name with optional configuration.

        This is the core method that all managers must implement.
        It should:
        1. Accept a driver name as string
        2. Look up the driver in internal dict
        3. Return an instance of the driver
        4. Apply any configuration provided
        5. Handle errors gracefully

        Args:
            driver_name: Name of the driver to load
            **config: Optional configuration for the driver

        Returns:
            Driver instance ready for use

        Raises:
            DriverNotFoundError: If driver is not available
            DriverLoadError: If driver fails to load
        """
        ...

    def list_drivers(self) -> list[str]:
        """
        Get list of available driver names.

        Returns:
            List of driver names that can be loaded
        """
        ...

    def has_driver(self, driver_name: str) -> bool:
        """
        Check if a driver is available.

        Args:
            driver_name: Name of driver to check

        Returns:
            True if driver is available, False otherwise
        """
        ...

    def get_driver_info(self, driver_name: str) -> dict[str, Any]:
        """
        Get information about a specific driver.

        Args:
            driver_name: Name of driver to get info for

        Returns:
            Dictionary with driver information

        Raises:
            DriverNotFoundError: If driver is not available
        """
        ...

    def register_driver(self, driver_name: str, driver_class: type, **metadata) -> None:
        """
        Register a new driver with the manager.

        Args:
            driver_name: Name to register the driver under
            driver_class: Class or factory for the driver
            **metadata: Additional metadata about the driver
        """
        ...

    def unregister_driver(self, driver_name: str) -> bool:
        """
        Unregister a driver from the manager.

        Args:
            driver_name: Name of driver to unregister

        Returns:
            True if driver was unregistered, False if not found
        """
        ...

    @property
    def driver_count(self) -> int:
        """
        Get the number of registered drivers.

        Returns:
            Number of available drivers
        """
        ...


class ManagerError(Exception):
    """Base exception for manager-related errors."""


class DriverNotFoundError(ManagerError):
    """Raised when a requested driver is not found."""

    def __init__(self, driver_name: str, available_drivers: list[str] | None = None):
        self.driver_name = driver_name
        self.available_drivers = available_drivers or []

        message = f"Driver '{driver_name}' not found"
        if self.available_drivers:
            message += f". Available drivers: {', '.join(self.available_drivers)}"

        super().__init__(message)


class DriverLoadError(ManagerError):
    """Raised when a driver fails to load."""

    def __init__(self, driver_name: str, reason: str):
        self.driver_name = driver_name
        self.reason = reason
        super().__init__(f"Failed to load driver '{driver_name}': {reason}")


class AbstractManagerContract(ABC):
    """
    Abstract base class implementing ManagerContract.

    Provides default implementations for common manager functionality
    while enforcing the contract through abstract methods.

    Managers can inherit from this class to get:
    - Driver registry management
    - Error handling
    - Thread-safety guarantees
    - Consistent interface
    """

    def __init__(self):
        """Initialize the manager with empty driver registry."""
        self._drivers: dict[str, dict[str, Any]] = {}
        self._instances: dict[str, Any] = {}
        self._lock = None  # Can be set to threading.Lock() if needed

    @abstractmethod
    def load(self, driver_name: str, **config) -> Any:
        """
        Load driver - must be implemented by subclasses.

        Args:
            driver_name: Name of driver to load
            **config: Configuration for the driver

        Returns:
            Driver instance
        """

    def list_drivers(self) -> list[str]:
        """Get list of available driver names."""
        return list(self._drivers.keys())

    def has_driver(self, driver_name: str) -> bool:
        """Check if driver is available."""
        return driver_name in self._drivers

    def get_driver_info(self, driver_name: str) -> dict[str, Any]:
        """Get driver information."""
        if driver_name not in self._drivers:
            raise DriverNotFoundError(driver_name, self.list_drivers())

        return self._drivers[driver_name].copy()

    def register_driver(self, driver_name: str, driver_class: type, **metadata) -> None:
        """Register a driver."""
        self._drivers[driver_name] = {
            "class": driver_class,
            "metadata": metadata,
            "registered_at": self._get_timestamp(),
        }

    def unregister_driver(self, driver_name: str) -> bool:
        """Unregister a driver."""
        if driver_name in self._drivers:
            del self._drivers[driver_name]
            # Also remove cached instance if exists
            if driver_name in self._instances:
                del self._instances[driver_name]
            return True
        return False

    @property
    def driver_count(self) -> int:
        """Get number of registered drivers."""
        return len(self._drivers)

    def _get_driver_class(self, driver_name: str) -> type:
        """Get driver class, raising error if not found."""
        if driver_name not in self._drivers:
            raise DriverNotFoundError(driver_name, self.list_drivers())

        return self._drivers[driver_name]["class"]

    def _get_timestamp(self) -> str:
        """Get current timestamp for registration tracking."""
        from datetime import datetime

        return datetime.utcnow().isoformat()

    def __len__(self) -> int:
        """Return number of registered drivers."""
        return len(self._drivers)

    def __contains__(self, driver_name: str) -> bool:
        """Check if driver is registered using 'in' operator."""
        return driver_name in self._drivers

    def __str__(self) -> str:
        """String representation of the manager."""
        return f"{self.__class__.__name__}(drivers={len(self._drivers)})"

    def __repr__(self) -> str:
        """Detailed string representation of the manager."""
        driver_names = list(self._drivers.keys())
        return f"{self.__class__.__name__}(drivers={driver_names})"
