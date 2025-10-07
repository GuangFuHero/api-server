import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy import Column, Enum, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel

from .base import BaseCRUDModel, TimestampModel


def generate_uuid_str():
    """Generates a string representation of a UUID4."""
    return str(uuid.uuid4())


class ShelterBase(SQLModel):
    """Base class for Shelter with common fields"""

    name: str = Field(max_length=255)
    location: str = Field(max_length=255)
    phone: str = Field(max_length=50)
    link: Optional[str] = Field(default=None, max_length=500)
    status: str = Field(max_length=255)
    capacity: Optional[int] = Field(default=None)
    current_occupancy: Optional[int] = Field(default=None)
    available_spaces: Optional[int] = Field(default=None)
    facilities: Optional[List[str]] = Field(default=None, sa_column=Column(JSONB))
    contact_person: Optional[str] = Field(default=None, max_length=255)
    notes: Optional[str] = Field(default=None, sa_column=Column(Text))
    coordinates: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))
    opening_hours: Optional[str] = Field(default=None, max_length=255)


class Shelter(ShelterBase, TimestampModel, BaseCRUDModel, table=True):
    __tablename__ = "shelters"

    id: str = Field(
        default_factory=generate_uuid_str,
        sa_column=Column(String, primary_key=True, default=generate_uuid_str),
    )
