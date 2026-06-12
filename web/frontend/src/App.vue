<template>
  <LoadingScreen />
  <div class="app-container dark-theme" :class="{ 'mobile-sidebar-open': mobileMenuOpen }">
    <!-- Mobile overlay -->
    <div class="mobile-overlay" v-if="mobileMenuOpen" @click="mobileMenuOpen=false" @touchmove.prevent></div>
    <!-- Mobile hamburger -->
    <div class="mobile-hamburger" @click="mobileMenuOpen=!mobileMenuOpen">
      <span></span><span></span><span></span>
    </div>

    <el-container>
      <!-- Animated Sidebar -->
      <el-aside :width="isMobile ? '0px' : (isCollapsed ? '70px' : '240px')" class="sidebar-glass" :class="{ 'mobile-visible': mobileMenuOpen }">
        <div class="logo-section" @click="isCollapsed = !isCollapsed">
          <!-- Logo: 3D Data Tower -->
          <div class="logo-3d-wrap">
            <div class="logo-scene">
              <!-- Tower base platform -->
              <div class="tower-platform"></div>
              <!-- Tower segments (3 stacked floors) -->
              <div class="tower-segment tower-s1">
                <div class="ts-face ts-front"></div>
                <div class="ts-face ts-right"></div>
                <div class="ts-face ts-top"></div>
                <div class="ts-glow"></div>
              </div>
              <div class="tower-segment tower-s2">
                <div class="ts-face ts-front"></div>
                <div class="ts-face ts-right"></div>
                <div class="ts-face ts-top"></div>
                <div class="ts-glow"></div>
              </div>
              <div class="tower-segment tower-s3">
                <div class="ts-face ts-front"></div>
                <div class="ts-face ts-right"></div>
                <div class="ts-face ts-top"></div>
                <div class="ts-glow"></div>
              </div>
              <!-- Core beam -->
              <div class="tower-core"></div>
            </div>
            <!-- Orbit rings -->
            <div class="logo-orbit orbit-a"></div>
            <div class="logo-orbit orbit-b"></div>
            <!-- Floating data dots -->
            <div class="logo-dot dot-1"></div>
            <div class="logo-dot dot-2"></div>
            <div class="logo-dot dot-3"></div>
          </div>
          <transition name="fade">
            <div v-show="!isCollapsed" class="logo-text">
              <span class="logo-title">Hangzhou</span>
              <span class="logo-subtitle">Housing Analytics</span>
            </div>
          </transition>
        </div>

        <div class="sidebar-divider"></div>

        <el-menu
          :default-active="activeMenu"
          router
          :collapse="isCollapsed"
          class="sidebar-menu"
        >
          <el-menu-item index="/">
            <el-icon><DataBoard /></el-icon>
            <span>{{ t('dashboard') }}</span>
          </el-menu-item>
          <el-menu-item index="/listings">
            <el-icon><Search /></el-icon>
            <span>{{ t('exploreListings') }}</span>
          </el-menu-item>
          <el-menu-item index="/district">
            <el-icon><MapLocation /></el-icon>
            <span>{{ t('districtAnalysis') }}</span>
          </el-menu-item>
          <el-menu-item index="/factors">
            <el-icon><TrendCharts /></el-icon>
            <span>{{ t('priceFactors') }}</span>
          </el-menu-item>
          <el-menu-item index="/evaluation">
            <el-icon><Histogram /></el-icon>
            <span>{{ t('pcaEvaluation') }}</span>
          </el-menu-item>
          <el-menu-item index="/classification">
            <el-icon><Connection /></el-icon>
            <span>{{ t('classification') }}</span>
          </el-menu-item>
          <el-menu-item index="/cleaning">
            <el-icon><Document /></el-icon>
            <span>{{ t('dataCleaning') }}</span>
          </el-menu-item>
          <el-menu-item index="/map">
            <el-icon><MapLocation /></el-icon>
            <span>{{ t('mapView') }}</span>
          </el-menu-item>
          <el-menu-item index="/house-gallery">
            <el-icon><PictureFilled /></el-icon>
            <span>{{ t('houseGallery') }}</span>
          </el-menu-item>
          <el-menu-item index="/photos">
            <el-icon><MagicStick /></el-icon>
            <span>{{ t('visualStorytelling') }}</span>
          </el-menu-item>
          <el-menu-item index="/gallery">
            <el-icon><Grid /></el-icon>
            <span>{{ t('chartGallery') }}</span>
          </el-menu-item>
          <el-menu-item index="/recommendations">
            <el-icon><MagicStick /></el-icon>
            <span>{{ t('buyingGuide') }}</span>
          </el-menu-item>
        </el-menu>

        <div class="sidebar-footer" v-show="!isCollapsed">
          <div class="footer-stats">
            <div class="stat-dot green"></div>
            <span>{{ t('systemActive') }}</span>
          </div>
          <div class="footer-version">v2.0</div>
        </div>
      </el-aside>

      <!-- Main Content -->
      <el-main class="main-content" :style="{ marginLeft: isMobile ? '0px' : (isCollapsed ? '70px' : '240px') }">
        <!-- Top Bar -->
        <div class="top-bar">
          <div class="breadcrumb">
            <el-breadcrumb separator="/">
              <el-breadcrumb-item :to="{ path: '/' }">{{ t('home') }}</el-breadcrumb-item>
              <el-breadcrumb-item v-if="currentPageTitle">{{ currentPageTitle }}</el-breadcrumb-item>
            </el-breadcrumb>
          </div>
          <div class="top-actions">
            <el-tooltip :content="theme === 'dark' ? 'Light Mode' : 'Dark Mode'" placement="bottom">
              <el-button circle class="glass-btn" @click="toggleTheme">
                <el-icon><component :is="theme === 'dark' ? 'Sunny' : 'Moon'" /></el-icon>
              </el-button>
            </el-tooltip>
            <el-tooltip :content="t('refreshData')" placement="bottom">
              <el-button circle class="glass-btn" @click="refreshData">
                <el-icon><Refresh /></el-icon>
              </el-button>
            </el-tooltip>
            <el-tooltip :content="t('toggleSidebar')" placement="bottom">
              <el-button circle class="glass-btn" @click="isCollapsed = !isCollapsed">
                <el-icon><Fold /></el-icon>
              </el-button>
            </el-tooltip>
          </div>
        </div>

        <!-- Page Content -->
        <router-view v-slot="{ Component }">
          <transition name="page-fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { computed, ref, provide, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import LoadingScreen from './components/LoadingScreen.vue'
