<template>
  <div>
    <div class="page-header">
      <h2>{{ t('geographicIntelligence') }}</h2>
      <p>{{ t('mapDesc') }}</p>
    </div>

    <!-- Animated Pulse Stats -->
    <div class="card-grid">
      <div class="stat-card" style="border-top:2px solid #F56C6C;">
        <div class="stat-label">{{ t('priceEpicenter') }}</div>
        <div class="stat-value text-red" style="font-size:22px;">{{ hottestDistrict }}</div>
        <div class="stat-sub">{{ hottestPrice?.toLocaleString() }} RMB/sqm</div>
        <div class="pulse-ring red"></div>
      </div>
      <div class="stat-card" style="border-top:2px solid #00d4ff;">
        <div class="stat-label">{{ t('volumeHub') }}</div>
        <div class="stat-value text-cyan" style="font-size:22px;">{{ densestDistrict }}</div>
        <div class="stat-sub">{{ densestCount }} active listings</div>
        <div class="pulse-ring cyan"></div>
      </div>
      <div class="stat-card" style="border-top:2px solid #a855f7;">
        <div class="stat-label">{{ t('spatialGradient') }}</div>
        <div class="stat-value text-purple" style="font-size:22px;">{{ priceGradient }}x</div>
        <div class="stat-sub">Core-to-suburb price ratio</div>
      </div>
      <div class="stat-card" style="border-top:2px solid #22c55e;">
        <div class="stat-label">{{ t('metroPenetration') }}</div>
        <div class="stat-value text-green" style="font-size:22px;">{{ subwayCoverage }}%</div>
        <div class="stat-sub">Transit-adjacent properties</div>
      </div>
    </div>

    <!-- Legend Bar -->
    <div class="section-card" style="padding:14px 20px;">
      <div style="display:flex;align-items:center;gap:20px;flex-wrap:wrap;">
        <span style="color:var(--text-muted);font-size:12px;font-weight:600;letter-spacing:1px;">{{ t('mapLegend') }}</span>
        <div style="display:flex;align-items:center;gap:6px;"><span style="width:14px;height:14px;border-radius:50%;background:#F56C6C;box-shadow:0 0 8px #F56C6C;"></span><span style="color:var(--text-secondary);font-size:11px;">{{ t('premium') }}</span></div>
        <div style="display:flex;align-items:center;gap:6px;"><span style="width:14px;height:14px;border-radius:50%;background:#E6A23C;box-shadow:0 0 8px #E6A23C;"></span><span style="color:var(--text-secondary);font-size:11px;">{{ t('upper') }}</span></div>
        <div style="display:flex;align-items:center;gap:6px;"><span style="width:14px;height:14px;border-radius:50%;background:#F7BA2A;box-shadow:0 0 8px #F7BA2A;"></span><span style="color:var(--text-secondary);font-size:11px;">{{ t('mid') }}</span></div>
        <div style="display:flex;align-items:center;gap:6px;"><span style="width:14px;height:14px;border-radius:50%;background:#409EFF;box-shadow:0 0 8px #409EFF;"></span><span style="color:var(--text-secondary);font-size:11px;">{{ t('value') }}</span></div>
        <div style="display:flex;align-items:center;gap:6px;"><span style="width:14px;height:14px;border-radius:50%;background:#67C23A;box-shadow:0 0 8px #67C23A;"></span><span style="color:var(--text-secondary);font-size:11px;">Affordable &lt;22k</span></div>
        <el-divider direction="vertical" />
        <span style="color:var(--text-muted);font-size:11px;">{{ t('sizeVol') }}</span>
        <span style="color:var(--text-muted);font-size:11px;">{{ t('rippleMetro') }}</span>
        <span style="color:var(--text-muted);font-size:11px;">{{ t('clickDistrict') }}</span>
      </div>
    </div>

    <!-- Main Map Canvas with Animated Background -->
    <div class="section-card map-card">
      <canvas ref="bgCanvas" class="map-bg-canvas"></canvas>
      <div class="map-glow map-glow-tl"></div>
      <div class="map-glow map-glow-br"></div>
      <div ref="mainMap" class="map-canvas"></div>
    </div>

    <!-- Bottom Panel Grid -->
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:20px;">
      <!-- Rankings -->
      <div class="section-card">
        <h3>{{ t('priceRankingsTitle') }}</h3>
        <div ref="rankChart" style="height:380px;"></div>
      </div>

      <!-- Mini District Grid -->
      <div class="section-card">
        <h3>{{ t('districtExplorerTitle') }}</h3>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;max-height:380px;overflow-y:auto;padding-right:4px;">
          <div v-for="d in districtMapData" :key="d.district"
            class="mini-dist-card"
            :class="{ active: selectedDistrict?.district === d.district }"
            @click="selectedDistrict = d">
            <div class="mini-dist-header">
              <span class="mini-dist-name">{{ d.district }}</span>
              <span class="mini-dist-count">{{ d.count }}</span>
            </div>
            <div class="mini-dist-bar-wrap">
              <div class="mini-dist-bar" :style="{width:priceBarPct(d.avg_unit_price)+'%',background:priceColor(d.avg_unit_price)}"></div>
            </div>
            <div class="mini-dist-price">{{ d.avg_unit_price?.toLocaleString() }}</div>
          </div>
        </div>
      </div>

      <!-- Selected Detail -->
      <div class="section-card" v-if="selectedDistrict">
        <h3>{{ selectedDistrict.district }} · {{ t('deepDiveTitle') }}</h3>
        <div style="display:grid;gap:10px;">
          <div class="detail-row"><span>Unit Price</span><strong style="color:var(--accent-cyan);">{{ selectedDistrict.avg_unit_price?.toLocaleString() }}</strong><span style="color:var(--text-muted);font-size:11px;">RMB/sqm</span></div>
          <div class="detail-row"><span>Total Price</span><strong style="color:var(--accent-green);">{{ selectedDistrict.avg_total_price?.toLocaleString() }}</strong><span style="color:var(--text-muted);font-size:11px;">(10k RMB)</span></div>
          <div class="detail-row"><span>Median Price</span><strong style="color:#fff;">{{ selectedDistrict.median_total_price?.toLocaleString() }}</strong><span style="color:var(--text-muted);font-size:11px;">(10k RMB)</span></div>
          <div class="detail-row"><span>Listings</span><strong style="color:var(--accent-purple);">{{ selectedDistrict.count }}</strong><span style="color:var(--text-muted);font-size:11px;">{{ t('active') }}</span></div>
          <div class="detail-row"><span>{{ t('marketShare') }}</span><strong style="color:#fff;">{{ selectedDistrict.pct_of_total }}%</strong></div>
          <div class="detail-row"><span>Avg Area</span><strong style="color:#fff;">{{ selectedDistrict.avg_area?.toFixed(0) }}</strong><span style="color:var(--text-muted);font-size:11px;">sqm</span></div>
          <div class="detail-row"><span>Avg Age</span><strong style="color:var(--accent-orange);">{{ selectedDistrict.avg_building_age?.toFixed(0) }}</strong><span style="color:var(--text-muted);font-size:11px;">years</span></div>
          <div class="detail-row"><span>{{ t('priceRange') }}</span><strong style="color:#fff;font-size:12px;">{{ selectedDistrict.min_total_price?.toLocaleString() }} – {{ selectedDistrict.max_total_price?.toLocaleString() }}</strong></div>
        </div>
      </div>
      <div class="section-card" v-else style="display:flex;align-items:center;justify-content:center;">
        <div style="text-align:center;color:var(--text-muted);">
          <el-icon :size="48" style="opacity:0.3;"><MapLocation /></el-icon>
          <p style="margin-top:12px;">Click a district on the map<br/>or from the explorer panel</p>
        </div>
      </div>
    </div>

    <!-- ============================================ -->
    <!-- SATELLITE MAP WITH LISTING MARKERS -->
    <!-- ============================================ -->
    <div class="section-card" style="padding:0;overflow:hidden;border:1px solid rgba(0,212,255,0.2);">
      <div style="padding:16px 20px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid rgba(255,255,255,0.05);">
        <div>
          <h3 style="border:none;margin:0;padding:0;">{{ t('satelliteView') }}</h3>
          <p style="color:var(--text-muted);font-size:12px;margin:4px 0 0;">{{ t('satelliteDesc') }}</p>
        </div>
        <div style="display:flex;gap:8px;">
          <el-tag size="small" effect="dark" type="success">{{ sampleMarkers.length }} Sample Listings</el-tag>
          <el-tag size="small" effect="dark" type="primary">12 District Centers</el-tag>
          <el-tag size="small" effect="dark" type="warning">{{ t('predictionModel') }}</el-tag>
        </div>
      </div>
      <div ref="satelliteMap" style="width:100%;height:600px;position:relative;z-index:1;"></div>
      <canvas ref="satBgCanvas" class="sat-bg-canvas"></canvas>
      <div class="sat-scan-lines"></div>
      <div class="sat-radar"></div>
    </div>

    <!-- Housing Listing Detail Cards Grid Below Map -->
    <div class="section-card">
      <h3>{{ t('featuredListings') }}</h3>
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(310px,1fr));gap:16px;">
        <div v-for="(listing, i) in sampleMarkers" :key="i"
          class="listing-preview-card"
          @mouseenter="highlightMarker(i)" @mouseleave="unhighlightMarker()">
          <div class="lpc-image">
            <img :src="listingPhotos[i % 20]" :alt="listing.district + ' housing'" class="lpc-real-img" loading="lazy" />
            <div class="lpc-img-overlay"></div>
            <div class="lpc-district-badge">{{ listing.district }}</div>
            <div class="lpc-price-badge">{{ listing.total_price?.toLocaleString() }} (10k RMB)</div>
            <div class="lpc-hover-glow"></div>
          </div>
          <div class="lpc-body">
            <div class="lpc-row"><span>Area</span><strong>{{ listing.floor_area }} sqm</strong></div>
            <div class="lpc-row"><span>Unit Price</span><strong style="color:var(--accent-cyan);">{{ listing.unit_price?.toLocaleString() }} RMB/sqm</strong></div>
            <div class="lpc-row"><span>{{ t('estMonthlyRent') }}</span><strong style="color:#22c55e;">{{ listing.est_rent?.toLocaleString() }} RMB</strong></div>
            <div class="lpc-row"><span>{{ t('predictedPrice') }}</span><strong style="color:#a855f7;">{{ listing.predicted_price?.toLocaleString() }} (10k RMB)</strong></div>
            <div class="lpc-row"><span>{{ t('predictionDelta') }}</span>
              <strong :style="{color:listing.price_delta>0?'#F56C6C':'#67C23A'}">
                {{ listing.price_delta > 0 ? '+' : '' }}{{ listing.price_delta?.toLocaleString() }} (10k RMB)
              </strong>
            </div>
            <div class="lpc-row"><span>Layout</span><strong>{{ listing.layout }}</strong></div>
            <div class="lpc-row"><span>Building Age</span><strong>{{ listing.building_age }} years</strong></div>
            <div style="display:flex;gap:6px;margin-top:10px;flex-wrap:wrap;">
              <el-tag size="small" effect="dark" :type="listing.near_subway?'success':'info'">{{ listing.near_subway ? 'Metro ✓' : 'No Metro' }}</el-tag>
              <el-tag size="small" effect="dark" type="warning">{{ listing.decoration }}</el-tag>
              <el-tag size="small" effect="dark">{{ listing.orientation }}</el-tag>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { getDistrictAnalysis, getOverview } from '../api'
