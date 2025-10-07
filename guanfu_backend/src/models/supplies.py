import time
import uuid
from typing import Optional

from sqlalchemy import BigInteger, Column, Enum, Integer, String, Text, func
from sqlmodel import Field, Relationship, SQLModel

from .base import BaseCRUDModel


def generate_uuid_str():
    """Generates a string representation of a UUID4."""
    return str(uuid.uuid4())


class SupplyBase(SQLModel):
    """Base class for Supply with common fields"""

    name: Optional[str] = Field(default=None, max_length=255)
    address: Optional[str] = Field(default=None, max_length=500)
    phone: Optional[str] = Field(default=None, max_length=50)
    notes: Optional[str] = Field(default=None, sa_column=Column(Text))
    pii_date: int = Field(
        default_factory=lambda: int(time.time()),
        sa_column=Column(BigInteger, nullable=False, default=lambda: int(time.time())),
    )
    valid_pin: Optional[str] = Field(default=None, max_length=255)
    created_at: int | None = Field(
        sa_column=Column(
            Integer, server_default=func.extract("epoch", func.current_timestamp())
        )
    )
    updated_at: int | None = Field(
        sa_column=Column(
            Integer,
            server_default=func.extract("epoch", func.current_timestamp()),
            onupdate=func.extract("epoch", func.current_timestamp()),
        )
    )


class Supply(SupplyBase, BaseCRUDModel, table=True):
    __tablename__ = "supplies"

    id: str = Field(
        default_factory=generate_uuid_str,
        sa_column=Column(String, primary_key=True, default=generate_uuid_str),
    )
    supply_items: list["SupplyItem"] = Relationship(
        back_populates="supply",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class SupplyItemBase(SQLModel):
    """Base class for SupplyItem with common fields"""

    total_number: int = Field()
    tag: str = Field(max_length=255)
    name: Optional[str] = Field(default=None, max_length=255)
    received_count: Optional[int] = Field(default=None)
    unit: Optional[str] = Field(default=None, max_length=50)


class SupplyItem(SupplyItemBase, BaseCRUDModel, table=True):
    __tablename__ = "supply_items"

    id: str = Field(
        default_factory=generate_uuid_str,
        sa_column=Column(String, primary_key=True, default=generate_uuid_str),
    )
    supply_id: str = Field(foreign_key="supplies.id")
    supply: Optional["Supply"] = Relationship(back_populates="supply_items")
