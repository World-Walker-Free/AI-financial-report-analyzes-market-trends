"""一致性预期指数与每日快照。

口径（需求文档 3.2）：
  I = (B - S) / N * 100，N = B + S + F，取值 -100 ~ 100
  - 只统计 direction ∈ {BULL, BEAR, NEUTRAL} 且 confidence >= 阈值（默认 0.6）
  - UNKNOWN / 低置信度不计入
  - 同一机构 + 同一品种 + 同一交易日只算一次，取置信度最高的一条
  - N = 0 时返回 None（前端显示 "-"）
"""
from sqlalchemy.orm import Session

from ..config import CONFIDENCE_THRESHOLD
from ..models import DailySentiment, Opinion, Report

VALID_DIRECTIONS = ("BULL", "BEAR", "NEUTRAL")


def compute_index(bull: int, bear: int, flat: int):
    """纯函数，方便单测：4 多 / 6 空 / 4 平 -> -14.3。"""
    total = bull + bear + flat
    if total <= 0:
        return None
    return round((bull - bear) / total * 100, 1)


def collect_day(db: Session, variety_code: str, trade_date, threshold: float = None):
    """统计某品种某交易日的多空平家数（同机构去重取最高置信度）。"""
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

    best = {}  # institution_id -> (opinion, report_id)
    for op, inst_id, report_id in rows:
        conf = float(op.confidence or 0)
        if inst_id not in best or conf > float(best[inst_id][0].confidence or 0):
            best[inst_id] = (op, report_id)

    bull = sum(1 for op, _ in best.values() if op.direction == "BULL")
    bear = sum(1 for op, _ in best.values() if op.direction == "BEAR")
    flat = sum(1 for op, _ in best.values() if op.direction == "NEUTRAL")
    reports = {rid for _, rid in best.values()}

    return {
        "variety_code": variety_code,
        "trade_date": trade_date,
        "bull": bull,
        "bear": bear,
        "flat": flat,
        "institution_count": bull + bear + flat,
        "report_count": len(reports),
        "index": compute_index(bull, bear, flat),
    }


def rebuild_day(db: Session, trade_date, variety_code: str = None) -> int:
    """重算某日快照（幂等：先删后插），返回写入行数。"""
    q = (
        db.query(Opinion.variety_code)
        .join(Report, Opinion.report_id == Report.id)
        .filter(Report.report_date == trade_date)
        .distinct()
    )
    codes = [r[0] for r in q.all()] if variety_code is None else [variety_code]

    for code in codes:
        stat = collect_day(db, code, trade_date)
        db.query(DailySentiment).filter(
            DailySentiment.variety_code == code,
            DailySentiment.trade_date == trade_date,
        ).delete(synchronize_session=False)
        db.add(DailySentiment(
            variety_code=code,
            trade_date=trade_date,
            bull_count=stat["bull"],
            bear_count=stat["bear"],
            flat_count=stat["flat"],
            institution_count=stat["institution_count"],
            report_count=stat["report_count"],
            consensus_index=stat["index"],
        ))
    db.commit()
    return len(codes)