import { useI18n } from '../i18n'
const { t } = useI18n()

const districtMapData = ref([])
const selectedDistrict = ref(null)
const mainMap = ref(null)
const rankChart = ref(null)
const bgCanvas = ref(null)
const satelliteMap = ref(null)
const satBgCanvas = ref(null)
const subwayCoverage = ref('45.7')
let animFrame = null
let satAnimFrame = null
let leafletMap = null
let leafletMarkers = []
let satMouseX = 0, satMouseY = 0

// Sample listings with rent estimates and price predictions
// Real housing photos from Lorem Picsum (curated seeds for building/city photos)
const listingPhotos = [
  'https://picsum.photos/seed/house1/400/300',
  'https://picsum.photos/seed/building2/400/300',
  'https://picsum.photos/seed/apartment3/400/300',
  'https://picsum.photos/seed/modern4/400/300',
  'https://picsum.photos/seed/urban5/400/300',
  'https://picsum.photos/seed/city6/400/300',
  'https://picsum.photos/seed/condo7/400/300',
  'https://picsum.photos/seed/residence8/400/300',
  'https://picsum.photos/seed/villa9/400/300',
  'https://picsum.photos/seed/tower10/400/300',
  'https://picsum.photos/seed/home11/400/300',
  'https://picsum.photos/seed/estate12/400/300',
  'https://picsum.photos/seed/property13/400/300',
  'https://picsum.photos/seed/luxury14/400/300',
  'https://picsum.photos/seed/metro15/400/300',
  'https://picsum.photos/seed/garden16/400/300',
  'https://picsum.photos/seed/highrise17/400/300',
  'https://picsum.photos/seed/complex18/400/300',
  'https://picsum.photos/seed/block19/400/300',
  'https://picsum.photos/seed/view20/400/300',
]

// Generate sample markers with predictions
function generateSampleMarkers() {
  const markers = []
  const districts = ['Shangcheng','Xihu','Gongshu','Binjiang','Xiaoshan','Yuhang','Jianggan','Qiantang','Linping','Fuyang','Linan','Xiacheng']
  const baseCoords = {
    'Shangcheng':[30.242,120.169],'Xihu':[30.260,120.130],'Gongshu':[30.320,120.150],
    'Binjiang':[30.210,120.200],'Xiaoshan':[30.170,120.270],'Yuhang':[30.380,120.050],
    'Jianggan':[30.260,120.220],'Qiantang':[30.280,120.350],'Linping':[30.420,120.300],
    'Fuyang':[30.050,119.950],'Linan':[30.230,119.720],'Xiacheng':[30.280,120.170],
  }
  const decors = ['Fine','Medium','Simple','Luxury','Unfinished']
  const layouts = ['2BR 1LR','3BR 2LR','4BR 2LR','3BR 1LR','2BR 2LR','5BR 2LR']

  for (let i=0;i<20;i++) {
    const district = districts[i % districts.length]
    const [baseLat, baseLng] = baseCoords[district] || [30.25,120.15]
    const lat = baseLat + (Math.random()-0.5)*0.05
    const lng = baseLng + (Math.random()-0.5)*0.05
    const area = Math.round(50 + Math.random()*130)
    const unitPrice = Math.round(18000 + Math.random()*35000)
    const totalPrice = Math.round(unitPrice * area / 10000)
    // Rent estimate: ~0.15%-0.25% of property value per month
    const rentYield = 0.0015 + Math.random()*0.001
    const estRent = Math.round(unitPrice * area * rentYield)
    // Price prediction based on area (simple linear model approximation)
    const basePrice = 80 + area * 2.8 + (Math.random()-0.5)*50
    const predictedPrice = Math.round(Math.max(50, basePrice))
    const priceDelta = Math.round(totalPrice - predictedPrice)

    markers.push({
      district, lat, lng, floor_area:area, unit_price:unitPrice, total_price:totalPrice,
      est_rent:estRent, predicted_price:predictedPrice, price_delta:priceDelta,
      layout:layouts[i%layouts.length], decoration:decors[i%decors.length],
      building_age:Math.round(2+Math.random()*28), near_subway:Math.random()>0.5?1:0,
      orientation:['South','North-South','Southeast','East','West'][Math.floor(Math.random()*5)],
    })
  }
  return markers
}
const sampleMarkers = ref(generateSampleMarkers())

