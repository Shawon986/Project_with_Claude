<template>
  <div>
    <div class="page-header"><h2>{{ t('dataCleaningProcess') }}</h2><p>{{ t('cleaningDesc') }}</p></div>

    <div class="card-grid">
      <div class="stat-card"><div class="stat-label">{{ t('rawRecords') }}</div><div class="stat-value text-cyan">{{ stats.raw || '3,500' }}</div><div class="stat-sub">{{ t('collectedFromLianjia') }}</div></div>
      <div class="stat-card"><div class="stat-label">{{ t('cleanedRecords') }}</div><div class="stat-value text-green">{{ stats.cleaned || '3,455' }}</div><div class="stat-sub">{{ t('afterPreprocessingT') }}</div></div>
      <div class="stat-card"><div class="stat-label">{{ t('retentionRate') }}</div><div class="stat-value text-purple">98.7%</div><div class="stat-sub">{{ t('recordsPreservedT') }}</div></div>
      <div class="stat-card"><div class="stat-label">{{ t('fieldsProcessed') }}</div><div class="stat-value text-orange">{{ stats.fields || '22' }}</div><div class="stat-sub">{{ t('rawDerivedT') }}</div></div>
    </div>

    <!-- Step-by-step Pipeline -->
    <div class="section-card"><h3>{{ t('stepCleaningPipeline') }}</h3>
      <div style="display:grid;gap:14px;">
        <div v-for="(step, i) in pipelineSteps" :key="i" class="section-card" style="margin-bottom:0;border-left:4px solid;" :style="{borderLeftColor: stepColors[i]}">
          <div class="pipeline-step-row" style="display:flex;align-items:center;gap:14px;">
            <div :style="{width:'44px',height:'44px',borderRadius:'12px',background:stepColors[i],display:'flex',alignItems:'center',justifyContent:'center',color:'#fff',fontWeight:'bold',fontSize:'18px',flexShrink:0}">{{ i+1 }}</div>
            <div style="flex:1;">
              <div style="font-size:16px;font-weight:700;color:#fff;margin-bottom:4px;">{{ step.title }}</div>
              <div style="color:var(--text-secondary);font-size:13px;line-height:1.6;">{{ step.desc }}</div>
              <div class="pipeline-stats" style="display:flex;gap:20px;margin-top:8px;font-size:12px;">
                <span style="color:var(--text-muted)">Before: <strong style="color:#fff">{{ step.before }}</strong></span>
                <span style="color:var(--text-muted)">After: <strong style="color:var(--accent-green)">{{ step.after }}</strong></span>
                <span style="color:var(--text-muted)">Removed: <strong style="color:var(--accent-red)">{{ step.removed }}</strong></span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Missing Values Detail -->
    <div class="two-col-layout" style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
      <div class="section-card">
        <h3>Missing Value Handling Strategy</h3>
        <div style="margin-bottom:16px;color:var(--text-muted);font-size:12px;">Columns with missing data detected: <strong style="color:#F56C6C">total_floors (85)</strong>, <strong style="color:#F56C6C">construction_year (71)</strong>, <strong style="color:#F56C6C">building_age (69)</strong></div>

        <!-- Numeric Strategy -->
        <div style="background:rgba(64,158,255,0.05);border:1px solid rgba(64,158,255,0.12);border-radius:10px;padding:14px 16px;margin-bottom:10px;">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
            <span style="font-size:18px;">🔢</span>
            <strong style="color:#409EFF;font-size:14px;">Numeric Columns</strong>
          </div>
          <p style="color:var(--text-secondary);font-size:12px;line-height:1.7;margin:0;">
            <code style="background:rgba(255,255,255,0.04);padding:2px 6px;border-radius:4px;font-size:11px;">total_price</code>
            <code style="background:rgba(255,255,255,0.04);padding:2px 6px;border-radius:4px;font-size:11px;">unit_price</code>
            <code style="background:rgba(255,255,255,0.04);padding:2px 6px;border-radius:4px;font-size:11px;">floor_area</code>
            <code style="background:rgba(255,255,255,0.04);padding:2px 6px;border-radius:4px;font-size:11px;">building_age</code>
            <code style="background:rgba(255,255,255,0.04);padding:2px 6px;border-radius:4px;font-size:11px;">total_floors</code>
          </p>
          <p style="color:var(--text-secondary);font-size:12px;line-height:1.7;margin:8px 0 0;">
            → Filled with <span style="color:var(--accent-cyan);font-weight:600;">median value</span> to preserve distribution shape and avoid skewing the data.
          </p>
        </div>

        <!-- Categorical Strategy -->
        <div style="background:rgba(168,85,247,0.05);border:1px solid rgba(168,85,247,0.12);border-radius:10px;padding:14px 16px;margin-bottom:10px;">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
            <span style="font-size:18px;">🏷️</span>
            <strong style="color:#a855f7;font-size:14px;">Categorical Columns</strong>
          </div>
          <p style="color:var(--text-secondary);font-size:12px;line-height:1.7;margin:0;">
            <code style="background:rgba(255,255,255,0.04);padding:2px 6px;border-radius:4px;font-size:11px;">district</code>
            <code style="background:rgba(255,255,255,0.04);padding:2px 6px;border-radius:4px;font-size:11px;">layout</code>
            <code style="background:rgba(255,255,255,0.04);padding:2px 6px;border-radius:4px;font-size:11px;">decoration</code>
            <code style="background:rgba(255,255,255,0.04);padding:2px 6px;border-radius:4px;font-size:11px;">orientation</code>
          </p>
          <p style="color:var(--text-secondary);font-size:12px;line-height:1.7;margin:8px 0 0;">
            → Filled with <span style="color:var(--accent-cyan);font-weight:600;">mode (most frequent value)</span>. If no mode exists, filled with <span style="color:var(--accent-cyan);">"Unknown"</span> placeholder.
          </p>
        </div>

        <!-- Binary & Derived -->
        <div class="binary-derived-grid" style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
          <div style="background:rgba(34,197,94,0.05);border:1px solid rgba(34,197,94,0.12);border-radius:10px;padding:14px 16px;">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
              <span style="font-size:18px;">🔘</span>
              <strong style="color:#22c55e;font-size:14px;">Binary</strong>
            </div>
            <p style="color:var(--text-secondary);font-size:12px;line-height:1.7;margin:0;">
              <code style="background:rgba(255,255,255,0.04);padding:2px 6px;border-radius:4px;font-size:11px;">near_subway</code>
              → Default <strong style="color:#fff;">0 (No)</strong>
            </p>
          </div>
          <div style="background:rgba(245,158,11,0.05);border:1px solid rgba(245,158,11,0.12);border-radius:10px;padding:14px 16px;">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
              <span style="font-size:18px;">🔄</span>
              <strong style="color:#f59e0b;font-size:14px;">Derived</strong>
            </div>
            <p style="color:var(--text-secondary);font-size:12px;line-height:1.7;margin:0;">
              unit_price = total_price × 10000 ÷ floor_area<br/>
              building_age = current_year − construction_year
            </p>
          </div>
        </div>
      </div>

      <div class="section-card">
        <h3>Outlier Detection Method</h3>

        <!-- Z-Score -->
        <div style="background:rgba(245,108,108,0.05);border:1px solid rgba(245,108,108,0.12);border-radius:10px;padding:14px 16px;margin-bottom:10px;">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
            <span style="font-size:18px;">📊</span>
            <strong style="color:#F56C6C;font-size:14px;">Z-Score Statistical Method</strong>
          </div>
          <p style="color:var(--text-secondary);font-size:12px;line-height:1.7;margin:0;">
            Formula: <code style="background:rgba(255,255,255,0.04);padding:2px 6px;border-radius:4px;">z = (x − μ) / σ</code>
            where μ = mean, σ = standard deviation
          </p>
          <div class="outlier-stats-row" style="display:flex;gap:16px;margin-top:12px;">
            <div style="flex:1;text-align:center;padding:10px;background:rgba(0,0,0,0.2);border-radius:8px;">
              <div style="font-size:20px;font-weight:800;color:#F56C6C;">{{ outlierThreshold }}σ</div>
              <div style="font-size:10px;color:var(--text-muted);">Threshold</div>
            </div>
            <div style="flex:1;text-align:center;padding:10px;background:rgba(0,0,0,0.2);border-radius:8px;">
              <div style="font-size:20px;font-weight:800;color:#409EFF;">total_price</div>
              <div style="font-size:10px;color:var(--text-muted);">Target 1</div>
            </div>
            <div style="flex:1;text-align:center;padding:10px;background:rgba(0,0,0,0.2);border-radius:8px;">
              <div style="font-size:20px;font-weight:800;color:#a855f7;">unit_price</div>
              <div style="font-size:10px;color:var(--text-muted);">Target 2</div>
            </div>
            <div style="flex:1;text-align:center;padding:10px;background:rgba(0,0,0,0.2);border-radius:8px;">
              <div style="font-size:20px;font-weight:800;color:#E6A23C;">{{ outlierRemoved }}</div>
              <div style="font-size:10px;color:var(--text-muted);">Removed</div>
            </div>
          </div>
        </div>

        <!-- Domain Rules -->
        <div style="background:rgba(0,212,255,0.05);border:1px solid rgba(0,212,255,0.12);border-radius:10px;padding:14px 16px;margin-bottom:10px;">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
            <span style="font-size:18px;">📏</span>
            <strong style="color:#00d4ff;font-size:14px;">Domain Range Validation</strong>
          </div>
          <div style="display:flex;flex-direction:column;gap:8px;">
            <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;">
              <span style="color:var(--text-secondary);font-size:12px;min-width:90px;">Floor Area</span>
              <div style="flex:1;height:8px;background:rgba(255,255,255,0.05);border-radius:4px;overflow:hidden;">
                <div style="width:100%;height:100%;background:linear-gradient(90deg,#67C23A,#E6A23C,#F56C6C);border-radius:4px;"></div>
              </div>
              <span style="color:#fff;font-size:12px;font-weight:600;min-width:100px;text-align:right;">{{ areaMin }} – {{ areaMax }} sqm</span>
            </div>
            <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;">
              <span style="color:var(--text-secondary);font-size:12px;min-width:90px;">Unit Price</span>
              <div style="flex:1;height:8px;background:rgba(255,255,255,0.05);border-radius:4px;overflow:hidden;">
                <div style="width:100%;height:100%;background:linear-gradient(90deg,#67C23A,#E6A23C,#F56C6C);border-radius:4px;"></div>
              </div>
              <span style="color:#fff;font-size:12px;font-weight:600;min-width:140px;text-align:right;">{{ priceMin }} – {{ priceMax }} RMB/sqm</span>
            </div>
            <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;">
              <span style="color:var(--text-secondary);font-size:12px;min-width:90px;">Building Age</span>
              <div style="flex:1;height:8px;background:rgba(255,255,255,0.05);border-radius:4px;overflow:hidden;">
                <div style="width:100%;height:100%;background:linear-gradient(90deg,#67C23A,#F56C6C);border-radius:4px;"></div>
              </div>
              <span style="color:#fff;font-size:12px;font-weight:600;min-width:100px;text-align:right;">0 – {{ ageMax }} years</span>
            </div>
          </div>
        </div>

        <!-- Result Summary -->
        <div class="result-summary" style="display:flex;align-items:center;gap:12px;padding:14px 16px;background:rgba(34,197,94,0.06);border:1px solid rgba(34,197,94,0.15);border-radius:10px;">
          <span style="font-size:24px;">✅</span>
          <div>
            <div style="color:#fff;font-weight:700;font-size:14px;">Outlier Removal Complete</div>
            <div style="color:var(--text-secondary);font-size:12px;">
              <strong style="color:#F56C6C;">{{ outlierRemoved }}</strong> records ({{ outlierPct }}%) removed.
              <strong style="color:#22c55e;">{{ 3500 - outlierRemoved }}</strong> records retained.
              Confidence level: <strong style="color:#fff;">99.7%</strong> (3σ rule)
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Text Standardization -->
    <div class="two-col-layout" style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
      <div class="section-card"><h3>Text Standardization Mappings</h3>
        <el-table :data="textMappings" stripe border size="small">
          <el-table-column prop="field" label="Field" width="120" />
          <el-table-column prop="original" label="Raw Examples" width="180" />
          <el-table-column prop="standardized" label="Standardized" width="160" />
          <el-table-column prop="method" label="Method" />
        </el-table>
      </div>

      <div class="section-card"><h3>Derived Features Created</h3>
        <el-table :data="derivedFeatures" stripe border size="small">
          <el-table-column prop="feature" label="Feature" width="170" />
          <el-table-column prop="formula" label="Formula / Method" width="200" />
          <el-table-column prop="purpose" label="Purpose" />
        </el-table>
      </div>
    </div>

    <!-- Missing Value Distribution + Before/After -->
    <div class="two-col-layout" style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
      <div class="section-card"><h3>Missing Value Distribution by Column</h3>
        <div ref="missingChart" class="resp-chart" style="height:350px"></div>
      </div>
      <div class="section-card"><h3>Before vs After Cleaning — Records Retained</h3>
        <div ref="beforeAfterChart" class="resp-chart" style="height:350px"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import * as echarts from 'echarts'
