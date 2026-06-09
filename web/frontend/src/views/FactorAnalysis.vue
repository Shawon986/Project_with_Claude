<template>
  <div>
    <div class="page-header"><h2>{{ t('priceFactorAnalysis') }}</h2><p>{{ t('factorsDesc') }}</p></div>

    <div class="card-grid">
      <div class="stat-card"><div class="stat-label">{{ t('modelR2') }}</div><div class="stat-value text-cyan" style="font-size:28px">{{ regression.r_squared || '-' }}</div><div class="stat-sub">{{ t('goodnessOfFit') }}</div></div>
      <div class="stat-card"><div class="stat-label">{{ t('cvR2Mean') }}</div><div class="stat-value text-green" style="font-size:28px">{{ regression.cv_r2_mean || '-' }}</div><div class="stat-sub">{{ t('crossValidated') }}</div></div>
      <div class="stat-card"><div class="stat-label">{{ t('topPredictor') }}</div><div class="stat-value text-orange" style="font-size:18px">{{ topFeature || '-' }}</div><div class="stat-sub">{{ t('strongestDriver') }}</div></div>
      <div class="stat-card"><div class="stat-label">{{ t('sampleSize') }}</div><div class="stat-value text-purple" style="font-size:28px">{{ regression.n_observations || '-' }}</div><div class="stat-sub">{{ t('observations') }}</div></div>
    </div>

    <div class="section-card"><h3>{{ t('correlationHeatmap') }}</h3><div ref="heatmapChart" style="height:520px"></div></div>

    <div class="section-card"><h3>{{ t('regressionCoefficients') }}</h3><div ref="coefChart" style="height:480px"></div></div>

    <!-- ============================================ -->
    <!-- SIGNIFICANT FEATURES — RICH VISUAL SECTION -->
    <!-- ============================================ -->
    <div class="section-card" v-if="significantFeatures.length > 0">
      <h3>Significant Features <span class="sig-badge">p &lt; 0.05</span></h3>
      <p style="color:var(--text-muted);font-size:13px;margin-bottom:20px;">
        These features show statistically significant impact on housing prices. Each card visualizes the coefficient magnitude, direction, and confidence level.
      </p>

      <!-- Feature Impact Cards -->
      <div class="sig-grid">
        <div v-for="(f, i) in significantFeatures" :key="i" class="sig-card"
          :class="'sig-tier-'+(f.p_value<0.001?'critical':f.p_value<0.01?'high':f.p_value<0.05?'moderate':'low')"
          :style="{animationDelay:(i*60)+'ms',borderLeftColor:f.coefficient>0?'#F56C6C':'#67C23A'}">

          <!-- Feature Icon + Name -->
          <div class="sig-header">
            <div class="sig-icon" :style="{background:f.coefficient>0?'rgba(245,108,108,0.15)':'rgba(34,197,94,0.15)'}">
              <span>{{ featureIcons[f.feature] || '📊' }}</span>
            </div>
            <div class="sig-name-wrap">
              <div class="sig-name">{{ formatFeatureName(f.feature) }}</div>
              <div class="sig-direction" :class="f.coefficient>0?'dir-up':'dir-down'">
                {{ f.coefficient>0 ? '📈 ' + t('priceIncrease') : '📉 ' + t('priceDecrease') }}
              </div>
            </div>
            <div class="sig-rank">#{{ i+1 }}</div>
          </div>

          <!-- Coefficient Impact Bar -->
          <div class="sig-impact">
            <div class="sig-impact-bar-wrap">
              <div class="sig-impact-bar" :class="f.coefficient>0?'bar-positive':'bar-negative'"
                :style="{width:impactWidth(f.coefficient)+'%'}">
                <div class="sig-impact-glow"></div>
              </div>
            </div>
            <div class="sig-impact-value" :class="f.coefficient>0?'val-positive':'val-negative'">
              {{ f.coefficient>0?'+':'' }}{{ f.coefficient }}
            </div>
          </div>

          <!-- Stats Row -->
          <div class="sig-stats">
            <div class="sig-stat-mini">
              <span class="ssm-label">{{ t('coefficient') }}</span>
              <span class="ssm-val" :style="{color:f.coefficient>0?'#F56C6C':'#67C23A'}">{{ f.coefficient }}</span>
            </div>
            <div class="sig-stat-mini">
              <span class="ssm-label">{{ t('stdError') }}</span>
              <span class="ssm-val">{{ f.std_error }}</span>
            </div>
            <div class="sig-stat-mini">
              <span class="ssm-label">{{ t('tStatistic') }}</span>
              <span class="ssm-val">{{ f.t_statistic }}</span>
            </div>
            <div class="sig-stat-mini">
              <span class="ssm-label">{{ t('pValue') }}</span>
              <span class="ssm-val pval" :class="'pval-'+(f.p_value<0.001?'critical':f.p_value<0.01?'high':'moderate')">
                {{ f.p_value }}
                <span class="pval-stars">{{ f.p_value<0.001?'★★★':f.p_value<0.01?'★★':'★' }}</span>
              </span>
            </div>
          </div>

          <!-- Significance Level Bar -->
          <div class="sig-level">
            <div class="sig-level-track">
              <div class="sig-level-fill" :class="'level-'+(f.p_value<0.001?'critical':f.p_value<0.01?'high':'moderate')"
                :style="{width:sigLevelPct(f.p_value)+'%'}"></div>
            </div>
            <div class="sig-level-labels">
              <span>p=1.0</span><span>p=0.05</span><span>p=0.01</span><span>p=0</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Summary Insight -->
      <div class="sig-summary">
        <div class="sig-summary-icon">💡</div>
        <div class="sig-summary-text">
          <strong>{{ significantFeatures.length }}</strong> features are statistically significant at p &lt; 0.05.
          <strong style="color:#F56C6C;">{{ positiveCount }}</strong> features push prices up,
          <strong style="color:#67C23A;">{{ negativeCount }}</strong> features push prices down.
          The strongest effect is from <strong style="color:var(--accent-cyan);">{{ topFeatureName }}</strong>
          (coefficient: <strong>{{ topFeatureCoef }}</strong>, p={{ topFeaturePval }}).
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div class="section-card" v-else>
      <h3>{{ t('significantFeatures') }}</h3>
      <div style="text-align:center;padding:40px;color:var(--text-muted);">
        <span style="font-size:40px;display:block;margin-bottom:12px;">🔬</span>
        <p>No significant features detected at p &lt; 0.05</p>
        <p style="font-size:12px;">Try running the regression analysis first from the command line.</p>
      </div>
    </div>

    <div class="scatter-grid">
      <div class="section-card"><h3>{{ t('areaVsTotalPrice') }}</h3><div ref="areaPriceChart" style="height:400px"></div></div>
      <div class="section-card"><h3>Building Age vs Unit Price</h3><div ref="agePriceChart" style="height:400px"></div></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import * as echarts from 'echarts'
