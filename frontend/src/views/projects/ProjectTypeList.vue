<template>
  <div class="project-type-list-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">{{ typeName }} - 项目列表</h1>
        <p class="page-subtitle">查看 {{ typeName }} 类型的所有项目</p>
      </div>
      <div class="header-actions">
        <el-button @click="$router.back()">
          返回
        </el-button>
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
          <el-select v-model="searchForm.status" placeholder="选择状态" clearable>
            <el-option label="草稿" value="draft" />
            <el-option label="处理中" value="processing" />
            <el-option label="已完成" value="completed" />
            <el-option label="失败" value="failed" />
          </el-select>
        </el-form-item>
        <el-form-item label="创建时间">
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

    <!-- 项目列表 -->
    <el-card class="table-card">
      <!-- 批量操作工具栏 -->
      <div class="table-toolbar">
        <div class="toolbar-left">
          <template v-if="selectedCount > 0">
            <el-button type="danger" :icon="Delete" @click="handleBatchDelete">
              批量删除 ({{ selectedCount }})
            </el-button>
            <el-divider direction="vertical" />
            <el-switch
              v-model="allSelected"
              inline-prompt
              active-text="全选所有页"
              inactive-text="仅选本页"
              @change="() => syncSelectionOnPage(tableRef, projects)"
            />
          </template>
        </div>
        <div class="toolbar-right">
          <el-tooltip content="刷新">
            <el-button :icon="Refresh" @click="fetchProjects" />
          </el-tooltip>
        </div>
      </div>

      <!-- 数据表格 -->
      <el-table
        ref="tableRef"
        v-loading="loading"
        :data="projects"
        :row-key="row => row.id"
        :reserve-selection="true"
        @selection-change="onSelectionChange"
        stripe
        style="width: 100%"
      >
        <el-table-column type="selection" width="50" />
        <el-table-column prop="name" label="项目名称" min-width="200">
          <template #default="{ row }">
            <el-link 
              type="primary" 
              :underline="false"
              @click="$router.push(`/projects/${row.id}`)"
            >
              {{ row.name }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="location" label="项目地点" width="150">
          <template #default="{ row }">
            <span>{{ row.location || '未指定' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="materials_count" label="材料数量" width="100">
          <template #default="{ row }">
            <span>{{ row.materials_count || 0 }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="analyzed_count" label="已分析" width="100">
          <template #default="{ row }">
            <span>{{ row.analyzed_count || 0 }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_by_name" label="创建人" width="120" />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              link
              :icon="View"
              @click="$router.push(`/projects/${row.id}`)"
            >
              查看
            </el-button>
            <el-button
              type="primary"
              link
              :icon="Edit"
              @click="$router.push(`/projects/${row.id}/edit`)"
            >
              编辑
            </el-button>
            <el-dropdown @command="(command) => handleCommand(command, row)">
              <el-button type="primary" link :icon="More">
                更多
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="duplicate" :icon="CopyDocument">
                    复制项目
                  </el-dropdown-item>
                  <el-dropdown-item command="export" :icon="Download">
                    导出数据
                  </el-dropdown-item>
                  <el-dropdown-item 
                    command="delete" 
                    :icon="Delete"
                    style="color: var(--el-color-danger);"
                  >
                    删除
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100, 500, 1000, 2000]"
          background
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Search,
  Refresh,
  Delete,
  View,
  Edit,
  More,
  CopyDocument,
  Download
} from '@element-plus/icons-vue'
import {
  getProjectList,
  deleteProject,
  batchDeleteProjects,
  duplicateProject,
  exportProject
} from '@/api/projects'
import { formatDate } from '@/utils'
import { useSelectionAcrossPages } from '@/composables/useSelectionAcrossPages'

const route = useRoute()
const router = useRouter()

// 响应式数据
const loading = ref(false)
const projects = ref([])
const selectedProjects = ref([])
const tableRef = ref()

// 跨页选择逻辑
const {
  allSelected,
  selectedIds: selectedProjectIds,
  excludedIds,
  toggleSelectAll,
  clearAll: clearAllSelection,
  handleSelectionChange,
  syncSelectionOnPage,
  getSelectedIds,
  createSelectedCount
} = useSelectionAcrossPages('id')

const selectedCount = createSelectedCount(() => pagination.total)

// 项目类型信息
const projectType = computed(() => route.params.type || 'other')
const typeName = computed(() => route.query.name || '其他工程')

// 搜索表单
const searchForm = reactive({
  name: '',
  status: '',
  dateRange: []
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
      project_type: projectType.value
    }
    
    // 添加搜索条件，但不重复 project_type
    if (searchForm.name) params.name = searchForm.name
    if (searchForm.status) params.status = searchForm.status
    
    // 处理日期范围
    if (searchForm.dateRange && searchForm.dateRange.length === 2) {
      params.created_start = searchForm.dateRange[0]
      params.created_end = searchForm.dateRange[1]
    }
    
    const response = await getProjectList(params)
    projects.value = response.data?.items || response.items || []
    pagination.total = response.data?.total || response.total || 0
    
    await nextTick()
    syncSelectionOnPage(tableRef, projects.value)
  } catch (error) {
    ElMessage.error('获取项目列表失败')
    console.error('获取项目列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 状态相关方法
const getStatusType = (status) => {
  const statusMap = {
    'draft': 'info',
    'processing': 'warning',
    'completed': 'success',
    'failed': 'danger'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status) => {
  const statusMap = {
    'draft': '草稿',
    'processing': '处理中',
    'completed': '已完成',
    'failed': '失败'
  }
  return statusMap[status] || status
}

// 搜索和重置
const handleSearch = () => {
  pagination.page = 1
  fetchProjects()
}

const handleReset = () => {
  Object.assign(searchForm, {
    name: '',
    status: '',
    dateRange: []
  })
  pagination.page = 1
  fetchProjects()
}

// 分页处理
const handleSizeChange = (size) => {
  pagination.size = size
  pagination.page = 1
  fetchProjects()
}

const handlePageChange = (page) => {
  pagination.page = page
  fetchProjects()
}

// 选择处理
const onSelectionChange = (selection) => {
  handleSelectionChange(selection, projects.value)
  selectedProjects.value = selection
}

// 批量删除
const handleBatchDelete = async () => {
  if (selectedCount.value === 0) return
  
  try {
    await ElMessageBox.confirm(
      `确定要删除已选择的 ${selectedCount.value} 个项目吗？`,
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
        const params = {
          page,
          size,
          project_type: projectType.value
        }
        
        // 添加搜索条件
        if (searchForm.name) params.name = searchForm.name
        if (searchForm.status) params.status = searchForm.status
        if (searchForm.dateRange && searchForm.dateRange.length === 2) {
          params.created_start = searchForm.dateRange[0]
          params.created_end = searchForm.dateRange[1]
        }
        
        const resp = await getProjectList(params)
        const list = resp.data?.items || resp.items || []
        list.forEach(p => ids.push(p.id))
        const total = resp.data?.total || resp.total || 0
        if (page * size >= total || list.length < size) break
        page += 1
      }
      return ids
    }

    const ids = await getSelectedIds(fetchAllIds)
    const response = await batchDeleteProjects(ids)
    
    // 处理响应
    if (response && response.data) {
      const { deleted_count, failed_count, failed_projects } = response.data
      
      if (failed_count > 0) {
        ElMessage.warning(`成功删除 ${deleted_count} 个项目，${failed_count} 个项目删除失败`)
        console.warn('部分项目删除失败:', failed_projects)
      } else {
        ElMessage.success(`成功删除 ${deleted_count} 个项目`)
      }
    } else {
      ElMessage.success('批量删除成功')
    }
    
    selectedProjects.value = []
    fetchProjects()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      
      // 根据错误类型显示不同消息
      if (error.response?.data?.detail) {
        ElMessage.error(error.response.data.detail)
      } else if (error.message) {
        ElMessage.error(`批量删除失败: ${error.message}`)
      } else {
        ElMessage.error('批量删除失败')
      }
    }
  }
}

// 更多操作处理
const handleCommand = async (command, row) => {
  switch (command) {
    case 'duplicate':
      await handleDuplicate(row)
      break
    case 'export':
      await handleExport(row)
      break
    case 'delete':
      await handleDelete(row)
      break
  }
}

// 复制项目
const handleDuplicate = async (project) => {
  try {
    await ElMessageBox.prompt('请输入新项目名称', '复制项目', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputValue: `${project.name} - 副本`
    })
      .then(async ({ value }) => {
        await duplicateProject(project.id, { name: value })
        ElMessage.success('项目复制成功')
        fetchProjects()
      })
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('项目复制失败')
      console.error('项目复制失败:', error)
    }
  }
}

// 导出项目
const handleExport = async (project) => {
  try {
    loading.value = true
    await exportProject(project.id, 'excel')
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
    console.error('导出失败:', error)
  } finally {
    loading.value = false
  }
}

// 删除项目
const handleDelete = async (project) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除项目 "${project.name}" 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await deleteProject(project.id)
    ElMessage.success('删除成功')
    fetchProjects()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
      console.error('删除失败:', error)
    }
  }
}

// 生命周期
onMounted(() => {
  fetchProjects()
})
</script>

<style lang="scss" scoped>
.project-type-list-container {
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

  .pagination-wrapper {
    display: flex;
    justify-content: center;
    margin-top: 20px;
  }
}

// 响应式设计
@media (max-width: $breakpoint-md) {
  .project-type-list-container {
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

  .search-form {
    .el-form-item {
      width: 100% !important;
      margin-bottom: 16px !important;
    }
  }

  .table-toolbar {
    flex-direction: column;
    gap: 12px;

    .toolbar-left,
    .toolbar-right {
      width: 100%;
      justify-content: flex-start;
    }
  }
}
</style>