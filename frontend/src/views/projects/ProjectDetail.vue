<template>
  <div class="project-detail-container">
    <!-- 加载状态 -->
    <div v-if="loading && !analysisState.isAnalyzing" v-loading="loading" style="height: 200px;" />
    
    <template v-else-if="project">
      <!-- 项目标题栏 -->
      <div class="page-header">
        <div class="header-content">
          <div class="title-section">
            <h1 class="page-title">{{ project.name }}</h1>
            <el-tag :type="getStatusType(project.status)" class="status-tag">
              {{ getStatusText(project.status) }}
            </el-tag>
          </div>
          <p class="page-subtitle">
            <el-icon><Location /></el-icon>
            {{ project.location || '未指定地点' }}
          </p>
        </div>
        <div class="header-actions">
          <el-button @click="$router.back()">
            返回
          </el-button>
          <el-button
            type="primary"
            :icon="Edit"
            @click="openEditDialog"
          >
            编辑
          </el-button>
        </div>
      </div>

      <!-- 项目统计卡片 -->
      <el-row :gutter="20" class="stats-row">
        <el-col :xs="24" :sm="12" :lg="6">
          <div class="stat-card">
            <div class="stat-icon materials">
              <el-icon><Box /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ projectStats.total_materials }}</div>
              <div class="stat-label">材料总数</div>
            </div>
          </div>
        </el-col>
        
        <el-col :xs="24" :sm="12" :lg="6">
          <div class="stat-card">
            <div class="stat-icon analyzed">
              <el-icon><TrendCharts /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ projectStats.analyzed_materials }}</div>
              <div class="stat-label">AI已分析材料</div>
            </div>
          </div>
        </el-col>
        
        <el-col :xs="24" :sm="12" :lg="6">
          <div class="stat-card">
            <div class="stat-icon matched">
              <el-icon><SuccessFilled /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ projectStats.matched_materials }}</div>
              <div class="stat-label">已匹配材料</div>
            </div>
          </div>
        </el-col>
        
        <el-col :xs="24" :sm="12" :lg="6">
          <div class="stat-card">
            <div class="stat-icon progress">
              <el-icon><Promotion /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ projectStats.progress }}%</div>
              <div class="stat-label">完成进度</div>
            </div>
          </div>
        </el-col>
      </el-row>

      <!-- 主要内容区域 -->
      <el-row :gutter="20" class="content-row">
        <!-- 左侧：项目信息和操作 -->
        <el-col :xs="24" :lg="8">
          <div class="left-content">
            <!-- 项目基本信息 -->
            <el-card class="info-card">
              <template #header>
                <span class="card-title">项目信息</span>
              </template>
              
              <div class="info-list">
                <div class="info-item">
                  <span class="label">项目类型:</span>
                  <span class="value">{{ getProjectTypeText(project.project_type) }}</span>
                </div>
                <div class="info-item">
                  <span class="label">工程造价:</span>
                  <span class="value">
                    {{ project.budget_amount ? `${project.budget_amount} 万元` : '未设置' }}
                  </span>
                </div>
                <div class="info-item">
                  <span class="label">基期信息价日期:</span>
                  <span class="value">{{ formatYearMonth(project.base_price_date) }}</span>
                </div>
                <div class="info-item">
                  <span class="label">合同工期:</span>
                  <span class="value">{{ getContractPeriodText(project) }}</span>
                </div>
                <div class="info-item">
                  <span class="label">基期信息价地区:</span>
                  <span class="value">{{ getLocationText(project) }}</span>
                </div>
                <div class="info-item">
                  <span class="label">是否支持调价:</span>
                  <span class="value">{{ project.support_price_adjustment ? '是' : '否' }}</span>
                </div>
                <div class="info-item">
                  <span class="label">调价范围:</span>
                  <span class="value">{{ project.price_adjustment_range ? `${project.price_adjustment_range}%` : '未设置' }}</span>
                </div>
                <div class="info-item">
                  <span class="label">分析范围:</span>
                  <span class="value">{{ getAuditScopeText(project.audit_scope) }}</span>
                </div>
                <div class="info-item">
                  <span class="label">创建时间:</span>
                  <span class="value">{{ formatDate(project.created_at) }}</span>
                </div>
                <div class="info-item">
                  <span class="label">创建人:</span>
                  <span class="value">{{ project.created_by_name || '未知' }}</span>
                </div>
              </div>
              
              <div v-if="project.description" class="description">
                <h4>项目描述</h4>
                <p>{{ project.description }}</p>
              </div>
            </el-card>

            <!-- 快速操作 -->
            <el-card class="actions-card">
              <template #header>
                <span class="card-title">快速操作</span>
              </template>
              
              <div class="action-buttons">
                <el-button
                  :icon="Upload"
                  @click="goToMaterialUpload"
                  class="action-btn upload-btn"
                >
                  上传材料清单
                </el-button>
                
                <el-button
                  :icon="Search"
                  @click="startMaterialIdentification"
                  :disabled="!canStartIdentification"
                  class="action-btn identification-btn"
                >
                  无信息价材料识别
                </el-button>
                
                <div class="analysis-button-group">
                  <el-button
                    :icon="TrendCharts"
                    @click="startPriceAnalysis"
                    :disabled="!canStartPriceAnalysis || analysisState.isAnalyzing"
                    :loading="analysisState.isAnalyzing"
                    class="action-btn analysis-btn"
                  >
                    AI分析(无信息价材料)
                  </el-button>

                  <el-button
                    :icon="DataAnalysis"
                    @click="viewAnalysisResults"
                    :disabled="!hasAnalysisResults || analysisState.isAnalyzing"
                    class="action-btn view-results-btn"
                    :loading="analysisState.isAnalyzing"
                  >
                    {{ analysisState.isAnalyzing ? '分析中...' : '查看无信息价分析结果' }}
                  </el-button>
                  
                  <el-button
                    :icon="TrendCharts"
                    @click="startPricedMaterialAnalysis"
                    :disabled="!canStartPricedMaterialAnalysis || analysisState.isAnalyzing"
                    :loading="analysisState.isAnalyzing"
                    class="action-btn priced-analysis-btn"
                  >
                    AI价格分析(市场信息价材料)
                  </el-button>
                  
                  <el-button
                    :icon="View"
                    @click="viewPricedMaterialAnalysisResults"
                    :disabled="!hasPricedAnalysisResults || analysisState.isAnalyzing"
                    class="action-btn view-priced-results-btn"
                  >
                    查看市场信息价分析结果
                  </el-button>
                  
                  <!-- 分析进度展示 -->
                  <div v-if="analysisState.isAnalyzing || analysisState.isIdentifying" class="analysis-progress">
                    <div class="progress-info">
                      <span class="progress-text">{{ analysisState.currentStep }}</span>
                      <span class="progress-percent">{{ Math.round(analysisState.progress) }}%</span>
                    </div>
                    <el-progress 
                      :percentage="analysisState.progress" 
                      :stroke-width="4"
                      status="active"
                    />
                    <div class="progress-detail">
                      {{ analysisState.completedSteps }}/{{ analysisState.totalSteps }} 个材料分析完成
                    </div>
                  </div>
                </div>

                <el-button
                  :icon="Document"
                  @click="generateReport"
                  :disabled="!canGenerateReport"
                  class="action-btn report-btn"
                >
                  生成价格报告
                </el-button>
                
                <el-button
                  :icon="Download"
                  @click="handleExportProject"
                  class="action-btn export-btn"
                >
                  导出项目数据
                </el-button>
              </div>
            </el-card>
          </div>
        </el-col>

        <!-- 右侧：材料列表和分析结果 -->
        <el-col :xs="24" :lg="16">
          <el-card class="materials-card">
            <template #header>
              <div class="card-header">
                <span class="card-title">项目材料</span>
                <div class="header-actions">
                  <el-button-group size="small">
                    <el-button
                      :type="activeTab === 'all' ? 'primary' : ''"
                      @click="activeTab = 'all'"
                    >
                      全部 ({{ projectStats.total_materials || 0 }})
                    </el-button>
                    <el-button
                      :type="activeTab === 'matched' ? 'primary' : ''"
                      @click="activeTab = 'matched'"
                    >
                      已匹配 ({{ projectStats.matched_materials || 0 }})
                    </el-button>
                    <el-button
                      :type="activeTab === 'needs_review' ? 'warning' : ''"
                      @click="activeTab = 'needs_review'"
                    >
                      需人工复核 ({{ projectStats.needs_review_materials || 0 }})
                    </el-button>
                    <el-button
                      :type="activeTab === 'unmatched' ? 'primary' : ''"
                      @click="activeTab = 'unmatched'"
                    >
                      未匹配/无信息价材料 ({{ projectStats.unpriced_materials || 0 }})
                    </el-button>
                  </el-button-group>
                  <el-button :icon="Refresh" @click="fetchMaterials" />
                </div>
              </div>
            </template>

            <!-- 搜索过滤区域 -->
            <div class="search-filter-section">
              <el-form :inline="true" class="search-form">
                <el-form-item label="搜索">
                  <el-input
                    v-model="searchFilters.keyword"
                    placeholder="材料名称/编码/规格"
                    clearable
                    style="width: 250px"
                    :prefix-icon="Search"
                    @clear="handleSearchClear"
                  />
                </el-form-item>
                <el-form-item label="单位">
                  <el-select
                    v-model="searchFilters.unit"
                    placeholder="全部单位"
                    clearable
                    style="width: 120px"
                  >
                    <el-option
                      v-for="unit in unitOptions"
                      :key="unit"
                      :label="unit"
                      :value="unit"
                    />
                  </el-select>
                </el-form-item>
                <el-form-item label="匹配状态">
                  <el-select
                    v-model="searchFilters.matchStatus"
                    placeholder="全部状态"
                    clearable
                    style="width: 140px"
                  >
                    <el-option label="已匹配" value="matched" />
                    <el-option label="需人工复核" value="needs_review" />
                    <el-option label="未匹配" value="unmatched" />
                  </el-select>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" :icon="Search" @click="applySearchFilters">
                    搜索
                  </el-button>
                  <el-button @click="resetSearchFilters">
                    重置
                  </el-button>
                </el-form-item>
              </el-form>
            </div>

            <!-- 批量操作工具栏 -->
            <div v-if="selectedCount > 0" class="batch-toolbar">
              <div class="selected-info">
                已选择 {{ selectedCount }} 项材料
                <el-divider direction="vertical" />
                <el-switch
                  v-model="allSelected"
                  inline-prompt
                  active-text="全选所有页"
                  inactive-text="仅选本页"
                  @change="onToggleSelectAll"
                />
              </div>
              <div class="batch-actions">
                <el-button
                  type="danger"
                  size="small"
                  :icon="Delete"
                  @click="batchDeleteMaterials"
                >
                  批量删除
                </el-button>
                <el-button size="small" @click="clearAllSelection">取消选择</el-button>
              </div>
            </div>

            <!-- 表格容器 -->
            <div class="table-container">
              <!-- 材料表格 -->
              <el-table
                ref="materialTableRef"
                v-loading="materialsLoading"
                :data="filteredMaterials"
                :row-key="row => row.id"
                :reserve-selection="true"
                stripe
                style="width: 100%"
                height="100%"
                @selection-change="onMaterialSelectionChange"
              >
                <el-table-column type="selection" width="55" />
                <el-table-column prop="material_code" label="编码" width="120">
                  <template #default="{ row }">
                    <span>{{ row.material_code || '-' }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="material_name" label="材料名称" min-width="200" />
                <el-table-column prop="specification" label="规格型号" width="150">
                  <template #default="{ row }">
                    <span>{{ row.specification || '-' }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="unit" label="单位" width="80" />
                <el-table-column prop="quantity" label="数量" width="100">
                  <template #default="{ row }">
                    {{ formatNumber(row.quantity) }}
                  </template>
                </el-table-column>
                <el-table-column prop="unit_price" label="单价" width="120">
                  <template #default="{ row }">
                    ¥{{ formatNumber(row.unit_price) }}
                  </template>
                </el-table-column>
                <el-table-column prop="remarks" label="备注" width="150">
                  <template #default="{ row }">
                    <span>{{ row.remarks || '-' }}</span>
                  </template>
                </el-table-column>
                <el-table-column label="匹配状态" width="120">
                  <template #default="{ row }">
                    <el-tag
                      :type="row.is_matched ? 'success' : (row.needs_review ? 'warning' : 'info')"
                      size="small"
                    >
                      {{ row.is_matched ? '已匹配' : (row.needs_review ? '需人工复核' : '未匹配') }}
                    </el-tag>
                    <div v-if="row.match_score !== null && row.match_score !== undefined" class="match-score">
                      匹配度: {{ (row.match_score * 100).toFixed(1) }}%
                    </div>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="160" fixed="right">
                  <template #default="{ row }">
                    <el-button
                      type="primary"
                      link
                      size="small"
                      @click="viewMaterialDetail(row)"
                    >
                      详情
                    </el-button>
                    <el-button
                      type="danger"
                      link
                      size="small"
                      @click="deleteMaterial(row)"
                    >
                      删除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>

              <!-- 空状态 -->
              <el-empty v-if="materials.length === 0" description="暂无材料数据">
                <el-button type="primary" @click="goToMaterialUpload">
                  上传材料清单
                </el-button>
              </el-empty>
            </div>

            <!-- 分页：固定在卡片底部 -->
            <div v-if="materials.length > 0" class="pagination-wrapper">
              <BasePagination
                v-model:current-page="pagination.page"
                v-model:page-size="pagination.size"
                :total="pagination.total"
                @size-change="handleSizeChange"
                @current-change="handlePageChange"
              />
            </div>
          </el-card>
        </el-col>
      </el-row>

    </template>

    <!-- 项目不存在 -->
    <el-result
      v-else
      icon="warning"
      title="项目不存在"
      sub-title="您访问的项目不存在或已被删除，请检查链接是否正确"
    >
      <template #extra>
        <el-button @click="$router.push('/projects')">返回项目列表</el-button>
        <el-button type="primary" @click="refreshProject">重新加载</el-button>
      </template>
    </el-result>

    <!-- 项目编辑对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑项目"
      width="900px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        :rules="editFormRules"
        label-width="120px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="项目名称" prop="name">
              <el-input v-model="editForm.name" placeholder="请输入项目名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="项目位置" prop="location">
              <el-input v-model="editForm.location" placeholder="请输入项目位置" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="项目类型" prop="project_type">
              <el-select v-model="editForm.project_type" placeholder="请选择项目类型" style="width: 100%">
                <el-option label="建筑工程" value="building" />
                <el-option label="装修工程" value="decoration" />
                <el-option label="市政工程" value="municipal" />
                <el-option label="园林工程" value="landscape" />
                <el-option label="公路工程" value="highway" />
                <el-option label="其他工程" value="other" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="工程造价" prop="budget_amount">
              <el-input v-model.number="editForm.budget_amount" placeholder="请输入工程造价(万元)" type="number" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="基期信息价日期">
              <el-date-picker
                v-model="editForm.base_price_date"
                type="month"
                placeholder="选择基期信息价日期"
                format="YYYY-MM"
                value-format="YYYY-MM"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="基期信息价省份">
              <el-select v-model="editForm.base_price_province" placeholder="选择省份" clearable style="width: 100%">
                <el-option label="浙江省" value="330000" />
                <el-option label="江苏省" value="320000" />
                <el-option label="广东省" value="440000" />
                <el-option label="北京市" value="110000" />
                <el-option label="上海市" value="310000" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="基期信息价城市">
              <el-select v-model="editForm.base_price_city" placeholder="选择城市" clearable style="width: 100%">
                <el-option label="杭州市" value="330100" />
                <el-option label="宁波市" value="330200" />
                <el-option label="南京市" value="320100" />
                <el-option label="苏州市" value="320500" />
                <el-option label="广州市" value="440100" />
                <el-option label="深圳市" value="440300" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="基期信息价区县">
              <el-select v-model="editForm.base_price_district" placeholder="选择区县" clearable style="width: 100%">
                <el-option label="上城区" value="330102" />
                <el-option label="拱墅区" value="330104" />
                <el-option label="西湖区" value="330105" />
                <el-option label="滨江区" value="330106" />
                <el-option label="萧山区" value="330107" />
                <el-option label="余杭区" value="330110" />
                <el-option label="临平区" value="330113" />
                <el-option label="钱塘区" value="330114" />
                <el-option label="富阳区" value="330111" />
                <el-option label="临安区" value="330112" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="合同开始月份">
              <el-date-picker
                v-model="editForm.contract_start_date"
                type="month"
                format="YYYY-MM"
                value-format="YYYY-MM"
                placeholder="选择合同开始月份"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="合同结束月份">
              <el-date-picker
                v-model="editForm.contract_end_date"
                type="month"
                format="YYYY-MM"
                value-format="YYYY-MM"
                placeholder="选择合同结束月份"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="是否支持调价">
              <el-switch
                v-model="editForm.support_price_adjustment"
                active-text="是"
                inactive-text="否"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="调价范围(%)">
              <el-input-number
                v-model="editForm.price_adjustment_range"
                :min="0"
                :max="100"
                :step="0.1"
                style="width: 100%"
                placeholder="调价范围"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="分析范围">
          <el-checkbox-group v-model="editForm.audit_scope">
            <el-checkbox value="price_analysis">价格合理性分析</el-checkbox>
            <el-checkbox value="material_matching">材料匹配度检查</el-checkbox>
            <el-checkbox value="market_comparison">市场价格对比</el-checkbox>
            <el-checkbox value="risk_assessment">风险评估</el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <el-form-item label="项目描述">
          <el-input
            v-model="editForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入项目描述"
          />
        </el-form-item>

        <el-form-item label="项目状态" prop="status">
          <el-select v-model="editForm.status" placeholder="请选择项目状态" style="width: 100%">
            <el-option label="草稿" value="draft" />
            <el-option label="处理中" value="processing" />
            <el-option label="已完成" value="completed" />
            <el-option label="失败" value="failed" />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showEditDialog = false">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="handleUpdateProject">
            保存
          </el-button>
        </div>
      </template>
    </el-dialog>

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
          @click="confirmStartPriceAnalysis"
        >
          开始分析
        </el-button>
      </template>
    </el-dialog>

    <!-- AI分析进度弹窗 -->
    <el-dialog
      v-model="showAnalysisProgressDialog"
      title="AI价格分析进行中"
      width="500px"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      :show-close="false"
    >
      <div class="analysis-progress-content">
        <div class="progress-section">
          <div class="progress-info">
            <span class="progress-text">{{ analysisState.currentStep }}</span>
            <span class="progress-percent">{{ Math.round(analysisState.progress) }}%</span>
          </div>
          <el-progress 
            :percentage="analysisState.progress" 
            :stroke-width="8"
            :show-text="false"
          />
          <div class="progress-detail">
            已完成 {{ analysisState.completedSteps }} / {{ analysisState.totalSteps }} 个材料
          </div>
        </div>
        
        <div class="analysis-tips">
          <el-icon class="tip-icon"><InfoFilled /></el-icon>
          <div class="tip-content">
            <p>AI正在分析材料的市场价格，这个过程需要一些时间</p>
            <p>分析完成后系统将自动跳转到分析结果页面</p>
            <p>您也可以选择"稍后查看"，分析将在后台继续进行</p>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button 
            @click="runAnalysisInBackground"
          >
            稍后查看
          </el-button>
          <el-button 
            type="primary" 
            :disabled="!analysisState.canViewResults"
            @click="viewAnalysisResults"
          >
            {{ analysisState.canViewResults ? '立即查看结果' : '查看分析结果' }}
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 材料分析详情弹窗 -->
    <MaterialAnalysisDetailDialog
      v-model="showAnalysisDetailDialog"
      :material-id="selectedMaterialId"
      @close="handleAnalysisDetailDialogClose"
      @refresh="handleMaterialRefresh"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import BasePagination from '@/components/BasePagination.vue'
import MaterialAnalysisDetailDialog from '@/components/analysis/MaterialAnalysisDetailDialog.vue'
import { useSelectionAcrossPages } from '@/composables/useSelectionAcrossPages'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus'
import {
  Location,
  Edit,
  Box,
  TrendCharts,
  SuccessFilled,
  Promotion,
  View,
  Upload,
  Document,
  Download,
  Refresh,
  Search,
  Delete,
  DataAnalysis,
  InfoFilled,
  MagicStick,
  ChatDotRound
} from '@element-plus/icons-vue'
import {
  getProject,
  getProjectStats,
  getProjectMaterials,
  exportProject,
  deleteProjectMaterial,
  batchDeleteProjectMaterials,
  updateProject
} from '@/api/projects'
import {
  matchProjectMaterials,
  getMatchingStatistics
} from '@/api/matching'
import {
  batchAnalyzeMaterials,
  getProjectAnalysisStatistics
} from '@/api/analysis'
import { formatDate, formatNumber } from '@/utils'

const route = useRoute()
const router = useRouter()

const PROVINCE_MAP = {
  '110000': '北京市',
  '120000': '天津市',
  '130000': '河北省',
  '140000': '山西省',
  '150000': '内蒙古自治区',
  '210000': '辽宁省',
  '220000': '吉林省',
  '230000': '黑龙江省',
  '310000': '上海市',
  '320000': '江苏省',
  '330000': '浙江省',
  '340000': '安徽省',
  '350000': '福建省',
  '360000': '江西省',
  '370000': '山东省',
  '410000': '河南省',
  '420000': '湖北省',
  '430000': '湖南省',
  '440000': '广东省',
  '450000': '广西壮族自治区',
  '460000': '海南省',
  '500000': '重庆市',
  '510000': '四川省',
  '520000': '贵州省',
  '530000': '云南省',
  '540000': '西藏自治区',
  '610000': '陕西省',
  '620000': '甘肃省',
  '630000': '青海省',
  '640000': '宁夏回族自治区',
  '650000': '新疆维吾尔自治区'
}

const CITY_MAP = {
  '110100': '北京市',
  '120100': '天津市',
  '130100': '石家庄市',
  '140100': '太原市',
  '150100': '呼和浩特市',
  '210100': '沈阳市',
  '220100': '长春市',
  '230100': '哈尔滨市',
  '310100': '上海市',
  '320100': '南京市',
  '330100': '杭州市',
  '340100': '合肥市',
  '350100': '福州市',
  '360100': '南昌市',
  '370100': '济南市',
  '410100': '郑州市',
  '420100': '武汉市',
  '430100': '长沙市',
  '440100': '广州市',
  '450100': '南宁市',
  '460100': '海口市',
  '500100': '重庆市',
  '510100': '成都市',
  '520100': '贵阳市',
  '530100': '昆明市',
  '540100': '拉萨市',
  '610100': '西安市',
  '620100': '兰州市',
  '630100': '西宁市',
  '640100': '银川市',
  '650100': '乌鲁木齐市'
}

const DISTRICT_MAP = {
  // 杭州市区（2021年行政区划调整后）
  '330102': '上城区',
  '330104': '拱墅区',
  '330105': '西湖区',
  '330106': '滨江区',
  '330107': '萧山区',
  '330108': '余杭区',      // 旧余杭区编码
  '330109': '富阳区',
  '330110': '余杭区',      // 新余杭区编码
  '330111': '富阳区',
  '330112': '临安区',
  '330113': '临平区',
  '330114': '钱塘区',
  '330122': '桐庐县',
  '330127': '淳安县',
  '330182': '建德市',
  // 历史区划（已合并，保留兼容）
  '330101': '上城区',
  '330103': '江干区'
}

const resolveRegionName = (code, map) => {
  if (!code) return null
  return map[code] || code
}

// 响应式数据
const loading = ref(false)
const materialsLoading = ref(false)
const activeTab = ref('all')
const showEditDialog = ref(false)
const submitting = ref(false)
const editFormRef = ref()
const materialTableRef = ref()
const selectedMaterials = ref([]) // 保留：用于表格本页显示
// 跨页选择逻辑
const {
  allSelected,
  selectedIds: selectedMaterialIds,
  excludedIds: excludedMaterialIds,
  toggleSelectAll,
  clearAll: clearAllSelection,
  handleSelectionChange,
  syncSelectionOnPage,
  getSelectedIds,
  createSelectedCount
} = useSelectionAcrossPages('id')

const selectedCount = createSelectedCount(() => pagination.total)

// 分析详情弹窗状态
const showAnalysisDetailDialog = ref(false)
const selectedMaterialId = ref(null)

const onToggleSelectAll = () => {
  // 切换模式后，重新同步当前页勾选状态
  nextTick(() => syncSelectionOnPage(materialTableRef, filteredMaterials.value))
}

const onMaterialSelectionChange = (selection) => {
  handleSelectionChange(selection, filteredMaterials.value)
  selectedMaterials.value = selection
}

const project = ref(null)
const projectStats = ref({
  total_materials: 0,
  analyzed_materials: 0,
  matched_materials: 0,
  needs_review_materials: 0,
  unpriced_materials: 0,
  progress: 0
})
const materials = ref([])

// 搜索过滤器
const searchFilters = reactive({
  keyword: '',
  unit: '',
  matchStatus: ''
})

// 单位选项（从材料列表中动态提取）
const unitOptions = computed(() => {
  const units = new Set()
  materials.value.forEach(m => {
    if (m.unit) units.add(m.unit)
  })
  return Array.from(units).sort()
})

// 分析状态管理
const analysisState = reactive({
  isAnalyzing: false,
  isIdentifying: false,
  progress: 0,
  currentStep: '',
  totalSteps: 0,
  completedSteps: 0,
  canViewResults: false,
  isBackgroundMode: false
})

// 分析进度弹窗显示状态
const showAnalysisProgressDialog = ref(false)

// AI模型选择相关
const showModelSelectDialog = ref(false)
const selectedAIModel = ref('dashscope') // 默认使用通义千问

// 编辑表单数据
const editForm = reactive({
  name: '',
  location: '',
  project_type: '',
  budget_amount: null,
  base_price_date: '',
  base_price_province: '',
  base_price_city: '',
  base_price_district: '',
  support_price_adjustment: true,
  price_adjustment_range: 5.0,
  audit_scope: [],
  description: '',
  status: 'draft'
})

// 编辑表单校验规则
const editFormRules = {
  name: [
    { required: true, message: '请输入项目名称', trigger: 'blur' },
    { min: 2, max: 100, message: '项目名称长度在2到100个字符', trigger: 'blur' }
  ],
  project_type: [
    { required: true, message: '请选择项目类型', trigger: 'change' }
  ],
  status: [
    { required: true, message: '请选择项目状态', trigger: 'change' }
  ]
}

// 分页数据
const pagination = reactive({
  page: 1,
  size: 50, // 增加默认每页显示数量以填满卡片空间
  total: 0
})

// 计算属性
const filteredMaterials = computed(() => materials.value)

// 实时统计计算属性
const realTimeStats = computed(() => {
  const matched = materials.value.filter(m => m.is_matched && m.matched_material_id).length
  const total = materials.value.length
  const unmatched = total - matched
  
  return {
    total_materials: total,
    matched_materials: matched,
    unmatched_materials: unmatched
  }
})

// 是否可以开始材料识别（有材料且还有未匹配的）
const canStartIdentification = computed(() => {
  return projectStats.value.total_materials > 0 && 
         (projectStats.value.matched_materials || 0) < projectStats.value.total_materials
})

// 是否可以开始价格分析（有未匹配的材料需要AI分析价格）
const canStartPriceAnalysis = computed(() => {
  const total = projectStats.value.total_materials || 0
  const matched = projectStats.value.matched_materials || 0
  const unmatched = total - matched
  // 只要有未匹配的材料就可以进行分析（包括重新分析）
  return unmatched > 0
})

// 是否可以开始市场信息价材料分析（有已匹配的材料）
const canStartPricedMaterialAnalysis = computed(() => {
  const matched = projectStats.value.matched_materials || 0
  // 只要有已匹配的材料就可以进行市场信息价材料分析
  return matched > 0
})

const canGenerateReport = computed(() => {
  return projectStats.value.analyzed_materials > 0
})

const hasAnalysisResults = computed(() => {
  return projectStats.value.analyzed_materials > 0
})

// 是否有市场信息价材料分析结果
const hasPricedAnalysisResults = computed(() => {
  // 可以通过检查已匹配材料数量来判断是否有市场信息价分析结果
  return projectStats.value.matched_materials > 0
})

// 获取项目详情
const fetchProject = async () => {
  loading.value = true
  try {
    const response = await getProject(route.params.id)
    project.value = response
  } catch (error) {
    ElMessage.error('获取项目详情失败')
    console.error('获取项目详情失败:', error)
  } finally {
    loading.value = false
  }

  // 项目数据加载完成后调整卡片对齐
  setTimeout(() => {
    adjustMaterialsCardHeight()
  }, 100)
}

// 获取项目统计
const fetchProjectStats = async () => {
  try {
    const response = await getProjectStats(route.params.id)
    // API现在直接返回数据，不再包装在data字段中
    projectStats.value = response
    console.log('项目统计数据:', response)
  } catch (error) {
    console.error('获取项目统计失败:', error)
  }
}

// 获取材料列表
const fetchMaterials = async () => {
  materialsLoading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size
    }
    if (searchFilters.keyword && searchFilters.keyword.trim()) {
      params.keyword = searchFilters.keyword.trim()
    }
    if (searchFilters.unit) {
      params.unit = searchFilters.unit
    }
    // 根据Tab或筛选条件设置匹配状态参数
    if (activeTab.value === 'matched') {
      params.is_matched = true
    } else if (activeTab.value === 'needs_review') {
      params.needs_review = true
    } else if (activeTab.value === 'unmatched') {
      params.is_matched = false
      params.needs_review = false
    } else if (searchFilters.matchStatus) {
      if (searchFilters.matchStatus === 'matched') {
        params.is_matched = true
      } else if (searchFilters.matchStatus === 'needs_review') {
        params.needs_review = true
      } else if (searchFilters.matchStatus === 'unmatched') {
        params.is_matched = false
        params.needs_review = false
      }
    }
    const response = await getProjectMaterials(route.params.id, params)
    console.log('获取项目材料数据响应:', response)
    
    // 新的API返回格式: { items: [], total: number, page: number, size: number, pages: number }
    if (response && typeof response === 'object' && response.items && Array.isArray(response.items)) {
      // 新的分页格式
      materials.value = response.items
      pagination.total = response.total || 0
      console.log(`加载了 ${materials.value.length} 个项目材料，总数: ${pagination.total}`)
    } else {
      // 兼容旧格式
      const result = response.data?.data || response.data || response
      
      if (Array.isArray(result)) {
        // 如果直接返回数组，说明没有分页信息
        materials.value = result
        pagination.total = result.length
      } else {
        // 如果是对象，包含分页信息
        materials.value = result.items || result.materials || result.data || []
        pagination.total = result.total || result.count || materials.value.length
      }
      console.log(`加载了 ${materials.value.length} 个项目材料，总数: ${pagination.total}`)
    }
    // 同步当前页勾选状态（跨页选择）
    await nextTick()
    syncSelectionOnPage(materialTableRef, filteredMaterials.value)
  } catch (error) {
    ElMessage.error('获取材料列表失败')
    console.error('获取材料列表失败:', error)
    materials.value = []
    pagination.total = 0
  } finally {
    materialsLoading.value = false
  }

  // 材料数据加载完成后调整卡片对齐
  setTimeout(() => {
    adjustMaterialsCardHeight()
  }, 50)
}

