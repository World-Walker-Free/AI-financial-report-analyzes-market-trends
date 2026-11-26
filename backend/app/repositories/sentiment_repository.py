"""每日快照数据访问。"""
from sqlalchemy.orm import Session

from ..models import DailyPrice, DailySentiment, Variety


def get_snapshot(db: Session, variety_code: str, trade_date):
    return (
        db.query(DailySentiment)
        .filter(
            DailySentiment.variety_code == variety_code,
            DailySentiment.trade_date == trade_date,
        )
        .first()
    )


def latest_date(db: Session, variety_code: str = None):
    q = db.query(DailySentiment.trade_date)
    if variety_code:
        q = q.filter(DailySentiment.variety_code == variety_code)
    row = q.order_by(DailySentiment.trade_date.desc()).first()
    return row[0] if row else None


def price_map(db: Session, variety_code: str, start, end):
    rows = (
        db.query(DailyPrice)
        .filter(
            DailyPrice.variety_code == variety_code,
            DailyPrice.trade_date >= start,
            DailyPrice.trade_date <= end,
        )
        .all()
    )
    return {r.trade_date: (float(r.close_price) if r.close_price is not None else None) for r in rows}
