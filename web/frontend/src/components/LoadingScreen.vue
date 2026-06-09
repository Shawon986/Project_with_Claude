<template>
  <Transition name="loader-exit">
    <div v-if="visible" class="loader-root" ref="root">
      <canvas ref="canvas" class="loader-canvas"></canvas>

      <!-- 3D Scene Container -->
      <div class="scene-3d" :class="{ 'scene-hide': exiting }">
        <!-- Perspective stage -->
        <div class="stage">

          <!-- === 3D ROTATING CUBE === -->
          <div class="cube-wrapper">
            <div class="cube" ref="cube">
              <!-- Front face -->
              <div class="cube-face cube-front">
                <div class="face-content">
                  <svg viewBox="0 0 40 40" class="face-icon">
                    <rect x="4" y="16" width="14" height="20" rx="1.5" fill="none" stroke="rgba(64,158,255,0.9)" stroke-width="2"/>
                    <rect x="22" y="10" width="14" height="26" rx="1.5" fill="none" stroke="rgba(64,158,255,0.9)" stroke-width="2"/>
                    <path d="M0 18 L20 0 L40 18" fill="none" stroke="rgba(64,158,255,0.7)" stroke-width="1.5"/>
                  </svg>
                </div>
              </div>
              <!-- Back face -->
              <div class="cube-face cube-back">
                <div class="face-content">
                  <div class="face-chart">
                    <span v-for="n in 5" :key="n" class="face-bar" :style="{ height: (14 + n * 10) + 'px', animationDelay: (n * 0.12) + 's' }"></span>
                  </div>
                </div>
              </div>
              <!-- Right face -->
              <div class="cube-face cube-right">
                <div class="face-content">
                  <div class="face-grid">
                    <span v-for="n in 9" :key="n" class="face-dot" :style="{ animationDelay: (n * 0.1) + 's' }"></span>
                  </div>
                </div>
              </div>
              <!-- Left face -->
              <div class="cube-face cube-left">
                <div class="face-content">
                  <svg viewBox="0 0 40 40" class="face-icon">
                    <circle cx="20" cy="20" r="16" fill="none" stroke="rgba(168,85,247,0.7)" stroke-width="1.5"/>
                    <circle cx="20" cy="20" r="8" fill="none" stroke="rgba(168,85,247,0.5)" stroke-width="1"/>
                    <line x1="20" y1="4" x2="20" y2="36" stroke="rgba(168,85,247,0.3)" stroke-width="0.5"/>
                    <line x1="4" y1="20" x2="36" y2="20" stroke="rgba(168,85,247,0.3)" stroke-width="0.5"/>
                  </svg>
                </div>
              </div>
              <!-- Top face -->
              <div class="cube-face cube-top">
                <div class="face-content">
                  <div class="face-glow"></div>
                </div>
              </div>
              <!-- Bottom face -->
              <div class="cube-face cube-bottom">
                <div class="face-content">
                  <div class="face-glow-bottom"></div>
                </div>
              </div>
            </div>
          </div>

          <!-- === FLOATING DATA RINGS (3D tilted) === -->
          <div class="data-ring ring-a">
            <svg viewBox="0 0 300 300">
              <ellipse cx="150" cy="150" rx="145" ry="145" fill="none" stroke="rgba(64,158,255,0.12)" stroke-width="0.8" stroke-dasharray="2 10"/>
            </svg>
            <div class="ring-dot rd-1"></div>
            <div class="ring-dot rd-2"></div>
            <div class="ring-dot rd-3"></div>
          </div>
          <div class="data-ring ring-b">
            <svg viewBox="0 0 300 300">
              <ellipse cx="150" cy="150" rx="110" ry="110" fill="none" stroke="rgba(0,212,255,0.1)" stroke-width="0.6" stroke-dasharray="6 14"/>
            </svg>
            <div class="ring-dot rd-4"></div>
            <div class="ring-dot rd-5"></div>
          </div>

          <!-- === FLOATING STAT CARDS (3D tilted) === -->
          <div class="float-card-3d fcard-1">
            <div class="fcard-inner">
              <span class="fcard-val">3,455</span>
              <span class="fcard-lbl">Listings</span>
            </div>
          </div>
          <div class="float-card-3d fcard-2">
            <div class="fcard-inner">
              <span class="fcard-val">12</span>
              <span class="fcard-lbl">Districts</span>
            </div>
          </div>
          <div class="float-card-3d fcard-3">
            <div class="fcard-inner">
              <span class="fcard-val">¥31.5k</span>
              <span class="fcard-lbl">Avg /sqm</span>
            </div>
          </div>

          <!-- === CENTER GLOW PLATFORM === -->
          <div class="platform">
            <div class="platform-glow"></div>
            <div class="platform-grid"></div>
            <div class="platform-ring p-ring-1"></div>
            <div class="platform-ring p-ring-2"></div>
            <div class="platform-ring p-ring-3"></div>
          </div>

        </div>

        <!-- === BRAND TEXT === -->
        <div class="brand-3d">
          <h1 class="brand-title-3d">
            <span class="bt-word bt-hz">Hangzhou</span>
            <span class="bt-word bt-ha">Housing Intelligence</span>
          </h1>
          <div class="brand-line"></div>
        </div>

        <!-- === PROGRESS BAR === -->
        <div class="prog-3d">
          <div class="prog-track">
            <div class="prog-fill" :style="{ width: progress + '%' }">
              <div class="prog-beam"></div>
            </div>
            <div class="prog-glint"></div>
          </div>
          <div class="prog-meta">
            <span class="pm-pct">{{ Math.round(progress) }}%</span>
            <span class="pm-msg">{{ statusMsg }}</span>
          </div>
        </div>
      </div>

      <!-- Corner HUD elements -->
      <div class="hud-corner hud-tl"><span>HANGZHOU · 30.25°N 120.16°E</span></div>
      <div class="hud-corner hud-tr"><span>SYS v2.0 · INIT</span></div>
      <div class="hud-corner hud-bl"><span>3,455 RECORDS · 12 DISTRICTS</span></div>
      <div class="hud-corner hud-br"><span>{{ Math.round(progress) }}% LOADED</span></div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'

