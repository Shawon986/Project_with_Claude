<template>
  <div class="story-page" @mousemove="onGlobalMouse">
    <!-- Background Layers -->
    <div class="bg-layers">
      <canvas ref="bgCanvas" class="bg-canvas"></canvas>
      <div class="bg-orbs"><div class="orb o1"></div><div class="orb o2"></div><div class="orb o3"></div></div>
      <div class="bg-grain"></div>
    </div>

    <!-- Parallax Shapes -->
    <div class="parallax-shapes">
      <div class="pshape ps1" :style="{transform:'translate('+(-mouseX*6)+'px,'+(-mouseY*6)+'px)'}"></div>
      <div class="pshape ps2" :style="{transform:'translate('+(mouseX*4)+'px,'+(mouseY*4)+'px)'}"></div>
      <div class="pshape ps3" :style="{transform:'translate('+(-mouseX*3)+'px,'+(mouseY*5)+'px)'}"></div>
    </div>

    <!-- ============================================ -->
    <!-- CHAPTER 0: HERO — The Story Begins -->
    <!-- ============================================ -->
    <section class="story-hero">
      <div class="hero-chapter-tag">Chapter Zero</div>
      <h1 class="hero-title">
        <span class="ht-line1">The Story of</span>
        <span class="ht-line2">Hangzhou's Homes</span>
      </h1>
      <p class="hero-desc">
        Every listing holds a story. Every price tells a tale. Through data, we uncover the hidden narrative
        of a city's housing market — where people live, what they pay, and why. This is visual storytelling
        through the lens of 3,455 second-hand housing listings across 12 districts.
      </p>
      <div class="hero-scroll-hint">
        <span>Scroll to begin the journey</span>
        <div class="scroll-arrow">↓</div>
      </div>
    </section>

    <!-- ============================================ -->
    <!-- CHAPTER 1: The Landscape -->
    <!-- ============================================ -->
    <section class="story-chapter">
      <div class="chapter-marker">
        <div class="chapter-line"></div>
        <div class="chapter-num">01</div>
        <div class="chapter-line"></div>
      </div>
      <div class="chapter-header">
        <h2>The Geographic Landscape</h2>
        <p>Where are the homes? How do prices paint the map of Hangzhou?</p>
      </div>

      <div class="story-cards">
        <div class="s-card" v-for="(item, i) in chapter1Items" :key="i"
          @mousemove="e=>onCardTilt(e,'c1-'+i)" @mouseleave="resetCardTilt('c1-'+i)"
          :style="{transform:cardTilts['c1-'+i]||''}" @click="openStory(item)">
          <div class="sc-art" :style="{background:item.gradient}">
            <div class="sc-art-icon">{{ item.icon }}</div>
            <div class="sc-art-glow" :style="{background:'radial-gradient(circle at 50% 50%,'+item.accent+'22,transparent 70%)'}"></div>
          </div>
          <div class="sc-info">
            <span class="sc-accent" :style="{color:item.accent}">{{ item.category }}</span>
            <h3>{{ item.title }}</h3>
            <p>{{ item.desc }}</p>
          </div>
        </div>
      </div>

      <div class="chapter-insight">
        <div class="insight-icon">💡</div>
        <p><strong>Key Insight:</strong> Hangzhou's housing prices follow a clear spatial gradient —
        from the premium West Lake core (>47k RMB/sqm) radiating outward to affordable suburban edges
        (<19k RMB/sqm). The price ratio between the most and least expensive district is
        <span style="color:#F56C6C;font-weight:700;">2.5×</span>.</p>
      </div>
    </section>

    <!-- ============================================ -->
    <!-- CHAPTER 2: The Price Story -->
    <!-- ============================================ -->
    <section class="story-chapter">
      <div class="chapter-marker">
        <div class="chapter-line"></div>
        <div class="chapter-num">02</div>
        <div class="chapter-line"></div>
      </div>
      <div class="chapter-header">
        <h2>The Anatomy of Price</h2>
        <p>What drives a home's value? Dissecting the forces behind every listing.</p>
      </div>

      <div class="story-cards">
        <div class="s-card" v-for="(item, i) in chapter2Items" :key="i"
          @mousemove="e=>onCardTilt(e,'c2-'+i)" @mouseleave="resetCardTilt('c2-'+i)"
          :style="{transform:cardTilts['c2-'+i]||''}" @click="openStory(item)">
          <div class="sc-art" :style="{background:item.gradient}">
            <div class="sc-art-icon">{{ item.icon }}</div>
            <div class="sc-art-glow" :style="{background:'radial-gradient(circle at 50% 50%,'+item.accent+'22,transparent 70%)'}"></div>
          </div>
          <div class="sc-info">
            <span class="sc-accent" :style="{color:item.accent}">{{ item.category }}</span>
            <h3>{{ item.title }}</h3>
            <p>{{ item.desc }}</p>
          </div>
        </div>
      </div>

      <div class="chapter-insight">
        <div class="insight-icon">📐</div>
        <p><strong>Key Insight:</strong> Floor area is the dominant price driver — each additional square meter
        adds approximately <span style="color:#409EFF;font-weight:700;">~4,200 RMB</span> to total price.
        Building age reduces value by <span style="color:#F56C6C;font-weight:700;">~2% annually</span> after year 10.
        The regression model explains <span style="color:#22c55e;font-weight:700;">56%</span> of price variance (R²=0.56).</p>
      </div>
    </section>

    <!-- ============================================ -->
    <!-- CHAPTER 3: Hidden Patterns -->
    <!-- ============================================ -->
    <section class="story-chapter">
      <div class="chapter-marker">
        <div class="chapter-line"></div>
        <div class="chapter-num">03</div>
        <div class="chapter-line"></div>
      </div>
      <div class="chapter-header">
        <h2>Hidden Patterns & Dimensions</h2>
        <p>PCA and Factor Analysis reveal the invisible structure beneath the data.</p>
      </div>

      <div class="story-cards">
        <div class="s-card" v-for="(item, i) in chapter3Items" :key="i"
          @mousemove="e=>onCardTilt(e,'c3-'+i)" @mouseleave="resetCardTilt('c3-'+i)"
          :style="{transform:cardTilts['c3-'+i]||''}" @click="openStory(item)">
          <div class="sc-art" :style="{background:item.gradient}">
            <div class="sc-art-icon">{{ item.icon }}</div>
            <div class="sc-art-glow" :style="{background:'radial-gradient(circle at 50% 50%,'+item.accent+'22,transparent 70%)'}"></div>
          </div>
          <div class="sc-info">
            <span class="sc-accent" :style="{color:item.accent}">{{ item.category }}</span>
            <h3>{{ item.title }}</h3>
            <p>{{ item.desc }}</p>
          </div>
        </div>
      </div>

      <div class="chapter-insight">
        <div class="insight-icon">🔮</div>
        <p><strong>Key Insight:</strong> 5 principal components capture <span style="color:#a855f7;font-weight:700;">69.2%</span>
        of total variance. The first component (Size/Price) alone explains 21.5%. Factor Analysis with KMO=0.53
        confirms 5 latent dimensions: Size, Quality, Location, Age, and Amenity factors.</p>
      </div>
    </section>

    <!-- ============================================ -->
    <!-- CHAPTER 4: The People — Market Segments -->
    <!-- ============================================ -->
    <section class="story-chapter">
      <div class="chapter-marker">
        <div class="chapter-line"></div>
        <div class="chapter-num">04</div>
        <div class="chapter-line"></div>
      </div>
      <div class="chapter-header">
        <h2>The People Behind the Prices</h2>
        <p>Cluster analysis reveals 5 distinct buyer personas and their housing choices.</p>
      </div>

      <div class="story-cards">
        <div class="s-card" v-for="(item, i) in chapter4Items" :key="i"
          @mousemove="e=>onCardTilt(e,'c4-'+i)" @mouseleave="resetCardTilt('c4-'+i)"
          :style="{transform:cardTilts['c4-'+i]||''}" @click="openStory(item)">
          <div class="sc-art" :style="{background:item.gradient}">
            <div class="sc-art-icon">{{ item.icon }}</div>
            <div class="sc-art-glow" :style="{background:'radial-gradient(circle at 50% 50%,'+item.accent+'22,transparent 70%)'}"></div>
          </div>
          <div class="sc-info">
            <span class="sc-accent" :style="{color:item.accent}">{{ item.category }}</span>
            <h3>{{ item.title }}</h3>
            <p>{{ item.desc }}</p>
          </div>
        </div>
      </div>

      <div class="chapter-insight">
        <div class="insight-icon">👥</div>
        <p><strong>Key Insight:</strong> 5 distinct market segments exist — from Compact Entry-Level buyers
        (~70sqm, budget-conscious) to Premium Large Unit seekers (~140sqm, luxury-focused). LDA achieves
        <span style="color:#22c55e;font-weight:700;">64.6%</span> accuracy in distinguishing these groups,
        confirming genuine structural differences in the market.</p>
      </div>
    </section>

    <!-- ============================================ -->
    <!-- EPILOGUE -->
    <!-- ============================================ -->
    <section class="story-epilogue">
      <div class="epilogue-icon">✦</div>
      <h2>The Story Continues</h2>
      <p>
        Every day, new listings appear. Prices shift. Neighborhoods evolve. The 3,455 listings we analyzed
        are a snapshot — a single frame in Hangzhou's ongoing urban story. Behind each data point is a family
        making a decision, a community changing, a city growing.
      </p>
      <p class="epilogue-credit">
        Data sourced from Lianjia Hangzhou · Analyzed with Python, scikit-learn, and ECharts ·
        Visualized with Vue 3 and FastAPI
      </p>
      <div class="epilogue-stats">
        <div class="ep-stat"><strong>3,455</strong><span>Listings Analyzed</span></div>
        <div class="ep-stat"><strong>12</strong><span>Districts Mapped</span></div>
        <div class="ep-stat"><strong>6</strong><span>Analysis Methods</span></div>
        <div class="ep-stat"><strong>22</strong><span>Data Features</span></div>
      </div>
    </section>

    <!-- Lightbox -->
    <Teleport to="body">
      <Transition name="lb-smooth">
        <div v-if="lightbox" class="lb-backdrop" @click.self="lightbox=null">
          <div class="lb-container">
            <button class="lb-close-btn" @click="lightbox=null"><span class="close-icon"></span></button>
            <div class="lb-hero-art" :style="{background:lightbox.gradient}">
              <div class="lb-art-icon">{{ lightbox.icon }}</div>
            </div>
            <div class="lb-body">
              <span class="lb-cat" :style="{color:lightbox.accent}">{{ lightbox.category }}</span>
              <h2>{{ lightbox.title }}</h2>
              <p class="lb-desc">{{ lightbox.desc }}</p>
              <div class="lb-tags"><span v-for="t in lightbox.tags" :key="t">{{ t }}</span></div>
              <div class="lb-stats-row">
                <div class="lb-stat-card"><div class="lb-stat-val" :style="{color:lightbox.accent}">{{ lightbox.stat1 }}</div><div class="lb-stat-lbl">{{ lightbox.stat1Label }}</div></div>
                <div class="lb-stat-card"><div class="lb-stat-val" :style="{color:lightbox.accent}">{{ lightbox.stat2 }}</div><div class="lb-stat-lbl">{{ lightbox.stat2Label }}</div></div>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useI18n } from '../i18n'
