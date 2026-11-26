"""研报数据访问。"""
from sqlalchemy.orm import Session

from ..models import Institution, Report


def get_with_institution(db: Session, report_id: int):
    """研报 + 机构，用于原文溯源。"""
    return (
        db.query(Report, Institution)
        .join(Institution, Report.institution_id == Institution.id)
        .filter(Report.id == report_id)
        .first()
    )


def list_by_date(db: Session, report_date):
    return db.query(Report).filter(Report.report_date == report_date).all()
