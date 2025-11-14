"""
ISO 19160 compliant address classes.

This module implements address data structures based on the schemas/address.json
schema definition, providing comprehensive international address support.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from ..core.base import BaseModel


class AddressType(Enum):
    """Address type enumeration."""
    RESIDENTIAL = "residential"
    BUSINESS = "business"
    MAILING = "mailing"
    BILLING = "billing"
    SHIPPING = "shipping"
    TEMPORARY = "temporary"
    PREVIOUS = "previous"


class AddressStatus(Enum):
    """Address status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING_VERIFICATION = "pending_verification"
    VERIFIED = "verified"
    INVALID = "invalid"


@dataclass
class Country(BaseModel):
    """ISO 3166 country information."""
    
    code: Optional[str] = None  # ISO 3166-1 alpha-2
    alpha3: Optional[str] = None  # ISO 3166-1 alpha-3
    numeric: Optional[str] = None  # ISO 3166-1 numeric
    name: Optional[str] = None  # English name
    local_name: Optional[str] = None  # Local language name
    
    def validate(self) -> None:
        """Validate country data."""
        super().validate()
        
        if self.code and len(self.code) != 2:
            raise ValueError("Country code must be 2 characters")
        
        if self.alpha3 and len(self.alpha3) != 3:
            raise ValueError("Alpha3 code must be 3 characters")
        
        if self.numeric and (len(self.numeric) != 3 or not self.numeric.isdigit()):
            raise ValueError("Numeric code must be 3 digits")


@dataclass
class GeographicCoordinates(BaseModel):
    """Geographic coordinates with accuracy information."""

    latitude: Optional[float] = None
    longitude: Optional[float] = None
    accuracy: Optional[str] = None  # rooftop, street, city, etc.
    source: Optional[str] = None  # google, manual, etc.
    
    def validate(self) -> None:
        """Validate coordinate data."""
        super().validate()

        if self.latitude is not None and not (-90 <= self.latitude <= 90):
            raise ValueError("Latitude must be between -90 and 90")

        if self.longitude is not None and not (-180 <= self.longitude <= 180):
            raise ValueError("Longitude must be between -180 and 180")


@dataclass
class AddressComponent(BaseModel):
    """Flexible address component for country-specific formats."""

    type: Optional[str] = None  # street_number, route, locality, etc.
    value: Optional[str] = None
    short_name: Optional[str] = None
    long_name: Optional[str] = None
    
    def validate(self) -> None:
        """Validate address component data."""
        super().validate()

        if self.type is not None and (not self.type or not self.type.strip()):
            raise ValueError("Component type cannot be empty")

        if self.value is not None and (not self.value or not self.value.strip()):
            raise ValueError("Component value cannot be empty")