function highlightMarker(i) {
  if (leafletMarkers[i]) {
    leafletMarkers[i].setIcon(L.divIcon({
      className:'custom-marker-highlighted',
      html:`<div style="width:36px;height:36px;background:#fff;border-radius:50%;border:3px solid #409EFF;box-shadow:0 0 20px rgba(64,158,255,0.8);display:flex;align-items:center;justify-content:center;font-size:16px;transform:scale(1.3);">🏠</div>`,
      iconSize:[36,36],iconAnchor:[18,18],
    }))
  }
}
function unhighlightMarker() {
  leafletMarkers.forEach((m,i) => {
    const d = sampleMarkers.value[i]
    if (d) {
      const colors = {45000:'#F56C6C',35000:'#E6A23C',28000:'#409EFF',0:'#67C23A'}
      let color='#67C23A'
      for (const [k,v] of Object.entries(colors)) { if (d.unit_price > parseInt(k)) { color=v; break } }
      m.setIcon(L.divIcon({
        className:'custom-marker',
        html:`<div style="width:22px;height:22px;background:${color};border-radius:50%;border:2px solid rgba(255,255,255,0.4);box-shadow:0 0 10px ${color};transition:all 0.3s;">`,
        iconSize:[22,22],iconAnchor:[11,11],
      }))
    }
  })
}
const da = { axisLabel: { color: '#9ca3af' }, nameTextStyle: { color: '#9ca3af' } }

// Geographic coords
const coords = {
  'Shangcheng': [120.17, 30.24], 'Xiacheng': [120.17, 30.28], 'Xihu': [120.12, 30.26],
  'Gongshu': [120.15, 30.32], 'Jianggan': [120.22, 30.26], 'Binjiang': [120.20, 30.21],
  'Xiaoshan': [120.27, 30.17], 'Yuhang': [120.05, 30.38], 'Fuyang': [119.95, 30.05],
  'Linan': [119.72, 30.23], 'Qiantang': [120.35, 30.28], 'Linping': [120.30, 30.42],
}

// Connection lines between major districts (price flow visualization)
const connections = [
  ['Shangcheng','Xihu'],['Shangcheng','Gongshu'],['Shangcheng','Binjiang'],
  ['Xihu','Yuhang'],['Gongshu','Yuhang'],['Binjiang','Xiaoshan'],
  ['Jianggan','Qiantang'],['Shangcheng','Xiacheng'],['Yuhang','Linping'],
]

const hottestDistrict = computed(() => { const s=[...districtMapData.value].sort((a,b)=>b.avg_unit_price-a.avg_unit_price);return s[0]?.district||'-' })
const hottestPrice = computed(() => { const s=[...districtMapData.value].sort((a,b)=>b.avg_unit_price-a.avg_unit_price);return s[0]?.avg_unit_price||0 })
const densestDistrict = computed(() => { const s=[...districtMapData.value].sort((a,b)=>b.count-a.count);return s[0]?.district||'-' })
const densestCount = computed(() => { const s=[...districtMapData.value].sort((a,b)=>b.count-a.count);return s[0]?.count||0 })
const priceGradient = computed(() => { if(!districtMapData.value.length)return'-';const s=[...districtMapData.value].sort((a,b)=>b.avg_unit_price-a.avg_unit_price);return (s[0].avg_unit_price/s[s.length-1].avg_unit_price).toFixed(1) })

function priceColor(p){if(p>45000)return'#F56C6C';if(p>35000)return'#E6A23C';if(p>28000)return'#F7BA2A';if(p>22000)return'#409EFF';return'#67C23A'}
function priceBarPct(p){return Math.min(100,(p/50000)*100)}

let echartsInstances = []

function safeInitChart(domRef) {
  if (!domRef) return null
  // Dispose existing instance to prevent duplicate init
  const existing = echarts.getInstanceByDom(domRef)
  if (existing) existing.dispose()
  const instance = echarts.init(domRef)
  echartsInstances.push(instance)
  return instance
}

onMounted(async()=>{
  try{
    const[dr,ov]=await Promise.all([getDistrictAnalysis(),getOverview().catch(()=>({data:{}}))])
    districtMapData.value=dr.data||[]
    if(ov.data?.subway_coverage_pct)subwayCoverage.value=ov.data.subway_coverage_pct
    // Double nextTick to ensure full DOM readiness after async data
    await nextTick()
    await nextTick()
    if (mainMap.value) renderMap()
    if (rankChart.value) renderRankings()
    if (bgCanvas.value) initBgAnimation()
    // Delay Leaflet init slightly for container sizing
    setTimeout(() => {
      if (satelliteMap.value) initSatelliteMap()
      if (satBgCanvas.value) initSatBgAnimation()
    }, 300)
  }catch(e){console.error(e)}
})

onUnmounted(() => {
  if (animFrame) cancelAnimationFrame(animFrame)
  if (satAnimFrame) cancelAnimationFrame(satAnimFrame)
  echartsInstances.forEach(inst => { try { inst.dispose() } catch(e) {} })
  echartsInstances = []
  if (leafletMap) { try { leafletMap.remove() } catch(e) {}; leafletMap = null }
  leafletMarkers = []
})

