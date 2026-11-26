<template>
  <div class="app-shell">
    <div class="topline"></div>

    <FilterBar
      :varieties="varieties"
      :variety="variety"
      :date="date"
      :range="range"
      :institution="institution"
      :updated-at="updatedAt"
      :loading="loading"
      @change="onFilter"
      @refresh="loadAll()"
    />

    <div v-if="error" class="err-bar">
      {{ error }}
      <button @click="loadAll()">重试</button>
      <button @click="error = ''">关闭</button>
    </div>

    <div v-if="toast" class="toast"><i class="dot-live"></i>{{ toast }}</div>

    <KpiCards :overview="overview" />

    <main>
      <div class="col-left">
        <div class="row1">
          <Gauge :value="overview.index" :date="overview.date" :loading="loading" />
          <ViewColumns :views="views" :institution="institution" :loading="loading" />
        </div>
        <HistoryTable :history="history" :loading="loading" />
        <TrendChart :history="history" :loading="loading" />
      </div>
      <aside>
        <RankingPanel type="bull" :list="ranking.bull" :loading="loading" />
        <RankingPanel type="bear" :list="ranking.bear" :loading="loading" />
      </aside>
    </main>

    <StatusBar :overview="overview" />
  </div>
</template>

<script>
import FilterBar from '@/components/FilterBar.vue'
import KpiCards from '@/components/KpiCards.vue'
import Gauge from '@/components/Gauge.vue'
import ViewColumns from '@/components/ViewColumns.vue'
import HistoryTable from '@/components/HistoryTable.vue'
import TrendChart from '@/components/TrendChart.vue'
import RankingPanel from '@/components/RankingPanel.vue'
import StatusBar from '@/components/StatusBar.vue'
import { getVarieties, getOverview, getViews, getHistory, getRanking } from '@/api'

export default {
  name: 'Dashboard',
  components: {
    FilterBar, KpiCards, Gauge, ViewColumns,
    HistoryTable, TrendChart, RankingPanel, StatusBar
  },
  data() {
    return {
      loading: false,
      error: '',
      toast: '',
      toastTimer: null,
      refreshSeq: 0,
      requestSeq: 0,          // 竞态保护：只认最后一次筛选的结果
      variety: 'RB2405',
      date: '2024-03-29',
      institution: 'all',
      range: { start: '2024-03-01', end: '2024-03-29', min: '2024-03-18' },
      updatedAt: '--',
      varieties: [],
      overview: {},
      views: { bull: [], bear: [], neutral: [] },
      history: [],
      ranking: { bull: [], bear: [] }
    }
  },
  mounted() { this.loadAll(true) },
  beforeDestroy() { if (this.toastTimer) clearTimeout(this.toastTimer) },
  methods: {
    onFilter({ key, value }) {
      this[key] = value
      this.loadAll(true)
    },
    showToast(text) {
      this.toast = text
      if (this.toastTimer) clearTimeout(this.toastTimer)
      this.toastTimer = setTimeout(() => { this.toast = '' }, 1800)
    },
    async loadAll(silent = false) {
      const seq = ++this.requestSeq
      this.loading = true
      this.error = ''
      const params = {
        variety: this.variety,
        date: this.date,
        start: this.range.start,
        end: this.date,
        institution: this.institution
      }

      // 五个接口各自独立：任意一个挂了，其余照常渲染，旧数据也保留
      const tasks = [
        { label: '/varieties', run: () => getVarieties(), apply: v => { this.varieties = v || [] } },
        { label: '/overview', run: () => getOverview(params), apply: v => { this.overview = v || {} } },
        { label: '/views', run: () => getViews(params), apply: v => { this.views = v || { bull: [], bear: [], neutral: [] } } },
        { label: '/history', run: () => getHistory(params), apply: v => { this.history = v || [] } },
        { label: '/ranking', run: () => getRanking(params), apply: v => { this.ranking = v || { bull: [], bear: [] } } }
      ]

      const settled = await Promise.allSettled(tasks.map(t => t.run()))

      // 快速连切筛选时，慢的旧响应不能盖掉新的；它也不许关掉新请求的 loading
      if (seq !== this.requestSeq) return

      const failed = []
      settled.forEach((r, i) => {
        if (r.status === 'fulfilled') tasks[i].apply(r.value)
        else failed.push(tasks[i].label)
      })

      if (failed.length) {
        this.error = `${failed.join('、')} 未返回；其余数据已更新，未返回的区块保留上一次数据`
      } else {
        this.refreshSeq++
        this.updatedAt = new Date().toLocaleTimeString('zh-CN', { hour12: false })
        // 同一秒内连点，时间字符串不变也要让用户看见「确实刷新了」
        if (!silent) this.showToast(`数据已刷新 · ${this.updatedAt} · 第 ${this.refreshSeq} 次`)
      }
      this.loading = false
    }
  }
}
</script>
