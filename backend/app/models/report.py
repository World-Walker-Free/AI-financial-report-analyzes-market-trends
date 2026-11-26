"""研报表：文件元信息 + 解析状态。"""
from sqlalchemy import Column, Date, DateTime, ForeignKey, Index, Integer, String, func

from ..database import Base


class Report(Base):
    __tablename__ = "t_report"

    id = Column(Integer, primary_key=True, autoincrement=True)
    institution_id = Column(Integer, ForeignKey("t_institution.id"), nullable=False)
    report_date = Column(Date, nullable=False, index=True)
    report_no = Column(String(64), nullable=True, comment="业务报告 ID，同一机构内唯一")
    title = Column(String(255), nullable=True, comment="研报标题")
    file_path = Column(String(512), nullable=True)
    file_hash = Column(String(64), unique=True, nullable=True, comment="SHA-256，用于去重")
    parse_status = Column(String(16), default="pending", comment="pending/ok/failed/need_ocr")
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("ix_report_inst_date", "institution_id", "report_date"),
    )
