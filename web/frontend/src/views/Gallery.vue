<template>
  <div>
    <div class="page-header">
      <h2>{{ t('chartGallery') }}</h2>
      <p>{{ t('interactiveCharts') }}</p>
    </div>

    <!-- Full Screen Modal -->
    <el-dialog v-model="fullscreenVisible" :title="fullscreenTitle" fullscreen destroy-on-close class="dark-dialog">
      <div ref="fullscreenChart" style="width:100%;height:85vh;"></div>
    </el-dialog>

    <div class="gallery-grid">
      <div class="gallery-item" v-for="chart in chartList" :key="chart.id" @click="openFullscreen(chart)">
        <div class="gallery-item-header">
          <span class="gallery-item-title">{{ chart.name }}</span>
          <el-tag size="small" :type="chart.tagType" effect="dark">{{ chart.category }}</el-tag>
        </div>
        <div class="gallery-chart-wrap" :ref="el => setChartRef(chart.id, el)"></div>
      </div>
    </div>

    <!-- Mini Stats Row -->
    <div class="card-grid" style="margin-top: 24px;">
      <div class="stat-card">
        <div class="stat-label">{{ t('totalCharts') }}</div>
        <div class="stat-value text-cyan">{{ chartList.length }}</div>
        <div class="stat-sub">{{ t('interactiveVisualizations') }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">{{ t('chartTypeCount') }}</div>
        <div class="stat-value text-purple">4</div>
        <div class="stat-sub">Bar • Scatter • Heatmap • Multi-series</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">{{ t('dataPointsRendered') }}</div>
        <div class="stat-value text-green">3,455</div>
        <div class="stat-sub">Across all visualizations</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">{{ t('renderingEngine') }}</div>
        <div class="stat-value text-orange">ECharts</div>
        <div class="stat-sub">Apache ECharts 5.x</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getChartData } from '../api'
import { useI18n } from '../i18n'
const { t } = useI18n()

const fullscreenVisible = ref(false)
const fullscreenTitle = ref('')
const fullscreenChart = ref(null)

const chartRefs = {}

function setChartRef(id, el) {
  if (el) chartRefs[id] = el
}

const chartList = [
  { id: 'district_avg_unit_price', name: 'Avg Unit Price by District', category: 'Price', tagType: 'primary' },
  { id: 'total_price_distribution', name: 'Total Price Distribution', category: 'Price', tagType: 'primary' },
  { id: 'area_vs_total_price', name: 'Floor Area vs Total Price', category: 'Correlation', tagType: 'success' },
  { id: 'building_age_vs_unit_price', name: 'Building Age vs Unit Price', category: 'Correlation', tagType: 'success' },
  { id: 'avg_price_by_layout', name: 'Avg Total Price by Layout', category: 'Price', tagType: 'primary' },
  { id: 'avg_price_by_decoration', name: 'Avg Unit Price by Decoration', category: 'Feature', tagType: 'warning' },
  { id: 'correlation_heatmap', name: 'Correlation Heatmap', category: 'Advanced', tagType: 'danger' },
  { id: 'regression_results', name: 'Regression Coefficients', category: 'Advanced', tagType: 'danger' },
  { id: 'pca_factor_scores', name: 'PCA Explained Variance', category: 'Advanced', tagType: 'danger' },
  { id: 'cluster_results', name: 'Clustering Results', category: 'Advanced', tagType: 'danger' },
]

