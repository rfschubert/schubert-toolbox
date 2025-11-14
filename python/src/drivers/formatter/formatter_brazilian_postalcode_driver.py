"""
Brazilian Postal Code Formatter Driver.

Driver for formatting Brazilian postal codes (CEP) to standard format XXXXX-XXX
following the Manager Pattern.

Usage:
    # Direct usage
    driver = FormatterBrazilianPostalcodeDriver()
    formatted = driver.format("88304053")  # Returns "88304-053"
    
    # Manager usage
    manager = FormatterManager()
    driver = manager.load("brazilian_postalcode")
    formatted = driver.format("88304053")
"""

import logging
import re
from typing import Any, Dict, Union

from contracts.formatter_contract import AbstractFormatterContract, FormatterValidationError

logger = logging.getLogger(__name__)

# Constants to avoid magic numbers
BRAZILIAN_POSTAL_CODE_FULL_LENGTH = 8
BRAZILIAN_POSTAL_CODE_MIN_PARTIAL_LENGTH = 5
BRAZILIAN_POSTAL_CODE_FIRST_PART_LENGTH = 5
DEFAULT_OUTPUT_FORMAT = 'XXXXX-XXX'


class FormatterBrazilianPostalcodeDriver(AbstractFormatterContract):
    """
    Brazilian postal code formatter driver.

    Implements the FormatterContract interface:
    - format(value: Union[str, int]) -> str
    - configure(**kwargs) -> Self
    - get_config() -> Dict[str, Any]
    """

    def __init__(self):
        """Initialize Brazilian postal code formatter with default configuration."""
        super().__init__()

        # Set default configuration using parent method
        self._set_default_config({
            'strict_validation': True,
            'allow_partial': False,
            'output_format': DEFAULT_OUTPUT_FORMAT
        })

        logger.debug("FormatterBrazilianPostalcodeDriver initialized")

    @property
    def name(self) -> str:
        """Get formatter display name."""
        return "Brazilian Postal Code"
    
    def format(self, value: Union[str, int]) -> str:
        """
        Format Brazilian postal code to standard XXXXX-XXX format.
        
        Args:
            value: Postal code as string or integer
            
        Returns:
            Formatted postal code string in XXXXX-XXX format
            
        Raises:
            ValidationError: If postal code is invalid or cannot be formatted
        """
        if value is None:
            raise FormatterValidationError("Postal code value is required", error_code="FORMATTER_VALUE_REQUIRED")
        
        # Convert to string and clean
        clean_value = self._clean_postal_code(value)
        
        # Validate if strict validation is enabled
        if self._config['strict_validation']:
            self._validate_postal_code(clean_value)
        
        # Format using configured output format
        formatted = self._apply_format(clean_value)

        # Security: Log sanitized input instead of raw value to prevent log injection
        safe_input = self._sanitize_for_logging(clean_value)
        logger.debug("Formatted postal code: %s -> %s", safe_input, formatted)
        return formatted
    
    def configure(self, **kwargs) -> 'FormatterBrazilianPostalcodeDriver':
        """
        Configure formatter options.

        Args:
            strict_validation: Enable strict validation (default: True)
            allow_partial: DEPRECATED - Brazilian CEPs must have exactly 8 digits (default: False)
            output_format: Output format pattern (default: 'XXXXX-XXX')

        Returns:
            Self for method chaining
        """
        for key, value in kwargs.items():
            if key in self._default_config:
                self._config[key] = value
                logger.debug("Brazilian postal code formatter configured: %s = %s", key, value)
            else:
                logger.warning("Unknown configuration option: %s", key)
        
        return self
    
    def get_config(self) -> Dict[str, Any]:
        """Get current formatter configuration."""
        return self._config.copy()
    
    def reset_config(self) -> 'FormatterBrazilianPostalcodeDriver':
        """Reset configuration to defaults."""
        self._config = self._default_config.copy()
        logger.debug("Brazilian postal code formatter configuration reset to defaults")
        return self
    
    def _clean_postal_code(self, value: Union[str, int]) -> str:
        """Clean postal code removing non-numeric characters."""
        # Convert to string
        str_value = str(value).strip()
        
        if not str_value:
            raise FormatterValidationError("Postal code cannot be empty", error_code="FORMATTER_EMPTY_VALUE")

        # Remove all non-numeric characters
        clean = re.sub(r'[^0-9]', '', str_value)

        if not clean:
            raise FormatterValidationError("Postal code must contain numeric digits", error_code="FORMATTER_NO_DIGITS")
        
        return clean
    
    def _validate_postal_code(self, postal_code: str) -> None:
        """Validate Brazilian postal code format."""
        # Brazilian CEP must have exactly 8 digits to be valid
        # The allow_partial configuration is deprecated as partial CEPs are invalid
        if len(postal_code) != BRAZILIAN_POSTAL_CODE_FULL_LENGTH:
            raise FormatterValidationError(
                f"Brazilian postal code must have exactly {BRAZILIAN_POSTAL_CODE_FULL_LENGTH} digits, got {len(postal_code)}",
                error_code="FORMATTER_INVALID_LENGTH"
            )

        # Note: Removed redundant isdigit() check as _clean_postal_code already ensures only digits
    
    def _apply_format(self, postal_code: str) -> str:
        """Apply formatting to clean postal code using configured output format."""
        output_format = self._config['output_format']

        if len(postal_code) == BRAZILIAN_POSTAL_CODE_FULL_LENGTH:
            # Standard format using configured pattern - only valid CEPs with 8 digits
            return self._format_with_pattern(postal_code, output_format)
        else:
            # Brazilian CEP must have exactly 8 digits to be valid
            # Do not format partial CEPs as they are invalid
            raise FormatterValidationError(
                f"Brazilian postal code must have exactly {BRAZILIAN_POSTAL_CODE_FULL_LENGTH} digits, got {len(postal_code)}",
                error_code="FORMATTER_INVALID_LENGTH"
            )

    def _format_with_pattern(self, postal_code: str, pattern: str) -> str:
        """Format postal code using the specified pattern."""
        if pattern == 'XXXXX-XXX':
            return f"{postal_code[:BRAZILIAN_POSTAL_CODE_FIRST_PART_LENGTH]}-{postal_code[BRAZILIAN_POSTAL_CODE_FIRST_PART_LENGTH:]}"
        elif pattern == 'XXXXX.XXX':
            return f"{postal_code[:BRAZILIAN_POSTAL_CODE_FIRST_PART_LENGTH]}.{postal_code[BRAZILIAN_POSTAL_CODE_FIRST_PART_LENGTH:]}"
        elif pattern == 'XXXXX XXX':
            return f"{postal_code[:BRAZILIAN_POSTAL_CODE_FIRST_PART_LENGTH]} {postal_code[BRAZILIAN_POSTAL_CODE_FIRST_PART_LENGTH:]}"
        elif pattern == 'XXXXXXXX':
            return postal_code
        else:
            # Default to standard format if pattern is not recognized
            logger.warning("Unknown output format pattern: %s, using default", pattern)
            return f"{postal_code[:BRAZILIAN_POSTAL_CODE_FIRST_PART_LENGTH]}-{postal_code[BRAZILIAN_POSTAL_CODE_FIRST_PART_LENGTH:]}"

    def _sanitize_for_logging(self, value: str, max_length: int = 20) -> str:
        """
        Sanitize value for safe logging to prevent log injection attacks.

        Args:
            value: Value to sanitize
            max_length: Maximum length to truncate to

        Returns:
            Sanitized string safe for logging
        """
        if value is None:
            return "None"

        # Convert to string and limit length
        safe_value = str(value)[:max_length]

        # Remove control characters and newlines to prevent log injection
        safe_value = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', safe_value)

        # Replace newlines and carriage returns
        safe_value = safe_value.replace('\n', '\\n').replace('\r', '\\r')

        return safe_value
    
    def is_valid_format(self, value: Union[str, int]) -> bool:
        """
        Check if value can be formatted as Brazilian postal code.
        
        Args:
            value: Value to check
            
        Returns:
            True if value can be formatted, False otherwise
        """
        try:
            self.format(value)
            return True
        except FormatterValidationError:
            return False
