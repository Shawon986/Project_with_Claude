<template>
  <div class="landing">
    <!-- Animated Background Layers -->
    <div class="bg-layer">
      <canvas ref="bgCanvas" class="bg-canvas"></canvas>
      <div class="bg-orb bg-orb-1"></div>
      <div class="bg-orb bg-orb-2"></div>
      <div class="bg-orb bg-orb-3"></div>
      <div class="bg-grid"></div>
    </div>

    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-glow"></div>
      <div class="hero-content">
        <div class="hero-badge">
          <span class="badge-dot"></span> {{ t('liveData') }} · 3,455 {{ t('listings') }} · 12 {{ t('districts') }}
        </div>
        <h1 class="hero-title">
          <span class="title-line">Hangzhou</span>
          <span class="title-line accent">{{ t('hangzhouHousingIntelligence') }}</span>
        </h1>
        <p class="hero-subtitle">{{ t('overviewDesc') }}</p>
        <div class="hero-actions">
          <el-button type="primary" size="large" round class="cta-btn" @click="$router.push('/listings')">
            {{ t('exploreListingsBtn') }} <el-icon><ArrowRight /></el-icon>
          </el-button>
          <el-button size="large" round class="cta-secondary glass-btn" @click="$router.push('/gallery')">
            {{ t('viewCharts') }} <el-icon><TrendCharts /></el-icon>
          </el-button>
        </div>
      </div>

      <!-- Floating Stat Cards -->
      <div class="floating-stats">
        <div class="float-card fc-1">
          <div class="fc-value text-cyan">{{ overview.total_listings?.toLocaleString() }}</div>
          <div class="fc-label">{{ t('totalListings') }}</div>
        </div>
        <div class="float-card fc-2">
          <div class="fc-value text-green">{{ overview.avg_unit_price ? (overview.avg_unit_price/1000).toFixed(1)+'k' : '-' }}</div>
          <div class="fc-label">{{ t('avgUnitPrice') }}</div>
        </div>
        <div class="float-card fc-3">
          <div class="fc-value text-purple">{{ overview.total_districts }}</div>
          <div class="fc-label">{{ t('districts') }}</div>
        </div>
        <div class="float-card fc-4">
          <div class="fc-value text-orange">{{ overview.avg_total_price?.toLocaleString() }}</div>
          <div class="fc-label">{{ t('avgTotal') }}</div>
        </div>
      </div>
    </section>

    <!-- Stats Strip -->
    <section class="stats-strip">
      <div class="strip-card" v-for="s in stripStats" :key="s.label">
        <div class="strip-icon" :style="{background:s.gradient}">
          <el-icon :size="22"><component :is="s.icon" /></el-icon>
        </div>
        <div class="strip-info">
          <div class="strip-value">{{ s.value }}</div>
          <div class="strip-label">{{ s.label }}</div>
        </div>
      </div>
    </section>

    <!-- Feature Modules Grid -->
    <section class="modules-section">
      <h2 class="section-heading">
        <span class="heading-line"></span>
        {{ t('platformModules') }}
        <span class="heading-sub">{{ t('modulesSub') }}</span>
      </h2>
      <div class="modules-grid">
        <div class="module-card" v-for="m in modules" :key="m.route" @click="$router.push(m.route)">
          <div class="module-glow" :style="{background:m.gradient}"></div>
          <div class="module-icon-wrap" :style="{background:m.gradient}">
            <el-icon :size="28"><component :is="m.icon" /></el-icon>
          </div>
          <h3 class="module-title">{{ m.title }}</h3>
          <p class="module-desc">{{ m.desc }}</p>
          <div class="module-meta">
            <span v-for="tag in m.tags" :key="tag" class="module-tag">{{ tag }}</span>
          </div>
          <div class="module-arrow">Explore →</div>
        </div>
      </div>
    </section>

    <!-- Quick Insights Panel -->
    <section class="insights-section">
      <h2 class="section-heading">
        <span class="heading-line"></span>
        {{ t('marketAtAGlance') }}
        <span class="heading-sub">{{ t('marketGlanceSub') }}</span>
      </h2>
      <div class="insights-grid">
        <div class="insight-card">
          <div class="insight-header">
            <el-icon :size="20" color="#409EFF"><Coin /></el-icon>
            <span>{{ t('priceLandscape') }}</span>
          </div>
          <div class="insight-body">
            <div class="insight-row"><span>{{ t('totalPriceRangeLabel') }}</span><strong>{{ overview.min_total_price }} – {{ overview.max_total_price?.toLocaleString() }} (10k)</strong></div>
            <div class="insight-row"><span>{{ t('medianTotalPriceLabel') }}</span><strong>{{ overview.median_total_price?.toLocaleString() }} (10k)</strong></div>
            <div class="insight-row"><span>{{ t('unitPriceRangeLabel') }}</span><strong>{{ overview.min_unit_price?.toLocaleString() }} – {{ overview.max_unit_price?.toLocaleString() }} RMB/sqm</strong></div>
          </div>
        </div>
        <div class="insight-card">
          <div class="insight-header">
            <el-icon :size="20" color="#67C23A"><Histogram /></el-icon>
            <span>{{ t('marketComposition') }}</span>
          </div>
          <div class="insight-body">
            <div class="insight-row"><span>{{ t('avgFloorAreaLabel') }}</span><strong>{{ overview.avg_area }} sqm</strong></div>
            <div class="insight-row"><span>{{ t('avgBuildingAgeLabel') }}</span><strong>{{ overview.avg_building_age }} years</strong></div>
            <div class="insight-row"><span>{{ t('subwayCoverageLabel') }}</span><strong>{{ overview.subway_coverage_pct }}%</strong></div>
          </div>
        </div>
        <div class="insight-card">
          <div class="insight-header">
            <el-icon :size="20" color="#a855f7"><MapLocation /></el-icon>
            <span>{{ t('geographicExtremes') }}</span>
          </div>
          <div class="insight-body">
            <div class="insight-row"><span>{{ t('mostExpensiveLabel') }}</span><strong style="color:#F56C6C">{{ overview.highest_price_district?.name }} — {{ overview.highest_price_district?.avg_unit_price?.toLocaleString() }} RMB/sqm</strong></div>
            <div class="insight-row"><span>{{ t('mostAffordableLabel') }}</span><strong style="color:#67C23A">{{ overview.lowest_price_district?.name }} — {{ overview.lowest_price_district?.avg_unit_price?.toLocaleString() }} RMB/sqm</strong></div>
          </div>
        </div>
      </div>
    </section>

    <!-- Price Distribution Explorer -->
    <section class="dist-section">
      <h2 class="section-heading">
        <span class="heading-line"></span>
        {{ t('priceDistributionExplorer') }}
        <span class="heading-sub">{{ t('distSub') }}</span>
      </h2>
      <div class="dist-layout">
        <div class="section-card dist-chart-card">
          <h3>{{ t('totalPriceDist') }}</h3>
          <div ref="distChart" style="height:340px;"></div>
        </div>
        <div class="dist-insights">
          <div class="dist-stat-card" style="border-top:2px solid #22c55e;">
            <div class="dist-stat-icon">🏠</div>
            <div class="dist-stat-body">
              <div class="dist-stat-val">{{ overview.median_total_price?.toLocaleString() }}</div>
              <div class="dist-stat-lbl">{{ t('medianPrice') }}</div>
            </div>
          </div>
          <div class="dist-stat-card" style="border-top:2px solid #409EFF;">
            <div class="dist-stat-icon">📊</div>
            <div class="dist-stat-body">
              <div class="dist-stat-val">{{ overview.avg_total_price ? Math.round(overview.avg_total_price).toLocaleString() : '-' }}</div>
              <div class="dist-stat-lbl">{{ t('averagePrice') }}</div>
            </div>
          </div>
          <div class="dist-stat-card" style="border-top:2px solid #f59e0b;">
            <div class="dist-stat-icon">📐</div>
            <div class="dist-stat-body">
              <div class="dist-stat-val">{{ overview.avg_area ? Math.round(overview.avg_area).toLocaleString() : '-' }} sqm</div>
              <div class="dist-stat-lbl">{{ t('avgFloorAreaShort') }}</div>
            </div>
          </div>
          <div class="dist-stat-card" style="border-top:2px solid #a855f7;">
            <div class="dist-stat-icon">🏢</div>
            <div class="dist-stat-body">
              <div class="dist-stat-val">{{ overview.avg_unit_price ? (overview.avg_unit_price/1000).toFixed(1)+'k' : '-' }}</div>
              <div class="dist-stat-lbl">{{ t('avgUnitPriceShort') }}</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Quick Charts Preview -->
    <section class="charts-preview">
      <h2 class="section-heading">
        <span class="heading-line"></span>
        {{ t('visualizationPreview') }}
        <span class="heading-sub">{{ t('vizSub') }}</span>
      </h2>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
        <div class="section-card preview-chart-card" @click="$router.push('/district')">
          <h3>{{ t('districtPriceComparison') }}</h3>
          <div ref="previewChart1" style="height:320px;"></div>
        </div>
        <div class="section-card preview-chart-card" @click="$router.push('/factors')">
          <h3>{{ t('areaVsTotalPrice') }}</h3>
          <div ref="previewChart2" style="height:320px;"></div>
        </div>
      </div>
    </section>

    <!-- Footer CTA -->
    <section class="footer-cta">
      <div class="cta-glow"></div>
      <h2>{{ t('readyToExplore') }}</h2>
      <p>{{ t('footerTagline') }}</p>
      <div class="footer-links">
        <el-button type="primary" size="large" round @click="$router.push('/listings')">{{ t('browseAllListings') }}</el-button>
        <el-button size="large" round class="glass-btn" @click="$router.push('/map')">{{ t('openMapView') }}</el-button>
        <el-button size="large" round class="glass-btn" @click="$router.push('/gallery')">{{ t('chartGallery') }}</el-button>
      </div>
      <div class="footer-credit">{{ t('hangzhouFooter') }}</div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getOverview, getChartData } from '../api'
