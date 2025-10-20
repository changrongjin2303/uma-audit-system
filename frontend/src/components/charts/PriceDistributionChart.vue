<template>
  <div class="price-distribution-chart">
    <div class="chart-header">
      <h3 class="chart-title">
        <el-icon><TrendCharts /></el-icon>
        价格分布分析
      </h3>
      <div class="chart-controls">
        <el-select
          v-model="chartType"
          placeholder="选择图表类型"
          size="small"
          style="width: 120px;"
        >
          <el-option label="柱状图" value="bar" />
          <el-option label="折线图" value="line" />
          <el-option label="饼图" value="pie" />
          <el-option label="散点图" value="scatter" />
        </el-select>
        
        <el-select
          v-model="dataSource"
          placeholder="数据来源"
          size="small"
          style="width: 120px; margin-left: 8px;"
        >
          <el-option label="全部" value="all" />
          <el-option label="政府信息价" value="government" />
          <el-option label="市场调研" value="market" />
          <el-option label="供应商报价" value="supplier" />
          <el-option label="历史数据" value="historical" />
        </el-select>
      </div>
    </div>

    <BaseChart
      ref="chartRef"
      :option="chartOption"
      :loading="loading"
      :height="400"
      :theme="isDark ? 'dark' : 'light'"
      @chart-click="handleChartClick"
      @chart-ready="handleChartReady"
    />

    <!-- 统计信息 -->
    <div class="chart-stats" v-if="statistics">
      <el-row :gutter="16">
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">{{ statistics.totalCount }}</div>
            <div class="stat-label">材料总数</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">¥{{ formatPrice(statistics.avgPrice) }}</div>
            <div class="stat-label">平均价格</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">{{ statistics.highRiskCount }}</div>
            <div class="stat-label">高风险材料</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">{{ (statistics.priceDeviationRate * 100).toFixed(1) }}%</div>
            <div class="stat-label">价格偏差率</div>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue'
import { TrendCharts } from '@element-plus/icons-vue'
import BaseChart from './BaseChart.vue'
import { RISK_LEVELS, DATA_SOURCES } from '@/config'
import { useAppStore } from '@/store/app'