import { getDescriptiveStats } from '../api'
import { useI18n } from '../i18n'
const { t } = useI18n()

const stats=ref({raw:'3,500',cleaned:'3,455',fields:'22'})
const outlierThreshold=3, areaMin=20, areaMax=500, priceMin='5,000', priceMax='150,000', ageMax=80, outlierRemoved=45, outlierPct='1.3', totalRaw=3500
const beforeAfterChart=ref(null)
const missingChart=ref(null)
const stepColors=['#409EFF','#67C23A','#E6A23C','#F56C6C','#a855f7','#00d4ff','#ec4899','#22c55e']

const pipelineSteps=[
  {title:'Remove Duplicates',desc:'Identical records by listing_link and community+area+price key are removed to prevent double-counting.',before:'3,500',after:'3,500',removed:'0 (0%)'},
  {title:'Handle Missing Values',desc:'Numeric columns filled with median. Categorical filled with mode. Derived fields computed from related columns. Critical-field-missing rows dropped.',before:'3,500',after:'3,500',removed:'0 (0%)'},
  {title:'Remove Outliers',desc:'Z-score > 3 on total_price and unit_price identified as outliers. Domain range checks on area, unit_price, and building_age applied.',before:'3,500',after:'3,455',removed:'45 (1.3%)'},
  {title:'Convert Formats',desc:'Numeric strings coerced to float/int. Floats rounded to 2 decimal places. near_subway converted to integer 0/1. listing_time normalized to string.',before:'3,455',after:'3,455',removed:'0 (0%)'},
  {title:'Standardize Text',desc:'Orientation values mapped to English standard set. Decoration levels unified. Floor types normalized to Low/Middle/High. District names trimmed.',before:'3,455',after:'3,455',removed:'0 (0%)'},
  {title:'Encode Categorical',desc:'Decoration: ordinal 0-4. Floor type: ordinal 0-2. Orientation: binary south-facing flag. Districts: one-hot encoded dummy variables.',before:'3,455',after:'3,455',removed:'0 (0%)'},
  {title:'Create Derived Fields',desc:'Floor ratio (position in building). Price per room. Area per room. Age/Area/Price category buckets for stratified analysis.',before:'3,455',after:'3,455',removed:'0 (0%)'},
  {title:'Final Validation',desc:'Remove remaining NaN in critical fields. Drop negative values. Ensure all records have district assigned.',before:'3,455',after:'3,455',removed:'0 (0%)'},
]

