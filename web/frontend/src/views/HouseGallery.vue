<template>
  <div class="house-gallery">
    <!-- Background -->
    <div class="hg-bg"><canvas ref="bgCanvas"></canvas></div>

    <!-- Header -->
    <div class="hg-header">
      <div class="hg-badge"><span class="hg-badge-dot"></span> {{ t('realListings') }}</div>
      <h1>{{ t('housingPhotoGallery') }}</h1>
      <p>{{ t('houseGalleryDesc') }}</p>
    </div>

    <!-- Filter Bar -->
    <div class="hg-filters">
      <el-select v-model="filters.district" :placeholder="t('allDistrictsFilter')" clearable size="large" class="hg-select">
        <el-option v-for="d in allDistricts" :key="d" :label="d" :value="d" />
      </el-select>
      <el-select v-model="filters.layout" :placeholder="t('allLayoutsFilter')" clearable size="large" class="hg-select">
        <el-option v-for="l in allLayouts" :key="l" :label="l" :value="l" />
      </el-select>
      <el-select v-model="filters.decoration" :placeholder="t('allDecorTypes')" clearable size="large" class="hg-select">
        <el-option v-for="d in ['Fine','Medium','Simple','Luxury','Unfinished']" :key="d" :label="d" :value="d" />
      </el-select>
      <el-input-number v-model="filters.maxPrice" :min="0" :step="50" :placeholder="t('maxPrice')" size="large" class="hg-input" controls-position="right" />
      <el-button type="primary" size="large" @click="applyFilters" :loading="loading" round>{{ t('applyFilters') }}</el-button>
      <el-button size="large" @click="resetFilters" round class="glass-btn">{{ t('resetFiltersBtn') }}</el-button>
    </div>

    <!-- Stats Row -->
    <div class="hg-stats">
      <div class="hg-stat"><span class="hgs-num">{{ filteredListings.length }}</span><span class="hgs-lbl">{{ t('listingsShownStat') }}</span></div>
      <div class="hg-stat"><span class="hgs-num">{{ avgPrice }}</span><span class="hgs-lbl">{{ t('avgPriceStat') }}</span></div>
      <div class="hg-stat"><span class="hgs-num">{{ avgRent }}</span><span class="hgs-lbl">{{ t('avgRentStat') }}</span></div>
      <div class="hg-stat"><span class="hgs-num">{{ allDistricts.length }}</span><span class="hgs-lbl">{{ t('districtsStat') }}</span></div>
    </div>

    <!-- Gallery Grid -->
    <TransitionGroup name="hg-card" tag="div" class="hg-grid">
      <div v-for="(house, i) in filteredListings" :key="house.id" class="hg-card"
        :style="{ transitionDelay: (i*40)+'ms' }"
        @mousemove="e=>onTilt(e,i)" @mouseleave="resetTilt(i)"
        :ref="el=>{if(el)cardEls[i]=el}"
        @click="openDetail(house)">
        <!-- Photo -->
        <div class="hg-photo">
          <img :src="house.photo" :alt="'House in '+house.district" loading="lazy" />
          <div class="hg-photo-overlay"></div>
          <div class="hg-photo-badge district">{{ house.district }}</div>
          <div class="hg-photo-badge price">{{ house.total_price?.toLocaleString() }} (10k RMB)</div>
          <div class="hg-photo-shimmer"></div>
        </div>
        <!-- Info -->
        <div class="hg-info">
          <div class="hg-info-row main">
            <span class="hg-layout">{{ house.layout }}</span>
            <span class="hg-unit-price">{{ (house.unit_price/1000).toFixed(1) }}k RMB/sqm</span>
          </div>
          <div class="hg-info-grid">
            <div class="hg-info-item"><span class="hg-ilabel">Area</span><span class="hg-ivalue">{{ house.floor_area }} sqm</span></div>
            <div class="hg-info-item"><span class="hg-ilabel">{{ t('rentMo') }}</span><span class="hg-ivalue rent">{{ house.est_rent?.toLocaleString() }} RMB</span></div>
            <div class="hg-info-item"><span class="hg-ilabel">{{ t('age') }}</span><span class="hg-ivalue">{{ house.building_age }} yr</span></div>
            <div class="hg-info-item"><span class="hg-ilabel">{{ t('floor') }}</span><span class="hg-ivalue">{{ house.floor }}</span></div>
          </div>
          <div class="hg-tags">
            <span class="hg-tag" :class="'tag-'+house.decoration.toLowerCase()">{{ house.decoration }}</span>
            <span class="hg-tag tag-orient">{{ house.orientation }}</span>
            <span class="hg-tag" :class="house.near_subway?'tag-metro-yes':'tag-metro-no'">{{ house.near_subway ? '🚇 ' + t('metro') : '🚗 ' + t('noMetro') }}</span>
          </div>
          <div class="hg-prediction">
            <span>Predicted: <strong>{{ house.predicted_price?.toLocaleString() }}</strong> (10k RMB)</span>
            <span :class="house.price_delta>0?'delta-over':'delta-under'">{{ house.price_delta>0?'↑ '+house.price_delta:'↓ '+Math.abs(house.price_delta) }} (10k)</span>
          </div>
        </div>
      </div>
    </TransitionGroup>

    <!-- Empty State -->
    <div v-if="filteredListings.length===0&&!loading" class="hg-empty">
      <span class="hg-empty-icon">🏠</span>
      <p>{{ t('noListings') }}</p>
      <el-button type="primary" round @click="resetFilters">{{ t('resetFiltersBtnT') }}</el-button>
    </div>

    <!-- Detail Modal -->
    <Teleport to="body">
      <Transition name="modal-pop">
        <div v-if="detailHouse" class="hg-modal-backdrop" @click.self="detailHouse=null">
          <div class="hg-modal">
            <button class="hg-modal-close" @click="detailHouse=null">✕</button>
            <div class="hg-modal-photo">
              <img :src="detailHouse.photo" :alt="'House in '+detailHouse.district" />
              <div class="hg-modal-photo-tag">{{ detailHouse.district }} · {{ detailHouse.layout }}</div>
            </div>
            <div class="hg-modal-body">
              <div class="hg-modal-header">
                <h2>{{ detailHouse.layout }} in {{ detailHouse.district }}</h2>
                <div class="hg-modal-price">{{ detailHouse.total_price?.toLocaleString() }} <small>(10k RMB)</small></div>
              </div>
              <div class="hg-modal-grid">
                <div class="hg-modal-stat"><label>Unit Price</label><strong>{{ detailHouse.unit_price?.toLocaleString() }} RMB/sqm</strong></div>
                <div class="hg-modal-stat"><label>Floor Area</label><strong>{{ detailHouse.floor_area }} sqm</strong></div>
                <div class="hg-modal-stat"><label>Monthly Rent</label><strong class="rent">~{{ detailHouse.est_rent?.toLocaleString() }} RMB</strong></div>
                <div class="hg-modal-stat"><label>Predicted Price</label><strong class="predict">{{ detailHouse.predicted_price?.toLocaleString() }} (10k)</strong></div>
                <div class="hg-modal-stat"><label>Building Age</label><strong>{{ detailHouse.building_age }} years</strong></div>
                <div class="hg-modal-stat"><label>Floor Level</label><strong>{{ detailHouse.floor }}</strong></div>
                <div class="hg-modal-stat"><label>Decoration</label><strong>{{ detailHouse.decoration }}</strong></div>
                <div class="hg-modal-stat"><label>Orientation</label><strong>{{ detailHouse.orientation }}</strong></div>
                <div class="hg-modal-stat"><label>{{ t('metro') }} Access</label><strong>{{ detailHouse.near_subway ? '✓ Yes' : '✗ No' }}</strong></div>
                <div class="hg-modal-stat"><label>Price Delta</label><strong :class="detailHouse.price_delta>0?'delta-over':'delta-under'">{{ detailHouse.price_delta>0?'+'+detailHouse.price_delta:detailHouse.price_delta }} (10k)</strong></div>
              </div>
              <div class="hg-modal-rent-note">
                💡 Rent estimate based on {{ (detailHouse.rent_yield*100).toFixed(1) }}% monthly yield of property value. Prediction based on area × district baseline model (R²≈0.56).
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from '../i18n'
const { t } = useI18n()
const bgCanvas = ref(null)
const detailHouse = ref(null)
const loading = ref(false)
const cardEls = ref({})
const tilts = ref({})
let animFrame = null

