<template>
  <div>
    <div class="page-header"><h2>{{ t('pcaFactorEvaluation') }}</h2><p>{{ t('pcaDesc') }}</p></div>

    <div class="card-grid">
      <div class="stat-card"><div class="stat-label">{{ t('principalComponents') }}</div><div class="stat-value text-cyan">{{ pcaData.n_components || '-' }}</div><div class="stat-sub">{{ t('extractedComponents') }}</div></div>
      <div class="stat-card"><div class="stat-label">{{ t('cumulativeVariance') }}</div><div class="stat-value text-green">{{ cumulativeVar }}%</div><div class="stat-sub">{{ t('totalVariance') }}</div></div>
      <div class="stat-card"><div class="stat-label">{{ t('pc1Dominant') }}</div><div class="stat-value text-orange" style="font-size:18px">{{ topPC1Feature }}</div><div class="stat-sub">{{ t('strongestPC1') }}</div></div>
      <div class="stat-card"><div class="stat-label">{{ t('compositeScoreRange') }}</div><div class="stat-value text-purple" style="font-size:20px">{{ scoreRange }}</div><div class="stat-sub">{{ t('standardizedComposite') }}</div></div>
    </div>

    <div class="section-card" v-if="pcaData">
      <h3>{{ t('pcaExplained') }}</h3>
      <div ref="pcaChart" style="height:420px"></div>
      <h4 style="color:#fff;margin:20px 0 10px;">{{ t('componentLoadings') }}</h4>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
        <div v-for="(loadings, pc) in (pcaData.top_loadings || {})" :key="pc" class="section-card" style="margin-bottom:0;">
          <h4 style="font-size:14px;border:none;margin:0 0 12px 0;padding:0;">{{ pc }} Key Features</h4>
          <div v-for="(val, feat) in loadings" :key="feat" style="display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid var(--border-glass);">
            <span style="font-size:13px;color:var(--text-secondary)">{{ feat }}</span>
            <el-tag size="small" :type="val>0?'danger':'success'" effect="dark">{{ val.toFixed(3) }}</el-tag>
          </div>
        </div>
      </div>
    </div>
    <div v-else class="section-card"><el-empty description="{{ t('noPCAResults') }}" /></div>

    <div class="section-card">
      <h3>{{ t('factorAnalysis') }}</h3>
      <div v-if="faData && !faData.error">
        <div class="card-grid">
          <div class="stat-card"><div class="stat-label">KMO Value</div><div class="stat-value text-cyan" style="font-size:24px">{{ faData.kmo_model }}</div><div class="stat-sub">Sampling adequacy</div></div>
          <div class="stat-card"><div class="stat-label">Bartlett p-value</div><div class="stat-value text-green" style="font-size:24px">{{ faData.bartlett_pvalue }}</div><div class="stat-sub">Sphericity test</div></div>
        </div>
        <div ref="faChart" style="height:400px"></div>
      </div>
      <el-empty v-else description="{{ t('noFactorResults') }}" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import * as echarts from 'echarts'
import { getPCAAnalysis } from '../api'
import { useI18n } from '../i18n'
const { t } = useI18n()
const pcaData=ref({}), faData=ref({}), pcaChart=ref(null), faChart=ref(null)
const cumulativeVar=computed(()=>{const cv=pcaData.value.cumulative_variance;return cv?.length?(cv[cv.length-1]*100).toFixed(1):'-'})
const topPC1Feature=computed(()=>{const l=pcaData.value.top_loadings?.PC1;if(!l)return'-';return Object.entries(l).sort((a,b)=>Math.abs(b[1])-Math.abs(a[1]))[0]?.[0]||'-'})
const scoreRange=computed(()=>{const s=pcaData.value.composite_score;return s?`${s.min?.toFixed(2)} ~ ${s.max?.toFixed(2)}`:'-'})
const da={axisLabel:{color:'#9ca3af'},nameTextStyle:{color:'#9ca3af'}}
onMounted(async()=>{
  try{const r=await getPCAAnalysis();pcaData.value=r.data.pca||{};faData.value=r.data.factor_analysis||{}
  if(pcaChart.value&&pcaData.value.explained_variance_ratio){const c=echarts.init(pcaChart.value);const ev=pcaData.value.explained_variance_ratio;const cv2=pcaData.value.cumulative_variance;const pcs=ev.map((_,i)=>`PC${i+1}`);c.setOption({tooltip:{trigger:'axis'},legend:{data:['Explained','Cumulative'],textStyle:{color:'#9ca3af'}},xAxis:{type:'category',data:pcs,...da},yAxis:[{type:'value',name:'Ratio',...da},{type:'value',name:'Cumulative',min:0,max:1,...da}],series:[{name:'Explained',type:'bar',data:ev,itemStyle:{color:'#409EFF'},label:{show:true,formatter:p=>(p.value*100).toFixed(1)+'%',color:'#9ca3af'}},{name:'Cumulative',type:'line',yAxisIndex:1,data:cv2,itemStyle:{color:'#F56C6C'},label:{show:true,formatter:p=>(p.value*100).toFixed(1)+'%',color:'#9ca3af'}}]})}
  if(faChart.value&&faData.value.variance_explained){const c=echarts.init(faChart.value);const ve=faData.value.variance_explained;const cv3=faData.value.cumulative_variance;const fs=ve.map((_,i)=>`Factor${i+1}`);c.setOption({tooltip:{trigger:'axis'},legend:{data:['Contribution','Cumulative'],textStyle:{color:'#9ca3af'}},xAxis:{type:'category',data:fs,...da},yAxis:[{type:'value',name:'Ratio',...da},{type:'value',name:'Cumulative',min:0,max:1,...da}],series:[{name:'Contribution',type:'bar',data:ve,itemStyle:{color:'#67C23A'},label:{show:true,formatter:p=>(p.value*100).toFixed(1)+'%',color:'#9ca3af'}},{name:'Cumulative',type:'line',yAxisIndex:1,data:cv3,itemStyle:{color:'#E6A23C'},label:{show:true,formatter:p=>(p.value*100).toFixed(1)+'%',color:'#9ca3af'}}]})}}catch(e){console.error(e)}
})
</script>
