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
        
        <!-- 基础搜索 -->
        <div class="basic-search">
          <el-input
            v-model="searchForm.keyword"
            placeholder="输入材料名称、规格、编码等关键词"
            clearable
            size="large"
            :prefix-icon="Search"
            @keyup.enter="handleSearch"
            class="search-input"
          >
            <template #append>
              <el-button :icon="Search" @click="handleSearch">搜索</el-button>
            </template>
          </el-input>
        </div>

        <!-- 高级筛选 -->
        <el-collapse v-model="activeCollapse" class="filter-collapse">
          <el-collapse-item title="高级筛选" name="advanced">
            <el-form :model="searchForm" label-width="100px" class="filter-form">
              <el-row :gutter="20">
                <el-col :span="8">
                  <el-form-item label="材料分类">
                    <el-select v-model="searchForm.category" placeholder="选择分类" clearable>
                      <el-option label="建筑材料" value="building" />
                      <el-option label="装饰材料" value="decoration" />
                      <el-option label="机械设备" value="machinery" />
                      <el-option label="人工费" value="labor" />
                      <el-option label="其他" value="other" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="适用地区">
                    <el-select v-model="searchForm.region" placeholder="选择地区" clearable>
                      <el-option label="北京" value="beijing" />
                      <el-option label="上海" value="shanghai" />
                      <el-option label="广州" value="guangzhou" />
                      <el-option label="深圳" value="shenzhen" />
                      <el-option label="杭州" value="hangzhou" />
                      <el-option label="全国" value="national" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="价格范围">
                    <el-input-number
                      v-model="searchForm.priceMin"
                      placeholder="最低价"
                      :min="0"
                      :precision="2"
                      controls-position="right"
                    />
                    <span style="margin: 0 8px;">-</span>
                    <el-input-number
                      v-model="searchForm.priceMax"
                      placeholder="最高价"
                      :min="0"
                      :precision="2"
                      controls-position="right"
                    />
                  </el-form-item>
                </el-col>
              </el-row>
              
              <el-row :gutter="20">
                <el-col :span="8">
                  <el-form-item label="数据来源">
                    <el-select v-model="searchForm.source" placeholder="选择来源" clearable>
                      <el-option label="政府信息价" value="government" />
                      <el-option label="市场调研" value="market" />
                      <el-option label="供应商报价" value="supplier" />
                      <el-option label="历史数据" value="historical" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="生效时间">
                    <el-date-picker
                      v-model="searchForm.dateRange"
                      type="daterange"
                      range-separator="至"
                      start-placeholder="开始日期"
                      end-placeholder="结束日期"
                      format="YYYY-MM-DD"
                      value-format="YYYY-MM-DD"
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
      <div v-if="selectedMaterials.length > 0" class="batch-toolbar">
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
      </div>

      <!-- 结果表格 -->
      <el-table
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
        <el-table-column prop="effective_date" label="生效日期" width="110">
          <template #default="{ row }">
            {{ formatDate(row.effective_date) }}
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
      <div v-if="materials.length > 0" class="pagination-wrapper">
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
      <el-empty v-else-if="!loading" description="没有找到匹配的材料">
        <el-button type="primary" @click="resetFilters">清空筛选条件</el-button>
      </el-empty>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Search,
  Download,
  Refresh
} from '@element-plus/icons-vue'
import { formatDate, formatNumber } from '@/utils'
import { getBaseMaterials, updateBaseMaterial } from '@/api/materials'
import { ElMessageBox } from 'element-plus'

// 响应式数据
const loading = ref(false)
const activeCollapse = ref(['advanced'])
const materials = ref([])
const selectedMaterials = ref([])
const tableRef = ref()

// 搜索表单
const searchForm = reactive({
  keyword: '',
  category: '',
  region: '',
  priceMin: null,
  priceMax: null,
  source: '',
  dateRange: null,
  verified: null
})

// 分页数据
const pagination = reactive({
  page: 1,
  size: 100,
  total: 0
})

// 搜索材料
const handleSearch = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.size,
      name: searchForm.keyword,
      category: searchForm.category,
      region: searchForm.region,
      price_min: searchForm.priceMin,
      price_max: searchForm.priceMax,
      is_verified: searchForm.verified
    }

    const response = await getBaseMaterials(params)
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

// 重置筛选
const resetFilters = () => {
  Object.assign(searchForm, {
    keyword: '',
    category: '',
    region: '',
    priceMin: null,
    priceMax: null,
    source: '',
    dateRange: null,
    verified: null
  })
  pagination.page = 1
  handleSearch()
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

// 初始化
onMounted(() => {
  handleSearch()
})
</script>

<style lang="scss" scoped>
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
      
      .search-input {
        max-width: 600px;
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