import { useI18n } from '../i18n'
const { t } = useI18n()

const overview = ref({})
const bgCanvas = ref(null)
const previewChart1 = ref(null)
const previewChart2 = ref(null)
const distChart = ref(null)
let animFrame = null

const stripStats = computed(() => [
  { icon:'OfficeBuilding', value:'3,455', label:t('stripActiveListings'), gradient:'linear-gradient(135deg,#409EFF,#00d4ff)' },
  { icon:'Grid', value:'12', label:t('stripDistricts'), gradient:'linear-gradient(135deg,#a855f7,#6366f1)' },
  { icon:'TrendCharts', value:'10', label:t('stripChartTypes'), gradient:'linear-gradient(135deg,#22c55e,#10b981)' },
  { icon:'DataAnalysis', value:'6', label:t('stripAnalysisMethods'), gradient:'linear-gradient(135deg,#f59e0b,#d97706)' },
  { icon:'Connection', value:'5', label:t('stripMarketClusters'), gradient:'linear-gradient(135deg,#ec4899,#f43f5e)' },
  { icon:'Star', value:'22', label:t('stripDataFeatures'), gradient:'linear-gradient(135deg,#6366f1,#8b5cf6)' },
])

const modules = computed(() => [
  { route:'/listings', icon:'Search', title:t('exploreListingsMod'), desc:t('exploreListingsModDesc'), tags:['Table','Filters','Pagination'], gradient:'linear-gradient(135deg,#409EFF,#2563eb)' },
  { route:'/district', icon:'MapLocation', title:t('districtAnalysisMod'), desc:t('districtAnalysisModDesc'), tags:['Charts','Rankings','Comparison'], gradient:'linear-gradient(135deg,#22c55e,#16a34a)' },
  { route:'/map', icon:'LocationFilled', title:t('geographicMapMod'), desc:t('geographicMapModDesc'), tags:['Canvas','Animation','Interactive'], gradient:'linear-gradient(135deg,#a855f7,#7c3aed)' },
  { route:'/factors', icon:'TrendCharts', title:t('priceFactorsMod'), desc:t('priceFactorsModDesc'), tags:['Regression','Correlation','ML'], gradient:'linear-gradient(135deg,#f59e0b,#d97706)' },
  { route:'/evaluation', icon:'Histogram', title:t('pcaEvaluationMod'), desc:t('pcaEvaluationModDesc'), tags:['PCA','Factor Analysis','Scoring'], gradient:'linear-gradient(135deg,#ec4899,#db2777)' },
  { route:'/classification', icon:'Connection', title:t('classificationMod'), desc:t('classificationModDesc'), tags:['Clustering','LDA','Segments'], gradient:'linear-gradient(135deg,#00d4ff,#0891b2)' },
  { route:'/gallery', icon:'PictureFilled', title:t('chartGalleryMod'), desc:t('chartGalleryModDesc'), tags:['Gallery','Fullscreen','10 Charts'], gradient:'linear-gradient(135deg,#6366f1,#4f46e5)' },
  { route:'/recommendations', icon:'MagicStick', title:t('buyingGuideMod'), desc:t('buyingGuideModDesc'), tags:['Guide','Insights','Advice'], gradient:'linear-gradient(135deg,#f43f5e,#e11d48)' },
])

