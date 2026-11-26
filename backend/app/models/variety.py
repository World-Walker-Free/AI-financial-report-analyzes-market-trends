"""品种字典表。"""
from sqlalchemy import Column, String

from ..database import Base


class Variety(Base):
    __tablename__ = "t_variety"

    code = Column(String(16), primary_key=True, comment="标准品种代码，如 RB")
    name = Column(String(32), nullable=False, comment="品种中文名")
    exchange = Column(String(16), nullable=True, comment="交易所")
    main_contract = Column(String(16), nullable=True, comment="主力合约，如 RB2405")
