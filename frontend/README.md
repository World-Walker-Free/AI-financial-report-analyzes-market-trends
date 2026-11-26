# AI 研报看板前端

本目录按 `Project_8-master` 中 `frontend/` 的初始目录约定整理，保留第二个压缩包中已经实现的页面、交互、Mock、API 适配和 ECharts 功能。

## 目录对应关系

| 初始结构 | 整理后的实现 |
|---|---|
| `src/views/Dashboard.vue` | 看板页面及数据加载、筛选联动 |
| `src/components/FilterBar.vue` | 顶栏、品种/日期/机构筛选 |
| `src/components/KpiCards.vue` | KPI 指标卡 |
| `src/components/Gauge.vue` | 一致性预期指数仪表盘 |
| `src/components/ViewColumns.vue` | 当日机构观点 |
| `src/components/HistoryTable.vue` | 历史观点表 |
| `src/components/TrendChart.vue` | 家数与指数趋势图 |
| `src/components/RankingPanel.vue` | 看多/看空排行 |
| `src/components/StatusBar.vue` | 底部状态栏 |
| `src/api/index.js` | 五个接口、数据源切换及字段适配 |
| `src/mock/dashboard.js` | 动态 Mock 数据 |
| `src/styles/index.css` | 页面样式 |
| `src/utils/` | ECharts 生命周期和格式化辅助函数 |

## 运行

```bash
npm install
npm run serve
```

访问 `http://localhost:8080`。

构建：

```bash
npm run build
```

## 数据源

复制 `.env.example` 为 `.env.local`，按需配置：

- `VUE_APP_DATA_SOURCE=mock`：本地 Mock，默认值
- `VUE_APP_DATA_SOURCE=api`：连接 FastAPI
- `VUE_APP_DATA_SOURCE=planb`：读取 `public/mock/dashboard.json`

真实 API 目标地址由 `VUE_APP_API_TARGET` 配置。修改环境变量后需重启开发服务。

## 工程配置说明

本次整理以“目录结构对齐、功能代码完整”为原则。第二个压缩包实际使用 **Vue 2.7 + Vue CLI 5**，因此保留 `vue.config.js`、`babel.config.js` 和对应依赖，不强行改造成初始脚手架占位文件所写的 Vite 配置，以免破坏现有工程的可运行性。