const props = defineProps({ duration: { type: Number, default: 2600 } })

const visible = ref(true)
const exiting = ref(false)
const progress = ref(0)
const statusMsg = ref('Booting kernel')
const canvas = ref(null)
const cube = ref(null)

let animId = null

const messages = [
  { at: 0,  msg: 'Booting kernel' },
  { at: 12, msg: 'Loading market corpus' },
  { at: 28, msg: 'Computing regressions' },
  { at: 42, msg: 'Training ML models' },
  { at: 56, msg: 'Rendering geospatial' },
  { at: 70, msg: 'Calibrating clusters' },
  { at: 84, msg: 'Finalizing dashboard' },
  { at: 96, msg: 'Launch sequence complete' },
]

// === 3D CANVAS PARTICLE FIELD ===
function initCanvas() {
  if (!canvas.value) return
  const c = canvas.value
  const ctx = c.getContext('2d')

  function resize() {
    c.width = window.innerWidth
    c.height = window.innerHeight
  }
  resize()
  window.addEventListener('resize', resize)

  const W = () => c.width
  const H = () => c.height
  const midX = () => W() / 2
  const midY = () => H() / 2

  // Depth-layered particles (z-index illusion via size/speed/opacity)
  const layers = [
    { count: 50, z: 0.3, minR: 0.4, maxR: 1.2, speed: 0.2, alpha: 0.25, hue: 210 },
    { count: 35, z: 0.6, minR: 1.0, maxR: 2.2, speed: 0.45, alpha: 0.4, hue: 195 },
    { count: 20, z: 1.0, minR: 1.8, maxR: 3.5, speed: 0.8, alpha: 0.55, hue: 270 },
  ]

  const allParticles = layers.map(l =>
    Array.from({ length: l.count }, () => ({
      ...l,
      x: Math.random() * W(),
      y: Math.random() * H(),
      r: l.minR + Math.random() * (l.maxR - l.minR),
      vx: (Math.random() - 0.5) * l.speed,
      vy: (Math.random() - 0.5) * l.speed,
      phase: Math.random() * Math.PI * 2,
      freq: 0.008 + Math.random() * 0.02,
      alphaBase: Math.random() * l.alpha * 0.5 + l.alpha * 0.5,
    }))
  ).flat()

  // Energy beams (vertical light streaks)
  const beams = Array.from({ length: 12 }, () => ({
    x: Math.random() * W(),
    y: Math.random() * H(),
    height: 40 + Math.random() * 120,
    width: 0.5 + Math.random() * 1.5,
    alpha: 0.02 + Math.random() * 0.08,
    speed: 0.3 + Math.random() * 1.2,
    hue: [210, 195, 270, 170][Math.floor(Math.random() * 4)],
    phase: Math.random() * Math.PI * 2,
  }))

  let tick = 0
  function draw() {
    tick++
    ctx.clearRect(0, 0, W(), H())

    // Deep background - dark radial
    const bg = ctx.createRadialGradient(midX(), midY(), 0, midX(), midY(), Math.max(W(), H()) * 0.75)
    bg.addColorStop(0, 'rgba(8,12,20,0)')
    bg.addColorStop(0.5, 'rgba(8,12,20,0.7)')
    bg.addColorStop(1, 'rgba(8,12,20,0.98)')
    ctx.fillStyle = bg
    ctx.fillRect(0, 0, W(), H())

    // Depth-sorted particles (far to near)
    const sorted = [...allParticles].sort((a, b) => a.z - b.z)
    sorted.forEach(p => {
      p.x += p.vx
      p.y += p.vy
      p.phase += p.freq
      if (p.x < -30) p.x = W() + 30
      if (p.x > W() + 30) p.x = -30
      if (p.y < -30) p.y = H() + 30
      if (p.y > H() + 30) p.y = -30

      // Parallax: closer layers (higher z) move more
      const parallaxX = (p.x - midX()) * (1 + p.z * 0.5) + midX()
      const parallaxY = (p.y - midY()) * (1 + p.z * 0.5) + midY()

      const alpha = Math.sin(p.phase) * p.alphaBase * 0.4 + p.alphaBase
      ctx.fillStyle = `hsla(${p.hue}, 65%, ${50 + p.z * 20}%, ${alpha})`
      ctx.beginPath()
      ctx.arc(parallaxX, parallaxY, p.r, 0, Math.PI * 2)
      ctx.fill()

      // Glow for near particles
      if (p.z > 0.5) {
        const glow = ctx.createRadialGradient(parallaxX, parallaxY, 0, parallaxX, parallaxY, p.r * 3)
        glow.addColorStop(0, `hsla(${p.hue}, 70%, 70%, ${alpha * 0.5})`)
        glow.addColorStop(1, 'transparent')
        ctx.fillStyle = glow
        ctx.beginPath()
        ctx.arc(parallaxX, parallaxY, p.r * 3, 0, Math.PI * 2)
        ctx.fill()
      }
    })

    // Energy beams
    beams.forEach(b => {
      b.y -= b.speed
      b.phase += 0.02
      if (b.y + b.height < 0) { b.y = H() + 20; b.x = Math.random() * W() }
      const alpha = b.alpha * (0.6 + Math.sin(b.phase) * 0.4)
      const grad = ctx.createLinearGradient(b.x, b.y, b.x, b.y + b.height)
      grad.addColorStop(0, `hsla(${b.hue}, 70%, 70%, ${alpha})`)
      grad.addColorStop(0.5, `hsla(${b.hue}, 60%, 60%, ${alpha * 0.6})`)
      grad.addColorStop(1, 'transparent')
      ctx.fillStyle = grad
      ctx.fillRect(b.x - b.width / 2, b.y, b.width, b.height)
    })

    // Central vortex - subtle rotating lines
    ctx.save()
    ctx.translate(midX(), midY())
    for (let i = 0; i < 6; i++) {
      const angle = (tick * 0.003) + (i * Math.PI / 3)
      const radius = 80 + Math.sin(tick * 0.02 + i) * 20
      ctx.strokeStyle = `rgba(64,158,255,${0.03 + Math.sin(tick * 0.015 + i) * 0.015})`
      ctx.lineWidth = 0.5
      ctx.beginPath()
      ctx.arc(0, 0, radius, angle, angle + Math.PI * 0.4)
      ctx.stroke()
    }
    ctx.restore()

    // Scan line effect
    const scanY = ((tick * 0.8) % H())
    const scanGrad = ctx.createLinearGradient(0, scanY - 30, 0, scanY + 30)
    scanGrad.addColorStop(0, 'transparent')
    scanGrad.addColorStop(0.5, 'rgba(64,158,255,0.03)')
    scanGrad.addColorStop(1, 'transparent')
    ctx.fillStyle = scanGrad
    ctx.fillRect(0, 0, W(), H())

    // Micro grid overlay
    ctx.strokeStyle = 'rgba(255,255,255,0.015)'
    ctx.lineWidth = 0.3
    const spacing = 70
    for (let x = spacing; x < W(); x += spacing) {
      ctx.beginPath()
      ctx.moveTo(x, 0)
      ctx.lineTo(x, H())
      ctx.stroke()
    }
    for (let y = spacing; y < H(); y += spacing) {
      ctx.beginPath()
      ctx.moveTo(0, y)
      ctx.lineTo(W(), y)
      ctx.stroke()
    }

    animId = requestAnimationFrame(draw)
  }
  draw()
}

