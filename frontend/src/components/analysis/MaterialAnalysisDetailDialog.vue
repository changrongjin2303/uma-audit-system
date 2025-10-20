<template>
  <el-dialog
    v-model="dialogVisible"
    title="材料分析详情"
    width="90%"
    center
    destroy-on-close
    class="analysis-detail-dialog"
    @close="handleClose"
  >
    <!-- 加载状态 -->
    <div v-if="loading" v-loading="loading" style="height: 300px;" />
    
    <!-- 详情内容 -->
    <template v-else-if="detailData">
      <div class="analysis-detail-content">
        <!-- 材料基本信息卡片 -->
        <el-card class="material-info-card">
          <template #header>
            <div class="card-header">
              <el-icon><Document /></el-icon>
              <span>项目材料信息</span>
            </div>
          </template>
          
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12" :md="8">
              <div class="info-item">
                <span class="label">材料名称：</span>
                <span class="value">{{ detailData.project_material.material_name }}</span>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12" :md="8">
              <div class="info-item">
                <span class="label">规格型号：</span>
                <span class="value">{{ detailData.project_material.specification || '无' }}</span>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12" :md="8">
              <div class="info-item">
                <span class="label">计量单位：</span>
                <span class="value">{{ detailData.project_material.unit || '无' }}</span>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12" :md="8">
              <div class="info-item">
                <span class="label">数量：</span>
                <span class="value">{{ formatNumber(detailData.project_material.quantity) }}</span>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12" :md="8">
              <div class="info-item">
                <span class="label">单价：</span>
                <span class="value price">¥{{ formatNumber(detailData.project_material.unit_price) }}</span>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12" :md="8">
              <div class="info-item">
                <span class="label">总价：</span>
                <span class="value price">¥{{ formatNumber(detailData.project_material.total_price) }}</span>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12" :md="8">
              <div class="info-item">
                <span class="label">材料编码：</span>
                <span class="value">{{ detailData.project_material.material_code || '无' }}</span>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12" :md="8">
              <div class="info-item">
                <span class="label">品牌：</span>
                <span class="value">{{ detailData.project_material.brand || '无' }}</span>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12" :md="8">
              <div class="info-item">
                <span class="label">分类：</span>
                <span class="value">{{ detailData.project_material.category || '无' }}</span>
              </div>
            </el-col>
          </el-row>
          
          <!-- 项目信息 -->
          <div v-if="detailData.project_info" class="project-info">
            <el-divider>项目信息</el-divider>
            <el-row :gutter="20">
              <el-col :xs="24" :sm="12" :md="8">
                <div class="info-item">
                  <span class="label">项目名称：</span>
                  <span class="value">{{ detailData.project_info.name }}</span>
                </div>
              </el-col>
              <el-col :xs="24" :sm="12" :md="8">
                <div class="info-item">
                  <span class="label">项目地区：</span>
                  <span class="value">{{ detailData.project_info.location || '无' }}</span>
                </div>
              </el-col>
              <el-col :xs="24" :sm="12" :md="8">
                <div class="info-item">
                  <span class="label">项目类型：</span>
                  <span class="value">{{ detailData.project_info.project_type || '无' }}</span>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-card>

        <!-- 匹配的市场信息价材料卡片 -->
        <el-card v-if="detailData.matched_base_material" class="matched-material-card">
          <template #header>
            <div class="card-header">
              <el-icon><Connection /></el-icon>
              <span>匹配的市场信息价材料</span>
              <el-tag type="success" size="small">已匹配</el-tag>
            </div>
          </template>
          
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12" :md="8">
              <div class="info-item">
                <span class="label">材料名称：</span>
                <span class="value">{{ detailData.matched_base_material.name }}</span>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12" :md="8">
              <div class="info-item">
                <span class="label">规格型号：</span>
                <span class="value">{{ detailData.matched_base_material.specification || '无' }}</span>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12" :md="8">
              <div class="info-item">
                <span class="label">计量单位：</span>
                <span class="value">{{ detailData.matched_base_material.unit || '无' }}</span>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12" :md="8">
              <div class="info-item">
                <span class="label">市场信息价：</span>
                <span class="value price market-price">¥{{ formatNumber(detailData.matched_base_material.price) }}</span>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12" :md="8">
              <div class="info-item">
                <span class="label">价格类型：</span>
                <span class="value">{{ detailData.matched_base_material.price_type || '无' }}</span>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12" :md="8">
              <div class="info-item">
                <span class="label">适用地区：</span>
                <span class="value">{{ detailData.matched_base_material.region || '无' }}</span>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12" :md="8">
              <div class="info-item">
                <span class="label">数据来源：</span>
                <span class="value">{{ detailData.matched_base_material.source || '无' }}</span>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12" :md="8">
              <div class="info-item">
                <span class="label">生效日期：</span>
                <span class="value">{{ formatDate(detailData.matched_base_material.effective_date) }}</span>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12" :md="8">
              <div class="info-item">
                <span class="label">材料分类：</span>
                <span class="value">{{ detailData.matched_base_material.category || '无' }}</span>
              </div>
            </el-col>
          </el-row>
        </el-card>

        <!-- 未匹配提示 -->
        <el-card v-else class="no-match-card">
          <template #header>
            <div class="card-header">
              <el-icon><Warning /></el-icon>
              <span>市场信息价材料匹配情况</span>
              <el-tag type="warning" size="small">未匹配</el-tag>
            </div>
          </template>
          <el-empty description="该材料尚未匹配到市场信息价材料，无法进行价格对比分析" />
        </el-card>

        <!-- AI分析结果卡片 -->
        <el-card v-if="detailData.analysis_result" class="analysis-result-card">
          <template #header>
            <div class="card-header">
              <el-icon><TrendCharts /></el-icon>
              <span>AI价格分析结果</span>
              <el-tag 
                :type="getAnalysisStatusType(detailData.analysis_result.status)" 
                size="small"
              >
                {{ getAnalysisStatusText(detailData.analysis_result.status) }}
              </el-tag>
            </div>
          </template>
          
          <!-- 价格对比结果 -->
          <div v-if="detailData.analysis_result.status === 'completed'" class="analysis-content">
            <!-- 合理性评估 -->
            <div class="reasonability-assessment">
              <h4>价格合理性评估</h4>
              <el-row :gutter="20">
                <el-col :xs="24" :sm="8">
                  <div class="assessment-item">
                    <span class="assessment-label">合理性判断：</span>
                    <el-tag 
                      :type="detailData.analysis_result.is_reasonable ? 'success' : 'danger'"
                      size="small"
                    >
                      {{ detailData.analysis_result.is_reasonable ? '合理' : '异常' }}
                    </el-tag>
                  </div>
                </el-col>
                <el-col :xs="24" :sm="8">
                  <div class="assessment-item">
                    <span class="assessment-label">合价差：</span>
                    <span 
                      class="assessment-value"
                      :class="{
                        'positive': detailData.analysis_result.total_price_difference > 0,
                        'negative': detailData.analysis_result.total_price_difference < 0
                      }"
                    >
                      {{ formatCurrency(detailData.analysis_result.total_price_difference, true) }}
                      <span v-if="detailData.analysis_result.quantity" class="quantity-hint">
                        （数量：{{ formatNumber(detailData.analysis_result.quantity) }} {{ detailData.analysis_result.unit || '' }}）
                      </span>
                    </span>
                  </div>
                </el-col>
                <el-col :xs="24" :sm="8">
                  <div class="assessment-item">
                    <span class="assessment-label">风险等级：</span>
                    <el-tag 
                      :type="getRiskLevelType(detailData.analysis_result.risk_level)"
                      size="small"
                    >
                      {{ getRiskLevelText(detailData.analysis_result.risk_level) }}
                    </el-tag>
                  </div>
                </el-col>
              </el-row>
            </div>

            <!-- 数据来源 -->
            <div v-if="dataSourceRows.length > 0" class="data-sources-section">
              <h4>数据来源与可靠性评估</h4>
              <el-table
                :data="dataSourceRows"
                border
                size="small"
                class="data-source-table"
              >
                <el-table-column prop="source_type" label="来源类型" min-width="140" />
                <el-table-column prop="platform_examples" label="平台/项目示例" min-width="200" />
                <el-table-column prop="data_count" label="数据量" min-width="120" align="center">
                  <template #default="{ row }">
                    <div class="data-count-cell">
                      <span>{{ row.data_count || '—' }}</span>
                      <span v-if="row.price_reference" class="price-reference">{{ row.price_reference }}</span>
                    </div>
                  </template>
                </el-table-column>
                <el-table-column prop="timeliness" label="时效性" min-width="120" align="center" />
                <el-table-column label="可靠性评级" min-width="180" align="center">
                  <template #default="{ row }">
                    <div class="reliability-cell">
                      <el-rate
                        v-if="row.reliability_value !== null"
                        :model-value="row.reliability_value"
                        :max="5"
                        disabled
                        allow-half
                        class="reliability-rate"
                      />
                      <span v-else class="reliability-placeholder">—</span>
                    </div>
                  </template>
                </el-table-column>
              </el-table>
              <p class="data-source-note">{{ dataSourceNote }}</p>
            </div>

            <!-- 分析说明 -->
            <div v-if="detailData.analysis_result.analysis_reasoning" class="analysis-reasoning">
              <h4>分析说明</h4>
              <div class="reasoning-content">
                {{ detailData.analysis_result.analysis_reasoning }}
              </div>
            </div>

            <!-- 风险因素 -->
            <div v-if="detailData.analysis_result.risk_factors" class="risk-factors">
              <h4>风险因素</h4>
              <div class="risk-content">
                {{ detailData.analysis_result.risk_factors }}
              </div>
            </div>

            <!-- 分析模型信息 -->
            <div class="analysis-meta">
              <el-divider>分析信息</el-divider>
              <el-row :gutter="20">
                <el-col :xs="24" :sm="12">
                  <div class="meta-item">
                    <span class="meta-label">分析模型：</span>
                    <span class="meta-value">{{ detailData.analysis_result.analysis_model || '无' }}</span>
                  </div>
                </el-col>
                <el-col :xs="24" :sm="12">
                  <div class="meta-item">
                    <span class="meta-label">分析时间：</span>
                    <span class="meta-value">{{ formatDate(detailData.analysis_result.analysis_date) }}</span>
                  </div>
                </el-col>
              </el-row>
            </div>
          </div>

          <!-- 分析失败提示 -->
          <div v-else-if="detailData.analysis_result.status === 'failed'" class="analysis-failed">
            <el-alert
              title="分析失败"
              description="AI价格分析过程中出现错误，请重新进行分析"
              type="error"
              :closable="false"
            />
          </div>

          <!-- 分析进行中提示 -->
          <div v-else class="analysis-processing">
            <el-alert
              title="分析进行中"
              description="AI正在分析材料价格，请稍候..."
              type="info"
              :closable="false"
            />
          </div>
        </el-card>

        <!-- 无分析结果提示 -->
        <el-card v-else class="no-analysis-card">
          <template #header>
            <div class="card-header">
              <el-icon><Warning /></el-icon>
              <span>AI分析结果</span>
              <el-tag type="info" size="small">未分析</el-tag>
            </div>
          </template>
          <el-empty description="该材料尚未进行AI价格分析，请先执行价格分析" />
        </el-card>
      </div>
    </template>

    <!-- 错误提示 -->
    <div v-else-if="error" class="error-content">
      <el-alert
        :title="error"
        type="error"
        :closable="false"
        show-icon
      />
    </div>

    <!-- 对话框底部 -->
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
        <el-button v-if="detailData?.project_material" type="primary" @click="goToMaterialDetail">
          查看完整详情
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Document, Connection, Warning, TrendCharts } from '@element-plus/icons-vue'
import { getMaterialAnalysisDetail } from '@/api/analysis'
import { formatAnalysisDataSources, getDataSourceNote } from '@/utils/dataSourceUtils'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  materialId: {
    type: [Number, String],
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'close'])