const { t } = useI18n()

const mouseX=ref(0), mouseY=ref(0), lightbox=ref(null), bgCanvas=ref(null), cardTilts=ref({})
let animFrame=null

const chapter1Items = [
  { category:'Spatial Analysis',icon:'🏙️',title:'Xihu — The Premium Heart',desc:'Adjacent to West Lake, UNESCO heritage. Average 47,146 RMB/sqm. Historic neighborhoods with strict height limits. 366 active listings.',tags:['Xihu','West Lake','Premium'],gradient:'linear-gradient(135deg,#0a101c,#141e30,#1a2438)',accent:'#409EFF',stat1:'47.1k',stat1Label:'RMB/sqm',stat2:'366',stat2Label:'Listings'},
  { category:'Spatial Analysis',icon:'🏘️',title:'Yuhang — The Rising Edge',desc:'Largest volume: 503 listings. Tech corridor near Alibaba Xixi. Average 29,505 RMB/sqm. Rapid appreciation as infrastructure expands.',tags:['Yuhang','Growth','Tech'],gradient:'linear-gradient(135deg,#140e08,#201810,#1c2014)',accent:'#E6A23C',stat1:'503',stat1Label:'Listings',stat2:'29.5k',stat2Label:'RMB/sqm'},
  { category:'Spatial Analysis',icon:'🌆',title:'Binjiang — Innovation Hub',desc:'High-Tech Zone. 304 listings averaging 42,781 RMB/sqm. Modern high-rises for Alibaba, NetEase, Hikvision professionals.',tags:['Binjiang','Tech','Modern'],gradient:'linear-gradient(135deg,#08141c,#101e2c,#0c1c28)',accent:'#0ea5e9',stat1:'304',stat1Label:'Listings',stat2:'42.8k',stat2Label:'RMB/sqm'},
  { category:'Spatial Analysis',icon:'🗺️',title:'The Price Gradient Map',desc:'From Shangcheng (47k) to Linan (18.6k) — a 2.5× spatial price gradient. Core districts cluster above 40k, suburbs below 25k RMB/sqm.',tags:['Map','Gradient','Spatial'],gradient:'linear-gradient(135deg,#180a0a,#241410,#1a1420)',accent:'#F56C6C',stat1:'2.5×',stat1Label:'Gradient',stat2:'12',stat2Label:'Districts'},
]

