import axios from 'axios'
import * as mock from '@/mock/dashboard'

// ============================================================
// 数据源开关：改 .env.local 的 VUE_APP_DATA_SOURCE，不用动代码
//   'mock'  : D1~D2，读本地假数据，不等 C（默认）
//   'api'   : D3 起，走 vue.config.js 代理到 C 的 FastAPI
//   'planb' : 后端没做完的兜底，读 public/mock/dashboard.json
// 想临时硬切，也可以直接改下面这行的默认值
// ============================================================
export const DATA_SOURCE = process.env.VUE_APP_DATA_SOURCE || 'mock'

// D2 验收用：VUE_APP_FORCE_EMPTY=1 时所有 Mock 返回空，专测「空数据不白屏」
// D2 验收用：VUE_APP_FAIL_ONE=/views,/ranking 时指定接口抛错，专测「部分降级」
// ⚠️ 两个开关验完都要关掉并重启，别带着它们进 D3 联调
const FORCE_EMPTY = process.env.VUE_APP_FORCE_EMPTY === '1'
const FAIL_LIST = (process.env.VUE_APP_FAIL_ONE || '')
  .split(',').map(s => s.trim()).filter(Boolean)

// Mock 是瞬时返回的：loading 会在同一次渲染批次里被设 true 又设 false，
// 骨架屏与按钮「加载中…」根本来不及显示，点刷新就像死了一样。
// 给 mock 模式加一点最小延迟（默认 400ms），让加载态真的可见。
// 仅 mock 生效，真实接口 / planb 不受影响；设 0 可关掉。
const MOCK_DELAY = Math.max(0, Number(process.env.VUE_APP_MOCK_DELAY ?? 400) || 0)

const http = axios.create({ baseURL: '/api', timeout: 8000 })

// C 统一返回 { code, msg, data }；非 0 直接抛给 App.vue 显示失败提示
function unwrap(res) {
  const body = res.data
  if (body && body.code !== undefined && body.code !== 0) {
    throw new Error(body.msg || '接口返回异常')
  }
  return body && body.data !== undefined ? body.data : body
}

// ---------- 字段适配层：后端字段名 → 页面视图模型 ----------
// 契约变了只改这里，组件一行都不用动。字段名在 D1 下午和 C 定死。
function adaptVarieties(list = []) {
  return list.map(v => ({ code: v.code || v.variety_code, name: v.name || v.variety_name }))
}
function adaptOverview(d = {}) {
  return {
    date: d.date,
    bull: d.bull, bear: d.bear, flat: d.flat,
    institutions: d.institutions ?? d.institution_count,
    coveredVarieties: d.coveredVarieties ?? d.variety_count,
    reports: d.reports ?? d.report_count,
    parseRate: d.parseRate ?? d.parse_rate,
    index: d.index ?? d.consensus_index,
    delta: d.delta || {},
    range: d.range || {},
    totalReports: d.totalReports ?? d.total_reports,
    totalInstitutions: d.totalInstitutions ?? d.total_institutions,
    totalVarieties: d.totalVarieties ?? d.total_varieties
  }
}
function adaptViews(d = {}) {
  const adapt = list => (list || []).map(v => ({
    org: v.org || v.institution,
    reportId: v.reportId || v.report_id,
    url: v.url || v.source_url || '#'
  }))
  // C 可能把"看平"叫 neutral，也可能叫 flat，两种都收
  return { bull: adapt(d.bull), bear: adapt(d.bear), neutral: adapt(d.neutral || d.flat) }
}
function adaptHistory(list = []) {
  return list.map(d => ({
    date: d.date,
    bull: d.bull, bear: d.bear, flat: d.flat,
    reports: d.reports ?? d.report_count,
    index: d.index ?? d.consensus_index
  }))
}
function adaptRanking(d = {}) {
  const pick = key => (d[key] || []).map(v => ({
    name: v.name || v.variety_name,
    value: Number(v.value ?? v.consensus_index)
  }))
  return { bull: pick('bull'), bear: pick('bear') }
}

// ---------- Plan B：B 用 Python 导出的静态 JSON ----------
let planBCache = null
async function planB() {
  if (!planBCache) {
    const { data } = await axios.get('/mock/dashboard.json')
    planBCache = data
  }
  return planBCache
}

function clone(v) {
  return JSON.parse(JSON.stringify(v))
}

// ---------- D2 验收辅助：造空数据 / 造单接口失败 ----------
const EMPTY = {
  varieties: [],
  overview: {},
  views: { bull: [], bear: [], neutral: [] },
  history: [],
  ranking: { bull: [], bear: [] }
}
function mockData(key, build) {
  return FORCE_EMPTY ? clone(EMPTY[key]) : clone(build())
}
async function simulate(label, build) {
  if (MOCK_DELAY) await new Promise(r => setTimeout(r, MOCK_DELAY))
  if (DATA_SOURCE === 'mock' && FAIL_LIST.includes(label)) {
    throw new Error('模拟失败（' + label + '）')
  }
  return build()
}

// ---------- 5 个接口（与 docs/接口约定.md 一一对应） ----------
export async function getVarieties() {
  if (DATA_SOURCE === 'mock') {
    return simulate('/varieties', () => mockData('varieties', () => mock.varieties))
  }
  if (DATA_SOURCE === 'planb') return adaptVarieties((await planB()).varieties)
  return adaptVarieties(unwrap(await http.get('/varieties')))
}

export async function getOverview(params = {}) {
  if (DATA_SOURCE === 'mock') {
    return simulate('/overview', () =>
      mockData('overview', () => adaptOverview(mock.buildOverview(params.variety, params.date))))
  }
  if (DATA_SOURCE === 'planb') return adaptOverview((await planB()).overview)
  return adaptOverview(unwrap(await http.get('/overview', { params })))
}

export async function getViews(params = {}) {
  if (DATA_SOURCE === 'mock') {
    return simulate('/views', () =>
      mockData('views', () => adaptViews(mock.buildViews(params.variety, params.date))))
  }
  if (DATA_SOURCE === 'planb') return adaptViews((await planB()).views)
  return adaptViews(unwrap(await http.get('/views', { params })))
}

export async function getHistory(params = {}) {
  if (DATA_SOURCE === 'mock') {
    return simulate('/history', () =>
      mockData('history', () => adaptHistory(mock.buildHistory(params.variety, params.start, params.end))))
  }
  if (DATA_SOURCE === 'planb') return adaptHistory((await planB()).history)
  return adaptHistory(unwrap(await http.get('/history', { params })))
}

export async function getRanking(params = {}) {
  if (DATA_SOURCE === 'mock') {
    return simulate('/ranking', () =>
      mockData('ranking', () => adaptRanking(mock.buildRanking(params.variety, params.date))))
  }
  if (DATA_SOURCE === 'planb') return adaptRanking((await planB()).ranking)
  return adaptRanking(unwrap(await http.get('/ranking', { params })))
}
