<template>
  <div class="excel-upload-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">项目材料上传</h1>
        <p class="page-subtitle">上传Excel文件，智能解析并导入项目材料清单数据</p>
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
        <el-step title="选择分类" description="选择材料分类层级" />
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

              <!-- 工作表选择 -->
              <div v-if="analysisResult.sheets.length > 1" class="sheet-selection">
                <h4>请选择要导入的工作表:</h4>
                <el-radio-group v-model="selectedSheet">
                  <el-radio
                    v-for="sheet in analysisResult.sheets"
                    :key="sheet.name"
                    :label="sheet.name"
                  >
                    {{ sheet.name }} ({{ sheet.rows }}行, {{ sheet.columns }}列)
                  </el-radio>
                </el-radio-group>
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
                    
                    <el-form-item label="单价" required>
                      <el-select v-model="fieldMapping.unit_price" placeholder="请选择">
                        <el-option
                          v-for="(column, index) in availableColumns"
                          :key="index"
                          :label="column"
                          :value="index"
                        />
                      </el-select>
                      <div class="field-preview">
                        {{ getFieldPreview('unit_price') }}
                      </div>
                    </el-form-item>
                  </el-form>
                </div>
              </el-col>

              <el-col :span="12">
                <div class="mapping-group">
                  <h4>可选字段</h4>
                  <el-form :model="fieldMapping" label-width="100px">
                    <el-form-item label="编码">
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
                    
                    <el-form-item label="数量">
                      <el-select v-model="fieldMapping.quantity" placeholder="请选择">
                        <el-option label="不映射" value="" />
                        <el-option
                          v-for="(column, index) in availableColumns"
                          :key="index"
                          :label="column"
                          :value="index"
                        />
                      </el-select>
                      <div class="field-preview">
                        {{ getFieldPreview('quantity') }}
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
            </div>
            <div class="stat-item">
              <span class="stat-label">异常数据:</span>
              <span class="stat-value danger">{{ invalidDataCount }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">重复数据:</span>
              <span class="stat-value warning">{{ duplicateDataCount }}</span>
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
            <el-table-column prop="material_code" label="编码" width="120" show-overflow-tooltip />
            <el-table-column prop="name" label="材料名称" min-width="150" show-overflow-tooltip />
            <el-table-column prop="specification" label="规格型号" width="120" show-overflow-tooltip />
            <el-table-column prop="unit" label="单位" width="80" />
            <el-table-column prop="unit_price" label="单价" width="100">
              <template #default="{ row }">
                <span :class="{ 'invalid-data': !row.valid }">
                  ¥{{ formatNumber(row.unit_price) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="quantity" label="数量" width="100">
              <template #default="{ row }">
                {{ formatNumber(row.quantity) }}
              </template>
            </el-table-column>
            <el-table-column prop="remarks" label="备注" width="150" show-overflow-tooltip />
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag v-if="row.valid" type="success" size="small">正常</el-tag>
                <el-tag v-else-if="row.duplicate" type="warning" size="small">重复</el-tag>
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
          </el-table>

          <!-- 数据处理选项 -->
          <div class="data-options">
            <h4>数据处理选项:</h4>
            <el-checkbox v-model="importOptions.skipInvalid">跳过异常数据</el-checkbox>
            <el-checkbox v-model="importOptions.skipDuplicate">跳过重复数据</el-checkbox>
            <el-checkbox v-model="importOptions.autoFix">自动修复可修复的数据</el-checkbox>
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
                  <div class="stat-card warning">
                    <div class="stat-number">{{ importResult.skippedCount }}</div>
                    <div class="stat-label">跳过数据</div>
                  </div>
                  <div class="stat-card danger">
                    <div class="stat-number">{{ importResult.failedCount }}</div>
                    <div class="stat-label">导入失败</div>
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
                <el-button type="primary" @click="goToProject">
                  查看项目
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

    <!-- 模板预览对话框 -->
    <el-dialog v-model="showTemplatePreview" title="Excel模板说明" width="800px">
      <div class="template-preview">
        <h3>标准Excel模板格式说明</h3>
        <p>请按照以下格式准备您的Excel文件:</p>
        
        <h4>必填字段 (A-C列):</h4>
        <ul>
          <li><strong>A列 - 材料名称:</strong> 材料的标准名称，不能为空</li>
          <li><strong>B列 - 单位:</strong> 材料的计量单位，如：吨、立方米、平方米等</li>
          <li><strong>C列 - 单价:</strong> 材料的单价，仅输入数字，不要包含货币符号</li>
        </ul>
        
        <h4>可选字段 (D-F列):</h4>
        <ul>
          <li><strong>D列 - 规格型号:</strong> 材料的具体规格，可为空</li>
          <li><strong>E列 - 数量:</strong> 材料数量，仅输入数字</li>
          <li><strong>F列 - 备注:</strong> 其他说明信息</li>
        </ul>
        
        <h4>注意事项:</h4>
        <ul>
          <li>第一行请设置为表头，系统会自动识别</li>
          <li>单价和数量字段请只输入数字，不要包含文字</li>
          <li>请确保数据的完整性和准确性</li>
          <li>支持多个工作表，系统会让您选择要导入的工作表</li>
        </ul>

        <div class="template-example">
          <h4>示例数据:</h4>
          <el-table :data="templateExample" border style="width: 100%">
            <el-table-column prop="code" label="编码" />
            <el-table-column prop="name" label="材料名称" />
            <el-table-column prop="unit" label="单位" />
            <el-table-column prop="price" label="单价" />
            <el-table-column prop="spec" label="规格型号" />
            <el-table-column prop="quantity" label="数量" />
            <el-table-column prop="remark" label="备注" />
          </el-table>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
console.log('🚀 项目材料上传页面 - 统一版本加载成功! v3.0')
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  UploadFilled,
  Download,
  View,
  Document,
  Tools,
  Loading
} from '@element-plus/icons-vue'
import { formatNumber } from '@/utils'
// 使用项目材料的API函数
import { parseProjectMaterialExcel, addProjectMaterials, getProjectMaterialPreviewData } from '@/api/projects'

const route = useRoute()
const router = useRouter()

// 获取项目ID
const projectId = route.params.projectId || route.params.id

// 响应式数据
const currentStep = ref(0)
const analyzing = ref(false)
const importing = ref(false)
const downloading = ref(false)
const showTemplatePreview = ref(false)
const uploadRef = ref()

const fileList = ref([])
const analysisResult = ref(null)
const selectedSheet = ref('')
const availableColumns = ref([])
const previewData = ref([])
const previewFilter = ref('all')
// 完整导入数据的响应式管理
const fullImportData = ref([])
const hasFullData = computed(() => fullImportData.value.length > 0)

// 字段映射配置
const fieldMapping = reactive({
  material_code: '',
  name: '',
  specification: '',
  unit: '',
  unit_price: '',
  quantity: '',
  remarks: ''
})

// 导入选项
const importOptions = reactive({
  skipInvalid: true,
  skipDuplicate: true,
  autoFix: true
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

// 模板示例数据
const templateExample = ref([
  {
    code: 'MT001',
    name: '水泥',
    unit: '吨',
    price: 580.00,
    spec: 'P.O 42.5',
    quantity: 10,
    remark: '普通硅酸盐水泥'
  },
  {
    code: 'MT002',
    name: '钢筋',
    unit: '吨',
    price: 4200.00,
    spec: 'HRB400 Φ12',
    quantity: 5,
    remark: '热轧带肋钢筋'
  }
])

// 计算属性
const canNext = computed(() => {
  switch (currentStep.value) {
    case 0:
      return fileList.value.length > 0
    case 1:
      return analysisResult.value !== null
    case 2:
      return fieldMapping.name !== '' && fieldMapping.unit !== '' && fieldMapping.unit_price !== ''
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
        return row.data[availableColumns.value[columnIndex]] || ''
      } else {
        return row[`col_${columnIndex}`] || ''
      }
    }
    
    const name = getValue('name') || ''
    const unit = getValue('unit') || ''
    const unitPrice = parseFloat(getValue('unit_price')) || 0
    const specification = getValue('specification') || ''
    
    // 验证数据有效性
    const isValid = name.trim() !== '' && unit.trim() !== '' && unitPrice > 0 && !isNaN(unitPrice)
    
    // 生成重复检测键（基于材料名称 + 规格型号 + 单位的组合）
    const duplicateKey = `${name.trim()}_${specification.trim()}_${unit.trim()}`.toLowerCase()
    
    const itemData = {
      index: i,
      duplicateKey,
      isValid,
      name,
      specification,
      unit,
      unitPrice
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
    
    // 统计分类：重复 > 无效 > 有效
    if (isDuplicate) {
      duplicateCount++
    } else if (item.isValid) {
      validCount++
    } else {
      invalidCount++
    }
    
    // 同时更新原始数据的标记
    if (sourceData[item.index]) {
      sourceData[item.index].belongsToDuplicateGroup = hasMultiple
      sourceData[item.index].isFirstInGroup = isFirstOccurrence && hasMultiple
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
        return row.data[availableColumns.value[columnIndex]] || ''
      } else {
        return row[`col_${columnIndex}`] || ''
      }
    }
      
    const name = getValue('name') || ''
    const specification = getValue('specification') || ''
    const unit = getValue('unit') || ''
    const unitPrice = parseFloat(getValue('unit_price')) || 0
    
    const item = {
      row_index: i,
      name: name,
      specification: specification,
      unit: unit,
      unit_price: unitPrice,
      quantity: parseFloat(getValue('quantity')) || 0,
      remarks: getValue('remarks') || '',
      valid: true,
      duplicate: false,
      errors: []
    }
    
    // 生成重复检测键
    const duplicateKey = `${name.trim()}_${specification.trim()}_${unit.trim()}`.toLowerCase()
    item.duplicateKey = duplicateKey
    
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
      item.valid = false
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
    
    if (!item.unit_price || item.unit_price <= 0) {
      item.valid = false
      item.errors.push('单价必须大于0')
    }
    
    // 检查是否为数字
    if (isNaN(item.unit_price)) {
      item.valid = false
      item.errors.push('单价格式错误')
    }
    
    // 清理临时字段
    delete item.duplicateKey
    
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
      return previewData.value.filter(item => item.belongsToDuplicateGroup)
    }
    return previewData.value
  }

  const processedFullData = processFullDataWithMapping(fullImportData.value)
  
  if (filterType === 'invalid') {
    return processedFullData.filter(item => !item.valid && !item.duplicate)
  } else if (filterType === 'duplicate') {
    return processedFullData.filter(item => item.belongsToDuplicateGroup)
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

// 步骤控制方法
const nextStep = async () => {
  try {
    switch (currentStep.value) {
      case 0:
        await analyzeFile()
        break
      case 1:
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
    // 使用项目材料的解析API
    const response = await parseProjectMaterialExcel(projectId, file.raw || file, {
      sheet_name: selectedSheet.value
    })
    
    const data = response.data || response
    analysisResult.value = data
    availableColumns.value = data.columns || []
    selectedSheet.value = data.sheets?.[0]?.name || 'Sheet1'
    
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

// 智能映射
const autoMapping = () => {
  const columns = availableColumns.value
  
  const mappingRules = {
    material_code: [
      '编码', '材料编码', '编号', '材料编号', '代码', '材料代码', '项目编码',
      'code', 'material_code', 'item_code', 'number'
    ],
    name: [
      '材料名称', '名称', '材料', '品名', '项目名称', '工程名称', '商品名称',
      'material', 'name', 'item', 'product'
    ],
    specification: [
      '规格', '型号', '规格型号', '规格/型号', '技术规格', '产品规格', '参数',
      'specification', 'model', 'spec', 'type'
    ],
    unit: [
      '单位', '计量单位', '计价单位', '工程量单位',
      'unit', 'measure', 'uom'
    ],
    unit_price: [
      '单价', '价格', '单位价格', '综合单价', '材料单价', '不含税单价', '含税单价', '市场价',
      'price', 'unit_price', 'unitprice', 'cost'
    ],
    quantity: [
      '数量', '工程量', '用量', '需求量', '消耗量',
      'quantity', 'amount', 'qty'
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
      let score = 0
      
      if (keywords.includes(columnStr)) {
        score = 100
      } else {
        keywords.forEach(keyword => {
          if (columnStr.includes(keyword)) {
            score += 50
          } else if (columnStr.toLowerCase().includes(keyword.toLowerCase())) {
            score += 30
          }
        })
        
        keywords.forEach(keyword => {
          const similarity = calculateSimilarity(columnStr, keyword)
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
        console.log('尝试使用新API获取预览数据...', { file: currentFile, sheet: selectedSheet.value })
        
        // 使用新的API获取完整预览数据
        const response = await getProjectMaterialPreviewData(projectId, currentFile, {
          sheet_name: selectedSheet.value,
          max_rows: 2000  // 最多预览2000行
        })
        
        if (response.code === 200 && response.data) {
          // 保存完整数据用于导入
          fullImportData.value = response.data.fullData || response.data.previewData
          sourceData = response.data.previewData  // 只用于预览显示
          console.log('新API获取成功，预览数据:', sourceData.length, '行，完整数据:', fullImportData.value.length, '行')
        } else {
          throw new Error(response.message || '新API调用失败')
        }
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
        
        // 支持两种数据访问方式
        if (row.data && availableColumns.value[columnIndex]) {
          // 使用列名访问
          return row.data[availableColumns.value[columnIndex]] || ''
        } else {
          // 使用索引访问（向后兼容）
          return row[`col_${columnIndex}`] || ''
        }
      }
        
        const name = getValue('name') || ''
        const specification = getValue('specification') || ''
        const unit = getValue('unit') || ''
        const unitPrice = parseFloat(getValue('unit_price')) || 0
        
        const item = {
          row_index: i,
          name: name,
          specification: specification,
          unit: unit,
          unit_price: unitPrice,
          quantity: parseFloat(getValue('quantity')) || 0,
          remarks: getValue('remarks') || '',
          valid: true,
          duplicate: false,
          errors: []
        }
        
        // 生成重复检测键 - 改进算法：考虑价格差异
        // 如果价格差异超过5%，则认为不是重复项
        const baseKey = `${name.trim()}_${specification.trim()}_${unit.trim()}`.toLowerCase()
        const priceKey = Math.round(unitPrice * 100) // 精确到分，避免浮点数误差
        const duplicateKey = `${baseKey}_${priceKey}`
        item.duplicateKey = duplicateKey
        item.baseKey = baseKey  // 保存基础键用于分析
        
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
        item.valid = false
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
      
      if (!item.unit_price || item.unit_price <= 0) {
        item.valid = false
        item.errors.push('单价必须大于0')
      }
      
      // 检查是否为数字
      if (isNaN(item.unit_price)) {
        item.valid = false
        item.errors.push('单价格式错误')
      }
      
      // 清理临时字段
      delete item.duplicateKey
      
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
    
    const getValue = (fieldName) => {
      const columnIndex = fieldMapping[fieldName]
      if (columnIndex === '' || columnIndex === undefined) return ''
      
      if (row.data && availableColumns.value[columnIndex]) {
        return row.data[availableColumns.value[columnIndex]] || ''
      } else {
        return row[`col_${columnIndex}`] || ''
      }
    }
    
    const item = {
      name: getValue('name') || '',
      specification: getValue('specification') || '',
      unit: getValue('unit') || '',
      unit_price: parseFloat(getValue('unit_price')) || 0,
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
    if (!item.unit_price || item.unit_price <= 0) {
      item.valid = false
    }
    if (isNaN(item.unit_price)) {
      item.valid = false
    }
    
    // 生成重复检测键 - 改进算法：考虑价格差异
    const baseKey = `${item.name.trim()}_${item.specification.trim()}_${item.unit.trim()}`.toLowerCase()
    const priceKey = Math.round(item.unit_price * 100) // 精确到分，避免浮点数误差
    const duplicateKey = `${baseKey}_${priceKey}`
    item.duplicateKey = duplicateKey
    item.baseKey = baseKey  // 保存基础键用于分析
    
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
      
      const getValue = (fieldName) => {
        const columnIndex = fieldMapping[fieldName]
        if (columnIndex === '' || columnIndex === undefined) return ''
        
        if (row.data && availableColumns.value[columnIndex]) {
          return row.data[availableColumns.value[columnIndex]] || ''
        } else {
          return row[`col_${columnIndex}`] || ''
        }
      }
      
      const item = {
        name: getValue('name') || '',
        specification: getValue('specification') || '',
        unit: getValue('unit') || '',
        unit_price: parseFloat(getValue('unit_price')) || 0,
        quantity: parseFloat(getValue('quantity')) || 0,
        remarks: getValue('remarks') || '',
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
      if (!item.unit_price || item.unit_price <= 0) {
        item.valid = false
      }
      if (isNaN(item.unit_price)) {
        item.valid = false
      }
      
      // 生成重复检测键 - 改进算法：考虑价格差异
      const baseKey = `${item.name.trim()}_${item.specification.trim()}_${item.unit.trim()}`.toLowerCase()
      const priceKey = Math.round(item.unit_price * 100) // 精确到分，避免浮点数误差
      const duplicateKey = `${baseKey}_${priceKey}`
      item.duplicateKey = duplicateKey
      item.baseKey = baseKey  // 保存基础键用于分析
      
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
      
      // 准备项目材料数据结构
      const materialData = {
        name: item.name || '',
        specification: item.specification || '',
        unit: item.unit || '',
        unit_price: item.unit_price || 0,
        quantity: item.quantity || 0,
        remarks: item.remarks || ''
      }
      
      materialsToImport.push(materialData)
    }
    
    const totalCount = materialsToImport.length
    importProgress.totalCount = totalCount
    
    if (totalCount === 0) {
      throw new Error('没有可导入的数据')
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
    
    importProgress.message = '正在导入项目材料数据...'
    importProgress.percentage = 50
    
    // 使用项目材料导入API
    const response = await addProjectMaterials(projectId, importData)
    const result = response.data?.data || response.data || response
    
    importProgress.percentage = 100
    importProgress.processed = totalCount
    importProgress.success = result.success_count || 0
    importProgress.failed = result.failed_count || 0
    
    importResult.success = result.success_count > 0
    importResult.title = importResult.success ? '导入完成' : '导入失败'
    importResult.message = importResult.success 
      ? `成功导入 ${result.success_count} 条材料数据到项目`
      : '导入过程中出现错误，请查看详细信息'
    importResult.totalCount = result.total_count || totalCount
    importResult.successCount = result.success_count || 0
    importResult.failedCount = result.failed_count || 0
    importResult.skippedCount = result.skipped_count || 0
    
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
  } finally {
    importing.value = false
  }
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
  resetAnalysis()
  resetMapping()
  resetPreview()
  resetImport()
}

const resetAnalysis = () => {
  analysisResult.value = null
  selectedSheet.value = ''
  availableColumns.value = []
}

const resetMapping = () => {
  Object.assign(fieldMapping, {
    name: '',
    specification: '',
    unit: '',
    unit_price: '',
    quantity: '',
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
    skippedCount: 0
  })
}

// 其他操作
const downloadTemplate = async () => {
  try {
    downloading.value = true
    ElMessage.info('项目材料模板下载功能开发中...')
  } catch (error) {
    console.error('下载模板失败:', error)
    ElMessage.error('下载模板失败，请稍后重试')
  } finally {
    downloading.value = false
  }
}

const downloadImportReport = () => {
  ElMessage.info('下载导入报告功能开发中...')
}

const goToProject = () => {
  if (projectId) {
    router.push({
      name: 'ProjectDetail',
      params: { id: projectId },
      query: { refresh: 'materials', timestamp: Date.now().toString() }
    })
  } else {
    router.push('/projects')
  }
}

// 根据选择的工作表更新数据样本
const updateSheetData = async () => {
  if (!analysisResult.value || !selectedSheet.value) return
  
  try {
    analyzing.value = true
    console.log('切换到工作表:', selectedSheet.value)
    
    const file = fileList.value[0]
    const response = await parseProjectMaterialExcel(projectId, file.raw || file, {
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

// 生命周期
onMounted(() => {
  // 初始化
})
</script>

<style lang="scss" scoped>
.excel-upload-container {
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

// 文件上传样式
.upload-section {
  .upload-area {
    margin-bottom: 24px;
    
    :deep(.el-upload-dragger) {
      width: 100%;
      padding: 60px 20px;
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

        &.success {
          color: #67c23a;
        }

        &.warning {
          color: #e6a23c;
        }

        &.danger {
          color: #f56c6c;
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
      }
    }
  }

  .action-buttons {
    display: flex;
    gap: 12px;
    justify-content: center;
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
  .excel-upload-container {
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

  .action-footer {
    flex-direction: column;

    .el-button {
      width: 100%;
    }
  }
}
</style>