import { getFactorAnalysis, getChartData } from '../api'
import { useI18n } from '../i18n'
const { t } = useI18n()
const regression=ref({}), significantFeatures=ref([]), topFeature=ref('Floor Area')
const heatmapChart=ref(null), coefChart=ref(null), areaPriceChart=ref(null), agePriceChart=ref(null)
const da={axisLabel:{color:'#9ca3af',fontSize:10},nameTextStyle:{color:'#9ca3af'}}

const featureIcons = {
  floor_area:'📐', rooms:'🛏️', halls:'🛋️', total_floors:'🏢', building_age:'📅',
  decoration_level:'✨', floor_type_encoded:'🏗️', orientation_south:'☀️',
  near_subway:'🚇', floor_ratio:'📏',
}

function formatFeatureName(f) {
  const map={floor_area:'Floor Area',rooms:'Bedrooms',halls:'Living Rooms',total_floors:'Total Floors',
    building_age:'Building Age',decoration_level:'Decoration Level',floor_type_encoded:'Floor Type',
    orientation_south:'South-facing',near_subway:'Near Subway',floor_ratio:'Floor Ratio'}
  return map[f]||f.replace('district_','District: ')
}

const maxAbsCoef = computed(()=>{
  if(!significantFeatures.value.length)return 1
  return Math.max(...significantFeatures.value.map(f=>Math.abs(f.coefficient)))
})
function impactWidth(coef){return(Math.abs(coef)/maxAbsCoef.value*100)}
function sigLevelPct(p){return Math.max(0,Math.min(100,(1-Math.log10(Math.max(p,0.0001))/5)*100))}

const positiveCount=computed(()=>significantFeatures.value.filter(f=>f.coefficient>0).length)
const negativeCount=computed(()=>significantFeatures.value.filter(f=>f.coefficient<0).length)
const topFeatureName=computed(()=>significantFeatures.value[0]?formatFeatureName(significantFeatures.value[0].feature):'-')
const topFeatureCoef=computed(()=>significantFeatures.value[0]?.coefficient||'-')
const topFeaturePval=computed(()=>significantFeatures.value[0]?.p_value||'-')

