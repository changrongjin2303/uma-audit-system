<template>
  <div class="analysis-details-container">
    <!-- 页面标题和工具栏 -->
    <div class="page-header">
      <div class="header-content">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item @click="$router.push('/analysis/results')">分析结果</el-breadcrumb-item>
          <el-breadcrumb-item>{{ currentProject?.name || '分析详情' }}</el-breadcrumb-item>
        </el-breadcrumb>
        <h1 class="page-title">{{ currentProject?.name || '项目分析详情' }}</h1>
        <p class="page-subtitle">查看项目的详细AI价格分析结果和合理性评估</p>
      </div>
      <div class="header-actions">
        <el-button
          type="success"
          :icon="TrendCharts"
          @click="startUnpricedAnalysis"
          :loading="analysisState.isAnalyzing && analysisState.analysisType === 'unpriced'"
          :disabled="analysisState.isAnalyzing"
        >
          {{ (analysisState.isAnalyzing && analysisState.analysisType === 'unpriced') ? '分析中...' : 'AI分析(无信息价材料)' }}
        </el-button>
        <el-button
          type="warning"
          :icon="TrendCharts"
          @click="startPricedAnalysis"
          :loading="analysisState.isAnalyzing && analysisState.analysisType === 'priced'"
          :disabled="analysisState.isAnalyzing"
        >
          {{ (analysisState.isAnalyzing && analysisState.analysisType === 'priced') ? '分析中...' : 'AI价格分析(市场信息价材料)' }}
        </el-button>
        <el-button
          type="primary"
          :icon="Document"
          @click="generateReport"
        >
          生成报告
        </el-button>
      </div>
    </div>

    <!-- 分析进度显示 -->
    <div v-if="analysisState.isAnalyzing" class="analysis-progress-section">
      <el-card>
        <div class="progress-content">
          <div class="progress-header">
            <h3>AI价格分析进行中</h3>
            <span class="progress-text">{{ analysisState.currentStep }}</span>
          </div>
          
          <el-progress
            :percentage="analysisState.progress"
            :stroke-width="8"
            color="#409eff"
            class="progress-bar"
          />
          
          <div class="progress-info">
            <span>进度: {{ analysisState.completedSteps }}/{{ analysisState.totalSteps }} 步骤</span>
            <span>{{ analysisState.progress }}%</span>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 分析概览统计 -->
    <div class="overview-section">
      <el-row :gutter="20" class="stats-row">
        <el-col :xs="24" :sm="12" :lg="6">
          <div class="stat-card">
            <div class="stat-icon total">
              <el-icon><Box /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ analysisStats.totalMaterials }}</div>
              <div class="stat-label">材料总数</div>
            </div>
          </div>
        </el-col>

        <el-col :xs="24" :sm="12" :lg="6">
          <div class="stat-card">
            <div class="stat-icon analyzed">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ analysisStats.analyzedMaterials }}</div>
              <div class="stat-label">已分析材料</div>
              <div class="stat-progress">
                {{ Math.round((analysisStats.analyzedMaterials / analysisStats.totalMaterials) * 100) }}%
              </div>
            </div>
          </div>
        </el-col>

        <el-col :xs="24" :sm="12" :lg="6">
          <div class="stat-card">
            <div class="stat-icon reasonable">
              <el-icon><SuccessFilled /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ analysisStats.reasonableMaterials }}</div>
              <div class="stat-label">价格合理</div>
              <div class="stat-progress success">
                {{ analysisStats.analyzedMaterials > 0 ? Math.round((analysisStats.reasonableMaterials / analysisStats.analyzedMaterials) * 100) : 0 }}%
              </div>
            </div>
          </div>
        </el-col>

        <el-col :xs="24" :sm="12" :lg="6">
          <div class="stat-card">
            <div class="stat-icon risk">
              <el-icon><Warning /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ analysisStats.riskMaterials }}</div>
              <div class="stat-label">存在风险</div>
              <div class="stat-progress danger">
                {{ analysisStats.analyzedMaterials > 0 ? Math.round((analysisStats.riskMaterials / analysisStats.analyzedMaterials) * 100) : 0 }}%
              </div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 分析结果列表 -->
    <el-card class="results-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="card-title">分析结果详情</span>
            <!-- 分析结果类型切换 -->
            <el-button-group class="analysis-type-toggle">
              <el-button
                :type="activeAnalysisType === 'unpriced' ? 'primary' : ''"
                @click="switchAnalysisType('unpriced')"
                size="small"
              >
                无信息价材料分析结果
              </el-button>
              <el-button
                :type="activeAnalysisType === 'priced' ? 'primary' : ''"
                @click="switchAnalysisType('priced')"
                size="small"
              >
                市场信息价材料分析结果
              </el-button>
            </el-button-group>
          </div>
          <div class="header-filters">
            <el-input
              v-model="searchKeyword"
              placeholder="输入材料名称搜索"
              prefix-icon="Search"
              clearable
              @input="handleFilterChange"
              style="width: 200px; margin-right: 8px;"
            />
            <el-select
              v-model="filterStatus"
              placeholder="筛选状态"
              @change="handleFilterChange"
              style="width: 120px; margin-right: 8px;"
            >
              <el-option label="全部" value="" />
              <el-option label="已分析" value="completed" />
              <el-option label="分析中" value="processing" />
              <el-option label="待分析" value="pending" />
              <el-option label="失败" value="failed" />
            </el-select>
            <el-select
              v-model="filterRisk"
              placeholder="风险等级"
              @change="handleFilterChange"
              style="width: 120px; margin-right: 8px;"
            >
              <el-option label="全部" value="" />
              <el-option label="正常" value="normal" />
              <el-option label="低风险" value="low" />
              <el-option label="中风险" value="medium" />
              <el-option label="高风险" value="high" />
              <el-option label="严重风险" value="critical" />
            </el-select>
            <el-button :icon="Refresh" @click="fetchAnalysisResults">
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <!-- 批量操作工具栏（与项目详情一致的结构） -->
      <div v-if="selectedCount > 0 || selectedResults.length > 0 || allSelected" class="batch-toolbar">
        <div class="selected-info">
          已选择 {{ selectedCount || selectedResults.length }} 条结果
          <el-divider direction="vertical" />
          <el-switch
            v-model="allSelected"
            inline-prompt
            active-text="全选所有页"
            inactive-text="仅选本页"
            @change="() => syncSelectionOnPage(tableRef, analysisResults)"
          />
        </div>
        <div class="batch-actions">
          <el-button type="primary" size="small" @click="batchReanalyze">重新分析</el-button>
          <el-button type="warning" size="small" @click="batchAdjust">批量调整</el-button>
          <el-button type="danger" size="small" @click="batchDeleteAnalyses">批量删除</el-button>
        </div>
      </div>

      <!-- 无信息价材料分析结果表格 -->
      <div v-show="activeAnalysisType === 'unpriced' && analysisResults.length > 0" class="table-container">
        <div class="table-wrapper">
          <el-table
            ref="tableRef"
            v-loading="loading"
            :data="analysisResults"
            :row-key="row => row.id"
            :reserve-selection="true"
            @selection-change="onSelectionChange"
            stripe
            style="width: 100%; height: 100%"
            height="100%"
          >
            <el-table-column type="selection" width="50" />
            <el-table-column prop="material_name" label="材料名称" min-width="150">
              <template #default="{ row }">
                <div class="material-name">{{ row.material_name }}</div>
              </template>
            </el-table-column>
            <el-table-column prop="specification" label="规格型号" min-width="120">
              <template #default="{ row }">
                <span class="material-spec">{{ row.specification || '无规格' }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="unit" label="单位" width="80" />
            <el-table-column prop="project_price" label="报审单价" width="120">
              <template #default="{ row }">
                <span v-if="row.project_price !== null && row.project_price !== undefined">¥{{ formatDecimal(row.project_price) }}</span>
                <span v-else class="no-data">-</span>
              </template>
            </el-table-column>
            <el-table-column prop="predicted_price_range" label="AI分析区间" width="180">
              <template #default="{ row }">
                <div v-if="row.predicted_price_min && row.predicted_price_max" class="price-range">
                  <span>¥{{ formatDecimal(row.predicted_price_min) }}</span>
                  <span class="range-separator">~</span>
                  <span>¥{{ formatDecimal(row.predicted_price_max) }}</span>
                </div>
                <span v-else class="no-data">-</span>
              </template>
            </el-table-column>
            <!-- 删除加权平均价列 -->
            <!-- <el-table-column prop="predicted_price_avg" label="加权平均价" width="140">
              <template #default="{ row }">
                <span v-if="row.predicted_price_avg" class="weighted-price">
                  ¥{{ formatNumber(row.predicted_price_avg) }}
                </span>
                <span v-else class="no-data">-</span>
              </template>
            </el-table-column> -->
            <el-table-column prop="deviation" label="偏差率" width="100">
              <template #default="{ row }">
                <span v-if="row.deviation !== null" :class="getDeviationClass(row.deviation)">
                  {{ row.deviation >= 0 ? '+' : '' }}{{ Math.round(row.deviation) }}%
                </span>
                <span v-else class="no-data">-</span>
              </template>
            </el-table-column>
            <!-- 置信度列已移除 -->
            <el-table-column prop="risk_level" label="风险等级" width="100">
              <template #default="{ row }">
                <el-tag v-if="row.risk_level" :type="getRiskType(row.risk_level)" size="small">
                  {{ getRiskText(row.risk_level) }}
                </el-tag>
                <span v-else class="no-data">-</span>
              </template>
            </el-table-column>
            <el-table-column prop="analysis_status" label="分析状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.analysis_status)" size="small">
                  {{ getStatusText(row.analysis_status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="analyzed_at" label="分析时间" width="180">
              <template #default="{ row }">
                {{ row.analyzed_at ? formatDate(row.analyzed_at) : '-' }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button
                  type="primary"
                  link
                  size="small"
                  :icon="View"
                  @click="viewDetail(row)"
                >
                  详情
                </el-button>
                <el-button
                  v-if="row.analysis_status === 'pending' || row.analysis_status === 'failed'"
                  type="success"
                  link
                  size="small"
                  :icon="TrendCharts"
                  @click="reanalyze(row)"
                >
                  重新分析
                </el-button>
                <el-button
                  v-if="row.analysis_status === 'completed'"
                  type="warning"
                  link
                  size="small"
                  :icon="Edit"
                  @click="adjustResult(row)"
                >
                  调整
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 分页：统一为通用组件 -->
        <div class="pagination-wrapper">
          <BasePagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.size"
            :total="pagination.total"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
          />
        </div>
      </div>

      <!-- 市场信息价材料分析结果的批量操作工具栏 -->
      <div v-if="activeAnalysisType === 'priced' && (selectedPricedCount > 0 || selectedPricedResults.length > 0 || allPricedSelected)" class="batch-toolbar">
        <div class="selected-info">
          已选择 {{ selectedPricedCount || selectedPricedResults.length }} 条结果
          <el-button 
            type="primary" 
            link 
            size="small" 
            @click="selectAllPriced" 
            v-if="!allPricedSelected"
          >
            全选当前页
          </el-button>
          <el-button 
            type="primary" 
            link 
            size="small" 
            @click="clearPricedSelection"
            v-if="allPricedSelected || selectedPricedResults.length > 0"
          >
            清空选择
          </el-button>
        </div>
        <div class="batch-actions">
          <el-button type="primary" size="small" @click="batchReanalyzePriced">重新分析</el-button>
          <el-button type="warning" size="small" @click="batchAdjustPriced">批量调整</el-button>
          <el-button type="danger" size="small" @click="batchDeletePricedAnalyses">批量删除</el-button>
        </div>
      </div>

      <!-- 市场信息价材料分析结果表格 -->
      <div v-show="activeAnalysisType === 'priced' && pricedAnalysisResults.length > 0" class="table-container">
        <div class="table-wrapper">
          <el-table
            ref="pricedTableRef"
            v-loading="loading"
            :data="pricedAnalysisResults"
            :row-key="row => row.material_id"
            stripe
            style="width: 100%; height: 100%"
            height="100%"
            @selection-change="handlePricedSelectionChange"
          >
            <!-- 选择列 -->
            <el-table-column type="selection" width="50" :selectable="row => row.analysis_status !== 'processing'" />
            <el-table-column prop="material_name" label="材料名称" min-width="150">
              <template #default="{ row }">
                <div class="material-name">{{ row.material_name }}</div>
              </template>
            </el-table-column>
            <el-table-column prop="specification" label="规格型号" min-width="120">
              <template #default="{ row }">
                <span class="material-spec">{{ row.specification || '无规格' }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="unit" label="单位" width="80" />
            <el-table-column prop="quantity" label="数量" width="100">
              <template #default="{ row }">
                {{ formatDecimal(row.quantity) }}
              </template>
            </el-table-column>
            <el-table-column prop="project_unit_price" label="报审单价" width="120">
              <template #default="{ row }">
                <span class="price-value">¥{{ formatDecimal(row.project_unit_price) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="基期信息价" width="140">
              <template #default="{ row }">
                <span class="price-value">¥{{ formatDecimal(getConvertedOriginalBasePrice(row), 4) }}</span>
                <span class="unit-hint">/{{ row.unit }}</span>
              </template>
            </el-table-column>
            <el-table-column label="价格差异" width="120">
              <template #default="{ row }">
                <span :class="{'price-increase': getPricedPriceDifference(row) > 0, 'price-decrease': getPricedPriceDifference(row) < 0}">
                  {{ getPricedPriceDifference(row) > 0 ? '+' : '' }}¥{{ formatDecimal(getPricedPriceDifference(row), 4) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="合同期平均价" width="130">
              <template #default="{ row }">
                <span class="price-value">¥{{ formatDecimal(getPricedContractAvgPrice(row), 4) }}</span>
                <span class="unit-hint">/{{ row.unit }}</span>
              </template>
            </el-table-column>
            <el-table-column label="风险幅度" width="100">
              <template #default="{ row }">
                <span :class="{'price-increase': getPricedRiskRate(row) > 0, 'price-decrease': getPricedRiskRate(row) < 0}">
                  {{ getPricedRiskRate(row) > 0 ? '+' : '' }}{{ (getPricedRiskRate(row) * 100).toFixed(2) }}%
                </span>
              </template>
            </el-table-column>
            <el-table-column label="调差" width="160">
              <template #default="{ row }">
                <span :class="{'price-increase': getPricedPriceAdjustment(row) > 0, 'price-decrease': getPricedPriceAdjustment(row) < 0}">
                  {{ getPricedPriceAdjustment(row) > 0 ? '+' : '' }}¥{{ formatNumber(getPricedPriceAdjustment(row)) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="difference_level" label="风险等级" width="100">
              <template #default="{ row }">
                <el-tag :type="getDifferenceLevelType(row.difference_level)" size="small">
                  {{ getDifferenceLevelText(row.difference_level) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="source_type" label="数据来源" width="120">
              <template #default="{ row }">
                <span class="source-type">{{ row.source_type }}</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button
                  type="primary"
                  link
                  size="small"
                  :icon="View"
                  @click="viewPricedDetail(row)"
                >
                  详情
                </el-button>
                <el-button
                  type="success"
                  link
                  size="small"
                  :icon="TrendCharts"
                  @click="reanalyzePriced(row)"
                >
                  重新分析
                </el-button>
                <el-button
                  type="danger"
                  link
                  size="small"
                  :icon="Delete"
                  @click="deletePricedAnalysis(row)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 市场信息价材料分析结果分页 -->
        <div class="pagination-wrapper">
          <BasePagination
            v-model:current-page="pricedPagination.page"
            v-model:page-size="pricedPagination.size"
            :total="pricedPagination.total"
            @size-change="handlePricedSizeChange"
            @current-change="handlePricedPageChange"
          />
        </div>
      </div>
      
      <!-- 空状态 -->
      <el-empty 
        v-if="(activeAnalysisType === 'unpriced' && analysisResults.length === 0) || (activeAnalysisType === 'priced' && pricedAnalysisResults.length === 0)" 
        :description="getEmptyStateDescription()"
        :image-size="120"
      >
        <template #image>
          <el-icon size="120" style="color: #dcdfe6;">
            <TrendCharts v-if="activeAnalysisType === 'unpriced'" />
            <DataAnalysis v-else-if="activeAnalysisType === 'priced'" />
          </el-icon>
        </template>
        
        <div class="empty-actions">
          <el-button 
            v-if="activeAnalysisType === 'unpriced'" 
            type="primary" 
            size="large"
            :icon="TrendCharts"
            @click="startUnpricedAnalysis"
          >
            开始AI价格分析
          </el-button>
          <el-button 
            v-else-if="activeAnalysisType === 'priced'" 
            type="primary" 
            size="large"
            :icon="DataAnalysis"
            @click="startPricedAnalysis"
          >
            开始市场信息价分析
          </el-button>
          
          <div class="empty-tips" style="margin-top: 16px; color: #909399; font-size: 14px;">
            <p v-if="activeAnalysisType === 'unpriced'">
              AI将分析项目中无信息价材料的市场价格，对比项目价格并评估合理性
            </p>
            <p v-else-if="activeAnalysisType === 'priced'">
              分析项目材料与政府市场信息价的差异，识别价格异常的材料
            </p>
          </div>
        </div>
      </el-empty>
    </el-card>

    <!-- 分析详情对话框 - 简化测试版本 -->
    <el-dialog
      v-model="showTestDialog"
      title="测试对话框"
      width="600px"
    >
      <div>
        <p>测试内容 - 如果你看到这个对话框，说明基本功能正常</p>
        <p>showTestDialog的值: {{ showTestDialog }}</p>
        <p>currentResult: {{ currentResult?.material_name }}</p>
      </div>
    </el-dialog>
    
    <!-- 完整的分析详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      :title="`${currentResult?.material_name} - 分析详情`"
      width="95%"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <div v-if="currentResult" class="detail-content">
        <!-- 基本信息 -->
        <div class="detail-section">
          <h4>材料信息</h4>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="材料名称">{{ currentResult.material_name }}</el-descriptions-item>
            <el-descriptions-item label="规格型号">{{ currentResult.specification || '无' }}</el-descriptions-item>
            <el-descriptions-item label="单位">{{ currentResult.unit }}</el-descriptions-item>
            <el-descriptions-item label="报审单价">¥{{ formatNumber(currentResult.project_price) }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- AI分析结果 -->
        <div v-if="currentResult.analysis_status === 'completed'" class="detail-section">
          <h4>AI分析结果</h4>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="预测价格区间">
              ¥{{ formatNumber(currentResult.predicted_price_min) }} ~ 
              ¥{{ formatNumber(currentResult.predicted_price_max) }}
            </el-descriptions-item>
            <!-- 删除加权平均价显示 -->
            <!-- <el-descriptions-item label="加权平均价">
              ¥{{ formatNumber(currentResult.predicted_price_avg) }}
            </el-descriptions-item> -->
            <el-descriptions-item label="偏差率">
              <span :class="getDeviationClass(currentResult.deviation)">
                {{ currentResult.deviation >= 0 ? '+' : '' }}{{ Math.round(currentResult.deviation) }}%
              </span>
            </el-descriptions-item>
            <el-descriptions-item label="置信度">{{ currentResult.confidence }}%</el-descriptions-item>
            <el-descriptions-item label="风险等级">
              <el-tag :type="getRiskType(currentResult.risk_level)" size="small">
                {{ getRiskText(currentResult.risk_level) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="数据来源" :span="2">
              <div v-if="currentDataSourceRows.length > 0" class="data-source-table-wrapper">
                <el-table
                  :data="currentDataSourceRows"
                  border
                  size="small"
                  class="data-source-table"
                >
                  <el-table-column prop="source_type" label="来源类型" min-width="120" />
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
                  <el-table-column label="可靠性评级" min-width="160" align="center">
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
                <p class="data-source-note">{{ currentDataSourceNote }}</p>
              </div>
              <span v-else>原始数据源：{{ currentResult.data_sources || currentResult.analysis_reasoning || '暂无数据' }}</span>
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 风险因素 -->
        <div v-if="currentResult.risk_factors?.length > 0" class="detail-section">
          <h4>风险因素</h4>
          <ul class="risk-factors-list">
            <li v-for="factor in currentResult.risk_factors" :key="factor" class="risk-factor">
              <el-icon class="risk-icon"><Warning /></el-icon>
              {{ factor }}
            </li>
          </ul>
        </div>

        <!-- AI分析说明 -->
        <div v-if="currentResult.ai_explanation" class="detail-section">
          <h4>AI分析说明</h4>
          <div class="ai-explanation">
            {{ currentResult.ai_explanation }}
          </div>
        </div>

        <!-- AI调用详情 -->
        <div v-if="materialAnalysisDetail && (materialAnalysisDetail.analysis_prompt || materialAnalysisDetail.api_response)" class="detail-section">
          <h4>AI调用详情</h4>
          
          <!-- AI提示词 -->
          <div v-if="materialAnalysisDetail.analysis_prompt" class="ai-detail-item">
            <h5 class="ai-detail-title">
              <el-icon><ChatDotRound /></el-icon>
              提示词 (Prompt)
            </h5>
            <div class="ai-prompt-content">
              <pre>{{ materialAnalysisDetail.analysis_prompt }}</pre>
            </div>
          </div>

          <!-- AI回复内容 -->
          <div v-if="materialAnalysisDetail.api_response" class="ai-detail-item">
            <h5 class="ai-detail-title">
              <el-icon><ChatDotRound /></el-icon>
              AI回复内容
            </h5>
            <div class="ai-response-content">
              <el-tabs v-model="activeResponseTab" type="card">
                <!-- 格式化显示 -->
                <el-tab-pane label="格式化显示" name="formatted">
                  <div class="response-formatted">
                    <template v-if="typeof materialAnalysisDetail.api_response === 'object'">
                      <div v-for="(value, key) in materialAnalysisDetail.api_response" :key="key" class="response-item">
                        <strong>{{ key }}:</strong>
                        <template v-if="typeof value === 'object'">
                          <pre>{{ JSON.stringify(value, null, 2) }}</pre>
                        </template>
                        <template v-else>
                          <span>{{ value }}</span>
                        </template>
                      </div>
                    </template>
                    <template v-else>
                      <pre>{{ materialAnalysisDetail.api_response }}</pre>
                    </template>
                  </div>
                </el-tab-pane>
                
                <!-- 原始JSON -->
                <el-tab-pane label="原始JSON" name="raw">
                  <div class="response-raw">
                    <pre>{{ JSON.stringify(materialAnalysisDetail.api_response, null, 2) }}</pre>
                  </div>
                </el-tab-pane>
              </el-tabs>
            </div>
          </div>

          <!-- AI模型信息 -->
          <div v-if="materialAnalysisDetail.analysis_model" class="ai-model-info">
            <el-tag type="info" size="small">
              <el-icon><Setting /></el-icon>
              使用模型: {{ materialAnalysisDetail.analysis_model }}
            </el-tag>
            <el-tag v-if="materialAnalysisDetail.analysis_cost" type="warning" size="small">
              分析成本: ¥{{ materialAnalysisDetail.analysis_cost }}
            </el-tag>
            <el-tag v-if="materialAnalysisDetail.analysis_time" type="success" size="small">
              耗时: {{ materialAnalysisDetail.analysis_time }}秒
            </el-tag>
          </div>
        </div>

        <!-- 分析历史 -->
        <div class="detail-section">
          <h4>分析历史</h4>
          <el-timeline>
            <el-timeline-item
              v-for="history in analysisHistory"
              :key="history.id"
              :timestamp="formatDateTime(history.created_at)"
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
                <div class="history-user">操作人: {{ history.created_by_name }}</div>
              </div>
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
    </el-dialog>

    <!-- 调整结果对话框 -->
    <el-dialog
      v-model="showAdjustDialog"
      title="调整分析结果"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="adjustFormRef"
        :model="adjustForm"
        :rules="adjustRules"
        label-width="100px"
      >
        <el-form-item label="风险等级" prop="risk_level">
          <el-select v-model="adjustForm.risk_level" style="width: 100%">
            <el-option label="正常" value="normal" />
            <el-option label="低风险" value="low" />
            <el-option label="中风险" value="medium" />
            <el-option label="高风险" value="high" />
            <el-option label="严重风险" value="critical" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="调整原因" prop="adjustment_reason">
          <el-input
            v-model="adjustForm.adjustment_reason"
            type="textarea"
            :rows="4"
            placeholder="请说明调整的原因"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showAdjustDialog = false">取消</el-button>
        <el-button
          type="primary"
          :loading="adjusting"
          @click="handleAdjustSubmit"
        >
          确定调整
        </el-button>
      </template>
    </el-dialog>

    <!-- 材料分析详情对话框 -->
    <MaterialAnalysisDetailDialog
      v-model="showAnalysisDetailDialog"
      :material-id="selectedMaterialId"
    />

    <!-- AI模型选择对话框 -->
    <el-dialog
      v-model="showModelSelectDialog"
      title="选择AI分析模型"
      width="480px"
      :close-on-click-modal="false"
      center
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
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick, watch } from 'vue'
import BasePagination from '@/components/BasePagination.vue'
import MaterialAnalysisDetailDialog from '@/components/analysis/MaterialAnalysisDetailDialog.vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  TrendCharts,
  Document,
  Box,
  CircleCheck,
  SuccessFilled,
  Warning,
  Refresh,
  View,
  Edit,
  ChatDotRound,
  Setting,
  DataAnalysis,
  Delete,
  Link,
  Promotion,
  MagicStick
} from '@element-plus/icons-vue'
import { formatDate, formatNumber, formatDateTime } from '@/utils'
import { formatAnalysisDataSources, getDataSourceNote } from '@/utils/dataSourceUtils'
import { useSelectionAcrossPages } from '@/composables/useSelectionAcrossPages'
import { getProjectAnalysisResults, getProjectPricedMaterialsAnalysis, batchAnalyzeMaterials, analyzePricedMaterials, getProjectAnalysisStatistics, deleteMaterialAnalysis, getMaterialAnalysisDetail } from '@/api/analysis'
import { deleteProjectMaterial, batchDeleteProjectMaterials, getProjectMaterials } from '@/api/projects'
import { useAnalysisStore } from '@/store/analysis'

// 格式化数字，去除末尾的0，不使用千分位逗号
const formatDecimal = (num, decimals = 4) => {
  if (typeof num !== 'number') return num
  const res = num.toFixed(decimals)
  if (res.includes('.')) {
    return res.replace(/\.?0+$/, '')
  }
  return res
}

const router = useRouter()
const route = useRoute()

// 响应式数据
const loading = ref(false)
const adjusting = ref(false)
const showDetailDialog = ref(false)
const showTestDialog = ref(false)
const showAdjustDialog = ref(false)
const showAnalysisDetailDialog = ref(false)
const selectedMaterialId = ref(null)

// AI模型选择相关
const showModelSelectDialog = ref(false)
const selectedAIModel = ref('dashscope') // 默认使用通义千问
const pendingAnalysisAction = ref('') // 'startAnalysis' 或 'batchReanalyze'

// 缓存加载状态，避免切换频繁重新请求导致闪烁
const hasLoadedUnpriced = ref(false)
const hasLoadedPriced = ref(false)

const currentProject = ref(null)
const filterStatus = ref('')
const filterRisk = ref('')
const searchKeyword = ref('')
const allUnpricedAnalysisResults = ref([])
const analysisResults = ref([])
const selectedResults = ref([])
const tableRef = ref()
const {
  allSelected,
  selectedIds: selectedResultIds,
  clearAll: clearAllSelection,
  handleSelectionChange,
  syncSelectionOnPage,
  createSelectedCount
} = useSelectionAcrossPages('id')
const currentResult = ref(null)
const analysisHistory = ref([])
const materialAnalysisDetail = ref(null)
const activeResponseTab = ref('formatted')

// 将分析结果ID映射到项目材料ID，方便批量操作时快速定位材料
const analysisIdToMaterialIdMap = computed(() => {
  const map = new Map()
  allUnpricedAnalysisResults.value.forEach(item => {
    if (item?.id && item?.material_id) {
      map.set(item.id, item.material_id)
    }
  })
  return map
})

// 根据当前选择状态（单选/多选/全选）获取对应的项目材料ID列表
const getSelectedMaterialIds = async () => {
  if (allSelected.value) {
    const ids = allUnpricedAnalysisResults.value
      .map(item => item.material_id)
      .filter(id => Boolean(id))
    return Array.from(new Set(ids))
  }

  const ids = Array.from(selectedResultIds.value)
    .map(id => analysisIdToMaterialIdMap.value.get(id))
    .filter(id => Boolean(id))

  return Array.from(new Set(ids))
}

const buildDataSourceContext = (...candidates) => {
  const normalizeCandidate = (candidate) => {
    if (!candidate) {
      return null
    }

    const analysisReasoning = candidate.analysis_reasoning ||
      candidate.ai_explanation ||
      candidate.reasoning ||
      candidate.explanation ||
      candidate.raw_response?.content ||
      candidate.api_response?.content || ''

    return {
      data_sources: candidate.data_sources ?? candidate.reference_prices ?? null,
      analysis_reasoning: analysisReasoning,
      data_source_note: candidate.data_source_note ?? candidate.data_sources_note ?? ''
    }
  }

  for (const candidate of candidates) {
    const context = normalizeCandidate(candidate)
    if (!context) {
      continue
    }

    const hasSources = Array.isArray(context.data_sources)
      ? context.data_sources.length > 0
      : Boolean(context.data_sources && String(context.data_sources).trim())

    if (hasSources || context.analysis_reasoning) {
      return context
    }
  }

  const fallback = normalizeCandidate(candidates.find(Boolean))
  return fallback
}

const currentDataSourceContext = computed(() =>
  buildDataSourceContext(
    materialAnalysisDetail.value?.analysis_result,
    materialAnalysisDetail.value,
    currentResult.value
  )
)

const currentDataSourceRows = computed(() =>
  formatAnalysisDataSources(currentDataSourceContext.value)
)

const currentDataSourceNote = computed(() =>
  getDataSourceNote(currentDataSourceContext.value)
)

// 分析类型切换状态
const activeAnalysisType = ref('unpriced') // 'unpriced' 或 'priced'
const pricedAnalysisResults = ref([]) // 市场信息价材料分析结果

// 市场信息价材料分析结果选择状态管理
const selectedPricedResults = ref([])
const selectedPricedCount = ref(0)
const allPricedSelected = ref(false)
const pricedTableRef = ref(null)

// 市场信息价材料分析结果分页状态
const pricedPagination = reactive({
  page: 1,
  size: 100
})

const analysisStore = useAnalysisStore()
const projectId = route.query.project_id

// 映射 Store 中的任务状态到本地 analysisState
const currentTask = computed(() => analysisStore.getTaskByProjectId(projectId))

const analysisState = computed(() => {
  const task = currentTask.value
  if (task && task.status === 'running') {
    return {
      isAnalyzing: true,
      analysisType: task.type,
      progress: task.progress,
      currentStep: task.currentStep,
      totalSteps: task.totalSteps,
      completedSteps: task.completedSteps
    }
  }
  return {
    isAnalyzing: false,
    analysisType: '',
    progress: 0,
    currentStep: '',
    totalSteps: 0,
    completedSteps: 0
  }
})

// 监听任务完成，刷新数据
watch(() => currentTask.value?.status, async (newStatus, oldStatus) => {
  if (newStatus === 'completed' && oldStatus === 'running') {
    // 任务完成，刷新数据
    if (currentTask.value.type === 'unpriced') {
      activeAnalysisType.value = 'unpriced'
      await fetchAnalysisResults()
    } else if (currentTask.value.type === 'priced') {
      activeAnalysisType.value = 'priced'
      await fetchPricedAnalysisResults()
    }
  }
})

// 统计数据
const analysisStats = reactive({
  totalMaterials: 0,
  analyzedMaterials: 0,
  reasonableMaterials: 0,
  riskMaterials: 0
})

// 分页数据
const pagination = reactive({
  page: 1,
  size: 1000,
  total: 0
})

const selectedCount = createSelectedCount(() => pagination.total)

// 调整表单
const adjustForm = reactive({
  risk_level: '',
  adjustment_reason: ''
})

const adjustRules = {
  risk_level: [
    { required: true, message: '请选择风险等级', trigger: 'change' }
  ],
  adjustment_reason: [
    { required: true, message: '请说明调整原因', trigger: 'blur' },
    { min: 10, message: '调整原因不能少于10个字符', trigger: 'blur' }
  ]
}

const isGuidedPriceAnalysis = (item) => item?.analysis_model === 'guided_price_comparison'

const applyAnalysisPagination = () => {
  const total = allUnpricedAnalysisResults.value.length
  
  // 强制显示所有数据，取消分页限制
  pagination.total = total
  // 设置页码为1
  pagination.page = 1
  // 将每页大小设置为总数，确保BasePagination组件知道我们在显示所有数据
  // 即使BasePagination没有直接使用这个值来切片，保持状态一致也是好的
  if (total > 0) {
    pagination.size = total
  }

  // 直接显示所有数据，不再进行slice操作
  analysisResults.value = allUnpricedAnalysisResults.value
}

// 获取分析结果
const fetchAnalysisResults = async () => {
  if (!route.query.project_id) {
    ElMessage.error('缺少项目ID参数')
    router.push('/analysis/results')
    return
  }
  
  loading.value = true
  try {
    const projectId = route.query.project_id
    const baseParams = {
      status: filterStatus.value || undefined,
      risk_level: filterRisk.value || undefined,
      material_name: searchKeyword.value || undefined
    }

    // 1. 获取所有分析结果 (PriceAnalysis)
    const chunkSize = Math.max(pagination.size, 1000)
    const analysisRecords = []
    let offset = 0

    while (true) {
      const response = await getProjectAnalysisResults(projectId, {
        ...baseParams,
        skip: offset,
        limit: chunkSize
      }, { __skipLoading: true })

      const items = response?.results || []
      if (!items.length) break
      analysisRecords.push(...items)
      if (items.length < chunkSize) break
      offset += items.length
    }

    // 2. 获取所有无信息价材料 (ProjectMaterial where is_matched=False)
    // 只有当没有设置特定的分析结果筛选条件时，才去获取所有材料并合并
    let finalResults = []
    const shouldFetchAllMaterials = !filterStatus.value && !filterRisk.value

    if (shouldFetchAllMaterials) {
      const unpricedMaterials = []
      const materialChunkSize = 1000
      let page = 1
      
      while (true) {
        const res = await getProjectMaterials(projectId, {
          page, 
          size: materialChunkSize, 
          is_matched: false, // Unpriced only
          keyword: searchKeyword.value || undefined
        }, { __skipLoading: true })
        
        const items = res.items || []
        if (!items.length) break
        unpricedMaterials.push(...items)
        if (items.length < materialChunkSize) break
        page++
      }

      // 创建分析结果映射
      const analysisMap = new Map()
      analysisRecords.forEach(record => {
        if (record.material_id) {
          analysisMap.set(record.material_id, record)
        }
      })

      // 遍历所有材料，优先使用分析结果，否则构造占位符
      unpricedMaterials.forEach(material => {
        const analysis = analysisMap.get(material.id)
        if (analysis) {
          finalResults.push(analysis)
        } else {
          // 构造占位符
          finalResults.push({
            id: `temp_${material.id}`, // 临时ID
            material_id: material.id,
            material_name: material.material_name,
            specification: material.specification,
            unit: material.unit,
            quantity: material.quantity,
            project_price: material.unit_price, // 原单价
            total_price: (material.quantity || 0) * (material.unit_price || 0),
            status: 'pending', // 默认状态
            analysis_model: 'ai_analysis', // 假设
            risk_level: 'unknown',
            price_variance: null,
            ai_price: null,
            is_reasonable: null,
            created_at: material.created_at
          })
        }
      })
    } else {
      // 如果有筛选条件，直接使用分析结果
      finalResults = analysisRecords
    }

    const inferRiskLevel = (variance, isReasonable) => {
      const numericVariance =
        typeof variance === 'number'
          ? variance
          : typeof variance === 'string'
            ? Number.parseFloat(variance)
            : null

      if (Number.isFinite(numericVariance)) {
        const v = Math.abs(numericVariance)
        if (v === 0) return 'normal'
        if (v <= 15) return 'low'
        if (v <= 30) return 'medium'
        return 'high'
      }
      if (isReasonable === false) return 'high'
      return 'normal'
    }

    const computeSignedDeviation = (item) => {
      const rawVariance = Number(item.price_variance)
      if (!Number.isFinite(rawVariance)) {
        return null
      }

      if (rawVariance < 0) {
        return rawVariance
      }

      const projectPrice = Number(item.project_price)
      const minPrice = item.predicted_price_min !== null && item.predicted_price_min !== undefined
        ? Number(item.predicted_price_min)
        : null
      const maxPrice = item.predicted_price_max !== null && item.predicted_price_max !== undefined
        ? Number(item.predicted_price_max)
        : null

      if (Number.isFinite(projectPrice)) {
        if (Number.isFinite(minPrice) && projectPrice < minPrice) {
          return -Math.abs(rawVariance)
        }
        if (Number.isFinite(maxPrice) && projectPrice > maxPrice) {
          return Math.abs(rawVariance)
        }
      }

      return rawVariance
    }

    const filteredRaw = finalResults.filter(item => !isGuidedPriceAnalysis(item))

    allUnpricedAnalysisResults.value = filteredRaw.map(item => ({
      id: item.id,
      material_id: item.material_id,
      material_name: item.material_name || `材料${item.material_id}`,
      specification: item.specification || '',
      unit: item.unit || '',
      quantity: Number(item.quantity),
      project_price: item.project_price, // Ensure project_price is passed
      originalPrice: Number(item.project_price),
      originalTotalPrice: Number(item.total_price || (Number(item.project_price || 0) * Number(item.quantity || 0))),
      aiPrice: item.ai_price !== null ? Number(item.ai_price) : null,
      predicted_price_min: item.predicted_price_min, // Pass predicted prices
      predicted_price_max: item.predicted_price_max,
      predicted_price_avg: item.predicted_price_avg,
      deviation: computeSignedDeviation(item), // 使用带符号的偏差
      confidence: Math.round((item.confidence_score || 0) * 100),
      // 优先使用后端返回的风险等级，如果没有则推断
      level: item.risk_level || inferRiskLevel(item.price_variance, item.is_reasonable),
      risk_level: item.risk_level || inferRiskLevel(item.price_variance, item.is_reasonable),
      analysis_status: item.status || 'pending',
      analyzed_at: item.analyzed_at,
      data_sources: Array.isArray(item.data_sources) ? item.data_sources.map(ds => ds.source).join(', ') : (item.data_sources || ''),
      risk_factors: item.risk_factors ? (Array.isArray(item.risk_factors) ? item.risk_factors : item.risk_factors.split('; ')) : [],
      ai_explanation: item.analysis_reasoning || '',
      reasoning: item.analysis_reasoning, // Compatible with both
      isReasonable: item.is_reasonable,
      status: item.status || 'pending',
      analysis_model: item.analysis_model,
      price_range: item.predicted_price_min && item.predicted_price_max
        ? `${formatNumber(item.predicted_price_min)} - ${formatNumber(item.predicted_price_max)}`
        : '-',
      data_source_note: item.data_source_note,
      features: item.features,
      implementation_standards: item.implementation_standards,
      technical_requirements: item.technical_requirements,
      brand_requirements: item.brand_requirements
    }))

    pagination.total = allUnpricedAnalysisResults.value.length
    applyAnalysisPagination()

    await nextTick()
    syncSelectionOnPage(tableRef, analysisResults.value)

    try {
      const stats = await getProjectAnalysisStatistics(route.query.project_id, { __skipLoading: true })
      Object.assign(analysisStats, {
        totalMaterials: stats.total_materials ?? analysisStats.totalMaterials,
        analyzedMaterials: stats.analyzed_materials ?? analysisStats.analyzedMaterials,
        reasonableMaterials: stats.reasonable_materials ?? analysisStats.reasonableMaterials,
        riskMaterials: stats.unreasonable_materials ?? analysisStats.riskMaterials
      })

    } catch (e) {
      // 回退：使用当前缓存结果估算
      const results = allUnpricedAnalysisResults.value
      const totalMaterials = results.length
      const analyzedMaterials = results.filter(r => r.analysis_status === 'completed').length
      const reasonableMaterials = results.filter(r => r.risk_level === 'normal').length
      const riskMaterials = results.filter(r => r.risk_level && r.risk_level !== 'normal').length
      Object.assign(analysisStats, {
        totalMaterials,
        analyzedMaterials,
        reasonableMaterials,
        riskMaterials
      })
    }

  } catch (error) {
    console.error('获取分析结果失败:', error)
    ElMessage.error('获取分析结果失败')
  } finally {
    loading.value = false
    hasLoadedUnpriced.value = true
  }
}

// 状态相关方法
const getStatusType = (status) => {
  const typeMap = {
    'completed': 'success',
    'processing': 'warning',
    'pending': 'info',
    'failed': 'danger'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    'completed': '已完成',
    'processing': '分析中',
    'pending': '待分析',
    'failed': '失败'
  }
  return textMap[status] || status
}

const getRiskType = (risk) => {
  const typeMap = {
    'normal': 'success',
    'low': 'warning',
    'medium': 'warning',
    'high': 'danger',
    'critical': 'danger'
  }
  return typeMap[risk] || 'info'
}

const getRiskText = (risk) => {
  const textMap = {
    'normal': '正常',
    'low': '低风险',
    'medium': '中风险',
    'high': '高风险',
    'critical': '严重风险'
  }
  return textMap[risk] || risk
}

const getDeviationClass = (deviation) => {
  const v = Math.abs(deviation)
  if (v === 0) return 'deviation-normal'
  if (v <= 15) return 'deviation-warning'
  if (v <= 30) return 'deviation-warning'
  return 'deviation-danger'
}

const getConfidenceColor = (confidence) => {
  if (confidence >= 80) return '#67c23a'
  if (confidence >= 60) return '#e6a23c'
  return '#f56c6c'
}


// 获取空状态描述
const getEmptyStateDescription = () => {
  if (activeAnalysisType.value === 'unpriced') {
    return '尚未进行无信息价材料AI价格分析'
  } else if (activeAnalysisType.value === 'priced') {
    return '尚未进行市场信息价材料差异分析'
  }
  return '暂无分析数据'
}

// 事件处理
const handleFilterChange = () => {
  if (activeAnalysisType.value === 'priced') {
    pricedPagination.page = 1
    fetchPricedAnalysisResults()
  } else {
    pagination.page = 1
    fetchAnalysisResults()
  }
}

// 市场信息价材料分析结果选择处理
const handlePricedSelectionChange = (selection) => {
  selectedPricedResults.value = selection
  selectedPricedCount.value = selection.length
}

const selectAllPriced = () => {
  if (pricedTableRef.value) {
    pricedAnalysisResults.value.forEach(row => {
      pricedTableRef.value.toggleRowSelection(row, true)
    })
  }
  allPricedSelected.value = true
}

const clearPricedSelection = () => {
  if (pricedTableRef.value) {
    pricedTableRef.value.clearSelection()
  }
  selectedPricedResults.value = []
  selectedPricedCount.value = 0
  allPricedSelected.value = false
}

const handleSizeChange = (size) => {
  pagination.size = size
  pagination.page = 1
  fetchAnalysisResults()
}

const handlePageChange = (page) => {
  pagination.page = page
  applyAnalysisPagination()
  nextTick().then(() => {
    syncSelectionOnPage(tableRef, analysisResults.value)
  })
}

// 市场信息价材料分析结果分页处理函数
const handlePricedSizeChange = (size) => {
  pricedPagination.size = size
  pricedPagination.page = 1
  fetchPricedAnalysisResults()
}

const handlePricedPageChange = (page) => {
  pricedPagination.page = page
  fetchPricedAnalysisResults()
}

const onSelectionChange = (selection) => {
  handleSelectionChange(selection, analysisResults.value)
  selectedResults.value = selection
}

// 操作方法 - 无信息价材料分析
const startUnpricedAnalysis = async () => {
  // 显示模型选择对话框
  pendingAnalysisAction.value = 'startAnalysis'
  showModelSelectDialog.value = true
}

// 模型选择确认处理
const handleModelSelectConfirm = () => {
  showModelSelectDialog.value = false
  if (pendingAnalysisAction.value === 'startAnalysis') {
    confirmStartAnalysis()
  } else if (pendingAnalysisAction.value === 'batchReanalyze') {
    confirmBatchReanalyze()
  }
}

// 确认开始分析（模型选择后）
const confirmStartAnalysis = async () => {
  let modelName = '通义千问'
  if (selectedAIModel.value === 'doubao') {
    modelName = '豆包'
  } else if (selectedAIModel.value === 'deepseek') {
    modelName = 'DeepSeek'
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要使用 ${modelName} 对该项目进行AI价格分析吗？系统将分析所有无信息价材料的市场价格。此操作将在后台进行，您可以继续其他操作。`,
      'AI价格分析确认',
      {
        confirmButtonText: '开始后台分析',
        cancelButtonText: '取消',
        type: 'info'
      }
    )
    
    // 调用 Store Action 启动后台分析
    // 不使用 await，让其在后台运行
    analysisStore.startUnpricedAnalysis(
      route.query.project_id,
      modelName,
      selectedAIModel.value
    )
    
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('启动分析失败')
    }
  }
}

// 市场信息价材料分析
const startPricedAnalysis = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要对该项目进行市场信息价材料价格分析吗？系统将分析项目材料与政府市场信息价的差异情况。此操作将在后台进行。',
      '市场信息价分析确认',
      {
        confirmButtonText: '开始后台分析',
        cancelButtonText: '取消',
        type: 'info'
      }
    )
    
    // 调用 Store Action 启动后台分析
    analysisStore.startPricedAnalysis(route.query.project_id)
    
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('启动市场信息价分析失败')
    }
  }
}

const generateReport = () => {
  router.push(`/reports/generate?project_id=${route.query.project_id}&type=analysis`)
}

// 切换分析类型
const switchAnalysisType = async (type) => {
  console.log('切换分析类型到:', type)
  if (activeAnalysisType.value === type) return
  
  // 清空两种分析类型的选择状态
  selectedResults.value = []
  clearPricedSelection()
  
  activeAnalysisType.value = type
  
  if (type === 'priced') {
    if (!hasLoadedPriced.value) {
      await fetchPricedAnalysisResults()
    }
  } else {
    if (!hasLoadedUnpriced.value) {
      await fetchAnalysisResults()
    }
  }
}

// 获取市场信息价材料分析结果
const fetchPricedAnalysisResults = async (silent = false) => {
  if (!route.query.project_id) {
    console.warn('没有项目ID，无法获取市场信息价材料分析结果')
    return
  }

  if (!silent) loading.value = true
  try {
    console.log('开始获取市场信息价材料分析结果，项目ID:', route.query.project_id)
    
    // 调用真实的API获取市场信息价材料分析结果
    const response = await getProjectPricedMaterialsAnalysis(route.query.project_id, {
      skip: (pricedPagination.page - 1) * pricedPagination.size,
      limit: pricedPagination.size,
      status: filterStatus.value || undefined,
      risk_level: filterRisk.value || undefined,
      material_name: searchKeyword.value || undefined
    }, { __skipLoading: true })
    
    console.log('市场信息价材料分析API响应:', response)
    
    if (response && response.results) {
      // 设置分页总数
      if (response.total !== undefined) {
        pricedPagination.total = response.total
      }
      
      // 转换API数据格式为前端需要的格式
      pricedAnalysisResults.value = response.results.map(item => ({
        id: item.id,
        material_id: item.material_id,
        material_name: item.material_name || '未知材料',
        specification: item.specification || '',
        unit: item.unit || '',
        quantity: parseFloat(item.quantity || 0),
        project_unit_price: parseFloat(item.project_unit_price || 0),
        base_unit_price: parseFloat(item.base_unit_price || 0), // 合同期平均价
        original_base_price: parseFloat(item.original_base_price || item.base_unit_price || 0), // 原始基期信息价
        base_unit: item.base_unit || item.unit || '', // 基期材料单位，用于单位转换
        unit_price_difference: parseFloat(item.unit_price_difference || 0),
        total_price_difference: parseFloat(item.total_price_difference || 0),
        price_difference_rate: parseFloat(item.price_difference_rate || 0),
        has_difference: Boolean(item.has_difference),
        difference_level: item.difference_level || 'normal',
        base_material_name: item.base_material_name || '',
        base_specification: item.base_specification || '',
        region: item.region || '',
        source_type: item.source_type || '政府市场信息价'
      }))
    } else {
      // 如果API没有返回数据，设置为空数组
      console.warn('API返回数据为空，没有市场信息价材料分析结果')
      pricedAnalysisResults.value = []
      pricedPagination.total = 0
    }
    
    console.log('市场信息价材料分析结果获取成功:', pricedAnalysisResults.value.length, '条数据')
    hasLoadedPriced.value = true
    
  } catch (error) {
    console.error('获取市场信息价材料分析结果失败:', error)
    ElMessage.error('获取市场信息价材料分析结果失败: ' + (error.message || '未知错误'))
    
    // API调用失败时，设置为空数组
    pricedAnalysisResults.value = []
    pricedPagination.total = 0
  } finally {
    if (!silent) loading.value = false
  }
}


// 差异等级相关方法
const getDifferenceLevelType = (level) => {
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

const hasHistoryPriceRange = (history) => {
  return history?.predicted_price_min !== null &&
    history?.predicted_price_min !== undefined &&
    history?.predicted_price_max !== null &&
    history?.predicted_price_max !== undefined
}

const getDifferenceLevelText = (level) => {
  const textMap = {
    'normal': '正常',
    'low': '低风险',
    'medium': '中风险',
    'high': '高风险',
    'critical': '严重风险'
  }
  return textMap[level] || '未知'
}

// ==================== 单位转换和价格计算逻辑 ====================

// 单位转换系数表
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
  // 体积单位 -> m³
  'm³': { base: 'm³', factor: 1 },
  'm3': { base: 'm³', factor: 1 },
  'M³': { base: 'm³', factor: 1 },
  'M3': { base: 'm³', factor: 1 },
  '立方米': { base: 'm³', factor: 1 },
  '方': { base: 'm³', factor: 1 },
  'L': { base: 'm³', factor: 0.001 },
  'l': { base: 'm³', factor: 0.001 },
  '升': { base: 'm³', factor: 0.001 }
}

// 获取单位转换信息
const getUnitInfo = (unit) => {
  if (!unit) return null
  const trimmedUnit = unit.trim()
  return unitConversionTable[trimmedUnit] || null
}

// 计算两个单位之间的转换系数
const getUnitConversionFactor = (fromUnit, toUnit) => {
  const fromInfo = getUnitInfo(fromUnit)
  const toInfo = getUnitInfo(toUnit)
  if (!fromInfo || !toInfo) return 1
  if (fromInfo.base !== toInfo.base) return 1
  return fromInfo.factor / toInfo.factor
}

// 获取行的单位转换系数
const getRowConversionFactor = (row) => {
  const projectUnit = row.unit
  const baseUnit = row.base_unit || row.unit
  return getUnitConversionFactor(baseUnit, projectUnit)
}

// 智能判断价格是否需要转换
// 如果价格接近项目单价（在50%以内），说明已按项目单位；如果接近大数（基准价），需要转换
const smartConvertPrice = (price, row, conversionFactor) => {
  if (!price || conversionFactor === 1) return price
  
  const projectPrice = row.project_unit_price
  
  // 如果价格接近项目单价（同数量级），说明已经是项目单位，不转换
  if (projectPrice && Math.abs(price - projectPrice) / projectPrice < 0.5) {
    return price
  }
  
  // 如果价格比项目单价大很多倍（超过10倍），说明是原始单位，需要转换
  if (projectPrice && price / projectPrice > 10) {
    return price / conversionFactor
  }
  
  // 默认不转换（假设已经是项目单位）
  return price
}

// 获取转换后的基期信息价（原始匹配价格）
const getConvertedOriginalBasePrice = (row) => {
  const conversionFactor = getRowConversionFactor(row)
  // original_base_price 是原始基期信息价，如果没有则使用 base_unit_price
  const originalPrice = row.original_base_price || row.base_unit_price
  return smartConvertPrice(originalPrice, row, conversionFactor)
}

// 获取转换后的合同期平均价
const getPricedContractAvgPrice = (row) => {
  const conversionFactor = getRowConversionFactor(row)
  // base_unit_price 实际上是合同期平均价（后端命名有点混乱）
  const avgPrice = row.base_unit_price
  return smartConvertPrice(avgPrice, row, conversionFactor)
}

// 价格差异：项目单价 - 转换后的基期信息价
const getPricedPriceDifference = (row) => {
  const convertedOriginalBasePrice = getConvertedOriginalBasePrice(row)
  return row.project_unit_price - convertedOriginalBasePrice
}

// 风险幅度：(合同期平均价 - 基期信息价) / 基期信息价
const getPricedRiskRate = (row) => {
  const convertedOriginalBasePrice = getConvertedOriginalBasePrice(row)
  const contractAvgPrice = getPricedContractAvgPrice(row)
  if (convertedOriginalBasePrice === 0) return 0
  return (contractAvgPrice - convertedOriginalBasePrice) / convertedOriginalBasePrice
}

// 调差：风险幅度在±5%以内则为0，超过部分乘以数量
const getPricedPriceAdjustment = (row) => {
  const riskRate = getPricedRiskRate(row)
  const threshold = 0.05
  
  if (riskRate >= -threshold && riskRate <= threshold) {
    return 0
  }
  
  const convertedOriginalBasePrice = getConvertedOriginalBasePrice(row)
  const contractAvgPrice = getPricedContractAvgPrice(row)
  
  let excessPerUnit = 0
  if (riskRate > threshold) {
    excessPerUnit = contractAvgPrice - convertedOriginalBasePrice * (1 + threshold)
  } else {
    excessPerUnit = contractAvgPrice - convertedOriginalBasePrice * (1 - threshold)
  }
  
  return excessPerUnit * row.quantity
}


const viewDetail = async (row) => {
  console.log('=== viewDetail 方法被调用 ===')
  console.log('参数 row:', row)
  console.log('当前 showDetailDialog 值:', showDetailDialog.value)
  
  try {
    console.log('设置 currentResult...')
    currentResult.value = row
    console.log('设置 showDetailDialog 为 true...')
    showDetailDialog.value = true
    console.log('设置后 showDetailDialog 值:', showDetailDialog.value)
    materialAnalysisDetail.value = null
    
    // 获取详细的分析数据（包含AI提示词、回复和分析历史）
    if (row.material_id) {
      console.log('正在调用API获取材料详情（含历史），material_id:', row.material_id)
      const detailResponse = await getMaterialAnalysisDetail(row.material_id)

      // FastAPI 直接返回的数据结构：{ code, message, data }
      const detailData = detailResponse?.data || detailResponse

      // 兼容旧结构：优先使用 data.analysis_result / data.analysis，其次整体对象
      materialAnalysisDetail.value =
        detailData?.analysis_result ||
        detailData?.analysis ||
        detailData

      console.log('API响应成功，材料分析详情（analysis_result）:', materialAnalysisDetail.value)

      // 从同一响应中提取分析历史
      if (detailData?.analysis_history) {
        analysisHistory.value = detailData.analysis_history.map(hist => ({
          id: hist.id,
          action: hist.action,
          note: hist.note,
          created_at: hist.created_at,
          created_by_name: hist.created_by_name || '系统',
          analysis_model: hist.analysis_model || '',
          predicted_price_min: hist.predicted_price_min,
          predicted_price_max: hist.predicted_price_max
        }))
      } else {
        analysisHistory.value = []
      }
    } else {
      console.warn('row.material_id 为空，无法获取详情')
    }
  } catch (error) {
    console.error('获取材料分析详情失败:', error)
    ElMessage.error('获取分析详情失败: ' + error.message)
  }
}

const reanalyze = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要重新分析材料 "${row.material_name}" 吗？`,
      '重新分析确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    ElMessage.info('重新分析已启动')
    // TODO: 调用重新分析API
    
    // 更新状态为分析中
    row.analysis_status = 'processing'
    
    // 3秒后更新为完成
    setTimeout(() => {
      row.analysis_status = 'completed'
      ElMessage.success('重新分析完成')
    }, 3000)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('重新分析失败')
    }
  }
}

const adjustResult = (row) => {
  currentResult.value = row
  adjustForm.risk_level = row.risk_level
  adjustForm.adjustment_reason = ''
  showAdjustDialog.value = true
}

const handleAdjustSubmit = async () => {
  adjusting.value = true
  try {
    // TODO: 调用调整API
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 更新结果
    currentResult.value.risk_level = adjustForm.risk_level
    
    ElMessage.success('调整成功')
    showAdjustDialog.value = false
    fetchAnalysisResults()
  } catch (error) {
    ElMessage.error('调整失败')
    console.error('调整失败:', error)
  } finally {
    adjusting.value = false
  }
}

const batchReanalyze = async () => {
  if (selectedCount.value === 0) return
  // 显示模型选择对话框
  pendingAnalysisAction.value = 'batchReanalyze'
  showModelSelectDialog.value = true
}

// 确认批量重新分析（模型选择后）
const confirmBatchReanalyze = async () => {
  let modelName = '通义千问'
  if (selectedAIModel.value === 'doubao') {
    modelName = '豆包'
  } else if (selectedAIModel.value === 'deepseek') {
    modelName = 'DeepSeek'
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要使用 ${modelName} 重新分析已选择的 ${selectedCount.value} 个材料吗？此操作将在后台进行。`,
      '批量重新分析确认',
      {
        confirmButtonText: '开始后台分析',
        cancelButtonText: '取消',
        type: 'info'
      }
    )

    const allMaterialIds = await getSelectedMaterialIds()

    if (allMaterialIds.length === 0) {
      ElMessage.warning('没有选中的材料需要重新分析')
      return
    }
    
    console.log('准备批量重新分析，材料IDs:', allMaterialIds, '使用模型:', modelName)
    
    // 调用 Store Action 启动后台分析
    analysisStore.startUnpricedAnalysis(
      route.query.project_id,
      modelName,
      selectedAIModel.value,
      { material_ids: allMaterialIds }
    )
    
    // 清空选择
    clearAllSelection()
    selectedResults.value = []
    
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量重新分析失败')
    }
  }
}

const batchAdjust = () => {
  ElMessage.info('批量调整功能开发中...')
}

// 批量删除分析结果（跨页）
const batchDeleteAnalyses = async () => {
  if (selectedCount.value === 0) return
  try {
    await ElMessageBox.confirm(
      `确定要删除已选择的 ${selectedCount.value} 条分析结果吗？删除后可重新分析生成。`,
      '批量删除确认',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )

    const ids = await getSelectedMaterialIds()
    if (ids.length === 0) {
      ElMessage.warning('没有选中的材料需要删除')
      return
    }
    // 逐个删除
    await Promise.allSettled(ids.map(id => deleteMaterialAnalysis(id)))
    ElMessage.success(`已删除 ${ids.length} 条分析结果`)
    clearAllSelection()
    await fetchAnalysisResults()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

// 生命周期
onMounted(async () => {
  // 根据路由参数决定默认显示的分析类型
  if (route.query.type === 'priced') {
    activeAnalysisType.value = 'priced'
    await fetchPricedAnalysisResults()
  } else {
    activeAnalysisType.value = 'unpriced'
    await fetchAnalysisResults()
    // 背景预取市场信息价分析结果，避免第一次切换时闪烁
    fetchPricedAnalysisResults(true)
  }
  
  // 设置当前项目信息，可以从路由参数或API获取
  if (route.query.project_id) {
    currentProject.value = {
      id: parseInt(route.query.project_id),
      name: route.query.project_name || `项目${route.query.project_id}`
    }
  }
})

// 市场信息价材料分析结果的批量操作方法
const batchReanalyzePriced = async () => {
  if (selectedPricedCount.value === 0) return
  try {
    await ElMessageBox.confirm(
      `确定要重新分析已选择的 ${selectedPricedCount.value} 个市场信息价材料吗？`,
      '批量重新分析确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const materialIds = selectedPricedResults.value
      .filter(row => row.material_id)
      .map(row => row.material_id)
    
    if (materialIds.length === 0) {
      ElMessage.warning('没有选中的材料需要重新分析')
      return
    }
    
    console.log('准备批量重新分析市场信息价材料，材料IDs:', materialIds)
    ElMessage.info(`正在重新分析 ${materialIds.length} 个市场信息价材料...`)
    
    // 调用市场信息价材料分析API
    try {
      const result = await analyzePricedMaterials(route.query.project_id, {
        material_ids: materialIds,
        batch_size: 10
      })
      
      ElMessage.success(`成功重新分析了 ${result.analyzed_count || materialIds.length} 个市场信息价材料`)
      
      // 清空选择
      clearPricedSelection()
      
      // 刷新数据
      await fetchPricedAnalysisResults()
      
    } catch (apiError) {
      console.error('批量重新分析市场信息价材料API调用失败:', apiError)
      ElMessage.error('批量重新分析失败: ' + (apiError.message || apiError.response?.data?.detail || '未知错误'))
    }
    
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量重新分析失败')
    }
  }
}

const batchAdjustPriced = async () => {
  if (selectedPricedCount.value === 0) return
  ElMessage.info('批量调整功能开发中')
}

const batchDeletePricedAnalyses = async () => {
  if (selectedPricedCount.value === 0) return
  try {
    await ElMessageBox.confirm(
      `确定要删除已选择的 ${selectedPricedCount.value} 条市场信息价材料分析结果吗？删除后可重新分析生成。`,
      '批量删除确认',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )

    const ids = selectedPricedResults.value.map(row => row.material_id)
    console.log('准备删除市场信息价材料分析结果，IDs:', ids)
    
    // 调用批量删除项目材料API
    await batchDeleteProjectMaterials(route.query.project_id, ids)
    ElMessage.success(`批量删除完成，删除了${ids.length}条分析结果`)
    
    // 清空选择
    clearPricedSelection()
    
    // 重新获取数据
    await fetchPricedAnalysisResults()
    
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

// 市场信息价材料分析结果的单个操作方法
const viewPricedDetail = async (row) => {
  console.log('查看市场信息价材料详情:', row)
  try {
    selectedMaterialId.value = row.material_id
    showAnalysisDetailDialog.value = true
  } catch (error) {
    console.error('打开材料详情失败:', error)
    ElMessage.error('打开材料详情失败')
  }
}

const reanalyzePriced = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要重新分析材料 "${row.material_name}" 吗？`,
      '重新分析确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    ElMessage.info('重新分析已启动')
    // TODO: 调用重新分析API
    
    // 模拟分析过程
    setTimeout(async () => {
      ElMessage.success('重新分析完成')
      await fetchPricedAnalysisResults()
    }, 3000)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('重新分析失败')
    }
  }
}

const deletePricedAnalysis = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除材料 "${row.material_name}" 的分析结果吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    console.log('删除市场信息价材料分析结果:', row.material_id)
    // 调用删除项目材料API
    await deleteProjectMaterial(route.query.project_id, row.material_id)
    ElMessage.success('删除成功')
    
    // 重新获取数据
    await fetchPricedAnalysisResults()
    
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}
</script>

<style lang="scss" scoped>
.analysis-details-container {
  padding: 20px;
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.page-header {
  flex-shrink: 0;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 20px;

  .header-content {
    .el-breadcrumb {
      margin-bottom: 12px;
      
      :deep(.el-breadcrumb__item):not(:last-child) {
        .el-breadcrumb__inner {
          cursor: pointer;
          color: $color-primary;
          
          &:hover {
            text-decoration: underline;
          }
        }
      }
    }

    .page-title {
      font-size: 24px;
      font-weight: 600;
      color: $text-primary;
      margin: 0 0 8px 0;
    }

    .page-subtitle {
      font-size: 14px;
      color: $text-secondary;
      margin: 0;
    }
  }

  .header-actions {
    display: flex;
    align-items: center;
    gap: 12px;
  }
}

.overview-section {
  flex-shrink: 0;
  margin-bottom: 20px;

  .stats-row {
    display: flex;
    flex-wrap: wrap;

    // 防止el-row的clearfix伪元素影响flex布局
    &::before,
    &::after {
      display: none;
    }

    :deep(.el-col) {
      display: flex;
      flex-direction: column;
    }

    .stat-card {
      flex: 1;
      background: white;
      border-radius: 8px;
      padding: 20px;
      display: flex;
      align-items: center;
      box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
      margin-bottom: 20px;

      .stat-icon {
        width: 50px;
        height: 50px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 16px;
        font-size: 20px;
        color: white;

        &.total {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        &.analyzed {
          background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }

        &.reasonable {
          background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        }

        &.risk {
          background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        }
      }

      .stat-content {
        flex: 1;

        .stat-number {
          font-size: 24px;
          font-weight: 700;
          color: $text-primary;
          line-height: 1;
          margin-bottom: 4px;
        }

        .stat-label {
          font-size: 14px;
          color: $text-secondary;
          margin-bottom: 4px;
        }

        .stat-progress {
          font-size: 12px;
          color: $text-placeholder;

          &.success {
            color: $color-success;
          }

          &.danger {
            color: $color-danger;
          }
        }
      }
    }
  }
}

.results-card {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;

  :deep(.el-card__body) {
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow: hidden;
    padding: 20px !important;
  }

  .card-header {
    flex-shrink: 0;
    display: flex;
    justify-content: space-between;
    align-items: center;

    .card-title {
      font-size: 16px;
      font-weight: 600;
      color: $text-primary;
    }

    .header-filters {
      display: flex;
      align-items: center;
    }
  }

  .batch-toolbar {
    flex-shrink: 0;
    margin-bottom: 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;

    .selected-info {
      display: flex;
      align-items: center;
      gap: 8px;
      color: $text-secondary;
    }

    .batch-actions {
      display: flex;
      gap: 8px;
    }
  }

  .table-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-height: 0;
    overflow: hidden;

    .table-wrapper {
      flex: 1;
      overflow: hidden;

      :deep(.el-table) {
        height: 100%;
      }

      :deep(.el-table__body-wrapper) {
        flex: 1;
      }
    }

    .pagination-wrapper {
      flex-shrink: 0;
      display: flex;
      justify-content: center;
      margin-top: auto;
      padding-top: 16px;
      border-top: 1px solid #f0f0f0;
    }
  }

  .material-info {
    .material-name {
      font-weight: 500;
      color: $text-primary;
      margin-bottom: 2px;
    }

    .material-spec {
      font-size: 12px;
      color: $text-secondary;
    }
  }

  /* 置信度列样式已移除 */

  .price-range {
    .range-separator {
      margin: 0 4px;
      color: $text-secondary;
    }
  }

  .weighted-price {
    font-weight: 600;
    color: $text-primary;
  }

  .deviation-normal {
    color: $color-success;
  }

  .deviation-warning {
    color: $color-warning;
  }

  .deviation-danger {
    color: $color-danger;
  }

  .no-data {
    color: $text-placeholder;
  }
}

// 详情对话框样式
.detail-content {
  .detail-section {
    margin-bottom: 24px;

    &:last-child {
      margin-bottom: 0;
    }
  }

  // 数据来源样式
  .data-source-table-wrapper {
    margin-top: 8px;
    width: 100%;
    overflow-x: auto;

    .data-source-table {
      width: 100%;

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
        font-size: 12px;
        color: #666;
      }
    }

    .data-source-note {
      margin: 8px 0 0 0;
      color: #909399;
      font-size: 12px;
      line-height: 1.6;
    }
  }

  .risk-factors-list {
    list-style: none;
    padding: 0;
    margin: 0;

    .risk-factor {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 0;
      border-bottom: 1px solid $border-color-lighter;

      &:last-child {
        border-bottom: none;
      }

      .risk-icon {
        color: $color-warning;
      }
    }
  }

  .ai-explanation {
    padding: 16px;
    background-color: $bg-color-base;
    border-radius: 8px;
    line-height: 1.6;
    color: $text-regular;
  }
  // AI调用详情样式
    .ai-detail-item {
      margin-bottom: 24px;

      &:last-child {
        margin-bottom: 0;
      }

      .ai-detail-title {
        font-size: 14px;
        font-weight: 600;
        color: $text-primary;
        margin: 0 0 12px 0;
        display: flex;
        align-items: center;
        gap: 8px;

        .el-icon {
          font-size: 16px;
        }
      }

      .ai-prompt-content {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 6px;
        padding: 16px;

        pre {
          margin: 0;
          padding: 0;
          white-space: pre-wrap;
          word-wrap: break-word;
          font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
          font-size: 13px;
          line-height: 1.5;
          color: #2d3748;
        }
      }

      .ai-response-content {
        .response-formatted {
          .response-item {
            margin-bottom: 16px;
            padding: 12px;
            background-color: #fafbfc;
            border: 1px solid #e1e8ed;
            border-radius: 6px;

            &:last-child {
              margin-bottom: 0;
            }

            strong {
              display: inline-block;
              margin-bottom: 8px;
              color: $text-primary;
              font-weight: 600;
            }

            pre {
              margin: 0;
              padding: 8px 0 0 0;
              white-space: pre-wrap;
              word-wrap: break-word;
              font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
              font-size: 12px;
              line-height: 1.4;
              color: #495057;
            }

            span {
              color: $text-regular;
              font-size: 14px;
            }
          }
        }

        .response-raw {
          background-color: #f8f9fa;
          border: 1px solid #e9ecef;
          border-radius: 6px;
          padding: 16px;
          max-height: 400px;
          overflow-y: auto;

          pre {
            margin: 0;
            padding: 0;
            white-space: pre-wrap;
            word-wrap: break-word;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 12px;
            line-height: 1.4;
            color: #495057;
          }
        }
      }
    }

    .ai-model-info {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 16px;
      padding-top: 16px;
      border-top: 1px solid #e9ecef;

      .el-tag {
        display: flex;
        align-items: center;
        gap: 4px;

        .el-icon {
          font-size: 12px;
        }
      }
    }

    .history-item {
      .history-action {
        font-weight: 500;
        color: $text-primary;
        margin-bottom: 4px;
      }

      .history-note {
        font-size: 14px;
        color: $text-secondary;
        margin-bottom: 4px;
      }

      .history-user {
        font-size: 12px;
        color: $text-placeholder;
      }
    }
  }

// 响应式设计
@media (max-width: $breakpoint-md) {
  .analysis-details-container {
    padding: 10px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;

    .header-actions {
      width: 100%;
      flex-wrap: wrap;
      gap: 8px;
    }
  }

  .stats-row {
    .stat-card {
      padding: 16px;

      .stat-icon {
        width: 40px;
        height: 40px;
        font-size: 18px;
      }

      .stat-content .stat-number {
        font-size: 20px;
      }
    }
  }

  .card-header {
    flex-direction: column;
    gap: 12px !important;
    align-items: flex-start !important;

    .header-filters {
      width: 100%;
      flex-wrap: wrap;
      gap: 8px;

      .el-select {
        width: 100px !important;
      }
    }
  }
}

// 分析进度显示样式
.analysis-progress-section {
  flex-shrink: 0;
  margin-bottom: 20px;

  .progress-content {
    .progress-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;

      h3 {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
        color: $text-primary;
      }

      .progress-text {
        font-size: 14px;
        color: $text-secondary;
      }
    }

    .progress-bar {
      margin-bottom: 12px;
    }

    .progress-info {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 12px;
      color: $text-placeholder;
    }
  }
}

// 分析类型切换样式
.analysis-type-toggle {
  margin-left: 16px;
}

// 市场信息价材料分析结果样式
.price-increase {
  color: #f56565;
  font-weight: 600;
}

.price-decrease {
  color: #48bb78;
  font-weight: 600;
}

.price-value {
  font-weight: 500;
}

.unit-hint {
  font-size: 11px;
  color: #909399;
  margin-left: 2px;
}

.source-type {
  font-size: 12px;
  color: #666;
  background-color: #f7fafc;
  padding: 2px 6px;
  border-radius: 3px;
}

// 搜索网址样式
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

// 头部左侧样式调整
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;

  .header-left {
    display: flex;
    align-items: center;
    flex: 1;
  }

  .header-filters {
    display: flex;
    align-items: center;
    gap: 8px;
  }
}

// 空状态样式
.empty-actions {
  text-align: center;
  
  .empty-tips {
    max-width: 400px;
    margin: 0 auto;
    line-height: 1.5;
    
    p {
      margin: 0;
    }
  }
}

// AI模型选择对话框样式
.model-select-content {
  padding: 0 20px;
  
  .model-select-hint {
    margin: 0 0 20px 0;
    font-size: 14px;
    color: $text-secondary;
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
      
      &:hover {
        border-color: $color-primary;
        box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
      }
      
      &.is-checked {
        border-color: $color-primary;
        background: linear-gradient(135deg, rgba(64, 158, 255, 0.08) 0%, rgba(64, 158, 255, 0.02) 100%);
        box-shadow: 0 4px 16px rgba(64, 158, 255, 0.2);
      }
      
      :deep(.el-radio__input) {
        margin-top: 4px;
      }
      
      :deep(.el-radio__label) {
        padding-left: 12px;
        width: 100%;
      }
      
      .model-info {
        .model-name {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 16px;
          font-weight: 600;
          color: $text-primary;
          margin-bottom: 6px;
          
          .el-icon {
            font-size: 20px;
            color: $color-primary;
          }
        }
        
        .model-desc {
          font-size: 13px;
          color: $text-secondary;
          line-height: 1.4;
        }
      }
    }
  }
}
</style>
