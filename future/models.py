"""
This is the base Model meant to be used as an interface for other models.
"""

from datetime import datetime

from pydantic import BaseModel, Field
from sqlalchemy import INTEGER as Integer  # , select, Text, Boolean, ForeignKey
from sqlalchemy import TIMESTAMP as Timestamp
from sqlalchemy import Column, String
from sqlalchemy.orm import DeclarativeBase


# https://docs.pydantic.dev/latest/usage/settings/


class Model(BaseModel):
    name: str = Field(default="")


class SQLModel(DeclarativeBase):  # type: ignore
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)


class User(SQLModel):
    __tablename__ = "users"
    name = Column(String)
    email = Column(String)
    password = Column(String)
    created_at = Column(Timestamp, default=datetime.now())
    updated_at = Column(Timestamp, default=datetime.now())
