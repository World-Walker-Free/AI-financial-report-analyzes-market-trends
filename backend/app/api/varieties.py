"""品种列表。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Variety
from ..schemas.response import ok

router = APIRouter(tags=["varieties"])


@router.get("/varieties")
def list_varieties(db: Session = Depends(get_db)):
    rows = db.query(Variety).order_by(Variety.code).all()
    return ok([
        {"code": v.code, "name": v.name, "exchange": v.exchange, "contract": v.main_contract}
        for v in rows
    ])
