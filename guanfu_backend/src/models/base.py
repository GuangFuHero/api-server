import time
from typing import Optional

from sqlalchemy import Column, Integer, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func, tuple_
from sqlmodel import Field, SQLModel


def current_timestamp_int():
    """Returns the current Unix timestamp as an integer."""
    return int(time.time())


class TimestampModel(SQLModel):
    """"""

    created_at: Optional[int] = Field(
        default=None,
        sa_column_kwargs={
            "server_default": func.extract("epoch", func.current_timestamp()),
        },
    )
    updated_at: Optional[int] = Field(
        default=None,
        sa_column_kwargs={
            "server_default": func.extract("epoch", func.current_timestamp()),
            "onupdate": func.extract("epoch", func.current_timestamp()),
        },
    )


class BaseCRUDModel(SQLModel):
    """Abstract model with CRUD operations"""

    @classmethod
    async def select_filter(
        cls,
        session: AsyncSession,
        column: tuple,
        filter: tuple,
        order_by: tuple | None = None,
    ):
        statement = select(column).where(filter)
        if order_by:
            statement = statement.order_by(*order_by)
        results = await session.execute(statement)
        return results

    @classmethod
    async def get(cls, session: AsyncSession, primary_key):
        results = await session.get(cls, primary_key)
        return results

    @classmethod
    async def insert_item(cls, session: AsyncSession, insert_value: dict):
        item = cls(**insert_value)
        session.add(item)
        await session.flush()
        return item

    @classmethod
    async def insert_items(cls, session: AsyncSession, insert_value_list: list):
        items_list = []
        for insert_value in insert_value_list:
            item = cls(**insert_value)
            items_list.append(item)

        session.add_all(items_list)
        await session.flush()
        return items_list

    @classmethod
    async def update_item(cls, session: AsyncSession, filter: tuple, update_data: dict):
        statement = update(cls).where(filter).values(update_data)
        await session.execute(statement)

    @classmethod
    async def get_multiple_by_pk(
        cls, session: AsyncSession, primary_columns, primary_keys: list[tuple]
    ):
        stmt = select(cls).where(tuple_(*primary_columns).in_(primary_keys))
        return await session.execute(stmt)