const chapter2Items = [
  { category:'Price Driver',icon:'📊',title:'Floor Area — The Dominant Force',desc:'Each additional square meter adds ~4,200 RMB to total price. The strongest single predictor in regression analysis. R² contribution: 0.48.',tags:['Area','Predictor','Linear'],gradient:'linear-gradient(135deg,#0a1208,#162312,#1a2a14)',accent:'#67C23A',stat1:'+4.2k',stat1Label:'per sqm',stat2:'R²=0.48',stat2Label:'Contribution'},
  { category:'Price Driver',icon:'📉',title:'Building Age — The Decay Factor',desc:'Properties lose ~3% value annually after year 10. Steepest decline between years 20-30. Core districts resist depreciation better than suburbs.',tags:['Age','Depreciation','Time'],gradient:'linear-gradient(135deg,#1c0a0a,#281410,#18141c)',accent:'#f43f5e',stat1:'-3%/yr',stat1Label:'Depreciation',stat2:'20yr+',stat2Label:'Steep Drop'},
  { category:'Price Driver',icon:'🚇',title:'Subway — The Connectivity Premium',desc:'45.7% of listings near metro stations. Proximity adds 5-15% price premium. Effect strongest in outer districts where transit transforms accessibility.',tags:['Transit','Premium','Access'],gradient:'linear-gradient(135deg,#08101c,#101c2c,#0c1c18)',accent:'#6366f1',stat1:'45.7%',stat1Label:'Coverage',stat2:'+5-15%',stat2Label:'Premium'},
  { category:'Price Driver',icon:'🔬',title:'The Full Regression Model',desc:'22 features combined: R²=0.56, CV R²=0.55. Top predictors: floor area, district (Xihu/Shangcheng), rooms count, building age, decoration level.',tags:['Regression','Model','R²'],gradient:'linear-gradient(135deg,#0c0818,#18102c,#141828)',accent:'#a855f7',stat1:'R²=0.56',stat1Label:'Model Fit',stat2:'22',stat2Label:'Features'},
]

