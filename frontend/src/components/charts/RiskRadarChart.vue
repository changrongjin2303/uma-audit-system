<template>
  <div class="risk-radar-chart">
    <div class="chart-header">
      <h3 class="chart-title">
        <el-icon><Warning /></el-icon>
        风险评估雷达图
      </h3>
      <div class="chart-controls">
        <el-select
          v-model="selectedProject"
          placeholder="选择项目"
          size="small"
          style="width: 180px;"
          @change="handleProjectChange"
        >
          <el-option
            v-for="project in projects"
            :key="project.id"
            :label="project.name"
            :value="project.id"
          />
        </el-select>
      </div>
    </div>

    <BaseChart
      ref="chartRef"
      :option="chartOption"
      :loading="loading"
      :height="450"
      @chart-ready="handleChartReady"
    />

    <!-- 风险指标说明 -->
    <div class="risk-indicators" v-if="riskData">
      <div class="indicators-header">
        <h4>风险指标说明</h4>
      </div>
      <el-row :gutter="16">
        <el-col :span="12" v-for="indicator in riskIndicators" :key="indicator.key">
          <div class="indicator-item">
            <div class="indicator-name">
              <el-icon :class="indicator.iconClass">
                <component :is="indicator.icon" />
              </el-icon>
              {{ indicator.name }}
            </div>
            <div class="indicator-value">
              <el-progress
                :percentage="getRiskScore(indicator.key)"
                :color="getRiskColor(getRiskScore(indicator.key))"
                :show-text="false"
                :stroke-width="8"
              />
              <span class="score">{{ getRiskScore(indicator.key) }}分</span>
            </div>
            <div class="indicator-desc">{{ indicator.description }}</div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 风险建议 -->
    <div class="risk-suggestions" v-if="suggestions.length > 0">
      <h4>风险改进建议</h4>
      <ul class="suggestions-list">
        <li v-for="(suggestion, index) in suggestions" :key="index">
          <el-icon class="suggestion-icon">
            <InfoFilled />
          </el-icon>
          {{ suggestion }}
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue'
import { Warning, InfoFilled, TrendCharts, User, Tools, Clock, Flag, Shop } from '@element-plus/icons-vue'
import BaseChart from './BaseChart.vue'