onMounted(async()=>{
  try{const r=await getFactorAnalysis();const d=r.data;const o=d.regression?.ols||{};const l=d.regression?.linear||{};regression.value={...o,...l};significantFeatures.value=o.significant_features||[];const ac=l.all_coefficients||o.all_coefficients||[];if(ac.length>0)topFeature.value=formatFeatureName(ac[0]?.feature||'')
  if(coefChart.value&&ac.length>0){const c=echarts.init(coefChart.value);const t=ac.slice(0,15).reverse();const lm={floor_area:'Floor Area',rooms:'Bedrooms',halls:'Living Rooms',total_floors:'Total Floors',building_age:'Building Age',decoration_level:'Decoration Level',floor_type_encoded:'Floor Type',orientation_south:'South-facing',near_subway:'Near Subway',floor_ratio:'Floor Ratio'};c.setOption({tooltip:{trigger:'axis'},grid:{left:150,right:80,top:10,bottom:20},xAxis:{type:'value',name:'Coefficient',...da},yAxis:{type:'category',data:t.map(f=>lm[f.feature]||f.feature.replace('district_','')),...da},series:[{type:'bar',data:t.map(f=>({value:f.coefficient,itemStyle:{color:f.coefficient>=0?'#F56C6C':'#67C23A'}})),label:{show:true,position:'right',color:'#9ca3af',fontSize:10}}]})}}catch(e){console.error(e)}
  try{const hr=await getChartData('correlation_heatmap');if(hr.data?.type==='heatmap'){const c=echarts.init(heatmapChart.value);c.setOption({tooltip:{position:'top'},grid:{left:120,right:40,top:20,bottom:80},xAxis:{type:'category',data:hr.data.xLabels,axisLabel:{rotate:45,color:'#9ca3af',fontSize:9}},yAxis:{type:'category',data:hr.data.yLabels,axisLabel:{color:'#9ca3af',fontSize:9}},visualMap:{min:-1,max:1,calculable:true,orient:'horizontal',left:'center',bottom:0,textStyle:{color:'#9ca3af'},inRange:{color:['#313695','#4575b4','#74add1','#e0f3f8','#ffffbf','#fee090','#f46d43','#d73027','#a50026']}},series:[{type:'heatmap',data:hr.data.data,label:{show:true,fontSize:8},emphasis:{itemStyle:{shadowBlur:10,shadowColor:'rgba(0,0,0,0.5)'}}}]})}}catch(e){}
  try{const ar=await getChartData('area_vs_total_price');if(ar.data?.data){echarts.init(areaPriceChart.value).setOption({tooltip:{trigger:'item'},grid:{left:60,right:20,top:10,bottom:45},xAxis:{type:'value',name:'Area (sqm)',...da},yAxis:{type:'value',name:'Total Price',...da},series:[{type:'scatter',data:ar.data.data.map(d=>[d.x,d.y]),symbolSize:4,itemStyle:{color:'#409EFF',opacity:0.5}}]})}}catch(e){}
  try{const br=await getChartData('building_age_vs_unit_price');if(br.data?.data){echarts.init(agePriceChart.value).setOption({tooltip:{trigger:'item'},grid:{left:60,right:20,top:10,bottom:45},xAxis:{type:'value',name:'Age (yr)',...da},yAxis:{type:'value',name:'Unit Price',...da},series:[{type:'scatter',data:br.data.data.map(d=>[d.x,d.y]),symbolSize:4,itemStyle:{color:'#67C23A',opacity:0.5}}]})}}catch(e){}
})
</script>

<style scoped>
/* Section badge */
.sig-badge {
  display:inline-block;padding:3px 10px;border-radius:6px;
  background:rgba(64,158,255,0.12);color:var(--accent-cyan);font-size:11px;
  font-weight:600;letter-spacing:0.5px;vertical-align:middle;margin-left:8px;
}

/* Feature Cards Grid */
.sig-grid {
  display:grid;grid-template-columns:repeat(auto-fill,minmax(380px,1fr));gap:14px;
  margin-bottom:20px;
}

/* Individual Feature Card */
.sig-card {
  background:rgba(20,25,35,0.5);border:1px solid rgba(255,255,255,0.04);
  border-left:3px solid;border-radius:14px;padding:18px 20px;
  transition:all 0.4s cubic-bezier(0.23,1,0.32,1);
  animation:sig-slide-in 0.5s ease-out both;
  position:relative;overflow:hidden;
}
.sig-card::after {
  content:'';position:absolute;top:0;right:0;width:120px;height:120px;
  background:radial-gradient(circle,rgba(64,158,255,0.03),transparent 70%);
  pointer-events:none;
}
.sig-card:hover {
  transform:translateY(-4px);border-color:rgba(255,255,255,0.1);
  box-shadow:0 12px 40px rgba(0,0,0,0.4);
}
@keyframes sig-slide-in {
  from {opacity:0;transform:translateY(20px)}
  to {opacity:1;transform:translateY(0)}
}