const chapter3Items = [
  { category:'Dimension Reduction',icon:'🧬',title:'PCA — The 5 Dimensions',desc:'5 principal components capture 69.2% of variance. PC1 (21.5%): Size-Price axis. PC2 (15.6%): Age-Quality axis. PC3-PC5: Location & Amenity nuances.',tags:['PCA','Components','Variance'],gradient:'linear-gradient(135deg,#180818,#241028,#180c24)',accent:'#ec4899',stat1:'69.2%',stat1Label:'Cumulative',stat2:'5',stat2Label:'Components'},
  { category:'Dimension Reduction',icon:'📐',title:'Factor Loading Architecture',desc:'Varimax rotation extracts 5 latent factors: Size (area/rooms loading 0.89), Quality (decoration/age 0.76), Location (district 0.82), Age, Amenity.',tags:['Factor','Loading','Latent'],gradient:'linear-gradient(135deg,#100818,#1c1028,#181020)',accent:'#c084fc',stat1:'5',stat1Label:'Factors',stat2:'0.53',stat2Label:'KMO'},
  { category:'Dimension Reduction',icon:'✨',title:'Correlation Constellation Map',desc:'15 features mapped as a star network. Floor Area↔Total Price: r=0.85 (brightest bond). Building Age↔Unit Price: r=-0.42. Rooms↔Area: r=0.78.',tags:['Correlation','Network','Stars'],gradient:'linear-gradient(135deg,#080818,#101428,#0c1424)',accent:'#00d4ff',stat1:'r=0.85',stat1Label:'Strongest',stat2:'15',stat2Label:'Features'},
  { category:'Dimension Reduction',icon:'🌊',title:'Temporal Listing Flow',desc:'Daily listing activity visualized as waveform. ~20 new listings/day average. Price volatility correlates with listing volume — more listings = more price dispersion.',tags:['Temporal','Flow','Activity'],gradient:'linear-gradient(135deg,#08141c,#101c28,#141c28)',accent:'#06b6d4',stat1:'~20/day',stat1Label:'New',stat2:'315k',stat2Label:'Avg Price'},
]