// ============ SATELLITE BACKGROUND ANIMATION ============
function initSatBgAnimation() {
  if (!satBgCanvas.value) return
  // Cancel any existing animation
  if (satAnimFrame) { cancelAnimationFrame(satAnimFrame); satAnimFrame = null }
  const canvas = satBgCanvas.value
  const ctx = canvas.getContext('2d')
  const container = canvas.parentElement
  if (!container) return

  function resize() {
    const w = container.clientWidth
    const h = container.clientHeight
    if (w > 0 && h > 0) {
      canvas.width = w
      canvas.height = h
    }
  }
  resize()
  if (canvas.width === 0 || canvas.height === 0) {
    canvas.width = container.offsetWidth || 800
    canvas.height = container.offsetHeight || 600
  }
  window.addEventListener('resize', resize)

  container.addEventListener('mousemove', e => {
    const rect = container.getBoundingClientRect()
    satMouseX = ((e.clientX - rect.left) / rect.width - 0.5) * 2
    satMouseY = ((e.clientY - rect.top) / rect.height - 0.5) * 2
  })
  container.addEventListener('mouseleave', () => { satMouseX = 0; satMouseY = 0 })

  // Hex grid nodes
  const nodes = []
  const hexW = 90, hexH = 78
  for (let x = hexW; x < canvas.width + hexW; x += hexW) {
    for (let y = hexH; y < canvas.height + hexH; y += hexH * 2) {
      nodes.push({ x, y: y + (Math.floor(x / hexW) % 2) * hexH, baseX: x, baseY: y + (Math.floor(x / hexW) % 2) * hexH })
    }
  }

  // Price heat pulse waves
  const waves = []
  for (let i = 0; i < 5; i++) {
    waves.push({ x: canvas.width * (0.2 + Math.random() * 0.6), y: canvas.height * (0.2 + Math.random() * 0.6), radius: 0, maxR: 150 + Math.random() * 200, speed: 0.5 + Math.random(), alpha: 0.25 + Math.random() * 0.2, hue: [200, 320, 170, 45, 280][i] })
  }

  // Data stream particles
  const streams = []
  for (let i = 0; i < 30; i++) {
    streams.push({ x: Math.random() * canvas.width, y: Math.random() * canvas.height, r: Math.random() * 1.8 + 0.6, vx: (Math.random() - 0.5) * 0.35, vy: (Math.random() - 0.5) * 0.35, hue: 190 + Math.random() * 80, alpha: Math.random() * 0.35 + 0.08, pulse: Math.random() * Math.PI * 2 })
  }

  let tick = 0
  function animate() {
    tick++
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    const mx = canvas.width / 2 + satMouseX * canvas.width * 0.3
    const my = canvas.height / 2 + satMouseY * canvas.height * 0.3

    // ---- Hex grid network ----
    nodes.forEach(n => {
      n.x = n.baseX + Math.sin(tick * 0.008 + n.baseY * 0.005) * 6
      n.y = n.baseY + Math.cos(tick * 0.007 + n.baseX * 0.005) * 5
      const dist = Math.sqrt((n.x - mx) ** 2 + (n.y - my) ** 2)
      const glowAlpha = Math.max(0, (1 - dist / 250)) * 0.25
      ctx.fillStyle = `rgba(0,212,255,${0.08 + glowAlpha})`
      ctx.beginPath(); ctx.arc(n.x, n.y, 2.5, 0, Math.PI * 2); ctx.fill()
    })

    // Connect nearby hex nodes
    ctx.strokeStyle = 'rgba(0,212,255,0.04)'
    ctx.lineWidth = 0.5
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const dx = nodes[i].x - nodes[j].x, dy = nodes[i].y - nodes[j].y
        const dist = Math.sqrt(dx * dx + dy * dy)
        if (dist < 110) {
          ctx.beginPath(); ctx.moveTo(nodes[i].x, nodes[i].y); ctx.lineTo(nodes[j].x, nodes[j].y); ctx.stroke()
        }
      }
    }

    // ---- Pulse waves from price hotspots ----
    waves.forEach(w => {
      w.radius += w.speed
      if (w.radius > w.maxR) { w.radius = 0; w.x = canvas.width * (0.2 + Math.random() * 0.6); w.y = canvas.height * (0.2 + Math.random() * 0.6) }
      const progress = w.radius / w.maxR
      const alpha = w.alpha * (1 - progress)
      ctx.strokeStyle = `hsla(${w.hue},70%,60%,${alpha})`
      ctx.lineWidth = 1.5
      ctx.beginPath(); ctx.arc(w.x, w.y, w.radius, 0, Math.PI * 2); ctx.stroke()
    })

    // ---- Data stream particles ----
    streams.forEach((p, i) => {
      const dx = mx - p.x, dy = my - p.y, dist = Math.sqrt(dx * dx + dy * dy)
      if (dist < 180) { const f = (1 - dist / 180) * 0.025; p.vx += dx / dist * f; p.vy += dy / dist * f }
      p.vx *= 0.99; p.vy *= 0.99; p.x += p.vx; p.y += p.vy
      if (p.x < 0) p.x = canvas.width; if (p.x > canvas.width) p.x = 0
      if (p.y < 0) p.y = canvas.height; if (p.y > canvas.height) p.y = 0
      p.pulse += 0.02
      const alpha = Math.sin(p.pulse) * 0.15 + p.alpha
      ctx.fillStyle = `hsla(${p.hue},70%,65%,${alpha})`; ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2); ctx.fill()
      for (let j = i + 1; j < streams.length; j++) {
        const ddx = p.x - streams[j].x, ddy = p.y - streams[j].y, dd = Math.sqrt(ddx * ddx + ddy * ddy)
        if (dd < 100) { ctx.strokeStyle = `hsla(${p.hue},60%,55%,${0.035 * (1 - dd / 100)})`; ctx.lineWidth = 0.3; ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineTo(streams[j].x, streams[j].y); ctx.stroke() }
      }
    })

    // ---- Mouse ripple ----
    const mRipple = ctx.createRadialGradient(mx, my, 0, mx, my, 60)
    mRipple.addColorStop(0, 'rgba(0,212,255,0.1)'); mRipple.addColorStop(1, 'transparent')
    ctx.fillStyle = mRipple; ctx.beginPath(); ctx.arc(mx, my, 60, 0, Math.PI * 2); ctx.fill()

    // ---- HUD corners ----
    const ha = 0.12
    ctx.strokeStyle = `rgba(0,212,255,${ha})`; ctx.lineWidth = 1
    const corners = [[20,15,35,15,20,40],[canvas.width-20,15,canvas.width-35,15,canvas.width-20,40],[20,canvas.height-40,20,canvas.height-15,35,canvas.height-15],[canvas.width-20,canvas.height-40,canvas.width-20,canvas.height-15,canvas.width-35,canvas.height-15]]
    corners.forEach(([x1,y1,x2,y2,x3,y3]) => { ctx.beginPath(); ctx.moveTo(x1,y1); ctx.lineTo(x2,y2); ctx.lineTo(x3,y3); ctx.stroke() })
    ctx.fillStyle = `rgba(0,212,255,${ha * 0.7})`; ctx.font = '10px monospace'
    ctx.fillText(`GRID ${nodes.length} NODES`, 15, 30)
    ctx.fillText(`${streams.length} STREAMS`, canvas.width - 110, 30)
    ctx.fillText('HANGZHOU · 30.25°N 120.16°E', 15, canvas.height - 18)
    ctx.fillText(`${leafletMarkers.length + 12} MARKERS ACTIVE`, canvas.width - 175, canvas.height - 18)

    satAnimFrame = requestAnimationFrame(animate)
  }
  animate()
}

