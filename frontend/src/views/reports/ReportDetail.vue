<template>
  <div class="report-detail">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>分析报告详情</span>
          <div>
            <el-button type="primary" :loading="downloading" @click="onDownload">下载</el-button>
            <el-button @click="onShare">分享</el-button>
          </div>
        </div>
      </template>

      <div class="report-content">
        <h2>{{ title }}</h2>
        <div class="report-meta">
          <p><strong>项目名称：</strong>{{ projectName || '-' }}</p>
          <p><strong>生成时间：</strong>{{ createTime }}</p>
          <p><strong>分析人员：</strong>{{ auditor }}</p>
        </div>

        <!-- 分析结果表格 -->
        <div class="report-summary">
          <MaterialAnalysisTable 
            :project-name="projectName"
            :analysis-data="analysisTableData"
          />
          
          <!-- 市场信息价材料表格 -->
          <GuidancePriceMaterialTable 
            :project-name="projectName"
            :guidance-price-data="guidancePriceTableData"
          />
        </div>

    <div class="report-charts">
      <h3>数据分析</h3>

      <div class="chart-section">
        <div class="chart-header">
          <span class="chart-title">风险等级分布</span>
          <span class="chart-desc">展示项目材料在不同风险等级上的数量分布，用于识别风险集中区间。</span>
        </div>
        <div ref="riskChartRef" class="chart-box full"></div>
      </div>

      <div class="chart-section">
        <div class="chart-header">
          <span class="chart-title">核增减额 TOP10</span>
          <span class="chart-desc">列出差额绝对值最大的材料，帮助快速定位重点复核对象。</span>
        </div>
        <div ref="varianceChartRef" class="chart-box full"></div>
      </div>

      <div class="chart-section">
        <div class="chart-header">
          <span class="chart-title">送审 VS AI 核审 总额对比</span>
          <span class="chart-desc">比较无信息价与市场信息价材料在送审金额与AI核审金额的总量差异。</span>
        </div>
        <div ref="priceDistChartRef" class="chart-box full"></div>
      </div>
    </div>
      </div>
    </el-card>
  </div>
  
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import html2canvas from 'html2canvas'
import { downloadReport, previewReport, previewReportByProject, generateReport } from '@/api/reports'
import MaterialAnalysisTable from '@/components/analysis/MaterialAnalysisTable.vue'
import GuidancePriceMaterialTable from '@/components/analysis/GuidancePriceMaterialTable.vue'

const route = useRoute()
const router = useRouter()

const reportId = Number(route.params.id)
const projectId = route.query.project_id ? Number(route.query.project_id) : null
const currentProjectId = ref(projectId)

// 顶部信息
const title = ref('造价材料分析报告')
const projectName = ref('')
const createTime = ref(new Date().toLocaleString())
const auditor = ref('系统')

// 读取配置参数
const reportType = ref(route.query.report_type || 'audit')
const reportIncludes = ref(route.query.includes ? route.query.includes.split(',') : [])

// 预览数据
const statistics = ref(null)
const analysisTableData = ref([])
const guidancePriceTableData = ref([])
const riskChartRef = ref()
const varianceChartRef = ref()
const priceDistChartRef = ref()
const downloading = ref(false)

const formatPercent = (v) => {
  if (v === null || v === undefined) return '-'
  return `${Number(v).toFixed(1)}%`
}

const formatCurrency = (v) => {
  if (!v || isNaN(v)) return '0'
  // 按万元显示
  return `${(Number(v) / 10000).toFixed(2)} 万元`
}

const chartInstances = {
  risk: null,
  adjustments: null,
  totals: null
}

const disposeCharts = () => {
  Object.keys(chartInstances).forEach(key => {
    if (chartInstances[key]) {
      chartInstances[key].dispose()
      chartInstances[key] = null
    }
  })
}

