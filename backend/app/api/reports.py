"""研报详情：原文溯源用。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Institution, Opinion, Report
from ..schemas.response import ok

router = APIRouter(tags=["reports"])


@router.get("/reports/{report_id}")
def report_detail(report_id: int, db: Session = Depends(get_db)):
    row = (
        db.query(Report, Institution)
        .join(Institution, Report.institution_id == Institution.id)
        .filter(Report.id == report_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="研报不存在")

    rep, inst = row
    opinions = db.query(Opinion).filter(Opinion.report_id == rep.id).all()

    return ok({
        "id": rep.id,
        "institution": inst.name,
        "reportDate": rep.report_date.isoformat(),
        "title": rep.title,
        "reportNo": rep.report_no,
        "sourceUrl": rep.file_path,
        "parseStatus": rep.parse_status,
        "opinions": [
            {
                "variety": o.variety_code,
                "direction": o.direction,
                "horizon": o.horizon,
                "confidence": float(o.confidence) if o.confidence is not None else None,
                "reason": o.reason,
                "evidence": o.evidence,
            }
            for o in opinions
        ],
    })
