"""观点数据访问：按日聚合所需的查询与去重。"""
from sqlalchemy.orm import Session

from ..config import CONFIDENCE_THRESHOLD
from ..models import Opinion, Report

VALID_DIRECTIONS = ("BULL", "BEAR", "NEUTRAL")


def by_report(db: Session, report_id: int):
    return db.query(Opinion).filter(Opinion.report_id == report_id).all()


def day_opinions(db: Session, variety_code: str, trade_date, threshold: float = None):
    """返回 [(opinion, report_id)]，同机构只保留置信度最高的一条。"""
    threshold = CONFIDENCE_THRESHOLD if threshold is None else threshold
    rows = (
        db.query(Opinion, Report.institution_id, Report.id)
        .join(Report, Opinion.report_id == Report.id)
        .filter(
            Report.report_date == trade_date,
            Opinion.variety_code == variety_code,
            Opinion.confidence >= threshold,
            Opinion.direction.in_(VALID_DIRECTIONS),
        )
        .all()
    )

    best = {}
    for op, inst_id, report_id in rows:
        conf = float(op.confidence or 0)
        if inst_id not in best or conf > float(best[inst_id][0].confidence or 0):
            best[inst_id] = (op, report_id)
    return list(best.values())
