import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

// Overview
export function getOverview() {
  return api.get('/overview')
}

// Listings
export function getListings(params = {}) {
  return api.get('/listings', { params })
}

export function getDistricts() {
  return api.get('/districts')
}

export function getLayouts() {
  return api.get('/layouts')
}

// Analysis
export function getDistrictAnalysis() {
  return api.get('/district-analysis')
}

export function getFactorAnalysis() {
  return api.get('/factor-analysis')
}

export function getPCAAnalysis() {
  return api.get('/pca-analysis')
}

export function getClusterAnalysis() {
  return api.get('/cluster-analysis')
}

export function getRecommendations() {
  return api.get('/recommendations')
}

export function getDescriptiveStats() {
  return api.get('/stats/descriptive')
}

// Charts
export function getCharts() {
  return api.get('/charts')
}

export function getChartData(chartId) {
  return api.get(`/chart-data/${chartId}`)
}

export default api