// Animated network background — nodes + connection mesh + scan rings
function initBgParticles() {
  if (!bgCanvas.value) return
  const c = bgCanvas.value
  const ctx = c.getContext('2d')
  function resize() { c.width = window.innerWidth; c.height = window.innerHeight }
  resize(); window.addEventListener('resize', resize)

  // Fixed anchor nodes (like district centers)
  const anchors = []
  const anchorCount = 14
  for (let i=0;i<anchorCount;i++) {
    anchors.push({
      x:Math.random()*c.width, y:Math.random()*c.height,
      baseX:Math.random()*c.width, baseY:Math.random()*c.height,
      r:3+Math.random()*4,
      hue:Math.random()>0.5?210:260,
      pulseOffset:Math.random()*Math.PI*2,
    })
  }

  // Floating traveler particles
  const particles = []
  for (let i=0;i<100;i++) {
    particles.push({
      x:Math.random()*c.width, y:Math.random()*c.height,
      r:Math.random()*1.8+0.8,
      vx:(Math.random()-0.5)*0.4, vy:(Math.random()-0.5)*0.4,
      hue:200+Math.random()*60,
      alpha:Math.random()*0.4+0.2,
      pulse:Math.random()*Math.PI*2,
      speed:Math.random()*0.02+0.008,
    })
  }

  // Scanning rings
  const rings = []
  function spawnRing() {
    const a = anchors[Math.floor(Math.random()*anchors.length)]
    rings.push({ x:a.x, y:a.y, r:0, maxR:100+Math.random()*150, alpha:0.35, speed:0.8+Math.random()*1.2 })
  }

  let tick=0
  function animate() {
    tick++; ctx.clearRect(0,0,c.width,c.height)

    // Slow drift of anchor nodes
    anchors.forEach(a => {
      a.x = a.baseX + Math.sin(tick*0.003+a.pulseOffset)*30
      a.y = a.baseY + Math.cos(tick*0.004+a.pulseOffset)*25
    })

    // Connection mesh between anchors (if close enough)
    for (let i=0;i<anchors.length;i++) {
      for (let j=i+1;j<anchors.length;j++) {
        const dx=anchors[i].x-anchors[j].x, dy=anchors[i].y-anchors[j].y
        const dist=Math.sqrt(dx*dx+dy*dy)
        const maxDist=350
        if (dist<maxDist) {
          const alpha=0.07*(1-dist/maxDist)
          ctx.strokeStyle=`hsla(${anchors[i].hue},60%,55%,${alpha})`
          ctx.lineWidth=0.5; ctx.beginPath(); ctx.moveTo(anchors[i].x,anchors[i].y); ctx.lineTo(anchors[j].x,anchors[j].y); ctx.stroke()
        }
      }
    }

    // Anchor glow halos
    anchors.forEach(a => {
      const pulse=Math.sin(tick*0.03+a.pulseOffset)*0.3+0.7
      const grad=ctx.createRadialGradient(a.x,a.y,0,a.x,a.y,25)
      grad.addColorStop(0,`hsla(${a.hue},70%,60%,${0.1*pulse})`)
      grad.addColorStop(0.5,`hsla(${a.hue},70%,60%,${0.03*pulse})`)
      grad.addColorStop(1,'transparent')
      ctx.fillStyle=grad; ctx.beginPath(); ctx.arc(a.x,a.y,25,0,Math.PI*2); ctx.fill()

      // Anchor core dot
      ctx.fillStyle=`hsla(${a.hue},80%,70%,${0.5*pulse})`
      ctx.beginPath(); ctx.arc(a.x,a.y,a.r,0,Math.PI*2); ctx.fill()
    })

    // Traveling particles with connections
    particles.forEach(p => {
      p.pulse+=p.speed; p.x+=p.vx; p.y+=p.vy
      if(p.x<0)p.x=c.width; if(p.x>c.width)p.x=0
      if(p.y<0)p.y=c.height; if(p.y>c.height)p.y=0

      // Connect to nearest anchor
      let nearestDist=Infinity, nearestAnchor=null
      anchors.forEach(a=>{const dx=a.x-p.x,dy=a.y-p.y,d=Math.sqrt(dx*dx+dy*dy);if(d<nearestDist){nearestDist=d;nearestAnchor=a}})
      if(nearestAnchor&&nearestDist<200){
        ctx.strokeStyle=`hsla(${nearestAnchor.hue},60%,55%,${0.04*(1-nearestDist/200)})`
        ctx.lineWidth=0.3; ctx.beginPath(); ctx.moveTo(p.x,p.y); ctx.lineTo(nearestAnchor.x,nearestAnchor.y); ctx.stroke()
      }

      const a=Math.sin(p.pulse)*0.2+p.alpha
      ctx.fillStyle=`hsla(${p.hue},70%,65%,${a})`; ctx.beginPath(); ctx.arc(p.x,p.y,p.r,0,Math.PI*2); ctx.fill()
    })

    // Scanning rings
    if(tick%40===0&&rings.length<5)spawnRing()
    for(let i=rings.length-1;i>=0;i--){
      const r=rings[i]; r.r+=r.speed
      if(r.r>=r.maxR){rings.splice(i,1);continue}
      ctx.strokeStyle=`rgba(64,158,255,${r.alpha*(1-r.r/r.maxR)})`
      ctx.lineWidth=1; ctx.beginPath(); ctx.arc(r.x,r.y,r.r,0,Math.PI*2); ctx.stroke()
    }

    animFrame=requestAnimationFrame(animate)
  }
  animate()
}