const chapter4Items = [
  { category:'Market Segment',icon:'💡',title:'Segment 1: Compact Entry-Level',desc:'~70sqm, ~200k total. Young professionals, first-time buyers. Concentrated in Yuhang, Linping. Older buildings, simple decoration. Budget-conscious.',tags:['Entry','Compact','First-Time'],gradient:'linear-gradient(135deg,#0a1808,#142414,#101c10)',accent:'#22c55e',stat1:'~70sqm',stat1Label:'Avg Area',stat2:'~200k',stat2Label:'Avg Price'},
  { category:'Market Segment',icon:'💎',title:'Segment 5: Premium Large Units',desc:'~140sqm+, ~500k+. Luxury seekers, established families. Xihu, Shangcheng, Binjiang. Fine/Luxury decoration, newer buildings, near subway.',tags:['Luxury','Large','Premium'],gradient:'linear-gradient(135deg,#0c1808,#182414,#1c2014)',accent:'#84cc16',stat1:'~140sqm',stat1Label:'Avg Area',stat2:'~500k+',stat2Label:'Avg Price'},
  { category:'Market Segment',icon:'🎯',title:'LDA Classification Accuracy',desc:'Linear Discriminant Analysis achieves 64.6% accuracy distinguishing 5 segments. First 2 discriminant axes explain 85% of between-cluster variance.',tags:['LDA','Classification','Accuracy'],gradient:'linear-gradient(135deg,#180c08,#241810,#141828)',accent:'#f97316',stat1:'64.6%',stat1Label:'Accuracy',stat2:'85%',stat2Label:'Axis Variance'},
  { category:'Market Segment',icon:'🔮',title:'Investment Potential Index',desc:'Composite score: price momentum × transit access × district growth × building quality. Top quartile districts flagged for appreciation potential.',tags:['Investment','Composite','Scoring'],gradient:'linear-gradient(135deg,#0c1808,#182414,#1c2014)',accent:'#14b8a6',stat1:'A+',stat1Label:'Quality',stat2:'Top 25%',stat2Label:'Potential'},
]

function onGlobalMouse(e){mouseX.value=(e.clientX/window.innerWidth-0.5)*2;mouseY.value=(e.clientY/window.innerHeight-0.5)*2}
function onCardTilt(e,id){const card=e.currentTarget,rect=card.getBoundingClientRect(),x=(e.clientX-rect.left)/rect.width-0.5,y=(e.clientY-rect.top)/rect.height-0.5;cardTilts.value[id]=`perspective(1000px) rotateY(${x*10}deg) rotateX(${-y*8}deg) translateY(-6px) scale(1.025)`}
function resetCardTilt(id){cardTilts.value[id]='perspective(1000px) rotateY(0deg) rotateX(0deg) translateY(0px) scale(1)'}
function openStory(item){lightbox.value=item;document.body.style.overflow='hidden'}
function closeStory(){lightbox.value=null;document.body.style.overflow=''}

