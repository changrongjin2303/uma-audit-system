<template>
  <div class="projects-container">
    <!-- 页面标题和工具栏 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">项目材料价格管理</h1>
        <p class="page-subtitle">查看并管理所有项目的项目列表</p>
      </div>
      <div class="header-actions">
        <el-button 
          type="primary" 
          :icon="Plus" 
          @click="$router.push('/projects/create')"
        >
          新建项目
        </el-button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="search-card">
      <el-form :model="searchForm" :inline="true" class="search-form">
        <el-form-item label="项目名称">
          <el-input
            v-model="searchForm.name"
            placeholder="请输入项目名称"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        
        <el-form-item label="项目状态">
          <el-select 
            v-model="searchForm.status" 
            placeholder="项目状态"
            clearable
          >
            <el-option label="草稿" value="draft" />
            <el-option label="处理中" value="processing" />
            <el-option label="已完成" value="completed" />
            <el-option label="失败" value="failed" />
          </el-select>
        </el-form-item>

        <el-form-item label="项目类型">
          <el-select 
            v-model="searchForm.project_type" 
            placeholder="项目类型"
            clearable
          >
            <el-option label="建筑工程" value="building" />
            <el-option label="装修工程" value="decoration" />
            <el-option label="市政工程" value="municipal" />
            <el-option label="园林工程" value="landscape" />
            <el-option label="公路工程" value="highway" />
            <el-option label="其他工程" value="other" />
          </el-select>
        </el-form-item>

        <el-form-item label="创建时间">
          <el-date-picker
            v-model="searchForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="width: 240px"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">
            搜索
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 项目列表表格 -->
    <el-card class="projects-card">
      <!-- 批量操作工具栏 -->
      <div class="table-toolbar">
        <div class="toolbar-left">
          <template v-if="selectedCount > 0">
            <el-button type="danger" :icon="Delete" @click="handleBatchDelete">
              批量删除 ({{ selectedCount }})
            </el-button>
            <el-divider direction="vertical" />
            <span class="selected-info">已选择 {{ selectedCount }} 个项目</span>
          </template>
          <template v-else>
            <span class="total-info">共 {{ pagination.total }} 个项目</span>
          </template>
        </div>
        <div class="toolbar-right">
          <el-button :icon="Refresh" @click="fetchProjects">刷新</el-button>
        </div>
      </div>

      <el-table 
        ref="projectTableRef"
        v-loading="loading"
        :data="projects"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        
        <el-table-column prop="name" label="项目名称" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">
            <el-link 
              :underline="false" 
              type="primary" 
              @click="goToDetail(row.id)"
            >
              {{ row.name }}
            </el-link>
          </template>
        </el-table-column>

        <el-table-column prop="location" label="项目地点" min-width="140" show-overflow-tooltip />

        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="project_type" label="项目类型" min-width="120">
          <template #default="{ row }">
            {{ getProjectTypeText(row.project_type) }}
          </template>
        </el-table-column>

        <el-table-column prop="total_materials" label="材料数量" width="100" align="center">
          <template #default="{ row }">
            {{ row.total_materials || 0 }}
          </template>
        </el-table-column>

        <el-table-column prop="analysis_count" label="已分析" width="100" align="center">
          <template #default="{ row }">
            {{ row.analysis_count || 0 }}
          </template>
        </el-table-column>

        <el-table-column prop="created_by" label="创建人" min-width="100" />

        <el-table-column prop="created_at" label="创建时间" min-width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button 
                :icon="View" 
                size="small" 
                @click="goToDetail(row.id)"
              >
                查看
              </el-button>
              <el-button 
                :icon="Edit" 
                size="small" 
                type="primary"
                @click="goToEdit(row.id)"
              >
                编辑
              </el-button>
              <el-button 
                :icon="Delete" 
                size="small" 
                type="danger" 
                @click="handleDelete(row)"
              >
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :page-sizes="[10, 20, 50, 100]"
          :small="false"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  View,
  Edit,
  Delete,
  Search,
  Refresh
} from '@element-plus/icons-vue'
import {
  getProjectList,
  deleteProject
} from '@/api/projects'
import { formatDate } from '@/utils'

