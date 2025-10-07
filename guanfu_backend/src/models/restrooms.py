import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy import BigInteger, Boolean, Column, Enum, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel

from ..enums import GeneralStatusEnum, RestroomFacilityTypeEnum
from .base import BaseCRUDModel, TimestampModel


def generate_uuid_str():
    """Generates a string representation of a UUID4."""
    return str(uuid.uuid4())


class RestroomBase(SQLModel):
    """Base class for Restroom with common fields"""

    name: str = Field(max_length=255)
    address: str = Field(max_length=500)
    facility_type: RestroomFacilityTypeEnum = Field(
        sa_column=Column(Enum(RestroomFacilityTypeEnum), nullable=False)
    )
    opening_hours: str = Field(max_length=255)
    is_free: bool = Field(sa_column=Column(Boolean, nullable=False))
    has_water: bool = Field(sa_column=Column(Boolean, nullable=False))
    has_lighting: bool = Field(sa_column=Column(Boolean, nullable=False))
    status: GeneralStatusEnum = Field(
        sa_column=Column(Enum(GeneralStatusEnum), nullable=False)
    )
    coordinates: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))
    phone: Optional[str] = Field(default=None, max_length=50)
    male_units: Optional[int] = Field(default=None)
    female_units: Optional[int] = Field(default=None)
    unisex_units: Optional[int] = Field(default=None)
    accessible_units: Optional[int] = Field(default=None)
    cleanliness: Optional[str] = Field(default=None, max_length=255)
    last_cleaned: Optional[int] = Field(default=None, sa_column=Column(BigInteger))
    facilities: Optional[List[str]] = Field(default=None, sa_column=Column(JSONB))
    distance_to_disaster_area: Optional[str] = Field(default=None, max_length=255)
    notes: Optional[str] = Field(default=None, sa_column=Column(Text))
    info_source: Optional[str] = Field(default=None, max_length=255)


class Restroom(RestroomBase, TimestampModel, BaseCRUDModel, table=True):
    __tablename__ = "restrooms"

    id: str = Field(
        default_factory=generate_uuid_str,
        sa_column=Column(String, primary_key=True, default=generate_uuid_str),
    )
