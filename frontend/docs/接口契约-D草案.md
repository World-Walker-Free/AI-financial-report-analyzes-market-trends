# 接口约定 · D 起草草案（待 D1 下午全组确认）

> **归档说明**：按组规「`docs/` 归 A」，这份由 D 起草、放 `frontend/` 下。
> 请把内容复制进 `docs/接口约定.md`，由 A 归档、C 确认实现、D 消费。
> 确认后谁改字段谁请全组喝奶茶。

| 项 | 内容 |
|---|---|
| 版本 | v1.0（草案） |
| 状态 | ⏳ D1 下午 15:00 前定死 |
| 起草 | D（前端） |
| 实现 | C（FastAPI / MySQL） |
| 归档 | A（组长） |
| 消费 | D（Vue + ECharts） |
| 联调 | D3 上午；D3 晚上是端到端生死线 |

---

## 一、通用约定（所有接口都适用）

### 1.1 基址与代理

前端只认 `/api/xxx`，由 `vue.config.js` 转发到 C 的 FastAPI：

```
浏览器  /api/overview  →  开发服务器代理  →  http://<C 的地址>/overview
```

`pathRewrite` 会去掉 `/api` 前缀，**C 的路由里不要写 `/api`**。跨域由前端代理解决，C 不用配 CORS。
代理地址在 `.env.local` 的 `VUE_APP_API_TARGET` 里配，C 给地址后 D 改一行、重启 `npm run serve`。

### 1.2 统一响应体

```json
{ "code": 0, "msg": "ok", "data": { } }
```

| 字段 | 类型 | 说明 |
|---|---|---|
| `code` | number | `0` = 成功；非 0 = 失败 |
| `msg` | string | 失败原因，前端会原样显示在顶部红色提示条 |
| `data` | object / array | 业务数据；失败时可为 `null` |

建议错误码：

| code | 含义 | 前端表现 |
|---|---|---|
| `0` | 成功 | 正常渲染 |
| `400` | 参数错误（缺 variety / 日期格式不对） | 提示条 + 保留旧数据 |
| `404` | 资源不存在 | 同上 |
| `500` | 服务端异常 | 同上 |

> ⚠️ **空数据不是错误**。某天没有观点时，请返回 `code: 0` + 空数组 / `null` 字段，
> **不要返回 404 或 500**，否则前端会弹「加载失败」而实际只是没数据。
> 前端已做三态：加载中骨架、空值 `--`、失败提示，且失败时**保留上一次数据不白屏**。

### 1.3 字段通用规则

| 规则 | 说明 |
|---|---|
| 日期 | 一律 `YYYY-MM-DD` 字符串，如 `2024-03-29` |
| 数值 | 全部是 **number**，不要 `"4"`、`"14.3"` 这种字符串 |
| 方向枚举 | `bull` / `bear` / `neutral`（C 若用 `flat`，D 的适配层已兼容，但**定稿请统一成 `neutral`**） |
| 品种 code | 形如 `RB2405`，与 `/varieties` 返回值严格一致 |
| `index` | 一致性预期指数，保留 **1 位小数**，范围 `[-100, 100]` |
| `N = 0` | `index` 返回 **`null`**，不是 `0`。前端显示 `--` |
| 置信度过滤 | C 侧只统计置信度 ≥ 0.6、且同机构同品种去重后的观点（文档第四节 C 的职责） |

### 1.4 一致性预期指数口径（C 与 D 必须一致）

```
index = round( (bull − bear) / (bull + bear + flat) × 100 , 1 )
```

- 分母 = **覆盖机构数**（看多 + 看空 + 看平），不是研报份数；
- `bull + bear + flat = 0` 时 `index = null`；
- `> 0` 偏多（橙色 `#d9741f`），`< 0` 偏空（绿色 `#218a55`），`= 0` 中性；
- 前端 `src/utils/format.js` 里有一份同口径的 `consensusIndex()`，仅用于 Mock 与 Plan B 兜底计算，**不覆盖后端返回值**（后端有 `index` 时以前端收到的为准）。

---

## 二、5 个接口逐条定义

### ① `GET /varieties` — 品种下拉

**参数**：无

**data**：`Array<{ code, name }>`

| 字段 | 类型 | 必填 | 示例 | 说明 |
|---|---|---|---|---|
| `code` | string | ✅ | `"RB2405"` | 后续所有接口的 `variety` 参数值 |
| `name` | string | ✅ | `"螺纹钢"` | 下拉显示名 |

```json
{ "code": 0, "msg": "ok", "data": [
  { "code": "RB2405", "name": "螺纹钢" },
  { "code": "I2405", "name": "铁矿石" },
  { "code": "P2405", "name": "棕榈油" }
] }
```

> P0 只要求单品种（螺纹钢）能演示，但下拉请至少给 3 个，方便 D 演示切换联动。
> P1 的品种切换靠这个接口扩展，不用改前端代码。