// === Progress ===
function runProgress() {
  const start = performance.now()
  function tick() {
    const elapsed = performance.now() - start
    const raw = (elapsed / props.duration) * 100
    const eased = raw < 88
      ? raw * (1 - Math.pow(1 - Math.min(raw / 88, 1), 3))
      : 88 + (raw - 88) * 0.25
    progress.value = Math.min(99.5, eased)
    for (let i = messages.length - 1; i >= 0; i--) {
      if (progress.value >= messages[i].at) { statusMsg.value = messages[i].msg; break }
    }
    if (elapsed < props.duration) requestAnimationFrame(tick)
    else finish()
  }
  requestAnimationFrame(tick)
}

function finish() {
  progress.value = 100
  statusMsg.value = 'Launch sequence complete'
  setTimeout(() => { exiting.value = true }, 300)
  setTimeout(() => { visible.value = false }, 900)
}

onMounted(async () => {
  await nextTick()
  initCanvas()
  setTimeout(runProgress, 200)
})

onUnmounted(() => { if (animId) cancelAnimationFrame(animId) })
</script>

<style scoped>
/* ============================================
   ROOT
   ============================================ */
.loader-root {
  position: fixed;
  inset: 0;
  z-index: 99999;
  background: #080c14;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  font-family: 'PingFang SC', 'Microsoft YaHei', 'Inter', sans-serif;
  perspective: 1200px;
}

