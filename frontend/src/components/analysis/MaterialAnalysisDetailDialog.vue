<template>
  <el-dialog
    v-model="dialogVisible"
    title="材料分析详情"
    width="95%"
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
              <el-tag type="success" size="small">基期信息价</el-tag>
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
                <span class="value">{{ getPriceTypeText(detailData.matched_base_material.price_type) }}</span>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12" :md="8">
              <div class="info-item">
                <span class="label">适用地区：</span>
                <span class="value">{{ getRegionText(detailData.matched_base_material.region) }}</span>
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
                <span class="label">期数：</span>
                <span class="value">{{ getPeriodText(detailData.matched_base_material) }}</span>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12" :md="8">
              <div class="info-item">
                <span class="label">材料分类：</span>
                <span class="value">{{ detailData.matched_base_material.category || '无' }}</span>
              </div>
            </el-col>
          </el-row>

          <div
            v-if="detailData.matched_base_materials?.length"
            class="price-history"
          >
            <el-divider>各期信息价记录</el-divider>
            <el-table
              :data="detailData.matched_base_materials"
              border
              size="small"
              class="price-history-table"
            >
              <el-table-column label="期数" min-width="140">
                <template #default="{ row }">
                  <div class="period-cell">
                    <span>{{ getPeriodText(row) }}</span>
                    <el-tag
                      v-if="row.is_current_match"
                      size="small"
                      type="success"
                      class="current-tag"
                    >
                      当前匹配
                    </el-tag>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="信息价（除税）" min-width="150">
                <template #default="{ row }">
                  {{ formatCurrency(row.price_excluding_tax ?? row.price) }}
                </template>
              </el-table-column>
              <el-table-column label="信息价（含税）" min-width="150">
                <template #default="{ row }">
                  {{ formatCurrency(row.price_including_tax ?? row.price) }}
                </template>
              </el-table-column>
              <el-table-column label="计量单位" prop="unit" min-width="110" />
              <el-table-column label="价格类型" min-width="130">
                <template #default="{ row }">
                  {{ getPriceTypeText(row.price_type) }}
                </template>
              </el-table-column>
              <el-table-column label="数据来源" min-width="160">
                <template #default="{ row }">
                  {{ row.price_source || row.source || '无' }}
                </template>
              </el-table-column>
              <el-table-column label="适用地区" min-width="140">
                <template #default="{ row }">
                  {{ getRegionText(row.region) }}
                </template>
              </el-table-column>
            </el-table>
          </div>
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
              
              <!-- 单位转换提示 -->
              <el-alert
                v-if="unitConversionInfo?.needsConversion"
                :title="`单位已转换：市场信息价单位(${unitConversionInfo.baseUnit}) → 项目材料单位(${unitConversionInfo.projectUnit})`"
                :description="`基期信息价 ${formatCurrency(detailData.matched_base_material?.price, false, 2)}/${unitConversionInfo.baseUnit} = ${formatCurrency(convertedBasePrice, false, 4)}/${unitConversionInfo.projectUnit}`"
                type="info"
                :closable="false"
                show-icon
                class="unit-conversion-alert"
              />
              <el-alert
                v-else-if="unitConversionInfo && !unitConversionInfo.canConvert && unitConversionInfo.projectUnit !== unitConversionInfo.baseUnit"
                :title="`单位不兼容警告`"
                :description="`项目材料单位(${unitConversionInfo.projectUnit})与市场信息价单位(${unitConversionInfo.baseUnit})无法自动转换，价格对比结果可能不准确`"
                type="warning"
                :closable="false"
                show-icon
                class="unit-conversion-alert"
              />
              
              <el-row :gutter="20">
                <el-col :xs="24" :sm="12" :md="4">
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
                <el-col :xs="24" :sm="12" :md="4">
                  <div class="assessment-item">
                    <span class="assessment-label">价格差异：</span>
                    <span 
                      class="assessment-value"
                      :class="{
                        'positive': priceDifference > 0,
                        'negative': priceDifference < 0
                      }"
                    >
                      {{ formatCurrency(priceDifference, true) }}
                      <span v-if="unitConversionInfo?.needsConversion" class="unit-hint">
                        /{{ unitConversionInfo.projectUnit }}
                      </span>
                    </span>
                  </div>
                </el-col>
                <el-col :xs="24" :sm="12" :md="4">
                  <div class="assessment-item">
                    <span class="assessment-label">合同期平均价：</span>
                    <span class="assessment-value">
                      {{ formatCurrency(convertedContractAvgPrice) }}
                      <span v-if="unitConversionInfo?.needsConversion" class="unit-hint">
                        /{{ unitConversionInfo.projectUnit }}
                      </span>
                    </span>
                  </div>
                </el-col>
                <el-col :xs="24" :sm="12" :md="4">
                  <div class="assessment-item">
                    <span class="assessment-label">风险幅度：</span>
                    <span 
                      class="assessment-value"
                      :class="{
                        'positive': riskRate > 0,
                        'negative': riskRate < 0
                      }"
                    >
                      {{ formatPercentage(riskRate, true) }}
                    </span>
                  </div>
                </el-col>
                <el-col :xs="24" :sm="12" :md="4">
                  <div class="assessment-item">
                    <span class="assessment-label">调差：</span>
                    <span 
                      class="assessment-value"
                      :class="{
                        'positive': priceAdjustment > 0,
                        'negative': priceAdjustment < 0
                      }"
                    >
                      {{ formatCurrency(priceAdjustment, true) }}
                      <span v-if="detailData.analysis_result.quantity" class="quantity-hint">
                        （数量：{{ formatNumber(detailData.analysis_result.quantity) }} {{ detailData.project_material?.unit || detailData.analysis_result.unit || '' }}）
                      </span>
                    </span>
                  </div>
                </el-col>
                <el-col :xs="24" :sm="12" :md="4">
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
                <el-table-column prop="price_range" label="预测价格区间" min-width="160" align="center">
                  <template #default="{ row }">
                    <span class="price-range-cell">{{ row.price_range || '—' }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="sample_description" label="样本描述" min-width="200" show-overflow-tooltip>
                  <template #default="{ row }">
                    <span>{{ row.sample_description || '—' }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="notes" label="可选补充" min-width="200" show-overflow-tooltip>
                  <template #default="{ row }">
                    <span>{{ row.notes || '—' }}</span>
                  </template>
                </el-table-column>
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

            <!-- 分析历史 -->
            <div v-if="analysisHistory.length > 0" class="analysis-history">
              <el-divider>分析历史</el-divider>
              <el-timeline>
                <el-timeline-item
                  v-for="history in analysisHistory"
                  :key="history.id"
                  :timestamp="formatDate(history.created_at)"
                  placement="top"
                >
                  <div class="history-item">
                    <div class="history-action">{{ history.action }}</div>
                    <div class="history-meta">
                      <el-tag v-if="history.analysis_model" size="small" type="info">
                        {{ history.analysis_model }}
                      </el-tag>
                      <span
                        v-if="hasHistoryPriceRange(history)"
                        class="history-price-range"
                      >
                        价格区间：
                        <span class="price">¥{{ formatNumber(history.predicted_price_min) }}</span>
                        <span class="price-sep">~</span>
                        <span class="price">¥{{ formatNumber(history.predicted_price_max) }}</span>
                      </span>
                    </div>
                    <div v-if="history.note" class="history-note">{{ history.note }}</div>
                    <div class="history-user">操作人: {{ history.created_by_name || '系统' }}</div>
                  </div>
                </el-timeline-item>
              </el-timeline>
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
        
        <!-- 人工判定按钮 -->
        <template v-if="detailData?.project_material && !detailData.project_material.is_matched && detailData.project_material.needs_review">
          <el-button type="success" @click="handleReview(true)">
            判定为已匹配
          </el-button>
          <el-button type="danger" @click="handleReview(false)">
            判定为未匹配
          </el-button>
        </template>

        <el-button v-if="detailData?.project_material" type="primary" @click="goToMaterialDetail">
          查看完整详情
        </el-button>
      </span>
    </template>

    <!-- AI模型选择对话框 -->
    <el-dialog
      v-model="showModelSelectDialog"
      title="选择AI分析模型"
      width="480px"
      :close-on-click-modal="false"
      center
      append-to-body
      class="ai-model-select-dialog"
    >
      <div class="model-select-content">
        <p class="model-select-hint">请选择用于价格分析的AI大模型：</p>
        <el-radio-group v-model="selectedAIModel" class="model-radio-group">
          <el-radio value="dashscope" size="large" border class="model-radio-item">
            <div class="model-info">
              <div class="model-name">
                <el-icon><Promotion /></el-icon>
                通义千问 (Qwen)
              </div>
              <div class="model-desc">阿里云通义千问大模型，支持联网搜索</div>
            </div>
          </el-radio>
          <el-radio value="doubao" size="large" border class="model-radio-item">
            <div class="model-info">
              <div class="model-name">
                <el-icon><MagicStick /></el-icon>
                豆包 (Doubao)
              </div>
              <div class="model-desc">字节跳动豆包大模型，高性能推理</div>
            </div>
          </el-radio>
          <el-radio value="deepseek" size="large" border class="model-radio-item">
            <div class="model-info">
              <div class="model-name">
                <el-icon><ChatDotRound /></el-icon>
                DeepSeek (V3)
              </div>
              <div class="model-desc">深度求索DeepSeek-V3模型，超强推理能力</div>
            </div>
          </el-radio>
        </el-radio-group>
      </div>
      <template #footer>
        <el-button @click="showModelSelectDialog = false">取消</el-button>
        <el-button
          type="primary"
          :disabled="!selectedAIModel"
          @click="handleModelSelectConfirm"
        >
          开始分析
        </el-button>
      </template>
    </el-dialog>
  </el-dialog>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Document, Connection, Warning, TrendCharts, Promotion, MagicStick, ChatDotRound } from '@element-plus/icons-vue'
import { getMaterialAnalysisDetail, analyzePricedMaterials, analyzeSingleMaterial } from '@/api/analysis'
import { updateProjectMaterial } from '@/api/projects'
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

const emit = defineEmits(['update:modelValue', 'close', 'refresh'])

const router = useRouter()
const dialogVisible = ref(false)
const loading = ref(false)
const detailData = ref(null)
const error = ref('')

// AI模型选择相关
const showModelSelectDialog = ref(false)
const selectedAIModel = ref('dashscope') // 默认使用通义千问

const dataSourceRows = computed(() =>
  formatAnalysisDataSources(detailData.value?.analysis_result || null)
)

const dataSourceNote = computed(() =>
  getDataSourceNote(detailData.value?.analysis_result || null)
)

const analysisHistory = computed(() => {
  if (!detailData.value?.analysis_history) {
    return []
  }
  return detailData.value.analysis_history.map(hist => ({
    id: hist.id,
    action: hist.action,
    note: hist.note,
    created_at: hist.created_at,
    created_by_name: hist.created_by_name || '系统',
    analysis_model: hist.analysis_model || '',
    predicted_price_min: hist.predicted_price_min,
    predicted_price_max: hist.predicted_price_max
  }))
})

const hasHistoryPriceRange = (history) => {
  return history?.predicted_price_min !== null &&
    history?.predicted_price_min !== undefined &&
    history?.predicted_price_max !== null &&
    history?.predicted_price_max !== undefined
}

// 单位转换系数表（转换为基础单位）
// 质量单位统一转换为 kg
// 长度单位统一转换为 m
// 面积单位统一转换为 m²
// 体积单位统一转换为 m³
const unitConversionTable = {
  // 质量单位 -> kg
  'kg': { base: 'kg', factor: 1 },
  'KG': { base: 'kg', factor: 1 },
  '千克': { base: 'kg', factor: 1 },
  'g': { base: 'kg', factor: 0.001 },
  'G': { base: 'kg', factor: 0.001 },
  '克': { base: 'kg', factor: 0.001 },
  't': { base: 'kg', factor: 1000 },
  'T': { base: 'kg', factor: 1000 },
  '吨': { base: 'kg', factor: 1000 },
  
  // 长度单位 -> m
  'm': { base: 'm', factor: 1 },
  'M': { base: 'm', factor: 1 },
  '米': { base: 'm', factor: 1 },
  'cm': { base: 'm', factor: 0.01 },
  'CM': { base: 'm', factor: 0.01 },
  '厘米': { base: 'm', factor: 0.01 },
  'mm': { base: 'm', factor: 0.001 },
  'MM': { base: 'm', factor: 0.001 },
  '毫米': { base: 'm', factor: 0.001 },
  'km': { base: 'm', factor: 1000 },
  'KM': { base: 'm', factor: 1000 },
  '千米': { base: 'm', factor: 1000 },
  '公里': { base: 'm', factor: 1000 },
  
  // 面积单位 -> m²
  'm²': { base: 'm²', factor: 1 },
  'm2': { base: 'm²', factor: 1 },
  'M²': { base: 'm²', factor: 1 },
  'M2': { base: 'm²', factor: 1 },
  '平方米': { base: 'm²', factor: 1 },
  '㎡': { base: 'm²', factor: 1 },
  'cm²': { base: 'm²', factor: 0.0001 },
  'cm2': { base: 'm²', factor: 0.0001 },
  '平方厘米': { base: 'm²', factor: 0.0001 },
  'mm²': { base: 'm²', factor: 0.000001 },
  'mm2': { base: 'm²', factor: 0.000001 },
  '平方毫米': { base: 'm²', factor: 0.000001 },
  
  // 体积单位 -> m³
  'm³': { base: 'm³', factor: 1 },
  'm3': { base: 'm³', factor: 1 },
  'M³': { base: 'm³', factor: 1 },
  'M3': { base: 'm³', factor: 1 },
  '立方米': { base: 'm³', factor: 1 },
  '方': { base: 'm³', factor: 1 },
  'L': { base: 'm³', factor: 0.001 },
  'l': { base: 'm³', factor: 0.001 },
  '升': { base: 'm³', factor: 0.001 },
  'mL': { base: 'm³', factor: 0.000001 },
  'ml': { base: 'm³', factor: 0.000001 },
  '毫升': { base: 'm³', factor: 0.000001 },
  
  // 其他单位（无需转换）
  '个': { base: '个', factor: 1 },
  '只': { base: '个', factor: 1 },
  '件': { base: '个', factor: 1 },
  '套': { base: '套', factor: 1 },
  '组': { base: '组', factor: 1 },
  '台': { base: '台', factor: 1 },
  '根': { base: '根', factor: 1 },
  '张': { base: '张', factor: 1 },
  '块': { base: '块', factor: 1 },
  '片': { base: '片', factor: 1 },
  '卷': { base: '卷', factor: 1 },
  '桶': { base: '桶', factor: 1 },
  '袋': { base: '袋', factor: 1 },
  '箱': { base: '箱', factor: 1 },
  '盒': { base: '盒', factor: 1 }
}

// 获取单位转换信息
const getUnitInfo = (unit) => {
  if (!unit) return null
  const trimmedUnit = unit.trim()
  return unitConversionTable[trimmedUnit] || null
}

// 计算两个单位之间的转换系数
// 返回：将 fromUnit 的价格转换为 toUnit 的价格所需的系数
// 例如：fromUnit='t', toUnit='kg' => 返回 0.001（因为 1元/t = 0.001元/kg）
const getUnitConversionFactor = (fromUnit, toUnit) => {
  const fromInfo = getUnitInfo(fromUnit)
  const toInfo = getUnitInfo(toUnit)
  
  // 如果任一单位无法识别，返回 1（不转换）
  if (!fromInfo || !toInfo) return 1
  
  // 如果基础单位不同，无法转换，返回 1
  if (fromInfo.base !== toInfo.base) return 1
  
  // 转换系数 = fromFactor / toFactor
  // 例如：t(1000) -> kg(1)，系数 = 1000/1 = 1000
  // 意味着 1t = 1000kg，所以 1元/t = 1/1000 元/kg = 0.001元/kg
  // 价格转换需要除以这个比率
  return fromInfo.factor / toInfo.factor
}

// 单位转换信息（用于显示）
const unitConversionInfo = computed(() => {
  const projectUnit = detailData.value?.project_material?.unit
  const baseUnit = detailData.value?.matched_base_material?.unit
  
  if (!projectUnit || !baseUnit) return null
  
  const factor = getUnitConversionFactor(baseUnit, projectUnit)
  
  if (factor === 1 && projectUnit !== baseUnit) {
    // 单位不同但无法转换
    return {
      needsConversion: false,
      canConvert: false,
      projectUnit,
      baseUnit,
      factor: 1,
      message: `单位不兼容（${projectUnit} vs ${baseUnit}）`
    }
  }
  
  if (factor !== 1) {
    return {
      needsConversion: true,
      canConvert: true,
      projectUnit,
      baseUnit,
      factor,
      message: `已将 ${baseUnit} 转换为 ${projectUnit}（系数: ${factor}）`
    }
  }
  
  return {
    needsConversion: false,
    canConvert: true,
    projectUnit,
    baseUnit,
    factor: 1,
    message: null
  }
})

// 转换后的基期信息价（按项目材料单位计算）
const convertedBasePrice = computed(() => {
  const basePrice = detailData.value?.matched_base_material?.price
  if (basePrice === null || basePrice === undefined) return null
  
  const conversionFactor = unitConversionInfo.value?.factor || 1
  // 价格转换：原价格 / 转换系数
  // 例如：4684元/t，转换系数1000，结果 = 4684/1000 = 4.684元/kg
  return basePrice / conversionFactor
})

// 转换后的合同期平均价（按项目材料单位计算）
const convertedContractAvgPrice = computed(() => {
  const contractAvgPrice = detailData.value?.analysis_result?.contract_average_price
  if (contractAvgPrice === null || contractAvgPrice === undefined) return null
  
  const conversionFactor = unitConversionInfo.value?.factor || 1
  // 如果合同期平均价是基于市场信息价单位计算的，需要转换
  // 但通常合同期平均价应该已经是按项目材料单位的
  // 这里需要判断合同期平均价的单位来源
  
  // 检查合同期平均价是否接近项目材料单价（说明已按项目单位计算）
  const projectPrice = detailData.value?.project_material?.unit_price
  if (projectPrice && Math.abs(contractAvgPrice - projectPrice) / projectPrice < 0.5) {
    // 合同期平均价接近项目单价，说明已经是项目单位，无需转换
    return contractAvgPrice
  }
  
  // 检查合同期平均价是否接近基期信息价（说明是市场单位）
  const basePrice = detailData.value?.matched_base_material?.price
  if (basePrice && conversionFactor !== 1 && Math.abs(contractAvgPrice - basePrice) / basePrice < 0.5) {
    // 合同期平均价接近基期信息价，需要转换
    return contractAvgPrice / conversionFactor
  }
  
  // 默认假设合同期平均价已经是项目单位
  return contractAvgPrice
})

// 价格差异：项目材料单价 - 转换后的基期信息价
const priceDifference = computed(() => {
  const projectPrice = detailData.value?.project_material?.unit_price
  const basePrice = convertedBasePrice.value
  if (projectPrice === null || projectPrice === undefined || basePrice === null || basePrice === undefined) {
    return null
  }
  return projectPrice - basePrice
})

// 风险幅度：(合同期平均价 - 转换后的基期信息价) / 转换后的基期信息价
const riskRate = computed(() => {
  const contractAvgPrice = convertedContractAvgPrice.value
  const basePrice = convertedBasePrice.value
  if (contractAvgPrice === null || contractAvgPrice === undefined || basePrice === null || basePrice === undefined || basePrice === 0) {
    return null
  }
  return (contractAvgPrice - basePrice) / basePrice
})

// 调差：风险幅度在±5%以内则为0，超过部分乘以数量
const priceAdjustment = computed(() => {
  const contractAvgPrice = convertedContractAvgPrice.value
  const basePrice = convertedBasePrice.value
  const quantity = detailData.value?.analysis_result?.quantity ?? detailData.value?.project_material?.quantity
  
  if (contractAvgPrice === null || contractAvgPrice === undefined || 
      basePrice === null || basePrice === undefined || basePrice === 0) {
    return null
  }
  if (quantity === null || quantity === undefined) {
    return null
  }
  
  const currentRiskRate = (contractAvgPrice - basePrice) / basePrice
  const threshold = 0.05 // ±5%
  
  // 如果风险幅度在±5%以内，调差为0
  if (currentRiskRate >= -threshold && currentRiskRate <= threshold) {
    return 0
  }
  
  // 超过±5%的部分计算调差
  let excessPerUnit = 0
  if (currentRiskRate > threshold) {
    // 价格偏高，超出上限的部分
    excessPerUnit = contractAvgPrice - basePrice * (1 + threshold)
  } else {
    // 价格偏低，超出下限的部分（负值）
    excessPerUnit = contractAvgPrice - basePrice * (1 - threshold)
  }
  
  return excessPerUnit * quantity
})

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
      
      // 调试：检查项目材料状态
      if (detailData.value?.project_material) {
        console.log('材料详情状态检查:', {
          id: detailData.value.project_material.id,
          name: detailData.value.project_material.material_name,
          is_matched: detailData.value.project_material.is_matched,
          needs_review: detailData.value.project_material.needs_review,
          project_id: detailData.value.project_material.project_id,
          should_show_review_buttons: !detailData.value.project_material.is_matched && detailData.value.project_material.needs_review
        })
      }

      // 调试：检查数据源是否包含价格区间
      if (detailData.value?.analysis_result?.data_sources) {
        console.log('数据源信息:', detailData.value.analysis_result.data_sources)
        detailData.value.analysis_result.data_sources.forEach((source, idx) => {
          console.log(`数据源 ${idx + 1}:`, {
            source_type: source.source_type,
            has_price_range_min: 'price_range_min' in source,
            price_range_min: source.price_range_min,
            has_price_range_max: 'price_range_max' in source,
            price_range_max: source.price_range_max,
            all_keys: Object.keys(source)
          })
        })
      }
      // 调试：检查分析历史
      if (detailData.value?.analysis_history) {
        console.log('分析历史:', detailData.value.analysis_history)
      } else {
        console.log('没有分析历史数据')
      }
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

// 人工判定处理
const handleReview = async (isMatched) => {
  const material = detailData.value?.project_material
  if (!material) return

  // 如果判定为未匹配，先弹出模型选择对话框
  if (!isMatched) {
    showModelSelectDialog.value = true
    return
  }

  // 判定为已匹配的逻辑（保持不变）
  const actionText = '已匹配'
  try {
    await ElMessageBox.confirm(
      `确定将该材料判定为"${actionText}"吗？判定后系统将自动进行市场信息价分析。`,
      '人工判定',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'success'
      }
    )

    loading.value = true
    
    // 1. 更新材料状态
    await updateProjectMaterial(material.project_id, material.id, {
      is_matched: true,
      needs_review: false,
      match_method: 'manual_review'
    })
    
    ElMessage.success(`已判定为${actionText}，正在进行分析...`)

    // 2. 触发市场信息价材料分析
    try {
      await analyzePricedMaterials(material.project_id, {
        material_ids: [material.id],
        force_reanalyze: true,
        __skipLoading: true
      })
      ElMessage.success('分析完成')
    } catch (analysisError) {
      console.error('分析失败:', analysisError)
      ElMessage.warning('状态更新成功，但后续分析失败: ' + (analysisError.message || '未知错误'))
    }
    
    // 3. 刷新数据
    await loadMaterialDetail()
    emit('refresh')
    
  } catch (error) {
    if (error !== 'cancel') {
      console.error('判定失败:', error)
      ElMessage.error('判定失败: ' + (error.message || '未知错误'))
    }
  } finally {
    loading.value = false
  }
}

