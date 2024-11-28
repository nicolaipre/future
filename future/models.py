# from sqlalchemy import INTEGER as Integer, Column, ForeignKey, String, Boolean, TIMESTAMP as Timestamp, select, Text
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import DeclarativeBase
from dataclasses import dataclass, asdict


class Model(DeclarativeBase):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)


class User(Model):
    __tablename__ = "users"
    name = Column(String)
    email = Column(String)
    password = Column(String)