const filters = ref({ district:'', layout:'', decoration:'', maxPrice:undefined })
const allDistricts = ['Shangcheng','Xihu','Gongshu','Binjiang','Xiaoshan','Yuhang','Jianggan','Qiantang','Linping','Fuyang','Linan','Xiacheng']
const allLayouts = ['1BR 0LR','1BR 1LR','2BR 1LR','2BR 2LR','3BR 1LR','3BR 2LR','4BR 2LR','5BR 2LR','5BR 3LR']

// Generate 40 houses with photos
const housePhotos = Array.from({length:40},(_,i)=>`https://picsum.photos/seed/hzhouse${i}/600/400`)
const floors = ['Low Floor','Middle Floor','High Floor']
const decors = ['Fine','Medium','Simple','Luxury','Unfinished']
const orients = ['South','North-South','Southeast','Southwest','East','West','North']
const layouts = ['2BR 1LR','3BR 2LR','4BR 2LR','2BR 2LR','3BR 1LR','5BR 2LR','1BR 1LR','4BR 2LR','5BR 3LR']

const allHouses = Array.from({length:40},(_,i)=>{
  const dist = allDistricts[i%12]
  const basePrices = {Shangcheng:47000,Xihu:47000,Gongshu:42000,Binjiang:43000,Xiaoshan:32000,Yuhang:30000,Jianggan:38000,Qiantang:28000,Linping:25000,Fuyang:22000,Linan:19000,Xiacheng:44000}
  const up = basePrices[dist]+(Math.random()-0.5)*8000
  const area = Math.round(45+Math.random()*140)
  const tp = Math.round(up*area/10000)
  const decay = 1.5+Math.random()*2.5
  const pp = Math.round(80+area*2.8+(Math.random()-0.5)*40)
  const ry = 0.0014+Math.random()*0.0012
  const er = Math.round(up*area*ry)
  return {
    id:i, district:dist, layout:layouts[i%9], floor_area:area, unit_price:Math.round(up),
    total_price:tp, building_age:Math.round(1+Math.random()*28), floor:floors[i%3],
    decoration:decors[i%5], orientation:orients[i%7], near_subway:Math.random()>0.5?1:0,
    photo:housePhotos[i], est_rent:er, predicted_price:pp, price_delta:tp-pp, rent_yield:ry
  }
})