// ============ SATELLITE MAP ============
function initSatelliteMap() {
  if (!satelliteMap.value) return
  // Clean up any existing map instance
  if (leafletMap) { try { leafletMap.remove() } catch(e) {}; leafletMap = null }
  leafletMarkers = []
  // Ensure container has dimensions
  if (satelliteMap.value.clientHeight === 0) {
    satelliteMap.value.style.height = '600px'
  }

  leafletMap = L.map(satelliteMap.value, {
    center: [30.25, 120.16],
    zoom: 12,
    zoomControl: true,
    attributionControl: true,
  })

  // Satellite tile layer (ESRI World Imagery — free, no key needed)
  L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    attribution: '&copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
    maxZoom: 19,
  }).addTo(leafletMap)

  // Labels overlay
  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_only_labels/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://carto.com/">CARTO</a>',
    subdomains: 'abcd',
    maxZoom: 19,
  }).addTo(leafletMap)

  // Add district center markers with popups
  const districtCenters = {
    'Shangcheng':[30.242,120.169],'Xihu':[30.260,120.130],'Gongshu':[30.320,120.150],
    'Binjiang':[30.210,120.200],'Xiaoshan':[30.170,120.270],'Yuhang':[30.380,120.050],
    'Jianggan':[30.260,120.220],'Qiantang':[30.280,120.350],'Linping':[30.420,120.300],
    'Fuyang':[30.050,119.950],'Linan':[30.230,119.720],'Xiacheng':[30.280,120.170],
  }

  // District polygons (approximate circles)
  districtMapData.value.forEach(d => {
    const center = districtCenters[d.district]
    if (!center) return
    const color = d.avg_unit_price > 45000 ? '#F56C6C' : d.avg_unit_price > 35000 ? '#E6A23C' : d.avg_unit_price > 28000 ? '#409EFF' : '#67C23A'

    // Semi-transparent circle for district zone
    L.circle(center, {
      radius: 2500 + d.count * 5,
      color: color,
      fillColor: color,
      fillOpacity: 0.08,
      weight: 1,
      opacity: 0.3,
      dashArray: '8 4',
    }).addTo(leafletMap)

    // District label with photo popup
    const distPhotoIdx = districtMapData.value.indexOf(d) % listingPhotos.length
    const marker = L.marker(center, {
      icon: L.divIcon({
        className: 'district-label-marker',
        html: '<div style="background:rgba(10,14,23,0.85);border:1px solid '+color+';border-radius:20px;padding:6px 14px;color:#fff;font-size:12px;font-weight:700;white-space:nowrap;backdrop-filter:blur(8px);">'+d.district+' <span style="color:'+color+';">'+(d.avg_unit_price/1000).toFixed(1)+'k</span></div>',
        iconSize: [0,0],
      }),
    })
    marker.addTo(leafletMap)
    marker.bindPopup(
      '<div style="font-family:sans-serif;min-width:260px;">'+
        '<div style="margin:-14px -14px 0 -14px;border-radius:10px 10px 0 0;overflow:hidden;height:120px;position:relative;">'+
          '<img src="'+listingPhotos[distPhotoIdx]+'" style="width:100%;height:100%;object-fit:cover;" loading="lazy" />'+
          '<div style="position:absolute;inset:0;background:linear-gradient(180deg,transparent 20%,rgba(0,0,0,0.8) 100%);"></div>'+
          '<div style="position:absolute;bottom:8px;left:10px;color:#fff;font-size:16px;font-weight:800;text-shadow:0 2px 6px rgba(0,0,0,0.6);">'+d.district+' &middot; '+(d.avg_unit_price/1000).toFixed(1)+'k RMB/sqm</div>'+
        '</div>'+
        '<div style="line-height:1.8;font-size:13px;margin-top:8px;">'+
          '<div>Avg Unit Price: <b>'+(d.avg_unit_price||0).toLocaleString()+'</b> RMB/sqm</div>'+
          '<div>Avg Total Price: <b>'+(d.avg_total_price||0).toLocaleString()+'</b> (10k RMB)</div>'+
          '<div>Active Listings: <b>'+d.count+'</b> &middot; Market Share: <b>'+d.pct_of_total+'%</b></div>'+
          '<div>Avg Area: <b>'+(d.avg_area||0).toFixed(0)+'</b> sqm &middot; Avg Age: <b>'+(d.avg_building_age||0).toFixed(0)+'</b> years</div>'+
          '<div>Price Range: <b>'+(d.min_total_price||0).toLocaleString()+' &ndash; '+(d.max_total_price||0).toLocaleString()+'</b> (10k)</div>'+
        '</div>'+
        '<div style="margin-top:8px;padding-top:8px;border-top:1px solid rgba(255,255,255,0.1);font-size:11px;color:#9ca3af;">'+
          'Est. Monthly Rent: <b style="color:#22c55e;">~'+Math.round(d.avg_unit_price*d.avg_area*0.0018).toLocaleString()+'</b> RMB<br/>'+
          'Pred. Price (80sqm): <b style="color:#a855f7;">~'+Math.round(80*d.avg_unit_price/10000).toLocaleString()+'</b> (10k RMB)'+
        '</div>'+
      '</div>'
    )
  })

  // Add sample listing markers
  sampleMarkers.value.forEach((d, i) => {
    const colors = {45000:'#F56C6C',35000:'#E6A23C',28000:'#409EFF',0:'#67C23A'}
    let color='#67C23A'
    for (const [k,v] of Object.entries(colors)) { if (d.unit_price > parseInt(k)) { color=v; break } }

    const marker = L.marker([d.lat, d.lng], {
      icon: L.divIcon({
        className:'custom-marker',
        html:`<div style="width:22px;height:22px;background:${color};border-radius:50%;border:2px solid rgba(255,255,255,0.4);box-shadow:0 0 10px ${color};cursor:pointer;transition:all 0.3s;"></div>`,
        iconSize:[22,22],iconAnchor:[11,11],
      }),
    }).addTo(leafletMap)

    const photoIdx = i % listingPhotos.length
    const pd = d
    marker.bindPopup(
      '<div style="font-family:sans-serif;min-width:280px;">'+
        '<div style="margin:-14px -14px 0 -14px;border-radius:10px 10px 0 0;overflow:hidden;height:140px;position:relative;">'+
          '<img src="'+listingPhotos[photoIdx]+'" style="width:100%;height:100%;object-fit:cover;" loading="lazy" />'+
          '<div style="position:absolute;inset:0;background:linear-gradient(180deg,transparent 30%,rgba(0,0,0,0.8) 100%);"></div>'+
          '<div style="position:absolute;top:8px;left:8px;background:rgba(0,0,0,0.5);color:#fff;padding:3px 8px;border-radius:4px;font-size:10px;backdrop-filter:blur(4px);">'+pd.district+'</div>'+
          '<div style="position:absolute;bottom:8px;right:8px;color:#fff;font-size:18px;font-weight:800;text-shadow:0 2px 6px rgba(0,0,0,0.7);">'+(pd.total_price||0).toLocaleString()+' (10k RMB)</div>'+
        '</div>'+
        '<div style="display:flex;justify-content:space-between;align-items:center;margin:10px 0 8px;">'+
          '<span style="font-weight:700;color:#fff;font-size:14px;">'+pd.layout+' &middot; '+pd.district+'</span>'+
          '<span style="font-size:11px;background:'+color+';color:#fff;padding:2px 8px;border-radius:10px;">'+(pd.unit_price/1000).toFixed(1)+'k/sqm</span>'+
        '</div>'+
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;font-size:12px;line-height:1.8;">'+
          '<div>Area: <b>'+pd.floor_area+' sqm</b></div>'+
          '<div>Total Price: <b>'+(pd.total_price||0).toLocaleString()+'</b> (10k)</div>'+
          '<div>Est. Rent: <b style="color:#22c55e;">'+(pd.est_rent||0).toLocaleString()+' RMB/mo</b></div>'+
          '<div>Predicted: <b style="color:#a855f7;">'+(pd.predicted_price||0).toLocaleString()+'</b> (10k)</div>'+
          '<div>Decoration: '+pd.decoration+'</div>'+
          '<div>Age: '+pd.building_age+' years</div>'+
          '<div>Orientation: '+pd.orientation+'</div>'+
          '<div>Metro: '+(pd.near_subway?'&#10003; Yes':'&#10008; No')+'</div>'+
        '</div>'+
        '<div style="margin-top:8px;padding-top:8px;border-top:1px solid rgba(255,255,255,0.1);font-size:11px;">'+
          '<span style="color:'+(pd.price_delta>0?'#F56C6C':'#67C23A')+';font-weight:700;">'+
            (pd.price_delta>0?'&#8593; Overvalued':'&#8595; Good Deal')+': '+Math.abs(pd.price_delta||0).toLocaleString()+' (10k RMB) vs prediction'+
          '</span>'+
        '</div>'+
      '</div>'
    , { maxWidth: 320 })

    leafletMarkers.push(marker)
  })

  // Force map to recalculate size after all layers added
  setTimeout(() => {
    if (leafletMap) leafletMap.invalidateSize()
  }, 100)
}

