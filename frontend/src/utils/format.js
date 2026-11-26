// 空数据统一显示 "--"，页面绝不白屏
export const EMPTY = '--'

export function isEmpty(v) {
  return v === null || v === undefined || v === '' || Number.isNaN(Number(v))
}

export function num(v, digits = 0) {
  return isEmpty(v) ? EMPTY : Number(v).toFixed(digits)
}

export function signed(v, digits = 1) {
  if (isEmpty(v)) return EMPTY
  const n = Number(v)
  return (n > 0 ? '+' : '') + n.toFixed(digits)
}

// 与 C 的口径保持一致：(看多 - 看空) / 覆盖机构数 × 100，保留 1 位小数
// N=0 时返回 null（不做除法），前端渲染成 "--"
export function consensusIndex(bull, bear, flat) {
  const b = Number(bull || 0)
  const s = Number(bear || 0)
  const f = Number(flat || 0)
  const total = b + s + f
  if (!total) return null
  return Math.round(((b - s) / total) * 1000) / 10
}

export function tone(v) {
  if (isEmpty(v)) return ''
  return Number(v) > 0 ? 'pos' : Number(v) < 0 ? 'neg' : ''
}

export function shortDate(d) {
  return d ? String(d).slice(5) : EMPTY
}