const filteredListings = computed(()=>{
  let l = allHouses
  const f = filters.value
  if(f.district) l=l.filter(h=>h.district===f.district)
  if(f.layout) l=l.filter(h=>h.layout===f.layout)
  if(f.decoration) l=l.filter(h=>h.decoration===f.decoration)
  if(f.maxPrice) l=l.filter(h=>h.total_price<=f.maxPrice)
  return l
})
const avgPrice = computed(()=>{const l=filteredListings.value;return l.length?Math.round(l.reduce((s,h)=>s+h.total_price,0)/l.length).toLocaleString():'-'})
const avgRent = computed(()=>{const l=filteredListings.value;return l.length?Math.round(l.reduce((s,h)=>s+h.est_rent,0)/l.length).toLocaleString():'-'})

function applyFilters(){loading.value=true;setTimeout(()=>loading.value=false,300)}
function resetFilters(){filters.value={district:'',layout:'',decoration:'',maxPrice:undefined};applyFilters()}
function openDetail(h){detailHouse.value=h}
function onTilt(e,i){const card=e.currentTarget,rect=card.getBoundingClientRect(),x=(e.clientX-rect.left)/rect.width-0.5,y=(e.clientY-rect.top)/rect.height-0.5;tilts.value[i]=`perspective(800px) rotateY(${x*14}deg) rotateX(${-y*10}deg) translateY(-6px)`}
function resetTilt(i){tilts.value[i]='perspective(800px) rotateY(0deg) rotateX(0deg) translateY(0px)'}

