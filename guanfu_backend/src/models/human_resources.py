import time
import uuid
from typing import List, Optional

from sqlalchemy import BigInteger, Boolean, Column, Enum, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel

from .base import BaseCRUDModel, TimestampModel


def generate_uuid_str():
    """Generates a string representation of a UUID4."""
    return str(uuid.uuid4())


class HumanResourceBase(SQLModel):
    """Base class for HumanResource with common fields"""

    org: str = Field(max_length=255)
    address: str = Field(max_length=500)
    phone: str = Field(max_length=50)
    status: str = Field(max_length=255)
    is_completed: bool = Field(sa_column=Column(Boolean, nullable=False))
    role_name: str = Field(max_length=255)
    role_type: str = Field(max_length=255)
    headcount_need: int = Field()
    headcount_got: int = Field()
    role_status: str = Field(max_length=255)
    has_medical: Optional[bool] = Field(default=None, sa_column=Column(Boolean))
    skills: Optional[List[str]] = Field(default=None, sa_column=Column(JSONB))
    certifications: Optional[List[str]] = Field(default=None, sa_column=Column(JSONB))
    experience_level: Optional[str] = Field(default=None, max_length=255)
    language_requirements: Optional[List[str]] = Field(
        default=None, sa_column=Column(JSONB)
    )
    headcount_unit: Optional[str] = Field(default=None, max_length=255)
    shift_start_ts: Optional[int] = Field(default=None, sa_column=Column(BigInteger))
    shift_end_ts: Optional[int] = Field(default=None, sa_column=Column(BigInteger))
    shift_notes: Optional[str] = Field(default=None, sa_column=Column(Text))
    assignment_timestamp: Optional[int] = Field(
        default=None, sa_column=Column(BigInteger)
    )
    assignment_count: Optional[int] = Field(default=None)
    assignment_notes: Optional[str] = Field(default=None, sa_column=Column(Text))
    pii_date: int = Field(
        default_factory=lambda: int(time.time()),
        sa_column=Column(BigInteger, nullable=False, default=lambda: int(time.time())),
    )
    valid_pin: Optional[str] = Field(default=None, max_length=255)


class HumanResource(HumanResourceBase, TimestampModel, BaseCRUDModel, table=True):
    __tablename__ = "human_resources"

    id: str = Field(
        default_factory=generate_uuid_str,
        sa_column=Column(String, primary_key=True, default=generate_uuid_str),
    )
