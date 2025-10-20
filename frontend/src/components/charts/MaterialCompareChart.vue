<template>
  <div class="material-compare-chart">
    <div class="chart-header">
      <h3 class="chart-title">
        <el-icon><DataAnalysis /></el-icon>
        材料对比分析
      </h3>
      <div class="chart-controls">
        <el-select
          v-model="compareType"
          placeholder="对比类型"
          size="small"
          style="width: 120px;"
        >
          <el-option label="价格对比" value="price" />
          <el-option label="质量对比" value="quality" />
          <el-option label="供应商对比" value="supplier" />
          <el-option label="综合对比" value="comprehensive" />
        </el-select>

        <el-button
          type="primary"
          size="small"
          @click="showMaterialSelector = true"
          style="margin-left: 8px;"
        >
          <el-icon><Plus /></el-icon>
          添加材料
        </el-button>
      </div>
    </div>

    <!-- 已选择的材料列表 -->
    <div class="selected-materials" v-if="selectedMaterials.length > 0">
      <div class="materials-header">
        <span>对比材料 ({{ selectedMaterials.length }})</span>
        <el-button type="text" size="small" @click="clearSelection">
          清空
        </el-button>
      </div>
      <div class="materials-list">
        <el-tag
          v-for="material in selectedMaterials"
          :key="material.id"
          closable
          @close="removeMaterial(material.id)"
          style="margin: 0 8px 8px 0;"
        >
          {{ material.name }}
        </el-tag>
      </div>
    </div>

    <BaseChart
      ref="chartRef"
      :option="chartOption"
      :loading="loading"
      :height="450"
      @chart-click="handleChartClick"
      @chart-ready="handleChartReady"
    />

    <!-- 对比数据表格 -->
    <div class="compare-table" v-if="selectedMaterials.length > 0">
      <el-table :data="comparisonData" border size="small">
        <el-table-column prop="name" label="材料名称" width="200" fixed="left" />
        <el-table-column prop="price" label="价格 (元)" sortable>
          <template #default="{ row }">
            ¥{{ formatPrice(row.price) }}
          </template>
        </el-table-column>
        <el-table-column prop="supplier" label="供应商" width="120" />
        <el-table-column prop="quality" label="质量等级" width="100">
          <template #default="{ row }">
            <el-rate v-model="row.quality" disabled size="small" />
          </template>
        </el-table-column>
        <el-table-column prop="deliveryTime" label="交付时间" width="100" />
        <el-table-column prop="riskLevel" label="风险等级" width="100">
          <template #default="{ row }">
            <el-tag :type="getRiskTagType(row.riskLevel)">
              {{ getRiskLabel(row.riskLevel) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="score" label="综合评分" width="120" sortable>
          <template #default="{ row }">
            <div class="score-cell">
              <el-progress
                :percentage="row.score"
                :color="getScoreColor(row.score)"
                :show-text="false"
                :stroke-width="6"
              />
              <span class="score-value">{{ row.score }}分</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="recommendation" label="建议" min-width="150">
          <template #default="{ row }">
            <el-icon :color="getRecommendationColor(row.recommendation)">
              <component :is="getRecommendationIcon(row.recommendation)" />
            </el-icon>
            {{ row.recommendation }}
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 材料选择弹窗 -->
    <el-dialog
      v-model="showMaterialSelector"
      title="选择对比材料"
      width="60%"
      :before-close="handleSelectorClose"
    >
      <div class="material-selector">
        <div class="selector-header">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索材料名称"
            clearable
            prefix-icon="Search"
            style="width: 300px;"
          />
          <el-select
            v-model="categoryFilter"
            placeholder="材料分类"
            clearable
            style="width: 150px; margin-left: 12px;"
          >
            <el-option
              v-for="category in materialCategories"
              :key="category.key"
              :label="category.label"
              :value="category.key"
            />
          </el-select>
        </div>

        <el-table
          ref="materialTable"
          :data="filteredAvailableMaterials"
          @selection-change="handleSelectionChange"
          height="400"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="name" label="材料名称" />
          <el-table-column prop="category" label="分类">
            <template #default="{ row }">
              {{ getCategoryLabel(row.category) }}
            </template>
          </el-table-column>
          <el-table-column prop="price" label="价格">
            <template #default="{ row }">
              ¥{{ formatPrice(row.price) }}
            </template>
          </el-table-column>
          <el-table-column prop="supplier" label="供应商" />
        </el-table>
      </div>

      <template #footer>
        <el-button @click="showMaterialSelector = false">取消</el-button>
        <el-button type="primary" @click="confirmSelection">
          确定 ({{ tempSelectedMaterials.length }})
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { DataAnalysis, Plus, Check, Warning, Close, Search } from '@element-plus/icons-vue'
import BaseChart from './BaseChart.vue'
import { MATERIAL_CATEGORIES, RISK_LEVELS } from '@/config'

export default {
  name: 'MaterialCompareChart',
  components: {
    BaseChart,
    DataAnalysis,
    Plus,
    Check,
    Warning,
    Close,
    Search
  },
  props: {
    // 可选材料列表
    availableMaterials: {
      type: Array,
      default: () => []
    },
    // 是否加载中
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['materials-change', 'compare-type-change'],
  setup(props, { emit }) {
    const chartRef = ref(null)
    const compareType = ref('price')
    const selectedMaterials = ref([])
    const showMaterialSelector = ref(false)
    const tempSelectedMaterials = ref([])
    const searchKeyword = ref('')
    const categoryFilter = ref('')
    const materialTable = ref(null)

    // 材料分类
    const materialCategories = computed(() => {
      return Object.keys(MATERIAL_CATEGORIES).map(key => ({
        key,
        label: MATERIAL_CATEGORIES[key].label
      }))
    })

    // 过滤后的可选材料
    const filteredAvailableMaterials = computed(() => {
      let materials = props.availableMaterials.filter(m => 
        !selectedMaterials.value.some(sm => sm.id === m.id)
      )

      if (searchKeyword.value) {
        materials = materials.filter(m => 
          m.name.toLowerCase().includes(searchKeyword.value.toLowerCase())
        )
      }

      if (categoryFilter.value) {
        materials = materials.filter(m => m.category === categoryFilter.value)
      }

      return materials
    })

    // 对比数据
    const comparisonData = computed(() => {
      return selectedMaterials.value.map(material => {
        // 计算综合评分
        const score = calculateComprehensiveScore(material)
        
        return {
          ...material,
          score,
          recommendation: getRecommendation(material, score)
        }
      })
    })

    // 图表配置
    const chartOption = computed(() => {
      const materials = selectedMaterials.value
      
      if (!materials || materials.length === 0) {
        return {}
      }

      switch (compareType.value) {
        case 'price':
          return createPriceChart(materials)
        case 'quality':
          return createQualityChart(materials)
        case 'supplier':
          return createSupplierChart(materials)
        case 'comprehensive':
          return createComprehensiveChart(materials)
        default:
          return createPriceChart(materials)
      }
    })

    // 创建价格对比图
    const createPriceChart = (materials) => {
      return {
        title: {
          text: '材料价格对比',
          left: 'center'
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow' }
        },
        xAxis: {
          type: 'category',
          data: materials.map(m => m.name),
          axisLabel: {
            rotate: 45,
            interval: 0
          }
        },
        yAxis: {
          type: 'value',
          name: '价格 (元)',
          axisLabel: {
            formatter: '¥{value}'
          }
        },
        series: [{
          name: '价格',
          type: 'bar',
          data: materials.map(m => ({
            value: m.price,
            itemStyle: {
              color: getPriceColor(m.price, materials)
            }
          })),
          itemStyle: {
            borderRadius: [4, 4, 0, 0]
          }
        }],
        grid: {
          left: '3%',
          right: '4%',
          bottom: '15%',
          containLabel: true
        }
      }
    }

    // 创建质量对比图
    const createQualityChart = (materials) => {
      return {
        title: {
          text: '材料质量对比',
          left: 'center'
        },
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c}星'
        },
        legend: {
          top: '10%',
          left: 'center'
        },
        series: [{
          name: '质量等级',
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          data: materials.map(m => ({
            value: m.quality || 3,
            name: m.name,
            itemStyle: {
              color: getQualityColor(m.quality || 3)
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

    // 创建供应商对比图
    const createSupplierChart = (materials) => {
      const supplierGroups = materials.reduce((acc, material) => {
        const supplier = material.supplier || '未知供应商'
        if (!acc[supplier]) {
          acc[supplier] = []
        }
        acc[supplier].push(material)
        return acc
      }, {})

      return {
        title: {
          text: '供应商材料分布',
          left: 'center'
        },
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c}个 ({d}%)'
        },
        series: [{
          name: '材料数量',
          type: 'pie',
          radius: '60%',
          data: Object.keys(supplierGroups).map(supplier => ({
            value: supplierGroups[supplier].length,
            name: supplier
          }))
        }]
      }
    }

    // 创建综合对比图
    const createComprehensiveChart = (materials) => {
      const indicators = [
        { name: '价格', max: 100 },
        { name: '质量', max: 100 },
        { name: '交付', max: 100 },
        { name: '风险', max: 100 },
        { name: '服务', max: 100 }
      ]

      const series = materials.map(material => ({
        name: material.name,
        type: 'radar',
        data: [{
          value: [
            normalizePrice(material.price, materials),
            (material.quality || 3) * 20,
            getDeliveryScore(material.deliveryTime),
            getRiskScore(material.riskLevel),
            getServiceScore(material.supplier)
          ],
          name: material.name
        }]
      }))

      return {
        title: {
          text: '材料综合对比',
          left: 'center'
        },
        tooltip: {
          trigger: 'item'
        },
        legend: {
          top: '10%',
          left: 'center'
        },
        radar: {
          indicator: indicators,
          name: {
            textStyle: {
              color: '#666'
            }
          }
        },
        series: series
      }
    }

    // 价格颜色映射
    const getPriceColor = (price, materials) => {
      const prices = materials.map(m => m.price).sort((a, b) => a - b)
      const minPrice = Math.min(...prices)
      const maxPrice = Math.max(...prices)
      const ratio = (price - minPrice) / (maxPrice - minPrice) || 0
      
      if (ratio < 0.33) return '#67C23A' // 绿色 - 低价
      if (ratio < 0.67) return '#E6A23C' // 黄色 - 中价
      return '#F56C6C' // 红色 - 高价
    }

    // 质量颜色映射
    const getQualityColor = (quality) => {
      const colors = ['#F56C6C', '#E6A23C', '#409EFF', '#67C23A', '#67C23A']
      return colors[Math.max(0, Math.min(4, quality - 1))] || '#409EFF'
    }

    // 标准化价格分数
    const normalizePrice = (price, materials) => {
      const prices = materials.map(m => m.price)
      const minPrice = Math.min(...prices)
      const maxPrice = Math.max(...prices)
      
      if (maxPrice === minPrice) return 50
      
      // 价格越低分数越高
      return 100 - ((price - minPrice) / (maxPrice - minPrice)) * 100
    }

    // 获取交付分数
    const getDeliveryScore = (deliveryTime) => {
      if (!deliveryTime) return 50
      
      const days = parseInt(deliveryTime)
      if (days <= 3) return 100
      if (days <= 7) return 80
      if (days <= 15) return 60
      if (days <= 30) return 40
      return 20
    }

    // 获取风险分数
    const getRiskScore = (riskLevel) => {
      const scores = {
        low: 100,
        medium: 70,
        high: 40,
        critical: 10
      }
      return scores[riskLevel] || 50
    }

    // 获取服务分数
    const getServiceScore = (supplier) => {
      // 这里可以根据供应商历史评价计算分数
      // 现在返回随机分数作为示例
      return Math.floor(Math.random() * 30) + 70
    }

    // 计算综合评分
    const calculateComprehensiveScore = (material) => {
      const priceScore = normalizePrice(material.price, selectedMaterials.value)
      const qualityScore = (material.quality || 3) * 20
      const deliveryScore = getDeliveryScore(material.deliveryTime)
      const riskScore = getRiskScore(material.riskLevel)
      const serviceScore = getServiceScore(material.supplier)

      // 加权平均
      return Math.round(
        priceScore * 0.3 +
        qualityScore * 0.25 +
        deliveryScore * 0.2 +
        riskScore * 0.15 +
        serviceScore * 0.1
      )
    }

    // 获取建议
    const getRecommendation = (material, score) => {
      if (score >= 85) return '强烈推荐'
      if (score >= 70) return '推荐'
      if (score >= 60) return '可考虑'
      return '不推荐'
    }

    // 获取建议颜色
    const getRecommendationColor = (recommendation) => {
      const colors = {
        '强烈推荐': '#67C23A',
        '推荐': '#409EFF',
        '可考虑': '#E6A23C',
        '不推荐': '#F56C6C'
      }
      return colors[recommendation] || '#909399'
    }

    // 获取建议图标
    const getRecommendationIcon = (recommendation) => {
      const icons = {
        '强烈推荐': 'Check',
        '推荐': 'Check',
        '可考虑': 'Warning',
        '不推荐': 'Close'
      }
      return icons[recommendation] || 'Warning'
    }

    // 获取风险标签
    const getRiskLabel = (level) => {
      return RISK_LEVELS[level]?.label || level
    }

    // 获取风险标签类型
    const getRiskTagType = (level) => {
      const types = {
        normal: 'success',
        low: 'warning',
        medium: 'warning',
        high: 'danger',
        critical: 'danger'
      }
      return types[level] || 'info'
    }

    // 获取分数颜色
    const getScoreColor = (score) => {
      if (score >= 85) return '#67C23A'
      if (score >= 70) return '#409EFF'
      if (score >= 60) return '#E6A23C'
      return '#F56C6C'
    }

    // 获取分类标签
    const getCategoryLabel = (category) => {
      return MATERIAL_CATEGORIES[category]?.label || category
    }

    // 格式化价格
    const formatPrice = (price) => {
      if (typeof price !== 'number') return '0.00'
      return price.toLocaleString('zh-CN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })
    }

    // 处理材料选择变化
    const handleSelectionChange = (selection) => {
      tempSelectedMaterials.value = selection
    }

    // 确认选择
    const confirmSelection = () => {
      selectedMaterials.value = [...selectedMaterials.value, ...tempSelectedMaterials.value]
      showMaterialSelector.value = false
      tempSelectedMaterials.value = []
      emit('materials-change', selectedMaterials.value)
    }

    // 移除材料
    const removeMaterial = (materialId) => {
      selectedMaterials.value = selectedMaterials.value.filter(m => m.id !== materialId)
      emit('materials-change', selectedMaterials.value)
    }

    // 清空选择
    const clearSelection = () => {
      selectedMaterials.value = []
      emit('materials-change', selectedMaterials.value)
    }

    // 处理选择器关闭
    const handleSelectorClose = () => {
      tempSelectedMaterials.value = []
      showMaterialSelector.value = false
    }

    // 处理图表点击
    const handleChartClick = (params) => {
      console.log('图表点击:', params)
    }

    // 处理图表就绪
    const handleChartReady = (chart) => {
      console.log('材料对比图初始化完成')
    }

    // 监听对比类型变化
    watch(compareType, (newType) => {
      emit('compare-type-change', newType)
    })

    return {
      chartRef,
      compareType,
      selectedMaterials,
      showMaterialSelector,
      tempSelectedMaterials,
      searchKeyword,
      categoryFilter,
      materialTable,
      materialCategories,
      filteredAvailableMaterials,
      comparisonData,
      chartOption,
      getRiskLabel,
      getRiskTagType,
      getScoreColor,
      getCategoryLabel,
      getRecommendationColor,
      getRecommendationIcon,
      formatPrice,
      handleSelectionChange,
      confirmSelection,
      removeMaterial,
      clearSelection,
      handleSelectorClose,
      handleChartClick,
      handleChartReady
    }
  }
}
</script>

<style scoped>
.material-compare-chart {
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

.selected-materials {
  padding: 12px 20px;
  background: #f9fafc;
  border-bottom: 1px solid #ebeef5;
}

.materials-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 13px;
  color: #606266;
}

.materials-list {
  display: flex;
  flex-wrap: wrap;
}

.compare-table {
  padding: 20px;
}

.score-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.score-value {
  font-size: 12px;
  font-weight: 500;
  min-width: 35px;
}

.material-selector {
  padding: 0;
}

.selector-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
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

  .materials-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .selector-header {
    flex-direction: column;
    gap: 12px;
  }
}

/* 深色主题样式 */
.dark .material-compare-chart {
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

.dark .materials-selector {
  background: #2d2d2d !important;
  border-top-color: #4c4d4f !important;
}

.dark .materials-header h4 {
  color: #e4e7ed !important;
}

.dark .selector-header h5 {
  color: #e4e7ed !important;
}
</style>
