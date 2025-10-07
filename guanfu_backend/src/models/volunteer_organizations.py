import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.sql import func
from sqlmodel import Field, SQLModel

from .base import BaseCRUDModel, TimestampModel


def generate_uuid_str():
    """Generates a string representation of a UUID4."""
    return str(uuid.uuid4())


class VolunteerOrganizationBase(SQLModel):
    """Base class for VolunteerOrganization with common fields"""

    registration_status: Optional[str] = Field(default=None, max_length=255)
    organization_nature: Optional[str] = Field(default=None, max_length=255)
    organization_name: str = Field(max_length=255)
    coordinator: Optional[str] = Field(default=None, max_length=255)
    contact_info: Optional[str] = Field(default=None, max_length=500)
    registration_method: Optional[str] = Field(default=None, max_length=255)
    service_content: Optional[str] = Field(default=None, sa_column=Column(Text))
    meeting_info: Optional[str] = Field(default=None, sa_column=Column(Text))
    notes: Optional[str] = Field(default=None, sa_column=Column(Text))
    image_url: Optional[str] = Field(default=None, max_length=500)


class VolunteerOrganization(
    VolunteerOrganizationBase, TimestampModel, BaseCRUDModel, table=True
):
    __tablename__ = "volunteer_organizations"

    id: str = Field(
        default_factory=generate_uuid_str,
        sa_column=Column(String, primary_key=True, default=generate_uuid_str),
    )
    # last_updated field removed - using updated_at from TimestampModel instead
