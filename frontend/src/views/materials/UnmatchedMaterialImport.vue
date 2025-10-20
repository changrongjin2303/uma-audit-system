<template>
  <div class="unmatched-material-import-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">无信息价导入</h1>
        <p class="page-subtitle">上传Excel文件，智能解析并导入无信息价材料数据到材料库</p>
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
        <!-- 日期选择区域 -->
        <div class="date-selection-section">
          <h3>日期选择</h3>
          <p class="section-desc">请选择材料的日期信息</p>

          <div class="date-selection">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="材料日期" required>
                  <el-date-picker
                    v-model="materialDate"
                    type="date"
                    placeholder="请选择材料日期"
                    format="YYYY-MM-DD"
                    value-format="YYYY-MM-DD"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <div class="selection-summary" v-if="materialDate">
              <el-alert
                :title="`已选择日期: ${materialDate}`"
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
          </div>
        </div>
      </div>

      <!-- 步骤2: 结构分析结果 -->
      <div v-if="currentStep === 1" class="step-content">
        <div class="analysis-result-section">
          <h3>文件结构分析结果</h3>
          <p class="section-desc">系统已自动分析您的Excel文件结构</p>

          <el-alert
            v-if="analysisResult"
            type="success"
            :closable="false"
            show-icon
          >
            <template #title>
              分析完成：共检测到 {{ analysisResult.total_rows || 0 }} 行数据，{{ availableColumns.length }} 个字段
            </template>
          </el-alert>

          <div v-if="analysisResult" class="analysis-details">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="文件名">{{ fileList[0]?.name }}</el-descriptions-item>
              <el-descriptions-item label="数据行数">{{ analysisResult.total_rows || 0 }}</el-descriptions-item>
              <el-descriptions-item label="检测到的字段数">{{ availableColumns.length }}</el-descriptions-item>
              <el-descriptions-item label="建议编码">{{ analysisResult.encoding || 'UTF-8' }}</el-descriptions-item>
            </el-descriptions>

            <h4 style="margin-top: 20px;">检测到的字段列表：</h4>
            <el-tag
              v-for="col in availableColumns"
              :key="col"
              style="margin: 5px;"
              type="info"
            >
              {{ col }}
            </el-tag>
          </div>
        </div>
      </div>

      <!-- 步骤3: 字段映射 -->
      <div v-if="currentStep === 2" class="step-content">
        <div class="field-mapping-section">
          <h3>字段映射配置</h3>
          <p class="section-desc">请将Excel文件中的列映射到系统字段（<span style="color: red;">*</span> 为必填字段）</p>

          <el-form label-width="120px" class="mapping-form">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="序号">
                  <el-select v-model="fieldMapping.serial_number" placeholder="选择对应列" clearable>
                    <el-option
                      v-for="col in availableColumns"
                      :key="col"
                      :label="col"
                      :value="col"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="材料名称" required>
                  <el-select v-model="fieldMapping.name" placeholder="选择对应列">
                    <el-option
                      v-for="col in availableColumns"
                      :key="col"
                      :label="col"
                      :value="col"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="规格型号">
                  <el-select v-model="fieldMapping.specification" placeholder="选择对应列" clearable>
                    <el-option
                      v-for="col in availableColumns"
                      :key="col"
                      :label="col"
                      :value="col"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="品牌">
                  <el-select v-model="fieldMapping.brand" placeholder="选择对应列" clearable>
                    <el-option
                      v-for="col in availableColumns"
                      :key="col"
                      :label="col"
                      :value="col"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="单位">
                  <el-select v-model="fieldMapping.unit" placeholder="选择对应列" clearable>
                    <el-option
                      v-for="col in availableColumns"
                      :key="col"
                      :label="col"
                      :value="col"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="除税价">
                  <el-select v-model="fieldMapping.price_excluding_tax" placeholder="选择对应列" clearable>
                    <el-option
                      v-for="col in availableColumns"
                      :key="col"
                      :label="col"
                      :value="col"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="备注">
                  <el-select v-model="fieldMapping.notes" placeholder="选择对应列" clearable>
                    <el-option
                      v-for="col in availableColumns"
                      :key="col"
                      :label="col"
                      :value="col"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>

          <el-alert
            type="warning"
            :closable="false"
            style="margin-top: 20px;"
          >
            <template #title>
              提示：材料名称为必填字段，请务必映射正确。其他字段可选
            </template>
          </el-alert>
        </div>
      </div>

      <!-- 步骤4: 数据预览 -->
      <div v-if="currentStep === 3" class="step-content">
        <div class="preview-section">
          <h3>数据预览</h3>
          <p class="section-desc">预览前20条数据，确认映射正确后可继续导入</p>

          <el-table
            v-loading="processing"
            :data="previewData"
            stripe
            border
            max-height="400"
            style="width: 100%; margin-top: 20px;"
          >
            <el-table-column prop="serial_number" label="序号" width="100" />
            <el-table-column prop="name" label="材料名称" min-width="200" show-overflow-tooltip />
            <el-table-column prop="specification" label="规格型号" width="150" show-overflow-tooltip />
            <el-table-column prop="brand" label="品牌" width="120" show-overflow-tooltip />
            <el-table-column prop="unit" label="单位" width="80" />
            <el-table-column prop="price_excluding_tax" label="除税价" width="120">
              <template #default="{ row }">
                <span v-if="row.price_excluding_tax">{{ row.price_excluding_tax }}</span>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column prop="notes" label="备注" width="150" show-overflow-tooltip />
          </el-table>

          <el-alert
            type="info"
            :closable="false"
            style="margin-top: 20px;"
          >
            <template #title>
              已加载 {{ previewData.length }} 条预览数据（最多显示前20条）
            </template>
          </el-alert>
        </div>
      </div>

      <!-- 步骤5: 导入确认 -->
      <div v-if="currentStep === 4" class="step-content">
        <div class="import-summary-section">
          <h3>导入确认</h3>
          <p class="section-desc">请确认以下信息无误后，点击"确认导入"按钮开始导入数据</p>

          <el-descriptions :column="2" border style="margin-top: 20px;">
            <el-descriptions-item label="材料日期">{{ materialDate }}</el-descriptions-item>
            <el-descriptions-item label="文件名">{{ fileList[0]?.name }}</el-descriptions-item>
            <el-descriptions-item label="预计导入数据量">{{ analysisResult?.total_rows || 0 }} 条</el-descriptions-item>
            <el-descriptions-item label="跳过重复数据">是</el-descriptions-item>
          </el-descriptions>

          <el-alert
            type="warning"
            :closable="false"
            style="margin-top: 20px;"
          >
            <template #title>
              注意：导入过程不可中断，请确认所有信息无误后再进行操作
            </template>
          </el-alert>

          <!-- 导入结果显示 -->
          <div v-if="importSummary.total > 0" class="import-result" style="margin-top: 20px;">
            <el-alert
              :type="importSummary.failed === 0 ? 'success' : 'warning'"
              :closable="false"
            >
              <template #title>
                导入完成：成功 {{ importSummary.success }} 条，失败 {{ importSummary.failed }} 条
              </template>
            </el-alert>

            <div v-if="importSummary.errors.length > 0" style="margin-top: 10px;">
              <h4>错误详情：</h4>
              <el-scrollbar max-height="200px">
                <div v-for="(error, index) in importSummary.errors" :key="index" class="error-item">
                  {{ error }}
                </div>
              </el-scrollbar>
            </div>
          </div>
        </div>
      </div>

      <!-- 步骤导航按钮 -->
      <div class="step-actions">
        <el-button v-if="currentStep > 0" @click="prevStep">
          上一步
        </el-button>
        <el-button
          v-if="currentStep < 4"
          type="primary"
          @click="nextStep"
          :disabled="!canProceed"
          :loading="processing"
        >
          {{ currentStep === 0 ? '开始分析' : '下一步' }}
        </el-button>
        <el-button
          v-if="currentStep === 4"
          type="success"
          @click="confirmImport"
          :loading="importing"
        >
          确认导入
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  UploadFilled,
  Document,
  Download,
  View,
  Location
} from '@element-plus/icons-vue'
import {
  getUnmatchedPreviewData,
  parseUnmatchedExcelStructure,
  importUnmatchedMaterials
} from '@/api/unmatchedMaterials'

