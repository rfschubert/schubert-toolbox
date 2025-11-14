"""
Schubert Toolbox - Python Standards Implementation

This package provides Python classes that implement the Schubert Toolbox JSON schemas
with proper validation, type hints, and ORM-ready structure.

The classes in this package are generated from and validated against the universal
JSON schemas located in the /schemas directory.

Usage:
    from standards import NaturalPerson, Address, PIXTransaction
    from standards.core import ValidationError

    person = NaturalPerson(
        name="João Silva",
        tax_id="12345678901",
        birth_date="1990-01-01"
    )

    person.add_email("joao@example.com", is_primary=True)
    person.add_address(Address(
        street_name="Rua das Flores, 123",
        locality="São Paulo",
        country_code="BR"
    ))

Key Features:
- JSON Schema validation
- Type hints throughout
- ORM-ready structure
- Multiple contact support
- International standards compliance
- Extensible architecture
"""

# Person models
# from .person.person import Person, NaturalPerson, LegalPerson, PersonType  # Temporarily disabled
# from .person.contact import ContactInformation, EmailContact, PhoneContact, ContactType  # Temporarily disabled
# from .person.background import BackgroundCheck, PEPStatus, ComplianceStatus  # Temporarily disabled
# Address models
from .address.address import Address, AddressType, GeographicCoordinates
from .core.base import BaseModel, Country, ValidationError


# Financial models
# from .financial.institution import FinancialInstitution, BrazilianBank, InstitutionType  # Temporarily disabled
# from .financial.account import BankAccount, BrazilianBankAccount, AccountType  # Temporarily disabled
# from .financial.identifiers import BIC, IBAN, LEI  # Temporarily disabled

# Payment models
# from .payment.pix import PIXKey, PIXTransaction, PIXQRCode, PIXKeyType, PIXTransactionType  # Temporarily disabled

__version__ = "1.0.0"
__author__ = "Schubert Toolbox Team"

__all__ = [
    # Core
    "BaseModel",
    "ValidationError",
    "Country",
    # Person
    # "Person",
    # "NaturalPerson",
    # "LegalPerson",
    # "PersonType",
    # "ContactInformation",
    # "EmailContact",
    # "PhoneContact",
    # "ContactType",
    # "BackgroundCheck",
    # "PEPStatus",
    # "ComplianceStatus",
    # Address
    "Address",
    "AddressType",
    "GeographicCoordinates",
    # Financial
    # "FinancialInstitution",
    # "BrazilianBank",
    # "InstitutionType",
    # "BankAccount",
    # "BrazilianBankAccount",
    # "AccountType",
    # "BIC",
    # "IBAN",
    # "LEI",
    # Payment
    # "PIXKey",
    # "PIXTransaction",
    # "PIXQRCode",
    # "PIXKeyType",
    # "PIXTransactionType",
]


def validate_against_schema(data: dict, schema_name: str) -> tuple[bool, list]:
    """
    Validate data against a JSON schema.

    Args:
        data: Data to validate
        schema_name: Name of schema ('person', 'address', 'financial', 'pix')

    Returns:
        Tuple of (is_valid, errors)
    """
    import json
    import os
    from pathlib import Path

    try:
        import jsonschema
    except ImportError:
        return False, [{"message": "jsonschema library not installed"}]

    # Get schema file path
    schema_path = Path(__file__).parent.parent.parent.parent / "schemas" / f"{schema_name}.json"

    if not schema_path.exists():
        return False, [{"message": f"Schema file not found: {schema_name}.json"}]

    try:
        with open(schema_path) as f:
            schema = json.load(f)

        jsonschema.validate(data, schema)
        return True, []

    except jsonschema.ValidationError as e:
        return False, [{"message": str(e), "path": list(e.path)}]
    except Exception as e:
        return False, [{"message": f"Validation error: {e!s}"}]


def get_schema_info() -> dict:
    """Get information about available schemas and models."""
    return {
        "version": __version__,
        "schemas": {
            "person": {
                "file": "person.json",
                "models": ["Person", "NaturalPerson", "LegalPerson"],
                "description": "Person schemas following ISO 20022",
            },
            "address": {
                "file": "address.json",
                "models": ["Address"],
                "description": "Address schemas following ISO 19160",
            },
            "financial": {
                "file": "financial.json",
                "models": ["FinancialInstitution", "BankAccount", "BIC", "IBAN", "LEI"],
                "description": "Financial schemas with international standards",
            },
            "pix": {
                "file": "pix.json",
                "models": ["PIXKey", "PIXTransaction", "PIXQRCode"],
                "description": "PIX payment system schemas",
            },
        },
        "features": [
            "JSON Schema validation",
            "Type hints throughout",
            "ORM-ready structure",
            "Multiple contact support",
            "International standards compliance",
            "Country-specific validation",
        ],
    }