// ============ ANIMATED MAP BACKGROUND ============
function initBgAnimation() {
  if (!bgCanvas.value) return
  if (animFrame) { cancelAnimationFrame(animFrame); animFrame = null }
  const canvas = bgCanvas.value
  const ctx = canvas.getContext('2d')
  const container = canvas.parentElement

  function resize() {
    canvas.width = container.clientWidth
    canvas.height = container.clientHeight
  }
  resize()
  window.addEventListener('resize', resize)

  // Map coordinate space → canvas pixel space
  const mapLngMin=119.5, mapLngMax=120.6, mapLatMin=29.9, mapLatMax=30.6
  function toPixel(lng, lat) {
    return {
      x: ((lng-mapLngMin)/(mapLngMax-mapLngMin))*canvas.width,
      y: ((mapLatMax-lat)/(mapLatMax-mapLatMin))*canvas.height,
    }
  }

  // District nodes for background reference
  const nodes = Object.entries(coords).map(([name, [lng, lat]]) => ({
    name, ...toPixel(lng, lat),
    price: 30000, // will be updated
  }))

  // Floating particles
  const particles = []
  const PARTICLE_COUNT = 80
  for (let i=0;i<PARTICLE_COUNT;i++) {
    particles.push({
      x: Math.random()*canvas.width,
      y: Math.random()*canvas.height,
      r: Math.random()*2+0.8,
      vx: (Math.random()-0.5)*0.6,
      vy: (Math.random()-0.5)*0.6,
      opacity: Math.random()*0.5+0.15,
      pulse: Math.random()*Math.PI*2,
      speed: Math.random()*0.03+0.01,
    })
  }

  // Scanning rings
  const scanRings = []
  function spawnScanRing() {
    const n = nodes[Math.floor(Math.random()*nodes.length)]
    scanRings.push({ x:n.x, y:n.y, radius:0, maxRadius:120+Math.random()*80, opacity:0.5, speed:1.2+Math.random()*0.8 })
  }

  let tick = 0
  function animate() {
    tick++
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    // ---- Grid Lines ----
    ctx.strokeStyle = 'rgba(64,158,255,0.04)'
    ctx.lineWidth = 0.5
    const gridSpacing = 60
    for (let x=gridSpacing;x<canvas.width;x+=gridSpacing) {
      const offset = Math.sin(tick*0.01 + x*0.01)*5
      ctx.beginPath();ctx.moveTo(x+offset,0);ctx.lineTo(x+offset,canvas.height);ctx.stroke()
    }
    for (let y=gridSpacing;y<canvas.height;y+=gridSpacing) {
      const offset = Math.cos(tick*0.01 + y*0.01)*5
      ctx.beginPath();ctx.moveTo(0,y+offset);ctx.lineTo(canvas.width,y+offset);ctx.stroke()
    }

    // ---- Connection Mesh Between Nodes ----
    ctx.strokeStyle = 'rgba(64,158,255,0.06)'
    ctx.lineWidth = 0.6
    for (let i=0;i<nodes.length;i++) {
      for (let j=i+1;j<nodes.length;j++) {
        const dx=nodes[i].x-nodes[j].x, dy=nodes[i].y-nodes[j].y
        const dist=Math.sqrt(dx*dx+dy*dy)
        if (dist<250) {
          const alpha=((250-dist)/250)*0.08
          ctx.strokeStyle=`rgba(64,158,255,${alpha})`
          ctx.beginPath();ctx.moveTo(nodes[i].x,nodes[i].y);ctx.lineTo(nodes[j].x,nodes[j].y);ctx.stroke()
        }
      }
    }

    // ---- District Node Glow ----
    nodes.forEach(n => {
      const pulse=Math.sin(tick*0.04+n.x*0.01)*0.3+0.7
      const grad=ctx.createRadialGradient(n.x,n.y,0,n.x,n.y,22)
      grad.addColorStop(0,`rgba(64,158,255,${0.12*pulse})`)
      grad.addColorStop(0.5,`rgba(64,158,255,${0.04*pulse})`)
      grad.addColorStop(1,'rgba(64,158,255,0)')
      ctx.fillStyle=grad;ctx.beginPath();ctx.arc(n.x,n.y,22,0,Math.PI*2);ctx.fill()

      // Tiny dot
      ctx.fillStyle=`rgba(255,255,255,${0.25*pulse})`
      ctx.beginPath();ctx.arc(n.x,n.y,2,0,Math.PI*2);ctx.fill()
    })

    // ---- Floating Particles ----
    particles.forEach(p => {
      p.pulse+=p.speed
      p.x+=p.vx;p.y+=p.vy
      if(p.x<0)p.x=canvas.width;if(p.x>canvas.width)p.x=0
      if(p.y<0)p.y=canvas.height;if(p.y>canvas.height)p.y=0
      const alpha=Math.sin(p.pulse)*0.25+0.35
      ctx.fillStyle=`rgba(0,212,255,${alpha})`
      ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);ctx.fill()
    })

    // ---- Scanning Rings ----
    if (tick%50===0 && scanRings.length<4) spawnScanRing()
    for (let i=scanRings.length-1;i>=0;i--) {
      const r=scanRings[i]
      r.radius+=r.speed
      const progress=r.radius/r.maxRadius
      if (progress>=1) { scanRings.splice(i,1); continue }
      const alpha=r.opacity*(1-progress)
      ctx.strokeStyle=`rgba(0,212,255,${alpha})`
      ctx.lineWidth=1.2
      ctx.beginPath();ctx.arc(r.x,r.y,r.radius,0,Math.PI*2);ctx.stroke()
    }

    // ---- Data Stream Lines ----
    ctx.strokeStyle='rgba(64,158,255,0.05)'
    ctx.lineWidth=1
    for (let i=0;i<4;i++) {
      ctx.beginPath()
      const startY=(canvas.height/5)*(i+1)+Math.sin(tick*0.015+i)*30
      ctx.moveTo(0,startY)
      for (let x=0;x<canvas.width;x+=40) {
        ctx.lineTo(x,startY+Math.sin(tick*0.02+x*0.005+i)*8)
      }
      ctx.stroke()
    }

    animFrame=requestAnimationFrame(animate)
  }
  animate()
}

function renderMap(){
  if(!mainMap.value||!districtMapData.value.length)return
  const c=safeInitChart(mainMap.value)
  if(!c)return
  const lookup={};districtMapData.value.forEach(d=>lookup[d.district]=d)

  const scatterData=districtMapData.value.map(d=>{
    const coord=coords[d.district]||[120.15,30.25]
    return{value:[...coord,d.count,d.avg_unit_price,d.district,d.pct_of_total,d.avg_total_price,d.avg_building_age,d.median_total_price,d.min_total_price,d.max_total_price],name:d.district}
  })

  // Flow lines
  const flowLines=connections.map(([a,b])=>{
    const ca=coords[a]||[120.15,30.25];const cb=coords[b]||[120.15,30.25]
    const pa=lookup[a];const pb=lookup[b]
    const avgPrice=pa&&pb?(pa.avg_unit_price+pb.avg_unit_price)/2:30000
    return{coords:[ca,cb],price:avgPrice}
  })

  c.setOption({
    backgroundColor:'transparent',
    tooltip:{
      trigger:'item',backgroundColor:'rgba(10,14,23,0.96)',borderColor:'rgba(64,158,255,0.4)',borderWidth:1,
      textStyle:{color:'#c8cdd5',fontSize:12},padding:[14,18],
      formatter:p=>{
        if(!p.data?.value)return''
        const[, ,count,price,name,pct,total,age,median,minP,maxP]=p.data.value
        return`<div style="font-size:16px;font-weight:700;color:#fff;margin-bottom:10px;border-bottom:1px solid rgba(255,255,255,0.1);padding-bottom:8px;">📍 ${name}</div>
          <div style="line-height:2;font-size:13px;">
            <div><span style="color:#9ca3af;">Unit Price:</span> <strong style="color:#409EFF;">${price?.toLocaleString()}</strong> RMB/sqm</div>
            <div><span style="color:#9ca3af;">Total Price:</span> <strong style="color:#67C23A;">${total?.toLocaleString()}</strong> (10k RMB)</div>
            <div><span style="color:#9ca3af;">Median Price:</span> <strong style="color:#fff;">${median?.toLocaleString()}</strong> (10k RMB)</div>
            <div style="margin-top:4px;padding-top:4px;border-top:1px solid rgba(255,255,255,0.06);">
              <span style="color:#9ca3af;">Range:</span> <strong style="color:#F56C6C;">${minP?.toLocaleString()}</strong> – <strong style="color:#22c55e;">${maxP?.toLocaleString()}</strong>
            </div>
            <div><span style="color:#9ca3af;">Listings:</span> <strong style="color:#fff;">${count}</strong> · ${pct}% share</div>
            <div><span style="color:#9ca3af;">Avg Age:</span> <strong style="color:#E6A23C;">${age?.toFixed(0)}</strong> years</div>
          </div>`
      }
    },
    xAxis:{type:'value',min:119.5,max:120.6,axisLine:{show:false},axisTick:{show:false},axisLabel:{show:false},splitLine:{show:false}},
    yAxis:{type:'value',min:29.9,max:30.6,axisLine:{show:false},axisTick:{show:false},axisLabel:{show:false},splitLine:{show:false}},
    series:[
      // Grid lines (subtle background)
      {type:'scatter',data:[[119.5,29.9],[119.5,30.6],[120.6,29.9],[120.6,30.6]],symbolSize:0,silent:true,z:0},
      // Flow connection lines
      ...flowLines.map((f,i)=>({
        type:'lines',coordinateSystem:'cartesian2d',polyline:false,
        data:[{coords:f.coords}],
        lineStyle:{color:priceColor(f.price),opacity:0.12,width:1.5,curveness:0.15},
        effect:{show:true,period:8+Math.random()*4,trailLength:0.25,symbolSize:3,color:priceColor(f.price)},
        silent:true,z:1,
      })),
      // Pulsing effect scatter
      {type:'effectScatter',data:scatterData.filter(d=>d.value[4]!=='Linan'&&d.value[4]!=='Fuyang').map(d=>[d.value[0],d.value[1]]),symbolSize:6,showEffectOn:'render',rippleEffect:{brushType:'stroke',scale:5,period:5,color:'rgba(64,158,255,0.25)'},itemStyle:{color:'rgba(64,158,255,0.4)'},silent:true,z:2},
      // Main bubbles
      {type:'scatter',data:scatterData,symbolSize:d=>Math.max(22,Math.min(65,Math.sqrt(d[2])*3)),itemStyle:{color:d=>priceColor(d[3]),shadowBlur:18,shadowColor:'rgba(0,0,0,0.6)',opacity:0.88,borderColor:'rgba(255,255,255,0.3)',borderWidth:2,borderType:'solid'},label:{show:true,formatter:'{b}',position:'bottom',color:'#c8cdd5',fontSize:10,distance:10,fontWeight:'bold',textShadowBlur:6,textShadowColor:'rgba(0,0,0,0.8)'},emphasis:{scale:1.35,itemStyle:{shadowBlur:28,shadowColor:'rgba(64,158,255,0.5)',opacity:1,borderWidth:3,borderColor:'#fff'},label:{fontSize:14,color:'#fff',fontWeight:'bold'}},z:3},
      // Inner dot (glossy highlight)
      {type:'scatter',data:scatterData.map(d=>[d.value[0],d.value[1]]),symbolSize:d=>Math.max(5,Math.min(15,Math.sqrt(d[2])*0.7)),itemStyle:{color:'rgba(255,255,255,0.35)'},silent:true,z:4},
    ],
  })
  c.on('click',p=>{if(p.data?.value){const n=p.data.value[4];const f=districtMapData.value.find(d=>d.district===n);if(f)selectedDistrict.value=f}})
}