.loader-canvas {
  position: absolute;
  inset: 0;
  z-index: 1;
}

/* ============================================
   3D SCENE
   ============================================ */
.scene-3d {
  position: relative;
  z-index: 10;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 32px;
  transition: opacity 0.55s ease, transform 0.55s cubic-bezier(0.4,0,0.2,1);
}
.scene-hide {
  opacity: 0;
  transform: translateY(-24px) scale(0.96);
}

.stage {
  position: relative;
  width: 380px;
  height: 380px;
  transform-style: preserve-3d;
  animation: stage-float 5s ease-in-out infinite;
}
@keyframes stage-float {
  0%, 100% { transform: translateY(0) rotateX(0deg); }
  50% { transform: translateY(-8px) rotateX(2deg); }
}

/* ============================================
   3D CUBE
   ============================================ */
.cube-wrapper {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 130px;
  height: 130px;
  transform-style: preserve-3d;
  transform: translate(-50%, -50%);
  z-index: 5;
}

.cube {
  width: 100%;
  height: 100%;
  position: relative;
  transform-style: preserve-3d;
  animation: cube-rotate 14s linear infinite;
}

@keyframes cube-rotate {
  0%   { transform: rotateX(-20deg) rotateY(0deg); }
  25%  { transform: rotateX(-20deg) rotateY(90deg); }
  50%  { transform: rotateX(-20deg) rotateY(180deg); }
  75%  { transform: rotateX(-20deg) rotateY(270deg); }
  100% { transform: rotateX(-20deg) rotateY(360deg); }
}

