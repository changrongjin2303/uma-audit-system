<template>
  <div class="report-generate">
    <el-card>
      <template #header>
        <span>生成分析报告</span>
      </template>
      
      <el-form :model="reportForm" label-width="120px">
        <el-form-item label="项目选择">
          <el-select v-model="reportForm.projectId" placeholder="请选择项目" :loading="loadingProjects">
            <el-option 
              v-for="project in projects" 
              :key="project.id" 
              :label="project.name" 
              :value="project.id" 
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="报告类型">
          <el-radio-group v-model="reportForm.type">
            <el-radio value="comprehensive">完整报告</el-radio>
            <el-radio value="summary">摘要报告</el-radio>
            <el-radio value="price_analysis">价格分析报告</el-radio>
            <el-radio value="custom">自定义报告</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="包含内容">
          <el-checkbox-group v-model="reportForm.includes">
            <el-checkbox value="charts">数据图表</el-checkbox>
            <el-checkbox value="details">详细清单</el-checkbox>
            <el-checkbox value="suggestions">分析建议</el-checkbox>
            <el-checkbox value="attachments">相关附件</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        
        <el-form-item label="输出格式">
          <el-select v-model="reportForm.format">
            <el-option label="Word文档" value="docx" />
            <el-option label="PDF文档" value="pdf" />
            <el-option label="Excel表格" value="xlsx" />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="generateReport" :loading="generating">
            生成报告
          </el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { generateReport as generateReportApi } from '@/api/reports'
import { getProjectsList } from '@/api/projects'

const router = useRouter()
const route = useRoute()

const reportForm = ref({
  projectId: '',
  // 与后端枚举一致: price_analysis | comprehensive | summary | custom
  type: 'comprehensive',
  includes: ['charts', 'details'],
  format: 'docx'
})

const generating = ref(false)
const projects = ref([])
const loadingProjects = ref(false)

const generateReport = async () => {
  if (!reportForm.value.projectId) {
    ElMessage.warning('请选择项目')
    return
  }
  
  generating.value = true
  
  try {
    // 调用真实的报告生成API
    const response = await generateReportApi({
      project_id: parseInt(reportForm.value.projectId),
      report_title: `${reportForm.value.projectId} - 分析报告`,
      config: {
        report_type: reportForm.value.type,
        include_charts: reportForm.value.includes.includes('charts'),
        include_detailed_analysis: reportForm.value.includes.includes('details'),
        include_recommendations: reportForm.value.includes.includes('suggestions'),
        include_appendices: reportForm.value.includes.includes('attachments')
      }
    })
    
    ElMessage.success(`报告生成成功！报告ID: ${response.report_id}`)
    
    // 跳转到报告列表页面
    await router.push('/reports')
  } catch (error) {
    console.error('报告生成失败:', error)
    const errorMsg = error.response?.data?.detail || error.message || '报告生成失败'
    ElMessage.error(errorMsg)
  } finally {
    generating.value = false
  }
}

// 加载项目列表
const loadProjects = async () => {
  loadingProjects.value = true
  try {
    const response = await getProjectsList({ page: 1, size: 100 })
    const projectData = response.data || response
    projects.value = projectData.projects || projectData.items || []
    console.log('加载项目列表成功:', projects.value)
  } catch (error) {
    console.error('加载项目列表失败:', error)
    ElMessage.error('加载项目列表失败')
  } finally {
    loadingProjects.value = false
  }
}

const resetForm = () => {
  reportForm.value = {
    projectId: '',
    type: 'full',
    includes: ['charts', 'details'],
    format: 'docx'
  }
}

// 页面初始化
onMounted(() => {
  // 读取URL参数进行预填充
  const { project_id, type } = route.query || {}
  if (project_id) {
    reportForm.value.projectId = String(project_id)
  }
  if (type) {
    // 将来自其他页面的别名映射为后端枚举
    const map = {
      analysis: 'price_analysis',
      full: 'comprehensive',
      exception: 'custom'
    }
    const normalized = map[type] || String(type)
    const allowed = ['price_analysis', 'comprehensive', 'summary', 'custom']
    if (allowed.includes(normalized)) {
      reportForm.value.type = normalized
    }
  }
  loadProjects()
})
</script>

<style scoped>
.report-generate {
  padding: 20px;
  max-width: 800px;
}
</style>