const router = useRouter()

// 响应式数据
const loading = ref(false)
const projects = ref([])
const selectedRows = ref([])
const projectTableRef = ref()

// 计算属性
const selectedCount = computed(() => selectedRows.value.length)

// 搜索表单
const searchForm = reactive({
  name: '',
  status: '',
  project_type: '',
  dateRange: null
})

// 分页数据
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 获取项目列表
const fetchProjects = async () => {
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
      delete params.dateRange
    }

    // 清理空值参数
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null || params[key] === undefined) {
        delete params[key]
      }
    })

    console.log('🔍 正在获取项目列表，参数:', params)
    const response = await getProjectList(params)
    console.log('📊 API响应数据:', response)
    
    // 处理后端API响应
    if (response.code === 200) {
      projects.value = response.data?.items || response.items || []
      pagination.total = response.data?.total || response.total || 0
      console.log('✅ 项目列表更新成功:', projects.value.length, '个项目')
    } 
    // 处理Mock API响应
    else if (response.items) {
      projects.value = response.items || []
      pagination.total = response.total || 0
      console.log('✅ Mock项目列表更新成功:', projects.value.length, '个项目')
    } else {
      console.error('❌ API返回错误:', response)
      ElMessage.error(response.message || '获取项目列表失败')
    }
  } catch (error) {
    console.error('❌ 获取项目列表失败:', error)
    ElMessage.error('获取项目列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索处理
const handleSearch = () => {
  pagination.page = 1
  fetchProjects()
}

// 重置搜索
const handleReset = () => {
  Object.assign(searchForm, {
    name: '',
    status: '',
    project_type: '',
    dateRange: null
  })
  pagination.page = 1
  fetchProjects()
}

// 分页处理
const handleSizeChange = (val) => {
  pagination.size = val
  pagination.page = 1
  fetchProjects()
}

const handlePageChange = (val) => {
  pagination.page = val
  fetchProjects()
}

// 选择处理
const handleSelectionChange = (selection) => {
  selectedRows.value = selection
}

// 获取状态类型
const getStatusType = (status) => {
  const types = {
    'draft': 'info',
    'processing': 'warning',
    'completed': 'success',
    'failed': 'danger'
  }
  return types[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const texts = {
    'draft': '草稿',
    'processing': '处理中',
    'completed': '已完成',
    'failed': '失败'
  }
  return texts[status] || '未知'
}

// 获取项目类型文本
const getProjectTypeText = (type) => {
  const texts = {
    'building': '建筑工程',
    'decoration': '装修工程',
    'municipal': '市政工程',
    'landscape': '园林工程',
    'highway': '公路工程',
    'other': '其他工程'
  }
  return texts[type] || '未知类型'
}

// 导航函数
const goToDetail = (id) => {
  router.push(`/projects/${id}`)
}

const goToEdit = (id) => {
  router.push(`/projects/${id}/edit`)
}

// 删除项目
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除项目 "${row.name}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    await deleteProject(row.id)
    ElMessage.success('删除成功')
    fetchProjects()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 批量删除项目
const handleBatchDelete = async () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请先选择要删除的项目')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedRows.value.length} 个项目吗？此操作不可恢复。`,
      '确认批量删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    // 批量删除API调用
    const deletePromises = selectedRows.value.map(row => deleteProject(row.id))
    await Promise.all(deletePromises)
    
    ElMessage.success(`成功删除 ${selectedRows.value.length} 个项目`)
    selectedRows.value = []
    fetchProjects()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败')
    }
  }
}

// 监听搜索表单变化
watch(() => searchForm, () => {
  // 可以在这里添加自动搜索逻辑
}, { deep: true })

// 生命周期
onMounted(() => {
  console.log('🚀 ProjectList组件已挂载，开始获取项目列表')
  fetchProjects()
})
</script>

<style lang="scss" scoped>
.projects-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 24px;

  .header-content {
    .page-title {
      font-size: 24px;
      font-weight: 600;
      color: #303133;
      margin: 0 0 8px 0;
    }

    .page-subtitle {
      font-size: 14px;
      color: #606266;
      margin: 0;
    }
  }

  .header-actions {
    display: flex;
    gap: 12px;
  }
}

