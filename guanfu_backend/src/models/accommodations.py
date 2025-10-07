import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy import Column, Enum, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel

from .base import BaseCRUDModel, TimestampModel


def generate_uuid_str():
    """Generates a string representation of a UUID4."""
    return str(uuid.uuid4())


class AccommodationBase(SQLModel):
    """Base class for Accommodation with common fields"""

    township: str = Field(max_length=255)
    name: str = Field(max_length=255)
    has_vacancy: str = Field(max_length=255)
    available_period: str = Field(max_length=255)
    contact_info: str = Field(max_length=500)
    address: str = Field(max_length=500)
    pricing: str = Field(max_length=255)
    status: str = Field(max_length=255)
    restrictions: Optional[str] = Field(default=None, max_length=500)
    room_info: Optional[str] = Field(default=None, max_length=500)
    coordinates: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))
    info_source: Optional[str] = Field(default=None, max_length=255)
    notes: Optional[str] = Field(default=None, sa_column=Column(Text))
    capacity: Optional[int] = Field(default=None)
    registration_method: Optional[str] = Field(default=None, max_length=255)
    facilities: Optional[List[str]] = Field(default=None, sa_column=Column(JSONB))
    distance_to_disaster_area: Optional[str] = Field(default=None, max_length=255)


class Accommodation(AccommodationBase, TimestampModel, BaseCRUDModel, table=True):
    __tablename__ = "accommodations"

    id: str = Field(
        default_factory=generate_uuid_str,
        sa_column=Column(String, primary_key=True, default=generate_uuid_str),
    )
