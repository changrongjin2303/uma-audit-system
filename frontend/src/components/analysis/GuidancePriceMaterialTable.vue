<template>
  <div class="guidance-price-material-table">
    <!-- 表格标题 -->
    <div class="table-header">
      <h3>表2 材料价格分析表（市场信息价材料）</h3>
      <div class="project-info">
        <span>项目名称：{{ projectName }}</span>
        <span class="unit-info">单位：元</span>
      </div>
    </div>

    <!-- 分析表格 -->
    <div class="table-container">
      <el-table
        :data="tableData"
        border
        stripe
        class="analysis-table"
        :summary-method="getSummaries"
        show-summary
      >
        <el-table-column
          prop="sequence"
          label="序号"
          width="80"
          align="center"
        />
        
        <el-table-column
          prop="materialName"
          label="材料名称"
          min-width="180"
          show-overflow-tooltip
          align="center"
        />
        
        <el-table-column
          prop="specification"
          label="规格型号"
          min-width="150"
          show-overflow-tooltip
          align="center"
        />
        
        <el-table-column
          prop="unit"
          label="单位"
          width="80"
          align="center"
        />
        
        <el-table-column
          prop="quantity"
          label="数量"
          width="100"
          align="center"
          :formatter="formatNumber"
        />
        
        <el-table-column
          label="送审结算"
          align="center"
        >
          <el-table-column
            prop="originalUnitPrice"
            label="单价"
            width="120"
            align="center"
            :formatter="formatCurrency"
          />
          <el-table-column
            prop="originalTotalPrice"
            label="合价"
            width="120"
            align="center"
            :formatter="formatCurrency"
          />
        </el-table-column>
        
        <el-table-column
          label="市场信息价结算"
          align="center"
        >
          <el-table-column
            prop="aiUnitPrice"
            label="单价"
            width="120"
            align="center"
            :formatter="formatCurrency"
          />
          <el-table-column
            prop="aiTotalPrice"
            label="合价"
            width="120"
            align="center"
            :formatter="formatCurrency"
          />
        </el-table-column>
        
        <el-table-column
          prop="adjustment"
          label="核增（减）额"
          width="120"
          align="center"
          :formatter="formatAdjustment"
          :class-name="getAdjustmentClass"
        />
        
        <el-table-column
          prop="weightPercentage"
          label="权重（%）"
          width="100"
          align="center"
          :formatter="formatPercent"
        />
      </el-table>
    </div>

    <!-- 表格备注 -->
    <div class="table-notes">
      <p>备注：（1）本表可扩展；（2）差额为正值即核减，负值即核增；（3）本表可纳入审价过程资料一并归档。</p>
    </div>

    <!-- 统计汇总 -->
    <div class="summary-info">
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="summary-item">
            <div class="summary-label">市场信息价材料总数</div>
            <div class="summary-value">{{ statistics.totalMaterials }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="summary-item">
            <div class="summary-label">送审总额</div>
            <div class="summary-value">{{ formatCurrency(statistics.originalTotal) }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="summary-item">
            <div class="summary-label">AI审核总额</div>
            <div class="summary-value">{{ formatCurrency(statistics.aiTotal) }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="summary-item">
            <div class="summary-label">核减总额</div>
            <div class="summary-value" :class="getAdjustmentSummaryClass()">
              {{ formatCurrency(statistics.totalAdjustment) }}
            </div>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const props = defineProps({
  projectName: {
    type: String,
    default: '示例项目'
  },
  guidancePriceData: {
    type: Array,
    default: () => []
  }
})

// 表格数据
const tableData = ref([])

// 统计信息
const statistics = computed(() => {
  const totalMaterials = tableData.value.length
  const originalTotal = tableData.value.reduce((sum, item) => sum + (item.originalTotalPrice || 0), 0)
  const aiTotal = tableData.value.reduce((sum, item) => sum + (item.aiTotalPrice || 0), 0)
  const totalAdjustment = originalTotal - aiTotal
  
  return {
    totalMaterials,
    originalTotal,
    aiTotal,
    totalAdjustment
  }
})

// 格式化数字
const formatNumber = (row, column, cellValue) => {
  if (!cellValue && cellValue !== 0) return '-'
  return Number(cellValue).toLocaleString()
}

// 格式化货币
const formatCurrency = (row, column, cellValue) => {
  const value = column === undefined && cellValue === undefined ? row : cellValue
  if (value === null || value === undefined || (typeof value === 'number' && isNaN(value))) return '-'
  return Number(value).toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

// 直接格式化货币值
const formatCurrencyValue = (value) => {
  if (!value && value !== 0) return '-'
  return Number(value).toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

// 格式化调整金额
const formatAdjustment = (row, column, cellValue) => {
  if (!cellValue && cellValue !== 0) return '-'
  const value = Number(cellValue)
  const formatted = Math.abs(value).toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
  return value > 0 ? `+${formatted}` : `-${formatted}`
}

// 格式化百分比
const formatPercent = (row, column, cellValue) => {
  if (!cellValue && cellValue !== 0) return '-'
  return `${Number(cellValue).toFixed(2)}%`
}

// 获取调整金额样式类
const getAdjustmentClass = ({ row }) => {
  const adjustment = row.adjustment || 0
  if (adjustment > 0) return 'positive-adjustment'
  if (adjustment < 0) return 'negative-adjustment'
  return ''
}

// 获取汇总调整金额样式类
const getAdjustmentSummaryClass = () => {
  const adjustment = statistics.value.totalAdjustment
  if (adjustment > 0) return 'positive-summary'
  if (adjustment < 0) return 'negative-summary'
  return ''
}

// 计算合计行
const getSummaries = (param) => {
  const { columns, data } = param
  const sums = []
  columns.forEach((column, index) => {
    if (index === 0) {
      sums[index] = '合计'
      return
    }
    
    const values = data.map(item => Number(item[column.property]))
    
    switch (column.property) {
      case 'quantity':
        sums[index] = '' // 数量列不显示合计
        break
      case 'originalTotalPrice':
      case 'aiTotalPrice':
      case 'adjustment':
        const sum = values.reduce((sum, val) => sum + (val || 0), 0)
        sums[index] = formatCurrencyValue(sum)
        break
      case 'weightPercentage':
        const totalWeight = values.reduce((sum, val) => sum + (val || 0), 0)
        sums[index] = `${totalWeight.toFixed(2)}%`
        break
      default:
        sums[index] = ''
    }
  })
  return sums
}

// 处理市场信息价材料数据
const processGuidancePriceData = (data) => {
  if (!data || data.length === 0) {
    // 生成示例市场信息价材料数据
    return [
      {
        sequence: 1,
        materialName: 'C30商品混凝土',
        specification: '坍落度180±20mm',
        unit: 'm³',
        quantity: 500,
        originalUnitPrice: 280.00,
        originalTotalPrice: 140000.00,
        aiUnitPrice: 275.50,
        aiTotalPrice: 137750.00,
        adjustment: 2250.00,
        weightPercentage: 35.2
      },
      {
        sequence: 2,
        materialName: 'HRB400E螺纹钢筋',
        specification: 'Φ16-25mm',
        unit: 't',
        quantity: 65,
        originalUnitPrice: 4200.00,
        originalTotalPrice: 273000.00,
        aiUnitPrice: 4150.00,
        aiTotalPrice: 269750.00,
        adjustment: 3250.00,
        weightPercentage: 28.6
      },
      {
        sequence: 3,
        materialName: '普通粘土砖',
        specification: 'MU10 240×115×53mm',
        unit: '千块',
        quantity: 180,
        originalUnitPrice: 420.00,
        originalTotalPrice: 75600.00,
        aiUnitPrice: 410.00,
        aiTotalPrice: 73800.00,
        adjustment: 1800.00,
        weightPercentage: 18.5
      },
      {
        sequence: 4,
        materialName: '水泥砂浆',
        specification: 'M7.5',
        unit: 'm³',
        quantity: 120,
        originalUnitPrice: 180.00,
        originalTotalPrice: 21600.00,
        aiUnitPrice: 175.00,
        aiTotalPrice: 21000.00,
        adjustment: 600.00,
        weightPercentage: 8.9
      },
      {
        sequence: 5,
        materialName: '铝合金门窗',
        specification: '6061-T5 厚度1.4mm',
        unit: 'm²',
        quantity: 85,
        originalUnitPrice: 350.00,
        originalTotalPrice: 29750.00,
        aiUnitPrice: 360.00,
        aiTotalPrice: 30600.00,
        adjustment: -850.00,
        weightPercentage: 8.8
      }
    ]
  }
  
  // 优化大量数据处理，支持几十行到上百行数据
  const mapped = data.map((item, index) => ({
    sequence: index + 1,
    materialName: item.material_name || item.name || `未知材料${index + 1}`,
    specification: item.specification || item.model || item.spec || '-',
    unit: item.unit || '个',
    quantity: Number(item.quantity) || 0,
    originalUnitPrice: Number(item.original_price) || 0,
    originalTotalPrice: Number(item.original_total_price) || (Number(item.original_price) || 0) * (Number(item.quantity) || 0),
    aiUnitPrice: Number(item.guidance_price || item.base_price) || 0,
    aiTotalPrice: Number(item.guidance_total_price) || (Number(item.guidance_price || item.base_price) || 0) * (Number(item.quantity) || 0),
    adjustment: Number(item.adjustment) || ((Number(item.original_price) || 0) - (Number(item.guidance_price || item.base_price) || 0)) * (Number(item.quantity) || 0),
    weightPercentage: Number(item.weight_percentage) || 0
  }))

  const diffFiltered = mapped.filter(item => Math.abs(item.adjustment || 0) > 1e-6)
  const totalOriginal = diffFiltered.reduce((sum, item) => sum + Math.abs(item.originalTotalPrice || 0), 0)

  return diffFiltered.map((item, idx) => ({
    ...item,
    sequence: idx + 1,
    weightPercentage: totalOriginal > 0 ? (Math.abs(item.originalTotalPrice || 0) / totalOriginal) * 100 : 0
  }))
}

onMounted(() => {
  tableData.value = processGuidancePriceData(props.guidancePriceData)
})

// 监听数据变化
import { watch } from 'vue'
watch(() => props.guidancePriceData, (newData) => {
  tableData.value = processGuidancePriceData(newData)
}, { deep: true })
</script>

<style lang="scss" scoped>
.guidance-price-material-table {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-top: 24px;
}

.table-header {
  margin-bottom: 16px;
  
  h3 {
    font-size: 16px;
    font-weight: 600;
    color: #2c3e50;
    margin: 0 0 8px 0;
    text-align: center;
  }
  
  .project-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 14px;
    color: #666;
    margin-bottom: 16px;
    
    .unit-info {
      font-weight: 500;
    }
  }
}

.table-container {
  margin-bottom: 16px;
  
  .analysis-table {
    width: 100%;
    font-size: 12px;
    
    // 重置所有边框样式
    :deep(*) {
      box-sizing: border-box;
    }
    
    // 表格主体 - 统一边框样式
    :deep(.el-table) {
      border: none !important;
      border-collapse: separate !important;
      border-spacing: 0 !important;
      outline: 1px solid #2c3e50 !important;
    }
    
    // 表格容器外框
    :deep(.el-table__inner-wrapper) {
      border: 1px solid #2c3e50 !important;
      border-radius: 0 !important;
    }
    
    // 统一所有单元格边框
    :deep(th),
    :deep(td),
    :deep(.el-table__cell) {
      border: none !important;
      border-right: 1px solid #2c3e50 !important;
      border-bottom: 1px solid #2c3e50 !important;
      text-align: center !important;
      vertical-align: middle !important;
      padding: 8px 4px !important;
    }
    
    // 最右边列不需要右边框（但多级表头除外）
    :deep(td:last-child),
    :deep(.el-table__body .el-table__cell:last-child) {
      border-right: none !important;
    }
    
    // 多级表头特殊处理 - 确保所有表头单元格都有右边框
    :deep(.el-table__header th),
    :deep(.el-table__header .el-table__cell) {
      border-right: 1px solid #2c3e50 !important;
    }
    
    // 最后一列表头也需要右边框来封口
    :deep(.el-table__header th:last-child),
    :deep(.el-table__header .el-table__cell:last-child) {
      border-right: 1px solid #2c3e50 !important;
    }
    
    // 表头特殊样式
    :deep(.el-table__header) {
      th, .el-table__cell {
        background-color: #f8f9fa !important;
        color: #2c3e50 !important;
        font-weight: 600 !important;
        text-align: center !important;
      }
    }
    
    // 表体样式
    :deep(.el-table__body) {
      td, .el-table__cell {
        text-align: center !important;
      }
      
      .positive-adjustment {
        color: #e74c3c;
        font-weight: 500;
      }
      
      .negative-adjustment {
        color: #27ae60;
        font-weight: 500;
      }
    }
    
    // 表尾样式
    :deep(.el-table__footer) {
      td, .el-table__cell {
        background-color: #f1f3f4 !important;
        font-weight: 600 !important;
        color: #2c3e50 !important;
        text-align: center !important;
      }
      
      // 最后一行不需要下边框
      tr:last-child {
        td, .el-table__cell {
          border-bottom: none !important;
        }
      }
    }
    
    // 移除Element Plus的默认边框效果
    :deep(.el-table--border::after) {
      display: none !important;
    }
    
    :deep(.el-table__inner-wrapper::before) {
      display: none !important;
    }
    
    :deep(.el-table--border) {
      border: none !important;
    }
    
    // 支持大量数据的虚拟滚动
    :deep(.el-table__body-wrapper) {
      max-height: 600px;
      overflow-y: auto;
    }
    
    // 优化大数据量时的性能
    :deep(.el-table__row) {
      transition: none;
    }
  }
}

.table-notes {
  margin-bottom: 20px;
  
  p {
    font-size: 12px;
    color: #666;
    margin: 0;
    line-height: 1.5;
  }
}

.summary-info {
  background: linear-gradient(135deg, #e8f5e8 0%, #d4edda 100%);
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #c3e6cb;
  
  .summary-item {
    text-align: center;
    padding: 12px;
    
    .summary-label {
      font-size: 14px;
      color: #666;
      margin-bottom: 8px;
    }
    
    .summary-value {
      font-size: 18px;
      font-weight: 600;
      color: #2c3e50;
      
      &.positive-summary {
        color: #e74c3c;
      }
      
      &.negative-summary {
        color: #27ae60;
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .guidance-price-material-table {
    padding: 16px;
  }
  
  .table-header {
    h3 {
      font-size: 14px;
    }
    
    .project-info {
      flex-direction: column;
      gap: 4px;
      align-items: flex-start;
    }
  }
  
  .analysis-table {
    font-size: 11px;
  }
  
  .summary-info {
    .summary-item {
      .summary-value {
        font-size: 16px;
      }
    }
  }
}
</style>
