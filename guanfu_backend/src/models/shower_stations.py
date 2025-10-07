import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy import Boolean, Column, Enum, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel

from .base import BaseCRUDModel, TimestampModel


def generate_uuid_str():
    """Generates a string representation of a UUID4."""
    return str(uuid.uuid4())


class ShowerStationBase(SQLModel):
    """Base class for ShowerStation with common fields"""

    name: str = Field(max_length=255)
    address: str = Field(max_length=500)
    facility_type: str = Field(max_length=255)
    time_slots: str = Field(max_length=255)
    available_period: str = Field(max_length=255)
    is_free: bool = Field(sa_column=Column(Boolean, nullable=False))
    status: str = Field(max_length=255)
    requires_appointment: bool = Field(sa_column=Column(Boolean, nullable=False))
    coordinates: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))
    phone: Optional[str] = Field(default=None, max_length=50)
    gender_schedule: Optional[Dict[str, Any]] = Field(
        default=None, sa_column=Column(JSONB)
    )
    capacity: Optional[int] = Field(default=None)
    pricing: Optional[str] = Field(default=None, max_length=255)
    notes: Optional[str] = Field(default=None, sa_column=Column(Text))
    info_source: Optional[str] = Field(default=None, max_length=255)
    facilities: Optional[List[str]] = Field(default=None, sa_column=Column(JSONB))
    distance_to_guangfu: Optional[str] = Field(default=None, max_length=255)
    contact_method: Optional[str] = Field(default=None, max_length=255)


class ShowerStation(ShowerStationBase, TimestampModel, BaseCRUDModel, table=True):
    __tablename__ = "shower_stations"

    id: str = Field(
        default_factory=generate_uuid_str,
        sa_column=Column(String, primary_key=True, default=generate_uuid_str),
    )
