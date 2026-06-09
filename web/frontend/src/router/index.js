import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Overview',
    component: () => import('../views/Overview.vue'),
  },
  {
    path: '/listings',
    name: 'Listings',
    component: () => import('../views/Listings.vue'),
  },
  {
    path: '/district',
    name: 'DistrictAnalysis',
    component: () => import('../views/DistrictAnalysis.vue'),
  },
  {
    path: '/factors',
    name: 'FactorAnalysis',
    component: () => import('../views/FactorAnalysis.vue'),
  },
  {
    path: '/evaluation',
    name: 'Evaluation',
    component: () => import('../views/Evaluation.vue'),
  },
  {
    path: '/classification',
    name: 'Classification',
    component: () => import('../views/Classification.vue'),
  },
  {
    path: '/gallery',
    name: 'Gallery',
    component: () => import('../views/Gallery.vue'),
  },
  {
    path: '/photos',
    name: 'PhotoGallery',
    component: () => import('../views/PhotoGallery.vue'),
  },
  {
    path: '/house-gallery',
    name: 'HouseGallery',
    component: () => import('../views/HouseGallery.vue'),
  },
  {
    path: '/recommendations',
    name: 'Recommendations',
    component: () => import('../views/Recommendations.vue'),
  },
  {
    path: '/charts',
    name: 'Charts',
    component: () => import('../views/Charts.vue'),
  },
  {
    path: '/map',
    name: 'MapView',
    component: () => import('../views/MapView.vue'),
  },
  {
    path: '/cleaning',
    name: 'DataCleaning',
    component: () => import('../views/DataCleaning.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