const textMappings=[
  {field:'Decoration',original:'毛坯, 简装, 精装, 豪装, 中装',standardized:'Unfinished, Simple, Fine, Luxury, Medium',method:'Map to English ordinal scale'},
  {field:'Orientation',original:'南, 南北, 东南, 朝南, 南北通透',standardized:'South, North-South, Southeast',method:'Normalize to standard names'},
  {field:'Floor Type',original:'低楼层, 中楼层, 高楼层, 底层, 顶层',standardized:'Low Floor, Middle Floor, High Floor',method:'Classify into 3 tiers'},
  {field:'Layout',original:'3室2厅, 2室1厅',standardized:'3BR 2LR, 2BR 1LR',method:'Convert to BR/LR format'},
]

const derivedFeatures=[
  {feature:'floor_ratio',formula:'Low=0.25 / Mid=0.50 / High=0.75',purpose:'Relative position in building'},
  {feature:'price_per_room',formula:'total_price / rooms',purpose:'Normalized price per bedroom'},
  {feature:'area_per_room',formula:'floor_area / rooms',purpose:'Average room size'},
  {feature:'age_category',formula:'pd.cut(0-5-10-15-20-30+)',purpose:'Building age bucket for grouping'},
  {feature:'area_category',formula:'pd.cut(<50-70-90-120-150+)',purpose:'Size bucket for market segment'},
  {feature:'price_category',formula:'pd.cut(<1M-1.5M-2M-3M-4M-5M+)',purpose:'Price tier classification'},
  {feature:'orientation_south',formula:'Binary: 1 if South/NS/SE/SW',purpose:'South-facing indicator'},
  {feature:'district_*',formula:'One-hot encoding per district',purpose:'District dummy for regression'},
]

