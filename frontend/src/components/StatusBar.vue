<template>
  <footer>
    <span>数据区间：{{ rangeText }}</span>
    <span>累计解析研报：<b style="color:#3f4652">{{ num(overview.totalReports) }}</b> 份</span>
    <span>覆盖机构：<b style="color:#3f4652">{{ num(overview.totalInstitutions) }}</b> 家</span>
    <span>覆盖品种：<b style="color:#3f4652">{{ num(overview.totalVarieties) }}</b> 个</span>
    <span class="sp">观点由 AI 抽取自公开研报，仅供研究参考，不构成投资建议</span>
    <span>v1.0.0</span>
  </footer>
</template>

<script>
import { num, EMPTY } from '@/utils/format'

export default {
  name: 'StatusBar',
  props: { overview: { type: Object, default: () => ({}) } },
  computed: {
    rangeText() {
      const r = this.overview.range || {}
      return r.start && r.end ? `${r.start} ~ ${r.end}` : EMPTY
    }
  },
  methods: { num }
}
</script>