const renderCharts = (chartData) => {
  disposeCharts()
  if (!chartData) return

  const { riskDistribution, adjustmentTopList, totalsComparison } = chartData

  if (riskChartRef.value) {
    chartInstances.risk = echarts.init(riskChartRef.value)
    chartInstances.risk.setOption({
      title: { text: '风险等级分布', left: 'center' },
      tooltip: { trigger: 'item', formatter: '{b}: {c}项 ({d}%)' },
      legend: { bottom: 0 },
      series: [{
        type: 'pie', radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        data: riskDistribution.map(item => ({ name: item.name, value: item.value, itemStyle: item.itemStyle }))
      }]
    })
  }

  if (varianceChartRef.value) {
    chartInstances.adjustments = echarts.init(varianceChartRef.value)
    chartInstances.adjustments.setOption({
      title: { text: '核增减额TOP10', left: 'center' },
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        valueFormatter: val => Number(val).toLocaleString('zh-CN', {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2
        })
      },
      grid: { left: 180, right: 120, top: 70, bottom: 40 },
      xAxis: {
        type: 'value',
        axisLabel: {
          formatter: value => Number(value).toLocaleString('zh-CN', {
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
          })
        }
      },
      yAxis: {
        type: 'category',
        data: adjustmentTopList.map(item => item.name || ''),
        inverse: true,
        axisLabel: {
          formatter: value => {
            if (!value) return ''
            return value.length > 18 ? `${value.slice(0, 18)}...` : value
          },
          width: 140,
          overflow: 'truncate',
          align: 'right',
          color: '#333',
          margin: 12
        }
      },
      series: [{
        type: 'bar',
        data: adjustmentTopList.map(item => ({
          value: item.value,
          itemStyle: { color: item.value >= 0 ? '#F56C6C' : '#67C23A' }
        })),
        label: {
          show: true,
          position: 'right',
          distance: 12,
          formatter: ({ value }) => Number(value).toLocaleString('zh-CN', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
          }),
          color: '#333'
        },
        barCategoryGap: '35%'
      }]
    })
  }

  if (priceDistChartRef.value) {
    chartInstances.totals = echarts.init(priceDistChartRef.value)
    chartInstances.totals.setOption({
      title: { text: '送审 VS AI 核审 总额对比', left: 'center' },
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        valueFormatter: val => Number(val).toLocaleString('zh-CN', { minimumFractionDigits: 2 })
      },
      legend: { bottom: 0, data: ['送审总额', 'AI核审总额'] },
      grid: { left: 80, right: 20, top: 60, bottom: 60 },
      xAxis: { type: 'category', data: totalsComparison.categories },
      yAxis: {
        type: 'value',
        splitLine: { show: true, lineStyle: { color: '#f0f0f0' } },
        axisLabel: {
          color: '#333',
          formatter: value => Number(value).toLocaleString('zh-CN', {
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
          })
        }
      },
      series: [
        {
          name: '送审总额',
          type: 'bar',
          data: totalsComparison.originalTotals,
          itemStyle: { color: '#409EFF' }
        },
        {
          name: 'AI核审总额',
          type: 'bar',
          data: totalsComparison.aiTotals,
          itemStyle: { color: '#67C23A' }
        }
      ]
    })
  }
}

