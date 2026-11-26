"""机构表。"""
from sqlalchemy import Column, DateTime, Integer, String, func

from ..database import Base


class Institution(Base):
    __tablename__ = "t_institution"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), unique=True, nullable=False, comment="机构全称")
    short_name = Column(String(32), nullable=True, comment="简称")
    created_at = Column(DateTime, server_default=func.now())