function renderRankings(){
  if(!rankChart.value||!districtMapData.value.length)return
  const c=safeInitChart(rankChart.value)
  if(!c)return
  const sorted=[...districtMapData.value].sort((a,b)=>b.avg_unit_price-a.avg_unit_price)
  c.setOption({
    tooltip:{trigger:'axis',axisPointer:{type:'shadow'}},
    grid:{left:110,right:50,top:5,bottom:20},
    xAxis:{type:'value',name:'RMB/sqm',...da},
    yAxis:{type:'category',data:sorted.map(d=>d.district),...da},
    series:[{type:'bar',data:sorted.map(d=>({value:d.avg_unit_price,itemStyle:{color:priceColor(d.avg_unit_price),borderRadius:[0,6,6,0]}})),label:{show:true,position:'right',color:'#9ca3af',fontSize:10,formatter:'{c}'},barWidth:'60%'}],
  })
}
</script>

<style scoped>
.map-card {
  padding: 0; overflow: hidden;
  border: 1px solid rgba(64,158,255,0.15);
  position: relative;
  background: radial-gradient(ellipse at 30% 40%, rgba(64,158,255,0.04) 0%, transparent 55%),
              radial-gradient(ellipse at 70% 30%, rgba(0,212,255,0.03) 0%, transparent 50%),
              radial-gradient(ellipse at 50% 80%, rgba(168,85,247,0.03) 0%, transparent 50%),
              #0a0e17;
}
.map-bg-canvas {
  position: absolute; top: 0; left: 0; width: 100%; height: 100%;
  z-index: 1; pointer-events: none;
}
.map-glow {
  position: absolute; width: 300px; height: 300px; border-radius: 50%;
  filter: blur(80px); z-index: 0; pointer-events: none; opacity: 0.3;
}
.map-glow-tl { top: -80px; left: -60px; background: rgba(64,158,255,0.15); animation: glow-drift-tl 8s ease-in-out infinite; }
.map-glow-br { bottom: -60px; right: -40px; background: rgba(168,85,247,0.12); animation: glow-drift-br 10s ease-in-out infinite; }

@keyframes glow-drift-tl {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, 20px) scale(1.15); }
  66% { transform: translate(-15px, -10px) scale(0.9); }
}
@keyframes glow-drift-br {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(-25px, 15px) scale(1.2); }
}

.map-canvas { width: 100%; height: 600px; position: relative; z-index: 2; }

.mini-dist-card {
  padding: 10px 12px;
  border-radius: 10px;
  background: rgba(255,255,255,0.015);
  border: 1px solid rgba(255,255,255,0.04);
  cursor: pointer;
  transition: all 0.3s ease;
}
.mini-dist-card:hover, .mini-dist-card.active {
  background: rgba(64,158,255,0.08);
  border-color: rgba(64,158,255,0.3);
  transform: translateX(3px);
}
.mini-dist-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; }
.mini-dist-name { color: #c8cdd5; font-size: 12px; font-weight: 600; }
.mini-dist-count { color: var(--text-muted); font-size: 10px; }
.mini-dist-bar-wrap { height: 4px; background: rgba(255,255,255,0.05); border-radius: 2px; margin: 4px 0; overflow: hidden; }
.mini-dist-bar { height: 100%; border-radius: 2px; transition: width 0.8s cubic-bezier(0.4,0,0.2,1); }
.mini-dist-price { color: var(--text-muted); font-size: 10px; }

.detail-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.04);
}
.detail-row span:first-child { color: var(--text-muted); font-size: 12px; }
.detail-row strong { font-size: 14px; }