const router = useRouter()
const dialogVisible = ref(false)
const loading = ref(false)
const detailData = ref(null)
const error = ref('')

const dataSourceRows = computed(() =>
  formatAnalysisDataSources(detailData.value?.analysis_result || null)
)

const dataSourceNote = computed(() =>
  getDataSourceNote(detailData.value?.analysis_result || null)
)

// 监听modelValue属性变化
watch(() => props.modelValue, (newVal) => {
  dialogVisible.value = newVal
  if (newVal && props.materialId) {
    loadMaterialDetail()
  }
})

// 监听dialogVisible变化，同步到父组件
watch(dialogVisible, (newVal) => {
  emit('update:modelValue', newVal)
})

// 加载材料详情
const loadMaterialDetail = async () => {
  if (!props.materialId) return
  
  loading.value = true
  error.value = ''
  
  try {
    const response = await getMaterialAnalysisDetail(props.materialId)
    if (response.code === 200) {
      detailData.value = response.data
    } else {
      error.value = response.message || '获取材料详情失败'
    }
  } catch (err) {
    console.error('获取材料详情失败:', err)
    error.value = err.message || '获取材料详情失败'
  } finally {
    loading.value = false
  }
}

// 关闭对话框
const handleClose = () => {
  dialogVisible.value = false
  detailData.value = null
  error.value = ''
  emit('close')
}

