"""
Brazilian CNPJ Formatter Driver.

This driver provides formatting and validation for Brazilian CNPJ (Cadastro Nacional
da Pessoa Jurídica) numbers, ensuring consistent formatting and basic validation.
"""

import logging
import re
from typing import Any, Dict

from contracts.formatter_contract import AbstractFormatterContract
from standards.core.base import ValidationError

logger = logging.getLogger(__name__)


class FormatterBrazilianCnpjDriver(AbstractFormatterContract):
    """
    Brazilian CNPJ formatter driver.
    
    Formats and validates Brazilian CNPJ numbers according to official standards.
    CNPJ format: XX.XXX.XXX/XXXX-XX (14 digits total)
    
    Features:
    - Input sanitization (removes non-digit characters)
    - Format validation (14 digits)
    - Consistent output formatting
    - Basic checksum validation (optional)
    
    Example:
        driver = FormatterBrazilianCnpjDriver()
        formatted = driver.format("11222333000181")
        # Returns: "11.222.333/0001-81"
    """
    
    def __init__(self):
        """Initialize Brazilian CNPJ formatter with default configuration."""
        super().__init__()

        # Set default configuration using parent method
        self._set_default_config({
            "strict_validation": True,
            "validate_checksum": False,  # Checksum validation is complex for CNPJ
            "allow_partial": False
        })

    @property
    def name(self) -> str:
        """Get the display name of the formatter."""
        return "Brazilian CNPJ Formatter"
    
    def configure(self, **kwargs) -> "FormatterBrazilianCnpjDriver":
        """
        Configure the formatter with custom settings.
        
        Args:
            strict_validation: If True, raises error for invalid format (default: True)
            validate_checksum: If True, validates CNPJ checksum (default: False)
            allow_partial: If True, allows partial CNPJ numbers (default: False)
            **kwargs: Additional configuration options
        """
        super().configure(**kwargs)
        logger.debug("Brazilian CNPJ formatter configured: %s", self._config)
        return self
    
    def clean(self, cnpj: Any) -> str:
        """
        Clean and validate a Brazilian CNPJ number, returning only digits.

        This method performs comprehensive cleaning and validation, making it
        suitable for use before API calls that require clean CNPJ numbers.

        Args:
            cnpj: CNPJ number as string, int, or any type that can be converted to string

        Returns:
            Clean CNPJ string with only digits (14 characters)

        Raises:
            ValidationError: If CNPJ format is invalid and strict_validation is True

        Example:
            formatter = FormatterBrazilianCnpjDriver()
            clean = formatter.clean("11.222.333/0001-81")
            # Returns: "11222333000181"
        """
        if cnpj is None:
            if self._config["strict_validation"]:
                raise ValidationError("CNPJ cannot be None")
            return ""

        # Convert to string and perform advanced cleaning
        cnpj_str = str(cnpj).strip()

        # Remove all non-digit characters (dots, slashes, hyphens, spaces, etc.)
        clean_cnpj = re.sub(r'[^\d]', '', cnpj_str)

        # Validate length
        if len(clean_cnpj) == 0:
            if self._config["strict_validation"]:
                raise ValidationError("CNPJ cannot be empty")
            return ""

        # Handle partial CNPJ if allowed
        if self._config["allow_partial"] and len(clean_cnpj) < 14:
            if self._config["strict_validation"]:
                raise ValidationError(f"Partial CNPJ not allowed in strict mode: {cnpj_str}")
            return clean_cnpj.zfill(14)  # Pad with zeros

        # Validate full CNPJ length
        if len(clean_cnpj) != 14:
            if self._config["strict_validation"]:
                raise ValidationError(f"CNPJ must have exactly 14 digits, got {len(clean_cnpj)}: {cnpj_str}")
            # Pad with zeros if too short, truncate if too long
            if len(clean_cnpj) < 14:
                clean_cnpj = clean_cnpj.zfill(14)
            else:
                clean_cnpj = clean_cnpj[:14]

        # Validate checksum if enabled
        if self._config["validate_checksum"]:
            if not self._validate_cnpj_checksum(clean_cnpj):
                if self._config["strict_validation"]:
                    raise ValidationError(f"Invalid CNPJ checksum: {cnpj_str}")

        logger.debug("Cleaned CNPJ: %s -> %s", cnpj_str, clean_cnpj)
        return clean_cnpj

    def format(self, cnpj: Any) -> str:
        """
        Format a Brazilian CNPJ number.

        Args:
            cnpj: CNPJ number as string, int, or any type that can be converted to string

        Returns:
            Formatted CNPJ string in XX.XXX.XXX/XXXX-XX format

        Raises:
            ValidationError: If CNPJ format is invalid and strict_validation is True

        Example:
            formatter = FormatterBrazilianCnpjDriver()
            result = formatter.format("11222333000181")
            # Returns: "11.222.333/0001-81"
        """
        # Use the clean method to get validated digits
        clean_cnpj = self.clean(cnpj)

        if not clean_cnpj:
            return ""

        # Handle partial CNPJ if allowed
        if self._config["allow_partial"] and len(clean_cnpj) < 14:
            return self._format_partial_cnpj(clean_cnpj)

        # Format: XX.XXX.XXX/XXXX-XX
        formatted = f"{clean_cnpj[:2]}.{clean_cnpj[2:5]}.{clean_cnpj[5:8]}/{clean_cnpj[8:12]}-{clean_cnpj[12:14]}"

        logger.debug("Formatted CNPJ: %s -> %s", cnpj, formatted)
        return formatted

    def is_valid(self, cnpj: Any) -> bool:
        """
        Check if a CNPJ is valid without raising exceptions.

        Args:
            cnpj: CNPJ number to validate

        Returns:
            True if CNPJ is valid, False otherwise

        Example:
            formatter = FormatterBrazilianCnpjDriver()
            is_valid = formatter.is_valid("11.222.333/0001-81")
            # Returns: True or False
        """
        try:
            # Temporarily disable strict validation to avoid exceptions
            original_strict = self._config["strict_validation"]
            self._config["strict_validation"] = False

            clean_cnpj = self.clean(cnpj)

            # Restore original setting
            self._config["strict_validation"] = original_strict

            # Check if we got a valid 14-digit CNPJ
            if not clean_cnpj or len(clean_cnpj) != 14:
                return False

            # If checksum validation is enabled, check it
            if self._config["validate_checksum"]:
                return self._validate_cnpj_checksum(clean_cnpj)

            return True

        except Exception:
            # Restore original setting in case of exception
            self._config["strict_validation"] = original_strict
            return False

    def _format_partial_cnpj(self, clean_cnpj: str) -> str:
        """Format partial CNPJ with available digits."""
        if len(clean_cnpj) <= 2:
            return clean_cnpj
        elif len(clean_cnpj) <= 5:
            return f"{clean_cnpj[:2]}.{clean_cnpj[2:]}"
        elif len(clean_cnpj) <= 8:
            return f"{clean_cnpj[:2]}.{clean_cnpj[2:5]}.{clean_cnpj[5:]}"
        elif len(clean_cnpj) <= 12:
            return f"{clean_cnpj[:2]}.{clean_cnpj[2:5]}.{clean_cnpj[5:8]}/{clean_cnpj[8:]}"
        else:
            return f"{clean_cnpj[:2]}.{clean_cnpj[2:5]}.{clean_cnpj[5:8]}/{clean_cnpj[8:12]}-{clean_cnpj[12:]}"
    
    def _validate_cnpj_checksum(self, cnpj: str) -> bool:
        """
        Validate CNPJ checksum using official algorithm.
        
        This is a simplified validation. Full CNPJ validation is complex
        and includes additional business rules.
        """
        if len(cnpj) != 14:
            return False
        
        # CNPJ checksum validation algorithm
        # This is a basic implementation - full validation would include more checks
        try:
            # First check digit
            weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
            sum1 = sum(int(cnpj[i]) * weights1[i] for i in range(12))
            remainder1 = sum1 % 11
            check1 = 0 if remainder1 < 2 else 11 - remainder1
            
            if int(cnpj[12]) != check1:
                return False
            
            # Second check digit
            weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
            sum2 = sum(int(cnpj[i]) * weights2[i] for i in range(13))
            remainder2 = sum2 % 11
            check2 = 0 if remainder2 < 2 else 11 - remainder2
            
            return int(cnpj[13]) == check2
            
        except (ValueError, IndexError):
            return False