function buildChartOption(data) {
  if (data.type === 'bar') {
    const isH = data.horizontal
    const colors = (data.y || []).map(v => v >= 0 ? '#c23531' : '#2f4554')
    const option = {
      backgroundColor: 'transparent',
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: isH ? { left: 100, right: 60, top: 10, bottom: 10 }
               : { left: 50, right: 20, top: 10, bottom: 50 },
      xAxis: isH ? { type: 'value', axisLabel: { color: '#9ca3af', fontSize: 10 } }
                 : { type: 'category', data: data.x, axisLabel: { rotate: 45, color: '#9ca3af', fontSize: 9 } },
      yAxis: isH ? { type: 'category', data: data.x, axisLabel: { color: '#9ca3af', fontSize: 10 } }
                 : { type: 'value', axisLabel: { color: '#9ca3af', fontSize: 10 } },
      series: [{
        type: 'bar', data: (data.y || []).map((v, i) => ({ value: v, itemStyle: { color: colors[i] } })),
        label: { show: false },
      }],
    }
    if (data.extraLine) {
      option.yAxis = [option.yAxis, { type: 'value', min: 0, max: 1, axisLabel: { color: '#9ca3af', fontSize: 9 } }]
      option.series.push({ type: 'line', data: data.extraLine, yAxisIndex: 1, itemStyle: { color: '#F56C6C' }, lineStyle: { type: 'dashed' }, symbol: 'none' })
    }
    return option
  }

  if (data.type === 'scatter') {
    return {
      backgroundColor: 'transparent',
      tooltip: { trigger: 'item', formatter: p => `${data.xLabel}: ${p.value[0]}<br/>${data.yLabel}: ${p.value[1]}` },
      grid: { left: 55, right: 25, top: 10, bottom: 40 },
      xAxis: { type: 'value', name: data.xLabel, nameTextStyle: { color: '#9ca3af', fontSize: 10 }, axisLabel: { color: '#9ca3af', fontSize: 9 } },
      yAxis: { type: 'value', name: data.yLabel, nameTextStyle: { color: '#9ca3af', fontSize: 10 }, axisLabel: { color: '#9ca3af', fontSize: 9 } },
      series: [{ type: 'scatter', data: (data.data || []).map(d => [d.x, d.y]), symbolSize: 4, itemStyle: { color: '#409EFF', opacity: 0.5 } }],
    }
  }

  if (data.type === 'multi-scatter') {
    return {
      backgroundColor: 'transparent',
      tooltip: { trigger: 'item' },
      legend: { data: (data.series || []).map(s => s.name), textStyle: { color: '#9ca3af', fontSize: 10 }, top: 5 },
      grid: { left: 55, right: 25, top: 35, bottom: 40 },
      xAxis: { type: 'value', name: data.xLabel, nameTextStyle: { color: '#9ca3af', fontSize: 10 }, axisLabel: { color: '#9ca3af', fontSize: 9 } },
      yAxis: { type: 'value', name: data.yLabel, nameTextStyle: { color: '#9ca3af', fontSize: 10 }, axisLabel: { color: '#9ca3af', fontSize: 9 } },
      series: (data.series || []).map(s => ({
        type: 'scatter', name: s.name, data: s.data.map(d => [d.x, d.y]),
        symbolSize: 5, itemStyle: { color: s.color, opacity: 0.6 },
      })),
    }
  }

  if (data.type === 'heatmap') {
    return {
      backgroundColor: 'transparent',
      tooltip: { position: 'top' },
      grid: { left: 90, right: 40, top: 10, bottom: 60 },
      xAxis: { type: 'category', data: data.xLabels, axisLabel: { rotate: 45, color: '#9ca3af', fontSize: 8 } },
      yAxis: { type: 'category', data: data.yLabels, axisLabel: { color: '#9ca3af', fontSize: 8 } },
      visualMap: { min: data.min, max: data.max, calculable: true, orient: 'horizontal', left: 'center', bottom: 0, textStyle: { color: '#9ca3af' },
        inRange: { color: ['#313695','#4575b4','#74add1','#e0f3f8','#ffffbf','#fee090','#f46d43','#d73027','#a50026'] } },
      series: [{ type: 'heatmap', data: data.data, label: { show: false }, emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.5)' } } }],
    }
  }

  return {}
}

async function loadAllCharts() {
  for (const chart of chartList) {
    try {
      const res = await getChartData(chart.id)
      if (res.data && chartRefs[chart.id]) {
        const existing = echarts.getInstanceByDom(chartRefs[chart.id])
        if (existing) existing.dispose()
        const instance = echarts.init(chartRefs[chart.id])
        instance.setOption(buildChartOption(res.data))
      }
    } catch (e) { console.error(`Failed to load ${chart.id}:`, e) }
  }
}

async function openFullscreen(chart) {
  fullscreenTitle.value = chart.name
  fullscreenVisible.value = true
  await nextTick()
  try {
    const res = await getChartData(chart.id)
    if (res.data && fullscreenChart.value) {
      // Dispose existing instance to avoid "dom already used" error
      const existing = echarts.getInstanceByDom(fullscreenChart.value)
      if (existing) existing.dispose()
      const instance = echarts.init(fullscreenChart.value)
      const opt = buildChartOption(res.data)
      opt.grid = opt.grid || {}
      if (opt.grid && !Array.isArray(opt.grid)) {
        opt.grid.left = 80; opt.grid.right = 60; opt.grid.top = 30; opt.grid.bottom = 60
      }
      instance.setOption(opt)
    }
  } catch (e) { console.error(e) }
}

onMounted(() => { loadAllCharts() })
</script>

<style scoped>
.dark-dialog :deep(.el-dialog) {
  background: var(--bg-primary);
}

.dark-dialog :deep(.el-dialog__header) {
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-glass);
  color: #fff;
}

.dark-dialog :deep(.el-dialog__body) {
  padding: 12px;
}

.dark-dialog :deep(.el-dialog__title) {
  color: #fff;
  font-size: 18px;
}
</style>