// 跳转到材料详情页面
const goToMaterialDetail = () => {
  if (detailData.value?.project_material) {
    const projectId = detailData.value.project_info?.id
    const materialId = detailData.value.project_material.id
    if (projectId && materialId) {
      router.push(`/projects/${projectId}/materials/${materialId}`)
      handleClose()
    }
  }
}

// 格式化数字
const formatNumber = (value) => {
  if (value === null || value === undefined) return '无'
  return new Intl.NumberFormat('zh-CN', { 
    minimumFractionDigits: 2, 
    maximumFractionDigits: 2 
  }).format(value)
}

const formatCurrency = (value, showSign = false) => {
  if (value === null || value === undefined) return '无'
  const formatter = new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
  const formatted = formatter.format(Math.abs(value))
  if (showSign) {
    if (value > 0) return `+${formatted}`
    if (value < 0) return `-${formatted}`
  }
  return value < 0 && !showSign ? `-${formatted}` : formatted
}

// 格式化百分比
const formatPercentage = (value, showSign = false) => {
  if (value === null || value === undefined) return '无'
  const formatted = (value * 100).toFixed(2) + '%'
  return showSign && value > 0 ? '+' + formatted : formatted
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '无'
  return new Date(dateString).toLocaleDateString('zh-CN')
}

