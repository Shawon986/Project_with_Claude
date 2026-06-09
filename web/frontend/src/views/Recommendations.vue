<template>
  <div>
    <div class="page-header"><h2>{{ t('homeBuyingGuide') }}</h2><p>{{ t('recommendationsDesc') }}</p></div>

    <div class="card-grid">
      <div class="stat-card"><div class="stat-label">{{ t('marketStatus') }}</div><div class="stat-value text-cyan" style="font-size:22px">{{ t('buyersMarket') }}</div><div class="stat-sub">{{ t('highInventory') }}</div></div>
      <div class="stat-card"><div class="stat-label">{{ t('bestValueDistrict') }}</div><div class="stat-value text-green" style="font-size:22px">{{ bestDistrict }}</div><div class="stat-sub">{{ t('lowestUnitPrice') }}</div></div>
      <div class="stat-card"><div class="stat-label">{{ t('priceModelR2') }}</div><div class="stat-value text-purple" style="font-size:22px">0.56</div><div class="stat-sub">{{ t('regressionFit') }}</div></div>
      <div class="stat-card"><div class="stat-label">{{ t('recommendations') }}</div><div class="stat-value text-orange" style="font-size:22px">{{ recommendations.length }}</div><div class="stat-sub">{{ t('dataBacked') }}</div></div>
    </div>

    <div v-if="recommendations.length > 0">
      <div v-for="(rec, idx) in recommendations" :key="idx" class="section-card" style="border-left:3px solid var(--border-accent);transition:all 0.3s ease;">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;">
          <div :style="{width:'40px',height:'40px',borderRadius:'10px',background:'var(--gradient-blue)',display:'flex',alignItems:'center',justifyContent:'center',color:'#fff'}">
            <el-icon :size="20"><component :is="iconMap[rec.icon]||'InfoFilled'" /></el-icon>
          </div>
          <strong style="font-size:17px;color:#fff;">{{ rec.title }}</strong>
        </div>
        <p style="line-height:1.8;color:var(--text-secondary);font-size:14px;padding-left:52px;">{{ rec.content }}</p>
      </div>
    </div>

    <div class="section-card"><h3>{{ t('keyDecisionPoints') }}</h3>
      <div class="dark-list" style="display:grid;grid-template-columns:1fr 1fr;gap:24px;">
        <div><strong>{{ t('budgetPlanning') }}</strong><br/>Median total price: ~200-300 (10k RMB). Mortgage should not exceed 40% of household income. Consider 30% down payment minimum.</div>
        <div><strong>{{ t('districtSelection') }}</strong><br/>Core districts have mature amenities at premium prices. Outer districts offer larger units for the same budget. Balance commute vs cost.</div>
        <div><strong>{{ t('unitSize') }}</strong><br/>90-120sqm is the market sweet spot. 3BR 2LR is the most common layout. Floor area is the strongest price predictor (top regression coefficient).</div>
        <div><strong>{{ t('buildingAgeDecision') }}</strong><br/>Newer homes (within 10yr) command a premium but offer better quality. Older homes (20yr+) are cheaper but face mortgage term limits and renovation costs.</div>
        <div><strong>{{ t('subwayAccess') }}</strong><br/>Properties near metro stations have stronger appreciation potential. Coverage is ~46% in Hangzhou. Premium for subway access: ~5-15%.</div>
        <div><strong>{{ t('decorationDecision') }}</strong><br/>Fine-decorated units cost 10-20% more. Unfinished units are ~20% cheaper but require significant renovation investment. Luxury finish adds ~30%.</div>
        <div><strong>{{ t('orientationDecision') }}</strong><br/>South-facing and North-South units are most desirable. East-West units are typically 5-10% cheaper. South-facing commands the highest premium.</div>
        <div><strong>{{ t('marketTiming') }}</strong><br/>Spring and autumn are peak transaction seasons. Winter typically has fewer listings but more motivated sellers. Compare historical prices per community.</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getRecommendations } from '../api'
import { useI18n } from '../i18n'
const { t } = useI18n()
const recommendations=ref([]), bestDistrict=ref('Yuhang')
const iconMap={overview:'DataAnalysis',district:'Location',area:'OfficeBuilding',age:'Clock',model:'TrendCharts',timing:'Timer',general:'Star'}
onMounted(async()=>{try{const r=await getRecommendations();recommendations.value=r.data.recommendations||[];if(r.data.recommendations)for(const rec of r.data.recommendations){if(rec.icon==='district'){const m=rec.content.match(/district\s+is\s+(\w+)/i);if(m)bestDistrict.value=m[1]}}}catch(e){console.error(e)}})
</script>
