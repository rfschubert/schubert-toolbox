"""
Person models following ISO 20022 standards with dict-based validation dispatch.

This module provides comprehensive person modeling for both natural
and legal persons using optimized validation patterns.
"""

from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import List, Optional, Dict, Any, Callable

from ..core.base import BaseModel, Country, ValidationError, Prioritizable, Auditable


class PersonType(Enum):
    """Types of persons following ISO 20022."""
    NATURAL = "natural"  # Individual person
    LEGAL = "legal"      # Organization, company, etc.


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

    document_type: Optional[DocumentType] = None
    document_number: Optional[str] = None
    issuing_country: Optional[Country] = None
    issuing_authority: Optional[str] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
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
    tax_id: Optional[str] = None
    tax_country: Optional[Country] = None
    
    # Contact and address references (managed separately)
    contact_ids: List[str] = field(default_factory=list)
    address_ids: List[str] = field(default_factory=list)
    
    # Identification documents
    identification_documents: List[IdentificationDocument] = field(default_factory=list)
    
    # Nationality and residence
    nationality: Optional[Country] = None
    country_of_residence: Optional[Country] = None
    
    # Registration date
    registration_date: Optional[date] = None
    
    # Validation dispatch table using dict instead of if/elif
    _VALIDATION_RULES: Dict[str, Callable[['Person'], None]] = field(default_factory=dict)
    
    def validate(self) -> None:
        """Validate person data using dict-based dispatch."""
        # Basic validation
        if not self.name or not self.name.strip():
            raise ValidationError("Name is required", field="name")
        
        # Tax ID validation - basic check only (detailed validation via validation system)
        if self.tax_id and not self.tax_id.strip():
            raise ValidationError(
                "Tax ID cannot be empty",
                field="tax_id",
                code="INVALID_TAX_ID"
            )
        
        # Validate documents
        for doc in self.identification_documents:
            doc.validate()
        
        # Person type specific validation using dispatch
        validator = self._VALIDATION_RULES.get(self.person_type.value)
        if validator:
            validator(self)
    
    def get_primary_identifier(self) -> Optional[str]:
        """Get the primary identifier for this person."""
        return self.tax_id or self.external_id if hasattr(self, 'external_id') else None
    
    def add_identification_document(self, document_type: DocumentType, 
                                  document_number: str, 
                                  issuing_country: Optional[Country] = None,
                                  set_as_primary: bool = False) -> IdentificationDocument:
        """Add an identification document."""
        doc = IdentificationDocument(
            document_type=document_type,
            document_number=document_number,
            issuing_country=issuing_country,
            is_primary=set_as_primary
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
    
    def get_primary_document(self) -> Optional[IdentificationDocument]:
        """Get the primary identification document."""
        # Use next() with generator for efficiency instead of loop
        return next(
            (doc for doc in self.identification_documents if doc.is_primary),
            self.identification_documents[0] if self.identification_documents else None
        )
    
    @abstractmethod
    def get_display_name(self) -> str:
        """Get display name for this person."""
        pass


@dataclass
class NaturalPerson(Person):
    """
    Natural person (individual) following ISO 20022 standards.
    
    Represents an individual human being with personal attributes.
    """
    
    person_type: PersonType = field(default=PersonType.NATURAL, init=False)
    
    # Personal information
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    birth_date: Optional[date] = None
    birth_place: Optional[str] = None
    birth_country: Optional[Country] = None
    
    # Family information
    mother_name: Optional[str] = None
    father_name: Optional[str] = None
    
    # Professional information
    occupation: Optional[str] = None
    employer: Optional[str] = None
    
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
    
    def get_age(self) -> Optional[int]:
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
    legal_name: Optional[str] = None  # Official registered name
    trade_name: Optional[str] = None  # Doing business as (DBA) name
    legal_form: Optional[str] = None  # e.g., "LLC", "Corporation", "Partnership"
    
    # Registration information
    registration_number: Optional[str] = None
    registration_country: Optional[Country] = None
    registration_date: Optional[date] = None
    
    # Business details
    industry_code: Optional[str] = None  # NAICS, SIC, or other industry classification
    business_description: Optional[str] = None
    website: Optional[str] = None
    
    # Key personnel references
    authorized_representative_ids: List[str] = field(default_factory=list)
    
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
    PersonType.LEGAL.value: lambda p: None,    # Legal person validation handled in subclass
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