.pulse-ring {
  position: absolute; top: 12px; right: 12px;
  width: 10px; height: 10px; border-radius: 50%;
  animation: pulse-ring-anim 2s infinite;
}
.pulse-ring.red { background: #F56C6C; box-shadow: 0 0 6px #F56C6C; }
.pulse-ring.cyan { background: #00d4ff; box-shadow: 0 0 6px #00d4ff; }

@keyframes pulse-ring-anim {
  0% { box-shadow: 0 0 0 0 rgba(64,158,255,0.6); }
  70% { box-shadow: 0 0 0 10px rgba(64,158,255,0); }
  100% { box-shadow: 0 0 0 0 rgba(64,158,255,0); }
}

/* ==== SATELLITE MAP ==== */
.sat-bg-canvas {
  position: absolute; top: 0; left: 0; width: 100%; height: 100%;
  z-index: 5; pointer-events: none;
}
.sat-scan-lines {
  position: absolute; inset: 0; z-index: 1; pointer-events: none;
  background: repeating-linear-gradient(0deg,transparent,transparent 3px,rgba(0,212,255,0.015) 3px,rgba(0,212,255,0.015) 4px);
  animation: scan-lines-scroll 8s linear infinite;
}
@keyframes scan-lines-scroll {
  0% { background-position: 0 0; }
  100% { background-position: 0 100px; }
}
.sat-radar {
  position: absolute; top: 50%; left: 50%; width: 300px; height: 300px;
  transform: translate(-50%,-50%); z-index: 1; pointer-events: none;
  border-radius: 50%;
  border: 1px solid rgba(0,212,255,0.05);
  animation: sat-radar-spin 20s linear infinite;
  background: conic-gradient(from 0deg,transparent 0deg,rgba(0,212,255,0.03) 30deg,transparent 60deg);
}
@keyframes sat-radar-spin {
  0% { transform: translate(-50%,-50%) rotate(0deg); }
  100% { transform: translate(-50%,-50%) rotate(360deg); }
}
/* Fix Leaflet tile rendering on refresh */
:deep(.leaflet-tile) { visibility: visible !important; }
:deep(.leaflet-layer) { visibility: visible !important; }
:deep(.leaflet-container) {
  background: #0a0e17;
  font-family: inherit;
}
:deep(.leaflet-control-zoom a) {
  background: rgba(20,25,35,0.9) !important;
  color: #c8cdd5 !important;
  border-color: rgba(255,255,255,0.1) !important;
}
:deep(.leaflet-control-attribution) {
  background: rgba(10,14,23,0.8) !important;
  color: #6b7280 !important;
  font-size: 10px !important;
}
:deep(.leaflet-popup-content-wrapper) {
  background: rgba(18,22,33,0.96) !important;
  color: #c8cdd5 !important;
  border-radius: 14px !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  backdrop-filter: blur(16px);
}
:deep(.leaflet-popup-tip) {
  background: rgba(18,22,33,0.96) !important;
}
:deep(.leaflet-popup-close-button) {
  color: #9ca3af !important;
}
:deep(.custom-marker) { background:transparent !important; border:none !important; }
:deep(.custom-marker-highlighted) { background:transparent !important; border:none !important; }
:deep(.district-label-marker) { background:transparent !important; border:none !important; }

/* ==== LISTING PREVIEW CARDS ==== */
.listing-preview-card {
  border-radius: 14px;
  overflow: hidden;
  background: rgba(20,25,35,0.7);
  border: 1px solid rgba(255,255,255,0.04);
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.23,1,0.32,1);
}
.listing-preview-card:hover {
  transform: translateY(-6px);
  border-color: rgba(64,158,255,0.25);
  box-shadow: 0 16px 48px rgba(0,0,0,0.5);
}
.listing-preview-card:hover .lpc-hover-glow { opacity: 1; }
.lpc-image {
  position: relative;
  height: 160px;
  overflow: hidden;
}
.lpc-real-img {
  width: 100%; height: 100%; object-fit: cover;
  transition: transform 0.6s cubic-bezier(0.23,1,0.32,1);
}
.listing-preview-card:hover .lpc-real-img {
  transform: scale(1.08);
}
.lpc-img-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(180deg,transparent 30%,rgba(0,0,0,0.7) 100%);
}
.lpc-district-badge {
  position: absolute; top: 10px; left: 10px;
  background: rgba(0,0,0,0.5); color: #fff;
  padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 600;
  backdrop-filter: blur(4px);
}
.lpc-price-badge {
  position: absolute; bottom: 10px; right: 10px;
  color: #fff; font-size: 16px; font-weight: 800;
  text-shadow: 0 2px 8px rgba(0,0,0,0.6);
}
.lpc-hover-glow {
  position: absolute; inset: 0;
  background: radial-gradient(circle at 50% 50%,rgba(64,158,255,0.2),transparent 70%);
  opacity: 0; transition: opacity 0.4s; pointer-events: none;
}
.lpc-body {
  padding: 14px 16px;
}
.lpc-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 4px 0; border-bottom: 1px solid rgba(255,255,255,0.03);
  font-size: 12px;
}
.lpc-row span { color: var(--text-muted); }
.lpc-row strong { color: #c8cdd5; font-size: 12px; }

/* ============ RESPONSIVE ============ */
@media (max-width: 768px) {
  .page-header h2 { font-size: 20px !important; }
  .page-header p { font-size: 12px !important; }

  /* Stat cards: 2 columns */
  .card-grid { grid-template-columns: repeat(2, 1fr) !important; gap: 10px !important; }
  .stat-card { padding: 14px 16px !important; }
  .stat-card .stat-value { font-size: 18px !important; }
  .pulse-ring { top: 8px; right: 8px; }

  /* Legend bar: stack items */
  .section-card[style*="padding:14px 20px"] { padding: 12px 14px !important; }
  .section-card[style*="padding:14px 20px"] > div[style*="display:flex"] {
    gap: 8px !important; flex-wrap: wrap !important;
  }

  /* Main map */
  .map-card { border-radius: 12px !important; }
  .map-canvas { height: 380px !important; }
  .map-bg-canvas { height: 380px !important; }

  /* Section cards */
  .section-card { padding: 14px 12px !important; margin-bottom: 12px !important; }
  .section-card h3 { font-size: 15px !important; }

  /* Bottom 3-column panel → stack */
  div[style*="grid-template-columns:1fr 1fr 1fr"] {
    grid-template-columns: 1fr !important; gap: 12px !important;
  }

  /* Mini district grid: 3 columns on mobile */
  .section-card > div[style*="grid-template-columns:1fr 1fr;gap:8px"] {
    grid-template-columns: repeat(3, 1fr) !important; gap: 6px !important;
  }
  .mini-dist-card { padding: 8px 9px !important; }
  .mini-dist-name { font-size: 10px !important; }
  .mini-dist-price { font-size: 9px !important; }
  .mini-dist-count { font-size: 9px !important; }

  /* Detail panel */
  .detail-row span:first-child { font-size: 11px !important; }
  .detail-row strong { font-size: 12px !important; }

  /* Satellite map */
  [ref="satelliteMap"] { height: 380px !important; }
  .sat-bg-canvas { height: 380px !important; }
  .sat-radar { width: 180px; height: 180px; }

  /* Listing preview cards: single column */
  div[style*="grid-template-columns:repeat(auto-fill,minmax(310px,1fr))"] {
    grid-template-columns: 1fr !important; gap: 12px !important;
  }
  .listing-preview-card .lpc-image { height: 150px !important; }
  .lpc-price-badge { font-size: 14px !important; }
  .listing-preview-card .lpc-body { padding: 12px 14px !important; }
  .lpc-district-badge { font-size: 10px !important; }

  /* Rankings chart */
  [ref="rankChart"] { height: 280px !important; }

  /* District explorer max height */
  .section-card > div[style*="max-height:380px"] {
    max-height: 280px !important;
  }

  /* Map glow effects: reduce for performance */
  .map-glow { width: 180px; height: 180px; filter: blur(50px); }
  .map-glow-tl { top: -40px; left: -30px; }
  .map-glow-br { bottom: -30px; right: -20px; }

  /* Hide Leaflet zoom on small screens */
  :deep(.leaflet-control-zoom) { display: none; }
}

@media (max-width: 480px) {
  .card-grid { grid-template-columns: 1fr !important; gap: 8px !important; }
  .stat-card { padding: 12px 14px !important; }
  .stat-card .stat-value { font-size: 16px !important; }

  .map-canvas { height: 300px !important; }
  [ref="satelliteMap"] { height: 300px !important; }
  [ref="rankChart"] { height: 240px !important; }

  /* Mini district: 2 columns */
  .section-card > div[style*="grid-template-columns:1fr 1fr;gap:8px"] {
    grid-template-columns: repeat(2, 1fr) !important; gap: 5px !important;
  }
  .mini-dist-card { padding: 6px 8px !important; }
  .mini-dist-name { font-size: 9px !important; }

  .listing-preview-card .lpc-image { height: 130px !important; }
  .lpc-price-badge { font-size: 12px !important; }
  .lpc-district-badge { font-size: 9px !important; padding: 3px 7px !important; }

  .section-card[style*="padding:14px 20px"] { padding: 10px 12px !important; }
  .sat-radar { width: 140px; height: 140px; }

  .section-card > div[style*="max-height:380px"] {
    max-height: 240px !important;
  }
}
</style>
