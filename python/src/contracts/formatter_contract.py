"""
Formatter Contract for standardizing formatter drivers.

This contract defines the interface that all formatter drivers must implement
to ensure consistency across the system.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Union


class FormatterContract(ABC):
    """
    Abstract base class defining the contract for formatter drivers.
    
    All formatter drivers must implement this interface to ensure
    consistent behavior across the system.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        Get the display name of the formatter.
        
        Returns:
            Human-readable name of the formatter
        """
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
            ValidationError: If value cannot be formatted
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
    
    def reset_config(self) -> 'FormatterContract':
        """
        Reset configuration to defaults.
        
        Returns:
            Self for method chaining
        """
        # Default implementation - can be overridden
        return self
    
    def is_valid_format(self, value: Union[str, int, Any]) -> bool:
        """
        Check if value can be formatted by this formatter.
        
        Args:
            value: Value to check
            
        Returns:
            True if value can be formatted, False otherwise
        """
        # Default implementation - can be overridden
        try:
            self.format(value)
            return True
        except Exception:
            return False
    
    def get_supported_types(self) -> list:
        """
        Get list of supported input types.
        
        Returns:
            List of supported Python types
        """
        # Default implementation - can be overridden
        return [str, int]
    
    def get_output_format(self) -> str:
        """
        Get description of the output format.
        
        Returns:
            String describing the output format
        """
        # Default implementation - can be overridden
        return "Formatted string"


class AbstractFormatterContract(FormatterContract):
    """
    Abstract base class with common formatter functionality.
    
    Provides default implementations for common formatter methods
    while still requiring subclasses to implement the core format() method.
    """
    
    def __init__(self):
        """Initialize formatter with default configuration."""
        self._default_config: Dict[str, Any] = {}
        self._config: Dict[str, Any] = {}
    
    @property
    def name(self) -> str:
        """Default name implementation."""
        return self.__class__.__name__.replace('Driver', '').replace('Formatter', '')
    
    def configure(self, **kwargs) -> 'AbstractFormatterContract':
        """
        Default configure implementation.
        
        Updates internal configuration dictionary with provided options.
        """
        for key, value in kwargs.items():
            if key in self._default_config:
                self._config[key] = value
            else:
                # Allow unknown config options but warn about them
                import logging
                logger = logging.getLogger(__name__)
                logger.warning("Unknown configuration option for %s: %s", self.name, key)
        
        return self
    
    def get_config(self) -> Dict[str, Any]:
        """Default get_config implementation."""
        return self._config.copy()
    
    def reset_config(self) -> 'AbstractFormatterContract':
        """Default reset_config implementation."""
        self._config = self._default_config.copy()
        return self
    
    def _set_default_config(self, config: Dict[str, Any]) -> None:
        """
        Set default configuration for the formatter.
        
        Args:
            config: Default configuration dictionary
        """
        self._default_config = config.copy()
        self._config = config.copy()


# Exception classes for formatter errors
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