function initBgCanvas(){
  if(!bgCanvas.value)return
  const c=bgCanvas.value,ctx=c.getContext('2d')
  function resize(){c.width=window.innerWidth;c.height=document.querySelector('.story-page')?.scrollHeight||window.innerHeight}
  resize();window.addEventListener('resize',resize)
  const pts=[]
  for(let i=0;i<70;i++)pts.push({x:Math.random()*c.width,y:Math.random()*c.height,r:Math.random()*1.5+0.5,vx:(Math.random()-0.5)*0.3,vy:(Math.random()-0.5)*0.3,h:200+Math.random()*60,a:Math.random()*0.3+0.07})
  let t=0
  function anim(){t++;ctx.clearRect(0,0,c.width,c.height)
    pts.forEach((p,i)=>{p.x+=p.vx;p.y+=p.vy;if(p.x<0)p.x=c.width;if(p.x>c.width)p.x=0;if(p.y<0)p.y=c.height;if(p.y>c.height)p.y=0
      const alpha=Math.sin(t*0.015+i*0.3)*0.1+p.a;ctx.fillStyle=`hsla(${p.h},60%,65%,${alpha})`;ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,2*Math.PI);ctx.fill()
      for(let j=i+1;j<pts.length;j++){const dx=p.x-pts[j].x,dy=p.y-pts[j].y,d=Math.sqrt(dx*dx+dy*dy);if(d<140){ctx.strokeStyle=`hsla(${p.h},50%,55%,${0.02*(1-d/140)})`;ctx.lineWidth=0.2;ctx.beginPath();ctx.moveTo(p.x,p.y);ctx.lineTo(pts[j].x,pts[j].y);ctx.stroke()}}})
    animFrame=requestAnimationFrame(anim)}
  anim()
}

onMounted(()=>initBgCanvas())
onUnmounted(()=>{if(animFrame)cancelAnimationFrame(animFrame);document.body.style.overflow=''})
</script>

<style scoped>
.story-page{position:relative;min-height:100vh;overflow-x:hidden}

