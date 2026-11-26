import * as echarts from 'echarts'

// 统一处理 init / resize / dispose，避免每个图表组件各写一遍
// 原型里是 window.resize 直接 location.reload()，组件化后改成只重绘图表
export function createChart(el) {
  const chart = echarts.init(el)
  const resize = () => chart.resize()
  window.addEventListener('resize', resize)

  // 侧栏宽度、窗口尺寸变化时容器会变，ResizeObserver 比只监听 window 更可靠
  let ro = null
  if (typeof ResizeObserver !== 'undefined') {
    ro = new ResizeObserver(resize)
    ro.observe(el)
  }

  return {
    setOption(option) {
      chart.setOption(option, true)
    },
    destroy() {
      window.removeEventListener('resize', resize)
      if (ro) ro.disconnect()
      chart.dispose()
    }
  }
}

export { echarts }
