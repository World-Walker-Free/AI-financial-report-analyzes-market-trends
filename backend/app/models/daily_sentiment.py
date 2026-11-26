"""每日指标快照：品种 × 交易日。"""
from sqlalchemy import Column, Date, DateTime, Integer, Numeric, String, func

from ..database import Base


class DailySentiment(Base):
    __tablename__ = "t_daily_sentiment"

    variety_code = Column(String(16), primary_key=True)
    trade_date = Column(Date, primary_key=True)
    bull_count = Column(Integer, default=0)
    bear_count = Column(Integer, default=0)
    flat_count = Column(Integer, default=0)
    institution_count = Column(Integer, default=0, comment="B+S+F，去重后的机构数")
    report_count = Column(Integer, default=0, comment="当日该品种涉及的研报数")
    consensus_index = Column(Numeric(5, 1), nullable=True, comment="N=0 时为 NULL")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