/* ==== BG ==== */
.bg-layers{position:fixed;inset:0;pointer-events:none;z-index:0}
.bg-canvas{position:absolute;inset:0;opacity:0.6}
.bg-orbs .orb{position:absolute;border-radius:50%;filter:blur(100px);opacity:0.1}
.o1{width:550px;height:550px;top:-150px;left:-100px;background:#409EFF;animation:o1 14s ease-in-out infinite}
.o2{width:450px;height:450px;top:50%;right:-150px;background:#a855f7;animation:o2 18s ease-in-out infinite}
.o3{width:350px;height:350px;bottom:-100px;left:40%;background:#00d4ff;animation:o3 16s ease-in-out infinite}
@keyframes o1{0%,100%{transform:translate(0,0)}33%{transform:translate(50px,30px)}66%{transform:translate(-25px,-20px)}}
@keyframes o2{0%,100%{transform:translate(0,0)}50%{transform:translate(-40px,-25px)}}
@keyframes o3{0%,100%{transform:translate(0,0)}33%{transform:translate(-30px,20px)}66%{transform:translate(20px,-15px)}}
.bg-grain{position:absolute;inset:0;opacity:0.025;background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.5'/%3E%3C/svg%3E");background-size:256px}

/* ==== PARALLAX ==== */
.parallax-shapes{position:fixed;inset:0;pointer-events:none;z-index:0}
.pshape{position:absolute;border-radius:50%;filter:blur(50px);opacity:0.05;transition:transform 0.6s cubic-bezier(0.25,0.46,0.45,0.94)}
.ps1{width:180px;height:180px;top:20%;left:65%;background:#409EFF}
.ps2{width:160px;height:160px;top:60%;left:70%;background:#a855f7}
.ps3{width:140px;height:140px;top:30%;left:25%;background:#00d4ff}

/* ==== CHAPTER 0: HERO ==== */
.story-hero{position:relative;z-index:2;text-align:center;padding:80px 20px 50px;min-height:60vh;display:flex;flex-direction:column;align-items:center;justify-content:center}
.hero-chapter-tag{font-size:11px;text-transform:uppercase;letter-spacing:4px;color:var(--text-muted);margin-bottom:20px;padding:6px 20px;border-radius:50px;border:1px solid rgba(255,255,255,0.06);background:rgba(26,31,46,0.4);backdrop-filter:blur(8px)}
.hero-title{font-size:64px;font-weight:900;letter-spacing:-3px;line-height:1.05;margin-bottom:20px}
.ht-line1{display:block;color:var(--text-secondary);font-size:28px;font-weight:400;letter-spacing:2px;margin-bottom:4px;text-transform:uppercase}
.ht-line2{display:block;background:linear-gradient(135deg,#409EFF 0%,#00d4ff 30%,#a855f7 60%,#ec4899 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.hero-desc{max-width:700px;color:var(--text-secondary);font-size:16px;line-height:1.9}
.hero-scroll-hint{margin-top:40px;display:flex;flex-direction:column;align-items:center;gap:8px;color:var(--text-muted);font-size:12px;text-transform:uppercase;letter-spacing:2px;opacity:0.6}
.scroll-arrow{font-size:20px;animation:scroll-bounce 2s ease-in-out infinite}
@keyframes scroll-bounce{0%,100%{transform:translateY(0)}50%{transform:translateY(8px)}}

/* ==== CHAPTERS ==== */
.story-chapter{position:relative;z-index:2;padding:60px 24px;max-width:1400px;margin:0 auto}
.chapter-marker{display:flex;align-items:center;justify-content:center;gap:20px;margin-bottom:16px}
.chapter-line{width:50px;height:1px;background:rgba(255,255,255,0.1)}
.chapter-num{font-size:13px;font-weight:700;color:var(--accent-cyan);letter-spacing:3px;font-family:'SF Mono','Cascadia Code',monospace}
.chapter-header{text-align:center;margin-bottom:36px}
.chapter-header h2{font-size:36px;font-weight:800;color:#fff;letter-spacing:-1px;margin-bottom:6px}
.chapter-header p{color:var(--text-muted);font-size:15px}

/* ==== STORY CARDS ==== */
.story-cards{display:grid;grid-template-columns:repeat(4,1fr);gap:18px;margin-bottom:32px}
@media(max-width:1100px){.story-cards{grid-template-columns:repeat(2,1fr)}}
@media(max-width:600px){.story-cards{grid-template-columns:1fr}}
.s-card{background:rgba(20,25,35,0.6);border:1px solid rgba(255,255,255,0.04);border-radius:18px;overflow:hidden;cursor:pointer;transition:all 0.45s cubic-bezier(0.23,1,0.32,1);will-change:transform;backface-visibility:hidden}
.s-card:hover{z-index:5;border-color:rgba(255,255,255,0.1);box-shadow:0 20px 60px rgba(0,0,0,0.5)}
.sc-art{position:relative;height:160px;display:flex;align-items:center;justify-content:center;overflow:hidden}
.sc-art-icon{font-size:44px;position:relative;z-index:2;transition:transform 0.5s cubic-bezier(0.34,1.56,0.64,1)}
.s-card:hover .sc-art-icon{transform:scale(1.15) rotate(-3deg)}
.sc-art-glow{position:absolute;inset:0;opacity:0.5;transition:opacity 0.5s}
.s-card:hover .sc-art-glow{opacity:1}
.sc-info{padding:18px 20px 22px}
.sc-accent{font-size:10px;text-transform:uppercase;letter-spacing:2px;font-weight:700}
.sc-info h3{font-size:15px;font-weight:700;color:#fff;margin:6px 0;line-height:1.25}
.sc-info p{font-size:12px;color:var(--text-secondary);line-height:1.6;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}

/* ==== INSIGHT ==== */
.chapter-insight{display:flex;gap:16px;padding:22px 28px;border-radius:16px;background:rgba(64,158,255,0.04);border:1px solid rgba(64,158,255,0.1);align-items:flex-start}
.insight-icon{font-size:26px;flex-shrink:0;margin-top:2px}
.chapter-insight p{color:var(--text-secondary);font-size:14px;line-height:1.8}

/* ==== EPILOGUE ==== */
.story-epilogue{position:relative;z-index:2;text-align:center;padding:80px 24px 60px;max-width:700px;margin:0 auto}
.epilogue-icon{font-size:28px;color:rgba(255,255,255,0.15);margin-bottom:16px}
.story-epilogue h2{font-size:34px;font-weight:800;color:#fff;margin-bottom:16px;letter-spacing:-1px}
.story-epilogue p{color:var(--text-secondary);font-size:15px;line-height:1.9;margin-bottom:12px}
.epilogue-credit{font-size:12px!important;color:var(--text-muted)!important;margin-top:20px!important}
.epilogue-stats{display:flex;justify-content:center;gap:36px;margin-top:32px;flex-wrap:wrap}
.ep-stat strong{display:block;font-size:26px;color:#fff;font-weight:800}
.ep-stat span{font-size:11px;color:var(--text-muted);text-transform:uppercase;letter-spacing:1px}

/* ==== LIGHTBOX ==== */
.lb-backdrop{position:fixed;inset:0;z-index:10000;background:rgba(0,0,0,0.88);backdrop-filter:blur(30px);display:flex;align-items:center;justify-content:center;padding:40px}
.lb-container{position:relative;display:flex;max-width:850px;width:100%;max-height:85vh;background:rgba(18,22,33,0.98);border-radius:24px;overflow:hidden;border:1px solid rgba(255,255,255,0.06);box-shadow:0 40px 120px rgba(0,0,0,0.7)}
.lb-close-btn{position:absolute;top:16px;right:16px;width:40px;height:40px;border-radius:50%;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.08);cursor:pointer;z-index:10;transition:all 0.35s;display:flex;align-items:center;justify-content:center}
.lb-close-btn:hover{background:rgba(255,255,255,0.14);transform:rotate(90deg)}
.close-icon{position:relative;width:16px;height:16px}
.close-icon::before,.close-icon::after{content:'';position:absolute;top:50%;left:0;width:100%;height:2px;background:#fff;border-radius:1px}
.close-icon::before{transform:rotate(45deg)}.close-icon::after{transform:rotate(-45deg)}
.lb-hero-art{position:relative;width:45%;min-height:350px;display:flex;align-items:center;justify-content:center;overflow:hidden;flex-shrink:0}
.lb-art-icon{font-size:80px;position:relative;z-index:2;filter:drop-shadow(0 10px 30px rgba(0,0,0,0.5));animation:lb-float 4s ease-in-out infinite}
@keyframes lb-float{0%,100%{transform:translateY(0)}50%{transform:translateY(-10px)}}
.lb-body{flex:1;padding:36px;display:flex;flex-direction:column;justify-content:center;overflow-y:auto}
.lb-cat{font-size:10px;text-transform:uppercase;letter-spacing:3px;font-weight:700;margin-bottom:8px;display:block}
.lb-body h2{font-size:24px;color:#fff;line-height:1.25;margin-bottom:12px}
.lb-desc{color:var(--text-secondary);line-height:1.8;font-size:14px;margin-bottom:16px}
.lb-tags{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:22px}
.lb-tags span{padding:5px 14px;border-radius:16px;background:rgba(255,255,255,0.04);font-size:11px;color:var(--text-muted)}
.lb-stats-row{display:flex;gap:16px}
.lb-stat-card{padding:14px 22px;border-radius:12px;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.04);text-align:center}
.lb-stat-val{font-size:24px;font-weight:800}
.lb-stat-lbl{font-size:10px;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.5px;margin-top:2px}

.lb-smooth-enter-active{transition:all 0.4s cubic-bezier(0.34,1.56,0.64,1)}
.lb-smooth-leave-active{transition:all 0.2s ease-in}
.lb-smooth-enter-from{opacity:0}.lb-smooth-enter-from .lb-container{transform:scale(0.92) translateY(20px)}
.lb-smooth-leave-to{opacity:0}.lb-smooth-leave-to .lb-container{transform:scale(0.95)}

@media(max-width:768px){.hero-title{font-size:38px}.story-cards{grid-template-columns:1fr}.lb-container{flex-direction:column}.lb-hero-art{width:100%;min-height:180px}}
</style>