.cube-face {
  position: absolute;
  width: 130px;
  height: 130px;
  backface-visibility: hidden;
  border: 1.2px solid rgba(64,158,255,0.15);
  background: rgba(12,18,30,0.85);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 30px rgba(64,158,255,0.08) inset;
}

.cube-front  { transform: translateZ(65px); }
.cube-back   { transform: rotateY(180deg) translateZ(65px); }
.cube-right  { transform: rotateY(90deg) translateZ(65px); }
.cube-left   { transform: rotateY(-90deg) translateZ(65px); }
.cube-top    { transform: rotateX(90deg) translateZ(65px); }
.cube-bottom { transform: rotateX(-90deg) translateZ(65px); }

.face-content {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.face-icon {
  width: 50px;
  height: 50px;
  filter: drop-shadow(0 0 8px rgba(64,158,255,0.4));
}
.face-chart {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  height: 50px;
}
.face-bar {
  width: 5px;
  border-radius: 2px;
  background: linear-gradient(to top, #409EFF, #00d4ff);
  animation: bar-bounce 1s ease-in-out infinite alternate;
  box-shadow: 0 0 6px rgba(0,212,255,0.5);
}
@keyframes bar-bounce {
  0% { transform: scaleY(0.6); opacity: 0.7; }
  100% { transform: scaleY(1); opacity: 1; }
}

.face-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}
.face-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #a855f7;
  animation: dot-pulse 1.5s ease-in-out infinite alternate;
  box-shadow: 0 0 6px rgba(168,85,247,0.6);
}
@keyframes dot-pulse {
  0% { opacity: 0.3; transform: scale(0.7); }
  100% { opacity: 1; transform: scale(1.2); }
}

.face-glow {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(64,158,255,0.5), transparent 70%);
  animation: face-glow-pulse 2s ease-in-out infinite;
}
.face-glow-bottom {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(0,212,255,0.3), transparent 70%);
  animation: face-glow-pulse 2s ease-in-out 0.6s infinite;
}
@keyframes face-glow-pulse {
  0%, 100% { opacity: 0.4; transform: scale(0.9); }
  50% { opacity: 0.9; transform: scale(1.15); }
}

/* ============================================
   DATA RINGS (3D TILTED)
   ============================================ */
.data-ring {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 350px;
  height: 350px;
  transform-style: preserve-3d;
  pointer-events: none;
  z-index: 3;
}
.data-ring svg {
  width: 100%;
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
}
.ring-a {
  transform: translate(-50%, -50%) rotateX(70deg) rotateZ(0deg);
  animation: ring-spin-a 20s linear infinite;
}
.ring-b {
  transform: translate(-50%, -50%) rotateX(70deg) rotateZ(45deg);
  animation: ring-spin-b 25s linear infinite;
}
@keyframes ring-spin-a {
  to { transform: translate(-50%, -50%) rotateX(70deg) rotateZ(360deg); }
}
@keyframes ring-spin-b {
  to { transform: translate(-50%, -50%) rotateX(70deg) rotateZ(405deg); }
}

