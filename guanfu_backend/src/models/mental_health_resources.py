import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy import Boolean, Column, Enum, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel

from ..enums import GeneralStatusEnum, MentalHealthDurationEnum, MentalHealthFormatEnum
from .base import BaseCRUDModel, TimestampModel


def generate_uuid_str():
    """Generates a string representation of a UUID4."""
    return str(uuid.uuid4())


class MentalHealthResourceBase(SQLModel):
    """Base class for MentalHealthResource with common fields"""

    duration_type: MentalHealthDurationEnum = Field(
        sa_column=Column(Enum(MentalHealthDurationEnum), nullable=False)
    )
    name: str = Field(max_length=255)
    service_format: MentalHealthFormatEnum = Field(
        sa_column=Column(Enum(MentalHealthFormatEnum), nullable=False)
    )
    service_hours: str = Field(max_length=255)
    contact_info: str = Field(max_length=500)
    is_free: bool = Field(sa_column=Column(Boolean, nullable=False))
    status: GeneralStatusEnum = Field(
        sa_column=Column(Enum(GeneralStatusEnum), nullable=False)
    )
    emergency_support: bool = Field(sa_column=Column(Boolean, nullable=False))
    website_url: Optional[str] = Field(default=None, max_length=500)
    target_audience: Optional[List[str]] = Field(default=None, sa_column=Column(JSONB))
    specialties: Optional[List[str]] = Field(default=None, sa_column=Column(JSONB))
    languages: Optional[List[str]] = Field(default=None, sa_column=Column(JSONB))
    location: Optional[str] = Field(default=None, max_length=255)
    coordinates: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))
    capacity: Optional[int] = Field(default=None)
    waiting_time: Optional[str] = Field(default=None, max_length=255)
    notes: Optional[str] = Field(default=None, sa_column=Column(Text))


class MentalHealthResource(
    MentalHealthResourceBase, TimestampModel, BaseCRUDModel, table=True
):
    __tablename__ = "mental_health_resources"

    id: str = Field(
        default_factory=generate_uuid_str,
        sa_column=Column(String, primary_key=True, default=generate_uuid_str),
    )
