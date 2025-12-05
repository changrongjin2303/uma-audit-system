<template>
  <div class="priced-material-analysis-container">
    <div v-loading="loading" class="analysis-content">
      <!-- 页面标题 -->
      <div class="page-header">
        <div class="header-content">
          <h1 class="page-title">
            <el-icon><TrendCharts /></el-icon>
            市场信息价材料分析结果
          </h1>
          <p v-if="projectName" class="page-subtitle">
            项目：{{ projectName }}
          </p>
        </div>
        <div class="header-actions">
          <el-button @click="$router.back()">
            返回
          </el-button>
          <el-button 
            type="primary" 
            :icon="Refresh" 
            @click="refreshData"
            :loading="loading"
          >
            刷新数据
          </el-button>
        </div>
      </div>

      <!-- 统计卡片 -->
      <el-row :gutter="20" class="stats-row" v-if="summary">
        <el-col :xs="24" :sm="12" :lg="6">
          <div class="stat-card">
            <div class="stat-icon analyzed">
              <el-icon><DataBoard /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ summary.total_analyzed }}</div>
              <div class="stat-label">分析材料总数</div>
            </div>
          </div>
        </el-col>
        
        <el-col :xs="24" :sm="12" :lg="6">
          <div class="stat-card">
            <div class="stat-icon differences">
              <el-icon><Warning /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ summary.total_differences }}</div>
              <div class="stat-label">存在价格差异</div>
            </div>
          </div>
        </el-col>
        
        <el-col :xs="24" :sm="12" :lg="6">
          <div class="stat-card">
            <div class="stat-icon rate">
              <el-icon><TrendCharts /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ (summary.difference_rate * 100).toFixed(1) }}%</div>
              <div class="stat-label">差异比例</div>
            </div>
          </div>
        </el-col>
        
        <el-col :xs="24" :sm="12" :lg="6">
          <div class="stat-card">
            <div class="stat-icon amount">
              <el-icon><Money /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ formatCurrency(summary.total_difference_amount) }}</div>
              <div class="stat-label">总价差金额</div>
            </div>
          </div>
        </el-col>
      </el-row>

      <!-- 筛选工具栏 -->
      <el-card class="filter-card">
        <div class="filter-toolbar">
          <div class="filter-left">
            <el-button-group>
              <el-button
                :type="activeFilter === 'all' ? 'primary' : ''"
                @click="activeFilter = 'all'"
              >
                全部 ({{ filteredDifferences.length }})
              </el-button>
              <el-button
                :type="activeFilter === 'differences' ? 'primary' : ''"
                @click="activeFilter = 'differences'"
              >
                有差异 ({{ differencesCount }})
              </el-button>
              <el-button
                :type="activeFilter === 'normal' ? 'primary' : ''"
                @click="activeFilter = 'normal'"
              >
                无差异 ({{ normalCount }})
              </el-button>
            </el-button-group>
          </div>
          
          <div class="filter-right">
            <el-select
              v-model="levelFilter"
              placeholder="选择风险等级"
              clearable
              style="width: 150px; margin-right: 12px;"
            >
              <el-option label="正常" value="normal" />
              <el-option label="低风险" value="low" />
              <el-option label="中风险" value="medium" />
              <el-option label="高风险" value="high" />
            </el-select>
            
            <el-input
              v-model="searchKeyword"
              placeholder="搜索材料名称"
              :prefix-icon="Search"
              style="width: 200px;"
              clearable
            />
          </div>
        </div>
      </el-card>

      <!-- 分析结果表格 -->
      <el-card class="results-card">
        <template #header>
          <div class="card-header">
            <span class="card-title">价格差异分析详情</span>
            <div class="header-actions">
              <el-button 
                :icon="Download" 
                @click="exportResults"
                :disabled="filteredDifferences.length === 0"
              >
                导出结果
              </el-button>
            </div>
          </div>
        </template>

        <el-table
          v-loading="tableLoading"
          :data="paginatedDifferences"
          stripe
          style="width: 100%"
          :default-sort="{ prop: 'price_difference_rate', order: 'descending' }"
        >
          <el-table-column prop="material_name" label="材料名称" min-width="200" />
          <el-table-column prop="specification" label="规格型号" width="150">
            <template #default="{ row }">
              {{ row.specification || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="unit" label="单位" width="80" />
          <el-table-column prop="quantity" label="数量" width="100">
            <template #default="{ row }">
              {{ formatNumber(row.quantity) }}
            </template>
          </el-table-column>
          <el-table-column prop="project_unit_price" label="项目单价" width="120">
            <template #default="{ row }">
              ¥{{ formatNumber(row.project_unit_price) }}
            </template>
          </el-table-column>
          <el-table-column prop="base_unit_price" label="基准单价" width="120">
            <template #default="{ row }">
              ¥{{ formatNumber(row.base_unit_price) }}
            </template>
          </el-table-column>
          <el-table-column prop="unit_price_difference" label="单价差" width="120" sortable>
            <template #default="{ row }">
              <span :class="getPriceDifferenceClass(row.unit_price_difference)">
                {{ row.unit_price_difference >= 0 ? '+' : '' }}¥{{ formatNumber(row.unit_price_difference) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="total_price_difference" label="合价差" width="140" sortable>
            <template #default="{ row }">
              <span :class="getPriceDifferenceClass(row.total_price_difference)">
                {{ row.total_price_difference >= 0 ? '+' : '' }}¥{{ formatNumber(row.total_price_difference) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="price_difference_rate" label="差异率" width="100" sortable>
            <template #default="{ row }">
              <span :class="getPriceDifferenceClass(row.price_difference_rate)">
                {{ row.price_difference_rate >= 0 ? '+' : '' }}{{ (row.price_difference_rate * 100).toFixed(2) }}%
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="difference_level" label="风险等级" width="120">
            <template #default="{ row }">
              <el-tag :type="getDifferenceLevelType(row.difference_level)" size="small">
                {{ getDifferenceLevelText(row.difference_level) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button
                type="primary"
                link
                size="small"
                @click="viewMaterialDetail(row)"
              >
                详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination-wrapper">
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.size"
            :page-sizes="[20, 50, 100]"
            :total="filteredDifferences.length"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
          />
        </div>
      </el-card>
    </div>

    <!-- 空状态 -->
    <el-empty v-if="!loading && differences.length === 0" description="暂无分析数据">
      <el-button type="primary" @click="$router.back()">
        返回项目
      </el-button>
    </el-empty>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  TrendCharts,
  Refresh,
  DataBoard,
  Warning,
  Money,
  Search,
  Download
} from '@element-plus/icons-vue'
import { formatNumber } from '@/utils'
import { getProjectPricedMaterialsAnalysis } from '@/api/analysis'

const route = useRoute()
const router = useRouter()

// 响应式数据
const loading = ref(false)
const tableLoading = ref(false)
const differences = ref([])
const summary = ref(null)
const projectName = ref('')
const activeFilter = ref('all')
const levelFilter = ref('')
const searchKeyword = ref('')

// 分页数据
const pagination = reactive({
  page: 1,
  size: 20
})

// 计算属性
const filteredDifferences = computed(() => {
  let filtered = differences.value

  // 按筛选条件过滤
  if (activeFilter.value === 'differences') {
    filtered = filtered.filter(item => item.has_difference)
  } else if (activeFilter.value === 'normal') {
    filtered = filtered.filter(item => !item.has_difference)
  }

  // 按差异等级过滤
  if (levelFilter.value) {
    filtered = filtered.filter(item => item.difference_level === levelFilter.value)
  }

  // 按关键词搜索
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(item =>
      item.material_name.toLowerCase().includes(keyword) ||
      (item.specification && item.specification.toLowerCase().includes(keyword))
    )
  }

  return filtered
})

const paginatedDifferences = computed(() => {
  const start = (pagination.page - 1) * pagination.size
  const end = start + pagination.size
  return filteredDifferences.value.slice(start, end)
})

const differencesCount = computed(() => {
  return differences.value.filter(item => item.has_difference).length
})

const normalCount = computed(() => {
  return differences.value.filter(item => !item.has_difference).length
})

// 方法
const fetchAnalysisResults = async () => {
  // 尝试多种方式获取项目ID
  const projectId = route.query.project_id || route.params.id || route.params.project_id
  
  console.log('获取项目ID:', {
    query: route.query,
    params: route.params,
    projectId
  })
  
  if (!projectId || projectId === 'undefined') {
    ElMessage.error('缺少项目ID参数')
    console.error('路由参数错误:', { query: route.query, params: route.params })
    router.back()
    return
  }

  loading.value = true
  try {
    // 调用真实API获取项目的市场信息价分析结果
    const response = await getProjectPricedMaterialsAnalysis(projectId, {
      skip: 0,
      limit: 1000  // 获取所有结果以便在前端进行筛选和统计
    })
    
    console.log('原始API响应:', response)
    
    // 转换API返回的数据格式为前端需要的格式
    const analysisResults = response.results || []
    differences.value = analysisResults.map(item => {
      return {
        material_id: item.material_id,
        material_name: item.material_name || '未知材料',
        specification: item.specification || '',
        unit: item.unit || '',
        quantity: parseFloat(item.quantity || 0),
        project_unit_price: parseFloat(item.project_unit_price || 0),
        base_unit_price: parseFloat(item.base_unit_price || 0),
        unit_price_difference: parseFloat(item.unit_price_difference || 0),
        total_price_difference: parseFloat(item.total_price_difference || 0),
        price_difference_rate: parseFloat(item.price_difference_rate || 0),
        has_difference: Boolean(item.has_difference),
        difference_level: item.difference_level || 'normal',
        base_material_name: item.base_material_name || '',
        analysis_status: 'completed' // 既然能获取到结果，说明分析已完成
      }
    })
    
    // 生成统计摘要
    const totalAnalyzed = differences.value.length
    const totalDifferences = differences.value.filter(d => d.has_difference).length
    const totalDifferenceAmount = differences.value.reduce((sum, d) => sum + (d.total_price_difference || 0), 0)
    
    summary.value = {
      total_analyzed: totalAnalyzed,
      total_differences: totalDifferences,
      difference_rate: totalAnalyzed > 0 ? totalDifferences / totalAnalyzed : 0,
      total_difference_amount: totalDifferenceAmount,
      level_distribution: {
        normal: differences.value.filter(d => d.difference_level === 'normal').length,
        low: differences.value.filter(d => d.difference_level === 'low').length,
        medium: differences.value.filter(d => d.difference_level === 'medium').length,
        high: differences.value.filter(d => d.difference_level === 'high').length
      }
    }
    
    projectName.value = route.query.project_name || '未知项目'

    console.log('获取市场信息价材料分析结果:', { 
      differences: differences.value.length, 
      sampleDifference: differences.value[0],
      summary: summary.value,
      filteredCount: filteredDifferences.value.length,
      paginatedCount: paginatedDifferences.value.length,
      loading: loading.value
    })
  } catch (error) {
    console.error('获取分析结果失败:', error)
    ElMessage.error('获取分析结果失败: ' + (error.message || '未知错误'))
    
    // 如果API调用失败，回退到空数据
    differences.value = []
    summary.value = {
      total_analyzed: 0,
      total_differences: 0,
      difference_rate: 0,
      total_difference_amount: 0,
      level_distribution: { normal: 0, low: 0, medium: 0, high: 0 }
    }
  } finally {
    loading.value = false
  }
}

// 生成模拟数据的函数
const generateMockData = async () => {
  // 模拟一些市场信息价材料分析数据
  const mockDifferences = [
    {
      material_id: 1,
      material_name: "商品混凝土C30",
      specification: "泵送，石子粒径16-31.5mm",
      unit: "m³",
      quantity: 120.5,
      project_unit_price: 285.00,
      base_unit_price: 265.00,
      unit_price_difference: 20.00,
      total_price_difference: 2410.00,
      price_difference_rate: 0.0755,
      has_difference: true,
      difference_level: "low",
      base_material_name: "商品混凝土C30（信息价）",
      analysis_status: "completed"
    },
    {
      material_id: 2,
      material_name: "钢筋HRB400",
      specification: "Φ12",
      unit: "t",
      quantity: 5.2,
      project_unit_price: 4850.00,
      base_unit_price: 4680.00,
      unit_price_difference: 170.00,
      total_price_difference: 884.00,
      price_difference_rate: 0.0363,
      has_difference: false,
      difference_level: "normal",
      base_material_name: "热轧带肋钢筋HRB400（信息价）",
      analysis_status: "completed"
    },
    {
      material_id: 3,
      material_name: "红砖",
      specification: "240×115×53mm",
      unit: "千块",
      quantity: 15.8,
      project_unit_price: 580.00,
      base_unit_price: 420.00,
      unit_price_difference: 160.00,
      total_price_difference: 2528.00,
      price_difference_rate: 0.3810,
      has_difference: true,
      difference_level: "high",
      base_material_name: "烧结普通砖（信息价）",
      analysis_status: "completed"
    }
  ]

  const mockSummary = {
    total_analyzed: mockDifferences.length,
    total_differences: mockDifferences.filter(d => d.has_difference).length,
    difference_rate: mockDifferences.filter(d => d.has_difference).length / mockDifferences.length,
    total_difference_amount: mockDifferences.reduce((sum, d) => sum + d.total_price_difference, 0),
    level_distribution: {
      normal: mockDifferences.filter(d => d.difference_level === 'normal').length,
      low: mockDifferences.filter(d => d.difference_level === 'low').length,
      medium: mockDifferences.filter(d => d.difference_level === 'medium').length,
      high: mockDifferences.filter(d => d.difference_level === 'high').length
    }
  }

  return {
    differences: mockDifferences,
    summary: mockSummary
  }
}

const refreshData = () => {
  fetchAnalysisResults()
}

const formatCurrency = (amount) => {
  if (amount >= 0) {
    return `+¥${formatNumber(amount)}`
  } else {
    return `-¥${formatNumber(Math.abs(amount))}`
  }
}

const getPriceDifferenceClass = (value) => {
  if (value > 0) return 'price-increase'
  if (value < 0) return 'price-decrease'
  return 'price-equal'
}

const getDifferenceLevelType = (level) => {
  const typeMap = {
    'normal': 'success',
    'low': 'warning',
    'medium': 'warning',
    'high': 'danger',
    'critical': 'danger',
    'severe': 'danger'
  }
  return typeMap[level] || 'info'
}

const getDifferenceLevelText = (level) => {
  const textMap = {
    'normal': '正常',
    'low': '低风险',
    'medium': '中风险',
    'high': '高风险',
    'critical': '严重风险',
    'severe': '严重风险'
  }
  return textMap[level] || level
}

const handleSizeChange = (size) => {
  pagination.size = size
  pagination.page = 1
}

const handlePageChange = (page) => {
  pagination.page = page
}

const viewMaterialDetail = (material) => {
  // 可以跳转到材料详情页面
  console.log('查看材料详情:', material)
  ElMessage.info('材料详情功能开发中')
}

const exportResults = () => {
  // 导出分析结果
  console.log('导出分析结果')
  ElMessage.info('导出功能开发中')
}

// 监听筛选条件变化，重置分页
watch([activeFilter, levelFilter, searchKeyword], () => {
  pagination.page = 1
})

// 生命周期
onMounted(() => {
  fetchAnalysisResults()
})
</script>

<style lang="scss" scoped>
.priced-material-analysis-container {
  padding: 20px;
  min-height: 100vh;
  background-color: #f5f6fa;
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
      color: #2c3e50;
      margin: 0 0 8px 0;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .page-subtitle {
      font-size: 14px;
      color: #7f8c8d;
      margin: 0;
    }
  }

  .header-actions {
    display: flex;
    gap: 12px;
  }
}

.stats-row {
  margin-bottom: 20px;

  .stat-card {
    background: white;
    border-radius: 8px;
    padding: 20px;
    display: flex;
    align-items: center;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    margin-bottom: 20px;

    .stat-icon {
      width: 50px;
      height: 50px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-right: 16px;
      font-size: 20px;
      color: white;

      &.analyzed {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      }

      &.differences {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
      }

      &.rate {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
      }

      &.amount {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
      }
    }

    .stat-content {
      flex: 1;

      .stat-number {
        font-size: 24px;
        font-weight: 700;
        color: #2c3e50;
        line-height: 1;
        margin-bottom: 4px;
      }

      .stat-label {
        font-size: 14px;
        color: #7f8c8d;
      }
    }
  }
}

.filter-card {
  margin-bottom: 20px;

  .filter-toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .filter-right {
      display: flex;
      align-items: center;
    }
  }
}

.results-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .card-title {
      font-size: 16px;
      font-weight: 600;
      color: #2c3e50;
    }
  }

  .pagination-wrapper {
    display: flex;
    justify-content: center;
    margin-top: 20px;
  }
}

// 价格差异样式
.price-increase {
  color: #e74c3c;
  font-weight: 600;
}

.price-decrease {
  color: #27ae60;
  font-weight: 600;
}

.price-equal {
  color: #7f8c8d;
}

// 响应式设计
@media (max-width: 768px) {
  .priced-material-analysis-container {
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

  .filter-toolbar {
    flex-direction: column;
    gap: 12px;
    align-items: stretch !important;

    .filter-right {
      justify-content: space-between;
    }
  }

  .stats-row {
    .stat-card {
      padding: 16px;

      .stat-icon {
        width: 40px;
        height: 40px;
        font-size: 18px;
      }

      .stat-content .stat-number {
        font-size: 20px;
      }
    }
  }
}
</style>