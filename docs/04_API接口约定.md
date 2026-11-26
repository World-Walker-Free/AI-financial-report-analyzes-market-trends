# API 接口约定（/api/v1 · C 后端实现版）

- 统一响应：`{"code": 0, "msg": "success", "data": ...}`；业务错误 `code != 0`；数据库不可用返回 HTTP 503。
- 日期格式 `YYYY-MM-DD`；指数保留 1 位小数；空数据返回空数组 / `null`，不报错。
- 启动：`uvicorn app.main:app --reload --port 8000`（在 `backend/` 下）。

## 1. GET /api/v1/varieties

```json
{"code":0,"msg":"success","data":[{"code":"RB","name":"螺纹钢","exchange":"SHFE","contract":"RB2405"}]}
```

## 2. GET /api/v1/overview?variety=RB&date=2024-03-29

`date` 省略时取该品种最新快照日。

```json
{"code":0,"msg":"success","data":{
  "variety":"RB","date":"2024-03-29",
  "bull":4,"bear":6,"flat":4,"total":14,
  "consensusIndex":-14.3,"closePrice":3590.0,"changePct":0.6,
  "reportCount":14,"institutionCount":14,"updatedAt":"15:30:12"
}}
```

## 3. GET /api/v1/views?variety=RB&date=2024-03-29

```json
{"code":0,"msg":"success","data":{
  "date":"2024-03-29","variety":"RB","total":14,
  "groups":{
    "bull":[{"institution":"中信期货","title":"中信期货螺纹钢日报","confidence":0.9,
             "direction":"BULL","horizon":"short","reason":"...","evidence":"...",
             "sourceUrl":"data/raw/...html","reportId":"20240329_中信期货_210000"}],
    "bear":[],"flat":[]
  }
}}
```

## 4. GET /api/v1/history?variety=RB&start=&end=&limit=8

并行数组，直接绑定 ECharts。

```json
{"code":0,"msg":"success","data":{
  "variety":"RB",
  "dates":["2024-03-28","2024-03-29"],
  "bull":[4,4],"bear":[6,6],"flat":[4,4],
  "price":[3580.0,3590.0],
  "index":[-14.3,-14.3]
}}
```

## 5. GET /api/v1/ranking?date=2024-03-29&type=bull&limit=10

`type`：`bull`（默认）| `bear`。

```json
{"code":0,"msg":"success","data":[
  {"variety":"P","name":"棕榈油","consensusIndex":50.0,"institutionCount":14}
]}
```

## 6. GET /api/v1/reports/{id}

```json
{"code":0,"msg":"success","data":{
  "id":1,"institution":"中信期货","reportDate":"2024-03-29",
  "title":"中信期货螺纹钢日报","reportNo":"20240329_中信期货_210000",
  "sourceUrl":"data/raw/20240329/report_0_0.html","parseStatus":"ok",
  "opinions":[{"variety":"RB","direction":"BULL","horizon":"short",
               "confidence":0.9,"reason":"...","evidence":"..."}]
}}
```

不存在返回 HTTP 404。

## 7. POST /api/v1/tasks/rebuild?date=2024-03-29&variety=RB

重算指定日期快照（幂等，重复执行结果不变）。

```json
{"code":0,"msg":"success","data":{"date":"2024-03-29","variety":"RB","updated":1}}
```

## 错误约定

| 场景 | HTTP | body |
|---|---|---|
| 参数格式错 | 422 | FastAPI 默认校验错误 |
| 研报不存在 | 404 | `{"detail":"研报不存在"}` |
| 数据库不可用 | 503 | `{"code":503,"msg":"数据库暂时不可用，请稍后重试","data":null}` |

## 与前端（组长）对齐点

- 字段名以本文为准：`consensusIndex / reportCount / institutionCount / closePrice / changePct`；
- `history` 用并行数组，不用对象数组；
- 原文溯源字段：`sourceUrl`、`reportId`。
