<template>
  <div class="material-import-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">市场信息价导入</h1>
        <p class="page-subtitle">上传Excel文件，智能解析并导入市场信息价数据到材料库</p>
      </div>
      <div class="header-actions">
        <el-button @click="$router.back()">
          返回
        </el-button>
      </div>
    </div>

    <!-- 上传步骤 -->
    <el-card class="steps-card">
      <el-steps :active="currentStep" finish-status="success" align-center>
        <el-step title="上传文件" description="选择并上传Excel文件" />
        <el-step title="结构分析" description="分析文件结构和数据" />
        <el-step title="字段映射" description="映射数据字段" />
        <el-step title="数据预览" description="预览解析结果" />
        <el-step title="导入数据" description="确认并导入数据" />
      </el-steps>
    </el-card>

    <!-- 步骤内容 -->
    <el-card class="content-card">
      <!-- 步骤1: 文件上传 -->
      <div v-if="currentStep === 0" class="step-content">
        <!-- 信息价类型选择区域 -->
        <div class="price-type-section">
          <h3>信息价类型选择</h3>
          <p class="section-desc">请选择您要上传的信息价类型和期数</p>
          
          <div class="type-selection">
            <el-row :gutter="20">
              <el-col :span="24">
                <el-form-item label="信息价类型" required>
                  <div class="price-type-buttons">
                    <el-button
                      :type="priceTypeForm.priceType === 'provincial' ? 'primary' : 'default'"
                      :class="{ 'active': priceTypeForm.priceType === 'provincial' }"
                      class="price-type-btn"
                      @click="selectPriceType('provincial')"
                      size="large"
                    >
                      <el-icon class="btn-icon"><Document /></el-icon>
                      <span>省刊信息价</span>
                    </el-button>
                    
                    <el-button
                      :type="priceTypeForm.priceType === 'municipal' ? 'primary' : 'default'"
                      :class="{ 'active': priceTypeForm.priceType === 'municipal' }"
                      class="price-type-btn"
                      @click="selectPriceType('municipal')"
                      size="large"
                    >
                      <el-icon class="btn-icon"><Location /></el-icon>
                      <span>市刊信息价</span>
                    </el-button>
                  </div>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20" v-if="priceTypeForm.priceType">
              <el-col :span="8">
                <el-form-item 
                  :label="priceTypeForm.priceType === 'provincial' ? '选择省份' : '选择省份'" 
                  required
                >
                  <el-select 
                    v-model="priceTypeForm.province" 
                    placeholder="请选择省份"
                    style="width: 100%"
                    @change="onProvinceChange"
                    clearable
                  >
                    <el-option
                      v-for="province in provinceOptions"
                      :key="province.value"
                      :label="province.label"
                      :value="province.value"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
              
              <el-col :span="8" v-if="priceTypeForm.priceType === 'municipal'">
                <el-form-item label="选择城市" required>
                  <el-select 
                    v-model="priceTypeForm.city"
                    placeholder="请选择城市"
                    style="width: 100%"
                    :disabled="!priceTypeForm.province || currentCityOptions.length === 0"
                    clearable
                  >
                    <el-option
                      v-for="city in currentCityOptions"
                      :key="city.value"
                      :label="city.label"
                      :value="city.value"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
              
              <!-- 期数选择已移除，将在文件结构分析步骤中根据工作表名称自动识别 -->
            </el-row>
            
            <div class="selection-summary" v-if="isSelectionComplete">
              <el-alert
                :title="getSelectionSummary()"
                type="info"
                :closable="false"
                show-icon
              />
            </div>
          </div>
        </div>

        <el-divider />

        <div class="upload-section">
          <h3>上传Excel文件</h3>
          <p class="section-desc">支持 .xlsx、.xls、.csv 格式，文件大小不超过50MB</p>

          <el-upload
            ref="uploadRef"
            :file-list="fileList"
            :auto-upload="false"
            accept=".xlsx,.xls,.csv"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            :before-upload="beforeUpload"
            :on-exceed="handleExceed"
            :limit="1"
            drag
            class="upload-area"
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 Excel (.xlsx, .xls) 和 CSV 格式，单个文件不超过 50MB
              </div>
            </template>
          </el-upload>

          <!-- 文件信息预览 -->
          <div v-if="fileList.length > 0" class="file-info">
            <h4>已选择文件:</h4>
            <div class="file-item">
              <el-icon><Document /></el-icon>
              <span class="file-name">{{ fileList[0].name }}</span>
              <span class="file-size">{{ formatFileSize(fileList[0].size) }}</span>
            </div>
            <div class="file-actions">
              <el-button type="danger" :icon="Delete" @click="removeSelectedFile">删除文件</el-button>
            </div>
          </div>

          <!-- 模板下载 -->
          <div class="template-section">
            <el-divider>需要模板?</el-divider>
            <div class="template-actions">
              <el-button :icon="Download" @click="downloadTemplate" :loading="downloading">
                下载Excel模板
              </el-button>
              <el-button :icon="View" @click="showTemplatePreview = true">
                查看模板说明
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 步骤2: 结构分析 -->
      <div v-if="currentStep === 1" class="step-content">
        <div v-loading="analyzing" element-loading-text="正在分析文件结构...">
          <div class="analysis-section">
            <h3>文件结构分析</h3>
            <p class="section-desc">系统已自动分析您的Excel文件结构</p>

            <div v-if="analysisResult" class="analysis-result">
              <!-- 文件基本信息统计卡片 -->
              <div class="stats-cards">
                <div class="stats-card">
                  <div class="stats-title">工作表数量</div>
                  <div class="stats-value">{{ analysisResult.sheets?.length || 1 }}</div>
                </div>
                <div class="stats-card">
                  <div class="stats-title">数据行数</div>
                  <div class="stats-value">{{ analysisResult.totalRows || 0 }}</div>
                </div>
                <div class="stats-card">
                  <div class="stats-title">数据列数</div>
                  <div class="stats-value">{{ analysisResult.totalColumns || 0 }}</div>
                </div>
                <div class="stats-card">
                  <div class="stats-title">数据完整度</div>
                  <div class="stats-value">{{ (analysisResult.completeness || 0).toFixed(2) }}%</div>
                </div>
              </div>

              <!-- 工作表选择（多选） -->
              <div v-if="analysisResult.sheets.length > 1" class="sheet-selection">
                <h4>请选择要导入的工作表（可多选）:</h4>
                <div class="sheet-checkbox-group">
                  <el-checkbox-group v-model="selectedSheets">
                    <el-checkbox
                    v-for="sheet in analysisResult.sheets"
                    :key="sheet.name"
                    :label="sheet.name"
                      class="sheet-checkbox"
                    >
                      <div class="sheet-info">
                        <span class="sheet-name">{{ sheet.name }}</span>
                        <span class="sheet-period" v-if="getSheetPeriod(sheet.name)">
                          (期数: {{ getSheetPeriod(sheet.name) }})
                        </span>
                        <span class="sheet-stats">
                          ({{ analysisResult.totalRows || sheet.rows }}行, {{ sheet.columns }}列)
                        </span>
                      </div>
                    </el-checkbox>
                  </el-checkbox-group>
                </div>
                <el-alert
                  v-if="selectedSheets.length > 0"
                  :title="`已选择 ${selectedSheets.length} 个工作表，系统将根据工作表名称自动识别期数`"
                  type="info"
                  :closable="false"
                  show-icon
                  style="margin-top: 10px;"
                />
              </div>
              <!-- 单个工作表时自动选中 -->
              <div v-else-if="analysisResult.sheets.length === 1" class="sheet-selection">
                <h4>检测到单个工作表:</h4>
                <el-alert
                  :title="`工作表: ${analysisResult.sheets[0].name}${getSheetPeriod(analysisResult.sheets[0].name) ? ' (期数: ' + getSheetPeriod(analysisResult.sheets[0].name) + ')' : ''}`"
                  type="info"
                  :closable="false"
                  show-icon
                />
              </div>

              <!-- 表头检测信息 -->
              <div v-if="analysisResult.headerDetectionApplied" class="header-detection-info">
                <el-alert
                  :title="`智能表头检测: 已自动识别第${analysisResult.detectedHeaderRow + 1}行为列名`"
                  type="success"
                  :closable="false"
                  show-icon
                >
                  <template #default>
                    <span>系统自动分析了文件前10行，根据内容特征识别出第{{analysisResult.detectedHeaderRow + 1}}行最适合作为列名。</span>
                  </template>
                </el-alert>
              </div>

              <!-- 数据样本预览 -->
              <div class="sample-preview">
                <h4>数据样本预览 (前5行):</h4>
                <el-table
                  :data="analysisResult.sampleData"
                  stripe
                  border
                  style="width: 100%"
                  max-height="300"
                >
                  <el-table-column
                    v-for="(column, index) in analysisResult.columns"
                    :key="index"
                    :prop="`col_${index}`"
                    :label="`列${index + 1}: ${column}`"
                    show-overflow-tooltip
                  />
                </el-table>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 步骤3: 字段映射 -->
      <div v-if="currentStep === 2" class="step-content">
        <div class="mapping-section">
          <h3>字段映射配置</h3>
          <p class="section-desc">请将Excel文件的列映射到系统对应的字段</p>

          <div class="mapping-form">
            <el-row :gutter="20">
              <el-col :span="12">
                <div class="mapping-group">
                  <h4>必填字段</h4>
                  <el-form :model="fieldMapping" label-width="100px">
                    <el-form-item label="材料名称" required>
                      <el-select v-model="fieldMapping.name" placeholder="请选择">
                        <el-option
                          v-for="(column, index) in availableColumns"
                          :key="index"
                          :label="column"
                          :value="index"
                        />
                      </el-select>
                      <div class="field-preview">
                        {{ getFieldPreview('name') }}
                      </div>
                    </el-form-item>
                    
                    <el-form-item label="单位" required>
                      <el-select v-model="fieldMapping.unit" placeholder="请选择">
                        <el-option
                          v-for="(column, index) in availableColumns"
                          :key="index"
                          :label="column"
                          :value="index"
                        />
                      </el-select>
                      <div class="field-preview">
                        {{ getFieldPreview('unit') }}
                      </div>
                    </el-form-item>
                    
                    <el-form-item label="除税信息价" required>
                      <el-select v-model="fieldMapping.price_excluding_tax" placeholder="请选择">
                        <el-option
                          v-for="(column, index) in availableColumns"
                          :key="index"
                          :label="column"
                          :value="index"
                        />
                      </el-select>
                      <div class="field-preview">
                        {{ getFieldPreview('price_excluding_tax') }}
                      </div>
                    </el-form-item>
                    
                    <el-form-item label="含税信息价">
                      <el-select v-model="fieldMapping.price_including_tax" placeholder="请选择">
                        <el-option label="不映射" value="" />
                        <el-option
                          v-for="(column, index) in availableColumns"
                          :key="index"
                          :label="column"
                          :value="index"
                        />
                      </el-select>
                      <div class="field-preview">
                        {{ getFieldPreview('price_including_tax') }}
                      </div>
                    </el-form-item>
                  </el-form>
                </div>
              </el-col>

              <el-col :span="12">
                <div class="mapping-group">
                  <h4>可选字段</h4>
                  <el-form :model="fieldMapping" label-width="100px">
                    <el-form-item label="材料编码">
                      <el-select v-model="fieldMapping.material_code" placeholder="请选择">
                        <el-option label="不映射" value="" />
                        <el-option
                          v-for="(column, index) in availableColumns"
                          :key="index"
                          :label="column"
                          :value="index"
                        />
                      </el-select>
                      <div class="field-preview">
                        {{ getFieldPreview('material_code') }}
                      </div>
                    </el-form-item>
                    
                    <el-form-item label="规格型号">
                      <el-select v-model="fieldMapping.specification" placeholder="请选择">
                        <el-option label="不映射" value="" />
                        <el-option
                          v-for="(column, index) in availableColumns"
                          :key="index"
                          :label="column"
                          :value="index"
                        />
                      </el-select>
                      <div class="field-preview">
                        {{ getFieldPreview('specification') }}
                      </div>
                    </el-form-item>
                    
                    
                    <el-form-item label="适用地区">
                      <el-select v-model="fieldMapping.region" placeholder="请选择">
                        <el-option label="不映射" value="" />
                        <el-option
                          v-for="(column, index) in availableColumns"
                          :key="index"
                          :label="column"
                          :value="index"
                        />
                      </el-select>
                      <div class="field-preview">
                        {{ getFieldPreview('region') }}
                      </div>
                    </el-form-item>
                    
                    <el-form-item label="备注">
                      <el-select v-model="fieldMapping.remarks" placeholder="请选择">
                        <el-option label="不映射" value="" />
                        <el-option
                          v-for="(column, index) in availableColumns"
                          :key="index"
                          :label="column"
                          :value="index"
                        />
                      </el-select>
                      <div class="field-preview">
                        {{ getFieldPreview('remarks') }}
                      </div>
                    </el-form-item>
                  </el-form>
                </div>
              </el-col>
            </el-row>

            <!-- 智能映射建议 -->
            <div class="smart-mapping">
              <el-button type="primary" :icon="Tools" @click="autoMappingAndPreview">
                智能映射
              </el-button>
              <span class="mapping-tip">系统将根据列名自动匹配最可能的字段映射</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 步骤4: 数据预览 -->
      <div v-if="currentStep === 3" class="step-content">
        <div class="preview-section">
          <h3>数据预览</h3>
          <p class="section-desc">
            请确认解析后的数据是否正确，共 {{ fullDataStats.totalCount }} 条数据
            <span v-if="hasFullData && fullDataLength !== previewData.length" 
                  class="preview-note">
              （预览显示前 {{ previewData.length }} 条）
            </span>
          </p>

          <div class="preview-stats">
            <div class="stat-item">
              <span class="stat-label">有效数据:</span>
              <span class="stat-value success">{{ validDataCount }}</span>
              <span class="stat-note">（包含重复数据）</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">异常数据:</span>
              <span class="stat-value danger">{{ invalidDataCount }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">重复数据:</span>
              <span class="stat-value warning">{{ duplicateDataCount }}</span>
              <span class="stat-note">（{{ importOptions.skipDuplicate ? '导入时跳过' : '将保留' }}）</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">实际导入:</span>
              <span class="stat-value info">{{ getImportCount() }}</span>
              <span class="stat-note">（根据处理选项计算）</span>
            </div>
          </div>

          <!-- 数据筛选 -->
          <div class="preview-filters">
            <el-radio-group v-model="previewFilter">
              <el-radio-button label="all">全部数据</el-radio-button>
              <el-radio-button label="valid">有效数据</el-radio-button>
              <el-radio-button label="invalid">异常数据</el-radio-button>
              <el-radio-button label="duplicate">重复数据</el-radio-button>
            </el-radio-group>
          </div>

          <!-- 预览表格 -->
          <el-table
            :data="filteredPreviewData"
            stripe
            border
            style="width: 100%"
            max-height="500"
            :row-class-name="getRowClassName"
          >
            <el-table-column type="index" label="行号" width="60" />
            <el-table-column prop="material_code" label="材料编码" width="120" show-overflow-tooltip>
              <template #default="{ row }">
                <div v-if="isEditing(row)" class="editable-cell">
                  <el-input v-model="row.material_code" size="small" placeholder="编码" />
                </div>
                <span v-else>{{ row.material_code || '--' }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="name" label="材料名称" min-width="150" show-overflow-tooltip>
              <template #default="{ row }">
                <div v-if="isEditing(row)" class="editable-cell">
                  <el-input v-model="row.name" size="small" placeholder="材料名称" />
                </div>
                <span v-else :class="{ 'invalid-data': !row.valid && !row.name }">{{ row.name || '--' }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="specification" label="规格型号" width="120" show-overflow-tooltip>
              <template #default="{ row }">
                <div v-if="isEditing(row)" class="editable-cell">
                  <el-input v-model="row.specification" size="small" placeholder="规格" />
                </div>
                <span v-else>{{ row.specification || '--' }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="unit" label="单位" width="120">
              <template #default="{ row }">
                <div v-if="isEditing(row)" class="editable-cell">
                  <el-input v-model="row.unit" size="small" placeholder="单位" />
                </div>
                <span v-else :class="{ 'invalid-data': !row.valid && !row.unit }">{{ row.unit || '--' }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="price_excluding_tax" label="除税信息价" width="140">
              <template #default="{ row }">
                <div v-if="isEditing(row)" class="editable-cell">
                  <el-input-number 
                    v-model="row.price_excluding_tax" 
                    size="small" 
                    :precision="2" 
                    :min="0"
                    controls-position="right"
                    style="width: 100%"
                  />
                </div>
                <span v-else :class="{ 'invalid-data': !row.valid && (!row.price_excluding_tax || row.price_excluding_tax <= 0) }">
                  ¥{{ formatNumber(row.price_excluding_tax) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="price_including_tax" label="含税信息价" width="140">
              <template #default="{ row }">
                <div v-if="isEditing(row)" class="editable-cell">
                  <el-input-number 
                    v-model="row.price_including_tax" 
                    size="small" 
                    :precision="2" 
                    :min="0"
                    controls-position="right"
                    style="width: 100%"
                  />
                </div>
                <span v-else>
                  <span v-if="row.price_including_tax" :class="{ 'invalid-data': !row.valid }">
                    ¥{{ formatNumber(row.price_including_tax) }}
                  </span>
                  <span v-else class="no-data">--</span>
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="region" label="地区" width="120" show-overflow-tooltip>
              <template #default="{ row }">
                <div v-if="isEditing(row)" class="editable-cell">
                  <el-input v-model="row.region" size="small" placeholder="地区" />
                </div>
                <span v-else>{{ row.region || '--' }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="remarks" label="备注" width="150" show-overflow-tooltip>
              <template #default="{ row }">
                <div v-if="isEditing(row)" class="editable-cell">
                  <el-input v-model="row.remarks" size="small" placeholder="备注" />
                </div>
                <span v-else>{{ row.remarks || '--' }}</span>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag v-if="row.duplicate" type="warning" size="small">重复</el-tag>
                <el-tag v-else-if="row.valid" type="success" size="small">正常</el-tag>
                <el-tag v-else-if="row.isFirstInGroup" type="info" size="small">原始</el-tag>
                <el-tag v-else type="danger" size="small">异常</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="问题" width="200" show-overflow-tooltip>
              <template #default="{ row }">
                <span v-if="row.errors && row.errors.length > 0" class="error-text">
                  {{ row.errors.join(', ') }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180" fixed="right" v-if="previewFilter === 'invalid'">
              <template #default="{ row }">
                <div v-if="!row.valid && !row.duplicate" class="action-buttons">
                  <el-button
                    v-if="!isEditing(row)"
                    type="primary"
                    size="small"
                    :icon="Edit"
                    @click="startEditing(row)"
                  >
                    编辑
                  </el-button>
                  <template v-else>
                    <el-button
                      type="success"
                      size="small"
                      :icon="Check"
                      @click="saveEditing(row)"
                    >
                      保存
                    </el-button>
                    <el-button
                      size="small"
                      :icon="Close"
                      @click="cancelEditing(row)"
                    >
                      取消
                    </el-button>
                  </template>
                </div>
              </template>
            </el-table-column>
          </el-table>

          <!-- 数据处理选项 -->
          <div class="data-options">
            <h4>数据处理选项:</h4>
            <el-checkbox v-model="importOptions.skipInvalid">跳过异常数据</el-checkbox>
            <el-checkbox v-model="importOptions.skipDuplicate">跳过重复数据</el-checkbox>
            <el-checkbox v-model="importOptions.autoFix">自动修复可修复的数据</el-checkbox>
            
            <!-- 批量导入配置 -->
            <div v-if="getImportCount() > 1000" class="batch-import-config">
              <h5>批量导入配置:</h5>
              <p class="batch-info">
                <el-icon class="info-icon"><InfoFilled /></el-icon>
                检测到大数据量({{ getImportCount() }}条)，将启用分批导入以确保稳定性
              </p>
              <el-form-item label="每批数量:">
                <el-input-number 
                  v-model="importOptions.batchSize" 
                  :min="100" 
                  :max="2000" 
                  :step="100"
                  controls-position="right"
                  style="width: 180px"
                />
                <span class="batch-tip">
                  将分 {{ Math.ceil(getImportCount() / importOptions.batchSize) }} 批处理
                </span>
              </el-form-item>
            </div>
          </div>
        </div>
      </div>

      <!-- 步骤5: 导入数据 -->
      <div v-if="currentStep === 4" class="step-content">
        <div v-if="importing" class="importing-section">
          <div class="importing-progress">
            <el-icon class="loading-icon"><Loading /></el-icon>
            <h3>正在导入数据...</h3>
            <p>{{ importProgress.message }}</p>
            <el-progress
              :percentage="importProgress.percentage"
              :stroke-width="8"
              status="success"
            />
            <div class="progress-stats">
              <span>已处理: {{ importProgress.processed }}</span>
              <span>成功: {{ importProgress.success }}</span>
              <span>失败: {{ importProgress.failed }}</span>
            </div>
          </div>
        </div>

        <div v-else class="import-result">
          <el-result
            :icon="importResult.success ? 'success' : 'error'"
            :title="importResult.title"
            :sub-title="importResult.message"
          >
            <template #extra>
              <div v-if="importResult.success" class="result-details">
                <div class="result-stats">
                  <div class="stat-card">
                    <div class="stat-number">{{ importResult.totalCount }}</div>
                    <div class="stat-label">总数据量</div>
                  </div>
                  <div class="stat-card success">
                    <div class="stat-number">{{ importResult.successCount }}</div>
                    <div class="stat-label">成功导入</div>
                  </div>
                  <div class="stat-card danger" :class="{ 'clickable': importResult.failedCount > 0 && importResult.errors && importResult.errors.length > 0 }" @click="showErrorDetails">
                    <div class="stat-number">{{ importResult.failedCount }}</div>
                    <div class="stat-label">导入失败</div>
                    <div v-if="importResult.failedCount > 0 && importResult.errors && importResult.errors.length > 0" class="stat-hint">
                      点击查看详情
                    </div>
                  </div>
                </div>

                <!-- 导入报告下载 -->
                <div class="import-report">
                  <el-button :icon="Download" @click="downloadImportReport">
                    下载导入报告
                  </el-button>
                </div>
              </div>

              <div class="action-buttons">
                <el-button @click="resetProcess">重新导入</el-button>
                <el-button type="primary" @click="goToMaterials">
                  查看材料库
                </el-button>
              </div>
            </template>
          </el-result>
        </div>
      </div>
    </el-card>

    <!-- 操作按钮 -->
    <div class="action-footer">
      <el-button v-if="currentStep > 0 && currentStep < 4" @click="prevStep">
        上一步
      </el-button>
      <el-button
        v-if="currentStep < 3"
        type="primary"
        :disabled="!canNext"
        @click="nextStep"
      >
        下一步
      </el-button>
      <el-button
        v-if="currentStep === 3"
        type="primary"
        :disabled="validDataCount === 0"
        @click="startImport"
      >
        开始导入 ({{ getImportCount() }} 条)
      </el-button>
    </div>

    <!-- 错误详情对话框 -->
    <el-dialog v-model="showErrorDialog" title="导入错误详情" width="800px">
      <div class="error-details">
        <el-alert
          type="error"
          :closable="false"
          show-icon
          style="margin-bottom: 20px;"
        >
          <template #title>
            共发现 {{ importResult.errors?.length || 0 }} 条错误信息
          </template>
        </el-alert>
        
        <div class="error-list">
          <el-scrollbar max-height="400px">
            <div
              v-for="(error, index) in importResult.errors"
              :key="index"
              class="error-item"
            >
              <el-icon class="error-icon"><WarningFilled /></el-icon>
              <span class="error-text">{{ error }}</span>
            </div>
          </el-scrollbar>
        </div>
        
        <div v-if="!importResult.errors || importResult.errors.length === 0" class="no-errors">
          <el-empty description="暂无详细错误信息" />
        </div>
      </div>
      
      <template #footer>
        <el-button @click="showErrorDialog = false">关闭</el-button>
        <el-button type="primary" @click="downloadErrorReport" v-if="importResult.errors && importResult.errors.length > 0">
          导出错误报告
        </el-button>
      </template>
    </el-dialog>

    <!-- 模板预览对话框 -->
    <el-dialog v-model="showTemplatePreview" title="Excel模板说明" width="800px">
      <div class="template-preview">
        <h3>标准Excel模板格式说明</h3>
        <p>请按照以下格式准备您的Excel文件:</p>
        
        <h4>必填字段 (A-C列):</h4>
        <ul>
          <li><strong>A列 - 材料名称:</strong> 材料的标准名称，不能为空</li>
          <li><strong>B列 - 单位:</strong> 材料的计量单位，如：吨、立方米、平方米等</li>
          <li><strong>C列 - 价格:</strong> 材料的参考价格，仅输入数字，不要包含货币符号</li>
        </ul>
        
        <h4>可选字段 (D-H列):</h4>
        <ul>
          <li><strong>D列 - 材料编码:</strong> 材料的编码或代码，可为空</li>
          <li><strong>E列 - 规格型号:</strong> 材料的具体规格，可为空</li>
          <li><strong>F列 - 材料分类:</strong> 如：建筑材料、装修材料等</li>
          <li><strong>G列 - 适用地区:</strong> 如：北京、上海、全国等</li>
          <li><strong>H列 - 备注:</strong> 其他说明信息</li>
        </ul>
        
        <h4>注意事项:</h4>
        <ul>
          <li>第一行请设置为表头，系统会自动识别</li>
          <li>价格字段请只输入数字，不要包含文字和符号</li>
          <li>请确保数据的完整性和准确性</li>
          <li>支持多个工作表，系统会让您选择要导入的工作表</li>
        </ul>

        <div class="template-example">
          <h4>示例数据:</h4>
          <el-table :data="templateExample" border style="width: 100%">
            <el-table-column prop="code" label="材料编码" />
            <el-table-column prop="name" label="材料名称" />
            <el-table-column prop="unit" label="单位" />
            <el-table-column prop="price" label="价格" />
            <el-table-column prop="spec" label="规格型号" />
            <el-table-column prop="category" label="分类" />
            <el-table-column prop="region" label="地区" />
            <el-table-column prop="remark" label="备注" />
          </el-table>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
console.log('🚀 市场信息价导入页面加载成功! v1.0')
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  UploadFilled,
  Download,
  View,
  Document,
  Tools,
  Loading,
  Location,
  InfoFilled,
  WarningFilled,
  Delete,
  Edit,
  Check,
  Close
} from '@element-plus/icons-vue'
import { formatNumber } from '@/utils'
// 使用基准材料的API函数
import { 
  parseExcelStructure, 
  getPreviewData, 
  importBaseMaterials,
  downloadBaseMaterialTemplate 
} from '@/api/materials'

const route = useRoute()
const router = useRouter()

// 响应式数据
const currentStep = ref(0)
const analyzing = ref(false)
const importing = ref(false)
const downloading = ref(false)
const showTemplatePreview = ref(false)
const showErrorDialog = ref(false)
const uploadRef = ref()

const fileList = ref([])
const analysisResult = ref(null)
const selectedSheet = ref('') // 保留用于兼容单工作表场景
const selectedSheets = ref([]) // 多工作表选择
const availableColumns = ref([])
const previewData = ref([])
const previewFilter = ref('all')
// 完整导入数据的响应式管理
const fullImportData = ref([])
const hasFullData = computed(() => fullImportData.value.length > 0)

// 编辑相关状态
const editingRows = ref(new Set()) // 正在编辑的行索引集合
const originalRowData = ref(new Map()) // 保存编辑前的原始数据

// 信息价类型选择表单
const priceTypeForm = reactive({
  priceType: '', // 'provincial' | 'municipal'
  priceDate: '', // YYYY-MM 格式
  region: '', // 地区信息，后续可扩展
  province: '', // 选择的省份
  city: '' // 选择的城市
})

// 省份和城市数据
const provinceOptions = ref([
  { value: 'beijing', label: '北京市' },
  { value: 'shanghai', label: '上海市' },
  { value: 'guangdong', label: '广东省' },
  { value: 'zhejiang', label: '浙江省' },
  { value: 'jiangsu', label: '江苏省' },
  { value: 'shandong', label: '山东省' },
  { value: 'sichuan', label: '四川省' },
  { value: 'hubei', label: '湖北省' },
  { value: 'hunan', label: '湖南省' },
  { value: 'henan', label: '河南省' },
  { value: 'hebei', label: '河北省' },
  { value: 'shanxi', label: '山西省' },
  { value: 'liaoning', label: '辽宁省' },
  { value: 'jilin', label: '吉林省' },
  { value: 'heilongjiang', label: '黑龙江省' },
  { value: 'anhui', label: '安徽省' },
  { value: 'fujian', label: '福建省' },
  { value: 'jiangxi', label: '江西省' },
  { value: 'guangxi', label: '广西壮族自治区' },
  { value: 'hainan', label: '海南省' },
  { value: 'chongqing', label: '重庆市' },
  { value: 'yunnan', label: '云南省' },
  { value: 'guizhou', label: '贵州省' },
  { value: 'tibet', label: '西藏自治区' },
  { value: 'shaanxi', label: '陕西省' },
  { value: 'gansu', label: '甘肃省' },
  { value: 'qinghai', label: '青海省' },
  { value: 'ningxia', label: '宁夏回族自治区' },
  { value: 'xinjiang', label: '新疆维吾尔自治区' },
  { value: 'tianjin', label: '天津市' },
  { value: 'neimenggu', label: '内蒙古自治区' }
])

const cityOptionsMap = reactive({
  guangdong: [
    { value: 'guangzhou', label: '广州市' },
    { value: 'shenzhen', label: '深圳市' },
    { value: 'dongguan', label: '东莞市' },
    { value: 'foshan', label: '佛山市' },
    { value: 'huizhou', label: '惠州市' },
    { value: 'zhongshan', label: '中山市' },
    { value: 'zhuhai', label: '珠海市' },
    { value: 'jiangmen', label: '江门市' }
  ],
  zhejiang: [
    { value: 'hangzhou', label: '杭州市' },
    { value: 'ningbo', label: '宁波市' },
    { value: 'wenzhou', label: '温州市' },
    { value: 'shaoxing', label: '绍兴市' },
    { value: 'jiaxing', label: '嘉兴市' },
    { value: 'huzhou', label: '湖州市' },
    { value: 'jinhua', label: '金华市' }
  ],
  jiangsu: [
    { value: 'nanjing', label: '南京市' },
    { value: 'suzhou', label: '苏州市' },
    { value: 'wuxi', label: '无锡市' },
    { value: 'changzhou', label: '常州市' },
    { value: 'nantong', label: '南通市' },
    { value: 'yangzhou', label: '扬州市' },
    { value: 'xuzhou', label: '徐州市' }
  ],
  shandong: [
    { value: 'jinan', label: '济南市' },
    { value: 'qingdao', label: '青岛市' },
    { value: 'yantai', label: '烟台市' },
    { value: 'weifang', label: '潍坊市' },
    { value: 'zibo', label: '淄博市' },
    { value: 'jining', label: '济宁市' }
  ],
  // 可以继续添加更多省份的城市
})

// 根据选择的省份获取城市列表
const currentCityOptions = computed(() => {
  if (priceTypeForm.priceType === 'municipal' && priceTypeForm.province) {
    return cityOptionsMap[priceTypeForm.province] || []
  }
  return []
})

// 检查选择是否完整
// 从工作表名称提取期数（支持多种格式：2025-01, 2025年01月, 202501等）
const getSheetPeriod = (sheetName) => {
  if (!sheetName) return null
  
  // 尝试匹配 YYYY-MM 格式（如：2025-01）
  const match1 = sheetName.match(/(\d{4})-(\d{1,2})/)
  if (match1) {
    const year = match1[1]
    const month = match1[2].padStart(2, '0')
    return `${year}-${month}`
  }
  
  // 尝试匹配 YYYY年MM月 格式（如：2025年01月）
  const match2 = sheetName.match(/(\d{4})年(\d{1,2})月/)
  if (match2) {
    const year = match2[1]
    const month = match2[2].padStart(2, '0')
    return `${year}-${month}`
  }
  
  // 尝试匹配 YYYYMM 格式（如：202501）
  const match3 = sheetName.match(/(\d{4})(\d{2})/)
  if (match3 && match3[1] >= '2000' && match3[1] <= '2099' && match3[2] >= '01' && match3[2] <= '12') {
    return `${match3[1]}-${match3[2]}`
  }
  
  return null
}

const isSelectionComplete = computed(() => {
  if (!priceTypeForm.priceType || !priceTypeForm.province) {
    return false
  }
  
  // 如果是市刊信息价，还需要选择城市
  if (priceTypeForm.priceType === 'municipal') {
    return !!priceTypeForm.city
  }
  
  // 期数不再需要在这里选择，将从工作表名称自动识别
  return true
})

// 获取选择摘要文本
const getSelectionSummary = () => {
  const typeText = priceTypeForm.priceType === 'provincial' ? '省刊信息价' : '市刊信息价'
  const provinceName = provinceOptions.value.find(p => p.value === priceTypeForm.province)?.label || ''
  
  let regionText = provinceName
  if (priceTypeForm.priceType === 'municipal' && priceTypeForm.city) {
    const cityName = currentCityOptions.value.find(c => c.value === priceTypeForm.city)?.label || ''
    regionText = `${provinceName} - ${cityName}`
  }
  
  // 期数将在文件结构分析步骤中根据工作表名称自动识别
  return `已选择: ${typeText} - ${regionText}（期数将从工作表名称自动识别）`
}

// 字段映射配置 - 适配基准材料字段
const fieldMapping = reactive({
  material_code: '',
  name: '',
  specification: '',
  unit: '',
  price_excluding_tax: '', // 除税信息价
  price_including_tax: '', // 含税信息价
  region: '',
  remarks: ''
})

// 导入选项
const importOptions = reactive({
  skipInvalid: true,
  skipDuplicate: true,
  autoFix: true,
  batchSize: 1000 // 默认每批1000条
})

// 导入进度
const importProgress = reactive({
  percentage: 0,
  message: '准备导入...',
  processed: 0,
  success: 0,
  failed: 0
})

// 导入结果
const importResult = reactive({
  success: false,
  title: '',
  message: '',
  totalCount: 0,
  successCount: 0,
  failedCount: 0,
  skippedCount: 0
})

// 模板示例数据 - 适配基准材料
const templateExample = ref([
  {
    code: 'BM001',
    name: '普通硅酸盐水泥',
    unit: '吨',
    price: 580.00,
    spec: 'P.O 42.5',
    category: '建筑材料',
    region: '北京',
    remark: '标准水泥'
  },
  {
    code: 'BM002',
    name: '热轧带肋钢筋',
    unit: '吨',
    price: 4200.00,
    spec: 'HRB400 Φ12',
    category: '建筑材料',
    region: '全国',
    remark: '三级钢筋'
  }
])

// 计算属性
const canNext = computed(() => {
  switch (currentStep.value) {
    case 0:
      return isSelectionComplete.value && fileList.value.length > 0
    case 1:
      return analysisResult.value !== null
    case 2:
      return fieldMapping.name !== '' && fieldMapping.unit !== '' && fieldMapping.price_excluding_tax !== ''
    case 3:
      return previewData.value.length > 0
    default:
      return false
  }
})

// 缓存完整数据的统计结果
const fullDataStats = ref({
  validCount: 0,
  invalidCount: 0,
  duplicateCount: 0,
  totalCount: 0,
  processedItems: []
})

// 基于完整数据计算统计信息
const calculateFullDataStats = () => {
  let sourceData = hasFullData.value ? fullImportData.value : previewData.value
  
  let validCount = 0
  let invalidCount = 0
  let duplicateCount = 0
  let processedItems = []
  
  // 第一步：收集所有数据并检测重复项
  const duplicateCheck = new Map()
  const itemsWithKeys = []
  
  // 遍历所有数据，生成唯一键
  for (let i = 0; i < sourceData.length; i++) {
    const row = sourceData[i]
    
    // 根据字段映射提取数据
    const getValue = (fieldName) => {
      const columnIndex = fieldMapping[fieldName]
      if (columnIndex === '' || columnIndex === undefined) return ''
      
      if (row.data && availableColumns.value[columnIndex]) {
        const mappedValue = row.data[availableColumns.value[columnIndex]]
        if (mappedValue !== undefined && mappedValue !== null && String(mappedValue).trim() !== '') {
          return mappedValue
        }
      }
      
      const fallbackValue = row[`col_${columnIndex}`]
      if (fallbackValue !== undefined && fallbackValue !== null && String(fallbackValue).trim() !== '') {
        return fallbackValue
      }
      
      return ''
    }
    
    const name = getValue('name') || ''
    const unit = getValue('unit') || ''
    const price_excluding_tax = parseFloat(getValue('price_excluding_tax')) || 0
    const specification = getValue('specification') || ''
    
    // 验证数据有效性
    const isValid = name.trim() !== '' && unit.trim() !== '' && price_excluding_tax > 0 && !isNaN(price_excluding_tax)
    
    // 生成重复检测键（基于材料编码 + 材料名称 + 规格型号 + 备注 + 地区 + 期数的组合）
    const materialCode = getValue('material_code') || ''
    const notes = getValue('verification_notes') || ''
    const region = getValue('region') || ''
    const period = row._period || getSheetPeriod(row._sheetName) || ''
    const duplicateKey = `${materialCode.trim()}_${name.trim()}_${specification.trim()}_${notes.trim()}_${region.trim()}_${period.trim()}`.toLowerCase()
    
    const itemData = {
      index: i,
      duplicateKey,
      isValid,
      name,
      specification,
      unit,
      price_excluding_tax
    }
    
    itemsWithKeys.push(itemData)
    
    // 统计重复键出现次数
    if (name.trim()) {
      duplicateCheck.set(duplicateKey, (duplicateCheck.get(duplicateKey) || 0) + 1)
    }
  }
  
  // 第二步：标记重复项（保留每组的第一个，标记后续为重复）
  const seenKeys = new Set()
  
  for (let i = 0; i < itemsWithKeys.length; i++) {
    const item = itemsWithKeys[i]
    const hasMultiple = item.name.trim() && duplicateCheck.get(item.duplicateKey) > 1
    const isFirstOccurrence = !seenKeys.has(item.duplicateKey)
    
    // 只有非首次出现且属于多重组的项才标记为重复
    const isDuplicate = hasMultiple && !isFirstOccurrence
    
    if (item.name.trim()) {
      seenKeys.add(item.duplicateKey)
    }
    
    // 统计分类：重复数据也算有效数据
    if (item.isValid) {
      validCount++  // 有效数据包含重复数据
    } else {
      invalidCount++
    }
    
    // 重复数据单独统计（但仍算在有效数据内）
    if (isDuplicate) {
      duplicateCount++
    }
    
    // 同时更新原始数据的标记
    if (sourceData[item.index]) {
      sourceData[item.index].belongsToDuplicateGroup = hasMultiple
      sourceData[item.index].isFirstInGroup = isFirstOccurrence && hasMultiple
      sourceData[item.index].duplicateKey = item.duplicateKey
    }
    
    processedItems.push({
      valid: item.isValid && !isDuplicate,
      duplicate: isDuplicate,
      invalid: !item.isValid && !isDuplicate,
      belongsToDuplicateGroup: hasMultiple,
      isFirstInGroup: isFirstOccurrence && hasMultiple
    })
  }
  
  fullDataStats.value = {
    validCount,
    invalidCount, 
    duplicateCount,
    totalCount: sourceData.length,
    processedItems
  }
}

const validDataCount = computed(() => {
  return fullDataStats.value.validCount
})

const invalidDataCount = computed(() => {
  return fullDataStats.value.invalidCount
})

const duplicateDataCount = computed(() => {
  return fullDataStats.value.duplicateCount
})

// 完整数据长度
const fullDataLength = computed(() => {
  return fullImportData.value.length
})

// 处理完整数据，应用字段映射和验证逻辑
const processFullDataWithMapping = (sourceData) => {
  const duplicateCheck = new Map()
  const tempMappedData = []
  
  // 先收集所有数据，统计重复键
  for (let i = 0; i < sourceData.length; i++) {
    const row = sourceData[i]
    
    // 根据字段映射提取数据
    const getValue = (fieldName) => {
      const columnIndex = fieldMapping[fieldName]
      if (columnIndex === '' || columnIndex === undefined) return ''
      
      if (row.data && availableColumns.value[columnIndex]) {
        const mappedValue = row.data[availableColumns.value[columnIndex]]
        if (mappedValue !== undefined && mappedValue !== null && String(mappedValue).trim() !== '') {
          return mappedValue
        }
      }
      
      const fallbackValue = row[`col_${columnIndex}`]
      if (fallbackValue !== undefined && fallbackValue !== null && String(fallbackValue).trim() !== '') {
        return fallbackValue
      }
      
      return ''
    }
      
    const name = getValue('name') || ''
    const specification = getValue('specification') || ''
    const unit = getValue('unit') || ''
    const price_excluding_tax = parseFloat(getValue('price_excluding_tax')) || 0
    const price_including_tax = parseFloat(getValue('price_including_tax')) || 0
    
    const item = {
      row_index: i,
      material_code: getValue('material_code') || '',
      name: name,
      specification: specification,
      unit: unit,
      price_excluding_tax: price_excluding_tax,
      price_including_tax: price_including_tax,
      region: getValue('region') || '',
      remarks: getValue('remarks') || '',
      valid: true,
      duplicate: false,
      errors: []
    }
    
    // 生成重复检测键（材料编码 + 材料名称 + 规格型号 + 备注 + 地区 + 期数，六个字段确定唯一性）
    const materialCode = getValue('material_code') || '' // 材料编码
    const notes = getValue('verification_notes') || '' // 备注
    const region = getValue('region') || '' // 地区
    const period = row._period || getSheetPeriod(row._sheetName) || '' // 期数
    const duplicateKey = `${materialCode.trim()}_${name.trim()}_${specification.trim()}_${notes.trim()}_${region.trim()}_${period.trim()}`.toLowerCase()
    item.duplicateKey = duplicateKey
    item._period = period // 保存期数信息
    item._sheetName = row._sheetName || '' // 保存工作表名称
    
    // 统计重复键出现次数
    if (name.trim()) {
      duplicateCheck.set(duplicateKey, (duplicateCheck.get(duplicateKey) || 0) + 1)
    }
    
    tempMappedData.push(item)
  }
  
  // 第二步：基于重复检测结果标记重复项
  const mappedData = []
  const seenKeys = new Set()
  
  for (const item of tempMappedData) {
    // 检测是否重复（只有非首次出现且属于多重组的项才标记为重复）
    const hasMultiple = item.name.trim() && duplicateCheck.get(item.duplicateKey) > 1
    const isFirstOccurrence = !seenKeys.has(item.duplicateKey)
    
    if (item.name.trim()) {
      seenKeys.add(item.duplicateKey)
    }
    
    // 添加重复组标记
    item.belongsToDuplicateGroup = hasMultiple
    item.isFirstInGroup = isFirstOccurrence && hasMultiple
    
    if (hasMultiple && !isFirstOccurrence) {
      item.duplicate = true
      // 不在此处设置 valid = false，让重复数据在筛选时处理
      item.errors.push('重复的材料记录')
    }
    
    // 数据验证
    if (!item.name || item.name.trim() === '') {
      item.valid = false
      item.errors.push('材料名称不能为空')
    }
    
    if (!item.unit || item.unit.trim() === '') {
      item.valid = false
      item.errors.push('单位不能为空')
    }
    
    if (!item.price_excluding_tax || item.price_excluding_tax <= 0) {
      item.valid = false
      item.errors.push('除税信息价必须大于0')
    }
    
    // 检查除税价格是否为数字
    if (isNaN(item.price_excluding_tax)) {
      item.valid = false
      item.errors.push('除税信息价格式错误')
    }
    
    // 含税价格验证（可选）
    if (item.price_including_tax && isNaN(item.price_including_tax)) {
      item.valid = false
      item.errors.push('含税信息价格式错误')
    }
    
    mappedData.push(item)
  }
  
  return mappedData
}

// 从完整数据中获取筛选结果
const getFilteredFullData = (filterType) => {
  if (!hasFullData.value) {
    if (filterType === 'invalid') {
      return previewData.value.filter(item => !item.valid && !item.duplicate)
    } else if (filterType === 'duplicate') {
      // 优化预览数据的重复排布
      const duplicateItems = previewData.value.filter(item => item.belongsToDuplicateGroup)

      if (duplicateItems.length === 0) {
        return []
      }

      // 按duplicateKey分组并排序
      const groupedByKey = new Map()
      duplicateItems.forEach(item => {
        if (!groupedByKey.has(item.duplicateKey)) {
          groupedByKey.set(item.duplicateKey, [])
        }
        groupedByKey.get(item.duplicateKey).push(item)
      })

      // 将Map转换为数组，按第一条数据的行索引排序各组
      const groups = Array.from(groupedByKey.values()).map(group => {
        // 每组内按原始行索引排序
        return group.sort((a, b) => a.row_index - b.row_index)
      }).sort((groupA, groupB) => {
        // 各组之间按第一条数据的行索引排序
        return groupA[0].row_index - groupB[0].row_index
      })

      const sortedDuplicates = []
      groups.forEach(group => {
        // 标记组内第一个为正常，其余为重复
        group.forEach((item, index) => {
          // 创建副本，不修改原始数据
          const duplicateItem = { ...item }
          if (index === 0) {
            // 第一个：正常数据
            duplicateItem.duplicate = false
            duplicateItem.isFirstInGroup = true
            duplicateItem.valid = true
          } else {
            // 后续：重复数据
            duplicateItem.duplicate = true
            duplicateItem.isFirstInGroup = false
            duplicateItem.valid = true // 重复数据也显示为有效，但有重复标记
          }
          duplicateItem.belongsToDuplicateGroup = true
          sortedDuplicates.push(duplicateItem)
        })
      })

      return sortedDuplicates
    }
    return previewData.value
  }

  const processedFullData = processFullDataWithMapping(fullImportData.value)
  
  if (filterType === 'invalid') {
    return processedFullData.filter(item => !item.valid && !item.duplicate)
  } else if (filterType === 'duplicate') {
    // 优化重复数据排布：让每条原始数据后紧跟它的重复数据
    const duplicateItems = processedFullData.filter(item => item.belongsToDuplicateGroup)

    if (duplicateItems.length === 0) {
      return []
    }

    // 按duplicateKey分组
    const groupedByKey = new Map()
    duplicateItems.forEach(item => {
      if (!groupedByKey.has(item.duplicateKey)) {
        groupedByKey.set(item.duplicateKey, [])
      }
      groupedByKey.get(item.duplicateKey).push(item)
    })

    // 转换为数组并按第一条数据的行索引排序各组
    const groups = Array.from(groupedByKey.values()).map(group => {
      // 每组内按原始行索引排序
      return group.sort((a, b) => a.row_index - b.row_index)
    }).sort((groupA, groupB) => {
      // 各组之间按第一条数据（原始数据）的行索引排序
      return groupA[0].row_index - groupB[0].row_index
    })

    // 重新排列：每组连续显示（原始数据 + 重复数据）
    const sortedDuplicates = []
    groups.forEach(group => {
      // 标记组内第一个为正常，其余为重复
      group.forEach((item, index) => {
        // 创建副本，不修改原始数据
        const duplicateItem = { ...item }
        if (index === 0) {
          // 第一个：正常数据
          duplicateItem.duplicate = false
          duplicateItem.isFirstInGroup = true
          duplicateItem.valid = true
        } else {
          // 后续：重复数据
          duplicateItem.duplicate = true
          duplicateItem.isFirstInGroup = false
          duplicateItem.valid = true // 重复数据也显示为有效，但有重复标记
        }
        duplicateItem.belongsToDuplicateGroup = true
        sortedDuplicates.push(duplicateItem)
      })
    })

    return sortedDuplicates
  }
  
  return processedFullData
}

const filteredPreviewData = computed(() => {
  switch (previewFilter.value) {
    case 'valid':
      return previewData.value.filter(item => item.valid)
    case 'invalid':
    case 'duplicate':
      return getFilteredFullData(previewFilter.value)
    default:
      return previewData.value
  }
})

// 信息价类型按钮选择方法
const selectPriceType = (type) => {
  priceTypeForm.priceType = type
  onPriceTypeChange(type)
}

// 信息价类型选择处理方法
const onPriceTypeChange = (value) => {
  console.log('信息价类型选择变化:', value)
  // 清空之前的省份和城市选择
  priceTypeForm.province = ''
  priceTypeForm.city = ''
  
  // 更新region字段
  updateRegionInfo()
}

// 省份选择变化处理方法
const onProvinceChange = (value) => {
  console.log('省份选择变化:', value)
  // 清空城市选择
  priceTypeForm.city = ''
  
  // 更新region字段
  updateRegionInfo()
}

// 更新region信息
const updateRegionInfo = () => {
  let region = ''
  
  if (priceTypeForm.province) {
    const provinceName = provinceOptions.value.find(p => p.value === priceTypeForm.province)?.label || ''
    
    if (priceTypeForm.priceType === 'municipal' && priceTypeForm.city) {
      const cityName = currentCityOptions.value.find(c => c.value === priceTypeForm.city)?.label || ''
      region = cityName
    } else {
      region = provinceName
    }
  }
  
  priceTypeForm.region = region
}

// 文件处理方法
const handleFileChange = (file, fileListParam) => {
  if (file.size > 50 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过 50MB')
    return false
  }
  
  const allowedTypes = ['.xlsx', '.xls', '.csv']
  const fileExtension = file.name.toLowerCase().substr(file.name.lastIndexOf('.'))
  if (!allowedTypes.includes(fileExtension)) {
    ElMessage.error('只支持 Excel (.xlsx, .xls) 和 CSV 格式文件')
    return false
  }
  
  fileList.value = fileListParam
  resetAnalysis()
  
  ElMessage.success('文件选择成功')
}

const handleFileRemove = () => {
  fileList.value = []
  resetAnalysis()
}

const beforeUpload = () => {
  return false
}

const handleExceed = () => {
  ElMessage.warning('只能上传一个文件')
}

const formatFileSize = (size) => {
  if (size < 1024) return size + ' B'
  if (size < 1024 * 1024) return (size / 1024).toFixed(2) + ' KB'
  return (size / (1024 * 1024)).toFixed(2) + ' MB'
}

const removeSelectedFile = () => {
  try {
    uploadRef.value?.clearFiles()
  } catch (e) {}
  fileList.value = []
  resetAnalysis()
}

// 步骤控制方法
const nextStep = async () => {
  try {
    switch (currentStep.value) {
      case 0:
        await analyzeFile()
        break
      case 1:
        // 检查是否选择了工作表
        const sheetsToCheck = selectedSheets.value.length > 0 ? selectedSheets.value : [selectedSheet.value]
        if (sheetsToCheck.length === 0 || (sheetsToCheck.length === 1 && !sheetsToCheck[0])) {
          ElMessage.error('请先选择要导入的工作表')
          return
        }
        setupFieldMapping()
        break
      case 2:
        await previewFileData()
        break
    }
    
    if (currentStep.value < 4) {
      currentStep.value++
    }
  } catch (error) {
    console.error('步骤执行失败:', error)
    ElMessage.error(`步骤执行失败: ${error.message}`)
    
    ElMessageBox.confirm(
      '当前步骤执行失败，是否继续到下一步？',
      '警告',
      {
        confirmButtonText: '继续',
        cancelButtonText: '取消',
        type: 'warning',
      }
    ).then(() => {
      if (currentStep.value < 4) {
        currentStep.value++
      }
    }).catch(() => {
      // 用户取消，保持当前步骤
    })
  }
}

const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

// 文件分析
const analyzeFile = async () => {
  analyzing.value = true
  try {
    if (!fileList.value.length) {
      ElMessage.error('请先选择文件')
      return
    }
    
    const file = fileList.value[0]
    // 使用基准材料的解析API
    const response = await parseExcelStructure(file.raw || file, {
      sheet_name: selectedSheet.value
    })
    
    const data = response.data || response
    analysisResult.value = data
    availableColumns.value = data.columns || []
    selectedSheet.value = data.sheets?.[0]?.name || 'Sheet1'
    
    // 自动选中所有工作表（用户可以在下一步取消选择）
    if (data.sheets && data.sheets.length > 0) {
      selectedSheets.value = data.sheets.map(s => s.name)
    } else {
      selectedSheets.value = [selectedSheet.value]
    }
    
    ElMessage.success('文件分析完成')
  } catch (error) {
    console.error('文件分析失败:', error)
    ElMessage.error('文件分析失败，请检查文件格式是否正确')
    
    analysisResult.value = {
      sheets: [
        { name: 'Sheet1', rows: 0, columns: 0 }
      ],
      totalRows: 0,
      totalColumns: 0,
      completeness: 0,
      columns: [],
      sampleData: []
    }
  } finally {
    analyzing.value = false
  }
}

// 设置字段映射
const setupFieldMapping = () => {
  availableColumns.value = analysisResult.value.columns
}

// 智能映射并预览
const autoMappingAndPreview = async () => {
  autoMapping()
  ElMessage.success('智能映射完成，请检查映射结果，确认无误后点击"下一步"')
}

// 去除空格/全角空格等，用于列名匹配
const normalizeForMatch = (text) => {
  if (!text) return ''
  return String(text)
    .replace(/[\s\u00A0\u3000]/g, '')
    .replace(/[（）]/g, (ch) => (ch === '（' ? '(' : ch === '）' ? ')' : ch))
    .trim()
}

// 智能映射 - 适配基准材料字段
const autoMapping = () => {
  const columns = availableColumns.value
  
  const mappingRules = {
    material_code: [
      '编码', '材料编码', '编号', '材料编号', '代码', '材料代码',
      'code', 'material_code', 'item_code', 'number'
    ],
    name: [
      '材料名称', '名称', '材料', '品名', '材料品名',
      'material', 'name', 'item', 'product'
    ],
    specification: [
      '规格', '型号', '规格型号', '规格/型号', '技术规格', '产品规格', '参数',
      'specification', 'model', 'spec', 'type'
    ],
    unit: [
      '单位', '计量单位', '计价单位',
      'unit', 'measure', 'uom'
    ],
    price_excluding_tax: [
      '除税价格', '除税信息价', '不含税价格', '除税价', '税前价格', '净价',
      '价格', '单价', '参考价格', '市场价', '信息价', '基准价',
      'price_excluding_tax', 'price_ex_tax', 'net_price', 'price', 'unit_price', 'cost'
    ],
    price_including_tax: [
      '含税价格', '含税信息价', '包税价格', '含税价', '含税', '含税信息',
      '信息价（含税）', '信息价(含税)', '税后价格', '毛价',
      'price_including_tax', 'price_inc_tax', 'gross_price', 'total_price'
    ],
    region: [
      '地区', '适用地区', '区域',
      'region', 'area', 'location'
    ],
    remarks: [
      '备注', '说明', '描述', '注释', '其他', '附注',
      'remark', 'note', 'description', 'comment'
    ]
  }
  
  Object.keys(fieldMapping).forEach(key => {
    fieldMapping[key] = ''
  })
  
  Object.entries(mappingRules).forEach(([field, keywords]) => {
    let bestMatch = -1
    let bestScore = 0
    
    columns.forEach((column, index) => {
      const columnStr = String(column).trim()
      const normalizedColumn = normalizeForMatch(columnStr)
      const lowerColumn = columnStr.toLowerCase()
      const normalizedLowerColumn = normalizedColumn.toLowerCase()
      let score = 0
      const hasExactMatch = keywords.some(keyword => normalizeForMatch(keyword) === normalizedColumn)
      
      if (hasExactMatch) {
        score = 100
      } else {
        keywords.forEach(keyword => {
          const normalizedKeyword = normalizeForMatch(keyword)
          if (!normalizedKeyword) {
            return
          }
          
          const lowerKeyword = keyword.toLowerCase()
          const normalizedLowerKeyword = normalizedKeyword.toLowerCase()
          
          if (
            columnStr.includes(keyword) ||
            lowerColumn.includes(lowerKeyword) ||
            normalizedLowerColumn.includes(normalizedLowerKeyword)
          ) {
            score += 50
          }
          
          const similarity = calculateSimilarity(normalizedColumn, normalizedKeyword)
          if (similarity > 0.6) {
            score += similarity * 20
          }
        })
      }
      
      if (score > bestScore) {
        bestScore = score
        bestMatch = index
      }
    })
    
    if (bestMatch >= 0 && bestScore >= 30) {
      fieldMapping[field] = bestMatch
    }
  })
  
  const mappedFields = Object.values(fieldMapping).filter(val => val !== '').length
  
  if (mappedFields > 0) {
    ElMessage.success(`智能映射完成，成功匹配${mappedFields}个字段`)
  } else {
    ElMessage.warning('智能映射未找到匹配的字段，请手动设置')
  }
}

// 计算字符串相似度
const calculateSimilarity = (str1, str2) => {
  const longer = str1.length > str2.length ? str1 : str2
  const shorter = str1.length > str2.length ? str2 : str1
  
  if (longer.length === 0) {
    return 1.0
  }
  
  const editDistance = getEditDistance(longer, shorter)
  return (longer.length - editDistance) / longer.length
}

// 计算编辑距离
const getEditDistance = (str1, str2) => {
  const matrix = []
  
  for (let i = 0; i <= str2.length; i++) {
    matrix[i] = [i]
  }
  
  for (let j = 0; j <= str1.length; j++) {
    matrix[0][j] = j
  }
  
  for (let i = 1; i <= str2.length; i++) {
    for (let j = 1; j <= str1.length; j++) {
      if (str2.charAt(i - 1) === str1.charAt(j - 1)) {
        matrix[i][j] = matrix[i - 1][j - 1]
      } else {
        matrix[i][j] = Math.min(
          matrix[i - 1][j - 1] + 1,
          matrix[i][j - 1] + 1,
          matrix[i - 1][j] + 1
        )
      }
    }
  }
  
  return matrix[str2.length][str1.length]
}

// 获取字段预览
const getFieldPreview = (field) => {
  const columnIndex = fieldMapping[field]
  if (columnIndex === '' || !analysisResult.value) return '未选择'
  
  const sampleData = analysisResult.value.sampleData[0]
  if (!sampleData) return '无数据'
  
  return sampleData[`col_${columnIndex}`] || '无数据'
}

// 数据预览
const previewFileData = async () => {
  try {
    console.log('开始数据预览...')
    
    // 检查是否选择了工作表
    const sheetsToProcess = selectedSheets.value.length > 0 ? selectedSheets.value : [selectedSheet.value]
    if (sheetsToProcess.length === 0 || (sheetsToProcess.length === 1 && !sheetsToProcess[0])) {
      ElMessage.error('请先选择要导入的工作表')
      return
    }
    
    // 首先检查是否有解析结果可以回退使用
    let sourceData = null
    let useNewAPI = true
    
    if (!fileList.value || fileList.value.length === 0) {
      if (!analysisResult.value || !analysisResult.value.sampleData) {
        ElMessage.error('没有可预览的数据')
        return
      }
      useNewAPI = false
      sourceData = analysisResult.value.sampleData
      console.log('使用已有分析结果数据:', sourceData.length, '行')
    }
    
    if (useNewAPI) {
      try {
        const currentFile = fileList.value[0].raw || fileList.value[0]
        console.log('尝试使用新API获取预览数据...', { file: currentFile, sheets: sheetsToProcess })
        
        // 支持多工作表：合并所有工作表的数据
        const allPreviewData = []
        const allFullData = []
        
        for (const sheetName of sheetsToProcess) {
        // 使用基准材料的预览API
        const response = await getPreviewData(currentFile, {
            sheet_name: sheetName,
          max_rows: 2000  // 最多预览2000行
        })
        
        if (response.code === 200 && response.data) {
            const sheetPreviewData = response.data.previewData || []
            const sheetFullData = response.data.fullData || response.data.previewData || []
            
            // 为每个数据项标记来源工作表
            const period = getSheetPeriod(sheetName)
            sheetPreviewData.forEach(item => {
              item._sheetName = sheetName
              item._period = period
            })
            sheetFullData.forEach(item => {
              item._sheetName = sheetName
              item._period = period
            })
            
            allPreviewData.push(...sheetPreviewData)
            allFullData.push(...sheetFullData)
            console.log(`工作表 "${sheetName}" 获取成功，预览数据: ${sheetPreviewData.length} 行，完整数据: ${sheetFullData.length} 行${period ? ' (期数: ' + period + ')' : ''}`)
        } else {
            throw new Error(response.message || `获取工作表 "${sheetName}" 数据失败`)
          }
        }
        
        // 合并所有工作表的数据
        fullImportData.value = allFullData
        sourceData = allPreviewData
        console.log('多工作表数据合并完成，总预览数据:', sourceData.length, '行，总完整数据:', fullImportData.value.length, '行')
      } catch (apiError) {
        console.warn('新API调用失败，回退到使用分析结果:', apiError.message)
        if (analysisResult.value && analysisResult.value.sampleData) {
          useNewAPI = false
          sourceData = analysisResult.value.sampleData
        } else {
          throw apiError
        }
      }
    }
    
    if (!sourceData || sourceData.length === 0) {
      ElMessage.error('没有可预览的数据')
      return
    }
    
    console.log('开始处理预览数据，数据源行数:', sourceData.length)
    
    // 第一步：收集所有数据并检测重复项
    const duplicateCheck = new Map()
    const tempMappedData = []
    
    // 先收集所有数据，统计重复键
    for (let i = 0; i < sourceData.length; i++) {
      const row = sourceData[i]
      
      // 根据字段映射提取数据
      const getValue = (fieldName) => {
        const columnIndex = fieldMapping[fieldName]
        if (columnIndex === '' || columnIndex === undefined) return ''
        
        if (row.data && availableColumns.value[columnIndex]) {
          const mappedValue = row.data[availableColumns.value[columnIndex]]
          if (mappedValue !== undefined && mappedValue !== null && String(mappedValue).trim() !== '') {
            return mappedValue
          }
        }
        
        const fallbackValue = row[`col_${columnIndex}`]
        if (fallbackValue !== undefined && fallbackValue !== null && String(fallbackValue).trim() !== '') {
          return fallbackValue
        }
        
        return ''
      }
        
        const name = getValue('name') || ''
        const specification = getValue('specification') || ''
        const unit = getValue('unit') || ''
        const price_excluding_tax = parseFloat(getValue('price_excluding_tax')) || 0
        const price_including_tax = parseFloat(getValue('price_including_tax')) || 0
        
        // 根据信息价类型确定适用地区显示文本
        const getPreviewRegionText = () => {
          const excelRegion = getValue('region') || ''
          
          if (priceTypeForm.priceType === 'provincial') {
            // 省刊信息价
             const provinceCode = priceTypeForm.province || ''
             const provinceName = provinceOptions.value.find(p => p.value === provinceCode)?.label || provinceCode
             
             if (excelRegion && excelRegion !== provinceCode && !excelRegion.includes(provinceName)) {
                return `${provinceName} ${excelRegion}`
             }
             return provinceName
          } else if (priceTypeForm.priceType === 'municipal') {
            // 市刊信息价
            const cityCode = priceTypeForm.city || ''
            const cityName = currentCityOptions.value.find(c => c.value === cityCode)?.label || (cityCode || '未选择城市')
            
            if (excelRegion && excelRegion !== cityCode && !excelRegion.includes(cityName)) {
               return `${cityName} ${excelRegion}`
            }
            return cityName
          } else {
            // 未选择信息价类型时，显示Excel中的原始地区信息
            return excelRegion
          }
        }

        const item = {
          row_index: i,
          material_code: getValue('material_code') || '',
          name: name,
          specification: specification,
          unit: unit,
          price_excluding_tax: price_excluding_tax,
          price_including_tax: price_including_tax,
          region: getPreviewRegionText(),
          excel_region: getValue('region') || '', // 保存Excel中的原始地区信息
          remarks: getValue('remarks') || '',
          valid: true,
          duplicate: false,
          errors: []
        }
        
        // 生成重复检测键 - 基于材料编码 + 材料名称 + 规格型号 + 备注 + 地区 + 期数
        const materialCode = getValue('material_code') || ''
        const notes = getValue('verification_notes') || ''
        const region = getValue('region') || ''
        const period = row._period || getSheetPeriod(row._sheetName) || '' // 期数
        const baseKey = `${materialCode.trim()}_${name.trim()}_${specification.trim()}_${notes.trim()}_${region.trim()}_${period.trim()}`.toLowerCase()
        const duplicateKey = baseKey
        item.duplicateKey = duplicateKey
        item.baseKey = baseKey  // 保存基础键用于分析
        item._period = period // 保存期数信息
        item._sheetName = row._sheetName || '' // 保存工作表名称
        
        // 统计重复键出现次数
        if (name.trim()) {
          duplicateCheck.set(duplicateKey, (duplicateCheck.get(duplicateKey) || 0) + 1)
        }
        
        tempMappedData.push(item)
      }
    
    // 第二步：基于重复检测结果标记重复项
    const mappedData = []
    const seenKeys = new Set()
    
    for (const item of tempMappedData) {
      // 检测是否重复（只有非首次出现且属于多重组的项才标记为重复）
      const hasMultiple = item.name.trim() && duplicateCheck.get(item.duplicateKey) > 1
      const isFirstOccurrence = !seenKeys.has(item.duplicateKey)
      
      if (item.name.trim()) {
        seenKeys.add(item.duplicateKey)
      }
      
      // 添加重复组标记
      item.belongsToDuplicateGroup = hasMultiple
      item.isFirstInGroup = isFirstOccurrence && hasMultiple
      
      if (hasMultiple && !isFirstOccurrence) {
        item.duplicate = true
        // 不在此处设置 valid = false，让重复数据在筛选时处理
        item.errors.push('重复的材料记录')
      }
      
      // 数据验证
      if (!item.name || item.name.trim() === '') {
        item.valid = false
        item.errors.push('材料名称不能为空')
      }
      
      if (!item.unit || item.unit.trim() === '') {
        item.valid = false
        item.errors.push('单位不能为空')
      }
      
      if (!item.price_excluding_tax || item.price_excluding_tax <= 0) {
        item.valid = false
        item.errors.push('除税信息价必须大于0')
      }
      
      // 检查除税价格是否为数字
      if (isNaN(item.price_excluding_tax)) {
        item.valid = false
        item.errors.push('除税信息价格式错误')
      }
      
      // 含税价格验证（可选）
      if (item.price_including_tax && isNaN(item.price_including_tax)) {
        item.valid = false
        item.errors.push('含税信息价格式错误')
      }
      
      mappedData.push(item)
    }
      
    previewData.value = mappedData
    
    // 计算完整数据统计
    calculateFullDataStats()
    
    const totalMessage = useNewAPI ? 
      `数据预览生成完成，预览${mappedData.length}条记录` : 
      `数据预览生成完成，共${mappedData.length}条记录`
    ElMessage.success(totalMessage)
  } catch (error) {
    console.error('预览失败完整错误:', error)
    if (error.response) {
      console.error('错误响应:', error.response.data)
      ElMessage.error(`数据预览生成失败: ${error.response.data.detail || error.message}`)
    } else {
      ElMessage.error('数据预览生成失败: ' + error.message)
    }
  }
}

// 获取将要导入的数据条数
const getImportCount = () => {
  let sourceData = hasFullData.value ? fullImportData.value : previewData.value
  let validCount = 0
  
  // 使用与实际导入相同的逻辑来计算数量
  const duplicateCheck = new Map()
  const tempItems = []
  
  // 第一步：处理所有数据并检测重复
  for (let i = 0; i < sourceData.length; i++) {
    const row = sourceData[i]
    
    // 修改 getValue 函数，优先使用已编辑的字段值
    const getValue = (fieldName) => {
      // 如果数据被编辑过，直接使用 row 对象中的值
      if (row._edited && row.hasOwnProperty(fieldName)) {
        const value = row[fieldName]
        if (value !== undefined && value !== null) {
          return String(value)
        }
      }
      
      // 如果 row 中直接有该字段（预览时生成的），也优先使用
      if (row.hasOwnProperty(fieldName) && !fieldName.startsWith('_') && fieldName !== 'data' && fieldName !== 'valid' && fieldName !== 'errors' && fieldName !== 'duplicate' && fieldName !== 'row_index') {
        const value = row[fieldName]
        // 确保返回的是有效值
        if (value !== undefined && value !== null && String(value).trim() !== '') {
          return String(value)
        }
      }
      
      // 否则从原始数据中提取
      const columnIndex = fieldMapping[fieldName]
      if (columnIndex === '' || columnIndex === undefined) return ''
      
      if (row.data && availableColumns.value[columnIndex]) {
        const mappedValue = row.data[availableColumns.value[columnIndex]]
        if (mappedValue !== undefined && mappedValue !== null && String(mappedValue).trim() !== '') {
          return mappedValue
        }
      }
      
      const fallbackValue = row[`col_${columnIndex}`]
      if (fallbackValue !== undefined && fallbackValue !== null && String(fallbackValue).trim() !== '') {
        return fallbackValue
      }
      
      return ''
    }
    
    const item = {
      name: getValue('name') || '',
      specification: getValue('specification') || '',
      unit: getValue('unit') || '',
      price_excluding_tax: parseFloat(getValue('price_excluding_tax')) || 0,
      price_including_tax: parseFloat(getValue('price_including_tax')) || 0,
      valid: true,
      duplicate: false
    }
    
    // 数据验证
    if (!item.name || item.name.trim() === '') {
      item.valid = false
    }
    if (!item.unit || item.unit.trim() === '') {
      item.valid = false
    }
    if (!item.price_excluding_tax || item.price_excluding_tax <= 0) {
      item.valid = false
    }
    if (isNaN(item.price_excluding_tax)) {
      item.valid = false
    }
    
    // 生成重复检测键（材料编码 + 材料名称 + 规格型号 + 备注 + 地区 + 期数，六个字段确定唯一性）
    const materialCode = getValue('material_code') || '' // 材料编码
    const notes = getValue('verification_notes') || '' // 备注
    const region = getValue('region') || '' // 地区
    const period = row._period || getSheetPeriod(row._sheetName) || '' // 期数
    const duplicateKey = `${materialCode.trim()}_${item.name.trim()}_${item.specification.trim()}_${notes.trim()}_${region.trim()}_${period.trim()}`.toLowerCase()
    item.duplicateKey = duplicateKey
    item._period = period // 保存期数信息
    item._sheetName = row._sheetName || '' // 保存工作表名称
    
    if (item.name.trim()) {
      duplicateCheck.set(duplicateKey, (duplicateCheck.get(duplicateKey) || 0) + 1)
    }
    
    tempItems.push(item)
  }
  
  // 第二步：基于重复检测结果统计实际导入数量
  const seenKeys = new Set()
  
  for (const item of tempItems) {
    const hasMultiple = item.name.trim() && duplicateCheck.get(item.duplicateKey) > 1
    const isFirstOccurrence = !seenKeys.has(item.duplicateKey)
    
    if (item.name.trim()) {
      seenKeys.add(item.duplicateKey)
    }
    
    // 跳过重复项（非首次出现）
    if (hasMultiple && !isFirstOccurrence) {
      item.duplicate = true
      if (importOptions.skipDuplicate) continue
    }
    
    // 跳过无效数据
    if (importOptions.skipInvalid && !item.valid) continue
    
    validCount++
  }
  
  return validCount
}

// 开始导入
const startImport = async () => {
  importing.value = true
  currentStep.value = 4
  
  try {
    let sourceDataForImport = hasFullData.value ? fullImportData.value : previewData.value
    console.log(`开始导入: 使用${hasFullData.value ? '完整' : '预览'}数据, 共${sourceDataForImport.length}条`)
    
    const duplicateCheck = new Map()
    const tempItems = []
    
    for (let i = 0; i < sourceDataForImport.length; i++) {
      const row = sourceDataForImport[i]
      
      // 修改 getValue 函数，优先使用已编辑的字段值
      const getValue = (fieldName) => {
        // 如果数据被编辑过，直接使用 row 对象中的值
        if (row._edited && row.hasOwnProperty(fieldName)) {
          const value = row[fieldName]
          if (value !== undefined && value !== null) {
            return String(value)
          }
        }
        
        // 如果 row 中直接有该字段（预览时生成的），也优先使用
        if (row.hasOwnProperty(fieldName) && !fieldName.startsWith('_') && fieldName !== 'data' && fieldName !== 'valid' && fieldName !== 'errors' && fieldName !== 'duplicate' && fieldName !== 'row_index') {
          const value = row[fieldName]
          // 确保返回的是有效值
          if (value !== undefined && value !== null && String(value).trim() !== '') {
            return String(value)
          }
        }
        
        // 否则从原始数据中提取
        const columnIndex = fieldMapping[fieldName]
        if (columnIndex === '' || columnIndex === undefined) return ''
        
        if (row.data && availableColumns.value[columnIndex]) {
          const mappedValue = row.data[availableColumns.value[columnIndex]]
          if (mappedValue !== undefined && mappedValue !== null && String(mappedValue).trim() !== '') {
            return mappedValue
          }
        }
        
        const fallbackValue = row[`col_${columnIndex}`]
        if (fallbackValue !== undefined && fallbackValue !== null && String(fallbackValue).trim() !== '') {
          return fallbackValue
        }
        
        return ''
      }
      
      // 根据信息价类型确定适用地区
      const getImportRegionText = () => {
        const excelRegion = getValue('region') || ''
        
        if (priceTypeForm.priceType === 'provincial') {
          // 省刊信息价：如果Excel有更详细地区，保留组合信息，否则使用省份
          const provinceCode = priceTypeForm.province || ''
          const provinceName = provinceOptions.value.find(p => p.value === provinceCode)?.label || provinceCode
          
          if (excelRegion && excelRegion !== provinceCode && !excelRegion.includes(provinceName)) {
            return `${provinceName} ${excelRegion}`
          }
          return provinceName
        } else if (priceTypeForm.priceType === 'municipal') {
          // 市刊信息价：如果Excel有更详细地区（如区县），保留组合信息
          const cityCode = priceTypeForm.city || ''
          const cityName = currentCityOptions.value.find(c => c.value === cityCode)?.label || cityCode
          
          if (excelRegion && excelRegion !== cityCode && !excelRegion.includes(cityName)) {
             return `${cityName} ${excelRegion}`
          }
          return cityName
        } else {
          // 未选择类型时保留Excel中的原始地区信息
          return excelRegion
        }
      }

      // 获取数据项的期数信息（从工作表名称提取）
      const itemPeriod = row._period || getSheetPeriod(row._sheetName) || ''

      const item = {
        material_code: getValue('material_code') || '',
        name: getValue('name') || '',
        specification: getValue('specification') || '',
        unit: getValue('unit') || '',
        price_excluding_tax: parseFloat(getValue('price_excluding_tax')) || 0,
        price_including_tax: parseFloat(getValue('price_including_tax')) || 0,
        region: getImportRegionText(),
        excel_region: getValue('region') || '', // 保存Excel中的原始地区信息
        remarks: getValue('remarks') || '',
        valid: true,
        duplicate: false,
        _period: itemPeriod, // 保存期数信息
        _sheetName: row._sheetName || '' // 保存工作表名称
      }
      
      // 如果是编辑过的数据，输出日志
      if (row._edited) {
        console.log(`🔧 导入编辑后的数据 - 行${row.row_index}: 名称=${item.name}, 单位=${item.unit}, 价格=${item.price_excluding_tax}`)
      }
      
      // 数据验证
      if (!item.name || item.name.trim() === '') {
        item.valid = false
      }
      if (!item.unit || item.unit.trim() === '') {
        item.valid = false
      }
      if (!item.price_excluding_tax || item.price_excluding_tax <= 0) {
        item.valid = false
      }
      if (isNaN(item.price_excluding_tax)) {
        item.valid = false
      }
      
      // 生成重复检测键（材料编码 + 材料名称 + 规格型号 + 备注 + 地区 + 期数，六个字段确定唯一性）
      const materialCode = item.material_code || ''
      const notes = item.verification_notes || item.remarks || ''
      const region = item.region || ''
      const period = itemPeriod || ''
      const duplicateKey = `${materialCode.trim()}_${item.name.trim()}_${item.specification.trim()}_${notes.trim()}_${region.trim()}_${period.trim()}`.toLowerCase()
      item.duplicateKey = duplicateKey
      
      if (item.name.trim()) {
        duplicateCheck.set(duplicateKey, (duplicateCheck.get(duplicateKey) || 0) + 1)
      }
      
      tempItems.push(item)
    }
    
    let materialsToImport = []
    const seenKeys = new Set()
    
    for (const item of tempItems) {
      const hasMultiple = item.name.trim() && duplicateCheck.get(item.duplicateKey) > 1
      const isFirstOccurrence = !seenKeys.has(item.duplicateKey)
      
      if (item.name.trim()) {
        seenKeys.add(item.duplicateKey)
      }
      
      if (hasMultiple && !isFirstOccurrence) {
        item.duplicate = true
        if (importOptions.skipDuplicate) continue
      }
      
      if (importOptions.skipInvalid && !item.valid) continue
      
      // 确定适用地区：使用与预览和导入逻辑一致的地区信息
      const regionForImport = item.region // 使用前面已经处理好的地区信息

      // 从数据项中获取期数（如果数据项标记了来源工作表）
      const itemPeriod = item._period || getSheetPeriod(item._sheetName) || null

      // 准备基准材料数据结构
      const materialData = {
        material_code: item.material_code || '',
        name: item.name || '',
        specification: item.specification || '',
        unit: item.unit || '',
        price: item.price_excluding_tax || 0, // 使用除税价格作为主价格
        price_excluding_tax: item.price_excluding_tax || 0,
        price_including_tax: item.price_including_tax || 0,
        region: regionForImport, // 使用用户选择的省市信息作为适用地区
        excel_region: item.excel_region || '', // 保存Excel中的原始地区信息
        remarks: item.remarks || '',
        source: 'excel_import',
        is_verified: false,
        // 添加信息价相关字段
        price_type: priceTypeForm.priceType, // 'provincial' | 'municipal'
        price_date: itemPeriod, // YYYY-MM，从工作表名称自动识别
        price_source: priceTypeForm.priceType === 'provincial' ? '省刊信息价' : '市刊信息价',
        // 添加详细的省份和城市信息
        province: priceTypeForm.province,
        city: priceTypeForm.city || ''
      }
      
      materialsToImport.push(materialData)
    }
    
    const totalCount = materialsToImport.length
    importProgress.totalCount = totalCount
    
    if (totalCount === 0) {
      throw new Error('没有可导入的数据')
    }
    
    // 检查必要的信息价配置
    if (!priceTypeForm.priceType) {
      throw new Error('请先选择信息价类型（省刊或市刊）')
    }
    if (!priceTypeForm.province) {
      throw new Error('请先选择省份')
    }
    if (priceTypeForm.priceType === 'municipal' && !priceTypeForm.city) {
      throw new Error('选择市刊信息价时必须选择城市')
    }
    
    // 检查是否有数据缺少期数（无法从工作表名称识别）
    const materialsWithoutPeriod = materialsToImport.filter(m => !m.price_date)
    if (materialsWithoutPeriod.length > 0) {
      console.warn(`警告: 有 ${materialsWithoutPeriod.length} 条数据无法识别期数，这些数据将使用空期数`)
    }
    
    importProgress.message = '正在准备导入数据...'
    importProgress.percentage = 10
    
    const importData = {
      materials: materialsToImport,
      import_options: {
        skip_duplicate: importOptions.skipDuplicate,
        skip_invalid: importOptions.skipInvalid,
        auto_fix: importOptions.autoFix
      }
    }
    
    importProgress.message = '正在导入市场信息价数据...'
    importProgress.percentage = 50
    
    // 检查是否需要分批导入（超过1000条数据）
    const BATCH_SIZE = importOptions.batchSize || 1000 // 使用用户配置的批次大小
    const needBatchImport = materialsToImport.length > 1000 // 超过1000条才分批
    
    let result = {
      total_count: 0,
      success_count: 0,
      failed_count: 0,
      skipped_count: 0,
      errors: []
    }
    
    if (needBatchImport) {
      console.log(`🔄 大数据量导入，将分${Math.ceil(materialsToImport.length / BATCH_SIZE)}批处理`)
      result = await batchImportMaterials(materialsToImport, BATCH_SIZE, importData.import_options)
    } else {
      console.log('📤 单批导入处理')
      const response = await importBaseMaterials(importData)
      result = response.data?.data || response.data || response
    }
    
    importProgress.percentage = 100
    importProgress.processed = totalCount
    importProgress.success = result.success_count || result.imported_count || 0
    importProgress.failed = result.failed_count || 0
    
    importResult.success = (result.success_count || result.imported_count || 0) > 0
    importResult.title = importResult.success ? '导入完成' : '导入失败'
    importResult.message = importResult.success 
      ? `成功导入 ${result.success_count || result.imported_count} 条市场信息价数据`
      : '导入过程中出现错误，请查看详细信息'
    importResult.totalCount = result.total_count || totalCount
    importResult.successCount = result.success_count || result.imported_count || 0
    importResult.failedCount = result.failed_count || 0
    importResult.skippedCount = result.skipped_count || 0
    importResult.errors = result.errors || [] // 保存错误详情
    
    if (result.errors && result.errors.length > 0) {
      console.warn('导入警告信息:', result.errors)
    }
    
  } catch (error) {
    console.error('导入失败:', error)
    importResult.success = false
    importResult.title = '导入失败'
    importResult.message = error.message || error.detail || '数据导入过程中出现错误'
    importResult.totalCount = previewData.value.length
    importResult.successCount = 0
    importResult.failedCount = previewData.value.length
    importResult.skippedCount = 0
    // 保存错误信息
    importResult.errors = [error.message || error.detail || '数据导入过程中出现错误']
    if (error.response?.data?.detail) {
      importResult.errors.push(error.response.data.detail)
    }
  } finally {
    importing.value = false
  }
}

// 分批导入材料数据
const batchImportMaterials = async (materials, batchSize, importOptions) => {
  const totalBatches = Math.ceil(materials.length / batchSize)
  const results = {
    total_count: 0,
    success_count: 0,
    failed_count: 0,
    skipped_count: 0,
    errors: []
  }
  
  console.log(`开始分批导入: 总数据${materials.length}条，分${totalBatches}批，每批${batchSize}条`)
  
  for (let i = 0; i < totalBatches; i++) {
    const start = i * batchSize
    const end = Math.min(start + batchSize, materials.length)
    const batchMaterials = materials.slice(start, end)
    
    const currentBatch = i + 1
    importProgress.message = `正在导入第${currentBatch}/${totalBatches}批数据 (${start + 1}-${end})`
    importProgress.percentage = Math.floor((50 + (currentBatch / totalBatches) * 45)) // 50%-95%
    
    console.log(`导入第${currentBatch}批: ${batchMaterials.length}条数据`)
    
    try {
      const batchData = {
        materials: batchMaterials,
        import_options: importOptions
      }
      
      const response = await importBaseMaterials(batchData)
      const batchResult = response.data?.data || response.data || response
      
      // 累加结果
      results.total_count += batchResult.total_count || 0
      results.success_count += batchResult.success_count || 0
      results.failed_count += batchResult.failed_count || 0
      results.skipped_count += batchResult.skipped_count || 0
      
      if (batchResult.errors && batchResult.errors.length > 0) {
        results.errors.push(...batchResult.errors)
      }
      
      console.log(`第${currentBatch}批完成: 成功${batchResult.success_count}，失败${batchResult.failed_count}`)
      
      // 批次间短暂延迟，避免服务器压力
      if (i < totalBatches - 1) {
        await new Promise(resolve => setTimeout(resolve, 500))
      }
      
    } catch (error) {
      console.error(`第${currentBatch}批导入失败:`, error)
      results.failed_count += batchMaterials.length
      results.errors.push(`第${currentBatch}批导入失败: ${error.message}`)
      
      // 如果单批失败，询问是否继续
      if (currentBatch < totalBatches) {
        const continueImport = await ElMessageBox.confirm(
          `第${currentBatch}批导入失败，是否继续导入剩余${totalBatches - currentBatch}批数据？`,
          '导入失败',
          {
            type: 'warning',
            confirmButtonText: '继续导入',
            cancelButtonText: '停止导入'
          }
        ).catch(() => false)
        
        if (!continueImport) {
          break
        }
      }
    }
  }
  
  console.log('分批导入完成:', results)
  return results
}

// 表格行样式
const getRowClassName = ({ row }) => {
  if (!row.valid && !row.duplicate) return 'invalid-row'
  if (row.duplicate) return 'duplicate-row'
  if (row.isFirstInGroup) return 'first-duplicate-row'
  return ''
}

// 重置处理流程
const resetProcess = () => {
  currentStep.value = 0
  fileList.value = []
  resetPriceTypeForm()
  resetAnalysis()
  resetMapping()
  resetPreview()
  resetImport()
}

const resetPriceTypeForm = () => {
  Object.assign(priceTypeForm, {
    priceType: '',
    priceDate: '',
    region: '',
    province: '',
    city: ''
  })
}

const resetAnalysis = () => {
  analysisResult.value = null
  selectedSheet.value = ''
  selectedSheets.value = []
  availableColumns.value = []
  previewData.value = []
  fullImportData.value = []
}

const resetMapping = () => {
  Object.assign(fieldMapping, {
    material_code: '',
    name: '',
    specification: '',
    unit: '',
    price_excluding_tax: '',
    price_including_tax: '',
    region: '',
    remarks: ''
  })
}

const resetPreview = () => {
  previewData.value = []
  previewFilter.value = 'all'
}

const resetImport = () => {
  importing.value = false
  Object.assign(importProgress, {
    percentage: 0,
    message: '准备导入...',
    processed: 0,
    success: 0,
    failed: 0
  })
  
  Object.assign(importResult, {
    success: false,
    title: '',
    message: '',
    totalCount: 0,
    successCount: 0,
    failedCount: 0,
    skippedCount: 0,
    errors: []
  })
}

// 其他操作
const downloadTemplate = async () => {
  try {
    downloading.value = true
    // 使用基准材料模板下载API
    await downloadBaseMaterialTemplate()
    ElMessage.success('模板下载成功')
  } catch (error) {
    console.error('下载模板失败:', error)
    ElMessage.error('下载模板失败，请稍后重试')
  } finally {
    downloading.value = false
  }
}

// 显示错误详情
const showErrorDetails = () => {
  if (importResult.failedCount > 0 && importResult.errors && importResult.errors.length > 0) {
    showErrorDialog.value = true
  } else {
    ElMessage.warning('暂无错误详情信息')
  }
}

// 导出错误报告
const downloadErrorReport = () => {
  if (!importResult.errors || importResult.errors.length === 0) {
    ElMessage.warning('没有错误信息可导出')
    return
  }
  
  try {
    const errorContent = importResult.errors.map((error, index) => {
      return `${index + 1}. ${error}`
    }).join('\n')
    
    const reportContent = `导入错误报告\n` +
      `生成时间: ${new Date().toLocaleString('zh-CN')}\n` +
      `总数据量: ${importResult.totalCount}\n` +
      `成功导入: ${importResult.successCount}\n` +
      `导入失败: ${importResult.failedCount}\n` +
      `跳过数量: ${importResult.skippedCount}\n\n` +
      `错误详情:\n${errorContent}`
    
    const blob = new Blob([reportContent], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `导入错误报告_${new Date().toISOString().slice(0, 10)}.txt`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    
    ElMessage.success('错误报告导出成功')
  } catch (error) {
    console.error('导出错误报告失败:', error)
    ElMessage.error('导出错误报告失败')
  }
}

const downloadImportReport = () => {
  ElMessage.info('下载导入报告功能开发中...')
}

const goToMaterials = () => {
  router.push('/materials/base')
}

// 根据选择的工作表更新数据样本
const updateSheetData = async () => {
  if (!analysisResult.value || !selectedSheet.value) return
  
  try {
    analyzing.value = true
    console.log('切换到工作表:', selectedSheet.value)
    
    const file = fileList.value[0]
    const response = await parseExcelStructure(file.raw || file, {
      sheet_name: selectedSheet.value
    })
    
    const data = response.data || response
    
    analysisResult.value = {
      ...analysisResult.value,
      totalRows: data.totalRows || 0,
      totalColumns: data.totalColumns || 0,
      completeness: data.completeness || 0,
      columns: data.columns || [],
      sampleData: data.sampleData || [],
      currentSheet: data.currentSheet || selectedSheet.value
    }
    
    availableColumns.value = data.columns || []
    resetMapping()
    
    ElMessage.success(`已切换到工作表"${selectedSheet.value}"，共${data.totalRows || 0}行数据`)
    
  } catch (error) {
    console.error('更新工作表数据失败:', error)
    ElMessage.error('切换工作表失败，请重试')
  } finally {
    analyzing.value = false
  }
}

// 监听工作表选择变化
watch(selectedSheet, async (newSheet, oldSheet) => {
  if (newSheet && newSheet !== oldSheet && analysisResult.value) {
    await updateSheetData()
  }
}, { immediate: false })

// 监听城市选择变化
watch(() => priceTypeForm.city, (newCity) => {
  if (newCity) {
    updateRegionInfo()
  }
})

// 编辑功能相关方法
const getRowKey = (row) => {
  // 使用行索引作为唯一键
  return row.row_index
}

const isEditing = (row) => {
  return editingRows.value.has(getRowKey(row))
}

const startEditing = (row) => {
  const key = getRowKey(row)
  
  // 保存原始数据
  originalRowData.value.set(key, JSON.parse(JSON.stringify(row)))
  
  // 标记为正在编辑
  editingRows.value.add(key)
  
  ElMessage.info('进入编辑模式，请修改数据')
}

const cancelEditing = (row) => {
  const key = getRowKey(row)
  
  // 恢复原始数据
  const original = originalRowData.value.get(key)
  if (original) {
    Object.assign(row, original)
    originalRowData.value.delete(key)
  }
  
  // 取消编辑状态
  editingRows.value.delete(key)
  
  ElMessage.info('已取消编辑')
}

const saveEditing = (row) => {
  const key = getRowKey(row)
  
  // 验证数据
  const errors = []
  
  if (!row.name || row.name.trim() === '') {
    errors.push('材料名称不能为空')
  }
  
  if (!row.unit || row.unit.trim() === '') {
    errors.push('单位不能为空')
  }
  
  if (!row.price_excluding_tax || row.price_excluding_tax <= 0) {
    errors.push('除税信息价必须大于0')
  }
  
  if (isNaN(row.price_excluding_tax)) {
    errors.push('除税信息价格式错误')
  }
  
  if (row.price_including_tax && isNaN(row.price_including_tax)) {
    errors.push('含税信息价格式错误')
  }
  
  // 如果还有错误，提示用户
  if (errors.length > 0) {
    ElMessage.error('数据验证失败：' + errors.join(', '))
    return
  }
  
  // 数据有效，更新状态
  row.valid = true
  row.errors = []
  // 标记为已编辑，确保导入时使用编辑后的值
  row._edited = true
  
  // 规范化数据格式
  row.name = String(row.name || '').trim()
  row.unit = String(row.unit || '').trim()
  row.material_code = String(row.material_code || '').trim()
  row.specification = String(row.specification || '').trim()
  row.region = String(row.region || '').trim()
  row.remarks = String(row.remarks || '').trim()
  row.price_excluding_tax = parseFloat(row.price_excluding_tax) || 0
  row.price_including_tax = parseFloat(row.price_including_tax) || 0
  
  // 如果该行在完整数据中也存在，同步更新
  if (hasFullData.value && fullImportData.value.length > 0) {
    const fullDataRow = fullImportData.value.find(item => item.row_index === row.row_index)
    if (fullDataRow) {
      fullDataRow.name = row.name
      fullDataRow.unit = row.unit
      fullDataRow.specification = row.specification
      fullDataRow.material_code = row.material_code
      fullDataRow.price_excluding_tax = row.price_excluding_tax
      fullDataRow.price_including_tax = row.price_including_tax
      fullDataRow.region = row.region
      fullDataRow.remarks = row.remarks
      fullDataRow.valid = true
      fullDataRow.errors = []
      fullDataRow._edited = true
    }
  }
  
  // 清除编辑状态
  editingRows.value.delete(key)
  originalRowData.value.delete(key)
  
  // 重新计算统计数据
  calculateFullDataStats()
  
  console.log(`数据已修复: 行${row.row_index}, 材料名称: ${row.name}, 单位: ${row.unit}, 价格: ${row.price_excluding_tax}`)
  ElMessage.success('数据已修复！该条数据将作为有效数据导入')
}

// 生命周期
onMounted(() => {
  // 初始化
})
</script>

<style lang="scss" scoped>
.material-import-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 20px;

  .header-content {
    .page-title {
      font-size: 24px;
      font-weight: 600;
      color: #303133;
      margin: 0 0 8px 0;
    }

    .page-subtitle {
      font-size: 14px;
      color: #909399;
      margin: 0;
    }
  }
}

.steps-card {
  margin-bottom: 20px;
  
  :deep(.el-steps) {
    margin: 20px 0;
  }
}

.content-card {
  margin-bottom: 20px;
  min-height: 500px;

  .step-content {
    padding: 20px;

    h3 {
      font-size: 18px;
      font-weight: 600;
      color: #303133;
      margin-bottom: 8px;
    }

    .section-desc {
      font-size: 14px;
      color: #909399;
      margin-bottom: 24px;
    }
  }
}

// 信息价类型选择样式
.price-type-section {
  margin-bottom: 32px;
  
  .type-selection {
    :deep(.el-form-item) {
      margin-bottom: 20px;
      
      .el-form-item__label {
        font-weight: 600;
        color: #303133;
      }
    }
    
    .price-type-buttons {
      display: flex;
      gap: 20px;
      justify-content: flex-start;
      
      .price-type-btn {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 20px 24px;
        min-width: 160px;
        min-height: 80px;
        border-radius: 12px;
        border: 2px solid #e5e7eb;
        background-color: #ffffff;
        transition: all 0.3s ease;
        position: relative;
        
        .btn-icon {
          font-size: 24px;
          margin-bottom: 8px;
          color: #6b7280;
          transition: color 0.3s ease;
        }
        
        span {
          font-size: 14px;
          font-weight: 500;
          color: #374151;
          transition: color 0.3s ease;
        }
        
        &:hover {
          border-color: #409eff;
          background-color: #f0f8ff;
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
          
          .btn-icon {
            color: #409eff;
          }
          
          span {
            color: #409eff;
          }
        }
        
        &.active,
        &:deep(.el-button--primary) {
          border-color: #409eff;
          background: linear-gradient(135deg, #409eff 0%, #67c23a 100%);
          color: #ffffff;
          box-shadow: 0 6px 20px rgba(64, 158, 255, 0.4);
          
          .btn-icon {
            color: #ffffff;
          }
          
          span {
            color: #ffffff;
          }
          
          &::after {
            content: '✓';
            position: absolute;
            top: 8px;
            right: 8px;
            background-color: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: bold;
          }
        }
      }
    }
    
    .selection-summary {
      margin-top: 16px;
      
      .el-alert {
        border-radius: 8px;
      }
    }
  }
}

// 文件上传样式
.upload-section {
  .upload-area {
    margin-bottom: 24px;
    
    :deep(.el-upload-dragger) {
      width: 100%;
      padding: 60px 20px;
    }
    
    :deep(.el-upload-list__item .el-icon-close) {
      width: 22px;
      height: 22px;
      font-size: 18px;
    }
  }

  .file-info {
    margin-bottom: 24px;
    padding: 16px;
    background-color: #f8f9fa;
    border-radius: 8px;

    h4 {
      font-size: 14px;
      margin-bottom: 12px;
    }

    .file-item {
      display: flex;
      align-items: center;
      gap: 12px;

      .el-icon {
        color: #409eff;
      }

      .file-name {
        flex: 1;
        font-weight: 500;
      }

      .file-size {
        font-size: 12px;
        color: #909399;
      }
    }

    .file-actions {
      margin-top: 12px;
    }
  }

  .template-section {
    .template-actions {
      display: flex;
      gap: 12px;
      justify-content: center;
    }
  }
}

// 分析结果样式
.analysis-section {
  .analysis-result {
    .stats-cards {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 20px;
      margin-bottom: 30px;

      .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 15px 0 rgba(102, 126, 234, 0.3);

        &:nth-child(2) {
          background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }
        &:nth-child(3) {
          background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }
        &:nth-child(4) {
          background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        }

        .stats-title {
          font-size: 14px;
          opacity: 0.9;
          margin-bottom: 10px;
        }

        .stats-value {
          font-size: 32px;
          font-weight: 700;
          line-height: 1;
        }
      }
    }

    .sheet-selection {
      margin-bottom: 24px;

      h4 {
        font-size: 14px;
        margin-bottom: 12px;
      }
      
      .sheet-checkbox-group {
        margin-top: 10px;
        
        .sheet-checkbox {
          display: block;
          margin-bottom: 10px;
          padding: 8px;
          border: 1px solid #e4e7ed;
          border-radius: 4px;
          transition: all 0.3s;
          
          &:hover {
            background-color: #f5f7fa;
            border-color: #409eff;
          }
          
          .sheet-info {
            display: flex;
            align-items: center;
            gap: 8px;
            
            .sheet-name {
              font-weight: 500;
            }
            
            .sheet-period {
              color: #409eff;
              font-weight: 500;
            }
            
            .sheet-stats {
              color: #909399;
              font-size: 12px;
            }
          }
        }
      }
    }

    .header-detection-info {
      margin-bottom: 20px;
      
      .el-alert {
        border-radius: 8px;
      }
    }

    .sample-preview {
      h4 {
        font-size: 14px;
        margin-bottom: 12px;
      }
    }
  }
}

// 字段映射样式
.mapping-section {
  .mapping-form {
    .mapping-group {
      h4 {
        font-size: 16px;
        margin-bottom: 16px;
        color: #303133;
      }

      .field-preview {
        font-size: 12px;
        color: #909399;
        margin-top: 4px;
        padding: 4px 8px;
        background-color: #f8f9fa;
        border-radius: 4px;
      }
    }

    .smart-mapping {
      margin-top: 24px;
      text-align: center;

      .mapping-tip {
        margin-left: 12px;
        font-size: 12px;
        color: #909399;
      }
    }
  }
}

// 数据预览样式
.preview-section {
  .preview-note {
    color: #909399;
    font-size: 13px;
    font-weight: normal;
  }
  
  .preview-stats {
    display: flex;
    gap: 24px;
    margin-bottom: 16px;

    .stat-item {
      .stat-label {
        font-size: 14px;
        color: #909399;
      }

      .stat-value {
        font-weight: 600;
        margin-left: 8px;
      }
      .stat-note {
        font-size: 12px;
        color: #909399;
        margin-left: 4px;
        font-weight: normal;
      }
      
      .stat-value {
        &.success {
          color: #67c23a;
        }

        &.warning {
          color: #e6a23c;
        }

        &.danger {
          color: #f56c6c;
        }
        
        &.info {
          color: #409eff;
        }
      }
    }
  }

  .preview-filters {
    margin-bottom: 16px;
  }

  .data-options {
    margin-top: 16px;
    padding: 16px;
    background-color: #f8f9fa;
    border-radius: 8px;

    h4 {
      font-size: 14px;
      margin-bottom: 12px;
    }

    .el-checkbox {
      margin-right: 24px;
    }
    
    .batch-import-config {
      margin-top: 20px;
      padding: 16px;
      background-color: #f0f9ff;
      border-radius: 8px;
      border: 1px solid #e0f2fe;
      
      h5 {
        font-size: 14px;
        margin-bottom: 12px;
        color: #0369a1;
      }
      
      .batch-info {
        display: flex;
        align-items: center;
        margin-bottom: 12px;
        font-size: 13px;
        color: #0c4a6e;
        
        .info-icon {
          margin-right: 8px;
          color: #0284c7;
        }
      }
      
      .el-form-item {
        margin-bottom: 0;
        
        .batch-tip {
          margin-left: 12px;
          font-size: 12px;
          color: #6b7280;
        }
      }
    }
  }
}

// 导入进度样式
.importing-section {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;

  .importing-progress {
    text-align: center;
    max-width: 400px;

    .loading-icon {
      font-size: 48px;
      color: #409eff;
      animation: rotate 2s linear infinite;
      margin-bottom: 16px;
    }

    h3 {
      margin-bottom: 8px;
    }

    p {
      margin-bottom: 16px;
      color: #909399;
    }

    .progress-stats {
      display: flex;
      justify-content: space-between;
      margin-top: 16px;
      font-size: 12px;
      color: #909399;
    }
  }
}

.import-result {
  .result-details {
    margin-bottom: 24px;

    .result-stats {
      display: flex;
      gap: 16px;
      justify-content: center;
      margin-bottom: 16px;

      .stat-card {
        text-align: center;
        padding: 16px;
        border-radius: 8px;
        border: 1px solid #dcdfe6;

        .stat-number {
          font-size: 24px;
          font-weight: 600;
          margin-bottom: 4px;
        }

        .stat-label {
          font-size: 12px;
          color: #909399;
        }

        &.success {
          border-color: #67c23a;
          .stat-number {
            color: #67c23a;
          }
        }

        &.warning {
          border-color: #e6a23c;
          .stat-number {
            color: #e6a23c;
          }
        }

        &.danger {
          border-color: #f56c6c;
          .stat-number {
            color: #f56c6c;
          }
        }
        
        &.clickable {
          cursor: pointer;
          transition: all 0.3s;
          
          &:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(245, 108, 108, 0.2);
          }
        }
        
        .stat-hint {
          font-size: 11px;
          color: #909399;
          margin-top: 4px;
          opacity: 0.8;
        }
      }
    }
  }

  .action-buttons {
    display: flex;
    gap: 12px;
    justify-content: center;
  }
}

.error-details {
  .error-list {
    .error-item {
      display: flex;
      align-items: flex-start;
      padding: 12px;
      margin-bottom: 8px;
      background-color: #fef0f0;
      border-left: 3px solid #f56c6c;
      border-radius: 4px;
      
      .error-icon {
        color: #f56c6c;
        margin-right: 8px;
        margin-top: 2px;
        flex-shrink: 0;
      }
      
      .error-text {
        color: #606266;
        line-height: 1.5;
        word-break: break-word;
      }
    }
  }
  
  .no-errors {
    text-align: center;
    padding: 40px 0;
  }
}

.action-footer {
  display: flex;
  justify-content: center;
  gap: 16px;
  padding: 20px;
  border-top: 1px solid #dcdfe6;
}

// 表格行样式
:deep(.el-table) {
  .invalid-row {
    background-color: #fdf0f0 !important;
  }

  .duplicate-row {
    background-color: #fdf9e8 !important;
  }

  .first-duplicate-row {
    background-color: #e8f4f8 !important;
  }

  .invalid-data {
    color: #f56c6c;
  }

  .error-text {
    color: #f56c6c;
    font-size: 12px;
  }

  .no-data {
    color: #c0c4cc;
    font-style: italic;
  }
  
  .editable-cell {
    padding: 0;
    
    :deep(.el-input__inner) {
      border-color: #409eff;
    }
    
    :deep(.el-input-number) {
      width: 100%;
      
      .el-input__inner {
        border-color: #409eff;
      }
    }
  }
  
  .action-buttons {
    display: flex;
    gap: 8px;
    justify-content: center;
  }
}

// 模板预览对话框样式
.template-preview {
  h3, h4 {
    color: #303133;
    margin-bottom: 12px;
  }

  p {
    color: #909399;
    margin-bottom: 16px;
  }

  ul {
    margin-bottom: 24px;
    padding-left: 20px;

    li {
      margin-bottom: 8px;
      color: #606266;

      strong {
        color: #303133;
      }
    }
  }

  .template-example {
    margin-top: 24px;
    padding: 16px;
    background-color: #f8f9fa;
    border-radius: 8px;
  }
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

// 响应式设计
@media (max-width: 768px) {
  .material-import-container {
    padding: 10px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .stats-cards {
    grid-template-columns: repeat(2, 1fr) !important;
  }

  .preview-stats {
    flex-direction: column;
    gap: 12px !important;
  }

  .price-type-buttons {
    flex-direction: column !important;
    align-items: stretch;
    
    .price-type-btn {
      min-width: 100% !important;
      min-height: 60px !important;
      flex-direction: row !important;
      justify-content: flex-start !important;
      
      .btn-icon {
        margin-bottom: 0 !important;
        margin-right: 12px !important;
      }
    }
  }

  .action-footer {
    flex-direction: column;

    .el-button {
      width: 100%;
    }
  }
}
</style>
