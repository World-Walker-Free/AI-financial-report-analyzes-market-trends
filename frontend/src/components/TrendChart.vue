<template>
  <div class="card">
    <div class="card-h">
      <h3>观点家数与一致性预期指数走势</h3>
      <div class="legend">
        <span><i style="background:#f08c3a"></i>看多</span>
        <span><i style="background:#aab2bd"></i>看平</span>
        <span><i style="background:#2fa96b"></i>看空</span>
        <span><i style="background:#2f6bff;height:2px;border-radius:1px"></i>一致性预期指数（右轴）</span>
      </div>
    </div>
    <div ref="chart" class="chart"></div>
    <div v-if="!history.length" class="empty-mask">--</div>
    <div v-if="loading" class="loading-mask">加载中…</div>
  </div>
</template>

<script>
import { createChart } from '@/utils/echarts'
import { shortDate, consensusIndex, isEmpty } from '@/utils/format'

export default {
  name: 'TrendChart',
  props: {
    history: { type: Array, default: () => [] },
    loading: { type: Boolean, default: false }
  },
  data() { return { holder: null } },
  watch: { history: 'render' },
  mounted() { this.holder = createChart(this.$refs.chart); this.render() },
  beforeDestroy() { if (this.holder) this.holder.destroy() },
  methods: {
    render() {
      if (!this.holder) return
      const rows = this.history || []
      const indexOf = r => isEmpty(r.index) ? consensusIndex(r.bull, r.bear, r.flat) : r.index
      // 左轴自适应：原型写死 12，真实数据超过 12 家时柱子会被裁掉
      const peak = rows.reduce((m, r) =>
        Math.max(m, Number(r.bull) || 0, Number(r.bear) || 0, Number(r.flat) || 0), 0)
      const yMax = Math.max(12, Math.ceil(peak / 3) * 3)
      this.holder.setOption({
        grid: { left: 42, right: 52, top: 14, bottom: 22, containLabel: false },
        legend: { show: false },
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(31,35,41,.92)', borderWidth: 0,
          textStyle: { color: '#fff', fontSize: 11 },
          formatter: params => {
            const i = params[0].dataIndex
            const r = rows[i]
            if (!r) return ''
            const v = indexOf(r)
            return `<b>${r.date}</b><br/>看多 / 看空 / 看平：${r.bull} / ${r.bear} / ${r.flat}<br/>当日研报数：${r.reports} 份<br/>一致性预期指数：${v === null ? '--' : (v > 0 ? '+' : '') + v}`
          }
        },
        xAxis: {
          type: 'category', data: rows.map(r => shortDate(r.date)),
          axisTick: { show: false }, axisLine: { lineStyle: { color: '#e6e9ee' } },
          axisLabel: { color: '#98a1ad', fontSize: 9.5 }
        },
        yAxis: [
          {
            type: 'value', min: 0, max: yMax, interval: 3,
            splitLine: { lineStyle: { color: '#eef0f3' } },
            axisLabel: { color: '#98a1ad', fontSize: 10, fontFamily: 'Bahnschrift' }
          },
          {
            type: 'value', min: -100, max: 100, interval: 50,
            splitLine: { show: false },
            axisLabel: { color: '#98a1ad', fontSize: 10, fontFamily: 'Bahnschrift' }
          }
        ],
        series: [
          { name: '看多', type: 'bar', barMaxWidth: 9, data: rows.map(r => r.bull), itemStyle: { color: '#f08c3a', borderRadius: [2, 2, 0, 0] } },
          { name: '看平', type: 'bar', barMaxWidth: 9, data: rows.map(r => r.flat), itemStyle: { color: '#aab2bd', borderRadius: [2, 2, 0, 0] } },
          { name: '看空', type: 'bar', barMaxWidth: 9, data: rows.map(r => r.bear), itemStyle: { color: '#2fa96b', borderRadius: [2, 2, 0, 0] } },
          {
            name: '一致性预期指数', type: 'line', yAxisIndex: 1,
            data: rows.map(indexOf), symbol: 'circle', symbolSize: 6,
            lineStyle: { color: '#2f6bff', width: 2 },
            itemStyle: { color: '#fff', borderColor: '#2f6bff', borderWidth: 2 },
            markLine: {
              silent: true, symbol: 'none',
              data: [{ yAxis: 0 }],
              lineStyle: { color: '#d7dce3', type: 'dashed', width: 1 },
              label: { show: false }
            }
          }
        ]
      })
    }
  }
}
</script>
