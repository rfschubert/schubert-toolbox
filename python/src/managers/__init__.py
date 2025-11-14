"""
Schubert Toolbox - Managers Package

This package contains all manager implementations that follow the ManagerContract.
Managers provide a unified interface for loading and managing drivers.

Usage:
    from managers import ValidatorManager, PersonManager
    
    validator_manager = ValidatorManager()
    person_manager = PersonManager()
    
    # Load drivers using consistent interface
    cpf_validator = validator_manager.load("cpf")
    person_factory = person_manager.load("person_factory")
"""

from .validator_manager import ValidatorManager
from .postalcode_manager import PostalCodeManager
from .formatter_manager import FormatterManager
# from .person_manager import PersonManager  # Temporarily disabled due to dataclass issues

__version__ = "1.0.0"
__author__ = "Schubert Toolbox Team"

__all__ = [
    "ValidatorManager",
    "PostalCodeManager",
    "FormatterManager",
    # "PersonManager",  # Temporarily disabled
]
