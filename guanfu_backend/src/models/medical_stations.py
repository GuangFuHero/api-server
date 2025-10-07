import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy import Column, Enum, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel

from ..enums import GeneralStatusEnum, MedicalStationTypeEnum
from .base import BaseCRUDModel, TimestampModel


def generate_uuid_str():
    """Generates a string representation of a UUID4."""
    return str(uuid.uuid4())


class MedicalStationBase(SQLModel):
    """Base class for MedicalStation with common fields"""

    station_type: MedicalStationTypeEnum = Field(
        sa_column=Column(Enum(MedicalStationTypeEnum), nullable=False)
    )
    name: str = Field(max_length=255)
    status: GeneralStatusEnum = Field(
        sa_column=Column(Enum(GeneralStatusEnum), nullable=False)
    )
    location: Optional[str] = Field(default=None, max_length=255)
    detailed_address: Optional[str] = Field(default=None, max_length=500)
    phone: Optional[str] = Field(default=None, max_length=50)
    contact_person: Optional[str] = Field(default=None, max_length=255)
    services: Optional[List[str]] = Field(default=None, sa_column=Column(JSONB))
    operating_hours: Optional[str] = Field(default=None, max_length=255)
    equipment: Optional[List[str]] = Field(default=None, sa_column=Column(JSONB))
    medical_staff: Optional[int] = Field(default=None)
    daily_capacity: Optional[int] = Field(default=None)
    coordinates: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))
    affiliated_organization: Optional[str] = Field(default=None, max_length=255)
    notes: Optional[str] = Field(default=None, sa_column=Column(Text))
    link: Optional[str] = Field(default=None, max_length=500)


class MedicalStation(MedicalStationBase, TimestampModel, BaseCRUDModel, table=True):
    __tablename__ = "medical_stations"

    id: str = Field(
        default_factory=generate_uuid_str,
        sa_column=Column(String, primary_key=True, default=generate_uuid_str),
    )
