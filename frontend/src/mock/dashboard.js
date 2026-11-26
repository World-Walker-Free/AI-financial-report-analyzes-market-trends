// 原型 index.html 里的 DATA 常量 → 按「品种 + 日期」动态生成的 Mock 数据
// D2 重点：切品种、切日期必须让 8 个区块的数字真的变，否则「联动」演不出来
// 所有 index 都用 consensusIndex() 现场算，保证与 C 的公式口径一致（D3 能手算对账）
import { consensusIndex } from '@/utils/format'

export const varieties = [
  { code: 'RB2405', name: '螺纹钢' },
  { code: 'I2405', name: '铁矿石' },
  { code: 'P2405', name: '棕榈油' }
]

export const dateRange = { start: '2024-03-01', end: '2024-03-29', min: '2024-03-18' }

// 10 个交易日：基础序列就是原型 DATA 里的那四组数
const dates = ['03-18', '03-19', '03-20', '03-21', '03-22', '03-25', '03-26', '03-27', '03-28', '03-29']
const base = {
  bull: [5, 6, 6, 7, 6, 5, 5, 4, 4, 4],
  bear: [5, 4, 5, 4, 5, 5, 6, 6, 6, 6],
  flat: [4, 4, 3, 3, 4, 4, 4, 4, 4, 4],
  reports: [30, 33, 28, 35, 31, 29, 36, 34, 32, 37]
}

// 每个品种在基础序列上叠一点偏移，制造「切过去数字确实不一样」的效果
// RB2405 = 原型原值（03-29 正好是 4/6/4 → -14.3，与手算一致）
const PROFILES = {
  RB2405: { bull: 0, bear: 0, flat: 0, reports: 0, orgAt: 0, rank: 0 },
  I2405: { bull: 2, bear: -1, flat: 0, reports: 6, orgAt: 3, rank: 8 },
  P2405: { bull: 3, bear: -2, flat: -1, reports: 12, orgAt: 6, rank: -6 }
}

const ORG_POOL = [
  '中信期货', '国泰君安', '永安期货', '申银万国', '海通期货', '一德期货', '光大期货',
  '兴业期货', '中粮期货', '长江期货', '中金财富', '五矿期货', '南华期货', '银河期货',
  '方正中期', '招商期货', '国投安信', '浙商期货', '华泰期货', '广发期货'
]

const BASE_BULL = [
  ['棕榈油', 50], ['铁矿石', 45.5], ['沪金', 40], ['豆粕', 36.4], ['菜籽油', 33.3],
  ['沪铜', 30], ['螺纹钢', 27.3], ['白糖', 25], ['棉花', 22.2], ['玻璃', 20]
]
const BASE_BEAR = [
  ['苹果', -80], ['玉米', -71.4], ['沥青', -70], ['聚乙烯', -66.7], ['聚丙烯', -66.7],
  ['PTA', -60], ['纯碱', -60], ['豆油', -57.1], ['白糖', -54.5], ['菜粕', -50]
]

const clamp = (n, lo, hi) => Math.min(hi, Math.max(lo, n))
const profileOf = code => PROFILES[code] || PROFILES.RB2405

// 某一天的完整指标（overview 与 history 共用，保证两处数字永远对得上）
function dayAt(i, code) {
  const p = profileOf(code)
  const bull = clamp(base.bull[i] + p.bull, 0, 99)
  const bear = clamp(base.bear[i] + p.bear, 0, 99)
  const flat = clamp(base.flat[i] + p.flat, 0, 99)
  const reports = clamp(base.reports[i] + p.reports, 0, 999)
  return {
    date: '2024-' + dates[i],
    bull, bear, flat, reports,
    index: consensusIndex(bull, bear, flat)
  }
}

function allDays(code) {
  return dates.map((_, i) => dayAt(i, code))
}

// 选到非交易日时，落到「最近一个交易日」，和真实后端行为一致
function pickDay(code, date) {
  const list = allDays(code)
  return list.filter(d => !date || d.date <= date).pop() || list[0]
}

export function buildHistory(variety, start, end) {
  return allDays(variety).filter(d =>
    (!start || d.date >= start) && (!end || d.date <= end)
  )
}

export function buildOverview(variety, date) {
  const list = allDays(variety)
  const hit = pickDay(variety, date)
  const i = list.findIndex(d => d.date === hit.date)
  const prev = i > 0 ? list[i - 1] : null
  return {
    date: hit.date,
    bull: hit.bull, bear: hit.bear, flat: hit.flat,
    institutions: hit.bull + hit.bear + hit.flat,
    coveredVarieties: 31,
    reports: hit.reports,
    parseRate: 98.7,
    index: hit.index,
    delta: prev ? {
      bull: hit.bull - prev.bull,
      bear: hit.bear - prev.bear,
      flat: hit.flat - prev.flat
    } : { bull: null, bear: null, flat: null },
    range: { start: dateRange.start, end: hit.date },
    totalReports: 3847,
    totalInstitutions: 86,
    totalVarieties: 31
  }
}

export function buildViews(variety, date) {
  const hit = pickDay(variety, date)
  const p = profileOf(variety)
  // 机构池按品种轮换，且列表长度严格等于当天家数（KPI 说 6 家就列 6 行，不穿帮）
  const pool = ORG_POOL.slice(p.orgAt).concat(ORG_POOL.slice(0, p.orgAt))
  let cursor = 0
  const take = (n, tag) => Array.from({ length: n }, (_, k) => {
    const org = pool[cursor++ % pool.length]
    const reportId = `${hit.date.replace(/-/g, '')}-${tag}${k + 1}`
    return {
      org,
      reportId,
      // Mock 阶段指向本地占位研报页，点击不会 404；D3 换成 C 返回的真实地址
      url: `/reports/sample.html?rid=${encodeURIComponent(reportId)}&org=${encodeURIComponent(org)}&date=${hit.date}`
    }
  })
  return {
    bull: take(hit.bull, 'B'),
    bear: take(hit.bear, 'S'),
    neutral: take(hit.flat, 'N')
  }
}

export function buildRanking(variety) {
  const p = profileOf(variety)
  const shift = v => Math.round(clamp(v + p.rank, -100, 100) * 10) / 10
  return {
    bull: BASE_BULL.map(([name, value]) => ({ name, value: shift(value) })),
    bear: BASE_BEAR.map(([name, value]) => ({ name, value: shift(value) }))
  }
}
