"""
Validation drivers package.

This package contains all validation driver implementations and
handles automatic registration with the global registry.
"""

# Validation drivers temporarily disabled - untracked files
# from .registry import ValidatorDriver, ValidatorRegistry, register_driver
# from .validator_contact_driver import EmailValidator, PhoneValidator
# from .validator_document_driver import CNPJValidator, CPFValidator, USSSNValidator


# Import other driver modules as they are created
# from .financial import BICValidator, IBANValidator, LEIValidator
# from .pix import PIXKeyValidator, PIXCPFValidator, PIXEmailValidator
# from .address import PostalCodeValidator
# from .generic import RequiredValidator, LengthValidator, RegexValidator


# Auto-register all drivers - temporarily disabled
# def _register_all_drivers():
#     """Register all available drivers with the global registry."""
#
#     # Document validators
#     register_driver(ValidatorDriver.CPF, CPFValidator)
#     register_driver(ValidatorDriver.CNPJ, CNPJValidator)
#     register_driver(ValidatorDriver.US_SSN, USSSNValidator)
#
#     # Contact validators
#     register_driver(ValidatorDriver.EMAIL, EmailValidator)
#     register_driver(ValidatorDriver.PHONE, PhoneValidator)

    # Financial validators (when implemented)
    # register_driver(ValidatorDriver.BIC, BICValidator)
    # register_driver(ValidatorDriver.IBAN, IBANValidator)
    # register_driver(ValidatorDriver.LEI, LEIValidator)

    # PIX validators (when implemented)
    # register_driver(ValidatorDriver.PIX_KEY, PIXKeyValidator)
    # register_driver(ValidatorDriver.PIX_CPF, PIXCPFValidator)
    # register_driver(ValidatorDriver.PIX_EMAIL, PIXEmailValidator)

    # Address validators (when implemented)
    # register_driver(ValidatorDriver.POSTAL_CODE, PostalCodeValidator)

    # Generic validators (when implemented)
    # register_driver(ValidatorDriver.REQUIRED, RequiredValidator)
    # register_driver(ValidatorDriver.LENGTH, LengthValidator)
    # register_driver(ValidatorDriver.REGEX, RegexValidator)


# Register all drivers when module is imported - temporarily disabled
# _register_all_drivers()

# Export all validators for direct import
__all__ = [
    # Registry
    "ValidatorDriver",
    "ValidatorRegistry",
    "register_driver",
    # Document validators
    "CPFValidator",
    "CNPJValidator",
    "USSSNValidator",
    # Contact validators
    "EmailValidator",
    "PhoneValidator",
    # Financial validators (when implemented)
    # "BICValidator",
    # "IBANValidator",
    # "LEIValidator",
    # PIX validators (when implemented)
    # "PIXKeyValidator",
    # "PIXCPFValidator",
    # "PIXEmailValidator",
    # Address validators (when implemented)
    # "PostalCodeValidator",
    # Generic validators (when implemented)
    # "RequiredValidator",
    # "LengthValidator",
    # "RegexValidator",
]