const prepareChartData = (analysisData = [], guidanceData = []) => {
  const riskOrder = ['normal', 'low', 'medium', 'high', 'critical']
  const riskLabels = {
    normal: '正常',
    low: '低风险',
    medium: '中风险',
    high: '高风险',
    critical: '极高风险'
  }
  const riskColors = {
    normal: '#67C23A',
    low: '#409EFF',
    medium: '#E6A23C',
    high: '#F56C6C',
    critical: '#C039A5'
  }

  const normalizeNumber = (value) => {
    const num = Number(value)
    return Number.isFinite(num) ? num : 0
  }

  const analysisItems = (analysisData || []).map(item => {
    const quantity = normalizeNumber(item.quantity || item.quantity_value)
    const originalUnit = normalizeNumber(item.original_price)
    const aiUnit = normalizeNumber(item.ai_predicted_price || item.predicted_price)
    const originalTotal = item.original_total_price !== undefined
      ? normalizeNumber(item.original_total_price)
      : originalUnit * quantity
    const aiTotal = item.ai_total_price !== undefined
      ? normalizeNumber(item.ai_total_price)
      : aiUnit * quantity
    const adjustment = item.adjustment !== undefined
      ? normalizeNumber(item.adjustment)
      : originalTotal - aiTotal
    const riskLevel = (item.risk_level || '').toLowerCase()

    return {
      name: item.material_name || item.name || '材料',
      riskLevel: riskLevel || 'normal',
      adjustment,
      originalTotal,
      aiTotal
    }
  })

  // 过滤掉风险等级为正常(normal)的材料
  const filteredAnalysisItems = analysisItems.filter(item => item.riskLevel !== 'normal')

  const guidanceItems = (guidanceData || []).map(item => {
    const originalTotal = item.original_total_price !== undefined
      ? normalizeNumber(item.original_total_price)
      : normalizeNumber(item.original_price) * normalizeNumber(item.quantity)
    const guidanceTotal = item.guidance_total_price !== undefined
      ? normalizeNumber(item.guidance_total_price)
      : normalizeNumber(item.guidance_price) * normalizeNumber(item.quantity)
    const adjustment = item.adjustment !== undefined
      ? normalizeNumber(item.adjustment)
      : originalTotal - guidanceTotal
    
    // 市场信息价材料也需要根据 risk_level 过滤，但需要确保 guidanceData 中包含 risk_level
    // 后端已经确保返回 risk_level
    const riskLevel = (item.risk_level || '').toLowerCase()

    return {
      name: item.material_name || item.name || '材料',
      riskLevel: riskLevel || 'normal',
      adjustment,
      originalTotal,
      aiTotal: guidanceTotal
    }
  })

  // 过滤掉风险等级为正常(normal)的材料
  const filteredGuidanceItems = guidanceItems.filter(item => item.riskLevel !== 'normal')

  const combinedRisk = analysisItems.reduce((acc, item) => {
    const key = riskLabels[item.riskLevel] ? item.riskLevel : 'normal'
    acc[key] = (acc[key] || 0) + 1
    return acc
  }, {})

  const riskDistribution = riskOrder
    .filter(key => combinedRisk[key])
    .map(key => ({ name: riskLabels[key], value: combinedRisk[key], itemStyle: { color: riskColors[key] } }))

  // TOP10 和 总额对比 使用过滤后的数据
  const adjustmentsMerged = [...filteredAnalysisItems, ...filteredGuidanceItems]
    .filter(item => Math.abs(item.adjustment) > 1e-2)
    .sort((a, b) => Math.abs(b.adjustment) - Math.abs(a.adjustment))
    .slice(0, 10)

  const adjustmentTopList = adjustmentsMerged.map(item => ({
    name: item.name,
    value: Number(item.adjustment.toFixed(2))
  }))

  const analysisTotalsOriginal = filteredAnalysisItems.reduce((sum, item) => sum + item.originalTotal, 0)
  const analysisTotalsAi = filteredAnalysisItems.reduce((sum, item) => sum + item.aiTotal, 0)
  const guidanceTotalsOriginal = filteredGuidanceItems.reduce((sum, item) => sum + item.originalTotal, 0)
  const guidanceTotalsAi = filteredGuidanceItems.reduce((sum, item) => sum + item.aiTotal, 0)

  const totalsComparison = {
    categories: ['无信息价材料', '市场信息价材料'],
    originalTotals: [Number(analysisTotalsOriginal.toFixed(2)), Number(guidanceTotalsOriginal.toFixed(2))],
    aiTotals: [Number(analysisTotalsAi.toFixed(2)), Number(guidanceTotalsAi.toFixed(2))]
  }

  return {
    riskDistribution: riskDistribution.length > 0 ? riskDistribution : [{ name: '正常', value: 0 }],
    adjustmentTopList,
    totalsComparison
  }
}

const captureCharts = async () => {
  const images = {}
  
  const processChart = async (chartRef, instance, key) => {
    if (!chartRef || !chartRef.parentElement) return
    
    // Capture the parent .chart-section
    const container = chartRef.parentElement
    
    // Save original styles
    const originalWidth = container.style.width
    const originalBackground = container.style.background
    
    try {
      // Force A4 content width (approx 700px to be safe within margins)
      // This ensures the layout in Word (A4) matches what we capture
      container.style.width = '700px'
      container.style.background = '#fff' // Ensure background is white
      
      // Trigger resize
      if (instance) instance.resize()
      
      // Wait for resize animation/render
      await new Promise(resolve => setTimeout(resolve, 300))
      
      const canvas = await html2canvas(container, {
        scale: 2, // Reduce scale to avoid large payload (2 is sufficient for docs)
        useCORS: true,
        backgroundColor: '#ffffff',
        logging: false
      })
      
      // Use JPEG with 0.8 quality for smaller size
      images[key] = canvas.toDataURL('image/jpeg', 0.8)
    } catch (e) {
      console.error(`Capture failed for ${key}:`, e)
    } finally {
      // Restore styles
      container.style.width = originalWidth
      container.style.background = originalBackground
      
      if (instance) instance.resize()
    }
  }
  
  // Capture sequentially
  if (riskChartRef.value) await processChart(riskChartRef.value, chartInstances.risk, 'risk')
  if (varianceChartRef.value) await processChart(varianceChartRef.value, chartInstances.adjustments, 'adjustment')
  if (priceDistChartRef.value) await processChart(priceDistChartRef.value, chartInstances.totals, 'totals')
  
  return images
}

