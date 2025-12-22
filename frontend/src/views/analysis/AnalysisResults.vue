<template>
  <div class="analysis-results-container">
    <!-- 页面标题和工具栏 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">价格分析结果</h1>
        <p class="page-subtitle">查看所有项目的AI价格分析结果和合理性评估报告</p>
      </div>
      <div class="header-actions">
        <el-button :icon="Refresh" @click="fetchProjects">
          刷新
        </el-button>
        <el-button
          type="primary"
          :icon="Document"
          @click="batchGenerateReports"
          :disabled="selectedProjects.length === 0"
        >
          批量生成报告
        </el-button>
      </div>
    </div>

    <!-- 项目统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon total">
            <el-icon><Box /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ projects.length }}</div>
            <div class="stat-label">项目总数</div>
          </div>
        </div>
      </el-col>

      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon analyzing">
            <el-icon><TrendCharts /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ totalAnalyzed }}</div>
            <div class="stat-label">已分析</div>
          </div>
        </div>
      </el-col>

      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon reasonable">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ totalReasonable }}</div>
            <div class="stat-label">价格合理</div>
          </div>
        </div>
      </el-col>

      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon risk">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ totalRisk }}</div>
            <div class="stat-label">存在风险</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 项目列表 - 表格展示 -->
    <el-card class="table-card">
      <!-- 搜索和筛选 -->
      <div class="table-toolbar">
        <div class="toolbar-left">
          <el-input
            v-model="searchKeyword"
            placeholder="请输入项目名称"
            clearable
            style="width: 250px;"
            :prefix-icon="Search"
            @input="handleSearch"
          />
        </div>
        <div class="toolbar-right">
          <el-tooltip content="刷新">
            <el-button :icon="Refresh" @click="fetchProjects" />
          </el-tooltip>
        </div>
      </div>

      <!-- 项目表格 -->
      <el-table
        v-loading="loading"
        :data="filteredProjects"
        stripe
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="name" label="项目名称" min-width="200">
          <template #default="{ row }">
            <div class="project-info">
              <el-link 
                type="primary" 
                :underline="false"
                @click="viewProjectDetails(row)"
                class="project-title"
              >
                {{ row.name }}
              </el-link>
              <div class="project-desc">{{ row.description || '暂无描述' }}</div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="project_type" label="项目类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getProjectTypeColor(row.project_type)" size="small">
              {{ getProjectTypeText(row.project_type) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="total_materials" label="总材料数" width="100">
          <template #default="{ row }">
            {{ row.total_materials || 0 }}
          </template>
        </el-table-column>
        
        <el-table-column prop="analysis_count" label="已分析" width="100">
          <template #default="{ row }">
            <span class="analyzed-count">{{ row.analysis_count }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="reasonable_count" label="价格合理" width="100">
          <template #default="{ row }">
            <span class="reasonable-count">{{ row.reasonable_count || 0 }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="risk_count" label="存在风险" width="100">
          <template #default="{ row }">
            <span class="risk-count">{{ row.risk_count || 0 }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="indeterminate_count" label="无法判定" width="120">
          <template #header>
            <span>无法判定</span>
            <el-tooltip content="已完成AI分析，但因缺少单价或AI未给出价格区间，无法判断合理性" placement="top">
              <el-icon style="vertical-align: middle; margin-left: 4px"><QuestionFilled /></el-icon>
            </el-tooltip>
          </template>
          <template #default="{ row }">
            <span class="indeterminate-count">{{ row.indeterminate_count || 0 }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="last_analyzed_at" label="最后分析时间" width="180">
          <template #default="{ row }">
            {{ row.last_analyzed_at ? formatDate(row.last_analyzed_at) : '-' }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              link
              size="small"
              :icon="View"
              @click="viewProjectDetails(row)"
            >
              查看详情
            </el-button>
            <el-button
              type="warning"
              link
              size="small"
              :icon="TrendCharts"
              @click="startProjectAnalysis(row)"
            >
              重新分析
            </el-button>
            <el-button
              type="success"
              link
              size="small"
              :icon="Document"
              @click="generateProjectReport(row)"
            >
              生成报告
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 空状态 -->
      <div v-if="projects.length === 0 && !loading" class="empty-state">
        <el-empty description="暂无项目有分析结果" :image-size="120">
          <el-button type="primary" @click="$router.push('/projects')">
            去创建项目
          </el-button>
        </el-empty>
      </div>
    </el-card>


    <!-- 分析详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      :title="`${currentResult?.material_name} - 分析详情`"
      width="800px"
      :close-on-click-modal="false"
    >
      <div v-if="currentResult" class="detail-content">
        <!-- 基本信息 -->
        <div class="detail-section">
          <h4>材料信息</h4>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="材料名称">{{ currentResult.material_name }}</el-descriptions-item>
            <el-descriptions-item label="规格型号">{{ currentResult.specification || '无' }}</el-descriptions-item>
            <el-descriptions-item label="单位">{{ currentResult.unit }}</el-descriptions-item>
            <el-descriptions-item label="项目单价">¥{{ formatNumber(currentResult.project_price) }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- AI分析结果 -->
        <div v-if="currentResult.analysis_status === 'completed'" class="detail-section">
          <h4>AI分析结果</h4>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="预测价格区间">
              ¥{{ formatNumber(currentResult.predicted_price_min) }} ~ 
              ¥{{ formatNumber(currentResult.predicted_price_max) }}
            </el-descriptions-item>
            <el-descriptions-item label="偏差率">
              <span :class="getDeviationClass(currentResult.deviation)">
                {{ currentResult.deviation >= 0 ? '+' : '' }}{{ currentResult.deviation }}%
              </span>
            </el-descriptions-item>
            <el-descriptions-item label="置信度">{{ currentResult.confidence }}%</el-descriptions-item>
            <el-descriptions-item label="风险等级">
              <el-tag :type="getRiskType(currentResult.risk_level)" size="small">
                {{ getRiskText(currentResult.risk_level) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="数据来源" :span="2">{{ currentResult.data_sources?.join(', ') || '未知' }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 风险因素 -->
        <div v-if="currentResult.risk_factors?.length > 0" class="detail-section">
          <h4>风险因素</h4>
          <ul class="risk-factors-list">
            <li v-for="factor in currentResult.risk_factors" :key="factor" class="risk-factor">
              <el-icon class="risk-icon"><Warning /></el-icon>
              {{ factor }}
            </li>
          </ul>
        </div>

        <!-- AI分析说明 -->
        <div v-if="currentResult.ai_explanation" class="detail-section">
          <h4>AI分析说明</h4>
          <div class="ai-explanation">
            {{ currentResult.ai_explanation }}
          </div>
        </div>

        <!-- 分析历史 -->
        <div class="detail-section">
          <h4>分析历史</h4>
          <el-timeline>
            <el-timeline-item
              v-for="history in analysisHistory"
              :key="history.id"
              :timestamp="formatDate(history.created_at)"
              placement="top"
            >
              <div class="history-item">
                <div class="history-action">{{ history.action }}</div>
                <div v-if="history.note" class="history-note">{{ history.note }}</div>
                <div class="history-user">操作人: {{ history.created_by_name }}</div>
              </div>
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
    </el-dialog>

    <!-- 调整结果对话框 -->
    <el-dialog
      v-model="showAdjustDialog"
      title="调整分析结果"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="adjustFormRef"
        :model="adjustForm"
        :rules="adjustRules"
        label-width="100px"
      >
        <el-form-item label="风险等级" prop="risk_level">
          <el-select v-model="adjustForm.risk_level" style="width: 100%">
            <el-option label="正常" value="normal" />
            <el-option label="低风险" value="low" />
            <el-option label="中风险" value="medium" />
            <el-option label="高风险" value="high" />
            <el-option label="极高风险" value="critical" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="调整原因" prop="adjustment_reason">
          <el-input
            v-model="adjustForm.adjustment_reason"
            type="textarea"
            :rows="4"
            placeholder="请说明调整的原因"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showAdjustDialog = false">取消</el-button>
        <el-button
          type="primary"
          :loading="adjusting"
          @click="handleAdjustSubmit"
        >
          确定调整
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  TrendCharts,
  Document,
  Box,
  CircleCheck,
  SuccessFilled,
  Warning,
  Refresh,
  View,
  Edit,
  Search,
  QuestionFilled
} from '@element-plus/icons-vue'
import { formatDate, formatNumber } from '@/utils'
import { getProjectAnalysisResults, getProjectAnalysisStatistics, getProjectsWithAnalysis } from '@/api/analysis'
import { generateReport } from '@/api/reports'

const router = useRouter()
const route = useRoute()

// 响应式数据
const loading = ref(false)
const adjusting = ref(false)
const showDetailDialog = ref(false)
const showAdjustDialog = ref(false)
const searchKeyword = ref('')

const projects = ref([])
const selectedProjects = ref([])
const currentResult = ref(null)
const analysisHistory = ref([])

// 调整表单
const adjustForm = reactive({
  risk_level: '',
  adjustment_reason: ''
})

const adjustRules = {
  risk_level: [
    { required: true, message: '请选择风险等级', trigger: 'change' }
  ],
  adjustment_reason: [
    { required: true, message: '请说明调整原因', trigger: 'blur' },
    { min: 10, message: '调整原因不能少于10个字符', trigger: 'blur' }
  ]
}

// 计算属性 - 项目排序（按最近分析时间倒序）
const sortedProjects = computed(() => {
  return [...projects.value].sort((a, b) => {
    // 优先按照分析数量排序，再按时间排序
    if (a.analysis_count !== b.analysis_count) {
      return b.analysis_count - a.analysis_count
    }
    // 时间排序
    const timeA = new Date(a.last_analyzed_at || 0)
    const timeB = new Date(b.last_analyzed_at || 0)
    return timeB - timeA
  })
})

// 计算属性 - 项目状态标签类型
const getAnalysisStatusType = (count) => {
  if (count === 0) return 'info'
  if (count <= 5) return 'warning'
  return 'success'
}

// 计算属性 - 总体统计
const totalAnalyzed = computed(() => {
  return projects.value.reduce((sum, project) => sum + (project.analysis_count || 0), 0)
})

const totalReasonable = computed(() => {
  return projects.value.reduce((sum, project) => sum + (project.reasonable_count || 0), 0)
})

const totalRisk = computed(() => {
  return projects.value.reduce((sum, project) => sum + (project.risk_count || 0), 0)
})

// 过滤项目列表
const filteredProjects = computed(() => {
  if (!searchKeyword.value) {
    return sortedProjects.value
  }
  return sortedProjects.value.filter(project => 
    project.name.toLowerCase().includes(searchKeyword.value.toLowerCase())
  )
})


// 获取有分析结果的项目列表
const fetchProjects = async () => {
  try {
    const response = await getProjectsWithAnalysis()
    
    if (response && response.projects) {
      projects.value = response.projects.map(project => ({
        id: project.id,
        name: project.name,
        description: project.description,
        project_type: project.project_type || 'other',
        analysis_count: project.analysis_count,
        total_materials: project.total_materials || 0,
        reasonable_count: project.reasonable_count || 0,
        risk_count: project.risk_count || 0,
        indeterminate_count: project.indeterminate_count || 0,
        failed_count: project.failed_count || 0,
        last_analyzed_at: project.last_analyzed_at
      }))
    } else {
      projects.value = []
    }
  } catch (error) {
    console.error('获取有分析结果的项目列表失败:', error)
    projects.value = []
    ElMessage.error('获取项目列表失败')
  }
}


// 查看项目详细分析结果 - 跳转到带项目ID的分析详情页
const viewProjectDetails = (project) => {
  const name = encodeURIComponent(project.name || '')
  router.push(`/analysis/details?project_id=${project.id}&project_name=${name}`)
}

// 开始项目分析
const startProjectAnalysis = async (project) => {
  try {
    await ElMessageBox.confirm(
      `确定要重新分析项目 "${project.name}" 的所有材料吗？这个过程可能需要较长时间。`,
      '重新分析确认',
      {
        confirmButtonText: '开始分析',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    ElMessage.info('分析已启动，请稍后查看结果')
    // TODO: 调用批量分析API
    
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('启动分析失败')
    }
  }
}

// 生成项目报告
const generateProjectReport = (project) => {
  router.push(`/reports/generate?project_id=${project.id}&type=analysis`)
}

// 搜索处理
const handleSearch = () => {
  // 搜索逻辑已通过计算属性filteredProjects实现
}

// 批量生成报告
const handleSelectionChange = (val) => {
  selectedProjects.value = val
}

const batchGenerateReports = async () => {
  if (selectedProjects.value.length === 0) {
    ElMessage.warning('请先选择要生成报告的项目')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要为选中的 ${selectedProjects.value.length} 个项目生成详细分析报告吗？`,
      '批量生成报告',
      {
        confirmButtonText: '确定生成',
        cancelButtonText: '取消',
        type: 'info'
      }
    )

    const loadingInstance = ElMessage.info({
      message: '正在批量生成报告，请稍候...',
      duration: 0
    })

    let successCount = 0
    let failCount = 0

    // 串行执行生成请求，避免后端压力过大
    for (const project of selectedProjects.value) {
      try {
        await generateReport({
          project_id: project.id,
          report_title: `${project.name} - 价格分析报告`,
          is_draft: true, // 使用草稿模式，先生成记录
          config: {
            report_type: "price_analysis",
            include_charts: true,
            include_detailed_analysis: true,
            include_recommendations: true,
            include_appendices: true
          }
        })
        successCount++
      } catch (error) {
        console.error(`项目 ${project.name} 报告生成失败:`, error)
        failCount++
      }
    }

    loadingInstance.close()

    if (failCount === 0) {
      ElMessage.success(`成功生成 ${successCount} 个报告记录，请前往报告列表查看和下载`)
    } else {
      ElMessage.warning(`报告生成完成：成功 ${successCount} 个，失败 ${failCount} 个`)
    }
    
    // 跳转到报告列表页查看结果
    router.push('/reports')
    
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量生成报告出错:', error)
      ElMessage.error('批量生成报告过程中发生错误')
    }
  }
}

// 项目类型相关方法
const getProjectTypeColor = (type) => {
  const colorMap = {
    'construction': 'primary',
    'renovation': 'success', 
    'municipal': 'warning',
    'other': 'info'
  }
  return colorMap[type] || 'info'
}

const getProjectTypeText = (type) => {
  const textMap = {
    'construction': '建筑工程',
    'renovation': '装修工程',
    'municipal': '市政工程', 
    'other': '其他'
  }
  return textMap[type] || '其他'
}

// 状态相关方法
const getStatusType = (status) => {
  const typeMap = {
    'completed': 'success',
    'processing': 'warning',
    'pending': 'info',
    'failed': 'danger'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    'completed': '已完成',
    'processing': '分析中',
    'pending': '待分析',
    'failed': '失败'
  }
  return textMap[status] || status
}

const getRiskType = (risk) => {
  const typeMap = {
    'normal': 'success',
    'low': 'warning',
    'medium': 'warning',
    'high': 'danger',
    'critical': 'danger',
    'severe': 'danger'
  }
  return typeMap[risk] || 'info'
}

const getRiskText = (risk) => {
  const textMap = {
    'normal': '正常',
    'low': '低风险',
    'medium': '中风险',
    'high': '高风险',
    'critical': '极高风险',
    'severe': '极高风险'
  }
  return textMap[risk] || risk
}

const getDeviationClass = (deviation) => {
  const v = Math.abs(deviation)
  if (v === 0) return 'deviation-normal'
  if (v <= 15) return 'deviation-warning'
  if (v <= 30) return 'deviation-warning'
  return 'deviation-danger'
}

const getConfidenceColor = (confidence) => {
  if (confidence >= 80) return '#67c23a'
  if (confidence >= 60) return '#e6a23c'
  return '#f56c6c'
}



// 生命周期
onMounted(async () => {
  loading.value = true
  try {
    await fetchProjects()
  } finally {
    loading.value = false
  }
})
</script>

<style lang="scss" scoped>
.analysis-results-container {
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
    align-items: center;
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

      &.total {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      }

      &.analyzing {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
      }

      &.reasonable {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
      }

      &.risk {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
      }
    }

    .stat-content {
      flex: 1;

      .stat-number {
        font-size: 24px;
        font-weight: 700;
        color: $text-primary;
        line-height: 1;
        margin-bottom: 4px;
      }

      .stat-label {
        font-size: 14px;
        color: $text-secondary;
      }
    }
  }
}

.table-card {
  .table-toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;

    .toolbar-left {
      display: flex;
      gap: 12px;
    }

    .toolbar-right {
      display: flex;
      gap: 8px;
    }
  }

  .project-info {
    .project-title {
      font-weight: 500;
      font-size: 14px;
      margin-bottom: 4px;
    }

    .project-desc {
      font-size: 12px;
      color: $text-secondary;
    }
  }

  .analyzed-count {
    color: $color-primary;
    font-weight: 600;
  }

  .reasonable-count {
    color: $color-success;
    font-weight: 600;
  }

  .risk-count {
    color: $color-danger;
    font-weight: 600;
  }

  .indeterminate-count {
    color: #909399;
    font-weight: 600;
  }

  .empty-state {
    text-align: center;
    padding: 40px;
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
      color: $text-primary;
    }

    .header-filters {
      display: flex;
      align-items: center;
    }
  }

  .batch-toolbar {
    margin-bottom: 16px;
  }

  .material-info {
    .material-name {
      font-weight: 500;
      color: $text-primary;
      margin-bottom: 2px;
    }

    .material-spec {
      font-size: 12px;
      color: $text-secondary;
    }
  }

  .price-range {
    .range-separator {
      margin: 0 4px;
      color: $text-secondary;
    }
  }

  .deviation-normal {
    color: $color-success;
  }

  .deviation-warning {
    color: $color-warning;
  }

  .deviation-danger {
    color: $color-danger;
  }

  .no-data {
    color: $text-placeholder;
  }

  .pagination-wrapper {
    display: flex;
    justify-content: center;
    margin-top: 20px;
  }
}

// 详情对话框样式
.detail-content {
  .detail-section {
    margin-bottom: 24px;

    &:last-child {
      margin-bottom: 0;
    }

    h4 {
      font-size: 16px;
      font-weight: 600;
      color: $text-primary;
      margin: 0 0 12px 0;
    }

    .risk-factors-list {
      list-style: none;
      padding: 0;
      margin: 0;

      .risk-factor {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 0;
        border-bottom: 1px solid $border-color-lighter;

        &:last-child {
          border-bottom: none;
        }

        .risk-icon {
          color: $color-warning;
        }
      }
    }

    .ai-explanation {
      padding: 16px;
      background-color: $bg-color-base;
      border-radius: 8px;
      line-height: 1.6;
      color: $text-regular;
    }

    .history-item {
      .history-action {
        font-weight: 500;
        color: $text-primary;
        margin-bottom: 4px;
      }

      .history-note {
        font-size: 14px;
        color: $text-secondary;
        margin-bottom: 4px;
      }

      .history-user {
        font-size: 12px;
        color: $text-placeholder;
      }
    }
  }
}

// 响应式设计
@media (max-width: $breakpoint-md) {
  .analysis-results-container {
    padding: 10px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;

    .header-actions {
      width: 100%;
      flex-wrap: wrap;
      gap: 8px;

      .el-select {
        width: 150px !important;
      }
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

  .table-toolbar {
    flex-direction: column;
    gap: 12px !important;

    .toolbar-left,
    .toolbar-right {
      width: 100%;
      justify-content: flex-start;
    }
  }

  .card-header {
    flex-direction: column;
    gap: 12px !important;
    align-items: flex-start !important;

    .header-filters {
      width: 100%;
      flex-wrap: wrap;
      gap: 8px;

      .el-select {
        width: 100px !important;
      }
    }
  }
}
</style>