async function loadPreviewCharts() {
  await nextTick()
  const da = { axisLabel:{color:'#9ca3af',fontSize:9}, nameTextStyle:{color:'#9ca3af',fontSize:9} }

  // Price distribution chart
  try {
    const rd = await getChartData('total_price_distribution')
    if (rd.data?.x && distChart.value) {
      const colors = ['#22c55e','#4ade80','#facc15','#f59e0b','#f97316','#ef4444','#dc2626']
      echarts.init(distChart.value).setOption({
        tooltip:{trigger:'axis',axisPointer:{type:'shadow'},formatter:p=>`${p[0].name}<br/><b>${p[0].value}</b> listings`},
        grid:{left:55,right:25,top:10,bottom:45},
        xAxis:{type:'category',data:rd.data.x,axisLabel:{rotate:35,color:'#9ca3af',fontSize:9}},
        yAxis:{type:'value',name:'Listings',...da},
        series:[{type:'bar',data:rd.data.y.map((v,i)=>({value:v,itemStyle:{color:colors[i%colors.length],borderRadius:[4,4,0,0]}})),barWidth:'70%',label:{show:false}}]
      })
    }
  } catch(e){}

  try {
    const r1 = await getChartData('district_avg_unit_price')
    if (r1.data?.x && previewChart1.value) {
      echarts.init(previewChart1.value).setOption({
        tooltip:{trigger:'axis'},grid:{left:110,right:50,top:5,bottom:15},
        xAxis:{type:'value',...da},yAxis:{type:'category',data:r1.data.x,...da},
        series:[{type:'bar',data:r1.data.y,itemStyle:{color:'#409EFF'},label:{show:false}}]
      })
    }
  } catch(e){}
  try {
    const r2 = await getChartData('area_vs_total_price')
    if (r2.data?.data && previewChart2.value) {
      echarts.init(previewChart2.value).setOption({
        tooltip:{trigger:'item'},grid:{left:55,right:25,top:5,bottom:35},
        xAxis:{type:'value',name:'Area (sqm)',...da},yAxis:{type:'value',name:'Price',...da},
        series:[{type:'scatter',data:r2.data.data.map(d=>[d.x,d.y]),symbolSize:4,itemStyle:{color:'#67C23A',opacity:0.5}}]
      })
    }
  } catch(e){}
}