---

### ② `GET /overview` — 顶部 6 张 KPI + 仪表盘 + 底部状态栏

**参数**：`variety`（必填）、`date`（必填，`YYYY-MM-DD`）

**data**：`Object`

| 字段 | 类型 | 必填 | 示例 | 用在哪 |
|---|---|---|---|---|
| `date` | string | ✅ | `"2024-03-29"` | 仪表盘右上角日期 |
| `bull` | number | ✅ | `4` | KPI 看多机构 |
| `bear` | number | ✅ | `6` | KPI 看空机构 |
| `flat` | number | ✅ | `4` | KPI 看平机构 |
| `institutions` | number | ✅ | `14` | 覆盖机构数 / 研报卡副标题 |
| `coveredVarieties` | number | ✅ | `31` | KPI 覆盖品种 |
| `reports` | number | ✅ | `37` | KPI 当日新增研报 |
| `parseRate` | number | 可空 | `98.7` | 解析成功率（%），无数据显示 `--` |
| `index` | number / null | ✅ | `-14.3` | KPI 第 6 张 + 仪表盘指针 |
| `delta.bull` | number | 可空 | `-2` | 「较上一交易日」，无数据显示 `--` |
| `delta.bear` | number | 可空 | `1` | 同上 |
| `delta.flat` | number | 可空 | `1` | 同上 |
| `range.start` | string | ✅ | `"2024-03-01"` | 顶栏区间 + 底部状态栏 |
| `range.end` | string | ✅ | `"2024-03-29"` | 同上 |
| `totalReports` | number | 可空 | `3847` | 底部累计解析研报 |
| `totalInstitutions` | number | 可空 | `86` | 底部覆盖机构 |
| `totalVarieties` | number | 可空 | `31` | 底部覆盖品种 |

```json
{ "code": 0, "msg": "ok", "data": {
  "date": "2024-03-29",
  "bull": 4, "bear": 6, "flat": 4,
  "institutions": 14, "coveredVarieties": 31, "reports": 37,
  "parseRate": 98.7, "index": -14.3,
  "delta": { "bull": -2, "bear": 1, "flat": 1 },
  "range": { "start": "2024-03-01", "end": "2024-03-29" },
  "totalReports": 3847, "totalInstitutions": 86, "totalVarieties": 31
} }
```

> `delta` 与 `total*` 属于「锦上添花」字段：**C 来不及就先不返回**，前端会显示 `--`，不报错、不白屏。
> 但 `bull / bear / flat / index / date / range` 是 P0，必须给。

---

### ③ `GET /views` — 当日机构观点三栏 + 原文溯源

**参数**：`variety`、`date`

**data**：`Object`，三个键各为数组

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `bull` / `bear` / `neutral` | Array | ✅ | 三栏列表；某方向没有机构时给 `[]` |
| `[].org` | string | ✅ | 机构名，如 `"中信期货"` |
| `[].reportId` | string | 可空 | 研报 ID，用于列表 key 与排查 |
| `[].url` | string | ✅ | **原文地址，P0 验收项** |

```json
{ "code": 0, "msg": "ok", "data": {
  "bull":    [{ "org": "中信期货", "reportId": "R0001", "url": "/reports/2024-03-29/R0001.html" }],
  "bear":    [{ "org": "海通期货", "reportId": "R0005", "url": "/reports/2024-03-29/R0005.pdf" }],
  "neutral": [{ "org": "中金财富", "reportId": "R0011", "url": "/reports/2024-03-29/R0011.html" }]
} }
```

> 🔴 **`url` 不能是 `#` 或空**。文档 P0 写着「原文溯源：点击能打开/定位到原研报」，
> 前端用的是 `<a target="_blank">`，点开是空白页会直接丢分。
> 可以是内网静态文件路径、Nginx 下的 PDF/HTML 地址，或带锚点的原文链接；
> 演示前请和 B 一起抽查 3 条能真的打开。

---

### ④ `GET /history` — 历史表 + 柱状/折线双轴组合图

**参数**：`variety`、`start`、`end`（`YYYY-MM-DD`）

**data**：`Array`，**按日期升序**（前端自己倒序取近 8 条）

| 字段 | 类型 | 必填 | 示例 | 说明 |
|---|---|---|---|---|
| `date` | string | ✅ | `"2024-03-29"` | 表格首列 / x 轴 |
| `bull` / `bear` / `flat` | number | ✅ | `4` / `6` / `4` | 柱状图三组 + 表格 |
| `reports` | number | ✅ | `37` | 当日研报数（表格 + tooltip） |
| `index` | number / null | ✅ | `-14.3` | 折线（右轴）+ 表格末列 |