// 获取分析状态类型
const getAnalysisStatusType = (status) => {
  const typeMap = {
    'completed': 'success',
    'processing': 'warning',
    'failed': 'danger',
    'pending': 'info'
  }
  return typeMap[status] || 'info'
}

// 获取分析状态文本
const getAnalysisStatusText = (status) => {
  const textMap = {
    'completed': '已完成',
    'processing': '分析中',
    'failed': '失败',
    'pending': '待分析'
  }
  return textMap[status] || '未知'
}

// 获取风险等级类型
const getRiskLevelType = (level) => {
  const typeMap = {
    'normal': 'success',
    'low': 'warning',
    'medium': 'warning',
    'high': 'danger',
    'critical': 'danger',
    'severe': 'danger'
  }
  return typeMap[level] || 'info'
}

// 获取风险等级文本
const getRiskLevelText = (level) => {
  const textMap = {
    'normal': '正常',
    'low': '低风险',
    'medium': '中风险',
    'high': '高风险',
    'critical': '严重风险',
    'severe': '严重风险'
  }
  return textMap[level] || '未知'
}

// 获取搜索网址列表
const getSearchUrls = (analysisResult) => {
  if (!analysisResult || !analysisResult.api_response) {
    return []
  }

  // 从API响应中提取搜索网址
  if (analysisResult.api_response.search_urls) {
    return analysisResult.api_response.search_urls
  }

  return []
}

</script>

