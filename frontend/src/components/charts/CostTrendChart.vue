<template>
  <div class="cost-trend-chart">
    <div class="chart-header">
      <h3 class="chart-title">
        <el-icon><TrendCharts /></el-icon>
        成本趋势分析
      </h3>
      <div class="chart-controls">
        <el-radio-group v-model="timeRange" size="small">
          <el-radio-button label="week">近一周</el-radio-button>
          <el-radio-button label="month">近一月</el-radio-button>
          <el-radio-button label="quarter">近一季</el-radio-button>
          <el-radio-button label="year">近一年</el-radio-button>
        </el-radio-group>
        
        <el-select
          v-model="selectedCategories"
          multiple
          placeholder="选择材料分类"
          size="small"
          style="width: 200px; margin-left: 12px;"
        >
          <el-option
            v-for="category in materialCategories"
            :key="category.key"
            :label="category.label"
            :value="category.key"
          />
        </el-select>
      </div>
    </div>

    <BaseChart
      ref="chartRef"
      :option="chartOption"
      :loading="loading"
      :height="400"
      @chart-click="handleChartClick"
      @chart-ready="handleChartReady"
    />

    <!-- 趋势统计 -->
    <div class="trend-stats" v-if="trendStats">
      <el-row :gutter="16">
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">¥{{ formatPrice(trendStats.currentCost) }}</div>
            <div class="stat-label">当前成本</div>
            <div class="stat-change" :class="trendStats.costChange >= 0 ? 'increase' : 'decrease'">
              <el-icon><component :is="trendStats.costChange >= 0 ? 'CaretTop' : 'CaretBottom'" /></el-icon>
              {{ Math.abs(trendStats.costChange).toFixed(1) }}%
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">¥{{ formatPrice(trendStats.avgCost) }}</div>
            <div class="stat-label">平均成本</div>
            <div class="stat-change" :class="trendStats.avgChange >= 0 ? 'increase' : 'decrease'">
              <el-icon><component :is="trendStats.avgChange >= 0 ? 'CaretTop' : 'CaretBottom'" /></el-icon>
              {{ Math.abs(trendStats.avgChange).toFixed(1) }}%
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">{{ trendStats.volatility.toFixed(1) }}%</div>
            <div class="stat-label">成本波动率</div>
            <div class="stat-desc">{{ getVolatilityDesc(trendStats.volatility) }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">{{ trendStats.predictedTrend }}</div>
            <div class="stat-label">预测趋势</div>
            <div class="stat-desc">{{ getTrendDesc(trendStats.predictedTrend) }}</div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 分析结果 -->
    <div class="trend-analysis" v-if="analysisResult">
      <h4>趋势分析结果</h4>
      <div class="analysis-content">
        <div class="analysis-item">
          <strong>主要影响因素：</strong>
          <el-tag
            v-for="factor in analysisResult.factors"
            :key="factor"
            size="small"
            type="info"
            style="margin-left: 4px;"
          >
            {{ factor }}
          </el-tag>
        </div>
        
        <div class="analysis-item">
          <strong>价格预测：</strong>
          <span :class="getPredictionClass(analysisResult.prediction)">
            {{ analysisResult.prediction }}
          </span>
        </div>
        
        <div class="analysis-item">
          <strong>建议措施：</strong>
          <ul class="recommendations">
            <li v-for="rec in analysisResult.recommendations" :key="rec">
              {{ rec }}
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { TrendCharts, CaretTop, CaretBottom } from '@element-plus/icons-vue'
import BaseChart from './BaseChart.vue'
import { MATERIAL_CATEGORIES } from '@/config'

export default {
  name: 'CostTrendChart',
  components: {
    BaseChart,
    TrendCharts,
    CaretTop,
    CaretBottom
  },
  props: {
    // 趋势数据
    data: {
      type: Array,
      default: () => []
    },
    // 趋势统计
    trendStats: {
      type: Object,
      default: null
    },
    // 分析结果
    analysisResult: {
      type: Object,
      default: null
    },
    // 是否加载中
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['time-range-change', 'category-change', 'data-point-click'],
  setup(props, { emit }) {
    const chartRef = ref(null)
    const timeRange = ref('month')
    const selectedCategories = ref(['building', 'decoration'])

    // 材料分类
    const materialCategories = computed(() => {
      return Object.keys(MATERIAL_CATEGORIES).map(key => ({
        key,
        label: MATERIAL_CATEGORIES[key].label
      }))
    })

    // 过滤后的数据
    const filteredData = computed(() => {
      if (!props.data || props.data.length === 0) return []
      
      return props.data.filter(item => {
        // 按时间范围过滤
        const itemDate = new Date(item.date)
        const now = new Date()
        let timeThreshold = new Date()
        
        switch (timeRange.value) {
          case 'week':
            timeThreshold.setDate(now.getDate() - 7)
            break
          case 'month':
            timeThreshold.setMonth(now.getMonth() - 1)
            break
          case 'quarter':
            timeThreshold.setMonth(now.getMonth() - 3)
            break
          case 'year':
            timeThreshold.setFullYear(now.getFullYear() - 1)
            break
          default:
            timeThreshold.setMonth(now.getMonth() - 1)
        }
        
        const inTimeRange = itemDate >= timeThreshold
        const inCategory = selectedCategories.value.length === 0 || 
                          selectedCategories.value.includes(item.category)
        
        return inTimeRange && inCategory
      })
    })

    // 图表配置
    const chartOption = computed(() => {
      const data = filteredData.value
      
      if (!data || data.length === 0) {
        return {}
      }

      // 按日期排序
      const sortedData = [...data].sort((a, b) => new Date(a.date) - new Date(b.date))
      
      // 按分类分组
      const seriesData = {}
      sortedData.forEach(item => {
        if (!seriesData[item.category]) {
          seriesData[item.category] = []
        }
        seriesData[item.category].push({
          date: item.date,
          cost: item.cost,
          name: item.name
        })
      })

      // 生成时间轴
      const dates = [...new Set(sortedData.map(item => item.date))].sort()
      
      // 生成系列数据
      const series = Object.keys(seriesData).map(category => {
        const categoryData = dates.map(date => {
          const item = seriesData[category].find(d => d.date === date)
          return item ? item.cost : null
        })

        return {
          name: MATERIAL_CATEGORIES[category]?.label || category,
          type: 'line',
          data: categoryData,
          smooth: true,
          symbol: 'circle',
          symbolSize: 6,
          itemStyle: {
            color: getCategoryColor(category)
          },
          lineStyle: {
            width: 2
          },
          connectNulls: false
        }
      })

      return {
        title: {
          text: '成本趋势变化',
          left: 'center',
          textStyle: {
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross'
          },
          formatter: (params) => {
            let html = `<div style="font-weight: bold; margin-bottom: 4px;">${params[0].axisValue}</div>`
            
            params.forEach(param => {
              if (param.value !== null) {
                html += `<div style="display: flex; align-items: center; gap: 8px;">
                  <span style="display: inline-block; width: 10px; height: 10px; background: ${param.color}; border-radius: 50%;"></span>
                  <span>${param.seriesName}: ¥${formatPrice(param.value)}</span>
                </div>`
              }
            })
            
            return html
          }
        },
        legend: {
          top: 30,
          data: series.map(s => s.name)
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '8%',
          top: '15%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: dates.map(date => formatDate(date)),
          axisLabel: {
            rotate: 45,
            fontSize: 11
          }
        },
        yAxis: {
          type: 'value',
          name: '成本 (元)',
          axisLabel: {
            formatter: '¥{value}'
          }
        },
        series: series,
        dataZoom: [{
          type: 'slider',
          show: true,
          xAxisIndex: [0],
          start: 0,
          end: 100
        }]
      }
    })

    // 获取分类颜色
    const getCategoryColor = (category) => {
      const colors = {
        building: '#409EFF',
        decoration: '#67C23A',
        machinery: '#E6A23C',
        labor: '#F56C6C',
        other: '#909399'
      }
      return colors[category] || '#409EFF'
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
    const formatDate = (dateStr) => {
      const date = new Date(dateStr)
      return date.toLocaleDateString('zh-CN', {
        month: 'short',
        day: 'numeric'
      })
    }

    // 获取波动率描述
    const getVolatilityDesc = (volatility) => {
      if (volatility < 5) return '低波动'
      if (volatility < 15) return '中等波动'
      return '高波动'
    }

    // 获取趋势描述
    const getTrendDesc = (trend) => {
      const descriptions = {
        'up': '价格上涨',
        'down': '价格下跌',
        'stable': '价格稳定',
        'volatile': '价格波动'
      }
      return descriptions[trend] || '未知'
    }

    // 获取预测样式类
    const getPredictionClass = (prediction) => {
      if (prediction.includes('上涨') || prediction.includes('增长')) return 'prediction-up'
      if (prediction.includes('下跌') || prediction.includes('下降')) return 'prediction-down'
      return 'prediction-stable'
    }

    // 处理图表点击事件
    const handleChartClick = (params) => {
      emit('data-point-click', {
        category: params.seriesName,
        date: filteredData.value[params.dataIndex]?.date,
        cost: params.value
      })
    }

    // 处理图表就绪事件
    const handleChartReady = (chart) => {
      console.log('成本趋势图初始化完成')
    }

    // 监听参数变化
    watch(timeRange, (newRange) => {
      emit('time-range-change', newRange)
    })

    watch(selectedCategories, (newCategories) => {
      emit('category-change', newCategories)
    }, { deep: true })

    return {
      chartRef,
      timeRange,
      selectedCategories,
      materialCategories,
      chartOption,
      formatPrice,
      getVolatilityDesc,
      getTrendDesc,
      getPredictionClass,
      handleChartClick,
      handleChartReady
    }
  }
}
</script>

<style scoped>
.cost-trend-chart {
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
  flex-wrap: wrap;
  gap: 8px;
}

.trend-stats {
  padding: 16px 20px;
  background: #f9fafc;
  border-top: 1px solid #ebeef5;
}

.stat-item {
  text-align: center;
  padding: 12px;
  background: white;
  border-radius: 6px;
}

.stat-value {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 6px;
}

.stat-change {
  font-size: 12px;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2px;
}

.stat-change.increase {
  color: #F56C6C;
}

.stat-change.decrease {
  color: #67C23A;
}

.stat-desc {
  font-size: 11px;
  color: #909399;
}

.trend-analysis {
  padding: 20px;
  border-top: 1px solid #ebeef5;
}

.trend-analysis h4 {
  margin: 0 0 16px 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.analysis-content {
  font-size: 13px;
  line-height: 1.6;
}

.analysis-item {
  margin-bottom: 12px;
}

.analysis-item strong {
  color: #303133;
}

.prediction-up {
  color: #F56C6C;
  font-weight: 500;
}

.prediction-down {
  color: #67C23A;
  font-weight: 500;
}

.prediction-stable {
  color: #409EFF;
  font-weight: 500;
}

.recommendations {
  margin: 6px 0 0 20px;
  color: #606266;
}

.recommendations li {
  margin-bottom: 4px;
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

  .trend-stats .el-col {
    margin-bottom: 12px;
  }
}

/* 深色主题样式 */
.dark .cost-trend-chart {
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

.dark .trend-stats {
  background: #2d2d2d !important;
  border-top-color: #4c4d4f !important;
}

.dark .stat-item {
  background: #2d2d2d !important;
  color: #e4e7ed !important;
}

.dark .stat-value {
  color: #e4e7ed !important;
}

.dark .stat-label {
  color: #909399 !important;
}

.dark .analysis-section {
  background: #2d2d2d !important;
  border-top-color: #4c4d4f !important;
}

.dark .analysis-title {
  color: #e4e7ed !important;
}

.dark .factors,
.dark .prediction,
.dark .recommendations {
  color: #c0c4cc !important;
}

/* 统计变化指示器 */
.dark .stat-change {
  color: #e4e7ed !important;
}

.dark .stat-change.increase {
  color: #67C23A !important;
}

.dark .stat-change.decrease {
  color: #F56C6C !important;
}
</style>