"""
Core base classes for Python standards implementation.

This module provides the foundational classes that all other models inherit from,
ensuring consistency and proper JSON schema validation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4


@dataclass
class BaseModel(ABC):
    """
    Abstract base class for all models.

    Provides common functionality like:
    - Unique identification
    - Audit trail (created/updated timestamps)
    - Metadata storage
    - JSON schema validation
    """

    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Post-initialization hook for validation."""
        self.validate()

    @abstractmethod
    def validate(self) -> None:
        """
        Validate the model instance.

        Raises:
            ValidationError: If validation fails
        """

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> dict[str, Any]:
        """Convert the model to a dictionary representation."""
        from dataclasses import asdict

        return asdict(self)

    def to_json(self) -> str:
        """Convert the model to JSON string."""
        import json
        from datetime import date, datetime

        def json_serializer(obj):
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            elif isinstance(obj, Enum):
                return obj.value
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

        return json.dumps(self.to_dict(), default=json_serializer, indent=2)


@dataclass
class Country:
    """
    ISO 3166 compliant country representation.

    Supports both 2-letter and 3-letter country codes,
    numeric codes, and localized names.
    """

    code: str | None = None  # ISO 3166-1 alpha-2 (US, BR, etc.)
    alpha3: str | None = None  # ISO 3166-1 alpha-3 (USA, BRA, etc.)
    numeric: str | None = None  # ISO 3166-1 numeric (840, 076, etc.)
    name: str | None = None  # English name
    local_name: str | None = None  # Localized name

    # Country data mapping using dict instead of multiple if/elif
    _COUNTRY_DATA = {
        "US": {"alpha3": "USA", "numeric": "840", "name": "United States"},
        "BR": {"alpha3": "BRA", "numeric": "076", "name": "Brazil"},
        "CA": {"alpha3": "CAN", "numeric": "124", "name": "Canada"},
        "GB": {"alpha3": "GBR", "numeric": "826", "name": "United Kingdom"},
        "DE": {"alpha3": "DEU", "numeric": "276", "name": "Germany"},
        "FR": {"alpha3": "FRA", "numeric": "250", "name": "France"},
        "JP": {"alpha3": "JPN", "numeric": "392", "name": "Japan"},
        "AU": {"alpha3": "AUS", "numeric": "036", "name": "Australia"},
        "MX": {"alpha3": "MEX", "numeric": "484", "name": "Mexico"},
        "AR": {"alpha3": "ARG", "numeric": "032", "name": "Argentina"},
        "CL": {"alpha3": "CHL", "numeric": "152", "name": "Chile"},
        "CO": {"alpha3": "COL", "numeric": "170", "name": "Colombia"},
        "PE": {"alpha3": "PER", "numeric": "604", "name": "Peru"},
        "UY": {"alpha3": "URY", "numeric": "858", "name": "Uruguay"},
    }

    def __post_init__(self):
        """Auto-populate missing fields using ISO 3166 data."""
        if self.code and not (self.alpha3 or self.numeric or self.name):
            self._populate_from_code()

    def _populate_from_code(self):
        """Populate other fields from the 2-letter code using dict lookup."""
        country_code = self.code.upper()
        data = self._COUNTRY_DATA.get(country_code)

        if data:
            self.alpha3 = data.get("alpha3")
            self.numeric = data.get("numeric")
            self.name = data.get("name")
            self.local_name = data.get("local_name", self.name)


class ValidationError(Exception):
    """
    Custom exception for model validation errors.

    Provides structured error information for better debugging
    and user feedback.
    """

    def __init__(
        self,
        message: str,
        field: str | None = None,
        code: str | None = None,
        details: dict | None = None,
    ):
        self.message = message
        self.field = field
        self.code = code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        """Convert error to dictionary representation."""
        return {
            "message": self.message,
            "field": self.field,
            "code": self.code,
            "details": self.details,
        }


@dataclass
class Prioritizable(ABC):
    """
    Mixin for entities that can have priority or preference ordering.

    Used for addresses, contact information, and other collections
    where one item should be considered primary or default.
    """

    is_primary: bool = False
    is_default: bool = False
    priority: int = 0

    def set_as_primary(self) -> None:
        """Mark this item as primary."""
        self.is_primary = True
        self.is_default = True
        self.priority = 1


@dataclass
class Auditable(ABC):
    """
    Mixin for entities that require audit trail functionality.

    Extends base audit capabilities with additional compliance
    and tracking features.
    """

    created_by: str | None = None
    updated_by: str | None = None
    version: int = 1

    def increment_version(self, updated_by: str | None = None) -> None:
        """
        Increment version and update audit fields.

        Args:
            updated_by: Identifier of the user making the update
        """
        self.version += 1
        self.updated_by = updated_by
        if hasattr(self, "update_timestamp"):
            self.update_timestamp()
