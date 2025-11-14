"""
Company model for Brazilian legal entities (CNPJ).

This module provides a simplified company model specifically for Brazilian
legal entities, avoiding the complexity of the full Person model hierarchy.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from .address.address import Address
from .core.base import Country


@dataclass
class Company:
    """
    Simplified company model for Brazilian legal entities.
    
    This model focuses on the essential company information needed
    for CNPJ lookups and business operations.
    """
    
    # Basic identification
    cnpj: str                                    # Formatted CNPJ
    legal_name: str                             # Razão social
    trade_name: Optional[str] = None            # Nome fantasia
    
    # Status and registration
    status: str = "UNKNOWN"                     # Company status
    registration_date: Optional[str] = None     # Data de início de atividade
    
    # Address information
    address: Optional[Address] = None           # Complete address
    
    # Contact information
    phone: Optional[str] = None                 # Formatted phone number
    email: Optional[str] = None                 # Email address
    
    # Business information
    primary_activity: Optional[str] = None      # CNAE principal
    company_size: Optional[str] = None          # Porte da empresa
    share_capital: Optional[float] = None       # Capital social
    
    # Legal information
    legal_nature: Optional[str] = None          # Natureza jurídica
    
    # Metadata
    country: Country = field(default_factory=lambda: Country(
        code="BR", alpha3="BRA", numeric="076", name="Brazil", local_name="Brasil"
    ))
    is_verified: bool = True
    verification_source: str = "unknown"
    last_updated: Optional[datetime] = None
    
    def get_display_name(self) -> str:
        """Get the best display name for the company."""
        return self.trade_name or self.legal_name
    
    def is_active(self) -> bool:
        """Check if the company is active."""
        return self.status.upper() in ["ATIVA", "ACTIVE"]
    
    def mark_as_verified(self, source: str) -> None:
        """Mark the company as verified from a specific source."""
        self.is_verified = True
        self.verification_source = source
        self.last_updated = datetime.now()
    
    def get_full_address(self) -> Optional[str]:
        """Get the full formatted address if available."""
        if self.address:
            return self.address.get_display_name()
        return None
    
    def to_dict(self) -> dict:
        """Convert company to dictionary representation."""
        result = {
            "cnpj": self.cnpj,
            "legal_name": self.legal_name,
            "trade_name": self.trade_name,
            "status": self.status,
            "registration_date": self.registration_date,
            "phone": self.phone,
            "email": self.email,
            "primary_activity": self.primary_activity,
            "company_size": self.company_size,
            "share_capital": self.share_capital,
            "legal_nature": self.legal_nature,
            "country": self.country.name if self.country else None,
            "is_verified": self.is_verified,
            "verification_source": self.verification_source,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
        }
        
        if self.address:
            result["address"] = {
                "street": self.address.street_name,
                "neighborhood": self.address.neighborhood,
                "city": self.address.locality,
                "state": self.address.administrative_area_1,
                "postal_code": self.address.postal_code,
                "country": self.address.country.name if self.address.country else None,
            }
        
        return result
