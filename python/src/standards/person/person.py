"""
Person models following ISO 20022 standards with dict-based validation dispatch.

This module provides comprehensive person modeling for both natural
and legal persons using optimized validation patterns.
"""

from abc import abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
from enum import Enum

from ..core.base import Auditable, BaseModel, Country, Prioritizable, ValidationError


class PersonType(Enum):
    """Types of persons following ISO 20022."""

    NATURAL = "natural"  # Individual person
    LEGAL = "legal"  # Organization, company, etc.


class PersonStatus(Enum):
    """Person status for lifecycle management."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DECEASED = "deceased"  # For natural persons
    DISSOLVED = "dissolved"  # For legal persons


class DocumentType(Enum):
    """Types of identification documents."""

    PASSPORT = "passport"
    NATIONAL_ID = "national_id"
    DRIVERS_LICENSE = "drivers_license"
    TAX_ID = "tax_id"
    SOCIAL_SECURITY = "social_security"
    BIRTH_CERTIFICATE = "birth_certificate"
    OTHER = "other"


@dataclass
class IdentificationDocument(BaseModel):
    """Identification document information."""

    document_type: DocumentType | None = None
    document_number: str | None = None
    issuing_country: Country | None = None
    issuing_authority: str | None = None
    issue_date: date | None = None
    expiry_date: date | None = None
    is_primary: bool = False

    def validate(self) -> None:
        """Validate identification document."""
        if not self.document_number:
            raise ValidationError("Document number is required", field="document_number")

        if self.expiry_date and self.issue_date:
            if self.expiry_date <= self.issue_date:
                raise ValidationError("Expiry date must be after issue date")

    def is_expired(self) -> bool:
        """Check if document is expired."""
        if not self.expiry_date:
            return False
        return date.today() > self.expiry_date


@dataclass
class Person(BaseModel, Prioritizable, Auditable):
    """
    Abstract base class for all persons (natural and legal).

    Follows ISO 20022 Party identification standards and provides
    common functionality using dict-based validation dispatch.
    """

    # Basic identification
    name: str
    person_type: PersonType
    status: PersonStatus = PersonStatus.ACTIVE

    # Tax identification
    tax_id: str | None = None
    tax_country: Country | None = None

    # Contact and address references (managed separately)
    contact_ids: list[str] = field(default_factory=list)
    address_ids: list[str] = field(default_factory=list)

    # Identification documents
    identification_documents: list[IdentificationDocument] = field(default_factory=list)

    # Nationality and residence
    nationality: Country | None = None
    country_of_residence: Country | None = None

    # Registration date
    registration_date: date | None = None

    # Validation dispatch table using dict instead of if/elif
    _VALIDATION_RULES: dict[str, Callable[["Person"], None]] = field(default_factory=dict)

    def validate(self) -> None:
        """Validate person data using dict-based dispatch."""
        # Basic validation
        if not self.name or not self.name.strip():
            raise ValidationError("Name is required", field="name")

        # Tax ID validation - basic check only (detailed validation via validation system)
        if self.tax_id and not self.tax_id.strip():
            raise ValidationError("Tax ID cannot be empty", field="tax_id", code="INVALID_TAX_ID")

        # Validate documents
        for doc in self.identification_documents:
            doc.validate()

        # Person type specific validation using dispatch
        validator = self._VALIDATION_RULES.get(self.person_type.value)
        if validator:
            validator(self)

    def get_primary_identifier(self) -> str | None:
        """Get the primary identifier for this person."""
        return self.tax_id or self.external_id if hasattr(self, "external_id") else None

    def add_identification_document(
        self,
        document_type: DocumentType,
        document_number: str,
        issuing_country: Country | None = None,
        set_as_primary: bool = False,
    ) -> IdentificationDocument:
        """Add an identification document."""
        doc = IdentificationDocument(
            document_type=document_type,
            document_number=document_number,
            issuing_country=issuing_country,
            is_primary=set_as_primary,
        )

        if set_as_primary:
            # Remove primary flag from other documents
            for existing_doc in self.identification_documents:
                existing_doc.is_primary = False

        # If this is the first document, make it primary
        if not self.identification_documents:
            doc.is_primary = True

        self.identification_documents.append(doc)
        return doc

    def get_primary_document(self) -> IdentificationDocument | None:
        """Get the primary identification document."""
        # Use next() with generator for efficiency instead of loop
        return next(
            (doc for doc in self.identification_documents if doc.is_primary),
            self.identification_documents[0] if self.identification_documents else None,
        )

    @abstractmethod
    def get_display_name(self) -> str:
        """Get display name for this person."""


@dataclass
class NaturalPerson(Person):
    """
    Natural person (individual) following ISO 20022 standards.

    Represents an individual human being with personal attributes.
    """

    person_type: PersonType = field(default=PersonType.NATURAL, init=False)

    # Personal information
    first_name: str | None = None
    middle_name: str | None = None
    last_name: str | None = None
    birth_date: date | None = None
    birth_place: str | None = None
    birth_country: Country | None = None

    # Family information
    mother_name: str | None = None
    father_name: str | None = None

    # Professional information
    occupation: str | None = None
    employer: str | None = None

    def validate(self) -> None:
        """Validate natural person data."""
        super().validate()

        # Validate birth date
        if self.birth_date and self.birth_date > date.today():
            raise ValidationError("Birth date cannot be in the future", field="birth_date")

        # Auto-generate full name if components are provided
        if self.first_name and self.last_name and not self.name:
            name_parts = [self.first_name]
            if self.middle_name:
                name_parts.append(self.middle_name)
            name_parts.append(self.last_name)
            self.name = " ".join(name_parts)

    def get_display_name(self) -> str:
        """Get display name for natural person."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.name

    def get_age(self) -> int | None:
        """Calculate age from birth date."""
        if not self.birth_date:
            return None

        today = date.today()
        age = today.year - self.birth_date.year

        # Adjust if birthday hasn't occurred this year
        if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
            age -= 1

        return age


