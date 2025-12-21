<template>
  <div class="reports-list-container">
    <!-- 页面标题和工具栏 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">价格分析报告管理</h1>
        <p class="page-subtitle">管理所有价格分析报告，支持生成、查看、下载和分享</p>
      </div>
      <div class="header-actions">
        <el-button 
          type="primary" 
          :icon="Plus" 
          @click="$router.push('/reports/generate')"
        >
          生成报告
        </el-button>
      </div>
    </div>

    <!-- 快速统计 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon total">
            <el-icon><Document /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ reportStats.total }}</div>
            <div class="stat-label">报告总数</div>
          </div>
        </div>
      </el-col>

      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon generating">
            <el-icon><Loading /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ reportStats.generating }}</div>
            <div class="stat-label">生成中</div>
          </div>
        </div>
      </el-col>

      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon completed">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ reportStats.completed }}</div>
            <div class="stat-label">已完成</div>
          </div>
        </div>
      </el-col>

      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon shared">
            <el-icon><Share /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ reportStats.shared }}</div>
            <div class="stat-label">已分享</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 搜索和筛选 -->
    <el-card class="search-card">
      <el-form :model="searchForm" :inline="true" class="search-form">
        <el-form-item label="报告名称">
          <el-input
            v-model="searchForm.title"
            placeholder="请输入报告名称"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="报告类型">
          <el-select v-model="searchForm.type" placeholder="选择类型" clearable>
            <el-option label="价格分析报告" value="price_analysis" />
            <el-option label="材料价格报告" value="material_audit" />
            <el-option label="项目总结报告" value="project_summary" />
            <el-option label="风险评估报告" value="risk_assessment" />
            <el-option label="成本优化报告" value="cost_optimization" />
          </el-select>
        </el-form-item>
        <el-form-item label="报告状态">
          <el-select v-model="searchForm.status" placeholder="选择状态" clearable>
            <el-option label="生成中" value="generating" />
            <el-option label="已完成" value="completed" />
            <el-option label="生成失败" value="failed" />
            <el-option label="已分享" value="shared" />
            <el-option label="已归档" value="archived" />
          </el-select>
        </el-form-item>
        <el-form-item label="生成时间">
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
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">
            搜索
          </el-button>
          <el-button @click="handleReset">
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 报告列表 -->
    <el-card class="table-card">
      <!-- 批量操作工具栏 -->
      <div class="table-toolbar">
        <div class="toolbar-left">
          <template v-if="selectedCount > 0">
            <el-button type="danger" :icon="Delete" @click="handleBatchDelete">
              批量删除 ({{ selectedCount }})
            </el-button>
            <el-button type="warning" :icon="FolderAdd" @click="handleBatchArchive">批量归档</el-button>
            <el-button type="success" :icon="Share" @click="handleBatchShare">批量分享</el-button>
            <el-divider direction="vertical" />
            <el-switch
              v-model="allSelected"
              inline-prompt
              active-text="全选所有页"
              inactive-text="仅选本页"
              @change="() => syncSelectionOnPage(tableRef, reports)"
            />
          </template>
        </div>
        <div class="toolbar-right">
          <el-tooltip content="刷新">
            <el-button :icon="Refresh" @click="fetchReports" />
          </el-tooltip>
          <el-dropdown @command="handleViewChange">
            <el-button :icon="Grid">
              视图 <el-icon><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="table" :class="{ 'is-active': viewMode === 'table' }">
                  <el-icon><List /></el-icon> 列表视图
                </el-dropdown-item>
                <el-dropdown-item command="grid" :class="{ 'is-active': viewMode === 'grid' }">
                  <el-icon><Grid /></el-icon> 网格视图
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>

      <!-- 表格视图 -->
      <div v-if="viewMode === 'table'" class="table-view">
        <el-table
          ref="tableRef"
          v-loading="loading"
          :data="reports"
          :row-key="row => row.id"
          :reserve-selection="true"
          @selection-change="onTableSelectionChange"
          stripe
          style="width: 100%"
        >
          <el-table-column type="selection" width="50" />
          <el-table-column prop="title" label="报告名称" min-width="200">
            <template #default="{ row }">
              <div class="report-info">
                <el-link 
                  type="primary" 
                  :underline="false"
                  @click="viewReport(row)"
                  class="report-title"
                >
                  {{ row.title }}
                </el-link>
                <div class="report-project">项目: {{ row.project_name }}</div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="type" label="报告类型" width="120">
            <template #default="{ row }">
              <el-tag :type="getTypeColor(row.type)" size="small">
                {{ getTypeText(row.type) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small">
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="file_size" label="文件大小" width="100">
            <template #default="{ row }">
              {{ row.file_size ? formatFileSize(row.file_size) : '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="generated_by" label="生成人" width="100" />
          <el-table-column prop="generated_at" label="生成时间" width="180">
            <template #default="{ row }">
              {{ row.generated_at ? formatDate(row.generated_at) : '-' }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="220" fixed="right">
            <template #default="{ row }">
              <el-button
                type="primary"
                link
                size="small"
                :icon="View"
                @click="viewReport(row)"
              >
                查看
              </el-button>
              <el-button
                v-if="row.status === 'completed'"
                type="success"
                link
                size="small"
                :icon="Download"
                @click="downloadReport(row)"
              >
                下载
              </el-button>
              <el-button
                v-if="row.status === 'completed'"
                type="warning"
                link
                size="small"
                :icon="Share"
                @click="openShareDialog(row)"
              >
                分享
              </el-button>
              <el-dropdown @command="(command) => handleCommand(command, row)">
                <el-button type="primary" link size="small">
                  更多 <el-icon><ArrowDown /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item v-if="row.status === 'failed'" command="regenerate" :icon="Refresh">
                      重新生成
                    </el-dropdown-item>
                    <el-dropdown-item command="edit" :icon="Edit">
                      编辑信息
                    </el-dropdown-item>
                    <el-dropdown-item command="archive" :icon="FolderAdd">
                      归档
                    </el-dropdown-item>
                    <el-dropdown-item command="delete" :icon="Delete" divided>
                      删除
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 网格视图 -->
      <div v-else class="grid-view">
        <div v-loading="loading" class="reports-grid">
          <div
            v-for="report in reports"
            :key="report.id"
            class="report-card"
            :class="{ 'selected': selectedReports.includes(report) }"
            @click="toggleReportSelection(report)"
          >
            <div class="card-header">
              <div class="report-type">
                <el-tag :type="getTypeColor(report.type)" size="small">
                  {{ getTypeText(report.type) }}
                </el-tag>
              </div>
              <div class="card-actions">
                <el-checkbox
                  :model-value="selectedReports.includes(report)"
                  @change="toggleReportSelection(report)"
                  @click.stop
                />
              </div>
            </div>
            
            <div class="card-icon">
              <el-icon class="report-icon" :class="getTypeIcon(report.type)">
                <Document />
              </el-icon>
            </div>
            
            <div class="card-content">
              <h4 class="report-title" @click.stop="viewReport(report)">
                {{ report.title }}
              </h4>
              <div class="report-meta">
                <div class="meta-item">
                  <span class="meta-label">项目:</span>
                  <span class="meta-value">{{ report.project_name }}</span>
                </div>
                <div class="meta-item">
                  <span class="meta-label">大小:</span>
                  <span class="meta-value">{{ report.file_size ? formatFileSize(report.file_size) : '-' }}</span>
                </div>
                <div class="meta-item">
                  <span class="meta-label">生成时间:</span>
                  <span class="meta-value">{{ formatDate(report.generated_at) }}</span>
                </div>
              </div>
            </div>
            
            <div class="card-footer">
              <div class="status-section">
                <el-tag :type="getStatusType(report.status)" size="small">
                  {{ getStatusText(report.status) }}
                </el-tag>
              </div>
              <div class="action-buttons">
                <el-button
                  type="primary"
                  size="small"
                  :icon="View"
                  @click.stop="viewReport(report)"
                  circle
                />
                <el-button
                  v-if="report.status === 'completed'"
                  type="success"
                  size="small"
                  :icon="Download"
                  @click.stop="downloadReport(report)"
                  circle
                />
                <el-button
                  v-if="report.status === 'completed'"
                  type="warning"
                  size="small"
                  :icon="Share"
                  @click.stop="openShareDialog(report)"
                  circle
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 分页：统一为通用组件 -->
      <BasePagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :total="pagination.total"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </el-card>

    <!-- 分享对话框 -->
    <el-dialog
      v-model="showShareDialog"
      title="分享报告"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="shareFormRef"
        :model="shareForm"
        :rules="shareRules"
        label-width="100px"
      >
        <el-form-item label="分享方式" prop="shareType">
          <el-radio-group v-model="shareForm.shareType">
            <el-radio label="link">分享链接</el-radio>
            <el-radio label="email">邮件发送</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item v-if="shareForm.shareType === 'link'" label="访问权限">
          <el-select v-model="shareForm.permission" style="width: 100%">
            <el-option label="任何人可查看" value="public" />
            <el-option label="仅限公司内部" value="internal" />
            <el-option label="指定用户" value="private" />
          </el-select>
        </el-form-item>
        
        <el-form-item v-if="shareForm.shareType === 'email'" label="接收邮箱" prop="emails">
          <el-input
            v-model="shareForm.emails"
            type="textarea"
            :rows="3"
            placeholder="请输入邮箱地址，多个地址用逗号分隔"
          />
        </el-form-item>
        
        <el-form-item label="有效期">
          <el-select v-model="shareForm.expiry" style="width: 100%">
            <el-option label="永久有效" value="never" />
            <el-option label="7天" value="7d" />
            <el-option label="30天" value="30d" />
            <el-option label="90天" value="90d" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="分享说明">
          <el-input
            v-model="shareForm.message"
            type="textarea"
            :rows="3"
            placeholder="可选：添加分享说明"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showShareDialog = false">取消</el-button>
        <el-button
          type="primary"
          :loading="sharing"
          @click="handleShareSubmit"
        >
          确定分享
        </el-button>
      </template>
    </el-dialog>

    <!-- 编辑报告信息对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑报告信息"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        :rules="editRules"
        label-width="80px"
      >
        <el-form-item label="报告标题" prop="title">
          <el-input
            v-model="editForm.title"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="报告描述">
          <el-input
            v-model="editForm.description"
            type="textarea"
            :rows="4"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="标签">
          <el-select
            v-model="editForm.tags"
            multiple
            filterable
            allow-create
            placeholder="选择或输入标签"
            style="width: 100%"
          >
            <el-option
              v-for="tag in availableTags"
              :key="tag"
              :label="tag"
              :value="tag"
            />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button
          type="primary"
          :loading="updating"
          @click="handleEditSubmit"
        >
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useSelectionAcrossPages } from '@/composables/useSelectionAcrossPages'
import BasePagination from '@/components/BasePagination.vue'
import {
  Plus,
  Document,
  Loading,
  CircleCheck,
  Share,
  Search,
  Refresh,
  Delete,
  FolderAdd,
  Grid,
  List,
  ArrowDown,
  View,
  Download,
  Edit
} from '@element-plus/icons-vue'
import { formatDate, formatFileSize } from '@/utils'
import {
  getReportsList,
  deleteReport,
  batchDeleteReports,
  shareReport,
  updateReport,
  downloadReport as downloadReportFile,
  regenerateReport
} from '@/api/reports'

const router = useRouter()

// 响应式数据
const loading = ref(false)
const sharing = ref(false)
const updating = ref(false)
const showShareDialog = ref(false)
const showEditDialog = ref(false)
const viewMode = ref('table')

const reports = ref([])
const selectedReports = ref([])
const tableRef = ref()
const {
  allSelected,
  selectedIds: selectedReportIds,
  excludedIds,
  toggleSelectAll,
  clearAll: clearAllSelection,
  handleSelectionChange,
  syncSelectionOnPage,
  getSelectedIds,
  createSelectedCount
} = useSelectionAcrossPages('id')
const selectedCount = createSelectedCount(() => pagination.total)
const currentReport = ref(null)
const availableTags = ref(['重要', '紧急', '已审核', '待确认'])

// 统计数据
const reportStats = reactive({
  total: 0,
  generating: 0,
  completed: 0,
  shared: 0
})

// 搜索表单
const searchForm = reactive({
  title: '',
  type: '',
  status: '',
  dateRange: []
})

// 分页数据
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 分享表单
const shareForm = reactive({
  shareType: 'link',
  permission: 'internal',
  emails: '',
  expiry: '30d',
  message: ''
})

const shareRules = {
  shareType: [
    { required: true, message: '请选择分享方式', trigger: 'change' }
  ],
  emails: [
    { 
      validator: (rule, value, callback) => {
        if (shareForm.shareType === 'email' && !value) {
          callback(new Error('请输入接收邮箱'))
        } else {
          callback()
        }
      }, 
      trigger: 'blur' 
    }
  ]
}

// 编辑表单
const editForm = reactive({
  title: '',
  description: '',
  tags: []
})

const editRules = {
  title: [
    { required: true, message: '请输入报告标题', trigger: 'blur' },
    { min: 2, max: 100, message: '标题长度在 2 到 100 个字符', trigger: 'blur' }
  ]
}

// 获取报告列表
const fetchReports = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      ...searchForm
    }
    
    // 处理日期范围
    if (searchForm.dateRange && searchForm.dateRange.length === 2) {
      params.start_date = searchForm.dateRange[0]
      params.end_date = searchForm.dateRange[1]
    }
    
    const response = await getReportsList(params)
    console.log('Reports API response:', response)
    
    // 修复API响应数据格式处理
    const reportData = response.data || response
    const rawReports = reportData.reports || reportData.items || []
    // 统一后端字段为前端所需字段
    reports.value = rawReports.map(r => ({
      id: r.report_id ?? r.id,
      project_id: r.project_id ?? r.projectId,
      title: r.report_title ?? r.title,
      type: r.report_type ?? r.type,
      status: r.status,
      file_size: r.file_size,
      project_name: r.project_name ?? (r.project_id ? `项目 ${r.project_id}` : (r.project || '')),
      generated_at: r.created_at ?? r.generated_at,
      download_url: r.download_url
    }))
    pagination.total = reportData.total || 0
    // 同步当前页勾选状态
    await nextTick()
    syncSelectionOnPage(tableRef, reports.value)
    
    // 更新统计数据 (通常从API返回)
    const stats = reportData.stats || {}
    Object.assign(reportStats, {
      total: stats.total || pagination.total || 0,
      generating: stats.generating || reports.value.filter(r => r.status === 'generating').length,
      completed: stats.completed || reports.value.filter(r => r.status === 'completed').length,
      shared: stats.shared || reports.value.filter(r => r.status === 'shared').length
    })
  } catch (error) {
    ElMessage.error('获取报告列表失败')
    console.error('获取报告列表失败:', error)
    
    // 显示空状态
    reports.value = []
    pagination.total = 0
    
    Object.assign(reportStats, {
      total: 0,
      generating: 0,
      completed: 0,
      shared: 0
    })
  } finally {
    loading.value = false
  }
}

// 状态相关方法
const getStatusType = (status) => {
  const typeMap = {
    'generating': 'warning',
    'completed': 'success',
    'failed': 'danger',
    'shared': 'info'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    'generating': '生成中',
    'completed': '已完成',
    'failed': '生成失败',
    'shared': '已分享'
  }
  return textMap[status] || status
}

const getTypeColor = (type) => {
  const colorMap = {
    'price_analysis': 'primary',
    'material_audit': 'success',
    'project_summary': 'warning',
    'risk_assessment': 'danger',
    'cost_optimization': 'info'
  }
  return colorMap[type] || 'default'
}

const getTypeText = (type) => {
  const textMap = {
    'price_analysis': '价格分析',
    'material_audit': '材料审计',
    'project_summary': '项目总结',
    'risk_assessment': '风险评估',
    'cost_optimization': '成本优化'
  }
  return textMap[type] || type
}

const getTypeIcon = (type) => {
  const iconMap = {
    'price_analysis': 'price-icon',
    'material_audit': 'audit-icon',
    'project_summary': 'summary-icon',
    'risk_assessment': 'risk-icon',
    'cost_optimization': 'optimization-icon'
  }
  return iconMap[type] || 'default-icon'
}

// 搜索和重置
const handleSearch = () => {
  pagination.page = 1
  fetchReports()
}

const handleReset = () => {
  Object.assign(searchForm, {
    title: '',
    type: '',
    status: '',
    dateRange: []
  })
  pagination.page = 1
  fetchReports()
}

// 分页处理
const handleSizeChange = (size) => {
  pagination.size = size
  pagination.page = 1
  fetchReports()
}

const handlePageChange = (page) => {
  pagination.page = page
  fetchReports()
}

// 选择处理
const onTableSelectionChange = (selection) => {
  handleSelectionChange(selection, reports.value)
  selectedReports.value = selection
}

const handleSelectionChangeLocal = (selection) => {
  selectedReports.value = selection
}

const toggleReportSelection = (report) => {
  const index = selectedReports.value.findIndex(item => item.id === report.id)
  if (index > -1) {
    selectedReports.value.splice(index, 1)
  } else {
    selectedReports.value.push(report)
  }
}

// 视图切换
const handleViewChange = (mode) => {
  viewMode.value = mode
}

// 报告操作
const viewReport = (report) => {
  const query = report.project_id ? `?project_id=${report.project_id}` : ''
  router.push(`/reports/${report.id}${query}`)
}

const downloadReport = async (report) => {
  try {
    await downloadReportFile(report.id)
    ElMessage.success('下载开始')
  } catch (error) {
    ElMessage.error('下载失败')
    console.error('下载失败:', error)
  }
}

const openShareDialog = (report) => {
  currentReport.value = report
  // 重置表单
  Object.assign(shareForm, {
    shareType: 'link',
    permission: 'internal',
    emails: '',
    expiry: '30d',
    message: ''
  })
  shareDialogVisible.value = true
}

const handleShareSubmit = async () => {
  sharing.value = true
  try {
    await shareReport(currentReport.value.id, shareForm)
    ElMessage.success('分享成功')
    showShareDialog.value = false
    fetchReports() // 刷新列表
  } catch (error) {
    ElMessage.error('分享失败')
    console.error('分享失败:', error)
  } finally {
    sharing.value = false
  }
}

// 更多操作处理
const handleCommand = async (command, row) => {
  switch (command) {
    case 'regenerate':
      await handleRegenerate(row)
      break
    case 'edit':
      await handleEdit(row)
      break
    case 'archive':
      await handleArchive(row)
      break
    case 'delete':
      await handleDelete(row)
      break
  }
}

const handleRegenerate = async (report) => {
  try {
    await ElMessageBox.confirm(
      `确定要重新生成报告 "${report.title}" 吗？`,
      '重新生成确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await regenerateReport(report.id)
    ElMessage.success('重新生成任务已启动')
    fetchReports()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('重新生成失败')
    }
  }
}

const handleEdit = (report) => {
  currentReport.value = report
  Object.assign(editForm, {
    title: report.title,
    description: report.description || '',
    tags: report.tags || []
  })
  showEditDialog.value = true
}

const handleEditSubmit = async () => {
  updating.value = true
  try {
    await updateReport(currentReport.value.id, editForm)
    ElMessage.success('更新成功')
    showEditDialog.value = false
    fetchReports()
  } catch (error) {
    ElMessage.error('更新失败')
    console.error('更新失败:', error)
  } finally {
    updating.value = false
  }
}

const handleArchive = async (report) => {
  try {
    await ElMessageBox.confirm(
      `确定要归档报告 "${report.title}" 吗？归档后可在归档列表中查看。`,
      '归档确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // TODO: 调用归档API
    ElMessage.success('归档成功')
    fetchReports()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('归档失败')
    }
  }
}

const handleDelete = async (report) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除报告 "${report.title}" 吗？删除后可在回收站中恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await deleteReport(report.id)
    ElMessage.success('删除成功')
    fetchReports()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 批量操作
const handleBatchDelete = async () => {
  if (selectedCount.value === 0) return
  
  try {
    await ElMessageBox.confirm(
      `确定要删除已选择的 ${selectedCount.value} 个报告吗？`,
      '批量删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    const fetchAllIds = async () => {
      const ids = []
      const size = 1000
      let page = 1
      while (true) {
        const resp = await getReportsList({
          page,
          size,
          ...searchForm
        })
        const data = resp.data || resp
        const list = data.reports || data.items || []
        list.forEach(r => ids.push(r.report_id ?? r.id))
        const total = data.total || 0
        if (page * size >= total || list.length < size) break
        page += 1
      }
      return ids
    }

    const ids = await getSelectedIds(fetchAllIds)
    await batchDeleteReports(ids)
    
    ElMessage.success('批量删除成功')
    clearAllSelection()
    fetchReports()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

const handleBatchArchive = () => {
  ElMessage.info('批量归档功能开发中...')
}

const handleBatchShare = () => {
  ElMessage.info('批量分享功能开发中...')
}

// 生命周期
onMounted(() => {
  fetchReports()
})
</script>

<style lang="scss" scoped>
.reports-list-container {
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

      &.generating {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
      }

      &.completed {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
      }

      &.shared {
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

.search-card {
  margin-bottom: 20px;

  .search-form {
    .el-form-item {
      margin-bottom: 0;
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

  .table-view {
    .report-info {
      .report-title {
        font-weight: 500;
        font-size: 14px;
        margin-bottom: 4px;
      }

      .report-project {
        font-size: 12px;
        color: $text-secondary;
      }
    }
  }

  .grid-view {
    .reports-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 20px;
      margin-bottom: 20px;

      .report-card {
        background: white;
        border-radius: 8px;
        border: 1px solid $border-color-lighter;
        padding: 20px;
        cursor: pointer;
        transition: all 0.3s ease;

        &:hover {
          box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.1);
          transform: translateY(-2px);
        }

        &.selected {
          border-color: $primary-color;
          box-shadow: 0 2px 12px 0 rgba($primary-color, 0.2);
        }

        .card-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;

          .report-type {
            flex: 1;
          }
        }

        .card-icon {
          text-align: center;
          margin-bottom: 16px;

          .report-icon {
            font-size: 48px;
            color: $primary-color;
          }
        }

        .card-content {
          margin-bottom: 16px;

          .report-title {
            font-size: 16px;
            font-weight: 600;
            color: $text-primary;
            margin: 0 0 12px 0;
            cursor: pointer;
            line-height: 1.4;

            &:hover {
              color: $primary-color;
            }
          }

          .report-meta {
            .meta-item {
              display: flex;
              justify-content: space-between;
              margin-bottom: 6px;
              font-size: 12px;

              .meta-label {
                color: $text-secondary;
              }

              .meta-value {
                color: $text-primary;
                text-align: right;
                max-width: 150px;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
              }
            }
          }
        }

        .card-footer {
          display: flex;
          justify-content: space-between;
          align-items: center;

          .status-section {
            flex: 1;
          }

          .action-buttons {
            display: flex;
            gap: 6px;
          }
        }
      }
    }
  }

  .pagination-wrapper {
    display: flex;
    justify-content: center;
    margin-top: 20px;
  }
}

// 下拉菜单活跃状态
:deep(.el-dropdown-menu__item.is-active) {
  background-color: $primary-color;
  color: white;
}

// 响应式设计
@media (max-width: $breakpoint-md) {
  .reports-list-container {
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

  .search-form {
    .el-form-item {
      width: 100% !important;
      margin-bottom: 16px !important;
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

  .reports-grid {
    grid-template-columns: 1fr !important;
  }
}
</style>
const onTableSelectionChange = (rows) => {
  handleSelectionChange(rows, reports.value)
  selectedReports.value = rows
}