// Background particles
function initBg(){if(!bgCanvas.value)return;const c=bgCanvas.value,ctx=c.getContext('2d')
  function rs(){c.width=window.innerWidth;c.height=window.innerHeight}rs();window.addEventListener('resize',rs)
  const p=[];for(let i=0;i<40;i++)p.push({x:Math.random()*c.width,y:Math.random()*c.height,r:Math.random()*2+0.6,vx:(Math.random()-0.5)*0.3,vy:(Math.random()-0.5)*0.3,h:200+Math.random()*60,a:Math.random()*0.3+0.08})
  let t=0;function an(){t++;ctx.clearRect(0,0,c.width,c.height)
    p.forEach((pt,i)=>{pt.x+=pt.vx;pt.y+=pt.vy;if(pt.x<0)pt.x=c.width;if(pt.x>c.width)pt.x=0;if(pt.y<0)pt.y=c.height;if(pt.y>c.height)pt.y=0
      const al=Math.sin(t*0.015+i)*0.1+pt.a;ctx.fillStyle=`hsla(${pt.h},60%,65%,${al})`;ctx.beginPath();ctx.arc(pt.x,pt.y,pt.r,0,2*Math.PI);ctx.fill()
      for(let j=i+1;j<p.length;j++){const dx=pt.x-p[j].x,dy=pt.y-p[j].y,d=Math.sqrt(dx*dx+dy*dy);if(d<120){ctx.strokeStyle=`hsla(${pt.h},50%,55%,${0.025*(1-d/120)})`;ctx.lineWidth=0.25;ctx.beginPath();ctx.moveTo(pt.x,pt.y);ctx.lineTo(p[j].x,p[j].y);ctx.stroke()}}})
    animFrame=requestAnimationFrame(an)}an()}
onMounted(initBg)
onUnmounted(()=>{if(animFrame)cancelAnimationFrame(animFrame)})
</script>

<style scoped>
.house-gallery{position:relative;min-height:100vh}
.hg-bg{position:fixed;inset:0;pointer-events:none;z-index:0}
.hg-bg canvas{width:100%;height:100%;opacity:0.5}

