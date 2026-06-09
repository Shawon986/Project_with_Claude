<template>
  <div>
    <div class="page-header"><h2>Advanced Charts</h2><p>Interactive chart explorer with all 10 visualizations</p></div>

    <div class="section-card" style="overflow-x:auto;">
      <div style="display:flex;gap:8px;flex-wrap:wrap;">
        <el-button v-for="c in charts" :key="c.id" :type="activeChart===c.id?'primary':'default'"
          :class="activeChart===c.id?'':'glass-btn'" size="small" round @click="activeChart=c.id">
          {{ c.shortName }}
        </el-button>
      </div>
    </div>

    <div class="section-card">
      <div ref="chartContainer" style="width:100%;min-height:520px;"></div>
      <div v-if="chartError" style="text-align:center;padding:40px;color:var(--text-muted);">{{ chartError }}</div>
    </div>

    <div class="card-grid">
      <div class="stat-card" v-for="(desc, id) in chartDescriptions" :key="id" v-show="activeChart===id">
        <div class="stat-label">Chart Description</div>
        <div class="stat-sub" style="font-size:13px;line-height:1.8;" v-html="desc"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getChartData } from '../api'
import { useI18n } from '../i18n'
const { t } = useI18n()

const activeChart=ref('district_avg_unit_price'), chartContainer=ref(null), chartError=ref('')
let chartInstance=null
const da={axisLabel:{color:'#9ca3af',fontSize:10},nameTextStyle:{color:'#9ca3af',fontSize:10}}

const charts=[
  {id:'district_avg_unit_price',shortName:'District Prices'},
  {id:'total_price_distribution',shortName:'Price Distribution'},
  {id:'area_vs_total_price',shortName:'Area vs Price'},
  {id:'building_age_vs_unit_price',shortName:'Age vs Price'},
  {id:'avg_price_by_layout',shortName:'Layout Prices'},
  {id:'avg_price_by_decoration',shortName:'Decoration Prices'},
  {id:'correlation_heatmap',shortName:'Correlation Heatmap'},
  {id:'regression_results',shortName:'Regression Coefs'},
  {id:'pca_factor_scores',shortName:'PCA Variance'},
  {id:'cluster_results',shortName:'Cluster Results'},
]

const chartDescriptions={
  district_avg_unit_price: '<strong style="color:var(--accent-cyan)">Avg Unit Price by District:</strong> Horizontal bar chart comparing average unit prices across all 12 Hangzhou districts. Reveals the spatial price hierarchy from premium urban cores to affordable suburban areas.',
  total_price_distribution: '<strong style="color:var(--accent-cyan)">Total Price Distribution:</strong> Histogram showing the frequency distribution of total listing prices. The peak represents the market\'s most active price band. Skewness indicates the proportion of luxury vs budget listings.',
  area_vs_total_price: '<strong style="color:var(--accent-cyan)">Floor Area vs Total Price:</strong> Scatter plot revealing the strong positive correlation between unit size and price. Each point represents one listing. The slope reflects the implicit price per additional square meter.',
  building_age_vs_unit_price: '<strong style="color:var(--accent-cyan)">Building Age vs Unit Price:</strong> Scatter plot showing how depreciation affects unit price. Generally negative correlation, but prime-location older properties may buck this trend.',
  avg_price_by_layout: '<strong style="color:var(--accent-cyan)">Avg Total Price by Layout:</strong> Comparison of average prices across layout types. Larger layouts (more BR+LR) command proportionally higher total prices.',
  avg_price_by_decoration: '<strong style="color:var(--accent-cyan)">Avg Unit Price by Decoration:</strong> Shows the price premium associated with different decoration levels. Fine and Luxury finishes command significant premiums over unfinished units.',
  correlation_heatmap: '<strong style="color:var(--accent-cyan)">Correlation Heatmap:</strong> Full correlation matrix of all numeric features. Deep red = strong positive correlation, deep blue = strong negative. Essential for identifying multicollinearity and key relationships.',
  regression_results: '<strong style="color:var(--accent-cyan)">Regression Coefficients:</strong> Linear regression feature coefficients sorted by magnitude. Red bars push prices higher (positive coefficients), blue bars push prices lower (negative coefficients).',
  pca_factor_scores: '<strong style="color:var(--accent-cyan)">PCA Explained Variance:</strong> Bar chart showing variance explained by each principal component, with a cumulative line overlay. Helps determine how many components capture meaningful information.',
  cluster_results: '<strong style="color:var(--accent-cyan)">Clustering Results:</strong> Multi-color scatter plot showing K-Means cluster assignments on Area vs Price axes. Each color represents a distinct market segment identified by the algorithm.',
}

