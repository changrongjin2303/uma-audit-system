<template>
  <div class="price-query-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">市场信息价查询</h1>
        <p class="page-subtitle">快速查询市场信息价材料信息，支持多种筛选条件和智能搜索</p>
      </div>
      <div class="header-actions">
        <el-button :icon="Download" @click="exportResults">
          导出结果
        </el-button>
        <el-button :icon="Refresh" @click="resetFilters">
          重置筛选
        </el-button>
      </div>
    </div>

    <!-- 查询筛选区域 -->
    <el-card class="search-card">
      <div class="search-section">
        <h3>查询条件</h3>
        
        <div class="basic-search" style="gap:12px;">
          <span style="color:#666;min-width:80px;">材料名称</span>
          <el-input
            v-model="searchForm.name"
            placeholder="材料名称"
            clearable
            size="large"
            :prefix-icon="Search"
            @keyup.enter="handleSearch"
            style="max-width: 300px;"
          />
          <div style="display:flex;align-items:center;gap:8px;">
            <span style="color:#666;min-width:80px;">规格型号</span>
            <el-select
              v-model="searchForm.specification"
              filterable
              allow-create
              default-first-option
              clearable
              placeholder="规格型号"
              :loading="loadingSpecs"
              size="large"
              style="width: 300px;"
            >
              <el-option
                v-for="spec in specOptions"
                :key="spec"
                :label="spec"
                :value="spec"
              />
              <template #empty>
                <div style="padding: 8px 12px; color: #909399;">暂无规格，可调整材料名称或点击“匹配型号”</div>
              </template>
            </el-select>
            <el-button :icon="Search" size="large" @click="fetchSpecOptions">匹配型号</el-button>
          </div>
          <el-button :icon="Search" size="large" @click="handleSearch">搜索</el-button>
          <el-button :icon="Refresh" class="reset-btn" size="large" @click="resetFilters">重置</el-button>
        </div>

        <!-- 高级筛选 -->
        <el-collapse v-model="activeCollapse" class="filter-collapse">
          <el-collapse-item title="高级筛选" name="advanced">
            <el-form :model="searchForm" label-width="100px" class="filter-form">
              <el-row :gutter="20">
                <el-col :span="8">
                  <el-form-item label="期刊类型">
                    <el-select v-model="searchForm.price_type" placeholder="选择期刊类型" clearable>
                      <el-option label="省刊" value="provincial" />
                      <el-option label="市刊" value="municipal" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="适用地区">
                    <el-select v-model="searchForm.region" placeholder="选择地区" clearable>
                      <el-option
                        v-for="region in availableRegions"
                        :key="region.value"
                        :label="region.label"
                        :value="region.value"
                      />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>
              
              <el-row :gutter="20">
                <el-col :span="8">
                  <el-form-item label="期数">
                    <el-date-picker
                      v-model="searchForm.price_date"
                      type="month"
                      placeholder="选择期数"
                      value-format="YYYY-MM"
                      style="width: 100%"
                      clearable
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="是否收藏">
                    <el-radio-group v-model="searchForm.verified" @change="handleFilterChange">
                      <el-radio :label="null">全部</el-radio>
                      <el-radio :label="true">已收藏</el-radio>
                      <el-radio :label="false">未收藏</el-radio>
                    </el-radio-group>
                  </el-form-item>
                </el-col>
              </el-row>
            </el-form>
          </el-collapse-item>
        </el-collapse>
      </div>
    </el-card>

    <!-- 查询结果 -->
    <el-card class="results-card">
      <template #header>
        <div class="results-header">
          <span>查询结果</span>
          <div class="results-stats" v-if="materials.length > 0">
            <el-tag type="info">共找到 {{ pagination.total }} 条记录</el-tag>
          </div>
        </div>
      </template>

      <!-- 批量操作工具栏 -->
      <div class="batch-toolbar">
        <el-radio-group v-model="viewMode" size="small" style="margin-right: 16px;">
            <el-radio-button label="grouped">按期数折叠</el-radio-button>
            <el-radio-button label="flat">平铺列表</el-radio-button>
        </el-radio-group>

        <template v-if="selectedMaterials.length > 0">
          <el-tag type="info">已选择 {{ selectedMaterials.length }} 项</el-tag>
          <el-button type="success" size="small" @click="batchFavorite(true)">
            批量收藏
          </el-button>
          <el-button type="warning" size="small" @click="batchFavorite(false)">
            批量取消收藏
          </el-button>
          <el-button type="info" size="small" @click="clearSelection">
            清空选择
          </el-button>
        </template>
      </div>

      <!-- 期数分组表格 -->
      <el-table
        v-if="viewMode === 'grouped'"
        ref="periodTableRef"
        v-loading="loading"
        :data="filteredPeriods"
        style="width: 100%"
        class="periods-table"
        max-height="500"
        :row-key="(row) => `${row.price_date}-${row.region}-${row.price_type}`"
      >
        <el-table-column type="expand">
            <template #default="{ row }">
                <div class="expanded-table-container">
                    <period-material-query-list 
                        :period="row" 
                        @view="viewDetail"
                    />
                </div>
            </template>
        </el-table-column>
        <el-table-column prop="price_date" label="期数" min-width="220" sortable>
          <template #default="{ row }">
            <span class="period-cell">{{ getPeriodText(row) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="region" label="地区" min-width="280">
          <template #default="{ row }">
            <span class="region-cell">{{ getApplicableRegionText(row) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="price_type" label="类型" min-width="200">
          <template #default="{ row }">
            <el-tag :type="getJournalType(row)" size="default">
              {{ getJournalText(row) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="count" label="材料数量" min-width="200" sortable>
          <template #default="{ row }">
            <el-tag type="info" size="default">{{ row.count }} 条</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button type="primary" link size="small" @click="expandPeriodRow(row)">
                展开
              </el-button>
              <el-button type="success" link size="small" @click="viewPeriodAsFlat(row)">
                查看列表
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 结果表格 -->
      <el-table
        v-else
        ref="tableRef"
        v-loading="loading"
        :data="materials"
        stripe
        style="width: 100%"
        max-height="500"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="material_code" label="编码" width="120" />
        <el-table-column prop="name" label="材料名称" min-width="200" show-overflow-tooltip />
        <el-table-column prop="specification" label="规格型号" width="150" show-overflow-tooltip />
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column prop="price_excluding_tax" label="除税价格" width="120">
          <template #default="{ row }">
            ¥{{ formatNumber(row.price_excluding_tax || row.price || 0) }}
          </template>
        </el-table-column>
        <el-table-column prop="price_including_tax" label="含税价格" width="120">
          <template #default="{ row }">
            ¥{{ formatNumber(row.price_including_tax || (row.price * 1.13) || 0) }}
          </template>
        </el-table-column>
        <el-table-column prop="region" label="适用地区" width="100">
          <template #default="{ row }">
            {{ getRegionText(row.region) }}
          </template>
        </el-table-column>
        <el-table-column prop="issue_period" label="期数" width="110">
          <template #default="{ row }">
            {{ getPeriodText(row) }}
          </template>
        </el-table-column>
        <el-table-column prop="is_verified" label="收藏状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_verified ? 'success' : 'info'" size="small">
              {{ row.is_verified ? '已收藏' : '未收藏' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewDetail(row)">
              查看
            </el-button>
            <el-button 
              :type="row.is_verified ? 'warning' : 'success'" 
              link 
              size="small" 
              @click="toggleFavorite(row)"
            >
              {{ row.is_verified ? '取消收藏' : '收藏' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div v-if="viewMode === 'flat' && materials.length > 0" class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          background
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>

      <!-- 空状态 -->
      <el-empty v-else-if="!loading && ((viewMode === 'flat' && materials.length === 0) || (viewMode === 'grouped' && filteredPeriods.length === 0))" description="没有找到匹配的材料">
        <el-button type="primary" @click="resetFilters">清空筛选条件</el-button>
      </el-empty>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Search,
  Download,
  Refresh
} from '@element-plus/icons-vue'
import { formatDate, formatNumber } from '@/utils'
import { getBaseMaterials, updateBaseMaterial, getRegions, searchSimilarBaseMaterials, getMaterialPeriods } from '@/api/materials'
import { ElMessageBox } from 'element-plus'
import PeriodMaterialQueryList from './components/PeriodMaterialQueryList.vue'

// 响应式数据
const viewMode = ref('grouped') // 'grouped' | 'flat'
const periods = ref([])
const filteredPeriods = computed(() => {
  return periods.value.filter(p => {
    if (searchForm.price_type && p.price_type !== searchForm.price_type) return false
    
    if (searchForm.region) {
       const match = p.region === searchForm.region || 
                     p.province === searchForm.region || 
                     p.city === searchForm.region
       if (!match) return false
    }
    
    if (searchForm.price_date && p.price_date !== searchForm.price_date) return false
    
    return true
  })
})
const loading = ref(false)
const activeCollapse = ref(['advanced'])
const materials = ref([])
const selectedMaterials = ref([])
const tableRef = ref()
const periodTableRef = ref()

// 搜索表单
const searchForm = reactive({
  name: '',
  specification: '',
  price_type: '',
  region: '',
  price_date: '',
  verified: null
})

const availableRegions = ref([])

// 分页数据
const pagination = reactive({
  page: 1,
  size: 100,
  total: 0
})

// 搜索材料
const handleSearch = async () => {
  if ((searchForm.name && searchForm.name.trim()) || (searchForm.specification && searchForm.specification.trim())) {
     if (viewMode.value !== 'flat') {
       viewMode.value = 'flat'
     } else {
       fetchMaterials()
     }
     return
  }

  if (viewMode.value === 'grouped') {
    fetchPeriods()
  } else {
    fetchMaterials()
  }
}

const fetchMaterials = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.size,
      name: searchForm.name,
      specification: searchForm.specification,
      price_type: searchForm.price_type,
      region: searchForm.region,
      price_date: searchForm.price_date,
      is_verified: searchForm.verified
    }

    const response = await getBaseMaterials(params, { __skipLoading: true })
    const result = response.data?.data || response.data || response
    
    materials.value = result.items || result.materials || []
    pagination.total = result.total || 0
    
  } catch (error) {
    console.error('查询材料失败:', error)
    ElMessage.error('查询失败: ' + (error.message || error))
    materials.value = []
    pagination.total = 0
  } finally {
    loading.value = false
  }
}

const fetchPeriods = async () => {
  loading.value = true
  try {
    const res = await getMaterialPeriods()
    const data = res.data?.data || res.data || res
    // data可能是数组，也可能是{periods: [...]}格式
    periods.value = Array.isArray(data) ? data : (data.periods || [])
    console.log('获取到期数列表:', periods.value.length, '条')
  } catch (error) {
    console.error('获取期数列表失败', error)
    ElMessage.error('获取期数列表失败')
  } finally {
    loading.value = false
  }
}

// 重置筛选
const resetFilters = () => {
  Object.assign(searchForm, {
    name: '',
    specification: '',
    price_type: '',
    region: '',
    price_date: '',
    verified: null
  })
  specOptions.value = []
  pagination.page = 1
  
  if (viewMode.value === 'grouped') {
    fetchPeriods()
  } else {
    fetchMaterials()
  }
}

const fetchAvailableRegions = async (priceType = null) => {
  try {
    const resp = await getRegions(priceType)
    const regions = resp.data?.regions || resp.regions || []
    availableRegions.value = regions
      .filter(r => r && r.trim())
      .sort()
      .map(r => ({ label: getRegionText(r), value: r }))
  } catch (e) {
    availableRegions.value = []
  }
}

// 筛选条件改变时的处理
const handleFilterChange = () => {
  pagination.page = 1
  handleSearch()
}

// 导出结果
const exportResults = () => {
  ElMessage.info('导出功能开发中...')
}

// 获取期刊显示文本
const getJournalText = (row) => {
  // 优先使用price_type + province/city 字段构建期刊信息
  if (row.price_type && (row.province || row.city)) {
    const province = getProvinceText(row.province)
    const city = getCityText(row.city)

    if (row.price_type === 'provincial') {
      // 省刊：显示省份 + 省刊
      return `${province}省刊`
    } else if (row.price_type === 'municipal' && city) {
      // 市刊：显示城市 + 市刊
      return `${city}市刊`
    }
  }

  // 兼容旧数据：使用journal_type字段
  if (row.journal_type) {
    return row.journal_type
  }

  // 从category字段解析
  if (row.category) {
    const parts = row.category.split('-')
    if (parts.length >= 3) {
      const type = parts[0] === 'municipal' ? '市刊' : '省刊'
      return type
    }
  }

  return '-'
}

// 获取期刊标签类型
const getJournalType = (row) => {
  if (row.price_type === 'provincial') {
    return 'success'
  } else if (row.price_type === 'municipal') {
    return 'primary'
  }

  // 兼容旧数据
  if (row.journal_type && row.journal_type.includes('省')) {
    return 'success'
  }

  return 'primary'
}

// 获取适用地区文本
const getApplicableRegionText = (row) => {
  // 省刊显示省份名称
  if (row.price_type === 'provincial') {
    if (row.province) {
      return getProvinceText(row.province) + '省'
    }
    return '浙江省' // 默认显示浙江省
  }

  // 市刊显示具体适用地区
  if (row.price_type === 'municipal' && row.region) {
    return getRegionText(row.region)
  }

  // 兼容旧数据
  if (row.journal_type && row.journal_type.includes('省') && row.province) {
    return getProvinceText(row.province) + '省'
  }

  if (row.journal_type && row.journal_type.includes('市') && row.region) {
    return getRegionText(row.region)
  }

  return '-'
}

// 省份代码到中文的映射
const getProvinceText = (province) => {
  if (!province) return ''

  if (/[\u4e00-\u9fa5]/.test(province)) {
    return province.replace(/省$/, '') // 去掉末尾的"省"字
  }

  const provinceMap = {
    'zhejiang': '浙江',
    'jiangsu': '江苏',
    'guangdong': '广东',
    'shandong': '山东',
    'beijing': '北京',
    'shanghai': '上海',
    'tianjin': '天津',
    'chongqing': '重庆'
  }

  return provinceMap[province] || province
}

// 城市代码到中文的映射
const getCityText = (city) => {
  if (!city) return ''

  if (/[\u4e00-\u9fa5]/.test(city)) {
    return city.replace(/市$/, '') // 去掉末尾的"市"字
  }

  const cityMap = {
    'hangzhou': '杭州',
    'ningbo': '宁波',
    'wenzhou': '温州',
    'nanjing': '南京',
    'suzhou': '苏州',
    'wuxi': '无锡',
    'guangzhou': '广州',
    'shenzhen': '深圳',
    'beijing': '北京',
    'shanghai': '上海'
  }

  return cityMap[city] || city
}

// 地区代码到中文的映射
const getRegionText = (region) => {
  if (!region) return '-'

  // 如果已经是中文，直接返回
  if (/[\u4e00-\u9fa5]/.test(region)) {
    return region
  }

  // 英文代码到中文的映射
  const textMap = {
    'beijing': '北京市',
    'shanghai': '上海市',
    'guangzhou': '广州市',
    'shenzhen': '深圳市',
    'hangzhou': '杭州市',
    'nanjing': '南京市',
    'suzhou': '苏州市',
    'wuxi': '无锡市',
    'national': '全国',
    'zhejiang': '浙江省',
    'jiangsu': '江苏省',
    'guangdong': '广东省',
    'shandong': '山东省',
    'tianjin': '天津市',
    'chongqing': '重庆市',
    'sichuan': '四川省',
    'hunan': '湖南省',
    'hubei': '湖北省',
    'henan': '河南省',
    'anhui': '安徽省',
    'fujian': '福建省',
    'jiangxi': '江西省',
    'liaoning': '辽宁省',
    'jilin': '吉林省',
    'heilongjiang': '黑龙江省',
    'shanxi': '山西省',
    'shaanxi': '陕西省',
    'hebei': '河北省',
    'yunnan': '云南省',
    'guizhou': '贵州省',
    'hainan': '海南省',
    'gansu': '甘肃省',
    'qinghai': '青海省',
    'xinjiang': '新疆维吾尔自治区',
    'ningxia': '宁夏回族自治区',
    'guangxi': '广西壮族自治区',
    'neimenggu': '内蒙古自治区',
    'xizang': '西藏自治区'
  }

  return textMap[region.toLowerCase()] || region
}

// 查看详情
const viewDetail = (material) => {
  ElMessage.info(`查看材料详情: ${material.name}`)
}

// 选择变化处理
const handleSelectionChange = (selection) => {
  selectedMaterials.value = selection
}

// 清空选择
const clearSelection = () => {
  tableRef.value?.clearSelection()
  selectedMaterials.value = []
}

// 切换收藏状态
const toggleFavorite = async (material) => {
  try {
    const isCurrentlyFavorite = material.is_verified
    const newFavoriteStatus = !isCurrentlyFavorite
    
    // 更新材料收藏状态
    await updateBaseMaterial(material.id, {
      is_verified: newFavoriteStatus
    })
    
    // 更新本地数据
    material.is_verified = newFavoriteStatus
    
    if (newFavoriteStatus) {
      ElMessage.success(`材料 "${material.name}" 已添加到收藏`)
    } else {
      ElMessage.success(`材料 "${material.name}" 已取消收藏`)
    }
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error('操作失败: ' + (error.message || '未知错误'))
  }
}

// 批量收藏/取消收藏
const batchFavorite = async (favorite) => {
  if (selectedMaterials.value.length === 0) {
    ElMessage.warning('请先选择要操作的材料')
    return
  }

  try {
    const action = favorite ? '收藏' : '取消收藏'
    await ElMessageBox.confirm(
      `确定要${action}选中的 ${selectedMaterials.value.length} 个材料吗？`,
      `批量${action}`,
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    loading.value = true
    const materialIds = selectedMaterials.value.map(m => m.id)
    
    // 批量更新
    const updatePromises = materialIds.map(id => 
      updateBaseMaterial(id, { is_verified: favorite })
    )
    
    await Promise.all(updatePromises)
    
    // 更新本地数据
    selectedMaterials.value.forEach(material => {
      material.is_verified = favorite
    })
    
    // 清空选择
    clearSelection()
    
    ElMessage.success(`成功${action} ${materialIds.length} 个材料`)
    
    // 如果当前筛选的是收藏状态，刷新数据
    if (searchForm.verified !== null) {
      handleSearch()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量操作失败:', error)
      ElMessage.error('批量操作失败: ' + (error.message || '未知错误'))
    }
  } finally {
    loading.value = false
  }
}

// 分页处理
const handleSizeChange = (size) => {
  pagination.size = size
  pagination.page = 1
  handleSearch()
}

const handlePageChange = (page) => {
  pagination.page = page
  handleSearch()
}

const expandPeriodRow = (row) => {
  if (periodTableRef.value) {
    periodTableRef.value.toggleRowExpansion(row, true)
  }
}

const viewPeriodAsFlat = (row) => {
  searchForm.price_type = row.price_type || ''
  const regionValue = row.price_type === 'provincial'
    ? (row.province || row.region || '')
    : (row.region || row.city || '')
  searchForm.region = regionValue
  searchForm.price_date = row.price_date && row.price_date !== 'None' ? row.price_date : ''
  pagination.page = 1
  const switched = viewMode.value !== 'flat'
  if (switched) {
    viewMode.value = 'flat'
  } else {
    fetchMaterials()
  }
}

// 初始化
onMounted(() => {
  fetchAvailableRegions()
  if (viewMode.value === 'grouped') {
    fetchPeriods()
  } else {
    fetchMaterials()
  }
})

watch(viewMode, (newMode) => {
  if (newMode === 'grouped') {
    fetchPeriods()
  } else {
    fetchMaterials()
  }
})

watch(() => searchForm.price_type, async (newType) => {
  searchForm.region = ''
  await fetchAvailableRegions(newType)
})

const getPeriodText = (row) => {
  if (row.price_date) {
    const parts = String(row.price_date).split('-')
    const year = parts[0]
    const month = parts[1] ? parts[1].padStart(2, '0') : ''
    return year && month ? `${year}年${month}月` : row.price_date
  }
  if (row.issue_period) return row.issue_period
  return '-'
}

// 规格候选逻辑
const specOptions = ref([])
const loadingSpecs = ref(false)
let specTimer = null

const fetchSpecOptions = async () => {
  loadingSpecs.value = true
  try {
    const resp = await getBaseMaterials({
      page: 1,
      page_size: 200,
      name: searchForm.name,
      price_type: searchForm.price_type,
      region: searchForm.region,
      price_date: searchForm.price_date,
      _t: Date.now()
    }, { __skipLoading: true })
    const result = resp.data?.data || resp.data || resp
    const items = result.items || result.materials || []
    const set = new Set()
    items.forEach(i => { if (i.specification) set.add(i.specification) })
    specOptions.value = Array.from(set)

    if (specOptions.value.length === 0 && searchForm.name && searchForm.name.trim()) {
      const similarResp = await searchSimilarBaseMaterials(searchForm.name, 50)
      const similar = similarResp.data || similarResp
      const list = Array.isArray(similar) ? similar : (similar.items || [])
      const set2 = new Set(specOptions.value)
      list.forEach(i => { if (i.specification) set2.add(i.specification) })
      specOptions.value = Array.from(set2)
    }
  } catch (e) {
    specOptions.value = []
  } finally {
    loadingSpecs.value = false
  }
}

watch(() => searchForm.name, (nv) => {
  if (specTimer) {
    clearTimeout(specTimer)
  }
  specTimer = setTimeout(() => {
    if (nv && nv.trim()) {
      fetchSpecOptions()
    } else {
      specOptions.value = []
      searchForm.specification = ''
    }
  }, 300)
})
</script>

<style lang="scss" scoped>
.expanded-table-container {
    padding: 10px 20px;
    background-color: #f8f9fa;
}

.price-query-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 20px;

  .header-content {
    .page-title {
      font-size: 24px;
      font-weight: 600;
      color: $text-primary;
      margin: 0 0 8px 0;
    }

    .page-subtitle {
      font-size: 14px;
      color: $text-secondary;
      margin: 0;
    }
  }

  .header-actions {
    display: flex;
    gap: 12px;
  }
}

.search-card {
  margin-bottom: 20px;

  .search-section {
    h3 {
      margin-bottom: 16px;
      color: $text-primary;
    }

    .basic-search {
      margin-bottom: 20px;
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      gap: 12px 16px;
      
      .search-input {
        max-width: 600px;
      }

      .reset-btn {
        height: 40px;
        padding: 0 16px;
      }
    }

    .filter-collapse {
      .filter-form {
        .el-form-item {
          margin-bottom: 16px;
        }
      }
    }
  }
}

.results-card {
  .results-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .batch-toolbar {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 0;
    margin-bottom: 10px;
    border-bottom: 1px solid #ebeef5;
  }

  .pagination-wrapper {
    display: flex;
    justify-content: center;
    margin-top: 20px;
  }
}

.periods-table {
  .period-cell {
    font-weight: 600;
    font-size: 15px;
    color: #1f2d3d;
  }

  .region-cell {
    font-size: 14px;
    color: #606266;
  }

  .action-buttons {
    display: flex;
    gap: 8px;
  }
}

// 响应式设计
@media (max-width: $breakpoint-md) {
  .price-query-container {
    padding: 10px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;

    .header-actions {
      width: 100%;
      justify-content: flex-start;
    }
  }

  .basic-search {
    .search-input {
      max-width: 100%;
    }
  }

  .filter-form {
    .el-row {
      .el-col {
        margin-bottom: 16px;
      }
    }
  }
}
</style>
