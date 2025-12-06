<template>
  <div class="reports-container">
    <el-card class="reports-card">
      <template #header>
        <div class="card-header">
          <span class="title">分析报告列表</span>
          <el-button type="primary" @click="refreshList">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <!-- 搜索筛选 -->
      <div class="filter-section">
        <el-select v-model="filterProjectId" placeholder="选择项目" clearable @change="handleSearch">
          <el-option
            v-for="project in projects"
            :key="project.id"
            :label="project.name"
            :value="project.id"
          />
        </el-select>
        <el-button type="primary" @click="handleSearch">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
      </div>

      <!-- 报告列表 -->
      <el-table
        v-loading="loading"
        :data="reports"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="report_title" label="报告标题" min-width="200">
          <template #default="{ row }">
            {{ row.report_title || `项目报告 #${row.id}` }}
          </template>
        </el-table-column>
        <el-table-column prop="project_name" label="所属项目" min-width="150" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="生成时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handlePreview(row)">
              <el-icon><View /></el-icon>
              预览
            </el-button>
            <el-button type="success" link @click="handleDownload(row)">
              <el-icon><Download /></el-icon>
              下载
            </el-button>
            <el-button type="danger" link @click="handleDelete(row)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ statistics.total_reports || 0 }}</div>
            <div class="stat-label">总报告数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ statistics.monthly_reports || 0 }}</div>
            <div class="stat-label">本月生成</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ statistics.success_rate || 0 }}%</div>
            <div class="stat-label">生成成功率</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ statistics.average_generation_time || 0 }}s</div>
            <div class="stat-label">平均生成时间</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Search, View, Download, Delete } from '@element-plus/icons-vue'
import { request } from '@/utils/request'

const loading = ref(false)
const reports = ref([])
const projects = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const filterProjectId = ref(null)
const statistics = ref({})

// 获取报告列表
const fetchReports = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      size: pageSize.value
    }
    if (filterProjectId.value) {
      params.project_id = filterProjectId.value
    }
    const res = await request.get('/reports/', params)
    reports.value = res.items || []
    total.value = res.total || 0
  } catch (error) {
    console.error('获取报告列表失败:', error)
    ElMessage.error('获取报告列表失败')
  } finally {
    loading.value = false
  }
}

// 获取项目列表
const fetchProjects = async () => {
  try {
    const res = await request.get('/projects/', { page: 1, size: 100 })
    projects.value = res.data?.items || []
  } catch (error) {
    console.error('获取项目列表失败:', error)
  }
}

// 获取统计信息
const fetchStatistics = async () => {
  try {
    const res = await request.get('/reports/statistics/')
    statistics.value = res
  } catch (error) {
    console.error('获取统计信息失败:', error)
  }
}

// 刷新列表
const refreshList = () => {
  fetchReports()
  fetchStatistics()
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  fetchReports()
}

// 分页
const handleSizeChange = (val) => {
  pageSize.value = val
  fetchReports()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchReports()
}

// 预览报告
const handlePreview = (row) => {
  // 跳转到报告详情页
  window.open(`/reports/detail/${row.id}`, '_blank')
}

// 下载报告
const handleDownload = async (row) => {
  try {
    ElMessage.info('正在下载报告...')
    const response = await request.download(`/reports/${row.id}/download`)
    ElMessage.success('下载成功')
  } catch (error) {
    console.error('下载失败:', error)
    ElMessage.error('下载失败')
  }
}

// 删除报告
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除报告 "${row.report_title || '项目报告 #' + row.id}" 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await request.delete(`/reports/${row.id}`)
    ElMessage.success('删除成功')
    fetchReports()
    fetchStatistics()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 状态显示
const getStatusType = (status) => {
  const types = {
    'completed': 'success',
    'generating': 'warning',
    'failed': 'danger'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    'completed': '已完成',
    'generating': '生成中',
    'failed': '失败'
  }
  return texts[status] || '未知'
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  fetchReports()
  fetchProjects()
  fetchStatistics()
})
</script>

<style scoped>
.reports-container {
  padding: 20px;
}

.reports-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header .title {
  font-size: 18px;
  font-weight: 600;
}

.filter-section {
  margin-bottom: 20px;
  display: flex;
  gap: 12px;
}

.filter-section .el-select {
  width: 200px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.stats-row {
  margin-top: 20px;
}

.stat-card {
  text-align: center;
}

.stat-content {
  padding: 10px 0;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #409eff;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 8px;
}
</style>