export default {
  name: 'RiskRadarChart',
  components: {
    BaseChart,
    Warning,
    InfoFilled,
    TrendCharts,
    User,
    Tools,
    Clock,
    Flag,
    Shop
  },
  props: {
    // 风险数据
    riskData: {
      type: Object,
      default: null
    },
    // 项目列表
    projects: {
      type: Array,
      default: () => []
    },
    // 是否加载中
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['project-change'],
  setup(props, { emit }) {
    const chartRef = ref(null)
    const selectedProject = ref(null)

    // 风险指标定义
    const riskIndicators = ref([
      {
        key: 'priceRisk',
        name: '价格风险',
        description: '材料价格偏离市场价格的程度',
        icon: 'TrendCharts',
        iconClass: 'price-risk'
      },
      {
        key: 'qualityRisk',
        name: '质量风险',
        description: '材料质量与标准要求的符合度',
        icon: 'Tools',
        iconClass: 'quality-risk'
      },
      {
        key: 'supplyRisk',
        name: '供应风险',
        description: '材料供应稳定性和可靠性',
        icon: 'Shop',
        iconClass: 'supply-risk'
      },
      {
        key: 'timeRisk',
        name: '时间风险',
        description: '材料交付时间的不确定性',
        icon: 'Clock',
        iconClass: 'time-risk'
      },
      {
        key: 'complianceRisk',
        name: '合规风险',
        description: '材料是否符合相关法规标准',
        icon: 'Flag',
        iconClass: 'compliance-risk'
      },
      {
        key: 'marketRisk',
        name: '市场风险',
        description: '市场波动对材料价格的影响',
        icon: 'TrendCharts',
        iconClass: 'market-risk'
      }
    ])

    // 图表配置
    const chartOption = computed(() => {
      if (!props.riskData) {
        return {}
      }

      const indicators = riskIndicators.value.map(indicator => ({
        name: indicator.name,
        max: 100
      }))

      const data = riskIndicators.value.map(indicator => 
        getRiskScore(indicator.key)
      )

      return {
        title: {
          text: '项目风险评估',
          left: 'center',
          textStyle: {
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          trigger: 'item',
          formatter: (params) => {
            const indicator = riskIndicators.value[params.dataIndex]
            const score = params.value
            return `${indicator.name}: ${score}分<br/>${indicator.description}`
          }
        },
        radar: {
          indicator: indicators,
          name: {
            textStyle: {
              color: '#666',
              fontSize: 12
            }
          },
          splitArea: {
            areaStyle: {
              color: [
                'rgba(64, 158, 255, 0.1)',
                'rgba(64, 158, 255, 0.05)'
              ]
            }
          },
          splitLine: {
            lineStyle: {
              color: '#e6e6e6'
            }
          },
          axisLine: {
            lineStyle: {
              color: '#e6e6e6'
            }
          }
        },
        series: [{
          name: '风险指标',
          type: 'radar',
          data: [{
            value: data,
            name: '当前项目',
            symbol: 'circle',
            symbolSize: 8,
            itemStyle: {
              color: '#409EFF'
            },
            areaStyle: {
              color: 'rgba(64, 158, 255, 0.2)'
            },
            lineStyle: {
              width: 2,
              color: '#409EFF'
            }
          }]
        }]
      }
    })

    // 获取风险分数
    const getRiskScore = (riskKey) => {
      if (!props.riskData || !props.riskData[riskKey]) return 0
      return Math.round(props.riskData[riskKey] * 100) / 100
    }

    // 获取风险颜色
    const getRiskColor = (score) => {
      if (score >= 80) return '#F56C6C'
      if (score >= 60) return '#E6A23C'
      if (score >= 40) return '#409EFF'
      return '#67C23A'
    }

    // 风险改进建议
    const suggestions = computed(() => {
      if (!props.riskData) return []

      const result = []
      
      if (getRiskScore('priceRisk') > 70) {
        result.push('建议重新评估材料价格，寻找更有竞争力的供应商')
      }
      
      if (getRiskScore('qualityRisk') > 70) {
        result.push('建议加强材料质量检测，确保符合项目标准')
      }
      
      if (getRiskScore('supplyRisk') > 70) {
        result.push('建议建立备用供应商，确保供应链稳定')
      }
      
      if (getRiskScore('timeRisk') > 70) {
        result.push('建议优化材料采购计划，预留充足交付时间')
      }
      
      if (getRiskScore('complianceRisk') > 70) {
        result.push('建议核实材料合规性，确保符合相关法规要求')
      }
      
      if (getRiskScore('marketRisk') > 70) {
        result.push('建议关注市场动态，适时调整采购策略')
      }

      return result
    })

    // 处理项目变化
    const handleProjectChange = (projectId) => {
      emit('project-change', projectId)
    }

    // 处理图表就绪事件
    const handleChartReady = (chart) => {
      console.log('风险雷达图初始化完成')
    }

    // 初始化
    onMounted(() => {
      if (props.projects.length > 0 && !selectedProject.value) {
        selectedProject.value = props.projects[0].id
      }
    })

    return {
      chartRef,
      selectedProject,
      riskIndicators,
      chartOption,
      suggestions,
      getRiskScore,
      getRiskColor,
      handleProjectChange,
      handleChartReady
    }
  }
}
</script>

<style scoped>
.risk-radar-chart {
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

.risk-indicators {
  padding: 20px;
  border-top: 1px solid #ebeef5;
}

.indicators-header h4 {
  margin: 0 0 16px 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.indicator-item {
  padding: 12px;
  background: #f9fafc;
  border-radius: 6px;
  margin-bottom: 12px;
}

.indicator-name {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 8px;
}

.indicator-name .el-icon {
  font-size: 14px;
}

.price-risk { color: #409EFF; }
.quality-risk { color: #67C23A; }
.supply-risk { color: #E6A23C; }
.time-risk { color: #F56C6C; }
.compliance-risk { color: #909399; }
.market-risk { color: #409EFF; }

.indicator-value {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 6px;
}

.indicator-value .el-progress {
  flex: 1;
}

.score {
  font-size: 12px;
  font-weight: 500;
  color: #303133;
  min-width: 40px;
  text-align: right;
}

.indicator-desc {
  font-size: 11px;
  color: #909399;
  line-height: 1.4;
}

.risk-suggestions {
  padding: 20px;
  background: #fff7e6;
  border-top: 1px solid #ebeef5;
}

.risk-suggestions h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.suggestions-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.suggestions-list li {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 8px 0;
  font-size: 13px;
  color: #606266;
  line-height: 1.4;
}

.suggestion-icon {
  color: #E6A23C;
  font-size: 14px;
  margin-top: 2px;
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

  .risk-indicators .el-col {
    margin-bottom: 8px;
  }
}

/* 深色主题样式 */
.dark .risk-radar-chart {
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

.dark .risk-indicators {
  background: #2d2d2d !important;
  border-top-color: #4c4d4f !important;
}

.dark .risk-item {
  color: #e4e7ed !important;
}

.dark .risk-name {
  color: #e4e7ed !important;
}

.dark .risk-value {
  color: #e4e7ed !important;
}

.dark .risk-suggestions {
  background: #2f2a1f !important;
  border-top-color: #4c4d4f !important;
}

.dark .risk-suggestions h4 {
  color: #e4e7ed !important;
}

.dark .suggestions-list li {
  color: #c0c4cc !important;
}

/* 风险指标卡片深色主题 */
.dark .indicator-item {
  background: #2d2d2d !important;
  color: #e4e7ed !important;
}

.dark .indicator-name {
  color: #e4e7ed !important;
}

.dark .indicator-desc {
  color: #909399 !important;
}

.dark .score {
  color: #e4e7ed !important;
}

.dark .indicators-header h4 {
  color: #e4e7ed !important;
}
</style>