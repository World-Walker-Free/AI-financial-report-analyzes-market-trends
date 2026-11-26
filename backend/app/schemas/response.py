"""统一响应结构：{code, msg, data}。"""


def ok(data, msg: str = "success"):
    return {"code": 0, "msg": msg, "data": data}


def fail(msg: str, code: int = 1):
    return {"code": code, "msg": msg, "data": None}