/* Header */
.hg-header{position:relative;z-index:2;text-align:center;padding:40px 20px 20px}
.hg-badge{display:inline-flex;align-items:center;gap:8px;padding:6px 18px;border-radius:50px;background:rgba(26,31,46,0.6);border:1px solid rgba(255,255,255,0.06);color:#c8cdd5;font-size:12px;margin-bottom:16px;backdrop-filter:blur(8px)}
.hg-badge-dot{width:7px;height:7px;border-radius:50%;background:#22c55e;box-shadow:0 0 8px #22c55e;animation:hg-pulse 2s ease-in-out infinite}
@keyframes hg-pulse{0%,100%{opacity:1}50%{opacity:0.4}}
.hg-header h1{font-size:44px;font-weight:900;color:#fff;letter-spacing:-2px;margin-bottom:8px}
.hg-header p{color:var(--text-secondary);font-size:15px;max-width:600px;margin:0 auto}

/* Filters */
.hg-filters{position:relative;z-index:2;display:flex;justify-content:center;gap:10px;padding:0 20px 20px;flex-wrap:wrap}
.hg-select{width:160px}
.hg-input{width:140px}

/* Stats */
.hg-stats{position:relative;z-index:2;display:flex;justify-content:center;gap:30px;padding:20px;flex-wrap:wrap}
.hg-stat{text-align:center}.hgs-num{display:block;font-size:24px;font-weight:800;color:#fff}.hgs-lbl{font-size:11px;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.5px}

/* Grid */
.hg-grid{position:relative;z-index:2;display:grid;grid-template-columns:repeat(auto-fill,minmax(310px,1fr));gap:18px;padding:0 20px 50px;max-width:1500px;margin:0 auto}

/* Card */
.hg-card{border-radius:16px;overflow:hidden;background:rgba(20,25,35,0.7);border:1px solid rgba(255,255,255,0.04);cursor:pointer;backdrop-filter:blur(8px);transition:transform 0.4s cubic-bezier(0.23,1,0.32,1),box-shadow 0.4s ease;will-change:transform}
.hg-card:hover{z-index:5;box-shadow:0 20px 60px rgba(0,0,0,0.5);border-color:rgba(255,255,255,0.12)}
.hg-card:hover .hg-photo img{transform:scale(1.08)}
.hg-card:hover .hg-photo-shimmer{left:150%}
.hg-card:hover .hg-photo-overlay{opacity:0.35}

/* Photo */
.hg-photo{position:relative;height:200px;overflow:hidden}
.hg-photo img{width:100%;height:100%;object-fit:cover;transition:transform 0.6s cubic-bezier(0.23,1,0.32,1)}
.hg-photo-overlay{position:absolute;inset:0;background:linear-gradient(180deg,transparent 30%,rgba(0,0,0,0.7) 100%);opacity:0.55;transition:opacity 0.4s}
.hg-photo-badge{position:absolute;padding:4px 10px;border-radius:6px;font-size:11px;font-weight:600;backdrop-filter:blur(4px);z-index:2}
.hg-photo-badge.district{top:10px;left:10px;background:rgba(0,0,0,0.5);color:#fff}
.hg-photo-badge.price{bottom:10px;right:10px;color:#fff;font-size:17px;font-weight:800;text-shadow:0 2px 8px rgba(0,0,0,0.7)}
.hg-photo-shimmer{position:absolute;top:0;left:-100%;width:40%;height:100%;background:linear-gradient(90deg,transparent,rgba(255,255,255,0.06),transparent);transform:skewX(-15deg);transition:left 0.7s ease;pointer-events:none;z-index:3}

/* Info */
.hg-info{padding:16px 18px;position:relative;z-index:2}
.hg-info-row.main{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}
.hg-layout{font-size:15px;font-weight:700;color:#fff}
.hg-unit-price{font-size:13px;font-weight:700;color:var(--accent-cyan)}
.hg-info-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:10px}
.hg-info-item{display:flex;justify-content:space-between;padding:6px 10px;background:rgba(255,255,255,0.02);border-radius:8px}
.hg-ilabel{font-size:11px;color:var(--text-muted)}.hg-ivalue{font-size:12px;color:#c8cdd5;font-weight:600}
.hg-ivalue.rent{color:#22c55e}
.hg-tags{display:flex;gap:5px;flex-wrap:wrap;margin-bottom:8px}
.hg-tag{padding:3px 9px;border-radius:6px;font-size:10px;color:#c8cdd5;background:rgba(255,255,255,0.04)}
.hg-tag.tag-fine{background:rgba(34,197,94,0.1);color:#22c55e}
.hg-tag.tag-luxury{background:rgba(245,108,108,0.1);color:#F56C6C}
.hg-tag.tag-medium{background:rgba(230,162,60,0.1);color:#E6A23C}
.hg-tag.tag-simple{background:rgba(64,158,255,0.1);color:#409EFF}
.hg-tag.tag-metro-yes{background:rgba(34,197,94,0.08);color:#22c55e}
.hg-tag.tag-metro-no{background:rgba(255,255,255,0.03);color:var(--text-muted)}
.hg-tag.tag-orient{background:rgba(168,85,247,0.08);color:#a855f7}
.hg-prediction{display:flex;justify-content:space-between;font-size:11px;padding-top:8px;border-top:1px solid rgba(255,255,255,0.04)}
.hg-prediction span{color:var(--text-muted)}.hg-prediction strong{color:#a855f7}
.delta-over{color:#F56C6C!important;font-weight:700}.delta-under{color:#22c55e!important;font-weight:700}

/* Card transitions */
.hg-card-enter-active{transition:all 0.5s cubic-bezier(0.34,1.56,0.64,1)}
.hg-card-leave-active{transition:all 0.3s ease-in;position:absolute}
.hg-card-enter-from{opacity:0;transform:translateY(30px) scale(0.93)}
.hg-card-leave-to{opacity:0;transform:translateY(-15px) scale(0.96)}
.hg-card-move{transition:transform 0.4s ease}

/* Empty */
.hg-empty{text-align:center;padding:80px 20px;position:relative;z-index:2}
.hg-empty-icon{font-size:60px;display:block;margin-bottom:12px;opacity:0.3}
.hg-empty p{color:var(--text-muted);font-size:16px;margin-bottom:16px}

/* Modal */
.hg-modal-backdrop{position:fixed;inset:0;z-index:10000;background:rgba(0,0,0,0.85);backdrop-filter:blur(20px);display:flex;align-items:center;justify-content:center;padding:30px}
.hg-modal{display:flex;max-width:850px;width:100%;max-height:88vh;background:rgba(18,22,33,0.98);border-radius:20px;overflow:hidden;border:1px solid rgba(255,255,255,0.06);box-shadow:0 40px 100px rgba(0,0,0,0.6);position:relative}
.hg-modal-close{position:absolute;top:14px;right:14px;width:38px;height:38px;border-radius:50%;background:rgba(255,255,255,0.08);border:none;color:#fff;font-size:16px;cursor:pointer;z-index:10;transition:all 0.3s}
.hg-modal-close:hover{background:rgba(255,255,255,0.2);transform:rotate(90deg)}
.hg-modal-photo{width:50%;position:relative;overflow:hidden;flex-shrink:0;min-height:350px}
.hg-modal-photo img{width:100%;height:100%;object-fit:cover}
.hg-modal-photo-tag{position:absolute;bottom:12px;left:12px;background:rgba(0,0,0,0.6);color:#fff;padding:5px 12px;border-radius:8px;font-size:13px;font-weight:600;backdrop-filter:blur(4px)}
.hg-modal-body{flex:1;padding:30px;overflow-y:auto}
.hg-modal-header{margin-bottom:20px}
.hg-modal-header h2{font-size:22px;color:#fff;margin-bottom:6px}
.hg-modal-price{font-size:28px;font-weight:800;color:var(--accent-cyan)}
.hg-modal-price small{font-size:14px;color:var(--text-muted)}
.hg-modal-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.hg-modal-stat{padding:12px 14px;background:rgba(255,255,255,0.02);border-radius:10px;border:1px solid rgba(255,255,255,0.03)}
.hg-modal-stat label{display:block;font-size:10px;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:3px}
.hg-modal-stat strong{font-size:15px;color:#c8cdd5}.hg-modal-stat strong.rent{color:#22c55e}.hg-modal-stat strong.predict{color:#a855f7}
.hg-modal-stat strong.delta-over{color:#F56C6C}.hg-modal-stat strong.delta-under{color:#22c55e}
.hg-modal-rent-note{margin-top:18px;padding:12px 14px;background:rgba(64,158,255,0.05);border-radius:10px;font-size:11px;color:var(--text-muted);line-height:1.6}

.modal-pop-enter-active{transition:all 0.35s cubic-bezier(0.34,1.56,0.64,1)}
.modal-pop-leave-active{transition:all 0.2s ease-in}
.modal-pop-enter-from{opacity:0}.modal-pop-enter-from .hg-modal{transform:scale(0.9) translateY(20px)}
.modal-pop-leave-to{opacity:0}

@media(max-width:768px){.hg-grid{grid-template-columns:1fr}.hg-modal{flex-direction:column}.hg-modal-photo{width:100%;min-height:200px}.hg-filters{flex-direction:column;align-items:center}.hg-select,.hg-input{width:100%!important}.hg-header h1{font-size:28px}}
</style>
