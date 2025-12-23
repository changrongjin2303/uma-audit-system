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
          fixed="left"
        />
        
        <el-table-column
          prop="materialName"
          label="材料名称"
          min-width="180"
          show-overflow-tooltip
          align="center"
          fixed="left"
        />
        
        <el-table-column
          prop="specification"
          label="规格型号"
          min-width="150"
          show-overflow-tooltip
          align="center"
          fixed="left"
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
            label="基期信息价"
            width="140"
            align="center"
          >
            <template #default="{ row }">
              {{ formatCurrency(null, null, row.originalBasePrice) }}
              <span class="unit-text">/{{ row.unit }}</span>
            </template>
          </el-table-column>

          <el-table-column
            label="价格差异"
            width="120"
            align="center"
          >
            <template #default="{ row }">
              <span :class="getDifferenceClass(calculatePriceDiff(row))">
                {{ formatCurrency(null, null, calculatePriceDiff(row)) }}
              </span>
            </template>
          </el-table-column>

          <el-table-column
            label="合同期平均价"
            width="140"
            align="center"
          >
            <template #default="{ row }">
              {{ formatCurrency(null, null, getGuidancePrice(row)) }}
              <span class="unit-text">/{{ row.unit }}</span>
            </template>
          </el-table-column>

          <el-table-column
            label="风险幅度"
            width="100"
            align="center"
          >
            <template #default="{ row }">
              <span :class="getDifferenceClass(calculatePriceDiff(row))">
                {{ formatPercent(null, null, calculateRiskRate(row)) }}
              </span>
            </template>
          </el-table-column>
        </el-table-column>
        
        <el-table-column
          prop="adjustment"
          label="调差"
          width="120"
          align="center"
          :formatter="formatAdjustment"
          :class-name="getAdjustmentClass"
        >
          <template #default="{ row }">
             <span :class="getDifferenceClass(calculatePriceDiff(row))">
               {{ formatCurrency(null, null, calculateAdjustmentDiff(row)) }}
             </span>
          </template>
        </el-table-column>
        
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
      <p>备注：（1）本表可扩展；（2）调差为正值即核减，负值即核增；（3）本表可纳入审价过程资料一并归档。</p>
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
            <div class="summary-label">调差总额</div>
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
  
  // 重新计算总调差
  const totalAdjustment = tableData.value.reduce((sum, item) => {
    return sum + (calculateAdjustmentDiff(item) || 0)
  }, 0)

  // AI审核总额 = 送审总额 + 调差总额
  // 注意：调差为正值即核增，所以 Audited = Original + Adjustment
  const aiTotal = originalTotal + totalAdjustment
  
  return {
    totalMaterials,
    originalTotal,
    aiTotal,
    totalAdjustment
  }
})

// 格式化数字，去除末尾的0，不使用千分位逗号
const formatDecimal = (num, decimals = 4) => {
  if (num === null || num === undefined || (typeof num === 'number' && isNaN(num))) return '-'
  const val = Number(num)
  const res = val.toFixed(decimals)
  if (res.includes('.')) {
    return res.replace(/\.?0+$/, '')
  }
  return res
}

// 格式化数字
const formatNumber = (row, column, cellValue) => {
  if (!cellValue && cellValue !== 0) return '-'
  return formatDecimal(cellValue)
}

// 格式化货币
const formatCurrency = (row, column, cellValue) => {
  const value = column === undefined && cellValue === undefined ? row : cellValue
  return formatDecimal(value)
}

// 直接格式化货币值
const formatCurrencyValue = (value) => {
  return formatDecimal(value)
}

// 格式化调整金额
const formatAdjustment = (row, column, cellValue) => {
  if (!cellValue && cellValue !== 0) return '-'
  const value = Number(cellValue)
  const formatted = formatDecimal(Math.abs(value))
  return value > 0 ? `+${formatted}` : `-${formatted}`
}

// 格式化百分比
const formatPercent = (row, column, cellValue) => {
  if (!cellValue && cellValue !== 0) return '-'
  return `${formatDecimal(cellValue, 2)}%`
}

// 获取基准单价（合同期平均价）
const getGuidancePrice = (row) => {
  return row.aiUnitPrice
}

// 获取原始单价
const getOriginalPrice = (row) => {
  return row.originalUnitPrice
}

// 计算价格差异：直接使用后端返回的差价
const calculatePriceDiff = (row) => {
  if (row.priceDiff !== undefined && row.priceDiff !== null) {
    return row.priceDiff
  }
  const guidance = getGuidancePrice(row) || 0
  const original = getOriginalPrice(row) || 0
  return original - guidance
}