import { useAppStore } from './stores/app'
import { useI18n } from './i18n'

const route = useRoute()
const router = useRouter()
const { state, toggleTheme } = useAppStore()
const { t } = useI18n()
const theme = computed(() => state.theme)

const isCollapsed = ref(false)
const mobileMenuOpen = ref(false)
const isMobile = ref(window.innerWidth < 768)

// Lock body scroll when mobile menu is open
watch(mobileMenuOpen, (open) => {
  if (open) {
    document.body.style.overflow = 'hidden'
    document.body.style.position = 'fixed'
    document.body.style.width = '100%'
  } else {
    document.body.style.overflow = ''
    document.body.style.position = ''
    document.body.style.width = ''
  }
})

// Watch window resize
function onResize() {
  isMobile.value = window.innerWidth < 768
  if (window.innerWidth >= 768) mobileMenuOpen.value = false
}
onMounted(() => window.addEventListener('resize', onResize))
onUnmounted(() => {
  window.removeEventListener('resize', onResize)
  // Clean up body styles
  document.body.style.overflow = ''
  document.body.style.position = ''
  document.body.style.width = ''
})

const activeMenu = computed(() => route.path)

const pageTitleKeys = {
  '/': 'dashboardOverview',
  '/listings': 'exploreListingsPage',
  '/district': 'districtPriceAnalysis',
  '/factors': 'priceFactorAnalysis',
  '/evaluation': 'pcaFactorEvaluation',
  '/classification': 'listingClassification',
  '/map': 'geographicIntelligence',
  '/cleaning': 'dataCleaningProcess',
  '/house-gallery': 'housingPhotoGallery',
  '/photos': 'visualStorytelling',
  '/gallery': 'chartGallery',
  '/recommendations': 'homeBuyingGuide',
}

const currentPageTitle = computed(() => t(pageTitleKeys[route.path] || ''))

function refreshData() {
  router.go(0)
}

provide('isCollapsed', isCollapsed)
</script>

<style>
/* =============================================
   DARK THEME + PERFORMANCE GLOBAL STYLES
   ============================================= */

