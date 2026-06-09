<template>
  <div>
    <div class="page-header"><h2>{{ t('listingClassification') }}</h2><p>{{ t('classificationDesc') }}</p></div>

    <div class="card-grid">
      <div class="stat-card"><div class="stat-label">{{ t('clustersIdentified') }}</div><div class="stat-value text-cyan">{{ nClusters }}</div><div class="stat-sub">{{ t('distinctSegments') }}</div></div>
      <div class="stat-card"><div class="stat-label">{{ t('ldaAccuracy') }}</div><div class="stat-value text-green" style="font-size:24px">{{ discriminant?.accuracy || '-' }}</div><div class="stat-sub">{{ t('classificationPrecision') }}</div></div>
      <div class="stat-card"><div class="stat-label">{{ t('cvAccuracy') }}</div><div class="stat-value text-purple" style="font-size:24px">{{ discriminant?.cv_accuracy_mean || '-' }}</div><div class="stat-sub">Cross-validated</div></div>
      <div class="stat-card"><div class="stat-label">{{ t('totalClassified') }}</div><div class="stat-value text-orange" style="font-size:28px">{{ totalClassified }}</div><div class="stat-sub">{{ t('listingsAcross') }}</div></div>
    </div>

    <!-- Elbow Method — rendered first to avoid v-if timing issues -->
    <div class="section-card">
      <h3>{{ t('elbowMethod') }}</h3>
      <p style="color:var(--text-muted);font-size:13px;margin-bottom:12px;">The "elbow" point indicates the optimal number of clusters. K={{ nClusters }} selected where inertia reduction slows significantly.</p>
      <div ref="elbowChart" style="height:420px"></div>
    </div>

    <div class="section-card" v-if="clusterProfiles.length > 0">
      <h3>{{ t('clusterProfiles') }}</h3>
      <div style="display:grid;grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px; margin-bottom:20px;">
        <div v-for="(c, idx) in clusterProfiles" :key="idx" class="section-card" style="margin-bottom:0;cursor:pointer;border-top:3px solid;" :style="{borderTopColor:colors[idx%5]}">
          <div style="font-size:15px;font-weight:700;color:#fff;margin-bottom:8px;">{{ clusterLabels[c.cluster_id] || 'Cluster '+(c.cluster_id+1) }}</div>
          <div style="color:var(--text-muted);font-size:12px;margin-bottom:4px;">{{ c.size }} listings ({{ c.pct }}%)</div>
          <div style="color:var(--accent-cyan);font-weight:700;font-size:16px;">{{ c.avg_total_price?.toLocaleString() }} <small style="font-size:11px;color:var(--text-muted)">(10k RMB)</small></div>
          <div style="color:var(--text-secondary);font-size:12px;margin-top:6px;">{{ c.avg_area }}sqm | {{ c.avg_building_age }}yr | {{ c.avg_rooms }}BR</div>
        </div>
      </div>
      <div ref="clusterChart" style="height:480px"></div>
    </div>

    <div class="section-card" v-if="clusterProfiles.length > 0">
      <h3>{{ t('detailedCluster') }}</h3>
      <el-table :data="clusterProfiles" stripe border size="small">
        <el-table-column label="Cluster" width="160"><template #default="{ row }"><el-tag :type="['primary','success','warning','danger','info'][row.cluster_id%5]" size="default" effect="dark">{{ clusterLabels[row.cluster_id] || 'Cluster '+(row.cluster_id+1) }}</el-tag></template></el-table-column>
        <el-table-column prop="size" label="Count" width="80" /><el-table-column prop="pct" label="Share" width="70"><template #default="{ row }">{{ row.pct }}%</template></el-table-column>
        <el-table-column prop="avg_total_price" label="Avg Total Price" width="160"><template #default="{ row }">{{ row.avg_total_price?.toLocaleString() }} (10k RMB)</template></el-table-column>
        <el-table-column prop="avg_unit_price" label="Avg Unit Price" width="170"><template #default="{ row }">{{ row.avg_unit_price?.toLocaleString() }} RMB/sqm</template></el-table-column>
        <el-table-column prop="avg_area" label="Area (sqm)" width="110" /><el-table-column prop="avg_building_age" label="Age (yr)" width="100" />
        <el-table-column label="Top Districts" min-width="200"><template #default="{ row }"><el-tag v-for="(c,d) in row.top_districts||{}" :key="d" size="small" effect="dark" style="margin:2px">{{ d }} ({{ c }})</el-tag></template></el-table-column>
      </el-table>
    </div>

    <div class="section-card" v-if="discriminant?.feature_importance">
      <h3>{{ t('discriminantFeature') }}</h3>
      <p style="color:var(--text-muted);font-size:13px;margin-bottom:12px;">Features ranked by their importance in discriminating between listing clusters. Higher percentages indicate stronger distinguishing power.</p>
      <el-table :data="discriminant.feature_importance||[]" stripe border size="small">
        <el-table-column prop="feature" label="Feature" width="250" />
        <el-table-column prop="importance" label="Importance Score" width="350">
          <template #default="{ row }">
            <el-progress :percentage="Math.min(row.importance*100, 100)" :stroke-width="18" :color="progressColor(row.importance)">
              <span style="color:#fff;font-size:11px;font-weight:600;">{{ (row.importance*100).toFixed(1) }}%</span>
            </el-progress>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import * as echarts from 'echarts'