// 计算风险幅度：直接使用后端返回的风险幅度
const calculateRiskRate = (row) => {
  if (row.riskRate !== undefined && row.riskRate !== null) {
    return row.riskRate
  }
  const diff = calculatePriceDiff(row)
  const original = getOriginalPrice(row)
  if (!original) return 0
  return (diff / original) * 100
}

// 计算调差：根据风险幅度计算，±5%以内不调差
const calculateAdjustmentDiff = (row) => {
  // 获取合同期平均价
  const contractAvgPrice = row.aiUnitPrice || 0
  
  // 获取风险幅度（百分比）
  let riskRate = 0
  if (row.riskRate !== undefined && row.riskRate !== null) {
    riskRate = row.riskRate
  } else {
    // 如果没有风险幅度，尝试计算
    const diff = calculatePriceDiff(row)
    const original = getOriginalPrice(row)
    if (!original) return 0
    // 假设 original 是基期价格，diff 是 original - contractAvg
    // riskRate = (contractAvg - original) / original * 100
    // contractAvg = original - diff
    // riskRate = (original - diff - original) / original * 100 = -diff / original * 100
    riskRate = -(diff / original) * 100
  }

  // 5% 阈值逻辑
  const thresholdPercent = 5
  const thresholdDecimal = 0.05
  
  // 如果风险幅度在 ±5% 以内，调差为 0
  if (Math.abs(riskRate) <= thresholdPercent) {
    return 0
  }
  
  // 反推基期信息价
  // riskRate (decimal) = (contractAvg - base) / base
  // base = contractAvg / (1 + riskRate)
  const riskRateDecimal = riskRate / 100
  if (1 + riskRateDecimal === 0) return 0 // 避免除以0
  
  const basePrice = contractAvgPrice / (1 + riskRateDecimal)
  
  let excessPerUnit = 0
  if (riskRate > thresholdPercent) {
    // 涨幅超过5%：合同期平均价 - 基期信息价 * (1 + 5%)
    excessPerUnit = contractAvgPrice - basePrice * (1 + thresholdDecimal)
  } else {
    // 跌幅超过5%：合同期平均价 - 基期信息价 * (1 - 5%)
    excessPerUnit = contractAvgPrice - basePrice * (1 - thresholdDecimal)
  }
  
  const quantity = row.quantity || 0
  return excessPerUnit * quantity
}

// 获取差异样式类
const getDifferenceClass = (value) => {
  if (!value) return ''
  return value > 0 ? 'diff-positive' : 'diff-negative'
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
        const totalAdjustment = data.reduce((sum, item) => {
           // 这里需要重新计算调差总和，因为adjustment字段可能不是基于5%阈值计算的
           // 但为了性能，我们应该在processGuidancePriceData中计算好
           // 由于calculateAdjustmentDiff依赖组件方法，这里简单处理：
           // 实际上最好的方式是在processGuidancePriceData中把calculateAdjustmentDiff的逻辑放进去
           // 这里先临时调用方法计算
           const adj = calculateAdjustmentDiff(item)
           return sum + (adj || 0)
        }, 0)
        sums[index] = formatCurrencyValue(totalAdjustment)
        break
      case 'weightPercentage':
        const totalWeight = values.reduce((sum, val) => sum + (val || 0), 0)
        sums[index] = `${formatDecimal(totalWeight, 2)}%`
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
    originalBasePrice: Number(item.original_base_price) || 0,
    baseUnit: item.base_unit || '',
    adjustment: Number(item.adjustment) || ((Number(item.guidance_price || item.base_price) || 0) - (Number(item.original_price) || 0)) * (Number(item.quantity) || 0),
    weightPercentage: Number(item.weight_percentage) || 0,
    priceDiff: item.price_diff !== undefined ? Number(item.price_diff) : undefined,
    riskRate: item.risk_rate !== undefined ? Number(item.risk_rate) : undefined
  }))

  // 移除过滤逻辑，显示所有数据，确保与项目详情页一致
  // const diffFiltered = mapped.filter(item => Math.abs(item.adjustment || 0) > 1e-6)
  const diffFiltered = mapped
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

.diff-positive {
  color: #F56C6C; /* Red */
  font-weight: bold;
}

.diff-negative {
  color: #67C23A; /* Green */
  font-weight: bold;
}

.unit-text {
  color: #909399;
  font-size: 12px;
  margin-left: 2px;
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