// 状态相关方法
const getStatusType = (status) => {
  const statusMap = {
    'draft': 'info',
    'processing': 'warning',
    'completed': 'success',
    'failed': 'danger'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status) => {
  const statusMap = {
    'draft': '草稿',
    'processing': '处理中',
    'completed': '已完成',
    'failed': '失败'
  }
  return statusMap[status] || status
}

const getProjectTypeText = (type) => {
  const typeMap = {
    'building': '建筑工程',
    'decoration': '装修工程',
    'municipal': '市政工程',
    'landscape': '园林工程',
    'highway': '公路工程',
    'other': '其他工程'
  }
  return typeMap[type] || type
}

// 获取地区文本
const getLocationText = (project) => {
  const parts = []

  const provinceName = resolveRegionName(project.base_price_province, PROVINCE_MAP)
  if (provinceName) parts.push(provinceName)

  const cityName = resolveRegionName(project.base_price_city, CITY_MAP)
  if (cityName) parts.push(cityName)

  const districtName = resolveRegionName(project.base_price_district, DISTRICT_MAP)
  if (districtName) parts.push(districtName)

  return parts.length > 0 ? parts.join(' ') : '未设置'
}

// 获取分析范围文本
const getAuditScopeText = (auditScope) => {
  if (!auditScope || !Array.isArray(auditScope) || auditScope.length === 0) {
    return '未设置'
  }

  const scopeMap = {
    'price_analysis': '价格合理性分析',
    'material_matching': '材料匹配度检查',
    'market_comparison': '市场价格对比',
    'risk_assessment': '风险评估'
  }

  return auditScope.map(scope => scopeMap[scope] || scope).join('、')
}

const getContractPeriodText = (project) => {
  const fmt = (m) => {
    if (!m) return null
    const s = String(m)
    if (s.includes('-')) {
      const [y, mm] = s.split('-')
      return `${y}年${String(mm).padStart(2, '0')}月`
    }
    if (/^\d{4}\d{2}$/.test(s)) {
      return `${s.slice(0,4)}年${s.slice(4)}月`
    }
    return s
  }
  const direct = project.contract_period
  if (direct && typeof direct === 'string') return direct
  const start = project.contract_start_date || project.contract_start || project.contract_start_month
  const end = project.contract_end_date || project.contract_end || project.contract_end_month
  const fs = fmt(start)
  const fe = fmt(end)
  if (fs && fe) return `${fs}至${fe}`
  if (project.description) {
    const m = String(project.description).match(/合同工期[:：]\s*(\d{4}[年-]\d{1,2}月?)\s*至\s*(\d{4}[年-]\d{1,2}月?)/)
    if (m) {
      const norm = (x) => {
        if (!x) return null
        const s = x.replace('年','-').replace('月','')
        const [y, mm] = s.split('-')
        return `${y}年${String(mm).padStart(2,'0')}月`
      }
      const s1 = norm(m[1])
      const s2 = norm(m[2])
      if (s1 && s2) return `${s1}至${s2}`
    }
  }
  return '未设置'
}

const formatYearMonth = (value) => {
  if (!value && value !== 0) return '未设置'
  const str = String(value).trim()
  if (!str) return '未设置'
  let normalized = str.replace('年', '-').replace('月', '')
  normalized = normalized.replace(/[/.]/g, '-')
  let year
  let month
  const parts = normalized.split('-').filter(Boolean)
  if (parts.length >= 2) {
    ;[year, month] = parts
  } else if (/^\d{6}$/.test(normalized)) {
    year = normalized.slice(0, 4)
    month = normalized.slice(4)
  } else if (/^\d{4}$/.test(normalized)) {
    year = normalized
    month = '01'
  } else {
    return str
  }
  const yearNum = parseInt(year, 10)
  let monthNum = parseInt(month, 10)
  if (!Number.isFinite(yearNum)) return str
  if (!Number.isFinite(monthNum)) monthNum = 1
  monthNum = Math.max(1, Math.min(12, monthNum))
  return `${yearNum}年${String(monthNum).padStart(2, '0')}月`
}

const getAnalysisStatusType = (status) => {
  const statusMap = {
    'pending': 'info',
    'processing': 'warning',
    'completed': 'success',
    'failed': 'danger'
  }
  return statusMap[status] || 'info'
}

const getAnalysisStatusText = (status) => {
  const statusMap = {
    'pending': '待分析',
    'processing': '分析中',
    'completed': '已完成',
    'failed': '失败'
  }
  return statusMap[status] || '未知'
}


// 分页处理
const handleSizeChange = (size) => {
  pagination.size = size
  pagination.page = 1
  fetchMaterials()
}

const handlePageChange = (page) => {
  pagination.page = page
  fetchMaterials()
}

// 搜索过滤方法
const applySearchFilters = () => {
  // 重置到第一页
  pagination.page = 1
  fetchMaterials()
}

const resetSearchFilters = () => {
  searchFilters.keyword = ''
  searchFilters.unit = ''
  searchFilters.matchStatus = ''
  pagination.page = 1
  fetchMaterials()
}

const handleSearchClear = () => {
  searchFilters.keyword = ''
  pagination.page = 1
  fetchMaterials()
}

// 操作方法
// 无信息价材料识别（原来的startAnalysis方法）
const startMaterialIdentification = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要开始无信息价材料识别吗？系统将对比项目材料与市场信息价材料库，识别出无信息价材料。',
      '确认识别',
      {
        confirmButtonText: '开始识别',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // 开启后台分析状态
    analysisState.isIdentifying = true
    analysisState.progress = 0
    analysisState.currentStep = '正在进行材料匹配分析...'
    
    ElMessage.info('无信息价材料识别已在后台开始...')
    
    // 模拟进度
    const progressTimer = setInterval(() => {
        if (analysisState.progress < 95) {
            analysisState.progress += Math.floor(Math.random() * 5) + 1
        }
    }, 800)

    const provinceName = resolveRegionName(project.value?.base_price_province, PROVINCE_MAP)
    const cityName = resolveRegionName(project.value?.base_price_city, CITY_MAP)
    const districtName = resolveRegionName(project.value?.base_price_district, DISTRICT_MAP)

    // 调用材料匹配API - 三级匹配模式
    // 传入 { __skipLoading: true } 跳过全局loading
    const result = await matchProjectMaterials(route.params.id, {
      batchSize: 100,
      autoMatchThreshold: 0.75,
      enableHierarchicalMatching: true,
      basePriceDate: project.value?.base_price_date || null,
      basePriceProvince: provinceName,
      basePriceCity: cityName,
      basePriceDistrict: districtName
    }, { __skipLoading: true })

    console.log('材料匹配结果:', result)
    
    clearInterval(progressTimer)
    analysisState.progress = 100
    analysisState.currentStep = '匹配完成'

    // 刷新项目统计信息
    await fetchProjectStats()
    await fetchMaterials()

    // 显示匹配结果
    const stats = result.statistics
    ElMessage.success(`匹配完成！共匹配了 ${stats.matched_count} 个材料，${stats.unmatched_count} 个无信息价材料`)
    
  } catch (error) {
    if (error !== 'cancel') {
      console.error('分析失败:', error)
      ElMessage.error('分析失败: ' + (error.message || error.response?.data?.detail || '未知错误'))
    }
  } finally {
    // 延迟关闭进度条
    setTimeout(() => {
        analysisState.isIdentifying = false
    }, 2000)
  }
}