export default {
  name: 'PriceDistributionChart',
  components: {
    BaseChart,
    TrendCharts
  },
  props: {
    // 价格数据
    data: {
      type: Array,
      default: () => []
    },
    // 是否加载中
    loading: {
      type: Boolean,
      default: false
    },
    // 统计信息
    statistics: {
      type: Object,
      default: null
    }
  },
  emits: ['material-click', 'data-filter'],
  setup(props, { emit }) {
    const chartRef = ref(null)
    const chartType = ref('bar')
    const dataSource = ref('all')
    const appStore = useAppStore()
    
    // 检测当前主题
    const isDark = computed(() => appStore.theme === 'dark')

    // 过滤后的数据
    const filteredData = computed(() => {
      if (!props.data || props.data.length === 0) return []
      
      let data = [...props.data]
      
      if (dataSource.value !== 'all') {
        data = data.filter(item => item.dataSource === dataSource.value)
      }
      
      return data
    })

    // 图表配置
    const chartOption = computed(() => {
      const data = filteredData.value
      
      if (!data || data.length === 0) {
        return {}
      }

      switch (chartType.value) {
        case 'bar':
          return createBarChart(data)
        case 'line':
          return createLineChart(data)
        case 'pie':
          return createPieChart(data)
        case 'scatter':
          return createScatterChart(data)
        default:
          return createBarChart(data)
      }
    })

    // 创建柱状图配置
    const createBarChart = (data) => {
      // 按价格区间分组
      const priceRanges = groupByPriceRange(data)
      
      return {
        title: {
          text: '材料价格分布',
          left: 'center',
          textStyle: {
            fontSize: 16,
            fontWeight: 'bold',
            color: isDark.value ? '#e4e7ed' : '#303133'
          }
        },
        tooltip: {
          trigger: 'axis',
          formatter: (params) => {
            const param = params[0]
            return `价格区间: ${param.name}<br/>
                   材料数量: ${param.value}<br/>
                   占比: ${((param.value / data.length) * 100).toFixed(1)}%`
          }
        },
        xAxis: {
          type: 'category',
          data: priceRanges.map(r => r.range),
          axisLabel: {
            rotate: 45,
            color: isDark.value ? '#e4e7ed' : '#606266'
          },
          axisLine: {
            lineStyle: {
              color: isDark.value ? '#4c4d4f' : '#dcdfe6'
            }
          }
        },
        yAxis: {
          type: 'value',
          name: '材料数量',
          axisLabel: {
            formatter: '{value}',
            color: isDark.value ? '#e4e7ed' : '#606266'
          },
          axisLine: {
            lineStyle: {
              color: isDark.value ? '#4c4d4f' : '#dcdfe6'
            }
          },
          splitLine: {
            lineStyle: {
              color: isDark.value ? '#4c4d4f' : '#dcdfe6'
            }
          }
        },
        series: [{
          name: '材料数量',
          type: 'bar',
          data: priceRanges.map(r => ({
            value: r.count,
            itemStyle: {
              color: getPriceRangeColor(r.risk)
            }
          })),
          itemStyle: {
            borderRadius: [4, 4, 0, 0]
          }
        }],
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        }
      }
    }

    // 创建折线图配置
    const createLineChart = (data) => {
      // 按时间排序
      const sortedData = [...data].sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt))
      
      return {
        title: {
          text: '价格趋势分析',
          left: 'center'
        },
        tooltip: {
          trigger: 'axis',
          formatter: (params) => {
            const param = params[0]
            const item = sortedData[param.dataIndex]
            return `材料: ${item.name}<br/>
                   价格: ¥${formatPrice(item.price)}<br/>
                   时间: ${formatDate(item.createdAt)}`
          }
        },
        xAxis: {
          type: 'category',
          data: sortedData.map((item, index) => index + 1),
          name: '材料序号'
        },
        yAxis: {
          type: 'value',
          name: '价格 (元)',
          axisLabel: {
            formatter: '¥{value}'
          }
        },
        series: [{
          name: '材料价格',
          type: 'line',
          data: sortedData.map(item => item.price),
          smooth: true,
          itemStyle: {
            color: '#409EFF'
          },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0, y: 0, x2: 0, y2: 1,
              colorStops: [
                { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
                { offset: 1, color: 'rgba(64, 158, 255, 0.05)' }
              ]
            }
          }
        }],
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        }
      }
    }

    // 创建饼图配置
    const createPieChart = (data) => {
      const riskGroups = groupByRiskLevel(data)
      
      return {
        title: {
          text: '风险等级分布',
          left: 'center'
        },
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          left: 'left'
        },
        series: [{
          name: '风险等级',
          type: 'pie',
          radius: '50%',
          data: riskGroups.map(group => ({
            value: group.count,
            name: group.label,
            itemStyle: {
              color: group.color
            }
          })),
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }]
      }
    }

    // 创建散点图配置
    const createScatterChart = (data) => {
      return {
        title: {
          text: '价格与风险关系',
          left: 'center'
        },
        tooltip: {
          trigger: 'item',
          formatter: (params) => {
            const item = data[params.dataIndex]
            return `材料: ${item.name}<br/>
                   价格: ¥${formatPrice(item.price)}<br/>
                   风险分数: ${item.riskScore}<br/>
                   风险等级: ${getRiskLabel(item.riskLevel)}`
          }
        },
        xAxis: {
          type: 'value',
          name: '价格 (元)',
          axisLabel: {
            formatter: '¥{value}'
          }
        },
        yAxis: {
          type: 'value',
          name: '风险分数',
          min: 0,
          max: 100
        },
        series: [{
          name: '材料',
          type: 'scatter',
          data: data.map(item => ({
            value: [item.price, item.riskScore || 0],
            itemStyle: {
              color: getRiskColor(item.riskLevel)
            }
          })),
          symbolSize: 8
        }],
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        }
      }
    }

    // 按价格区间分组
    const groupByPriceRange = (data) => {
      const ranges = [
        { min: 0, max: 100, range: '0-100元', risk: 'low' },
        { min: 100, max: 500, range: '100-500元', risk: 'low' },
        { min: 500, max: 1000, range: '500-1000元', risk: 'medium' },
        { min: 1000, max: 5000, range: '1000-5000元', risk: 'medium' },
        { min: 5000, max: 10000, range: '5000-10000元', risk: 'high' },
        { min: 10000, max: Infinity, range: '10000元以上', risk: 'high' }
      ]

      return ranges.map(range => ({
        ...range,
        count: data.filter(item => 
          item.price >= range.min && item.price < range.max
        ).length
      })).filter(range => range.count > 0)
    }

    // 按风险等级分组
    const groupByRiskLevel = (data) => {
      const riskCounts = {}
      
      data.forEach(item => {
        const level = item.riskLevel || 'normal'
        riskCounts[level] = (riskCounts[level] || 0) + 1
      })

      return Object.keys(riskCounts).map(level => ({
        level,
        count: riskCounts[level],
        label: getRiskLabel(level),
        color: getRiskColor(level)
      }))
    }

    // 获取价格区间颜色
    const getPriceRangeColor = (risk) => {
      const colors = {
        normal: '#67C23A',
        low: '#E6A23C',
        medium: '#E6A23C',
        high: '#F56C6C'
      }
      return colors[risk] || '#409EFF'
    }

    // 获取风险等级标签
    const getRiskLabel = (level) => {
      return RISK_LEVELS[level]?.label || level
    }

    // 获取风险等级颜色
    const getRiskColor = (level) => {
      const colorMap = {
        normal: '#67C23A',
        low: '#E6A23C',
        medium: '#E6A23C',
        high: '#F56C6C',
        critical: '#F56C6C'
      }
      return colorMap[level] || '#409EFF'
    }

    // 格式化价格
    const formatPrice = (price) => {
      if (typeof price !== 'number') return '0.00'
      return price.toLocaleString('zh-CN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })
    }

    // 格式化日期
    const formatDate = (date) => {
      return new Date(date).toLocaleDateString('zh-CN')
    }

    // 处理图表点击事件
    const handleChartClick = (params) => {
      if (chartType.value === 'scatter') {
        const material = filteredData.value[params.dataIndex]
        emit('material-click', material)
      }
    }

    // 处理图表就绪事件
    const handleChartReady = (chart) => {
      console.log('价格分布图表初始化完成')
    }

    // 监听筛选条件变化
    watch([chartType, dataSource], () => {
      emit('data-filter', {
        chartType: chartType.value,
        dataSource: dataSource.value
      })
    })

    return {
      chartRef,
      chartType,
      dataSource,
      chartOption,
      handleChartClick,
      handleChartReady,
      formatPrice
    }
  }
}
</script>

<style scoped>
.price-distribution-chart {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #ebeef5;
}

.chart-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.chart-controls {
  display: flex;
  align-items: center;
}

.chart-stats {
  padding: 16px 20px;
  background: #f9fafc;
  border-top: 1px solid #ebeef5;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: #909399;
}

@media (max-width: 768px) {
  .chart-header {
    flex-direction: column;
    gap: 12px;
  }

  .chart-controls {
    width: 100%;
    justify-content: center;
  }

  .chart-stats .el-col {
    margin-bottom: 12px;
  }
}

/* 深色主题样式 */
.dark .price-distribution-chart {
  background: #2d2d2d !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
}

.dark .chart-header {
  border-bottom-color: #4c4d4f !important;
  background: #2d2d2d !important;
}

.dark .chart-title {
  color: #e4e7ed !important;
}

.dark .chart-stats {
  background: #2d2d2d !important;
  border-top-color: #4c4d4f !important;
}

.dark .stat-item {
  color: #e4e7ed !important;
}

.dark .stat-value {
  color: #409EFF !important;
}

.dark .stat-label {
  color: #909399 !important;
}
</style>