const loadPreview = async () => {
  try {
    let data
    if (projectId) {
      data = await previewReportByProject(projectId)
    } else {
      data = await previewReport(reportId)
    }
    // 兼容 response 数据结构
    const res = data.data || data
    currentProjectId.value = res.project_id || currentProjectId.value
    projectName.value = res.project_name || projectName.value
    statistics.value = res.statistics || null
    analysisTableData.value = res.analysis_materials || res.materials || []
    guidancePriceTableData.value = res.guidance_price_materials || []
    const chartData = prepareChartData(res.analysis_materials || [], res.guidance_price_materials || [])
    renderCharts(chartData)
  } catch (e) {
    console.error('加载报告预览失败:', e)
    ElMessage.error('加载报告预览失败')
  }
}

const onDownload = async () => {
  downloading.value = true
  try {
    // 如果已有有效的报告ID，尝试更新并下载（即重新生成但不创建新记录）
    if (reportId && reportId > 0) {
      ElMessage.info('正在更新报告内容，请稍候...')
      
      // 1. 截取图表 (确保下载的是最新的图表)
      const chartImages = await captureCharts()
      
      // 2. 调用生成接口，但传入 report_id 以触发更新逻辑
      // 注意：这里我们需要 projectId。如果页面加载时没有 projectId，需要从详情数据中获取
      // loadPreview() 中已经设置了 projectId.value
      
      const updateParams = {
        project_id: currentProjectId.value, // 确保有项目ID
        report_title: title.value,
        report_type: reportType.value, // 使用配置的类型
        config: {
          include_charts: reportIncludes.value.length > 0 ? reportIncludes.value.includes('charts') : true,
          include_detailed_analysis: reportIncludes.value.length > 0 ? reportIncludes.value.includes('details') : true,
          include_recommendations: reportIncludes.value.length > 0 ? reportIncludes.value.includes('suggestions') : true,
          include_appendices: reportIncludes.value.length > 0 ? reportIncludes.value.includes('attachments') : true
        },
        chart_images: chartImages,
        report_id: reportId // 关键：传入报告ID进行更新
      }
      
      console.log('正在请求更新报告:', updateParams)
      
      const generateResult = await generateReport(updateParams)
      
      if (generateResult) {
         ElMessage.success('报告更新成功，正在下载...')
         await downloadReport(reportId)
      } else {
         throw new Error('报告更新失败')
      }
      
    } else {
      // 已有报告ID的情况，直接下载
      await downloadReport(reportId)
      ElMessage.success('报告下载成功')
    }
  } catch (e) {
    console.error('下载失败:', e)
    ElMessage.error('下载失败：' + (e.message || '未知错误'))
  } finally {
    downloading.value = false
    // 恢复图表大小（以防万一）
    Object.values(chartInstances).forEach(instance => {
      if (instance) instance.resize()
    })
  }
}

const onShare = () => {
  ElMessage.info('分享功能开发中')
}

onMounted(() => {
  loadPreview()
  window.addEventListener('resize', onResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
  disposeCharts()
})

const onResize = () => {
  Object.values(chartInstances).forEach(instance => {
    if (instance) {
      instance.resize()
    }
  })
}
</script>

<style scoped>
.report-detail {
  padding: 20px;
}

.card-header { display: flex; justify-content: space-between; align-items: center; }

.report-content h2 { text-align: center; margin-bottom: 20px; }

.report-meta { background: #f5f5f5; padding: 15px; border-radius: 4px; margin-bottom: 20px; }
.report-meta p { margin: 5px 0; }

.report-summary, .report-charts { margin-bottom: 20px; }
.report-summary h3, .report-charts h3 { border-bottom: 2px solid #409EFF; padding-bottom: 10px; margin-bottom: 15px; }

.report-charts {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.chart-section {
  background: #fff;
  border: 1px solid #eee;
  border-radius: 6px;
  padding: 16px 20px 24px;
}

.chart-header {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 12px;
}

.chart-title {
  font-weight: 600;
  font-size: 16px;
  color: #2c3e50;
}

.chart-desc {
  font-size: 13px;
  color: #777;
}

.chart-box {
  width: 100%;
  height: 28vw;
  min-height: 280px;
  max-height: 360px;
}
</style>