<style lang="scss" scoped>
.analysis-detail-dialog {
  .analysis-detail-content {
    max-height: 70vh;
    overflow-y: auto;

    .el-card {
      margin-bottom: 20px;

      &:last-child {
        margin-bottom: 0;
      }
    }

    .card-header {
      display: flex;
      align-items: center;
      gap: 8px;

      .el-tag {
        margin-left: auto;
      }
    }

    .info-item {
      margin-bottom: 12px;
      display: flex;
      align-items: center;

      .label {
        color: #666;
        font-size: 14px;
        min-width: 80px;
        flex-shrink: 0;
      }

      .value {
        font-weight: 500;
        color: #333;

        &.price {
          color: #e6a23c;
          font-weight: 600;
        }

        &.market-price {
          color: #67c23a;
        }

        &.positive {
          color: #f56c6c;
        }

        &.negative {
          color: #67c23a;
        }
      }
    }

    .project-info {
      margin-top: 16px;
    }

    // 搜索网址样式
    .search-urls-section {
      margin-bottom: 24px;

      h4 {
        margin-bottom: 12px;
        color: #333;
        font-size: 16px;
        font-weight: 500;
      }

      .search-urls {
        .search-url-item {
          margin-bottom: 8px;
          padding: 8px 12px;
          background-color: #f8f9fa;
          border: 1px solid #e9ecef;
          border-radius: 6px;

          &:last-child {
            margin-bottom: 0;
          }

          .el-link {
            font-size: 13px;
            word-break: break-all;
            line-height: 1.4;
          }
        }
      }
    }

    // 数据来源样式
    .data-sources-section {
      margin-bottom: 24px;

      h4 {
        margin-bottom: 12px;
        color: #333;
        font-size: 16px;
        font-weight: 500;
      }

      .data-source-table {
        margin-bottom: 8px;

        .el-table__header th {
          background: #f5f7fa;
          color: #333;
          font-weight: 600;
        }

        .el-table__body tr:nth-child(odd) {
          background: #fbfdff;
        }

        .data-count-cell {
          display: flex;
          flex-direction: column;
          gap: 2px;

          .price-reference {
            font-size: 12px;
            color: #a6a6a6;
          }
        }
      }

      .reliability-cell {
        display: flex;
        justify-content: center;

        .reliability-rate {
          --el-rate-icon-size: 18px;

          :deep(.el-rate__icon) {
            color: rgba(31, 31, 31, 0.25) !important;
          }

          :deep(.el-rate__icon.is-active),
          :deep(.el-rate__decimal) {
            color: #1f1f1f !important;
          }
        }

        .reliability-placeholder {
          color: #666;
          font-size: 12px;
        }
      }

      .data-source-note {
        margin: 0;
        color: #909399;
        font-size: 12px;
        line-height: 1.6;
      }
    }

    .analysis-content {
      .price-prediction,
      .reasonability-assessment,
      .search-urls-section,
      .data-sources-section,
      .analysis-reasoning,
      .risk-factors {
        margin-bottom: 20px;

        h4 {
          margin-bottom: 12px;
          color: #303133;
          font-size: 16px;
        }
      }

      .prediction-item,
      .assessment-item {
        margin-bottom: 12px;

        .prediction-label,
        .assessment-label {
          display: block;
          color: #666;
          font-size: 14px;
          margin-bottom: 4px;
        }

        .prediction-value,
        .assessment-value {
          font-size: 16px;
          font-weight: 600;
          color: #e6a23c;

          &.positive {
            color: #f56c6c;
          }

          &.negative {
            color: #67c23a;
          }
        }
      }

      .reasoning-content,
      .risk-content {
        padding: 12px;
        background: #f8f9fa;
        border-radius: 4px;
        line-height: 1.6;
        color: #555;
      }

      .analysis-meta {
        .meta-item {
          display: flex;
          align-items: center;
          margin-bottom: 8px;

          .meta-label {
            color: #666;
            font-size: 14px;
            min-width: 80px;
            flex-shrink: 0;
          }

          .meta-value {
            color: #333;
          }
        }
      }
    }

    .analysis-failed,
    .analysis-processing {
      padding: 20px 0;
    }

    .error-content {
      padding: 20px 0;
      text-align: center;
    }
  }

  .dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
  }
}

// 响应式设计
@media (max-width: 768px) {
  .analysis-detail-dialog {
    .analysis-detail-content {
      .el-row {
        .el-col {
          margin-bottom: 12px;
        }
      }

      .info-item {
        flex-direction: column;
        align-items: flex-start;

        .label {
          margin-bottom: 4px;
          min-width: auto;
        }
      }
    }
  }
}
</style>