// AI价格分析 - 分析未匹配材料的价格
const startPriceAnalysis = async () => {
  console.log('开始AI价格分析流程 - 显示模型选择对话框')
  // 显示模型选择对话框
  showModelSelectDialog.value = true
}

// 确认开始AI价格分析（模型选择后）
const confirmStartPriceAnalysis = async () => {
  // 关闭模型选择对话框
  showModelSelectDialog.value = false
  
  const modelMap = {
    'dashscope': '通义千问',
    'doubao': '豆包',
    'deepseek': 'DeepSeek'
  }
  const modelName = modelMap[selectedAIModel.value] || selectedAIModel.value
  console.log('用户选择的AI模型:', modelName)
  
  try {
    // 获取基本信息
    const unmatched = (projectStats.value.total_materials || 0) - (projectStats.value.matched_materials || 0)
    const isReanalysis = hasAnalysisResults.value
    const actionText = isReanalysis ? '重新分析' : '开始分析'
    const titleText = isReanalysis ? '确认AI重新分析' : '确认AI价格分析'
    const messageText = isReanalysis 
      ? `确定要使用 ${modelName} 重新分析吗？系统将对${unmatched}个未匹配的材料重新进行网络搜索，覆盖现有的分析结果。这个过程可能需要一些时间。`
      : `确定要使用 ${modelName} 开始AI价格分析吗？系统将对${unmatched}个未匹配的材料进行网络搜索，获取市场合理价格并与项目价格对比分析。这个过程可能需要一些时间。`
    
    console.log('显示确认对话框')
    await ElMessageBox.confirm(messageText, titleText, {
      confirmButtonText: actionText,
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    console.log('用户确认开始分析')
    
    // 获取要分析的材料：改为针对整个项目的未匹配材料（跨页）
    const fetchAllUnmatched = async () => {
      const pageSize = 1000
      let page = 1
      const list = []
      while (true) {
        const resp = await getProjectMaterials(route.params.id, { page, size: pageSize })
        const items = resp?.items || resp?.data?.items || resp?.data || resp?.materials || resp || []
        const pageList = Array.isArray(items) ? items : (items.items || [])
        if (!pageList || pageList.length === 0) break
        pageList.filter(m => !m.is_matched || !m.matched_material_id).forEach(m => list.push(m))
        const total = resp?.total || resp?.data?.total
        if ((total && page * pageSize >= total) || pageList.length < pageSize) break
        page += 1
      }
      return list
    }

    const unmatchedMaterials = await fetchAllUnmatched()
    console.log('筛选出未匹配材料(全项目):', unmatchedMaterials.length, '个')
    
    if (unmatchedMaterials.length === 0) {
      ElMessage.warning('没有找到需要分析的无信息价材料')
      return
    }
    
    // 初始化分析状态
    analysisState.isAnalyzing = true
    analysisState.progress = 0
    analysisState.currentStep = '准备分析...'
    analysisState.completedSteps = 0
    analysisState.totalSteps = unmatchedMaterials.length
    analysisState.canViewResults = false
    analysisState.isBackgroundMode = false
    
    // 显示进度弹窗
    console.log('显示分析进度弹窗')
    showAnalysisProgressDialog.value = true
    console.log('进度弹窗已显示，全局loading应该被跳过')
    
    // 提取材料ID
    const materialIds = unmatchedMaterials.map(m => m.id)
    console.log('材料ID列表:', materialIds)
    
    // 使用平滑的预估进度，避免前期过快/后期卡顿
    const maxSimulatedProgress = 95
    const simulateDurationMs = Math.min(
      Math.max(unmatchedMaterials.length * 3000, 45000),
      240000
    )
    const progressStartAt = Date.now()
    const progressInterval = setInterval(() => {
      if (!analysisState.isAnalyzing) {
        clearInterval(progressInterval)
        return
      }

      const elapsed = Date.now() - progressStartAt
      const rawRatio = Math.min(elapsed / simulateDurationMs, 1)
      const easedRatio = 1 - Math.pow(1 - rawRatio, 2) // ease-out，前慢后快
      const simulated = 5 + easedRatio * (maxSimulatedProgress - 5)

      analysisState.progress = Math.min(simulated, maxSimulatedProgress)

      if (analysisState.totalSteps > 0) {
        const estimatedCompleted = Math.min(
          analysisState.totalSteps,
          Math.max(0, Math.round(easedRatio * analysisState.totalSteps))
        )
        analysisState.completedSteps = estimatedCompleted
        const currentMaterial = Math.min(
          analysisState.totalSteps,
          Math.max(estimatedCompleted + 1, 1)
        )
        analysisState.currentStep = estimatedCompleted >= analysisState.totalSteps
          ? '正在整理分析结果...'
          : `正在分析第 ${currentMaterial} 个材料...`
      } else {
        analysisState.currentStep = '正在准备分析数据...'
      }
    }, 1500)
    
    try {
      console.log('调用批量分析API')
      
      // 调用API - 使用用户选择的模型
      const apiData = {
        material_ids: materialIds,
        force_reanalyze: isReanalysis,
        batch_size: 5,
        preferred_provider: selectedAIModel.value
      }
      console.log('API请求参数:', apiData)
      
      // 禁用全局loading，因为我们有自己的进度弹窗
      console.log('即将调用AI分析API，配置skipLoading=true')
      const result = await batchAnalyzeMaterials(route.params.id, apiData, {
        __skipLoading: true // 跳过全局loading
      })
      console.log('API返回结果:', result)

      // 停止进度更新并完成
      clearInterval(progressInterval)
      analysisState.progress = 100
      analysisState.currentStep = '分析完成！'
      analysisState.completedSteps = analysisState.totalSteps
      analysisState.canViewResults = true
      
      console.log('分析完成，刷新数据')
      
      // 等待数据刷新完成
      try {
        await Promise.all([
          // 刷新项目统计数据
          getProjectStats(route.params.id, { __skipLoading: true }).then(response => {
            projectStats.value = response
            console.log('项目统计已刷新:', response)
          }).catch(err => console.warn('刷新统计失败:', err)),
          
          // 刷新材料列表数据
          getProjectMaterials(route.params.id, {
            page: pagination.page,
            size: pagination.size
          }, { __skipLoading: true }).then(response => {
            // 修复数据格式处理
            if (response && typeof response === 'object' && response.items && Array.isArray(response.items)) {
              materials.value = response.items
              pagination.total = response.total || 0
            } else {
              const result = response.data?.data || response.data || response
              if (Array.isArray(result)) {
                materials.value = result
                pagination.total = result.length
              } else {
                materials.value = result.items || result.materials || result.data || []
                pagination.total = result.total || result.count || materials.value.length
              }
            }
            console.log('材料列表已刷新:', materials.value.length, '条记录')
          }).catch(err => console.warn('刷新材料失败:', err))
        ])
        
        // 显示成功消息
        const count = result?.result?.success_count || result?.result?.analyzed_count || materialIds.length
        const successMsg = isReanalysis 
          ? `AI重新分析完成！成功重新分析了${count}个未匹配材料的市场价格`
          : `AI价格分析完成！成功分析了${count}个未匹配材料的市场价格`
        
        ElMessage.success(successMsg)
        console.log('分析成功完成')
        
        // 给用户一个倒计时提示，然后自动跳转
        let countdown = 3
        const countdownMsg = ElMessage.info({
          message: `分析完成！将在 ${countdown} 秒后自动跳转到分析结果页面...`,
          duration: 0, // 不自动关闭
          showClose: true
        })
        
        const countdownInterval = setInterval(() => {
          countdown--
          if (countdown > 0) {
            countdownMsg.message = `分析完成！将在 ${countdown} 秒后自动跳转到分析结果页面...`
          } else {
            clearInterval(countdownInterval)
            countdownMsg.close()
            
            console.log('准备自动跳转到分析结果页面')
            
            // 重置分析状态
            analysisState.isAnalyzing = false
            showAnalysisProgressDialog.value = false
            
            // 自动跳转到分析结果页面
            router.push(`/analysis/details?project_id=${route.params.id}&project_name=${encodeURIComponent(project.value.name)}`)
            
            console.log('已跳转到分析结果页面')
          }
        }, 1000)
        
      } catch (refreshError) {
        console.error('刷新数据时出错:', refreshError)
      }
      
    } catch (apiError) {
      clearInterval(progressInterval)
      console.error('API调用失败:', apiError)
      
      // 重置状态
      analysisState.isAnalyzing = false
      analysisState.progress = 0
      analysisState.currentStep = ''
      analysisState.canViewResults = false
      showAnalysisProgressDialog.value = false
      
      const errorMsg = apiError?.response?.data?.detail || apiError?.message || '分析失败，请稍后重试'
      ElMessage.error('AI价格分析失败: ' + errorMsg)
      throw apiError
    }
    
  } catch (error) {
    if (error === 'cancel') {
      console.log('用户取消分析')
    } else {
      console.error('分析流程出错:', error)
    }
  }
}

// AI市场信息价材料分析 - 对比项目材料与市场信息价材料库的价格差异
const startPricedMaterialAnalysis = async () => {
  console.log('开始AI市场信息价材料分析流程')
  
  try {
    // 获取基本信息
    const matched = projectStats.value.matched_materials || 0
    
    console.log('显示确认对话框')
    await ElMessageBox.confirm(
      `确定要开始AI市场信息价材料分析吗？系统将对比项目中${matched}个已匹配材料的价格与市场信息价材料库中的价格，分析存在差异的材料并计算单价差和合价差。这个过程可能需要一些时间。`,
      '确认AI市场信息价材料分析',
      {
        confirmButtonText: '开始分析',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    console.log('用户确认开始市场信息价材料分析')
    
    // 获取已匹配的材料
    const fetchAllMatched = async () => {
      const pageSize = 1000
      let page = 1
      const list = []
      while (true) {
        const resp = await getProjectMaterials(route.params.id, { page, size: pageSize })
        const items = resp?.items || resp?.data?.items || resp?.data || resp?.materials || resp || []
        const pageList = Array.isArray(items) ? items : (items.items || [])
        if (!pageList || pageList.length === 0) break
        pageList.filter(m => m.is_matched && m.matched_material_id).forEach(m => list.push(m))
        const total = resp?.total || resp?.data?.total
        if ((total && page * pageSize >= total) || pageList.length < pageSize) break
        page += 1
      }
      return list
    }

    const matchedMaterials = await fetchAllMatched()
    console.log('筛选出已匹配材料(全项目):', matchedMaterials.length, '个')
    
    if (matchedMaterials.length === 0) {
      ElMessage.warning('没有找到需要分析的市场信息价材料')
      return
    }
    
    // 初始化分析状态
    analysisState.isAnalyzing = true
    analysisState.progress = 0
    analysisState.currentStep = '准备市场信息价材料分析...'
    analysisState.completedSteps = 0
    analysisState.totalSteps = matchedMaterials.length
    analysisState.canViewResults = false
    analysisState.isBackgroundMode = false
    
    // 显示进度弹窗
    console.log('显示分析进度弹窗')
    showAnalysisProgressDialog.value = true
    
    // 提取材料ID
    const materialIds = matchedMaterials.map(m => m.id)
    console.log('市场信息价材料ID列表:', materialIds)
    
    // 市场信息价材料分析通常耗时较短，直接显示简易进度
    analysisState.progress = matchedMaterials.length > 1 ? 20 : 50
    analysisState.currentStep = '正在对比市场信息价材料...'

    try {
      console.log('调用市场信息价材料分析API')
      
      // 调用新的市场信息价材料分析API
      const { analyzePricedMaterials } = await import('@/api/analysis')
      
      const apiData = {
        material_ids: materialIds,
        batch_size: 10
      }
      console.log('API请求参数:', apiData)
      
      const result = await analyzePricedMaterials(route.params.id, apiData, {
        __skipLoading: true // 跳过全局loading
      })
      console.log('API返回结果:', result)
      
      // 完成进度
      analysisState.progress = 100
      analysisState.currentStep = '市场信息价材料分析完成！'
      analysisState.completedSteps = analysisState.totalSteps
      analysisState.canViewResults = true
      
      console.log('市场信息价材料分析完成，刷新数据')
      
      // 等待数据刷新完成
      try {
        await Promise.all([
          // 刷新项目统计数据
          getProjectStats(route.params.id, { __skipLoading: true }).then(response => {
            projectStats.value = response
            console.log('项目统计已刷新:', response)
          }).catch(err => console.warn('刷新统计失败:', err)),
          
          // 刷新材料列表数据
          getProjectMaterials(route.params.id, {
            page: pagination.page,
            size: pagination.size
          }, { __skipLoading: true }).then(response => {
            if (response && typeof response === 'object' && response.items && Array.isArray(response.items)) {
              materials.value = response.items
              pagination.total = response.total || 0
            } else {
              const result = response.data?.data || response.data || response
              if (Array.isArray(result)) {
                materials.value = result
                pagination.total = result.length
              } else {
                materials.value = result.items || result.materials || result.data || []
                pagination.total = result.total || result.count || materials.value.length
              }
            }
            console.log('材料列表已刷新:', materials.value.length, '条记录')
          }).catch(err => console.warn('刷新材料失败:', err))
        ])
        
        // 显示成功消息
        const count = result?.analyzed_count || result?.result?.analyzed_count || materialIds.length
        const diffCount = result?.differences_count || result?.result?.differences_count || 0
        const successMsg = `AI市场信息价材料分析完成！对比了${count}个市场信息价材料，发现${diffCount}个材料存在价格差异`

        console.log('市场信息价材料分析成功完成')

        // 收起进度弹窗
        analysisState.isAnalyzing = false
        showAnalysisProgressDialog.value = false

        ElMessage.success(successMsg)

        // 自动跳转到分析结果页面
        const jumpUrl = `/analysis/details?project_id=${route.params.id}&project_name=${encodeURIComponent(project.value.name)}&type=priced`
        console.log('跳转URL:', jumpUrl)
        router.push(jumpUrl)
        console.log('已跳转到市场信息价材料分析结果页面')

      } catch (refreshError) {
        console.error('刷新数据时出错:', refreshError)
      }
      
    } catch (apiError) {
      console.error('API调用失败:', apiError)
      
      // 重置状态
      analysisState.isAnalyzing = false
      analysisState.progress = 0
      analysisState.currentStep = ''
      analysisState.canViewResults = false
      showAnalysisProgressDialog.value = false
      
      const errorMsg = apiError?.response?.data?.detail || apiError?.message || '市场信息价材料分析失败，请稍后重试'
      ElMessage.error('AI市场信息价材料分析失败: ' + errorMsg)
      throw apiError
    }
    
  } catch (error) {
    if (error === 'cancel') {
      console.log('用户取消市场信息价材料分析')
    } else {
      console.error('市场信息价材料分析流程出错:', error)
    }
  }
}

// 分析进度弹窗 - 稍后查看（后台运行）
const runAnalysisInBackground = () => {
  analysisState.isBackgroundMode = true
  showAnalysisProgressDialog.value = false
  ElMessage.success('分析将在后台继续运行，完成后会通知您')
}

// 查看分析结果
const viewAnalysisResults = () => {
  // 关闭进度弹窗
  showAnalysisProgressDialog.value = false
  // 跳转到分析结果页面
  router.push(`/analysis/details?project_id=${route.params.id}&project_name=${encodeURIComponent(project.value.name)}`)
}

// 查看市场信息价材料分析结果
const viewPricedMaterialAnalysisResults = () => {
  // 跳转到统一的分析详情页面，并设置参数表明要显示市场信息价材料分析结果
  const jumpUrl = `/analysis/details?project_id=${route.params.id}&project_name=${encodeURIComponent(project.value.name)}&type=priced`
  console.log('跳转到市场信息价材料分析结果页面:', jumpUrl)
  router.push(jumpUrl)
}

const generateReport = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要生成价格报告吗？系统将根据已完成的价格分析结果生成详细的价格报告。生成过程可能需要几分钟时间，请耐心等待。',
      '确认生成报告',
      {
        confirmButtonText: '开始生成',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 显示开始生成的提示
    const loadingMessage = ElMessage({
      message: '正在生成价格报告，这可能需要几分钟时间，请不要关闭页面...',
      type: 'info',
      duration: 0, // 不自动关闭
      showClose: true
    })
    
    try {
      // 直接调用报告生成API
      const { generateReport: generateReportApi } = await import('@/api/reports')
      
      const response = await generateReportApi({
        project_id: parseInt(route.params.id),
        report_title: `${project.value.name} - 无信息价材料价格报告`,
        config: {
          report_type: 'comprehensive',
          include_charts: true,
          include_detailed_analysis: true,
          include_recommendations: true,
          include_appendices: true
        }
      })
      
      // 关闭loading消息
      loadingMessage.close()
      
      ElMessage.success(`报告生成成功！报告ID: ${response.report_id}`)
      
      // 跳转到报告列表页面
      router.push('/reports')
      
    } catch (apiError) {
      // 关闭loading消息
      loadingMessage.close()
      
      console.error('API调用失败:', apiError)
      
      // 更详细的错误处理
      let errorMsg = '报告生成失败'
      
      if (apiError.code === 'ECONNABORTED' || apiError.message?.includes('timeout')) {
        errorMsg = '报告生成超时，这通常是因为项目材料数量过多。请稍后重试或联系管理员。'
      } else if (apiError.response?.data?.detail) {
        errorMsg = apiError.response.data.detail
      } else if (apiError.message) {
        errorMsg = apiError.message
      }
      
      ElMessage.error({
        message: errorMsg,
        duration: 8000, // 错误消息显示更长时间
        showClose: true
      })
      
      throw apiError
    }
    
  } catch (error) {
    if (error !== 'cancel') {
      console.error('生成报告失败:', error)
    }
  }
}

const handleExportProject = async () => {
  try {
    ElMessage.info('正在生成导出文件...')
    
    // 调用后端导出接口，会直接下载文件
    await exportProject(route.params.id, 'comprehensive')
    
    ElMessage.success('项目数据导出成功')
  } catch (error) {
    ElMessage.error('导出失败: ' + (error.message || error.response?.data?.detail || '未知错误'))
    console.error('导出失败:', error)
  }
}

const viewMaterialDetail = (material) => {
  // 使用新的分析详情弹窗
  selectedMaterialId.value = material.id
  showAnalysisDetailDialog.value = true
}

// 处理分析详情弹窗关闭
const handleAnalysisDetailDialogClose = () => {
  showAnalysisDetailDialog.value = false
  selectedMaterialId.value = null
}

// 处理材料列表刷新
const handleMaterialRefresh = () => {
  fetchMaterials()
  fetchProjectStats()
}

// 删除项目材料
const deleteMaterial = async (material) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除材料 "${material.material_name}" 吗？删除后无法恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await deleteProjectMaterial(route.params.id, material.id)
    ElMessage.success('材料删除成功')
    
    // 刷新材料列表和统计
    await fetchMaterials()
    await fetchProjectStats()
    
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除材料失败:', error)
      ElMessage.error('删除材料失败: ' + (error.response?.data?.detail || error.message || '未知错误'))
    }
  }
}