import { getClusterAnalysis, getChartData } from '../api'
import { useI18n } from '../i18n'
const { t } = useI18n()

const clusteringData = ref(null)
const discriminant = ref(null)
const clusterProfiles = ref([])
const clusterLabels = ref({})
const clusterChart = ref(null)
const elbowChart = ref(null)
const colors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#00d4ff']
const nClusters = computed(() => clusteringData.value?.n_clusters || 5)
const totalClassified = computed(() => clusterProfiles.value.reduce((s, c) => s + c.size, 0))
const da = { axisLabel: { color: '#9ca3af' }, nameTextStyle: { color: '#9ca3af' } }

function progressColor(val) {
  if (val > 0.15) return '#409EFF'
  if (val > 0.08) return '#67C23A'
  if (val > 0.04) return '#E6A23C'
  return '#909399'
}

// Watch for data + render elbow chart after DOM update
watch([clusteringData], async () => {
  if (!clusteringData.value?.inertias) return
  await nextTick()
  if (elbowChart.value) {
    const c = echarts.init(elbowChart.value)
    c.setOption({
      tooltip: { trigger: 'axis', formatter: p => `K=${p[0].axisValue}<br/>Inertia: ${p[0].value.toFixed(0)}` },
      grid: { left: 70, right: 30, top: 20, bottom: 40 },
      xAxis: { type: 'category', data: clusteringData.value.k_range, name: 'K (Number of Clusters)', ...da },
      yAxis: { type: 'value', name: 'Inertia (WCSS)', ...da },
      series: [{
        type: 'line',
        data: clusteringData.value.inertias.map((v, i) => ({
          value: v,
          symbolSize: i === (clusteringData.value.n_clusters - 1) ? 14 : 6,
          itemStyle: { color: i === (clusteringData.value.n_clusters - 1) ? '#F56C6C' : '#409EFF' },
        })),
        markLine: {
          silent: true,
          symbol: 'none',
          lineStyle: { type: 'dashed', color: '#F56C6C' },
          data: [{ xAxis: clusteringData.value.n_clusters - 1, label: { formatter: `K=${clusteringData.value.n_clusters}`, color: '#F56C6C' } }],
        },
        smooth: true,
        symbolSize: 8,
      }],
    })
  }
})

// Watch for cluster profiles + render cluster scatter after DOM update
watch([clusterProfiles], async () => {
  if (!clusterProfiles.value.length) return
  await nextTick()
  try {
    const cs = await getChartData('cluster_results')
    if (cs.data?.type === 'multi-scatter' && clusterChart.value) {
      const c = echarts.init(clusterChart.value)
      c.setOption({
        tooltip: { trigger: 'item' },
        legend: { data: cs.data.series.map(s => s.name), textStyle: { color: '#9ca3af' }, top: 5 },
        grid: { left: 65, right: 25, top: 40, bottom: 50 },
        xAxis: { type: 'value', name: cs.data.xLabel, ...da },
        yAxis: { type: 'value', name: cs.data.yLabel, ...da },
        series: cs.data.series.map(s => ({
          type: 'scatter', name: s.name,
          data: s.data.map(d => [d.x, d.y]),
          symbolSize: 6, itemStyle: { color: s.color, opacity: 0.6 },
        })),
      })
    }
  } catch (e) { console.error(e) }
})

onMounted(async () => {
  try {
    const r = await getClusterAnalysis()
    discriminant.value = r.data.discriminant?.lda || {}
    clusterLabels.value = r.data.clustering?.cluster_labels || {}
    clusteringData.value = r.data.clustering || {}
    clusterProfiles.value = r.data.clustering?.cluster_profiles || []
  } catch (e) { console.error('Failed to load cluster data:', e) }
})
</script>
