<template>
  <div class="card">
    <div class="card-h">
      <h3>当日机构观点</h3>
      <span class="hint">共 <b>{{ total }}</b> 家机构 · 点击"查看原文"溯源</span>
    </div>
    <div class="views">
      <div v-for="col in columns" :key="col.key" class="view-col" :class="[col.key, { dim: isDim(col.key) }]">
        <div class="vh">
          <span class="n">{{ col.name }}</span>
          <span class="c">{{ num(col.list.length) }}</span>
          <span style="color:#98a1ad;font-size:10px">家</span>
          <span class="m">占比 {{ ratio(col.list.length) }}</span>
        </div>
        <div class="view-list">
          <div v-for="(item, i) in col.list" :key="item.reportId + i" class="view-item">
            <span class="nm" :title="item.org">{{ item.org }}</span>
            <a class="lk" :href="item.url" target="_blank" rel="noopener">查看原文</a>
          </div>
          <div v-if="!col.list.length" class="view-item" style="color:#aeb5bf">--</div>
        </div>
      </div>
    </div>
    <div v-if="loading" class="loading-mask">加载中…</div>
  </div>
</template>

<script>
import { num } from '@/utils/format'

export default {
  name: 'ViewColumns',
  props: {
    views: { type: Object, default: () => ({ bull: [], bear: [], neutral: [] }) },
    institution: { type: String, default: 'all' },
    loading: { type: Boolean, default: false }
  },
  computed: {
    columns() {
      const v = this.views || {}
      return [
        { key: 'bull', name: '看多', list: v.bull || [] },
        { key: 'bear', name: '看空', list: v.bear || [] },
        { key: 'neutral', name: '看平', list: v.neutral || [] }
      ]
    },
    total() { return this.columns.reduce((s, c) => s + c.list.length, 0) }
  },
  methods: {
    num,
    ratio(n) { return this.total ? (n / this.total * 100).toFixed(0) + '%' : '--' },
    isDim(key) {
      if (this.institution === 'all') return false
      const map = { bull: 'bull', bear: 'bear', flat: 'neutral' }
      return map[this.institution] !== key
    }
  }
}
</script>
