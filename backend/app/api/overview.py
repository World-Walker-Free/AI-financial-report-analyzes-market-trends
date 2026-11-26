"""市场概览：KPI + 仪表盘指数。"""
from datetime import date as date_cls

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import DailyPrice, DailySentiment
from ..schemas.response import ok

router = APIRouter(tags=["overview"])


def _latest_trade_date(db: Session, variety: str):
    row = (
        db.query(DailySentiment.trade_date)
        .filter(DailySentiment.variety_code == variety)
        .order_by(DailySentiment.trade_date.desc())
        .first()
    )
    return row[0] if row else None


@router.get("/overview")
def overview(
    variety: str = Query("RB"),
    date: str = Query(None),
    db: Session = Depends(get_db),
):
    trade_date = date_cls.fromisoformat(date) if date else _latest_trade_date(db, variety)

    snap = None
    price = None
    if trade_date:
        snap = (
            db.query(DailySentiment)
            .filter(
                DailySentiment.variety_code == variety,
                DailySentiment.trade_date == trade_date,
            )
            .first()
        )
        price = (
            db.query(DailyPrice)
            .filter(
                DailyPrice.variety_code == variety,
                DailyPrice.trade_date == trade_date,
            )
            .first()
        )

    data = {
        "variety": variety,
        "date": trade_date.isoformat() if trade_date else None,
        "bull": snap.bull_count if snap else 0,
        "bear": snap.bear_count if snap else 0,
        "flat": snap.flat_count if snap else 0,
        "total": snap.institution_count if snap else 0,
        "consensusIndex": float(snap.consensus_index) if snap and snap.consensus_index is not None else None,
        "closePrice": float(price.close_price) if price and price.close_price is not None else None,
        "changePct": float(price.change_pct) if price and price.change_pct is not None else None,
        "reportCount": snap.report_count if snap else 0,
        "institutionCount": snap.institution_count if snap else 0,
        "updatedAt": snap.updated_at.strftime("%H:%M:%S") if snap and snap.updated_at else None,
    }
    return ok(data)