const router = useRouter()

// 响应式数据
const currentStep = ref(0)
const materialDate = ref('')
const fileList = ref([])
const uploadRef = ref()
const processing = ref(false)
const importing = ref(false)
const analyzing = ref(false)

// 文件分析结果
const analysisResult = ref(null)
const selectedSheet = ref('')
const availableColumns = ref([])

// 字段映射
const fieldMapping = ref({
  serial_number: null,
  name: null,
  specification: null,
  brand: null,
  unit: null,
  price_excluding_tax: null,
  date: null,
  notes: null
})

// 预览数据
const previewData = ref([])
const importSummary = ref({
  total: 0,
  success: 0,
  failed: 0,
  errors: []
})

// 计算属性
const canProceed = computed(() => {
  if (currentStep.value === 0) {
    return materialDate.value && fileList.value.length > 0
  }
  return true
})

// 文件大小格式化
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// 文件选择处理
const handleFileChange = (file, uploadFiles) => {
  fileList.value = uploadFiles
}

const handleFileRemove = (file, uploadFiles) => {
  fileList.value = uploadFiles
}

const beforeUpload = (file) => {
  const isValidType = /\.(xlsx|xls|csv)$/i.test(file.name)
  const isLt50M = file.size / 1024 / 1024 < 50

  if (!isValidType) {
    ElMessage.error('只能上传 Excel 或 CSV 格式的文件!')
    return false
  }
  if (!isLt50M) {
    ElMessage.error('文件大小不能超过 50MB!')
    return false
  }
  return true
}

