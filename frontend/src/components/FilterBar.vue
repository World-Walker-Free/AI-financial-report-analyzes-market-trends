<template>
  <header>
    <div class="brand">
      <div class="logo">AI</div>
      <div>
        <div class="t">AI 研报观点 · 市场走势看板</div>
        <div class="s">FUTURES RESEARCH CONSENSUS DASHBOARD</div>
      </div>
    </div>
    <nav>
      <a class="on" href="javascript:;">市场概览</a>
      <a href="javascript:;">机构观点</a>
      <a href="javascript:;">品种排行</a>
      <a href="javascript:;">研报库</a>
      <a href="javascript:;">数据设置</a>
    </nav>
    <div class="filters">
      <div class="field">
        <label>品种</label>
        <select :value="variety" @change="emitChange('variety', $event.target.value)">
          <option v-for="v in varieties" :key="v.code" :value="v.code">{{ v.name }} {{ v.code }}</option>
        </select>
      </div>
      <div class="field">
        <label>日期</label>
        <input
          type="date"
          :value="date"
          :min="range.min || range.start"
          :max="range.end"
          @change="emitChange('date', $event.target.value)"
        >
      </div>
      <div class="field">
        <label>机构</label>
        <select :value="institution" @change="emitChange('institution', $event.target.value)">
          <option value="all">全部机构</option>
          <option value="bull">仅看多</option>
          <option value="bear">仅看空</option>
          <option value="flat">仅看平</option>
        </select>
      </div>
      <button class="btn primary" :disabled="loading" @click="$emit('refresh')">
        {{ loading ? '加载中…' : '刷新数据' }}
      </button>
      <span class="updated"><i class="dot-live"></i>更新于 {{ updatedAt }}</span>
    </div>
  </header>
</template>

<script>
export default {
  name: 'FilterBar',
  props: {
    varieties: { type: Array, default: () => [] },
    variety: { type: String, default: '' },
    date: { type: String, default: '' },
    range: { type: Object, default: () => ({ start: '--', end: '--' }) },
    institution: { type: String, default: 'all' },
    updatedAt: { type: String, default: '--' },
    loading: { type: Boolean, default: false }
  },
  methods: {
    emitChange(key, value) {
      if (value) this.$emit('change', { key, value })
    }
  }
}
</script>
