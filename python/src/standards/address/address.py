"""
ISO 19160 compliant address classes.

This module implements address data structures based on the schemas/address.json
schema definition, providing comprehensive international address support.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

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

    code: str | None = None  # ISO 3166-1 alpha-2
    alpha3: str | None = None  # ISO 3166-1 alpha-3
    numeric: str | None = None  # ISO 3166-1 numeric
    name: str | None = None  # English name
    local_name: str | None = None  # Local language name

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

    latitude: float | None = None
    longitude: float | None = None
    accuracy: str | None = None  # rooftop, street, city, etc.
    source: str | None = None  # google, manual, etc.

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

    type: str | None = None  # street_number, route, locality, etc.
    value: str | None = None
    short_name: str | None = None
    long_name: str | None = None

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
    street_number: str | None = None
    street_name: str | None = None
    street_type: str | None = None  # Street, Avenue, Road, etc.
    unit: str | None = None  # Apartment, suite, unit number
    building: str | None = None  # Building name or number
    floor: str | None = None  # Floor number

    # Geographic areas
    neighborhood: str | None = None  # District, suburb, neighborhood
    locality: str | None = None  # City, town, village
    sublocality: str | None = None  # Sub-city area
    administrative_area_1: str | None = None  # State, province, region
    administrative_area_2: str | None = None  # County, district
    administrative_area_3: str | None = None  # Sub-district

    # Postal information
    postal_code: str | None = None
    postal_code_suffix: str | None = None

    # Country information
    country: Country | None = None

    # Address classification
    address_type: AddressType = AddressType.RESIDENTIAL
    status: AddressStatus = AddressStatus.ACTIVE

    # Geographic coordinates
    coordinates: GeographicCoordinates | None = None

    # Flexible components for country-specific formats
    components: list[AddressComponent] = field(default_factory=list)

    # Formatted addresses
    formatted_address: str | None = None
    formatted_address_local: str | None = None

    # Verification information
    is_verified: bool = False
    verified_at: datetime | None = None
    verification_source: str | None = None

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

    def get_full_street_address(self) -> str | None:
        """Get complete street address combining number, name, and type."""
        parts = []

        if self.street_number:
            parts.append(self.street_number)

        if self.street_name:
            parts.append(self.street_name)

        if self.street_type:
            parts.append(self.street_type)

        return " ".join(parts) if parts else None

    def get_administrative_hierarchy(self) -> list[str]:
        """Get administrative areas in hierarchical order."""
        areas = []

        for area in [
            self.administrative_area_3,
            self.administrative_area_2,
            self.administrative_area_1,
        ]:
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

    def get_component_by_type(self, component_type: str) -> AddressComponent | None:
        """Get address component by type."""
        for component in self.components:
            if component.type == component_type:
                return component
        return None

    def add_component(
        self,
        component_type: str,
        value: str,
        short_name: str | None = None,
        long_name: str | None = None,
    ) -> None:
        """Add or update an address component."""
        # Remove existing component of same type
        self.components = [c for c in self.components if c.type != component_type]

        # Add new component
        component = AddressComponent(
            type=component_type, value=value, short_name=short_name, long_name=long_name
        )
        self.components.append(component)

    def mark_as_verified(self, source: str | None = None) -> None:
        """Mark address as verified."""
        self.is_verified = True
        self.verified_at = datetime.utcnow()
        self.verification_source = source
        self.status = AddressStatus.VERIFIED

    def to_dict(self) -> dict[str, Any]:
        """Convert address to dictionary representation."""
        result = super().to_dict()

        # Convert enums to values
        result["address_type"] = self.address_type.value
        result["status"] = self.status.value

        # Convert nested objects
        if self.country:
            result["country"] = self.country.to_dict()

        if self.coordinates:
            result["coordinates"] = self.coordinates.to_dict()

        result["components"] = [c.to_dict() for c in self.components]

        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Address":
        """Create Address from dictionary representation."""
        # Convert enum fields
        if "address_type" in data:
            data["address_type"] = AddressType(data["address_type"])

        if "status" in data:
            data["status"] = AddressStatus(data["status"])

        # Convert nested objects
        if data.get("country"):
            data["country"] = Country.from_dict(data["country"])

        if data.get("coordinates"):
            data["coordinates"] = GeographicCoordinates.from_dict(data["coordinates"])

        if "components" in data:
            data["components"] = [AddressComponent.from_dict(c) for c in data["components"]]

        return cls(**data)
