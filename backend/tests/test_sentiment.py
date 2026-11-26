"""一致性预期指数单测：python -m pytest tests -q"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.database import Base  # noqa: E402
from app.models import Institution, Opinion, Report  # noqa: E402
from app.services.sentiment import collect_day, compute_index  # noqa: E402


def test_compute_index_basic():
    assert compute_index(4, 6, 4) == -14.3      # 文档示例
    assert compute_index(5, 0, 0) == 100.0
    assert compute_index(0, 5, 0) == -100.0
    assert compute_index(3, 3, 3) == 0.0
    assert compute_index(0, 0, 0) is None       # N=0 返回 None，不是 0


def test_dedupe_threshold_and_unknown():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine)()

    from datetime import date
    d = date(2024, 3, 29)
    insts = [Institution(name=f"机构{i}") for i in range(3)]
    db.add_all(insts)
    db.flush()

    def add(inst, direction, conf):
        rep = Report(institution_id=inst.id, report_date=d, file_hash=f"h{inst.id}-{direction}-{conf}")
        db.add(rep)
        db.flush()
        db.add(Opinion(report_id=rep.id, variety_code="RB", direction=direction,
                       confidence=conf, extraction_method="AI"))

    add(insts[0], "BULL", 0.9)   # 同机构两条，取最高 -> BULL
    add(insts[0], "BEAR", 0.7)
    add(insts[1], "BULL", 0.5)   # 低于 0.6，不计
    add(insts[2], "NEUTRAL", 0.8)
    db.commit()

    stat = collect_day(db, "RB", d)
    assert stat["bull"] == 1
    assert stat["bear"] == 0
    assert stat["flat"] == 1
    assert stat["institution_count"] == 2
    assert stat["index"] == 0.0