.ring-dot {
  position: absolute;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  pointer-events: none;
}
.rd-1 { top: 8px; left: 50%; background: #409EFF; box-shadow: 0 0 10px #409EFF, 0 0 20px #409EFF; }
.rd-2 { top: 70%; left: 5%; background: #00d4ff; box-shadow: 0 0 10px #00d4ff; }
.rd-3 { top: 70%; right: 5%; background: #a855f7; box-shadow: 0 0 10px #a855f7; }
.rd-4 { top: 20%; left: 15%; background: #22c55e; box-shadow: 0 0 8px #22c55e; }
.rd-5 { top: 60%; right: 10%; background: #f59e0b; box-shadow: 0 0 8px #f59e0b; }

/* ============================================
   FLOATING STAT CARDS (3D)
   ============================================ */
.float-card-3d {
  position: absolute;
  z-index: 4;
  pointer-events: none;
  animation: fcard-float 4s ease-in-out infinite;
}
.fcard-inner {
  padding: 10px 18px;
  border-radius: 12px;
  background: rgba(16, 22, 36, 0.85);
  border: 1px solid rgba(64,158,255,0.15);
  backdrop-filter: blur(12px);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.5), 0 0 20px rgba(64,158,255,0.08);
  transform: rotateY(-15deg) rotateX(5deg);
}
.fcard-val {
  font-size: 18px;
  font-weight: 800;
  color: #409EFF;
  letter-spacing: -0.5px;
  text-shadow: 0 0 10px rgba(64,158,255,0.5);
}
.fcard-lbl {
  font-size: 9px;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 2px;
}

.fcard-1 { top: 5%; left: 0%; animation-delay: 0s; }
.fcard-2 { top: 15%; right: -5%; animation-delay: 0.8s; }
.fcard-3 { bottom: 10%; left: 10%; animation-delay: 1.6s; }

@keyframes fcard-float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

/* ============================================
   PLATFORM (floor reflection)
   ============================================ */
.platform {
  position: absolute;
  bottom: 20%;
  left: 50%;
  transform: translateX(-50%) rotateX(60deg);
  width: 260px;
  height: 260px;
  z-index: 1;
  pointer-events: none;
}
.platform-glow {
  position: absolute;
  inset: -20px;
  border-radius: 50%;
  background: radial-gradient(ellipse at center, rgba(64,158,255,0.06), transparent 70%);
  animation: plat-glow 3s ease-in-out infinite;
}
@keyframes plat-glow {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}
.platform-grid {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background:
    repeating-linear-gradient(0deg, transparent, transparent 24px, rgba(64,158,255,0.03) 24px, rgba(64,158,255,0.03) 25px),
    repeating-linear-gradient(90deg, transparent, transparent 24px, rgba(64,158,255,0.03) 24px, rgba(64,158,255,0.03) 25px);
  mask-image: radial-gradient(ellipse at center, black 30%, transparent 70%);
  -webkit-mask-image: radial-gradient(ellipse at center, black 30%, transparent 70%);
}
.platform-ring {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  border-radius: 50%;
  border: 1px solid rgba(64,158,255,0.06);
}
.p-ring-1 { width: 200px; height: 200px; }
.p-ring-2 { width: 140px; height: 140px; animation: p-ring-pulse 4s ease-in-out infinite; }
.p-ring-3 { width: 80px; height: 80px; animation: p-ring-pulse 4s ease-in-out 1s infinite; }

@keyframes p-ring-pulse {
  0%, 100% { border-color: rgba(64,158,255,0.04); transform: translate(-50%, -50%) scale(1); }
  50% { border-color: rgba(64,158,255,0.12); transform: translate(-50%, -50%) scale(1.08); }
}

/* ============================================
   BRAND TEXT
   ============================================ */
.brand-3d {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  z-index: 2;
}
.brand-title-3d {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}
.bt-word {
  display: block;
}
.bt-hz {
  font-size: 38px;
  font-weight: 900;
  color: #fff;
  letter-spacing: -1.5px;
  text-shadow: 0 0 40px rgba(64,158,255,0.3), 0 2px 4px rgba(0,0,0,0.5);
}
.bt-ha {
  font-size: 12px;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 6px;
}
.brand-line {
  width: 60px;
  height: 2px;
  border-radius: 1px;
  background: linear-gradient(90deg, transparent, #409EFF, #00d4ff, #a855f7, transparent);
  animation: brand-line-shift 2s ease-in-out infinite;
}
@keyframes brand-line-shift {
  0%, 100% { background-position: -100% 0; opacity: 0.6; }
  50% { background-position: 100% 0; opacity: 1; }
}

/* ============================================
   PROGRESS BAR
   ============================================ */
.prog-3d {
  width: 340px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  z-index: 2;
}
.prog-track {
  height: 5px;
  border-radius: 3px;
  overflow: hidden;
  background: rgba(255,255,255,0.03);
  position: relative;
  box-shadow: 0 0 10px rgba(0,0,0,0.4) inset;
}
.prog-fill {
  height: 100%;
  border-radius: 3px;
  background: linear-gradient(90deg, #1d4ed8, #409EFF, #00d4ff, #a855f7, #c084fc);
  background-size: 300% 100%;
  animation: prog-rainbow 3s linear infinite;
  transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}
@keyframes prog-rainbow {
  to { background-position: 300% 0; }
}
.prog-beam {
  position: absolute;
  right: -3px;
  top: -4px;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #fff;
  box-shadow: 0 0 16px #00d4ff, 0 0 32px #409EFF, 0 0 48px rgba(64,158,255,0.4);
}
.prog-glint {
  position: absolute;
  top: 0;
  left: -80%;
  width: 60%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.12), transparent);
  animation: glint-sweep 2.5s ease-in-out infinite;
}
@keyframes glint-sweep {
  0% { left: -80%; }
  100% { left: 120%; }
}
.prog-meta {
  display: flex;
  justify-content: space-between;
  padding: 0 2px;
}
.pm-pct {
  font-size: 13px;
  font-weight: 700;
  color: #409EFF;
  font-variant-numeric: tabular-nums;
  text-shadow: 0 0 8px rgba(64,158,255,0.5);
}
.pm-msg {
  font-size: 11px;
  color: #6b7280;
  font-weight: 500;
  letter-spacing: 0.5px;
}

/* ============================================
   HUD CORNERS
   ============================================ */
.hud-corner {
  position: absolute;
  z-index: 8;
  pointer-events: none;
  font-family: 'SF Mono', 'Cascadia Code', 'Consolas', monospace;
  font-size: 10px;
  color: rgba(255,255,255,0.15);
  letter-spacing: 1.5px;
  font-weight: 500;
}
.hud-tl { top: 22px; left: 26px; }
.hud-tr { top: 22px; right: 26px; }
.hud-bl { bottom: 22px; left: 26px; }
.hud-br { bottom: 22px; right: 26px; }

/* ============================================
   EXIT
   ============================================ */
.loader-exit-leave-active {
  transition: opacity 0.7s ease, filter 0.7s ease;
}
.loader-exit-leave-to {
  opacity: 0;
  filter: blur(6px);
}

/* ============================================
   MOBILE
   ============================================ */
@media (max-width: 768px) {
  .stage { width: 280px; height: 280px; }
  .cube-wrapper { width: 100px; height: 100px; }
  .cube-face { width: 100px; height: 100px; }
  .cube-front { transform: translateZ(50px); }
  .cube-back { transform: rotateY(180deg) translateZ(50px); }
  .cube-right { transform: rotateY(90deg) translateZ(50px); }
  .cube-left { transform: rotateY(-90deg) translateZ(50px); }
  .cube-top { transform: rotateX(90deg) translateZ(50px); }
  .cube-bottom { transform: rotateX(-90deg) translateZ(50px); }
  .face-icon { width: 38px; height: 38px; }
  .data-ring { width: 260px; height: 260px; }
  .bt-hz { font-size: 28px; }
  .bt-ha { font-size: 10px; letter-spacing: 5px; }
  .prog-3d { width: 260px; }
  .fcard-val { font-size: 15px; }
  .fcard-lbl { font-size: 8px; }
  .hud-corner { font-size: 8px; }
  .hud-tl, .hud-tr { top: 14px; }
  .hud-bl, .hud-br { bottom: 14px; }
  .hud-tl, .hud-bl { left: 14px; }
  .hud-tr, .hud-br { right: 14px; }
  .platform { width: 180px; height: 180px; }
}
@media (max-width: 380px) {
  .stage { width: 220px; height: 220px; }
  .cube-wrapper { width: 80px; height: 80px; }
  .cube-face { width: 80px; height: 80px; }
  .cube-front { transform: translateZ(40px); }
  .cube-back { transform: rotateY(180deg) translateZ(40px); }
  .cube-right { transform: rotateY(90deg) translateZ(40px); }
  .cube-left { transform: rotateY(-90deg) translateZ(40px); }
  .cube-top { transform: rotateX(90deg) translateZ(40px); }
  .cube-bottom { transform: rotateX(-90deg) translateZ(40px); }
  .bt-hz { font-size: 22px; }
  .prog-3d { width: 200px; }
  .data-ring { width: 200px; height: 200px; }
}
</style>