@dataclass
class LegalPerson(Person):
    """
    Legal person (organization) following ISO 20022 standards.

    Represents a legal entity such as a company or organization.
    """

    person_type: PersonType = field(default=PersonType.LEGAL, init=False)

    # Business information
    legal_name: str | None = None  # Official registered name
    trade_name: str | None = None  # Doing business as (DBA) name
    legal_form: str | None = None  # e.g., "LLC", "Corporation", "Partnership"

    # Registration information
    registration_number: str | None = None
    registration_country: Country | None = None
    registration_date: date | None = None

    # Business details
    industry_code: str | None = None  # NAICS, SIC, or other industry classification
    business_description: str | None = None
    website: str | None = None

    # Key personnel references
    authorized_representative_ids: list[str] = field(default_factory=list)

    def validate(self) -> None:
        """Validate legal person data."""
        super().validate()

        # Legal name should be provided for legal persons
        if not self.legal_name:
            self.legal_name = self.name

    def get_display_name(self) -> str:
        """Get display name for legal person."""
        return self.trade_name or self.legal_name or self.name


# Register validation rules using dict dispatch
Person._VALIDATION_RULES = {
    PersonType.NATURAL.value: lambda p: None,  # Natural person validation handled in subclass
    PersonType.LEGAL.value: lambda p: None,  # Legal person validation handled in subclass
}


# Factory function using dict dispatch
def create_person(person_type: PersonType, name: str, **kwargs) -> Person:
    """Factory function to create appropriate person type using dict dispatch."""

    person_creators = {
        PersonType.NATURAL: lambda: NaturalPerson(name=name, **kwargs),
        PersonType.LEGAL: lambda: LegalPerson(name=name, **kwargs),
    }

    creator = person_creators.get(person_type)
    if not creator:
        raise ValueError(f"Unknown person type: {person_type}")

    return creator()
