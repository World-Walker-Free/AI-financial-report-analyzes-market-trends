"""当日机构观点明细（看多/看空/看平三栏）。"""
from datetime import date as date_cls

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..config import CONFIDENCE_THRESHOLD
from ..database import get_db
from ..models import DailySentiment, Institution, Opinion, Report
from ..schemas.response import ok

router = APIRouter(tags=["views"])

VALID = ("BULL", "BEAR", "NEUTRAL")


def _latest_date(db: Session, variety: str):
    row = (
        db.query(DailySentiment.trade_date)
        .filter(DailySentiment.variety_code == variety)
        .order_by(DailySentiment.trade_date.desc())
        .first()
    )
    return row[0] if row else None


@router.get("/views")
def views(
    variety: str = Query("RB"),
    date: str = Query(None),
    db: Session = Depends(get_db),
):
    trade_date = date_cls.fromisoformat(date) if date else _latest_date(db, variety)
    if not trade_date:
        return ok({"date": None, "variety": variety, "total": 0,
                   "groups": {"bull": [], "bear": [], "flat": []}})

    rows = (
        db.query(Opinion, Report, Institution)
        .join(Report, Opinion.report_id == Report.id)
        .join(Institution, Report.institution_id == Institution.id)
        .filter(
            Report.report_date == trade_date,
            Opinion.variety_code == variety,
            Opinion.confidence >= CONFIDENCE_THRESHOLD,
            Opinion.direction.in_(VALID),
        )
        .all()
    )

    # 同机构同品种同日去重，取置信度最高的一条
    best = {}
    for op, rep, inst in rows:
        conf = float(op.confidence or 0)
        if inst.id not in best or conf > best[inst.id][0]:
            best[inst.id] = (conf, op, rep, inst)

    groups = {"bull": [], "bear": [], "flat": []}
    key_map = {"BULL": "bull", "BEAR": "bear", "NEUTRAL": "flat"}
    for conf, op, rep, inst in best.values():
        groups[key_map[op.direction]].append({
            "institution": inst.name,
            "title": rep.title or rep.report_no or "",
            "confidence": conf,
            "direction": op.direction,
            "horizon": op.horizon,
            "reason": op.reason,
            "evidence": op.evidence,
            "sourceUrl": rep.file_path or "",
            "reportId": rep.report_no or str(rep.id),
        })

    total = sum(len(v) for v in groups.values())
    return ok({"date": trade_date.isoformat(), "variety": variety, "total": total, "groups": groups})