```json
{ "code": 0, "msg": "ok", "data": [
  { "date": "2024-03-28", "bull": 4, "bear": 6, "flat": 4, "reports": 32, "index": -14.3 },
  { "date": "2024-03-29", "bull": 4, "bear": 6, "flat": 4, "reports": 37, "index": -14.3 }
] }
```

> P0 只要求 3/25～3/29 五个交易日。**给 5 条就能演示**，前端表格与图表都能自适应条数。
> 组合图左轴固定 `0~12` 家、右轴 `-100~100`，若某天家数超 12 请告知 D 调刻度。

---

### ⑤ `GET /ranking` — 看多 / 看空 TOP10

**参数**：`date`

**data**：`Object`

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `bull` / `bear` | Array | ✅ | 各最多 10 条，按 `value` 降序 / 升序 |
| `[].name` | string | ✅ | 品种名，如 `"棕榈油"` |
| `[].value` | number | ✅ | 一致性预期指数；**看空为负值** |

```json
{ "code": 0, "msg": "ok", "data": {
  "bull": [{ "name": "棕榈油", "value": 50 }, { "name": "铁矿石", "value": 45.5 }],
  "bear": [{ "name": "苹果", "value": -80 }, { "name": "玉米", "value": -71.4 }]
} }
```

> 看空侧请给**负数**（前端靠正负决定条形向左还是向右）。给正数也能画，但方向会反。

---

## 三、字段名对不上怎么办（避免 D3 扯皮）

前端 `src/api/index.js` 里有一层 `adapt*()` 适配函数：

```
C 的字段  →  adaptOverview / adaptViews / adaptHistory / adaptRanking  →  组件视图模型
```

已预置的别名兼容：

| 前端用 | 也接受 C 写成 |
|---|---|
| `institutions` | `institution_count` |
| `coveredVarieties` | `variety_count` |
| `reports` | `report_count` |
| `parseRate` | `parse_rate` |
| `index` | `consensus_index` |
| `org` | `institution` |
| `reportId` | `report_id` |
| `url` | `source_url` |
| `neutral` | `flat` |
| `name` / `value` | `variety_name` / `consensus_index` |

**结论**：契约定稿后如果 C 已经写完了不想改名，告诉 D 实际字段名，**D 只改 `src/api/index.js` 的适配层，8 个组件一行不动**。这比让 C 返工快。但请务必在 D2 下班前说，别留到 D3 上午。

---

## 四、联调节奏与兜底

| 时间 | 谁 | 做什么 |
|---|---|---|
| D1 15:00 前 | 全组 | 确认本文，A 归档进 `docs/接口约定.md` |
| D2 下班前 | C | 给 Swagger 地址或 5 份示例 JSON（可直接用本文样例） |
| D3 上午 | C + D | D 把 `.env.local` 切成 `api`，逐个接口对字段 |
| D3 晚上 | 全组 | **端到端生死线**：页面出现真实数据 |
| D3 未通 | B + D | 启用 **Plan B**：B 用 Python 从 MySQL 导出 `frontend/public/mock/dashboard.json`，D 切成 `planb`，看板照常演示（只是不能实时切品种） |

前端三态数据源（`.env.local` 的 `VUE_APP_DATA_SOURCE`）：

| 值 | 数据来源 | 用在哪 |
|---|---|---|
| `mock` | `src/mock/dashboard.js` | D1～D2，不等任何人 |
| `api` | C 的 FastAPI（经前端代理） | D3 起 |
| `planb` | `public/mock/dashboard.json` | 后端没做完的兜底 |

Plan B 的 JSON 结构由 `frontend/public/mock/dashboard.json` 现成文件给出，
B 导出时把五个键（`varieties / overview / views / history / ranking`）填满即可，字段名走本文约定。

---

## 五、验收清单（D3 当场逐条勾）

- [ ] 5 个接口都返回 `code: 0`，浏览器 Network 无 404 / 500 / CORS 红字
- [ ] `npm run serve` 页面 8 区块全部有真实数据
- [ ] 手算一组 `(4−6)/14×100 = -14.3`，与 KPI、仪表盘、历史表、折线图**四处显示一致**
- [ ] 切品种下拉 → 全页联动，1 秒内完成
- [ ] 点「查看原文」→ 能打开研报（抽查 3 条）
- [ ] 把某接口改空 → 页面显示 `--` 且**不白屏、不弹失败**
- [ ] 把接口地址写错 → 顶部出现失败提示，且**旧数据仍在**
- [ ] `npm run build` 成功，`dist/` 可交给 C 部署

---

## 六、变更记录

| 日期 | 版本 | 改了什么 | 提出人 | 确认人 |
|---|---|---|---|---|
| D1 | v1.0 | 初稿：5 接口字段、指数口径、空数据约定 | D | ⏳ 待 C / A |

> 组规：**之后谁改字段谁请全组喝奶茶**。改字段请同时通知 D（改适配层）与 A（更新本文档）。
