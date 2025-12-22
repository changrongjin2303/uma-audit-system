<template>
  <div class="hidden-chart-generator" style="position: fixed; top: 0; left: -9999px; opacity: 0; visibility: visible; z-index: -1;">
    <!-- 渲染容器 -->
    <div ref="containerRef" class="chart-container" style="width: 700px; background: #fff; padding: 20px;">
      <!-- 风险分布图 -->
      <div class="chart-section" style="width: 700px; height: 400px; background: #fff; padding: 20px; margin-bottom: 20px;">
        <div ref="riskChartRef" style="width: 100%; height: 100%;"></div>
      </div>
      
      <!-- 差异TOP10 -->
      <div class="chart-section" style="width: 700px; height: 400px; background: #fff; padding: 20px; margin-bottom: 20px;">
        <div ref="varianceChartRef" style="width: 100%; height: 100%;"></div>
      </div>
      
      <!-- 总额对比 -->
      <div class="chart-section" style="width: 700px; height: 400px; background: #fff; padding: 20px;">
        <div ref="priceDistChartRef" style="width: 100%; height: 100%;"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import html2canvas from 'html2canvas'
import { previewReportByProject } from '@/api/reports'
import { prepareChartData } from '@/utils/chartUtils'

const containerRef = ref(null)
const riskChartRef = ref(null)
const varianceChartRef = ref(null)
const priceDistChartRef = ref(null)

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
      animation: false, // 禁用动画以加快截图
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
      animation: false,
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
      animation: false,
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

const captureImages = async () => {
  const images = {}
  
  const processChart = async (chartRef, key) => {
    if (!chartRef || !chartRef.parentElement) {
      console.warn(`Chart ref for ${key} not found`)
      return
    }
    const container = chartRef.parentElement
    
    try {
      // 临时确保可见性，虽然我们在样式中用了 opacity: 0，但为了 html2canvas 稳健性
      // html2canvas 应该能处理 opacity: 0，但不能处理 visibility: hidden 或 display: none
      
      const canvas = await html2canvas(container, {
        scale: 2,
        useCORS: true,
        backgroundColor: '#ffffff',
        logging: false,
        onclone: (clonedDoc) => {
          // 确保克隆的元素可见
          const clonedEl = clonedDoc.querySelector('.hidden-chart-generator')
          if (clonedEl) {
            clonedEl.style.opacity = '1'
            clonedEl.style.visibility = 'visible'
          }
        }
      })
      images[key] = canvas.toDataURL('image/jpeg', 0.8)
      console.log(`Captured chart ${key}, size: ${images[key].length}`)
    } catch (e) {
      console.error(`Capture failed for ${key}:`, e)
    }
  }
  
  await processChart(riskChartRef.value, 'risk')
  await processChart(varianceChartRef.value, 'adjustment')
  await processChart(priceDistChartRef.value, 'totals')
  
  return images
}

// 对外暴露的方法
const generateImages = async (projectId) => {
  try {
    // 1. 获取数据
    const data = await previewReportByProject(projectId)
    const res = data.data || data
    
    // 2. 准备图表数据
    const chartData = prepareChartData(
      res.analysis_materials || res.materials || [], 
      res.guidance_price_materials || []
    )
    
    // 3. 渲染图表
    renderCharts(chartData)
    
    // 4. 等待渲染完成（增加等待时间确保渲染）
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // 5. 截图
    return await captureImages()
    
  } catch (error) {
    console.error('Hidden chart generation failed:', error)
    return null
  } finally {
    disposeCharts()
  }
}

defineExpose({
  generateImages
})

onBeforeUnmount(() => {
  disposeCharts()
})
</script>
