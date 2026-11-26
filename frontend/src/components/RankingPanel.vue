<template>
  <div class="card">
    <div class="card-h"><h3>{{ isBull ? '看多排行 TOP10' : '看空排行 TOP10' }}</h3><span class="hint">按一致性指数</span></div>
    <div ref="chart" class="chart"></div>
    <div v-if="!list.length" class="empty-mask">--</div>
    <div v-if="loading" class="loading-mask">加载中…</div>
  </div>
</template>

<script>
import { createChart, echarts } from '@/utils/echarts'

export default {
  name: 'RankingPanel',
  props: {
    type: { type: String, default: 'bull' }, // 'bull' | 'bear'
    list: { type: Array, default: () => [] },
    loading: { type: Boolean, default: false }
  },
  data() { return { holder: null } },
  computed: { isBull() { return this.type === 'bull' } },
  watch: { list: 'render' },
  mounted() { this.holder = createChart(this.$refs.chart); this.render() },
  beforeDestroy() { if (this.holder) this.holder.destroy() },
  methods: {
    render() {
      if (!this.holder) return
      const items = this.list.slice(0, 10).slice().reverse() // y 轴类目自下而上
      const color = this.isBull
        ? new echarts.graphic.LinearGradient(0, 0, 1, 0, [{ offset: 0, color: '#f6b878' }, { offset: 1, color: '#ee8a35' }])
        : new echarts.graphic.LinearGradient(0, 0, 1, 0, [{ offset: 0, color: '#2a9d63' }, { offset: 1, color: '#74c79b' }])
      this.holder.setOption({
        grid: { left: 6, right: 46, top: 4, bottom: 4, containLabel: true },
        tooltip: {
          trigger: 'item',
          backgroundColor: 'rgba(31,35,41,.92)', borderWidth: 0,
          textStyle: { color: '#fff', fontSize: 11 },
          formatter: p => `${p.name}<br/>一致性预期指数：<b>${p.value > 0 ? '+' : ''}${p.value}</b>`
        },
        xAxis: {
          type: 'value',
          min: this.isBull ? 0 : -100,
          max: this.isBull ? 100 : 0,
          show: false
        },
        yAxis: {
          type: 'category', data: items.map(i => i.name),
          axisTick: { show: false }, axisLine: { show: false },
          axisLabel: { color: '#2b3038', fontSize: 11.5, margin: 8 }
        },
        series: [{
          type: 'bar', data: items.map(i => i.value), barWidth: 8,
          showBackground: true, backgroundStyle: { color: '#f3f5f7', borderRadius: 2 },
          itemStyle: { color, borderRadius: 2 },
          label: {
            show: true,
            position: this.isBull ? 'right' : 'left',
            color: this.isBull ? '#d9741f' : '#218a55',
            fontSize: 11.5, fontFamily: 'Bahnschrift', fontWeight: 600,
            formatter: p => (p.value > 0 ? '+' : '') + p.value
          }
        }]
      })
    }
  }
}
</script>