async function renderChart(){
  if(!chartContainer.value)return;chartError.value=''
  try{
    const res=await getChartData(activeChart.value);const data=res.data
    if(chartInstance)chartInstance.dispose();chartInstance=echarts.init(chartContainer.value)

    if(data.type==='bar'){
      const isH=data.horizontal;const colors=(data.y||[]).map(v=>v>=0?'#c23531':'#2f4554')
      const opt={tooltip:{trigger:'axis',axisPointer:{type:'shadow'}},grid:isH?{left:150,right:100,top:30,bottom:20}:{left:70,right:30,top:30,bottom:70},xAxis:isH?{type:'value',...da}:{type:'category',data:data.x,axisLabel:{rotate:45,color:'#9ca3af',fontSize:10}},yAxis:isH?{type:'category',data:data.x,...da}:{type:'value',...da},series:[{type:'bar',data:(data.y||[]).map((v,i)=>({value:v,itemStyle:{color:colors[i]}})),label:{show:true,position:isH?'right':'top',color:'#9ca3af',fontSize:10}}],...(data.title?{title:{text:data.title,left:'center',textStyle:{color:'#fff',fontSize:16}}}:{})}
      if(data.extraLine){opt.yAxis=[opt.yAxis,{type:'value',name:'Cumulative',min:0,max:1,...da}];opt.series.push({type:'line',data:data.extraLine,yAxisIndex:1,itemStyle:{color:'#F56C6C'},lineStyle:{type:'dashed'},symbol:'none',label:{show:true,formatter:p=>(p.value*100).toFixed(0)+'%',color:'#9ca3af'}})}
      chartInstance.setOption(opt)
    }else if(data.type==='scatter'){
      chartInstance.setOption({...(data.title?{title:{text:data.title,left:'center',textStyle:{color:'#fff'}}}:{}),tooltip:{trigger:'item'},grid:{left:70,right:30,top:30,bottom:50},xAxis:{type:'value',name:data.xLabel,...da},yAxis:{type:'value',name:data.yLabel,...da},series:[{type:'scatter',data:(data.data||[]).map(d=>[d.x,d.y]),symbolSize:5,itemStyle:{color:'#409EFF',opacity:0.5}}]})
    }else if(data.type==='multi-scatter'){
      chartInstance.setOption({...(data.title?{title:{text:data.title,left:'center',textStyle:{color:'#fff'}}}:{}),tooltip:{trigger:'item'},legend:{data:data.series.map(s=>s.name),textStyle:{color:'#9ca3af'},top:5},grid:{left:70,right:30,top:40,bottom:50},xAxis:{type:'value',name:data.xLabel,...da},yAxis:{type:'value',name:data.yLabel,...da},series:data.series.map(s=>({type:'scatter',name:s.name,data:s.data.map(d=>[d.x,d.y]),symbolSize:6,itemStyle:{color:s.color,opacity:0.6}}))})
    }else if(data.type==='heatmap'){
      chartInstance.setOption({...(data.title?{title:{text:data.title,left:'center',textStyle:{color:'#fff'}}}:{}),tooltip:{position:'top'},grid:{left:130,right:50,top:20,bottom:80},xAxis:{type:'category',data:data.xLabels,axisLabel:{rotate:45,color:'#9ca3af',fontSize:9}},yAxis:{type:'category',data:data.yLabels,axisLabel:{color:'#9ca3af',fontSize:9}},visualMap:{min:data.min,max:data.max,calculable:true,orient:'horizontal',left:'center',bottom:0,textStyle:{color:'#9ca3af'},inRange:{color:['#313695','#4575b4','#74add1','#e0f3f8','#ffffbf','#fee090','#f46d43','#d73027','#a50026']}},series:[{type:'heatmap',data:data.data,label:{show:true,fontSize:8},emphasis:{itemStyle:{shadowBlur:10,shadowColor:'rgba(0,0,0,0.5)'}}}]})
    }else{chartError.value='Chart type not recognized: '+(data.type||'unknown')}
  }catch(e){chartError.value='Failed to load chart: '+e.message;console.error(e)}
}

watch(activeChart,()=>nextTick(renderChart))
onMounted(()=>nextTick(renderChart))
</script>
