<template>
  <div>
    <div class="page-header"><h2>{{ t('districtPriceAnalysis') }}</h2><p>{{ t('districtDesc') }}</p></div>
    <div class="card-grid">
      <div class="stat-card"><div class="stat-label">{{ t('mostExpensive') }}</div><div class="stat-value text-red" style="font-size:22px">{{ topDistrict?.district || '-' }}</div><div class="stat-sub">{{ topDistrict?.avg_unit_price?.toLocaleString() || '-' }} RMB/sqm</div></div>
      <div class="stat-card"><div class="stat-label">{{ t('mostAffordable') }}</div><div class="stat-value text-green" style="font-size:22px">{{ bottomDistrict?.district || '-' }}</div><div class="stat-sub">{{ bottomDistrict?.avg_unit_price?.toLocaleString() || '-' }} RMB/sqm</div></div>
      <div class="stat-card"><div class="stat-label">{{ t('priceSpread') }}</div><div class="stat-value text-orange" style="font-size:22px">{{ priceSpread }}x</div><div class="stat-sub">Highest / Lowest ratio</div></div>
      <div class="stat-card"><div class="stat-label">{{ t('activeDistricts') }}</div><div class="stat-value text-purple" style="font-size:28px">{{ districtData.length }}</div><div class="stat-sub">{{ t('withListings') }}</div></div>
    </div>
    <div class="section-card"><h3>{{ t('avgUnitPriceByDistrict') }}</h3><div ref="barChart" style="height:480px"></div></div>
    <div class="section-card"><h3>{{ t('districtDetailTable') }}</h3>
      <el-table :data="districtData" stripe border v-loading="loading" max-height="500" size="small">
        <el-table-column prop="district" :label="t('districtCol')" width="120" fixed /><el-table-column prop="count" :label="t('listingsCol')" width="90" sortable />
        <el-table-column prop="pct_of_total" :label="t('shareCol')" width="70" sortable><template #default="{ row }">{{ row.pct_of_total }}%</template></el-table-column>
        <el-table-column prop="avg_unit_price" :label="t('avgUnitPriceCol')" width="180" sortable><template #default="{ row }">{{ row.avg_unit_price?.toLocaleString() }}</template></el-table-column>
        <el-table-column prop="median_unit_price" :label="t('medianUnitPriceCol')" width="170" sortable><template #default="{ row }">{{ row.median_unit_price?.toLocaleString() }}</template></el-table-column>
        <el-table-column prop="avg_total_price" :label="t('avgTotalPriceCol')" width="150" sortable><template #default="{ row }">{{ row.avg_total_price?.toLocaleString() }} (10k)</template></el-table-column>
        <el-table-column prop="avg_area" :label="t('avgAreaCol')" width="120" /><el-table-column prop="avg_building_age" :label="t('avgAgeCol')" width="120" />
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import * as echarts from 'echarts'
import { getDistrictAnalysis } from '../api'
import { useI18n } from '../i18n'
const { t } = useI18n()
const districtData=ref([]), loading=ref(false), barChart=ref(null)
const topDistrict=computed(()=>districtData.value[0])
const bottomDistrict=computed(()=>districtData.value[districtData.value.length-1])
const priceSpread=computed(()=>{if(!topDistrict.value||!bottomDistrict.value)return'-';return(topDistrict.value.avg_unit_price/bottomDistrict.value.avg_unit_price).toFixed(1)})
onMounted(async()=>{loading.value=true;try{const r=await getDistrictAnalysis();districtData.value=r.data;if(barChart.value&&r.data.length>0){const c=echarts.init(barChart.value);const d=[...r.data].reverse();c.setOption({tooltip:{trigger:'axis'},grid:{left:110,right:100,top:20,bottom:30},xAxis:{type:'value',name:'RMB/sqm',axisLabel:{color:'#9ca3af'},nameTextStyle:{color:'#9ca3af'}},yAxis:{type:'category',data:d.map(x=>x.district),axisLabel:{color:'#9ca3af'}},series:[{type:'bar',data:d.map(x=>x.avg_unit_price),itemStyle:{color:new echarts.graphic.LinearGradient(0,0,1,0,[{offset:0,color:'#83bff6'},{offset:1,color:'#188df0'}])},label:{show:true,position:'right',color:'#9ca3af'}}]})}}catch(e){console.error(e)}finally{loading.value=false}})
</script>
