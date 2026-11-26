<template>
  <section class="kpis">
    <div class="kpi bull">
      <div class="k">看多机构</div>
      <div class="v">{{ num(o.bull) }}<small>家</small></div>
      <div class="d">较上一交易日 <span :class="deltaClass(o.delta && o.delta.bull)">{{ signed(o.delta && o.delta.bull, 0) }}</span></div>
    </div>
    <div class="kpi bear">
      <div class="k">看空机构</div>
      <div class="v">{{ num(o.bear) }}<small>家</small></div>
      <div class="d">较上一交易日 <span :class="deltaClass(o.delta && o.delta.bear)">{{ signed(o.delta && o.delta.bear, 0) }}</span></div>
    </div>
    <div class="kpi neutral">
      <div class="k">看平机构</div>
      <div class="v">{{ num(o.flat) }}<small>家</small></div>
      <div class="d">较上一交易日 <span :class="deltaClass(o.delta && o.delta.flat)">{{ signed(o.delta && o.delta.flat, 0) }}</span></div>
    </div>
    <div class="kpi">
      <div class="k">覆盖品种 / 机构</div>
      <div class="v">{{ num(o.coveredVarieties) }}<small>个 / {{ num(o.institutions) }} 家</small></div>
      <div class="d">品种观点覆盖数</div>
    </div>
    <div class="kpi price">
      <div class="k">当日新增研报</div>
      <div class="v">{{ num(o.reports) }}<small>份</small></div>
      <div class="d">覆盖机构 {{ num(o.institutions) }} 家 · 解析成功率 {{ num(o.parseRate, 1) }}%</div>
    </div>
    <div class="kpi">
      <div class="k">一致性预期指数</div>
      <div class="v" :style="{ color: indexColor }">{{ signed(o.index, 1) }}</div>
      <div class="d">区间 [-100, 100] · {{ indexTone }}</div>
    </div>
  </section>
</template>

<script>
import { num, signed, isEmpty } from '@/utils/format'

export default {
  name: 'KpiCards',
  props: { overview: { type: Object, default: () => ({}) } },
  computed: {
    o() { return this.overview || {} },
    indexTone() {
      if (isEmpty(this.o.index)) return '暂无数据'
      return this.o.index > 0 ? '偏多' : this.o.index < 0 ? '偏空' : '中性'
    },
    indexColor() {
      if (isEmpty(this.o.index)) return '#8b939e'
      return this.o.index > 0 ? '#d9741f' : this.o.index < 0 ? '#218a55' : '#6b7280'
    }
  },
  methods: {
    num,
    signed,
    deltaClass(v) { return isEmpty(v) ? '' : (v > 0 ? 'up' : 'down') }
  }
}
</script>
