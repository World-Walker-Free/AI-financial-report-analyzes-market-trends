"""观点表：一份研报可对应多条（多品种/多周期）。"""
from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, Numeric, String, func

from ..database import Base


class Opinion(Base):
    __tablename__ = "t_view"

    id = Column(Integer, primary_key=True, autoincrement=True)
    report_id = Column(Integer, ForeignKey("t_report.id"), nullable=False, index=True)
    variety_code = Column(String(16), nullable=False, index=True)
    contract_code = Column(String(16), nullable=True)
    horizon = Column(String(16), default="short", comment="intraday/short/medium")
    direction = Column(String(8), nullable=False, comment="BULL/BEAR/NEUTRAL/UNKNOWN")
    raw_direction = Column(String(64), nullable=True, comment="研报原始表述")
    strategy = Column(String(128), nullable=True)
    reason = Column(String(512), nullable=True)
    evidence = Column(String(1024), nullable=True, comment="原文依据")
    source_page = Column(Integer, nullable=True)
    extraction_method = Column(String(8), default="AI", comment="RULE/AI")
    confidence = Column(Numeric(3, 2), nullable=True)
    review_status = Column(String(16), default="auto", comment="auto/pending/manual")
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("ix_view_variety_dir", "variety_code", "direction"),
    )