const handleExceed = () => {
  ElMessage.warning('只能上传一个文件，请先删除已选文件')
}

// 步骤导航
const nextStep = async () => {
  if (currentStep.value === 0) {
    // 分析文件
    await analyzeFile()
  } else if (currentStep.value === 2) {
    // 验证字段映射 - 只要求名称必填
    if (!fieldMapping.value.name) {
      ElMessage.error('请至少映射材料名称字段')
      return
    }
    // 加载预览数据
    await loadPreviewData()
  }
  if (currentStep.value < 4) {
    currentStep.value++
  }
}

const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

// 分析文件
const analyzeFile = async () => {
  if (!fileList.value.length) {
    ElMessage.error('请先选择文件')
    return
  }

  analyzing.value = true
  processing.value = true
  try {
    const file = fileList.value[0].raw
    const response = await parseUnmatchedExcelStructure(file)
    analysisResult.value = response.data?.data || response.data

    // 设置默认选中的工作表
    if (analysisResult.value.sheets && analysisResult.value.sheets.length > 0) {
      selectedSheet.value = analysisResult.value.sheets[0].name
    }

    // 获取可用列
    availableColumns.value = analysisResult.value.columns || []

    // 智能映射字段
    autoMapFields()

    ElMessage.success('文件分析完成')
  } catch (error) {
    console.error('文件分析失败:', error)
    ElMessage.error('文件分析失败: ' + (error.message || error))
  } finally {
    analyzing.value = false
    processing.value = false
  }
}

// 智能映射字段
const autoMapFields = () => {
  const columns = availableColumns.value.map(c => c.toLowerCase())

  // 尝试自动映射常见字段
  const mapping = {
    serial_number: ['序号', '编号', 'serial', 'number', 'no'],
    name: ['材料名称', '名称', 'name', '材料'],
    specification: ['规格', '规格型号', 'specification', 'spec', '型号'],
    brand: ['品牌', 'brand'],
    unit: ['单位', 'unit', '计量单位'],
    price_excluding_tax: ['除税价', '价格', 'price', '单价', '不含税价'],
    notes: ['备注', 'notes', 'remark', '说明']
  }

  for (const [field, keywords] of Object.entries(mapping)) {
    const matched = availableColumns.value.find(col => {
      const lower = col.toLowerCase()
      return keywords.some(keyword => lower.includes(keyword.toLowerCase()))
    })
    if (matched) {
      fieldMapping.value[field] = matched
    }
  }
}

// 加载预览数据
const loadPreviewData = async () => {
  processing.value = true
  try {
    const file = fileList.value[0].raw

    // 使用现有的 get-preview-data API
    const response = await getUnmatchedPreviewData(file, { max_rows: 20 })
    const result = response.data?.data || response.data

    // 获取数据 - 使用 previewData 字段
    const rawData = result.previewData || result.preview_data || []

    // 应用字段映射
    previewData.value = rawData.map(row => {
      const mappedRow = {}
      const rowData = row.data || row

      // 根据字段映射提取数据
      for (const [targetField, sourceField] of Object.entries(fieldMapping.value)) {
        if (sourceField && rowData[sourceField] !== undefined) {
          mappedRow[targetField] = rowData[sourceField]
        }
      }

      // 添加日期
      mappedRow.date = materialDate.value

      return mappedRow
    })

    ElMessage.success('数据预览加载完成')
  } catch (error) {
    console.error('加载预览数据失败:', error)
    ElMessage.error('加载预览数据失败: ' + (error.message || error))
  } finally {
    processing.value = false
  }
}