/* Header Row */
.sig-header {display:flex;align-items:center;gap:12px;margin-bottom:14px}
.sig-icon {width:42px;height:42px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:20px;flex-shrink:0}
.sig-name-wrap{flex:1}
.sig-name{font-size:15px;font-weight:700;color:#fff}
.sig-direction{font-size:11px;margin-top:2px}
.dir-up{color:#F56C6C}.dir-down{color:#67C23A}
.sig-rank{font-size:22px;font-weight:900;color:rgba(255,255,255,0.06);letter-spacing:-1px}

/* Impact Bar */
.sig-impact{display:flex;align-items:center;gap:12px;margin-bottom:12px}
.sig-impact-bar-wrap{flex:1;height:10px;background:rgba(255,255,255,0.04);border-radius:5px;overflow:hidden}
.sig-impact-bar{height:100%;border-radius:5px;position:relative;transition:width 1s cubic-bezier(0.34,1.56,0.64,1);min-width:4px}
.bar-positive{background:linear-gradient(90deg,rgba(245,108,108,0.4),#F56C6C)}
.bar-negative{background:linear-gradient(90deg,rgba(34,197,94,0.4),#67C23A)}
.sig-impact-glow{position:absolute;right:0;top:0;width:20px;height:100%;border-radius:50%;filter:blur(6px)}
.bar-positive .sig-impact-glow{background:#F56C6C}.bar-negative .sig-impact-glow{background:#67C23A}
.sig-impact-value{font-size:18px;font-weight:800;min-width:70px;text-align:right}
.val-positive{color:#F56C6C}.val-negative{color:#67C23A}

/* Mini Stats */
.sig-stats{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:8px;margin-bottom:12px}
.sig-stat-mini{padding:8px 10px;background:rgba(255,255,255,0.02);border-radius:8px;text-align:center}
.ssm-label{display:block;font-size:9px;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:2px}
.ssm-val{font-size:13px;font-weight:700;color:#c8cdd5}
.pval-critical{color:#F56C6C!important}.pval-high{color:#E6A23C!important}.pval-moderate{color:#409EFF!important}
.pval-stars{font-size:9px;margin-left:3px}

/* Significance Level Bar */
.sig-level{margin-top:6px}
.sig-level-track{height:3px;background:rgba(255,255,255,0.04);border-radius:2px;overflow:hidden}
.sig-level-fill{height:100%;border-radius:2px;transition:width 1s ease}
.level-critical{background:#F56C6C}.level-high{background:#E6A23C}.level-moderate{background:#409EFF}
.sig-level-labels{display:flex;justify-content:space-between;font-size:8px;color:var(--text-muted);margin-top:3px}

/* Summary */
.sig-summary{display:flex;gap:14px;padding:16px 20px;background:rgba(64,158,255,0.04);border:1px solid rgba(64,158,255,0.1);border-radius:14px;margin-top:20px;align-items:flex-start}
.sig-summary-icon{font-size:22px;flex-shrink:0;margin-top:1px}
.sig-summary-text{font-size:13px;color:var(--text-secondary);line-height:1.8}

/* Scatter chart grid */
.scatter-grid{display:grid;grid-template-columns:1fr 1fr;gap:20px}

/* =============================================
   MOBILE RESPONSIVE
   ============================================= */
@media(max-width:768px){
  /* Cards */
  .sig-grid{grid-template-columns:1fr !important;gap:10px !important}
  .sig-card{padding:14px 15px !important}
  .sig-stats{grid-template-columns:1fr 1fr !important;gap:6px !important}
  .sig-stat-mini{padding:6px 8px !important}
  .ssm-val{font-size:11px !important}

  /* Header */
  .sig-name{font-size:13px !important}
  .sig-rank{font-size:16px !important}
  .sig-impact-value{font-size:14px !important;min-width:55px !important}

  /* Charts — stack vertically */
  .scatter-grid{grid-template-columns:1fr !important}

  /* Heatmap */
  [ref="heatmapChart"]{height:350px !important}
  /* Coefficient chart */
  [ref="coefChart"]{height:340px !important}

  /* Scatter charts */
  [ref="areaPriceChart"],[ref="agePriceChart"]{height:280px !important}

  /* Summary */
  .sig-summary{flex-direction:column !important;padding:14px !important;gap:8px !important}
  .sig-summary-icon{font-size:18px !important}
  .sig-summary-text{font-size:12px !important}

  /* Stat cards */
  .card-grid{grid-template-columns:1fr 1fr !important}
  .stat-card{padding:14px !important}
  .stat-value{font-size:20px !important}
  .stat-sub{font-size:10px !important}

  /* Section header */
  .sig-badge{font-size:9px !important;padding:2px 7px !important}
}
</style>