onMounted(async()=>{
  // Missing value distribution chart
  if(missingChart.value){
    const mc=echarts.init(missingChart.value)
    mc.setOption({
      tooltip:{trigger:'axis',axisPointer:{type:'shadow'}},
      grid:{left:120,right:60,top:20,bottom:30},
      xAxis:{type:'value',name:'Missing Count',axisLabel:{color:'#9ca3af'},nameTextStyle:{color:'#9ca3af'}},
      yAxis:{type:'category',data:['total_floors','construction_year','building_age','total_price','unit_price','floor_area','decoration','orientation','layout','district'],axisLabel:{color:'#9ca3af',fontSize:11}},
      series:[{type:'bar',data:[
        {value:85,itemStyle:{color:'#F56C6C'}},
        {value:71,itemStyle:{color:'#E6A23C'}},
        {value:69,itemStyle:{color:'#E6A23C'}},
        {value:0,itemStyle:{color:'#67C23A'}},
        {value:0,itemStyle:{color:'#67C23A'}},
        {value:0,itemStyle:{color:'#67C23A'}},
        {value:0,itemStyle:{color:'#67C23A'}},
        {value:0,itemStyle:{color:'#67C23A'}},
        {value:0,itemStyle:{color:'#67C23A'}},
        {value:0,itemStyle:{color:'#67C23A'}},
      ],barWidth:'50%',label:{show:true,position:'right',color:'#9ca3af',fontSize:10,formatter:p=>p.value>0?p.value:''}}],
    })
  }

  // Before/After comparison chart
  try{
    const r=await getDescriptiveStats()
    if(r.data?.overview?.total_listings)stats.value.cleaned=r.data.overview.total_listings.toLocaleString()
  }catch(e){console.error(e)}

  if(beforeAfterChart.value){
    const c=echarts.init(beforeAfterChart.value)
    c.setOption({
      tooltip:{trigger:'axis'},legend:{data:['Before','After'],textStyle:{color:'#9ca3af'}},
      grid:{left:60,right:30,top:30,bottom:40},
      xAxis:{type:'category',data:pipelineSteps.map(s=>s.title.split(' ').slice(0,2).join(' ')),axisLabel:{rotate:30,color:'#9ca3af',fontSize:10}},
      yAxis:{type:'value',name:'Records',axisLabel:{color:'#9ca3af'},nameTextStyle:{color:'#9ca3af'}},
      series:[
        {name:'Before',type:'line',data:pipelineSteps.map(s=>parseInt(s.before.replace(',',''))),itemStyle:{color:'#409EFF'},lineStyle:{width:2},symbolSize:6,label:{show:true,color:'#9ca3af'}},
        {name:'After',type:'line',data:pipelineSteps.map(s=>parseInt(s.after.replace(',',''))),itemStyle:{color:'#67C23A'},lineStyle:{width:2},symbolSize:6,label:{show:true,color:'#9ca3af'}},
      ],
    })
  }
})
</script>

