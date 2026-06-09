<template>
  <div>
    <div class="page-header">
      <h2>{{ t('exploreListingsPage') }}</h2>
      <p>{{ t('listingsDesc', { total: total.toLocaleString() }) }}</p>
    </div>

    <div class="section-card">
      <el-form :inline="true" :model="filters" size="default">
        <el-form-item :label="t('district')">
          <el-select v-model="filters.district" :placeholder="t('allDistricts')" clearable style="width:145px">
            <el-option v-for="d in districts" :key="d" :label="d" :value="d" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('layout')">
          <el-select v-model="filters.layout" :placeholder="t('allLayouts')" clearable style="width:145px">
            <el-option v-for="l in layouts" :key="l" :label="l" :value="l" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('totalPrice')">
          <el-input-number v-model="filters.min_price" :min="0" :step="10" style="width:115px" placeholder="Min" controls-position="right" />
          <span style="margin:0 8px;color:var(--text-muted)"> {{ t('to') }} </span>
          <el-input-number v-model="filters.max_price" :min="0" :step="10" style="width:115px" placeholder="Max" controls-position="right" />
        </el-form-item>
        <el-form-item :label="t('area')">
          <el-input-number v-model="filters.min_area" :min="0" :step="5" style="width:115px" placeholder="Min" controls-position="right" />
          <span style="margin:0 8px;color:var(--text-muted)"> {{ t('to') }} </span>
          <el-input-number v-model="filters.max_area" :min="0" :step="5" style="width:115px" placeholder="Max" controls-position="right" />
        </el-form-item>
        <el-form-item :label="t('decoration')">
          <el-select v-model="filters.decoration" :placeholder="t('allTypes')" clearable style="width:130px">
            <el-option v-for="d in ['Unfinished','Simple','Medium','Fine','Luxury']" :key="d" :label="d" :value="d" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('orientation')">
          <el-select v-model="filters.orientation" :placeholder="t('allDirections')" clearable style="width:140px">
            <el-option v-for="o in ['South','North-South','Southeast','Southwest','East','West','North']" :key="o" :label="o" :value="o" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-input v-model="filters.keyword" :placeholder="t('searchCommunity')" clearable style="width:200px">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="search" :loading="loading">
            <el-icon><Search /></el-icon> Search
          </el-button>
          <el-button @click="reset" class="glass-btn">
            <el-icon><RefreshLeft /></el-icon> Reset
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="section-card">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
        <div style="color:var(--text-muted);font-size:14px;">
          {{ t('found') }} <strong style="color:#c8cdd5;">{{ total.toLocaleString() }}</strong> {{ t('matchingListings') }}
          <span v-if="activeFiltersCount > 0" style="color:var(--accent-cyan);margin-left:8px;">
            · {{ activeFiltersCount }} {{ t('activeFilter') }}{{ activeFiltersCount > 1 ? 's' : '' }}
          </span>
        </div>
        <el-tag size="small" effect="dark" type="info">{{ t('page') }} {{ pagination.page }} {{ t('of') }} {{ totalPages }}</el-tag>
      </div>

      <el-table :data="listings" stripe border v-loading="loading" max-height="560" size="small" class="listing-table">
        <el-table-column prop="community_name" :label="t('community')" width="195" fixed>
          <template #default="{ row }">
            <span style="font-weight:600;color:#c8cdd5;">{{ row.community_name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="district" :label="t('district')" width="115" sortable />
        <el-table-column prop="sub_district" :label="t('subDistrict')" width="130" sortable />
        <el-table-column prop="total_price" :label="t('totalPrice')" width="130" sortable>
          <template #default="{ row }">
            <span style="font-weight:600;color:var(--accent-cyan);">{{ row.total_price }}</span>
            <span style="color:var(--text-muted);font-size:11px;margin-left:3px;">(10k RMB)</span>
          </template>
        </el-table-column>
        <el-table-column prop="unit_price" :label="t('unitPrice')" width="160" sortable>
          <template #default="{ row }">{{ row.unit_price?.toLocaleString() }}</template>
        </el-table-column>
        <el-table-column prop="floor_area" :label="t('area')" width="100" sortable />
        <el-table-column prop="layout" :label="t('layout')" width="100" sortable>
          <template #default="{ row }">
            <el-tag size="small" effect="dark" :type="layoutTagType(row.layout)">{{ row.layout }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="floor" :label="t('floorLevel')" width="115" />
        <el-table-column prop="orientation" :label="t('orientation')" width="110" />
        <el-table-column prop="decoration" :label="t('decoration')" width="110">
          <template #default="{ row }">
            <el-tag size="small" effect="dark" :type="decorTagType(row.decoration)">{{ row.decoration }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="building_age" :label="t('ageYears')" width="100" sortable>
          <template #default="{ row }">
            <span :style="{color: row.building_age <= 5 ? '#67C23A' : row.building_age <= 15 ? '#E6A23C' : '#F56C6C'}">
              {{ row.building_age }}
            </span>
          </template>
        </el-table-column>
        <el-table-column :label="t('nearSubway')" width="105">
          <template #default="{ row }">
            <el-tag :type="row.near_subway ? 'success' : 'info'" size="small" effect="dark">
              {{ row.near_subway ? '✓ Yes' : '✗ No' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="listing_time" :label="t('listed')" width="105" sortable />
        <el-table-column :label="t('source')" width="65" fixed="right">
          <template #default="{ row }">
            <a v-if="row.listing_link" :href="row.listing_link" target="_blank" style="color:var(--accent-cyan);text-decoration:none;font-weight:600;">
              View →
            </a>
            <span v-else style="color:var(--text-muted)">—</span>
          </template>
        </el-table-column>
      </el-table>

      <div style="margin-top:18px;display:flex;justify-content:center;">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @size-change="search"
          @current-change="search"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { getListings, getDistricts, getLayouts } from '../api'
import { useI18n } from '../i18n'
const { t } = useI18n()

const listings = ref([])
const total = ref(0)
const loading = ref(false)
const districts = ref([])
const layouts = ref([])

const filters = reactive({
  district: '', layout: '', decoration: '', orientation: '', keyword: '',
  min_price: undefined, max_price: undefined,
  min_area: undefined, max_area: undefined,
})

const pagination = reactive({ page: 1, pageSize: 20 })

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pagination.pageSize)))
const activeFiltersCount = computed(() => {
  return Object.values(filters).filter(v => v !== '' && v !== undefined && v !== null).length
})

function layoutTagType(layout) {
  const rooms = parseInt(layout)
  if (rooms >= 5) return 'danger'
  if (rooms >= 4) return 'warning'
  if (rooms >= 3) return 'primary'
  return 'info'
}

function decorTagType(dec) {
  const map = { 'Luxury': 'danger', 'Fine': 'success', 'Medium': 'warning', 'Simple': 'info', 'Unfinished': 'info' }
  return map[dec] || 'info'
}

async function search() {
  loading.value = true
  try {
    const params = { page: pagination.page, page_size: pagination.pageSize }
    for (const [k, v] of Object.entries(filters)) {
      if (v !== '' && v !== undefined && v !== null && v !== 0) params[k] = v
    }
    const res = await getListings(params)
    if (res.data) {
      listings.value = res.data.data || []
      total.value = res.data.total || 0
    }
  } catch (e) {
    console.error('Search failed:', e)
    listings.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

function reset() {
  Object.assign(filters, {
    district: '', layout: '', decoration: '', orientation: '', keyword: '',
    min_price: undefined, max_price: undefined, min_area: undefined, max_area: undefined,
  })
  pagination.page = 1
  search()
}

onMounted(async () => {
  const [dRes, lRes] = await Promise.all([
    getDistricts().catch(() => ({ data: [] })),
    getLayouts().catch(() => ({ data: [] })),
  ])
  districts.value = dRes.data
  layouts.value = lRes.data
  search()
})
</script>

<style scoped>
.listing-table :deep(.el-table__body-wrapper) {
  scrollbar-width: thin;
}
</style>