// 搜索卡片样式
.search-card {
  margin-bottom: 20px;

  .search-form {
    .el-form-item {
      margin-bottom: 0;
    }
  }
}

// 项目卡片样式
.projects-card {
  .table-toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 0;
    margin-bottom: 16px;
    border-bottom: 1px solid #e4e7ed;

    .toolbar-left {
      display: flex;
      align-items: center;
      gap: 16px;

      .selected-info {
        color: #409eff;
        font-weight: 500;
      }

      .total-info {
        color: #909399;
      }
    }

    .toolbar-right {
      display: flex;
      gap: 12px;
    }
  }

  .el-table {
    border: none;
    outline: none;
    
    :deep(.el-table__header) {
      th {
        background-color: #fafafa;
        color: #606266;
        font-weight: 600;
        border-bottom: 1px solid #e4e7ed;
      }
    }

    :deep(.el-table__body) {
      tr {
        &:hover {
          td {
            background-color: #f5f7fa;
          }
        }
      }
    }
    
    :deep(.el-table__border-line) {
      display: none;
    }

    // 操作列按钮样式
    .action-buttons {
      display: flex;
      gap: 12px;
      align-items: center;
      white-space: nowrap;
      
      .el-button {
        padding: 4px 6px;
        font-size: 12px;
        height: auto;
        min-height: auto;
        border: none;
        background: transparent;
        box-shadow: none;
        white-space: nowrap;
        
        &:hover {
          background: transparent;
        }
        
        &:focus {
          background: transparent;
          box-shadow: none;
        }
        
        &.el-button--small {
          padding: 4px 8px;
          border: none;
          background: transparent;
        }
        
        // 查看按钮 - 蓝色
        &:first-child {
          color: #409eff;
          
          &:hover {
            color: #66b3ff;
            background: transparent;
          }
        }
        
        // 编辑按钮 - 蓝色
        &.el-button--primary {
          color: #409eff;
          background: transparent;
          border: none;
          
          &:hover {
            color: #66b3ff;
            background: transparent;
          }
        }
        
        // 删除按钮 - 红色
        &.el-button--danger {
          color: #f56c6c;
          background: transparent;
          border: none;
          
          &:hover {
            color: #f78989;
            background: transparent;
          }
        }
      }
    }
  }

  // 分页样式
  .pagination-wrapper {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 20px 0 10px 0;
    margin-top: 16px;
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .search-card {
    .search-form {
      .el-form-item {
        margin-bottom: 16px;
        width: 100%;
      }
    }
  }

  .projects-card {
    .table-toolbar {
      flex-direction: column;
      align-items: flex-start;
      gap: 12px;

      .toolbar-left,
      .toolbar-right {
        width: 100%;
        justify-content: flex-start;
      }

      .toolbar-right {
        justify-content: flex-end;
      }
    }

    .el-table {
      :deep(.el-table__body-wrapper) {
        overflow-x: auto;
      }
    }
  }
}

@media (max-width: 768px) {
  .projects-container {
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

  .search-card {
    .search-form {
      .el-form-item {
        margin-bottom: 12px;
        width: 100%;
        
        .el-input,
        .el-select,
        .el-date-picker {
          width: 100%;
        }
      }
    }
  }

  .projects-card {
    .table-toolbar {
      padding: 12px 0;
      
      .toolbar-left {
        margin-bottom: 12px;
        
        .selected-info,
        .total-info {
          font-size: 14px;
        }
      }
      
      .el-button {
        padding: 6px 12px;
        font-size: 12px;
      }
    }

    .el-table {
      font-size: 12px;
      
      :deep(.el-table__body) {
        td {
          padding: 8px 0;
        }
      }

      .el-button {
        padding: 4px 8px;
        font-size: 11px;
        margin-right: 4px;
      }
    }

    .pagination-wrapper {
      padding: 16px;
      
      .el-pagination {
        :deep(.el-pagination__sizes),
        :deep(.el-pagination__total) {
          display: none;
        }
      }
    }
  }
}

// 加载状态
.el-loading-mask {
  border-radius: 8px;
}

// 空状态
.el-table__empty-block {
  padding: 60px 0;
}
</style>
