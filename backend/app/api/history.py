"""历史序列：并行数组，直接喂 ECharts。"""
from datetime import date as date_cls

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import DailyPrice, DailySentiment
from ..schemas.response import ok

router = APIRouter(tags=["history"])


@router.get("/history")
def history(
    variety: str = Query("RB"),
    start: str = Query(None),
    end: str = Query(None),
    limit: int = Query(8, ge=1, le=60),
    db: Session = Depends(get_db),
):
    q = db.query(DailySentiment).filter(DailySentiment.variety_code == variety)
    if start:
        q = q.filter(DailySentiment.trade_date >= date_cls.fromisoformat(start))
    if end:
        q = q.filter(DailySentiment.trade_date <= date_cls.fromisoformat(end))
    rows = q.order_by(DailySentiment.trade_date.asc()).all()
    if not start and not end:
        rows = rows[-limit:]

    dates = [r.trade_date.isoformat() for r in rows]
    prices = {}
    if dates:
        prows = (
            db.query(DailyPrice)
            .filter(
                DailyPrice.variety_code == variety,
                DailyPrice.trade_date >= rows[0].trade_date,
                DailyPrice.trade_date <= rows[-1].trade_date,
            )
            .all()
        )
        prices = {p.trade_date.isoformat(): (float(p.close_price) if p.close_price is not None else None)
                  for p in prows}

    return ok({
        "variety": variety,
        "dates": dates,
        "bull": [r.bull_count for r in rows],
        "bear": [r.bear_count for r in rows],
        "flat": [r.flat_count for r in rows],
        "price": [prices.get(d) for d in dates],
        "index": [float(r.consensus_index) if r.consensus_index is not None else None for r in rows],
    })