// 确认未匹配判定并开始AI分析
const handleModelSelectConfirm = async () => {
  showModelSelectDialog.value = false
  const material = detailData.value?.project_material
  if (!material) return

  let modelName = '通义千问'
  if (selectedAIModel.value === 'doubao') {
    modelName = '豆包'
  } else if (selectedAIModel.value === 'deepseek') {
    modelName = 'DeepSeek'
  }

  loading.value = true
  try {
    // 1. 更新材料状态
    await updateProjectMaterial(material.project_id, material.id, {
      is_matched: false,
      needs_review: false,
      match_method: 'manual_review'
    })
    
    ElMessage.success(`已判定为未匹配，正在后台使用 ${modelName} 进行分析...`)

    // 2. 触发AI分析（后台运行）
    // 不使用 await 阻塞，或者 catch 错误不影响 UI 状态
    analyzeSingleMaterial(material.id, {
        preferred_provider: selectedAIModel.value,
        force_reanalyze: true
    }).then(() => {
        ElMessage.success('AI分析完成，请刷新查看结果')
        // 如果当前还在查看该材料，自动刷新
        if (detailData.value?.project_material?.id === material.id) {
            loadMaterialDetail()
        }
        emit('refresh')
    }).catch(err => {
        console.error('后台AI分析失败:', err)
        ElMessage.error(`AI分析失败: ${err.message}`)
    })

    // 3. 立即刷新当前视图（显示为未匹配状态）
    await loadMaterialDetail()
    emit('refresh')

  } catch (error) {
    console.error('判定失败:', error)
    ElMessage.error('判定失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
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
const formatNumber = (value, decimals = 2) => {
  if (value === null || value === undefined) return '无'
  // 使用 toLocaleString 但不使用分组分隔符
  return Number(value).toLocaleString('zh-CN', { 
    minimumFractionDigits: decimals, 
    maximumFractionDigits: decimals,
    useGrouping: true // 数量可以保留逗号分隔
  })
}

const formatCurrency = (value, showSign = false, decimals = 4) => {
  if (value === null || value === undefined) return '无'
  // 使用 toFixed 避免逗号分隔符
  const absValue = Math.abs(value).toFixed(decimals)
  const formatted = `¥${absValue}`
  if (showSign) {
    if (value > 0) return `+${formatted}`
    if (value < 0) return `-${formatted}`
  }
  return value < 0 && !showSign ? `-${formatted}` : formatted
}

// 格式化百分比
const formatPercentage = (value, showSign = false, decimals = 2) => {
  if (value === null || value === undefined) return '无'
  const formatted = (value * 100).toFixed(decimals) + '%'
  if (showSign) {
    if (value > 0) return '+' + formatted
    if (value < 0) return formatted // 负数已经有负号
  }
  return formatted
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '无'
  return new Date(dateString).toLocaleDateString('zh-CN')
}

// 期数显示（优先 price_date，回退 effective_date）
const getPeriodText = (obj) => {
  if (!obj) return '无'
  if (obj.price_date) {
    const parts = String(obj.price_date).split('-')
    const y = parts[0]
    const m = parts[1] ? parts[1].padStart(2, '0') : ''
    return y && m ? `${y}年${m}月` : obj.price_date
  }
  if (obj.effective_date) {
    try {
      const d = new Date(obj.effective_date)
      const y = d.getFullYear()
      const m = String(d.getMonth() + 1).padStart(2, '0')
      return `${y}年${m}月`
    } catch (_) {
      return formatDate(obj.effective_date)
    }
  }
  return '无'
}

// 地区中文映射（常见省市与全国）
const getRegionText = (region) => {
  if (!region) return '无'
  const map = {
    beijing: '北京市',
    shanghai: '上海市',
    guangzhou: '广州市',
    shenzhen: '深圳市',
    hangzhou: '杭州市',
    ningbo: '宁波市',
    wenzhou: '温州市',
    shaoxing: '绍兴市',
    jiaxing: '嘉兴市',
    huzhou: '湖州市',
    jinhua: '金华市',
    nanjing: '南京市',
    suzhou: '苏州市',
    wuxi: '无锡市',
    changzhou: '常州市',
    nantong: '南通市',
    yangzhou: '扬州市',
    xuzhou: '徐州市',
    jinan: '济南市',
    qingdao: '青岛市',
    yantai: '烟台市',
    weifang: '潍坊市',
    zibo: '淄博市',
    jining: '济宁市',
    national: '全国'
  }
  return map[region] || region
}

// 价格类型中文映射
const getPriceTypeText = (type) => {
  const map = {
    provincial: '省刊信息价',
    municipal: '市刊信息价'
  }
  return map[type] || (type || '无')
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
    'critical': '极高风险',
    'severe': '极高风险'
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

    .price-history {
      margin-top: 16px;

      .price-history-table {
        margin-top: 12px;
      }

      .period-cell {
        display: flex;
        align-items: center;
        gap: 8px;
      }

      .current-tag {
        line-height: 1;
      }
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
        width: 100%;
        overflow-x: auto;

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

        .price-range-cell {
          color: #e6a23c;
          font-weight: 500;
          font-size: 13px;
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

      .unit-conversion-alert {
        margin-bottom: 16px;
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

          .unit-hint {
            font-size: 12px;
            font-weight: normal;
            color: #909399;
          }

          .quantity-hint {
            font-size: 12px;
            font-weight: normal;
            color: #909399;
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

      .analysis-history {
        margin-top: 20px;

        .history-item {
          .history-action {
            font-weight: 500;
            color: #333;
            margin-bottom: 4px;
          }

          .history-note {
            font-size: 14px;
            color: #666;
            margin-bottom: 4px;
          }

          .history-user {
            font-size: 12px;
            color: #999;
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

.ai-model-select-dialog {
  .model-select-content {
    padding: 0 20px;
    
    .model-select-hint {
      margin: 0 0 20px 0;
      font-size: 14px;
      color: #909399;
      text-align: center;
    }
    
    .model-radio-group {
      display: flex;
      flex-direction: column;
      gap: 16px;
      width: 100%;
      
      .model-radio-item {
        width: 100%;
        height: auto !important;
        padding: 16px 20px !important;
        margin: 0 !important;
        border-radius: 12px !important;
        transition: all 0.3s ease;
        display: flex;
        align-items: flex-start;
        
        &:hover {
          border-color: #409eff;
          box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
        }
        
        &.is-checked {
          border-color: #409eff;
          background: linear-gradient(135deg, rgba(64, 158, 255, 0.08) 0%, rgba(64, 158, 255, 0.02) 100%);
          box-shadow: 0 4px 16px rgba(64, 158, 255, 0.2);
        }
        
        :deep(.el-radio__input) {
          margin-top: 4px;
        }
        
        :deep(.el-radio__label) {
          white-space: normal;
          width: 100%;
          padding-left: 12px;
        }
        
        .model-info {
          display: flex;
          flex-direction: column;
          gap: 5px;
          
          .model-name {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 16px;
            font-weight: 600;
            color: #303133;
            margin-bottom: 6px;
            
            .el-icon {
              font-size: 20px;
              color: #409eff;
            }
          }
          
          .model-desc {
            font-size: 13px;
            color: #909399;
            line-height: 1.4;
          }
        }
      }
    }
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
