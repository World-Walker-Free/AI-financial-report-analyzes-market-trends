"""生成演示数据并重算快照。

用法（在 backend 目录下）：
    python -m scripts.seed_demo

默认写 SQLite（backend/app.db）；设置 DATABASE_URL 可写 MySQL。
"""
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.models import (  # noqa: E402
    DailyPrice,
    DailySentiment,
    Institution,
    Opinion,
    Report,
    Variety,
)
from app.services.sentiment import rebuild_day  # noqa: E402

DATES = [date(2024, 3, d) for d in (18, 19, 20, 21, 22, 25, 26, 27, 28, 29)]

# 螺纹钢 10 个交易日的多空平家数（与前端 Mock 一致）
RB = {
    "bull": [5, 6, 6, 7, 6, 5, 5, 4, 4, 4],
    "bear": [5, 4, 5, 4, 5, 5, 6, 6, 6, 6],
}

INSTITUTIONS = [
    "中信期货", "国泰君安", "永安期货", "申银万国", "海通期货", "一德期货", "光大期货",
    "兴业期货", "中粮期货", "长江期货", "中金财富", "五矿期货", "南华期货", "银河期货",
]

VARIETIES = [
    ("RB", "螺纹钢", "SHFE", "RB2405"),
    ("I", "铁矿石", "DCE", "I2405"),
    ("P", "棕榈油", "DCE", "P2405"),
    ("CU", "沪铜", "SHFE", "CU2405"),
    ("AU", "沪金", "SHFE", "AU2406"),
    ("M", "豆粕", "DCE", "M2405"),
    ("TA", "PTA", "CZCE", "TA2405"),
    ("SA", "纯碱", "CZCE", "SA2405"),
]

BULL_TEXT = "库存去化，需求边际改善，逢低做多"
BEAR_TEXT = "库存压力仍存，短期承压运行"
FLAT_TEXT = "多空交织，区间震荡"


def reset(db):
    for model in (Opinion, Report, DailySentiment, DailyPrice, Institution, Variety):
        db.query(model).delete()
    db.commit()


def seed(db):
    db.add_all([
        Variety(code=c, name=n, exchange=e, main_contract=m) for c, n, e, m in VARIETIES
    ])
    insts = [Institution(name=n, short_name=n[:4]) for n in INSTITUTIONS]
    db.add_all(insts)
    db.commit()

    # 螺纹钢：每天 14 家机构各一份研报，一篇一个观点
    for i, d in enumerate(DATES):
        bull, bear = RB["bull"][i], RB["bear"][i]
        flat = 14 - bull - bear
        directions = ["BULL"] * bull + ["BEAR"] * bear + ["NEUTRAL"] * flat
        for j, inst in enumerate(insts):
            rep = Report(
                institution_id=inst.id, report_date=d,
                report_no=f"{d.strftime('%Y%m%d')}_{inst.name}_{210000 + i * 14 + j}",
                title=f"{inst.name}螺纹钢日报 {d.isoformat()}",
                file_path=f"data/raw/{d.strftime('%Y%m%d')}/report_{i}_{j}.html",
                file_hash=f"demo-{d}-{j}", parse_status="ok",
            )
            db.add(rep)
            db.flush()
            direction = directions[j % len(directions)]
            text = {"BULL": BULL_TEXT, "BEAR": BEAR_TEXT, "NEUTRAL": FLAT_TEXT}[direction]
            db.add(Opinion(
                report_id=rep.id, variety_code="RB", contract_code="RB2405",
                horizon="short", direction=direction, raw_direction=text[:8],
                strategy="逢低做多" if direction == "BULL" else ("观望" if direction == "BEAR" else "区间"),
                reason=text, evidence=text, confidence=round(0.6 + (j % 4) * 0.1, 2),
                extraction_method="AI",
            ))

        # 边界样本：低于阈值的观点、UNKNOWN，都不应计入指数
        rep2 = Report(institution_id=insts[0].id, report_date=d,
                      report_no=f"{d.strftime('%Y%m%d')}_low",
                      title="低置信度样本", file_path="data/raw/low.html",
                      file_hash=f"low-{d}", parse_status="ok")
        db.add(rep2)
        db.flush()
        db.add(Opinion(report_id=rep2.id, variety_code="RB", direction="BEAR",
                       confidence=0.40, reason="低置信度", extraction_method="AI"))
        db.add(Opinion(report_id=rep2.id, variety_code="RB", direction="UNKNOWN",
                       confidence=0.90, reason="未明确", extraction_method="AI"))

        # 其它品种：确定性伪随机，保证排行有数据
        for k, (code, *_rest) in enumerate(VARIETIES[1:]):
            b = 2 + (i + k) % 4
            s = 2 + (i * 2 + k) % 4
            f = max(14 - b - s, 1)
            for j, direction in enumerate(["BULL"] * b + ["BEAR"] * s + ["NEUTRAL"] * f):
                rep = Report(institution_id=insts[j % len(insts)].id, report_date=d,
                             report_no=f"{d.strftime('%Y%m%d')}_{code}_{j}",
                             title=f"{code} 日报", file_path=f"data/raw/{code}.html",
                             file_hash=f"{d}-{code}-{j}", parse_status="ok")
                db.add(rep)
                db.flush()
                db.add(Opinion(report_id=rep.id, variety_code=code, horizon="short",
                               direction=direction, confidence=0.7, extraction_method="AI"))

        db.add(DailyPrice(variety_code="RB", trade_date=d,
                          close_price=3500 + i * 10, change_pct=round((i % 5 - 2) * 0.6, 2),
                          sample_count=5))
    db.commit()

    for d in DATES:
        rebuild_day(db, d)


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        reset(db)
        seed(db)
        total = db.query(Opinion).count()
        snaps = db.query(DailySentiment).count()
        print(f"seeded: opinions={total}, snapshots={snaps}, dates={len(DATES)}")
        row = (db.query(DailySentiment)
                 .filter(DailySentiment.variety_code == "RB", DailySentiment.trade_date == DATES[-1])
                 .first())
        print(f"RB {row.trade_date}: bull={row.bull_count} bear={row.bear_count} "
              f"flat={row.flat_count} index={row.consensus_index}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