onMounted(async()=>{
  try { const r = await getOverview(); overview.value = r.data } catch(e) { console.error(e) }
  initBgParticles()
  loadPreviewCharts()
})
onUnmounted(()=>{ if(animFrame) cancelAnimationFrame(animFrame) })
</script>

<style scoped>
/* ========== LANDING PAGE STYLES ========== */
.landing { position: relative; overflow: hidden; }

/* ---- Animated Background ---- */
.bg-layer { position: fixed; top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none; }
.bg-canvas { position:absolute;top:0;left:0;width:100%;height:100%; }
.bg-grid {
  position:absolute;top:0;left:0;width:100%;height:100%;
  background-image: linear-gradient(rgba(64,158,255,0.03) 1px,transparent 1px),
                    linear-gradient(90deg,rgba(64,158,255,0.03) 1px,transparent 1px);
  background-size: 80px 80px;
}
.bg-orb { position:absolute;border-radius:50%;filter:blur(100px);opacity:0.25; }
.bg-orb-1 { width:500px;height:500px;top:-150px;left:-100px;background:rgba(64,158,255,0.15);animation:orb-drift-1 12s ease-in-out infinite; }
.bg-orb-2 { width:400px;height:400px;top:40%;right:-120px;background:rgba(168,85,247,0.12);animation:orb-drift-2 15s ease-in-out infinite; }
.bg-orb-3 { width:350px;height:350px;bottom:-100px;left:30%;background:rgba(0,212,255,0.1);animation:orb-drift-3 18s ease-in-out infinite; }
@keyframes orb-drift-1 { 0%,100%{transform:translate(0,0)}33%{transform:translate(60px,40px)}66%{transform:translate(-30px,-20px)} }
@keyframes orb-drift-2 { 0%,100%{transform:translate(0,0)}50%{transform:translate(-50px,-30px)} }
@keyframes orb-drift-3 { 0%,100%{transform:translate(0,0)}33%{transform:translate(40px,-25px)}66%{transform:translate(-20px,35px)} }