:root {
  --bg-primary: #0a0e17;
  --bg-secondary: #111827;
  --bg-card: #1a1f2e;
  --bg-glass: rgba(26, 31, 46, 0.7);
  --bg-glass-hover: rgba(30, 37, 55, 0.85);
  --border-glass: rgba(255, 255, 255, 0.06);
  --border-accent: rgba(64, 158, 255, 0.2);
  --text-primary: #e8eaed;
  --text-secondary: #9ca3af;
  --text-muted: #6b7280;
  --accent-blue: #409EFF;
  --accent-cyan: #00d4ff;
  --accent-purple: #a855f7;
  --accent-green: #22c55e;
  --accent-orange: #f59e0b;
  --accent-red: #ef4444;
  --accent-pink: #ec4899;
  --gradient-blue: linear-gradient(135deg, #409EFF, #00d4ff);
  --gradient-purple: linear-gradient(135deg, #a855f7, #6366f1);
  --gradient-card: linear-gradient(145deg, rgba(26,31,46,0.9), rgba(17,24,39,0.95));
  --shadow-glass: 0 8px 32px rgba(0, 0, 0, 0.4);
  --shadow-glow: 0 0 20px rgba(64, 158, 255, 0.15);
  --radius-lg: 16px;
  --radius-md: 12px;
  --radius-sm: 8px;
}

/* ====== LIGHT MODE ====== */
[data-theme="light"] {
  --bg-primary: #f0f2f5;
  --bg-secondary: #ffffff;
  --bg-card: #ffffff;
  --bg-glass: rgba(255,255,255,0.9);
  --bg-glass-hover: rgba(255,255,255,1);
  --border-glass: rgba(0,0,0,0.08);
  --border-accent: rgba(64,158,255,0.3);
  --text-primary: #111827;
  --text-secondary: #374151;
  --text-muted: #6b7280;
  --shadow-glass: 0 2px 16px rgba(0,0,0,0.06);
  --shadow-glow: 0 0 16px rgba(64,158,255,0.08);
  --gradient-card: linear-gradient(145deg, #ffffff, #f9fafb);
}
[data-theme="light"] body { background: #f0f2f5; color: #111827; }
[data-theme="light"] .app-container { background: #f0f2f5; }
[data-theme="light"] .main-content { background: #f0f2f5; }

/* Sidebar */
[data-theme="light"] .sidebar-glass {
  background: #ffffff !important;
  border-right: 1px solid rgba(0,0,0,0.08) !important;
}
[data-theme="light"] .sidebar-glass::before { opacity: 0.3; }
[data-theme="light"] .sidebar-divider { background: rgba(0,0,0,0.06); }
[data-theme="light"] .logo-title { color: #111827 !important; }
[data-theme="light"] .logo-subtitle { color: #6b7280 !important; }
[data-theme="light"] .sidebar-menu .el-menu-item { color: #374151 !important; }
[data-theme="light"] .sidebar-menu .el-menu-item:hover { background: rgba(64,158,255,0.06) !important; color: #111827 !important; }
[data-theme="light"] .sidebar-menu .el-menu-item.is-active { background: rgba(64,158,255,0.1) !important; color: #2563eb !important; box-shadow: inset 3px 0 0 #2563eb; }
[data-theme="light"] .sidebar-footer { border-top-color: rgba(0,0,0,0.06); }
[data-theme="light"] .footer-stats { color: #374151; }
[data-theme="light"] .footer-version { color: #6b7280; }

/* Top bar */
[data-theme="light"] .top-bar { background: #ffffff; border-color: rgba(0,0,0,0.06); box-shadow: 0 1px 4px rgba(0,0,0,0.04); }
[data-theme="light"] .glass-btn { background: #f3f4f6 !important; border-color: rgba(0,0,0,0.08) !important; color: #374151 !important; }
[data-theme="light"] .glass-btn:hover { background: #e5e7eb !important; color: #111827 !important; border-color: rgba(64,158,255,0.3) !important; }

/* Page headers */
[data-theme="light"] .page-header h2 { color: #111827; }
[data-theme="light"] .page-header p { color: #6b7280; }

/* Cards */
[data-theme="light"] .stat-card { background: #ffffff; border-color: rgba(0,0,0,0.06); box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
[data-theme="light"] .stat-card:hover { border-color: rgba(64,158,255,0.3); box-shadow: 0 4px 16px rgba(0,0,0,0.08); }
[data-theme="light"] .stat-card .stat-label { color: #6b7280; }
[data-theme="light"] .stat-card .stat-sub { color: #4b5563; }
[data-theme="light"] .section-card { background: #ffffff; border-color: rgba(0,0,0,0.06); box-shadow: 0 1px 3px rgba(0,0,0,0.03); }
[data-theme="light"] .section-card h3 { color: #111827; border-bottom-color: rgba(0,0,0,0.06); }
[data-theme="light"] .section-card h4 { color: #111827; }
[data-theme="light"] .stat-dot.green { box-shadow: 0 0 6px rgba(34,197,94,0.5); }

/* Gallery & modules */
[data-theme="light"] .gallery-item { background: #ffffff; border-color: rgba(0,0,0,0.06); }
[data-theme="light"] .gallery-item:hover { border-color: rgba(64,158,255,0.3); }
[data-theme="light"] .gallery-item-header { background: #f9fafb; border-bottom-color: rgba(0,0,0,0.06); }
[data-theme="light"] .gallery-item-title { color: #111827; }
[data-theme="light"] .module-card { background: #ffffff; border-color: rgba(0,0,0,0.06); }
[data-theme="light"] .module-card:hover { border-color: rgba(64,158,255,0.25); }
[data-theme="light"] .module-title { color: #111827; }
[data-theme="light"] .module-desc { color: #4b5563; }
[data-theme="light"] .module-tag { background: rgba(0,0,0,0.04); color: #6b7280; }
[data-theme="light"] .insight-card { background: #ffffff; border-color: rgba(0,0,0,0.06); }
[data-theme="light"] .insight-header { color: #111827; border-bottom-color: rgba(0,0,0,0.06); }
[data-theme="light"] .insight-row span { color: #6b7280; }
[data-theme="light"] .insight-row strong { color: #111827; }

/* Tables */
[data-theme="light"] .el-table {
  --el-table-bg-color: #fff; --el-table-tr-bg-color: #fff;
  --el-table-header-bg-color: #f9fafb; --el-table-border-color: rgba(0,0,0,0.06);
  --el-table-text-color: #374151; --el-table-header-text-color: #111827;
  --el-table-row-hover-bg-color: rgba(64,158,255,0.03);
  color: #374151 !important;
}
[data-theme="light"] .el-table td { color: #374151 !important; border-bottom-color: rgba(0,0,0,0.04) !important; }
[data-theme="light"] .el-table th { color: #111827 !important; border-bottom-color: rgba(0,0,0,0.08) !important; background: #f9fafb; }
[data-theme="light"] .el-table--striped .el-table__body tr.el-table__row--striped td { background: #f9fafb; }
[data-theme="light"] .el-table .el-table__body tr:hover > td { background-color: rgba(64,158,255,0.03) !important; }

/* Forms */
[data-theme="light"] .el-input__wrapper,
[data-theme="light"] .el-select .el-input__wrapper,
[data-theme="light"] .el-input-number .el-input__wrapper {
  background: #f9fafb !important; border-color: rgba(0,0,0,0.1) !important;
}
[data-theme="light"] .el-input__inner,
[data-theme="light"] .el-select .el-input__inner { color: #111827 !important; }
[data-theme="light"] .el-form-item__label { color: #374151 !important; }
[data-theme="light"] .el-radio-group .el-radio-button__inner { background: #f9fafb; border-color: rgba(0,0,0,0.1); color: #374151; }

/* Breadcrumb */
[data-theme="light"] .el-breadcrumb__inner { color: #9ca3af !important; }
[data-theme="light"] .el-breadcrumb__item:last-child .el-breadcrumb__inner { color: #374151 !important; font-weight: 500; }

/* Tags, pagination, dialog */
[data-theme="light"] .el-pagination { --el-pagination-bg-color: #fff; --el-pagination-text-color: #374151; }
[data-theme="light"] .el-pagination button { background: #fff !important; color: #374151 !important; }
[data-theme="light"] .el-pagination button.is-active { background: #409EFF !important; color: #fff !important; }
[data-theme="light"] .el-empty__description p { color: #9ca3af; }
[data-theme="light"] .el-dialog { background: #ffffff; box-shadow: 0 20px 60px rgba(0,0,0,0.15); }
[data-theme="light"] .el-dialog__header { background: #f9fafb; border-color: rgba(0,0,0,0.06); }
[data-theme="light"] .el-dialog__title { color: #111827; }
[data-theme="light"] .el-divider { border-color: rgba(0,0,0,0.06); }
[data-theme="light"] .el-card { background: #fff; border-color: rgba(0,0,0,0.06); color: #111827; }
[data-theme="light"] .el-timeline-item__node { background: #fff; border-color: rgba(64,158,255,0.3); }

/* Scrollbar */
[data-theme="light"] ::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.15); }
[data-theme="light"] ::-webkit-scrollbar-thumb:hover { background: rgba(0,0,0,0.25); }

/* Override hardcoded white text */
[data-theme="light"] .section-card h3,
[data-theme="light"] .gallery-item-title,
[data-theme="light"] .module-title,
[data-theme="light"] .insight-header,
[data-theme="light"] .dark-list strong,
[data-theme="light"] .sig-name,
[data-theme="light"] .detail-row strong,
[data-theme="light"] .mini-dist-name { color: #111827 !important; }

[data-theme="light"] .dark-list { color: #374151; }
[data-theme="light"] .section-card p,
[data-theme="light"] .module-desc,
[data-theme="light"] .sig-direction,
[data-theme="light"] .detail-row span:first-child,
[data-theme="light"] .mini-dist-price,
[data-theme="light"] .mini-dist-count { color: #4b5563 !important; }

/* MapView specific */
[data-theme="light"] .map-card { background: #ffffff; }
[data-theme="light"] .mini-dist-card { background: #f9fafb; border-color: rgba(0,0,0,0.04); }
[data-theme="light"] .mini-dist-card:hover,
[data-theme="light"] .mini-dist-card.active { background: rgba(64,158,255,0.06); border-color: rgba(64,158,255,0.2); }
[data-theme="light"] .detail-row { border-bottom-color: rgba(0,0,0,0.04); }
[data-theme="light"] .listing-preview-card { background: #ffffff; border-color: rgba(0,0,0,0.06); }
[data-theme="light"] .listing-preview-card:hover { border-color: rgba(64,158,255,0.2); }

/* DataCleaning specific */
[data-theme="light"] .sig-card { background: #ffffff; border-color: rgba(0,0,0,0.06); }
[data-theme="light"] .sig-stat-mini { background: #f9fafb; }
[data-theme="light"] .ssm-label { color: #6b7280; }
[data-theme="light"] .ssm-val { color: #374151; }
[data-theme="light"] .sig-summary { background: rgba(64,158,255,0.03); border-color: rgba(64,158,255,0.1); }
[data-theme="light"] .sig-summary-text { color: #374151; }

/* FactorAnalysis specific */
[data-theme="light"] .sig-level-track { background: rgba(0,0,0,0.06); }
[data-theme="light"] .sig-impact-bar-wrap { background: rgba(0,0,0,0.06); }

/* HouseGallery specific */
[data-theme="light"] .hg-card { background: #ffffff; border-color: rgba(0,0,0,0.06); }
[data-theme="light"] .hg-card:hover { border-color: rgba(0,0,0,0.1); }
[data-theme="light"] .hg-layout { color: #111827; }
[data-theme="light"] .hg-ilabel { color: #6b7280; }
[data-theme="light"] .hg-ivalue { color: #374151; }
[data-theme="light"] .hg-tag { background: rgba(0,0,0,0.04); color: #374151; }
[data-theme="light"] .hg-prediction { border-top-color: rgba(0,0,0,0.06); }
[data-theme="light"] .hg-prediction span { color: #6b7280; }

/* PhotoGallery specific */
[data-theme="light"] .s-card { background: #ffffff; border-color: rgba(0,0,0,0.06); }
[data-theme="light"] .s-card:hover { border-color: rgba(0,0,0,0.1); }
[data-theme="light"] .sc-info h3 { color: #111827; }
[data-theme="light"] .sc-info p { color: #4b5563; }
[data-theme="light"] .chapter-insight { background: rgba(64,158,255,0.03); border-color: rgba(64,158,255,0.1); }
[data-theme="light"] .chapter-insight p { color: #374151; }
[data-theme="light"] .epilogue-stats strong { color: #111827; }
[data-theme="light"] .story-epilogue p { color: #4b5563; }

/* Chart/dark containers that need light bg */
[data-theme="light"] .gallery-chart-wrap,
[data-theme="light"] .chart-container { background: transparent; }

/* Hamburger menu */
[data-theme="light"] .mobile-hamburger { background: #ffffff; border-color: rgba(0,0,0,0.1); }
[data-theme="light"] .mobile-hamburger span { background: #374151; }
[data-theme="light"] .mobile-sidebar-open .mobile-hamburger span { background: #2563eb; }

/* Floating/profile cards */
[data-theme="light"] .float-card { background: rgba(255,255,255,0.9); border-color: rgba(0,0,0,0.06); }
[data-theme="light"] .float-card:hover { border-color: rgba(64,158,255,0.3); }
[data-theme="light"] .strip-card { background: #ffffff; border-color: rgba(0,0,0,0.06); }
[data-theme="light"] .strip-card:hover { border-color: rgba(0,0,0,0.1); }
[data-theme="light"] .strip-value { color: #111827; }

/* Preview chart cards */
[data-theme="light"] .preview-chart-card { background: #ffffff; }

/* Filter bar */
[data-theme="light"] .filter-bar { background: #ffffff; }

/* Recommendations specific */
[data-theme="light"] .dark-list { color: #374151; }
[data-theme="light"] .dark-list strong { color: #2563eb; }

/* Loading screen compatibility */
[data-theme="light"] .loader-root { background: #f0f2f5; }
[data-theme="light"] .loader-canvas { opacity: 0.5; }

/* Misc light overrides for hardcoded dark text */
[data-theme="light"] .section-heading { color: #111827; }
[data-theme="light"] .heading-sub { color: #6b7280; }
[data-theme="light"] .hero-badge { background: rgba(64,158,255,0.06); border-color: rgba(64,158,255,0.15); color: #2563eb; }
[data-theme="light"] .title-line { color: #111827; }
[data-theme="light"] .hero-subtitle { color: #4b5563; }
[data-theme="light"] .cta-secondary { background: #f3f4f6 !important; border-color: rgba(0,0,0,0.1) !important; color: #374151 !important; }
[data-theme="light"] .cta-secondary:hover { background: #e5e7eb !important; }
[data-theme="light"] .footer-cta h2 { color: #111827; }
[data-theme="light"] .footer-cta p { color: #6b7280; }
[data-theme="light"] .footer-credit { color: #9ca3af; }
[data-theme="light"] .fc-label { color: #6b7280 !important; }
[data-theme="light"] .fc-value { color: inherit; }
[data-theme="light"] .strip-label { color: #6b7280; }
[data-theme="light"] .sig-badge { background: rgba(64,158,255,0.08); color: #2563eb; }
[data-theme="light"] .dist-stat-card { background: #ffffff; border-color: rgba(0,0,0,0.06); }
[data-theme="light"] .dist-stat-val { color: #111827; }
[data-theme="light"] .dist-stat-lbl { color: #6b7280; }
[data-theme="light"] .dist-chart-card { background: #ffffff; }

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'PingFang SC', 'Microsoft YaHei', 'Inter', 'Helvetica Neue', sans-serif;
  background: var(--bg-primary);
  color: var(--text-primary);
}

.app-container {
  min-height: 100vh;
  background: var(--bg-primary);
}

/* =============================================
   SIDEBAR GLASS DESIGN
   ============================================= */
.sidebar-glass {
  background: linear-gradient(180deg, rgba(17,24,39,0.98) 0%, rgba(10,14,23,0.95) 100%) !important;
  border-right: 1px solid var(--border-glass) !important;
  backdrop-filter: blur(20px);
  min-height: 100vh;
  height: 100vh;
  transition: width 0.35s cubic-bezier(0.4, 0, 0.2, 1) !important;
  position: fixed !important;
  top: 0;
  left: 0;
  z-index: 100;
  overflow: hidden;
}

.sidebar-glass::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(ellipse at 30% 20%, rgba(64,158,255,0.03) 0%, transparent 50%),
              radial-gradient(ellipse at 70% 80%, rgba(168,85,247,0.03) 0%, transparent 50%);
  pointer-events: none;
}

.logo-section {
  display: flex;
  align-items: center;
  padding: 20px 18px;
  cursor: pointer;
  gap: 12px;
  transition: all 0.3s ease;
}

/* ====== 3D LOGO: DATA TOWER ====== */
.logo-3d-wrap {
  position: relative;
  width: 52px;
  height: 52px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* ---- 3D Scene ---- */
.logo-scene {
  width: 44px;
  height: 44px;
  perspective: 180px;
  perspective-origin: 50% 35%;
  position: relative;
  z-index: 2;
  transform-style: preserve-3d;
  animation: scene-drift 6s ease-in-out infinite;
}
@keyframes scene-drift {
  0%, 100% { transform: rotateY(0deg); }
  25%  { transform: rotateY(5deg); }
  75%  { transform: rotateY(-5deg); }
}

/* ---- Tower Platform ---- */
.tower-platform {
  position: absolute;
  bottom: 6px;
  left: 50%;
  transform: translateX(-50%) rotateX(60deg);
  width: 36px;
  height: 36px;
  background: radial-gradient(ellipse, rgba(64,158,255,0.15) 0%, rgba(64,158,255,0.04) 50%, transparent 70%);
  border-radius: 50%;
  border: 1px solid rgba(64,158,255,0.1);
  animation: platform-pulse 3s ease-in-out infinite;
}
@keyframes platform-pulse {
  0%, 100% { box-shadow: 0 0 8px rgba(64,158,255,0.1); }
  50% { box-shadow: 0 0 20px rgba(64,158,255,0.25); }
}

/* ---- Tower Segments (3 isometric stacked blocks) ---- */
.tower-segment {
  position: absolute;
  width: 22px;
  height: 22px;
  transform-style: preserve-3d;
  left: 11px;
}
.tower-s1 { top: 16px; z-index: 4; animation: seg-breathe 4s ease-in-out infinite; }
.tower-s2 { top: 8px;  z-index: 3; animation: seg-breathe 4s ease-in-out 0.3s infinite; }
.tower-s3 { top: 0px;  z-index: 2; animation: seg-breathe 4s ease-in-out 0.6s infinite; }
@keyframes seg-breathe {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-1px); }
}

/* Segment faces */
.ts-face {
  position: absolute;
  backface-visibility: hidden;
}
.ts-front {
  width: 20px;
  height: 7px;
  background: linear-gradient(180deg, rgba(64,158,255,0.9), rgba(30,100,220,0.95));
  border-radius: 1.5px;
  box-shadow: 0 0 6px rgba(64,158,255,0.4) inset;
  top: 0;
  left: 0;
}
.ts-right {
  width: 7px;
  height: 7px;
  background: rgba(24,80,190,0.9);
  right: -4px;
  top: 0;
  transform-origin: left center;
  border-radius: 0 1.5px 1.5px 0;
}
.ts-top {
  width: 20px;
  height: 7px;
  background: rgba(100,180,255,0.7);
  top: -4px;
  left: 0;
  transform-origin: bottom center;
  border-radius: 1.5px 1.5px 0 0;
}

/* Segment glow */
.ts-glow {
  position: absolute;
  top: 0;
  left: 0;
  width: 20px;
  height: 7px;
  background: transparent;
  box-shadow: 0 0 10px rgba(64,158,255,0.5), 0 0 20px rgba(64,158,255,0.2);
  border-radius: 1.5px;
  animation: glow-flicker 2s ease-in-out infinite;
}
@keyframes glow-flicker {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

/* ---- Core Beam ---- */
.tower-core {
  position: absolute;
  left: 50%;
  top: -2px;
  transform: translateX(-50%);
  width: 2px;
  height: 28px;
  background: linear-gradient(to top, transparent, #00d4ff, #409EFF, #a855f7, transparent);
  border-radius: 1px;
  z-index: 5;
  animation: core-pulse 2.5s ease-in-out infinite;
  box-shadow: 0 0 8px rgba(0,212,255,0.6), 0 0 20px rgba(64,158,255,0.3);
}
@keyframes core-pulse {
  0%, 100% { opacity: 0.5; height: 28px; }
  50% { opacity: 1; height: 32px; }
}

/* ---- Orbit Rings ---- */
.logo-orbit {
  position: absolute;
  top: 50%;
  left: 50%;
  border-radius: 50%;
  border: 1px solid transparent;
  pointer-events: none;
}
.orbit-a {
  width: 54px;
  height: 54px;
  margin: -27px 0 0 -27px;
  border-color: rgba(64,158,255,0.2);
  animation: orbit-spin-a 7s linear infinite;
}
.orbit-b {
  width: 38px;
  height: 38px;
  margin: -19px 0 0 -19px;
  border-color: rgba(168,85,247,0.15);
  border-style: dashed;
  border-width: 0.8px;
  animation: orbit-spin-b 5s linear infinite reverse;
}
@keyframes orbit-spin-a { to { transform: rotate(360deg); } }
@keyframes orbit-spin-b { to { transform: rotate(-360deg); } }

/* ---- Floating Dots ---- */
.logo-dot {
  position: absolute;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  pointer-events: none;
}
.dot-1 {
  background: #00d4ff;
  box-shadow: 0 0 6px #00d4ff;
  animation: dot-float-1 3.5s ease-in-out infinite;
  top: 8px; left: 10px;
}
.dot-2 {
  background: #a855f7;
  box-shadow: 0 0 6px #a855f7;
  animation: dot-float-2 4s ease-in-out infinite 0.5s;
  top: 6px; right: 8px;
}
.dot-3 {
  background: #22c55e;
  box-shadow: 0 0 6px #22c55e;
  animation: dot-float-3 3s ease-in-out infinite 1s;
  bottom: 10px; right: 10px;
}
@keyframes dot-float-1 {
  0%, 100% { transform: translate(0, 0) scale(1); opacity: 0.6; }
  50% { transform: translate(6px, -8px) scale(1.6); opacity: 1; }
}
@keyframes dot-float-2 {
  0%, 100% { transform: translate(0, 0) scale(0.8); opacity: 0.5; }
  50% { transform: translate(-5px, -10px) scale(1.4); opacity: 1; }
}
@keyframes dot-float-3 {
  0%, 100% { transform: translate(0, 0) scale(1); opacity: 0.7; }
  50% { transform: translate(-7px, -6px) scale(1.5); opacity: 1; }
}

/* ---- Hover: intensify ---- */
.logo-section:hover .logo-scene { animation-duration: 3s; }
.logo-section:hover .orbit-a { border-color: rgba(64,158,255,0.45); box-shadow: 0 0 14px rgba(64,158,255,0.2); }
.logo-section:hover .orbit-b { border-color: rgba(168,85,247,0.35); }
.logo-section:hover .tower-core { box-shadow: 0 0 14px rgba(0,212,255,0.9), 0 0 30px rgba(64,158,255,0.5); }
.logo-section:hover .ts-glow { box-shadow: 0 0 16px rgba(64,158,255,0.7), 0 0 30px rgba(64,158,255,0.3); }
.logo-section:hover .dot-1, .logo-section:hover .dot-2, .logo-section:hover .dot-3 {
  animation-duration: 1.5s;
}

.logo-text {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.logo-title {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  letter-spacing: 0.5px;
}

.logo-subtitle {
  font-size: 11px;
  color: var(--text-muted);
  letter-spacing: 1px;
  text-transform: uppercase;
}

.sidebar-divider {
  height: 1px;
  background: var(--border-glass);
  margin: 0 16px 8px;
}

.sidebar-menu {
  border-right: none !important;
  background: transparent !important;
  padding: 8px;
}

.sidebar-menu .el-menu-item {
  margin: 3px 0;
  border-radius: 10px !important;
  transition: all 0.3s ease !important;
  color: var(--text-secondary) !important;
  font-size: 14px;
  height: 48px;
  line-height: 48px;
}

.sidebar-menu .el-menu-item:hover {
  background: rgba(64, 158, 255, 0.08) !important;
  color: #fff !important;
  transform: translateX(3px);
}

.sidebar-menu .el-menu-item.is-active {
  background: rgba(64, 158, 255, 0.12) !important;
  color: var(--accent-cyan) !important;
  font-weight: 600;
  box-shadow: inset 3px 0 0 var(--accent-cyan);
}

.sidebar-footer {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px 20px;
  border-top: 1px solid var(--border-glass);
}

.footer-stats {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--text-secondary);
}

.stat-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.stat-dot.green {
  background: var(--accent-green);
  box-shadow: 0 0 8px rgba(34, 197, 94, 0.5);
  animation: pulse-dot 2s infinite;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.footer-version {
  font-size: 10px;
  color: var(--text-muted);
  margin-top: 4px;
  letter-spacing: 1px;
}

/* =============================================
   MAIN CONTENT AREA
   ============================================= */
.main-content {
  background: var(--bg-primary);
  padding: 24px 28px;
  min-height: 100vh;
  transition: margin-left 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
  padding: 16px 20px;
  background: var(--bg-glass);
  backdrop-filter: blur(12px);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-lg);
}

.top-bar .el-breadcrumb {
  font-size: 14px;
}

.glass-btn {
  background: var(--bg-glass) !important;
  border: 1px solid var(--border-glass) !important;
  color: var(--text-secondary) !important;
  transition: all 0.3s ease !important;
}

.glass-btn:hover {
  background: var(--bg-glass-hover) !important;
  color: #fff !important;
  border-color: var(--border-accent) !important;
  box-shadow: var(--shadow-glow);
}
/* =============================================
   PAGE TRANSITIONS
   ============================================= */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.page-fade-enter-from {
  opacity: 0;
  transform: translateY(12px);
}

.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-12px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* =============================================
   SHARED DARK CARDS & COMPONENTS
   ============================================= */
.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  font-size: 26px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 4px;
  letter-spacing: -0.3px;
}

.page-header p {
  color: var(--text-secondary);
  font-size: 14px;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 18px;
  margin-bottom: 24px;
}

.stat-card {
  background: var(--gradient-card);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-lg);
  padding: 22px 24px;
  backdrop-filter: blur(12px);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--gradient-blue);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-glass), var(--shadow-glow);
  border-color: var(--border-accent);
}

.stat-card:hover::before {
  opacity: 1;
}

.stat-card .stat-label {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  color: var(--text-muted);
  margin-bottom: 8px;
  font-weight: 600;
}

.stat-card .stat-value {
  font-size: 32px;
  font-weight: 800;
  letter-spacing: -1px;
}

.stat-card .stat-sub {
  font-size: 13px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.text-blue { color: var(--accent-blue); }
.text-cyan { color: var(--accent-cyan); }
.text-green { color: var(--accent-green); }
.text-orange { color: var(--accent-orange); }
.text-red { color: var(--accent-red); }
.text-purple { color: var(--accent-purple); }

.section-card {
  background: var(--bg-card);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-lg);
  padding: 24px;
  margin-bottom: 24px;
  backdrop-filter: blur(8px);
  transition: all 0.3s ease;
}

.section-card:hover {
  border-color: var(--border-accent);
}

.section-card h3 {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 18px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-glass);
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-card h3::before {
  content: '';
  width: 4px;
  height: 20px;
  background: var(--gradient-blue);
  border-radius: 2px;
}

.chart-container {
  width: 100%;
  height: 420px;
}

/* =============================================
   GALLERY GRID
   ============================================= */
.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
  gap: 20px;
}

.gallery-item {
  background: var(--bg-card);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: all 0.4s ease;
  cursor: pointer;
  position: relative;
}

.gallery-item:hover {
  transform: translateY(-6px);
  box-shadow: var(--shadow-glass), var(--shadow-glow);
  border-color: var(--border-accent);
}

.gallery-item-header {
  padding: 14px 18px;
  background: rgba(0,0,0,0.3);
  border-bottom: 1px solid var(--border-glass);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.gallery-item-title {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
}

.gallery-chart-wrap {
  height: 380px;
  padding: 8px;
}

/* =============================================
   TIMELINE & LIST STYLES
   ============================================= */
.dark-timeline .el-timeline-item__node {
  background: var(--bg-card);
  border-color: var(--border-accent);
}

.dark-list {
  line-height: 2.2;
  color: var(--text-secondary);
  font-size: 14px;
}

.dark-list strong {
  color: var(--accent-cyan);
}

/* =============================================
   SCROLLBAR
   ============================================= */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: rgba(255,255,255,0.1);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(255,255,255,0.2);
}

/* =============================================
   ELEMENT PLUS DARK OVERRIDES
   ============================================= */
.el-table {
  --el-table-bg-color: var(--bg-card);
  --el-table-tr-bg-color: var(--bg-card);
  --el-table-header-bg-color: rgba(0,0,0,0.4);
  --el-table-border-color: var(--border-glass);
  --el-table-text-color: #b0b7c3;
  --el-table-header-text-color: #c8cdd5;
  --el-table-row-hover-bg-color: rgba(64,158,255,0.08);
  color: #b0b7c3 !important;
  font-size: 13px;
}

.el-table .el-table__body tr {
  background-color: var(--bg-card);
}

.el-table .el-table__body tr.el-table__row--striped {
  background-color: rgba(255,255,255,0.015);
}

.el-table .el-table__body tr:hover > td {
  background-color: rgba(64,158,255,0.06) !important;
}

.el-table .el-table__body td {
  color: #b0b7c3 !important;
  border-bottom-color: rgba(255,255,255,0.04) !important;
}

.el-table .el-table__body td .el-table__cell {
  color: #b0b7c3;
}

.el-table th.el-table__cell {
  background: rgba(0,0,0,0.4);
  font-weight: 600;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: #c8cdd5 !important;
  border-bottom: 2px solid rgba(255,255,255,0.08) !important;
}

.el-table--striped .el-table__body tr.el-table__row--striped td {
  background: rgba(255,255,255,0.018);
}

.el-pagination {
  --el-pagination-bg-color: var(--bg-card);
  --el-pagination-text-color: var(--text-primary);
}

.el-input__wrapper, .el-select .el-input__wrapper, .el-input-number .el-input__wrapper {
  background: var(--bg-secondary) !important;
  border-color: var(--border-glass) !important;
  box-shadow: none !important;
}

.el-input__inner, .el-select .el-input__inner {
  color: var(--text-primary) !important;
}

.el-radio-group .el-radio-button__inner {
  background: var(--bg-secondary);
  border-color: var(--border-glass);
  color: var(--text-secondary);
}

.el-radio-group .el-radio-button.is-active .el-radio-button__inner {
  background: var(--accent-blue);
  border-color: var(--accent-blue);
  color: #fff;
}

.el-tag {
  border: none;
}

.el-empty__description p {
  color: var(--text-muted);
}

.el-card {
  background: var(--bg-card);
  border-color: var(--border-glass);
  color: var(--text-primary);
}

.el-divider {
  border-color: var(--border-glass);
}

.el-breadcrumb__inner {
  color: var(--text-muted) !important;
}

.el-breadcrumb__item:last-child .el-breadcrumb__inner {
  color: var(--text-secondary) !important;
}

/* =============================================
   MOBILE RESPONSIVE — ≤768px
   ============================================= */
@media (max-width: 768px) {
  /* Mobile hamburger */
  .mobile-hamburger {
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 5px;
    position: fixed;
    top: 12px;
    left: 12px;
    z-index: 200;
    width: 40px;
    height: 40px;
    border-radius: 10px;
    background: rgba(20,25,35,0.9);
    border: 1px solid rgba(255,255,255,0.08);
    cursor: pointer;
    padding: 10px;
    backdrop-filter: blur(12px);
  }
  .mobile-hamburger span {
    display: block;
    height: 2px;
    background: #c8cdd5;
    border-radius: 1px;
    transition: all 0.3s ease;
  }
  .mobile-sidebar-open .mobile-hamburger span:nth-child(1) { transform: rotate(45deg) translate(5px,5px); }
  .mobile-sidebar-open .mobile-hamburger span:nth-child(2) { opacity: 0; }
  .mobile-sidebar-open .mobile-hamburger span:nth-child(3) { transform: rotate(-45deg) translate(5px,-5px); }

  /* Mobile overlay */
  .mobile-overlay {
    position: fixed;
    inset: 0;
    z-index: 98;
    background: rgba(0,0,0,0.5);
    backdrop-filter: blur(4px);
  }

  /* Sidebar on mobile: off-screen by default, slides in when menu open */
  .sidebar-glass {
    position: fixed !important;
    left: -280px;
    top: 0;
    height: 100vh !important;
    z-index: 99;
    transition: left 0.35s cubic-bezier(0.4,0,0.2,1) !important;
    width: 280px !important;
    overflow-y: auto;
    overflow-x: hidden;
    -webkit-overflow-scrolling: touch;
    overscroll-behavior: contain;
    touch-action: pan-y;
  }
  .sidebar-glass.mobile-visible {
    left: 0;
  }

  /* Main content full width on mobile */
  .main-content {
    margin-left: 0 !important;
    padding: 16px 14px 60px !important;
  }

  /* Top bar */
  .top-bar {
    padding: 10px 14px !important;
    margin-bottom: 16px !important;
    margin-left: 36px !important;
  }
  .top-bar .el-breadcrumb { font-size: 12px; }

  /* Cards single column */
  .card-grid {
    grid-template-columns: 1fr !important;
    gap: 12px !important;
  }

  /* Section cards less padding */
  .section-card {
    padding: 16px 14px !important;
    margin-bottom: 14px !important;
  }
  .section-card h3 {
    font-size: 16px !important;
  }

  /* Charts fit screen */
  .chart-container {
    height: 280px !important;
  }

  /* Tables scroll horizontally */
  .el-table {
    font-size: 12px !important;
  }
  .el-table td,
  .el-table th {
    padding: 6px 8px !important;
  }
  .el-table .el-table__body-wrapper {
    overflow-x: auto;
  }

  /* Forms stack */
  .el-form--inline .el-form-item {
    display: block !important;
    margin-right: 0 !important;
    margin-bottom: 10px !important;
  }
  .el-form--inline {
    display: block !important;
  }

  /* Gallery grids */
  .gallery-grid, .gallery-masonry, .modules-grid, .insights-grid, .story-cards {
    grid-template-columns: 1fr !important;
    gap: 12px !important;
  }

  /* Hero title */
  .hero-title, .gallery-title {
    font-size: 32px !important;
  }
  .hero-subtitle, .gallery-desc {
    font-size: 14px !important;
  }

  /* Floating stats */
  .floating-stats {
    flex-direction: column !important;
    align-items: center !important;
    gap: 12px !important;
  }
  .float-card {
    width: 100% !important;
    max-width: 300px !important;
  }

  /* Stats strip */
  .stats-strip {
    flex-direction: column !important;
    align-items: center !important;
    gap: 10px !important;
  }
  .strip-card {
    width: 100% !important;
    max-width: 320px !important;
  }

  /* Map card */
  .map-card, .map-canvas, .sat-bg-canvas {
    height: 380px !important;
  }

  /* Page header */
  .page-header h2 {
    font-size: 22px !important;
  }

  /* Gallery & masonry cards */
  .g-card-wrap.wide { grid-column: span 1 !important; }
  .lpc-image { height: 120px !important; }

  /* Footer links */
  .footer-links { flex-direction: column !important; align-items: center !important; }
  .footer-cta h2 { font-size: 24px !important; }

  /* Lightbox on mobile */
  .lb-container { flex-direction: column !important; max-height: 90vh !important; }
  .lb-hero-art { width: 100% !important; min-height: 180px !important; }
  .lb-body { padding: 20px !important; }
  .lb-body h2 { font-size: 20px !important; }

  /* Filter bar */
  .filter-bar { padding: 10px 0 !important; }
  .filter-track { justify-content: flex-start !important; flex-wrap: nowrap !important; overflow-x: auto !important; padding: 0 10px !important; }
  .filter-btn { white-space: nowrap !important; flex-shrink: 0 !important; }

  /* Hide footer version on mobile */
  .sidebar-footer { display: none; }
  .footer-credit { font-size: 10px !important; }
}
@media (min-width: 769px) {
  .mobile-hamburger { display: none; }
  .mobile-overlay { display: none; }
}
</style>
