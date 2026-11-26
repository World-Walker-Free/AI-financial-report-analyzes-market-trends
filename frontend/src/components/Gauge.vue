<template>
  <div class="card">
    <div class="card-h"><h3>一致性预期指数</h3><span class="hint">{{ date || '--' }}</span></div>
    <div class="gauge-wrap">
      <div ref="chart" class="chart"></div>
      <div class="gauge-legend">
        <span><i style="background:#2fa96b"></i>看空</span>
        <span><i style="background:#aab2bd"></i>中性</span>
        <span><i style="background:#f08c3a"></i>看多</span>
        <span style="margin-left:auto">公式：(看多-看空)/总数 × 100</span>
      </div>
    </div>
    <div v-if="isEmpty(value)" class="empty-mask">--</div>
    <div v-if="loading" class="loading-mask">加载中…</div>
  </div>
</template>

<script>
import { createChart } from '@/utils/echarts'
import { isEmpty } from '@/utils/format'

export default {
  name: 'Gauge',
  props: {
    value: { type: Number, default: null },
    date: { type: String, default: '' },
    loading: { type: Boolean, default: false }
  },
  data() { return { holder: null } },
  watch: { value: 'render' },
  mounted() { this.holder = createChart(this.$refs.chart); this.render() },
  beforeDestroy() { if (this.holder) this.holder.destroy() },
  methods: {
    isEmpty,
    render() {
      if (!this.holder) return
      const empty = isEmpty(this.value)
      const v = empty ? 0 : this.value
      const label = empty ? '--' : (this.value > 0 ? '+' : '') + this.value.toFixed(1)
      this.holder.setOption({
        series: [{
          type: 'gauge',
          min: -100, max: 100,
          startAngle: 180, endAngle: 0,
          center: ['50%', '80%'], radius: '96%',
          axisLine: {
            lineStyle: {
              width: 14,
              color: [[0.25, '#2fa96b'], [0.75, '#cfd4da'], [1, '#f08c3a']]
            }
          },
          pointer: { show: !empty, length: '62%', width: 4, itemStyle: { color: '#1f2329' } },
          anchor: { show: !empty, size: 8, itemStyle: { color: '#fff', borderColor: '#1f2329', borderWidth: 2 } },
          axisTick: { show: false },
          splitLine: { length: 10, lineStyle: { color: '#d3d8df', width: 1 } },
          axisLabel: {
            distance: 18, fontSize: 10, color: '#98a1ad', fontFamily: 'Bahnschrift',
            formatter: val => [-100, -50, 0, 50, 100].indexOf(val) >= 0 ? val : ''
          },
          title: { show: false },
          detail: {
            offsetCenter: [0, '-14%'], fontSize: 30, fontWeight: 700,
            fontFamily: 'Bahnschrift',
            color: empty ? '#8b939e' : (v >= 0 ? '#d9741f' : '#218a55'),
            formatter: () => label
          },
          data: [{ value: v }]
        }],
        graphic: [{
          type: 'text', left: 'center', top: '58%',
          style: { text: '一致性预期指数', fill: '#98a1ad', fontSize: 10 }
        }]
      })
    }
  }
}
</script>
