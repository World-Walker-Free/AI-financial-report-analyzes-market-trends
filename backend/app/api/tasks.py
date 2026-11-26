"""重算任务：指定日期重建每日快照（幂等）。"""
from datetime import date as date_cls

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.response import ok
from ..services.sentiment import rebuild_day

router = APIRouter(tags=["tasks"])


@router.post("/tasks/rebuild")
def rebuild(
    date: str = Query(..., description="YYYY-MM-DD"),
    variety: str = Query(None, description="只重算某个品种，默认全部"),
    db: Session = Depends(get_db),
):
    trade_date = date_cls.fromisoformat(date)
    count = rebuild_day(db, trade_date, variety)
    return ok({"date": trade_date.isoformat(), "variety": variety, "updated": count})