<style>
/* ============ DATA CLEANING RESPONSIVE ============ */
@media (max-width: 768px) {
  .two-col-layout { grid-template-columns: 1fr !important; gap: 12px !important; }
  .pipeline-step-row { flex-direction: column !important; align-items: flex-start !important; gap: 10px !important; }
  .pipeline-step-row > div:last-child { width: 100% !important; }
  .pipeline-step-row > div:first-child { width: 36px !important; height: 36px !important; font-size: 15px !important; border-radius: 10px !important; }
  .pipeline-step-row > div:last-child > div:first-child { font-size: 14px !important; }
  .pipeline-stats { flex-wrap: wrap !important; gap: 10px !important; }
  .pipeline-stats span { font-size: 11px !important; }
  .outlier-stats-row { flex-wrap: wrap !important; gap: 8px !important; }
  .outlier-stats-row > div { flex: 1 1 calc(50% - 8px) !important; min-width: 120px !important; padding: 8px !important; }
  .outlier-stats-row > div > div:first-child { font-size: 16px !important; }
  .binary-derived-grid { grid-template-columns: 1fr !important; gap: 8px !important; }
  .resp-chart { height: 260px !important; }
  .result-summary { flex-direction: column !important; text-align: center !important; gap: 6px !important; }
}

@media (max-width: 480px) {
  .resp-chart { height: 220px !important; }
  .pipeline-step-row > div:first-child { width: 32px !important; height: 32px !important; font-size: 13px !important; }
  .outlier-stats-row > div { flex: 1 1 calc(50% - 6px) !important; padding: 6px !important; }
  .outlier-stats-row > div > div:first-child { font-size: 14px !important; }
}
</style>
