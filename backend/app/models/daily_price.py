"""可选价格表：研报提及价，没有行情源时可为空。"""
from sqlalchemy import Column, Date, Integer, Numeric, String

from ..database import Base


class DailyPrice(Base):
    __tablename__ = "t_daily_price"

    variety_code = Column(String(16), primary_key=True)
    trade_date = Column(Date, primary_key=True)
    close_price = Column(Numeric(12, 2), nullable=True, comment="研报提及的收盘/参考价")
    change_pct = Column(Numeric(6, 2), nullable=True)
    sample_count = Column(Integer, default=0, comment="提及该价格的研报数")
