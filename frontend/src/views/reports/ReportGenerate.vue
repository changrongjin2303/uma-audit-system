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
            预览并生成
          </el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
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
    // 1. 先创建报告草稿记录
    const response = await generateReportApi({
      project_id: parseInt(reportForm.value.projectId),
      report_title: `${reportForm.value.projectId} - 分析报告`, // 这里可能需要更好的标题逻辑
      is_draft: true, // 关键：标记为草稿，仅创建记录
      config: {
        report_type: reportForm.value.type,
        include_charts: reportForm.value.includes.includes('charts'),
        include_detailed_analysis: reportForm.value.includes.includes('details'),
        include_recommendations: reportForm.value.includes.includes('suggestions'),
        include_appendices: reportForm.value.includes.includes('attachments')
      }
    })
    
    // 2. 获取到新创建的 report_id
    const newReportId = response.report_id || response.data?.report_id
    
    if (!newReportId) {
      throw new Error('无法获取新生成的报告ID')
    }
    
    ElMessage.success('报告记录已创建，正在跳转预览...')
    
    // 3. 跳转到详情页，传入真实的 report_id
    await router.push({
      name: 'ReportDetail',
      params: { id: newReportId },
      query: {
        project_id: reportForm.value.projectId, // 仍然保留 project_id 以备不时之需
        report_type: reportForm.value.type,
        includes: reportForm.value.includes.join(',')
      }
    })
    
  } catch (error) {
    console.error('创建报告记录失败:', error)
    ElMessage.error('创建报告记录失败: ' + (error.message || '未知错误'))
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
