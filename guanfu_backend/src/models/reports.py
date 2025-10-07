import uuid
from typing import Optional

from sqlalchemy import BigInteger, Boolean, Column, String, Text
from sqlmodel import Field, SQLModel

from .base import BaseCRUDModel, TimestampModel


def generate_uuid_str():
    """Generates a string representation of a UUID4."""
    return str(uuid.uuid4())


class ReportBase(SQLModel):
    """Base class for Report with common fields"""

    location_id: str = Field(max_length=255)
    name: str = Field(max_length=255)
    location_type: str = Field(max_length=255)
    reason: str = Field(sa_column=Column(Text, nullable=False))
    notes: Optional[str] = Field(default=None, sa_column=Column(Text))
    status: bool = Field(sa_column=Column(Boolean, nullable=False))


class Report(ReportBase, TimestampModel, BaseCRUDModel, table=True):
    __tablename__ = "reports"

    id: str = Field(
        default_factory=generate_uuid_str,
        sa_column=Column(String, primary_key=True, default=generate_uuid_str),
    )