// 批量删除材料
const batchDeleteMaterials = async () => {
  if (selectedCount.value === 0) {
    ElMessage.warning('请选择要删除的材料')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要删除已选择的 ${selectedCount.value} 个材料吗？删除后无法恢复。`,
      '批量删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 计算被选中的所有ID（跨页）
    const fetchAllIds = async () => {
      const pageSize = 1000
      let page = 1
      const ids = []
      // 根据当前标签过滤
      const filterByTab = (m) => {
        if (activeTab.value === 'matched') return m.is_matched && m.matched_material_id
        if (activeTab.value === 'unmatched') return !m.is_matched || !m.matched_material_id
        return true
      }
      while (true) {
        const resp = await getProjectMaterials(route.params.id, { page, size: pageSize })
        const items = resp?.items || resp?.data?.items || resp?.data || resp?.materials || resp || []
        const list = Array.isArray(items) ? items : (items.items || [])
        if (!list || list.length === 0) break
        list.filter(filterByTab).forEach(m => ids.push(m.id))
        const total = resp?.total || resp?.data?.total
        if ((total && page * pageSize >= total) || list.length < pageSize) break
        page += 1
      }
      return ids
    }

    const materialIds = await getSelectedIds(fetchAllIds)
    if (!materialIds || materialIds.length === 0) {
      ElMessage.warning('未获取到选中项')
      return
    }
    // 使用批量删除API
    await batchDeleteProjectMaterials(route.params.id, materialIds)
    ElMessage.success(`成功删除 ${materialIds.length} 个材料`)
    
    // 清空选择并刷新数据
    clearAllSelection()
    await nextTick()
    if (materialTableRef.value) materialTableRef.value.clearSelection()
    await fetchMaterials()
    await fetchProjectStats()
    
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除材料失败:', error)
      ElMessage.error('批量删除材料失败: ' + (error.response?.data?.detail || error.message || '未知错误'))
    }
  }
}

// 清空选择
const clearSelection = () => {
  clearAllSelection()
  if (materialTableRef.value) materialTableRef.value.clearSelection()
  selectedMaterials.value = []
}

const goToMaterialUpload = () => {
  router.push(`/projects/${route.params.id}/material-upload`)
}

// 打开编辑对话框
const openEditDialog = () => {
  if (project.value) {
    // 初始化编辑表单数据
    editForm.name = project.value.name || ''
    editForm.location = project.value.location || ''
    editForm.project_type = project.value.project_type || ''
    editForm.budget_amount = project.value.budget_amount || null
    editForm.base_price_date = project.value.base_price_date || ''
    editForm.base_price_province = project.value.base_price_province || ''
    editForm.base_price_city = project.value.base_price_city || ''
    editForm.base_price_district = project.value.base_price_district || ''
    editForm.support_price_adjustment = project.value.support_price_adjustment !== false
    editForm.price_adjustment_range = project.value.price_adjustment_range || 5.0
    editForm.audit_scope = project.value.audit_scope || []
  editForm.description = project.value.description || ''
  editForm.status = project.value.status || 'draft'
  editForm.contract_start_date = project.value.contract_start_date || project.value.contract_start || project.value.contract_start_month || ''
  editForm.contract_end_date = project.value.contract_end_date || project.value.contract_end || project.value.contract_end_month || ''

    showEditDialog.value = true
  }
}

// 处理项目更新
const handleUpdateProject = async () => {
  if (!editFormRef.value) return
  
  try {
    // 表单验证
    await editFormRef.value.validate()
    
    submitting.value = true
    
    // 调用更新API
    const data = {
      name: editForm.name,
      location: editForm.location || null,
      project_type: editForm.project_type,
      budget_amount: editForm.budget_amount || null,
      base_price_date: editForm.base_price_date || null,
      base_price_province: editForm.base_price_province || null,
      base_price_city: editForm.base_price_city || null,
      base_price_district: editForm.base_price_district || null,
      support_price_adjustment: editForm.support_price_adjustment,
      price_adjustment_range: editForm.price_adjustment_range || null,
      audit_scope: editForm.audit_scope || null,
      description: editForm.description || null,
      status: editForm.status,
      contract_start_date: editForm.contract_start_date || null,
      contract_end_date: editForm.contract_end_date || null
    }
    const fmt = (m) => {
      if (!m) return null
      const s = String(m)
      if (s.includes('-')) {
        const [y, mm] = s.split('-')
        return `${y}年${String(mm).padStart(2,'0')}月`
      }
      return null
    }
    const s1 = fmt(data.contract_start_date)
    const s2 = fmt(data.contract_end_date)
    if (s1 && s2) {
      const text = `合同工期：${s1}至${s2}`
      const has = data.description && /合同工期[:：]/.test(data.description)
      data.description = has ? data.description.replace(/合同工期[:：].*$/, text) : (data.description ? `${data.description}\n${text}` : text)
    }
    const response = await updateProject(route.params.id, data)
    
    ElMessage.success('项目更新成功')
    showEditDialog.value = false
    
    // 重新获取项目数据
    await fetchProject()
    
  } catch (error) {
    console.error('更新项目失败:', error)
    ElMessage.error('更新项目失败: ' + (error.response?.data?.detail || error.message || '未知错误'))
  } finally {
    submitting.value = false
  }
}

// 重新加载项目数据
const refreshProject = () => {
  project.value = null
  fetchProject()
  fetchProjectStats()
  fetchMaterials()
}

// 监听路由查询参数变化，自动刷新数据
watch(() => route.query, (newQuery, oldQuery) => {
  if (newQuery.refresh === 'materials' && newQuery.timestamp !== oldQuery?.timestamp) {
    console.log('检测到材料刷新请求，正在刷新材料列表...')
    fetchMaterials()
    fetchProjectStats()
    
    // 清除查询参数，避免重复刷新
    router.replace({
      path: route.path,
      query: {}
    })
    
    ElMessage.success('材料列表已刷新')
  }
}, { immediate: false, deep: true })

// 动态调整材料卡片高度以实现对齐
const adjustMaterialsCardHeight = () => {
  nextTick(() => {
    try {
      const infoCard = document.querySelector('.info-card')
      const actionsCard = document.querySelector('.actions-card')
      const materialsCard = document.querySelector('.materials-card')

      if (infoCard && actionsCard && materialsCard) {
        // 获取信息卡片的顶部位置
        const infoCardTop = infoCard.getBoundingClientRect().top
        // 获取操作卡片的底部位置
        const actionsCardBottom = actionsCard.getBoundingClientRect().bottom

        // 计算材料卡片应该的高度
        const targetHeight = actionsCardBottom - infoCardTop

        // 设置材料卡片的高度
        materialsCard.style.height = `${targetHeight}px`

        console.log('材料卡片高度已调整为:', targetHeight + 'px')
      }
    } catch (error) {
      console.warn('调整材料卡片高度时出错:', error)
    }
  })
}

// 监听窗口大小变化，重新调整对齐
const handleResize = () => {
  adjustMaterialsCardHeight()
}

// 生命周期
onMounted(() => {
  fetchProject()
  fetchProjectStats()
  fetchMaterials()

  // 初始对齐调整
  setTimeout(() => {
    adjustMaterialsCardHeight()
  }, 100)

  // 监听窗口大小变化
  window.addEventListener('resize', handleResize)
})

watch(activeTab, () => {
  pagination.page = 1
  fetchMaterials()
})

// 清理事件监听器
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style lang="scss" scoped>
.project-detail-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 20px;

  .header-content {
    .title-section {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 8px;

      .page-title {
        font-size: 24px;
        font-weight: 600;
        color: $text-primary;
        margin: 0;
      }

      .status-tag {
        font-size: 12px;
      }
    }

    .page-subtitle {
      font-size: 14px;
      color: $text-secondary;
      margin: 0;
      display: flex;
      align-items: center;
      gap: 4px;
    }
  }

  .header-actions {
    display: flex;
    gap: 12px;
  }
}

.stats-row {
  margin-bottom: 20px;
  display: flex;
  flex-wrap: wrap;

  :deep(.el-col) {
    display: flex;
  }

  .stat-card {
    flex: 1;
    width: 100%;
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

      &.materials {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      }

      &.analyzed {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
      }

      &.matched {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
      }

      &.progress {
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
      }
    }
  }
}

.content-row {
  // 确保左右列等高
  .el-col {
    display: flex;
    flex-direction: column;
  }

  // 左侧内容容器 - 自适应内容高度
  .left-content {
    display: flex;
    flex-direction: column;
    height: auto; // 改为自适应高度
    position: relative; // 添加相对定位作为参考
  }

  // 右侧列使用绝对定位实现精确对齐
  .el-col:last-child {
    position: relative;
  }

  .info-card,
  .actions-card {
    margin-bottom: 20px;

    .card-title {
      font-size: 16px;
      font-weight: 600;
      color: $text-primary;
    }
  }

  // 信息卡片完全展示内容，不折叠
  .info-card {
    flex-shrink: 0; // 不允许压缩
    height: auto; // 自适应内容高度
    min-height: auto; // 移除最小高度限制
    max-height: none; // 移除最大高度限制，完全展示
    overflow: visible; // 不使用滚动，完全显示内容
  }

  // 操作卡片完全展示内容，不折叠
  .actions-card {
    margin-bottom: 0;
    flex-shrink: 0; // 不允许压缩
    height: auto; // 自适应内容高度
    min-height: auto; // 移除最小高度限制

    :deep(.el-card__body) {
      height: auto;
      display: flex;
      flex-direction: column;
      padding: 20px; // 确保有足够的内边距
    }
  }

  // 材料卡片布局 - 与左侧卡片精确对齐
  .materials-card {
    display: flex;
    flex-direction: column;
    min-width: 0;
    // 使用JavaScript动态计算高度来实现精确对齐
    // 上边与info-card对齐，下边与actions-card对齐

    :deep(.el-card__body) {
      flex-grow: 1;
      display: flex;
      flex-direction: column;
      overflow: hidden; // 改为hidden避免多余滚动条
      min-width: 0;
      min-height: 600px;
      padding: 20px; // 确保合适的内边距
    }

    // 材料表格容器 - 占据大部分空间
    .table-container {
      flex-grow: 1;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      min-height: 0; // 重要：允许flex子元素收缩
    }

    // 确保材料表格能够充分利用空间
    .el-table {
      flex-grow: 1;
      overflow: auto; // 表格内部滚动
    }

    // 分页组件固定在底部
    .pagination-wrapper {
      flex-shrink: 0; // 不允许压缩
      margin-top: auto; // 推到底部
      padding-top: 16px;
      border-top: 1px solid #f0f0f0;
      background: white;
    }
  }

  .info-card {
    .info-list {
      .info-item {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid $border-color-lighter;

        &:last-child {
          border-bottom: none;
        }

        .label {
          font-size: 14px;
          color: $text-secondary;
          min-width: 80px;
        }

        .value {
          font-size: 14px;
          color: $text-primary;
          text-align: right;
          flex: 1;
        }
      }
    }

    .description {
      margin-top: 20px;
      padding-top: 16px;
      border-top: 1px solid $border-color-lighter;

      h4 {
        font-size: 14px;
        font-weight: 600;
        color: $text-primary;
        margin: 0 0 8px 0;
      }

      p {
        font-size: 14px;
        color: $text-regular;
        line-height: 1.5;
        margin: 0;
      }
    }
  }

  .actions-card {
    .action-buttons {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
  }

  .materials-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .card-title {
        font-size: 16px;
        font-weight: 600;
        color: $text-primary;
      }

      .header-actions {
        display: flex;
        align-items: center;
        gap: 12px;
      }
    }

    .search-filter-section {
      padding: 16px;
      background: #f8f9fa;
      border-radius: 8px;
      margin-bottom: 16px;

      .search-form {
        margin-bottom: 0;

        :deep(.el-form-item) {
          margin-bottom: 0;
          margin-right: 16px;

          &:last-child {
            margin-right: 0;
          }
        }

        :deep(.el-form-item__label) {
          font-size: 14px;
          color: #606266;
          font-weight: 500;
        }
      }
    }

    .batch-toolbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 16px;
      background-color: #f5f7fa;
      border-radius: 6px;
      margin-bottom: 16px;
      
      .selected-info {
        font-size: 14px;
        color: $text-secondary;
        font-weight: 500;
      }
      
      .batch-actions {
        display: flex;
        gap: 8px;
      }
    }

    .pagination-wrapper {
      display: flex;
      justify-content: center;
      align-items: center;
      width: 100%;
      min-height: 50px;
      flex-shrink: 0; // 不允许压缩
      margin-top: auto; // 推到底部
      padding-top: 16px;
      border-top: 1px solid #f0f0f0;
      background: white;

      :deep(.el-pagination) {
        width: 100%;
        justify-content: center;
      }
    }
  }
}


// 缩放自适应处理
@media (min-width: 1200px) {
  .content-row {
    .left-content {
      height: calc(100vh - 280px); // 大屏幕时减少顶部空间
    }
    .materials-card {
      height: calc(100vh - 280px);
    }
  }
}

@media (max-width: 1200px) and (min-width: 768px) {
  .content-row {
    .left-content {
      height: calc(100vh - 350px); // 中等屏幕时增加顶部空间
    }
    .materials-card {
      height: calc(100vh - 350px);
    }
    .info-card {
      min-height: 250px;
      max-height: 300px;
    }
  }
}

// 响应式设计
@media (max-width: $breakpoint-md) {
  .project-detail-container {
    padding: 10px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;

    .header-actions {
      width: 100%;
      justify-content: flex-start;
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

  .materials-card {
    .card-header {
      flex-direction: column;
      gap: 12px;
      align-items: flex-start;

      .header-actions {
        width: 100%;
        justify-content: space-between;
      }
    }

    .search-filter-section {
      padding: 12px;

      .search-form {
        :deep(.el-form-item) {
          display: block;
          width: 100%;
          margin-bottom: 12px;
          margin-right: 0;

          &:last-child {
            margin-bottom: 0;
          }

          .el-input,
          .el-select {
            width: 100%;
          }
        }
      }
    }
  }

  // 移动端取消固定高度，改为自适应
  .content-row {
    .left-content, .materials-card {
      height: auto;
      min-height: auto;
    }
    .info-card {
      min-height: auto;
      max-height: none;
    }
    .actions-card {
      min-height: auto;
    }
  }
}

// 匹配状态样式
.match-score {
  font-size: 11px;
  color: #666;
  margin-top: 2px;
}

// 快速操作按钮样式 - 使用深度选择器
.actions-card {
  .action-buttons {
    display: flex;
    flex-direction: column;
    gap: 12px;
    align-items: stretch; // 确保所有按钮拉伸到容器宽度

    :deep(.action-btn) {
    width: 100% !important;
    height: 44px !important;
    font-size: 14px !important;
    font-weight: 500;
    border-radius: 8px;
    transition: all 0.3s ease;
    margin: 0 !important;
    padding: 0 16px !important;
    box-sizing: border-box;
    
    // 上传材料清单按钮 - 蓝色渐变
    &.upload-btn {
      background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
      border-color: #3b82f6;
      color: white;
      
      &:hover:not(:disabled) {
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
        border-color: #1d4ed8;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
      }
    }

    // 无信息价材料识别按钮 - 紫色渐变
    &.identification-btn {
      background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
      border-color: #6366f1;
      color: white;
      
      &:hover:not(:disabled) {
        background: linear-gradient(135deg, #5855eb 0%, #7c3aed 100%);
        border-color: #5855eb;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
      }
    }
    
    // AI价格分析按钮 - 绿色渐变
    &.analysis-btn {
      background: linear-gradient(135deg, #10b981 0%, #059669 100%);
      border-color: #10b981;
      color: white;
      
      &:hover:not(:disabled) {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        border-color: #059669;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
      }
    }
    
    // AI市场信息价材料分析按钮 - 紫绿渐变
    &.priced-analysis-btn {
      background: linear-gradient(135deg, #8b5cf6 0%, #06b6d4 100%);
      border-color: #8b5cf6;
      color: white;
      
      &:hover:not(:disabled) {
        background: linear-gradient(135deg, #7c3aed 0%, #0891b2 100%);
        border-color: #7c3aed;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4);
      }
    }
    
    // 查看分析结果按钮 - 青色渐变
    &.view-results-btn {
      background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
      border-color: #06b6d4;
      color: white;
      
      &:hover:not(:disabled) {
        background: linear-gradient(135deg, #0891b2 0%, #0e7490 100%);
        border-color: #0891b2;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(6, 182, 212, 0.4);
      }
    }
    
    // 查看市场信息价分析结果按钮 - 蓝紫色渐变
    &.view-priced-results-btn {
      background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
      border-color: #6366f1;
      color: white;
      
      &:hover:not(:disabled) {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        border-color: #4f46e5;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
      }
    }
    
    // 生成价格报告按钮 - 橙色渐变
    &.report-btn {
      background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
      border-color: #f59e0b;
      color: white;
      
      &:hover:not(:disabled) {
        background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
        border-color: #d97706;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.4);
      }
    }
    
    // 确保所有按钮都有统一的基础样式
    &.el-button {
      border: 1px solid;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 500;
      
      // 禁用状态的统一样式
      &:disabled {
        background: #f3f4f6 !important;
        border-color: #d1d5db !important;
        color: #9ca3af !important;
        cursor: not-allowed;
        opacity: 0.6;
        transform: none !important;
        box-shadow: none !important;
      }
      
      // 确保图标和文字对齐
      .el-icon {
        margin-right: 6px;
      }
    }
    
    // 导出项目数据按钮 - 深蓝色渐变
    &.export-btn {
      background: linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%);
      border-color: #1e40af;
      color: white;
      
      &:hover:not(:disabled) {
        background: linear-gradient(135deg, #1e3a8a 0%, #1e3a8a 100%);
        border-color: #1e3a8a;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(30, 64, 175, 0.4);
      }
    }
    }
  }
}

// 分析进度相关样式
.analysis-button-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}

.analysis-progress {
  margin-top: 8px;
  padding: 12px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 13px;

  .progress-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
    
    .progress-text {
      color: #64748b;
      font-weight: 500;
    }
    
    .progress-percent {
      color: #10b981;
      font-weight: 600;
    }
  }

  .progress-detail {
    margin-top: 6px;
    color: #64748b;
    font-size: 12px;
    text-align: center;
  }

  :deep(.el-progress__text) {
    display: none !important;
  }
}

// 移动端适配
@media (max-width: 768px) {
  .analysis-progress {
    padding: 10px;
    font-size: 12px;
    
    .progress-info {
      .progress-text {
        font-size: 12px;
      }
      
      .progress-percent {
        font-size: 12px;
      }
    }
    
    .progress-detail {
      font-size: 11px;
    }
  }
}

// 分析进度弹窗样式
.analysis-progress-content {
  .progress-section {
    margin-bottom: 24px;
    
    .progress-info {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
      
      .progress-text {
        color: #374151;
        font-weight: 500;
        font-size: 14px;
      }
      
      .progress-percent {
        color: #059669;
        font-weight: 600;
        font-size: 14px;
      }
    }

    .progress-detail {
      margin-top: 8px;
      color: #6b7280;
      font-size: 12px;
      text-align: center;
    }
  }

  .analysis-tips {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 16px;
    background-color: #f0f9ff;
    border: 1px solid #bae6fd;
    border-radius: 8px;
    
    .tip-icon {
      color: #0ea5e9;
      font-size: 16px;
      margin-top: 2px;
      flex-shrink: 0;
    }
    
    .tip-content {
      flex: 1;
      
      p {
        margin: 0 0 8px 0;
        color: #374151;
        font-size: 13px;
        line-height: 1.5;
        
        &:last-child {
          margin-bottom: 0;
        }
      }
    }
  }
}

// 移动端分析进度弹窗
@media (max-width: 768px) {
  .analysis-progress-content {
    .progress-section {
      .progress-info {
        .progress-text {
          font-size: 13px;
        }
        
        .progress-percent {
          font-size: 13px;
        }
      }
      
      .progress-detail {
        font-size: 11px;
      }
    }
    
    .analysis-tips {
      padding: 12px;
      
      .tip-content p {
        font-size: 12px;
      }
    }
  }
}

// AI模型选择对话框样式
.model-select-content {
  padding: 0 20px;
  
  .model-select-hint {
    margin: 0 0 20px 0;
    font-size: 14px;
    color: #606266;
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
</style>