@dataclass
class Address(BaseModel):
    """
    ISO 19160 compliant address with international support.

    Based on schemas/address.json schema definition.
    """

    # Street information
    street_number: Optional[str] = None
    street_name: Optional[str] = None
    street_type: Optional[str] = None  # Street, Avenue, Road, etc.
    unit: Optional[str] = None  # Apartment, suite, unit number
    building: Optional[str] = None  # Building name or number
    floor: Optional[str] = None  # Floor number

    # Geographic areas
    neighborhood: Optional[str] = None  # District, suburb, neighborhood
    locality: Optional[str] = None  # City, town, village
    sublocality: Optional[str] = None  # Sub-city area
    administrative_area_1: Optional[str] = None  # State, province, region
    administrative_area_2: Optional[str] = None  # County, district
    administrative_area_3: Optional[str] = None  # Sub-district

    # Postal information
    postal_code: Optional[str] = None
    postal_code_suffix: Optional[str] = None

    # Country information
    country: Optional[Country] = None

    # Address classification
    address_type: AddressType = AddressType.RESIDENTIAL
    status: AddressStatus = AddressStatus.ACTIVE

    # Geographic coordinates
    coordinates: Optional[GeographicCoordinates] = None

    # Flexible components for country-specific formats
    components: List[AddressComponent] = field(default_factory=list)

    # Formatted addresses
    formatted_address: Optional[str] = None
    formatted_address_local: Optional[str] = None

    # Verification information
    is_verified: bool = False
    verified_at: Optional[datetime] = None
    verification_source: Optional[str] = None

    # Priority and selection
    is_primary: bool = False
    is_default: bool = False
    priority: int = 0

    def validate(self) -> None:
        """
        Validate address data according to schema requirements.

        At least one of street_name, locality, or formatted_address must be present.
        """
        super().validate()

        # Schema anyOf requirement: at least one of these must be present
        if not any([self.street_name, self.locality, self.formatted_address]):
            raise ValueError(
                "Address must have at least one of: street_name, locality, or formatted_address"
            )

        # Validate nested objects
        if self.country:
            self.country.validate()

        if self.coordinates:
            self.coordinates.validate()

        for component in self.components:
            component.validate()

    def get_full_street_address(self) -> Optional[str]:
        """Get complete street address combining number, name, and type."""
        parts = []

        if self.street_number:
            parts.append(self.street_number)

        if self.street_name:
            parts.append(self.street_name)

        if self.street_type:
            parts.append(self.street_type)

        return " ".join(parts) if parts else None

    def get_administrative_hierarchy(self) -> List[str]:
        """Get administrative areas in hierarchical order."""
        areas = []

        for area in [self.administrative_area_3, self.administrative_area_2, self.administrative_area_1]:
            if area:
                areas.append(area)

        return areas

    def get_display_name(self) -> str:
        """Get a human-readable display name for the address."""
        if self.formatted_address:
            return self.formatted_address

        parts = []

        # Street address
        street = self.get_full_street_address()
        if street:
            parts.append(street)

        # Unit/Building info
        if self.unit:
            parts.append(f"Unit {self.unit}")
        elif self.building:
            parts.append(self.building)

        # Locality
        if self.locality:
            parts.append(self.locality)

        # Administrative area 1 (state/province)
        if self.administrative_area_1:
            parts.append(self.administrative_area_1)

        # Country
        if self.country and self.country.name:
            parts.append(self.country.name)

        return ", ".join(parts) if parts else "Unknown Address"

    def is_complete(self) -> bool:
        """Check if address has sufficient information for delivery."""
        # Must have either formatted address or structured components
        if self.formatted_address:
            return True

        # For structured address, need at least street and locality
        return bool(self.street_name and self.locality)

    def get_component_by_type(self, component_type: str) -> Optional[AddressComponent]:
        """Get address component by type."""
        for component in self.components:
            if component.type == component_type:
                return component
        return None

    def add_component(self, component_type: str, value: str,
                     short_name: Optional[str] = None,
                     long_name: Optional[str] = None) -> None:
        """Add or update an address component."""
        # Remove existing component of same type
        self.components = [c for c in self.components if c.type != component_type]

        # Add new component
        component = AddressComponent(
            type=component_type,
            value=value,
            short_name=short_name,
            long_name=long_name
        )
        self.components.append(component)

    def mark_as_verified(self, source: Optional[str] = None) -> None:
        """Mark address as verified."""
        self.is_verified = True
        self.verified_at = datetime.utcnow()
        self.verification_source = source
        self.status = AddressStatus.VERIFIED

    def to_dict(self) -> Dict[str, Any]:
        """Convert address to dictionary representation."""
        result = super().to_dict()

        # Convert enums to values
        result['address_type'] = self.address_type.value
        result['status'] = self.status.value

        # Convert nested objects
        if self.country:
            result['country'] = self.country.to_dict()

        if self.coordinates:
            result['coordinates'] = self.coordinates.to_dict()

        result['components'] = [c.to_dict() for c in self.components]

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Address':
        """Create Address from dictionary representation."""
        # Convert enum fields
        if 'address_type' in data:
            data['address_type'] = AddressType(data['address_type'])

        if 'status' in data:
            data['status'] = AddressStatus(data['status'])

        # Convert nested objects
        if 'country' in data and data['country']:
            data['country'] = Country.from_dict(data['country'])

        if 'coordinates' in data and data['coordinates']:
            data['coordinates'] = GeographicCoordinates.from_dict(data['coordinates'])

        if 'components' in data:
            data['components'] = [AddressComponent.from_dict(c) for c in data['components']]

        return cls(**data)
