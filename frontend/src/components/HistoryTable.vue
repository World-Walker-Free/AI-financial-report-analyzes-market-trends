<template>
  <div class="card">
    <div class="card-h">
      <h3>历史观点与一致性预期</h3>
      <span class="hint">近 {{ limit }} 个交易日 · 数据每日 15:10 自动更新</span>
    </div>
    <table class="tbl">
      <colgroup>
        <col style="width:19%"><col style="width:10%"><col style="width:10%"><col style="width:10%">
        <col style="width:13%"><col style="width:17%"><col style="width:21%">
      </colgroup>
      <thead>
        <tr><th>报告日期</th><th>看多</th><th>看空</th><th>看平</th><th>覆盖机构</th><th>当日研报</th><th>一致性预期指数</th></tr>
      </thead>
      <tbody>
        <tr v-for="(row, i) in rows" :key="row.date" :class="{ cur: i === 0 }">
          <td>{{ row.date || '--' }}</td>
          <td>{{ num(row.bull) }} <span class="tag b">多</span></td>
          <td>{{ num(row.bear) }} <span class="tag s">空</span></td>
          <td>{{ num(row.flat) }} <span class="tag n">平</span></td>
          <td>{{ covered(row) }}</td>
          <td>{{ num(row.reports) }} 份</td>
          <td class="idx" :class="tone(row.index)">{{ signed(row.index, 1) }}</td>
        </tr>
        <tr v-if="!rows.length"><td colspan="7" style="text-align:center;color:#aeb5bf;padding:18px">--</td></tr>
      </tbody>
    </table>
    <div v-if="loading" class="loading-mask">加载中…</div>
  </div>
</template>

<script>
import { num, signed, tone, isEmpty } from '@/utils/format'

export default {
  name: 'HistoryTable',
  props: {
    history: { type: Array, default: () => [] },
    limit: { type: Number, default: 8 },
    loading: { type: Boolean, default: false }
  },
  computed: {
    rows() { return this.history.slice(-this.limit).reverse() }
  },
  methods: {
    num, signed, tone,
    covered(row) {
      if (isEmpty(row.bull) && isEmpty(row.bear) && isEmpty(row.flat)) return '--'
      return Number(row.bull || 0) + Number(row.bear || 0) + Number(row.flat || 0)
    }
  }
}
</script>