/* ---- Hero ---- */
.hero { position:relative;z-index:1;text-align:center;padding:70px 20px 50px; }
.hero-glow { position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:600px;height:600px;border-radius:50%;background:radial-gradient(circle,rgba(64,158,255,0.08) 0%,transparent 70%);pointer-events:none; }
.hero-content { position:relative;z-index:2;max-width:800px;margin:0 auto; }
.hero-badge { display:inline-flex;align-items:center;gap:8px;padding:8px 20px;border-radius:50px;background:rgba(64,158,255,0.08);border:1px solid rgba(64,158,255,0.2);color:var(--accent-cyan);font-size:13px;margin-bottom:28px; }
.badge-dot { width:8px;height:8px;border-radius:50%;background:#22c55e;box-shadow:0 0 8px #22c55e;animation:pulse-dot 2s infinite; }
.hero-title { font-size:56px;font-weight:900;letter-spacing:-2px;margin-bottom:18px;line-height:1.1; }
.title-line { display:block;color:#fff; }
.title-line.accent { background:linear-gradient(135deg,#409EFF,#00d4ff,#a855f7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text; }
.hero-subtitle { font-size:17px;color:var(--text-secondary);line-height:1.7;max-width:650px;margin:0 auto 32px; }
.hero-actions { display:flex;gap:14px;justify-content:center;flex-wrap:wrap; }
.cta-btn { padding:14px 32px !important;font-weight:700 !important;font-size:15px !important;box-shadow:0 4px 20px rgba(64,158,255,0.4) !important; }
.cta-secondary { padding:14px 32px !important;font-weight:600 !important;font-size:15px !important; }

/* ---- Floating Cards ---- */
.floating-stats { position:relative;z-index:2;display:flex;justify-content:center;gap:20px;margin-top:50px;flex-wrap:wrap; }
.float-card { padding:20px 28px;border-radius:16px;background:rgba(26,31,46,0.8);border:1px solid rgba(255,255,255,0.06);backdrop-filter:blur(12px);text-align:center;transition:all 0.4s ease;animation:float-card-in 0.8s ease-out both; }
.fc-1 { animation-delay:0.1s; } .fc-2 { animation-delay:0.25s; } .fc-3 { animation-delay:0.4s; } .fc-4 { animation-delay:0.55s; }
@keyframes float-card-in { from { opacity:0;transform:translateY(30px); } to { opacity:1;transform:translateY(0); } }
.float-card:hover { transform:translateY(-8px);border-color:rgba(64,158,255,0.3);box-shadow:0 12px 40px rgba(0,0,0,0.4); }
.fc-value { font-size:28px;font-weight:800;letter-spacing:-1px; }
.fc-label { font-size:12px;color:var(--text-muted);margin-top:4px;text-transform:uppercase;letter-spacing:1px; }

/* ---- Stats Strip ---- */
.stats-strip { position:relative;z-index:2;display:flex;justify-content:center;gap:16px;margin:50px 0 60px;flex-wrap:wrap; }
.strip-card { display:flex;align-items:center;gap:14px;padding:16px 24px;border-radius:14px;background:rgba(26,31,46,0.7);border:1px solid rgba(255,255,255,0.05);backdrop-filter:blur(8px);transition:all 0.3s ease; }
.strip-card:hover { transform:translateY(-4px);border-color:rgba(255,255,255,0.12);box-shadow:0 8px 30px rgba(0,0,0,0.3); }
.strip-icon { width:44px;height:44px;border-radius:12px;display:flex;align-items:center;justify-content:center;color:#fff;flex-shrink:0; }
.strip-value { font-size:20px;font-weight:800;color:#fff; }
.strip-label { font-size:11px;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.5px;margin-top:1px; }

/* ---- Section Headings ---- */
.section-heading { text-align:center;margin-bottom:36px;position:relative;z-index:2; }
.heading-line { display:block;width:60px;height:3px;background:var(--gradient-blue);margin:0 auto 16px;border-radius:2px; }
.section-heading { font-size:30px;font-weight:800;color:#fff;letter-spacing:-1px; }
.heading-sub { display:block;font-size:15px;color:var(--text-muted);font-weight:400;margin-top:6px; }

/* ---- Modules Grid ---- */
.modules-section { position:relative;z-index:2;padding:0 20px 50px; }
.modules-grid { display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:18px;max-width:1300px;margin:0 auto; }
.module-card { position:relative;padding:28px 26px;border-radius:18px;background:rgba(26,31,46,0.7);border:1px solid rgba(255,255,255,0.05);backdrop-filter:blur(8px);cursor:pointer;transition:all 0.4s cubic-bezier(0.4,0,0.2,1);overflow:hidden; }
.module-card:hover { transform:translateY(-6px);border-color:rgba(64,158,255,0.25);box-shadow:0 16px 48px rgba(0,0,0,0.4); }
.module-card:hover .module-arrow { opacity:1;transform:translateX(0); }
.module-glow { position:absolute;top:-40px;right:-40px;width:120px;height:120px;border-radius:50%;opacity:0.06;filter:blur(30px);transition:opacity 0.4s; }
.module-card:hover .module-glow { opacity:0.12; }
.module-icon-wrap { width:52px;height:52px;border-radius:14px;display:flex;align-items:center;justify-content:center;color:#fff;margin-bottom:16px; }
.module-title { font-size:18px;font-weight:700;color:#fff;margin-bottom:8px; }
.module-desc { font-size:13px;color:var(--text-secondary);line-height:1.7;margin-bottom:14px; }
.module-meta { display:flex;gap:6px;flex-wrap:wrap; }
.module-tag { padding:3px 10px;border-radius:6px;background:rgba(255,255,255,0.04);font-size:11px;color:var(--text-muted); }
.module-arrow { color:var(--accent-cyan);font-size:13px;font-weight:600;margin-top:12px;opacity:0;transform:translateX(-10px);transition:all 0.4s; }

/* ---- Insights ---- */
.insights-section { position:relative;z-index:2;padding:0 20px 50px; }
.insights-grid { display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:18px;max-width:1100px;margin:0 auto; }
.insight-card { padding:22px 24px;border-radius:16px;background:rgba(26,31,46,0.6);border:1px solid rgba(255,255,255,0.05);backdrop-filter:blur(8px); }
.insight-header { display:flex;align-items:center;gap:10px;color:#fff;font-weight:700;font-size:15px;margin-bottom:16px;padding-bottom:12px;border-bottom:1px solid rgba(255,255,255,0.06); }
.insight-row { display:flex;justify-content:space-between;align-items:center;padding:7px 0;font-size:13px; }
.insight-row span { color:var(--text-muted); }
.insight-row strong { color:var(--text-primary);font-size:12.5px; }

/* ---- Chart Previews ---- */
.charts-preview { position:relative;z-index:2;padding:0 20px 50px;max-width:1300px;margin:0 auto; }
.preview-chart-card { cursor:pointer;transition:all 0.4s ease; }
.preview-chart-card:hover { border-color:rgba(64,158,255,0.3) !important;transform:translateY(-3px);box-shadow:0 12px 40px rgba(0,0,0,0.3); }

/* ---- Footer CTA ---- */
.footer-cta { position:relative;z-index:2;text-align:center;padding:60px 20px;margin-top:20px; }
.cta-glow { position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:500px;height:200px;border-radius:50%;background:radial-gradient(ellipse,rgba(64,158,255,0.06) 0%,transparent 70%);pointer-events:none; }
.footer-cta h2 { font-size:32px;font-weight:800;color:#fff;margin-bottom:8px;letter-spacing:-1px; }
.footer-cta p { color:var(--text-muted);font-size:15px;margin-bottom:28px; }
.footer-links { display:flex;gap:12px;justify-content:center;flex-wrap:wrap; }
.footer-credit { color:var(--text-muted);font-size:11px;margin-top:32px;opacity:0.6; }

/* ---- Price Distribution ---- */
.dist-section{position:relative;z-index:2;padding:0 20px 50px;max-width:1300px;margin:0 auto}
.dist-layout{display:grid;grid-template-columns:2fr 1fr;gap:20px;align-items:start}
.dist-chart-card{cursor:pointer;transition:all 0.4s ease}
.dist-chart-card:hover{border-color:rgba(64,158,255,0.3)!important;transform:translateY(-3px);box-shadow:0 12px 40px rgba(0,0,0,0.3)}
.dist-insights{display:flex;flex-direction:column;gap:12px}
.dist-stat-card{display:flex;align-items:center;gap:14px;padding:16px 18px;border-radius:14px;background:rgba(26,31,46,0.7);border:1px solid rgba(255,255,255,0.05);backdrop-filter:blur(8px);transition:all 0.3s ease}
.dist-stat-card:hover{transform:translateX(4px);border-color:rgba(255,255,255,0.1);box-shadow:0 8px 24px rgba(0,0,0,0.3)}
.dist-stat-icon{font-size:24px;flex-shrink:0}
.dist-stat-val{font-size:20px;font-weight:800;color:#fff;letter-spacing:-0.5px}
.dist-stat-lbl{font-size:11px;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.5px;margin-top:2px}

@media(max-width:768px){
  .dist-layout{grid-template-columns:1fr;gap:14px}
  .dist-insights{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
  .dist-stat-card{padding:12px 14px;gap:10px}
  .dist-stat-icon{font-size:20px}
  .dist-stat-val{font-size:16px}
}
@media(max-width:480px){
  .dist-insights{grid-template-columns:1fr}
}

@keyframes pulse-dot { 0%,100%{opacity:1}50%{opacity:0.4} }
</style>
