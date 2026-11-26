"""品种排行：按一致性预期指数排序。"""
from datetime import date as date_cls

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import DailySentiment, Variety
from ..schemas.response import ok

router = APIRouter(tags=["ranking"])


def _latest_date(db: Session):
    row = db.query(DailySentiment.trade_date).order_by(DailySentiment.trade_date.desc()).first()
    return row[0] if row else None


@router.get("/ranking")
def ranking(
    date: str = Query(None),
    type: str = Query("bull", pattern="^(bull|bear)$"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    trade_date = date_cls.fromisoformat(date) if date else _latest_date(db)
    if not trade_date:
        return ok([])

    q = (
        db.query(DailySentiment, Variety.name)
        .outerjoin(Variety, DailySentiment.variety_code == Variety.code)
        .filter(
            DailySentiment.trade_date == trade_date,
            DailySentiment.consensus_index.isnot(None),
        )
    )
    q = q.order_by(
        DailySentiment.consensus_index.desc() if type == "bull" else DailySentiment.consensus_index.asc()
    )
    rows = q.limit(limit).all()

    return ok([
        {
            "variety": s.variety_code,
            "name": name or s.variety_code,
            "consensusIndex": float(s.consensus_index),
            "institutionCount": s.institution_count,
        }
        for s, name in rows
    ])