// 确认导入
const confirmImport = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要导入这些数据吗？',
      '确认导入',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    importing.value = true

    // 首先获取完整数据
    const file = fileList.value[0].raw
    const previewResponse = await getUnmatchedPreviewData(file, { max_rows: 10000 })
    const previewResult = previewResponse.data?.data || previewResponse.data
    const rawData = previewResult.fullData || previewResult.full_data || []

    // 应用字段映射并添加日期
    const materials = rawData.map(row => {
      const mappedRow = {}
      const rowData = row.data || row

      // 根据字段映射提取数据
      for (const [targetField, sourceField] of Object.entries(fieldMapping.value)) {
        if (sourceField && rowData[sourceField] !== undefined) {
          mappedRow[targetField] = rowData[sourceField]
        }
      }

      // 添加日期
      mappedRow.date = materialDate.value

      return mappedRow
    })

    // 准备导入数据 - 使用JSON格式
    const importData = {
      materials: materials,
      import_options: {
        skip_duplicate: true,
        validate_data: true
      }
    }

    // 调用导入API
    const response = await importUnmatchedMaterials(importData)
    const result = response.data?.data || response.data

    // 更新导入摘要
    importSummary.value = {
      total: result.total_count || 0,
      success: result.success_count || 0,
      failed: result.failed_count || 0,
      errors: result.errors || []
    }

    if (importSummary.value.failed === 0) {
      ElMessage.success(`导入成功！共导入 ${importSummary.value.success} 条数据`)
      // 延迟跳转，让用户看到结果
      setTimeout(() => {
        router.push('/unmatched-materials/library?refresh=true')
      }, 2000)
    } else {
      ElMessage.warning(`导入完成，成功 ${importSummary.value.success} 条，失败 ${importSummary.value.failed} 条`)
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('导入失败:', error)
      ElMessage.error('导入失败: ' + (error.message || error))
    }
  } finally {
    importing.value = false
  }
}

onMounted(() => {
  // 初始化
})
</script>

<style lang="scss" scoped>
.unmatched-material-import-container {
  padding: 20px;
  min-height: calc(100vh - 60px);

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    margin-bottom: 20px;

    .header-content {
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
  }

  .steps-card {
    margin-bottom: 20px;
  }

  .content-card {
    min-height: 500px;

    .step-content {
      padding: 20px;

      .date-selection-section {
        h3 {
          font-size: 18px;
          margin-bottom: 8px;
          color: $text-primary;
        }

        .section-desc {
          font-size: 14px;
          color: $text-secondary;
          margin-bottom: 20px;
        }

        .date-selection {
          padding: 20px;
          background: #f5f7fa;
          border-radius: 4px;

          .selection-summary {
            margin-top: 20px;
          }
        }
      }

      .upload-section {
        h3 {
          font-size: 18px;
          margin-bottom: 8px;
          color: $text-primary;
        }

        .section-desc {
          font-size: 14px;
          color: $text-secondary;
          margin-bottom: 20px;
        }

        .upload-area {
          margin-bottom: 20px;

          :deep(.el-upload-dragger) {
            padding: 40px;
          }
        }

        .file-info {
          margin-top: 20px;
          padding: 15px;
          background: #f5f7fa;
          border-radius: 4px;

          h4 {
            font-size: 14px;
            margin: 0 0 10px 0;
            color: $text-primary;
          }

          .file-item {
            display: flex;
            align-items: center;
            gap: 10px;

            .el-icon {
              font-size: 24px;
              color: $color-primary;
            }

            .file-name {
              flex: 1;
              font-size: 14px;
              color: $text-primary;
            }

            .file-size {
              font-size: 12px;
              color: $text-secondary;
            }
          }
        }
      }
    }

    .step-actions {
      display: flex;
      justify-content: center;
      gap: 16px;
      padding: 20px;
      border-top: 1px solid #ebeef5;
    }
  }

  // 分析结果样式
  .analysis-result-section,
  .field-mapping-section,
  .preview-section,
  .import-summary-section {
    h3 {
      font-size: 18px;
      margin-bottom: 8px;
      color: $text-primary;
    }

    .section-desc {
      font-size: 14px;
      color: $text-secondary;
      margin-bottom: 20px;
    }

    .analysis-details {
      margin-top: 20px;

      h4 {
        font-size: 16px;
        margin-bottom: 12px;
        color: $text-primary;
      }
    }
  }

  .mapping-form {
    padding: 20px;
    background: #f5f7fa;
    border-radius: 4px;

    .el-form-item {
      margin-bottom: 16px;
    }
  }

  .error-item {
    padding: 8px;
    margin: 5px 0;
    background: #fef0f0;
    border-left: 3px solid #f56c6c;
    color: #f56c6c;
    font-size: 13px;
  }
}
</style>
