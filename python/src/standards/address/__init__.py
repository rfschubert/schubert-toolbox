"""
Address standards module.

This module provides ISO 19160 compliant address classes based on the
schemas/address.json schema definition.
"""

from .address import (
    Address,
    Country,
    GeographicCoordinates,
    AddressComponent,
    AddressType,
    AddressStatus
)

__version__ = "1.0.0"
__author__ = "Schubert Toolbox Team"

__all__ = [
    "Address",
    "Country",
    "GeographicCoordinates",
    "AddressComponent",
    "AddressType",
    "AddressStatus"
]
