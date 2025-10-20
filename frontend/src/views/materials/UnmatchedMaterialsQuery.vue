<template>
  <div class="price-query-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">无信息价查询</h1>
        <p class="page-subtitle">快速查询无信息价材料信息，支持多种筛选条件和智能搜索</p>
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
                  <el-form-item label="是否验证">
                    <el-radio-group v-model="searchForm.verified">
                      <el-radio :label="null">全部</el-radio>
                      <el-radio :label="true">已验证</el-radio>
                      <el-radio :label="false">未验证</el-radio>
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

      <!-- 结果表格 -->
      <el-table
        v-loading="loading"
        :data="materials"
        stripe
        style="width: 100%"
        max-height="500"
      >
        <el-table-column prop="serial_number" label="序号" width="120" />
        <el-table-column prop="name" label="材料名称" min-width="200" show-overflow-tooltip />
        <el-table-column prop="specification" label="规格型号" width="150" show-overflow-tooltip />
        <el-table-column prop="brand" label="品牌" width="120" show-overflow-tooltip>
          <template #default="{ row }">
            <span>{{ row.brand || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column prop="price_excluding_tax" label="价格（除税价）" width="140">
          <template #default="{ row }">
            <span v-if="row.price_excluding_tax">¥{{ formatNumber(row.price_excluding_tax) }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="date" label="日期" width="120">
          <template #default="{ row }">
            {{ row.date ? formatDate(row.date) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="is_verified" label="验证状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_verified ? 'success' : 'warning'" size="small">
              {{ row.is_verified ? '已验证' : '未验证' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewDetail(row)">
              查看
            </el-button>
            <el-button type="success" link size="small" @click="addToProject(row)">
              添加到项目
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
import { getUnmatchedMaterials } from '@/api/unmatchedMaterials'

// 响应式数据
const loading = ref(false)
const activeCollapse = ref(['advanced'])
const materials = ref([])

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
  size: 20,
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

    const response = await getUnmatchedMaterials(params)
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

// 导出结果
const exportResults = () => {
  ElMessage.info('导出功能开发中...')
}

// 查看详情
const viewDetail = (material) => {
  ElMessage.info(`查看材料详情: ${material.name}`)
}

// 添加到项目
const addToProject = (material) => {
  ElMessage.success(`材料 "${material.name}" 已添加到收藏`)
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