"""
Schubert Toolbox - Contracts Package

This package defines the contracts (interfaces) that all components must implement
to ensure consistency and interoperability across the system.

Contracts define:
- Method signatures
- Expected behavior
- Input/output specifications
- Error handling requirements

Usage:
    from contracts import ValidatorContract, ManagerContract

    class MyValidator(ValidatorContract):
        def validate(self, data: Any) -> ValidationResultContract:
            # Implementation must follow contract
            pass

    class MyManager(ManagerContract):
        def load(self, driver_name: str) -> Any:
            # Implementation must follow contract
            pass
"""

from .formatter_contract import (
    AbstractFormatterContract,
    FormatterConfigurationError,
    FormatterContract,
    FormatterError,
    FormatterValidationError,
)
from .manager_contract import (
    AbstractManagerContract,
    DriverLoadError,
    DriverNotFoundError,
    ManagerContract,
    ManagerError,
)
# Validator contracts temporarily disabled - untracked files
# from .validator_contract import (
#     ValidationErrorContract,
#     ValidationResultContract,
#     ValidatorConfigContract,
#     ValidatorContract,
# )


__version__ = "1.0.0"
__author__ = "Schubert Toolbox Team"

__all__ = [
    # Manager contracts
    "ManagerContract",
    "ManagerError",
    "DriverNotFoundError",
    "DriverLoadError",
    "AbstractManagerContract",
    # Validator contracts
    "ValidatorContract",
    "ValidationResultContract",
    "ValidationErrorContract",
    "ValidatorConfigContract",
    # Formatter contracts
    "FormatterContract",
    "AbstractFormatterContract",
    "FormatterError",
    "FormatterValidationError",
    "FormatterConfigurationError",
]
