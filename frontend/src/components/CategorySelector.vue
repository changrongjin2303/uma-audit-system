<template>
  <div class="category-selector">
    <h4 class="selector-title">选择材料分类层级</h4>
    <p class="selector-desc">请选择要将材料导入到的分类层级，系统将根据您的选择进行分类存放</p>
    
    <!-- 步骤1: 选择信息来源类型 -->
    <div class="step-section">
      <h5 class="step-title">
        <span class="step-number">1</span>
        选择信息来源类型
      </h5>
      <el-radio-group v-model="selectedSourceType" @change="handleSourceTypeChange">
        <el-radio 
          v-for="sourceType in sourceTypes" 
          :key="sourceType.value"
          :label="sourceType.value"
          class="source-type-radio"
        >
          <div class="source-type-content">
            <div class="source-type-label">{{ sourceType.label }}</div>
            <div class="source-type-desc">{{ sourceType.description }}</div>
          </div>
        </el-radio>
      </el-radio-group>
    </div>

    <!-- 步骤2: 选择年月期次 -->
    <div v-if="selectedSourceType" class="step-section">
      <h5 class="step-title">
        <span class="step-number">2</span>
        选择年月期次
      </h5>
      <div v-loading="loadingYearMonths" class="year-month-selection">
        <template v-if="yearMonthCategories.length > 0">
          <el-radio-group v-model="selectedYearMonth" @change="handleYearMonthChange">
            <el-radio 
              v-for="category in yearMonthCategories" 
              :key="category.id"
              :label="category.id"
              class="year-month-radio"
            >
              <div class="year-month-content">
                <div class="year-month-label">{{ category.name }}</div>
                <div class="year-month-code">{{ category.year_month }}</div>
              </div>
            </el-radio>
          </el-radio-group>
          
          <!-- 新增年月期次选项 -->
          <div class="add-year-month">
            <el-button 
              :icon="Plus" 
              type="primary" 
              plain 
              @click="showAddYearMonth = true"
            >
              新增年月期次
            </el-button>
          </div>
        </template>
        
        <div v-else class="empty-year-months">
          <el-empty description="暂无年月期次数据">
            <el-button 
              type="primary" 
              :icon="Plus" 
              @click="showAddYearMonth = true"
            >
              创建第一个年月期次
            </el-button>
          </el-empty>
        </div>
      </div>
    </div>

    <!-- 选择结果预览 -->
    <div v-if="selectedSourceType && selectedYearMonth" class="selection-preview">
      <h5 class="preview-title">选择预览</h5>
      <div class="selection-path">
        <el-tag type="primary" size="large">{{ getSourceTypeLabel() }}</el-tag>
        <el-icon class="path-arrow"><ArrowRight /></el-icon>
        <el-tag type="success" size="large">{{ getYearMonthLabel() }}</el-tag>
      </div>
      <p class="preview-desc">
        材料将被导入到 <strong>{{ getSourceTypeLabel() }}</strong> 的 <strong>{{ getYearMonthLabel() }}</strong> 分类下
      </p>
    </div>

    <!-- 新增年月期次对话框 -->
    <el-dialog
      v-model="showAddYearMonth"
      title="新增年月期次"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form 
        ref="addYearMonthForm" 
        :model="addYearMonthData" 
        :rules="addYearMonthRules"
        label-width="100px"
      >
        <el-form-item label="信息来源" prop="source_type">
          <el-select v-model="addYearMonthData.source_type" disabled>
            <el-option 
              v-for="sourceType in sourceTypes"
              :key="sourceType.value"
              :label="sourceType.label"
              :value="sourceType.value"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="年月" prop="year_month">
          <el-date-picker
            v-model="addYearMonthData.year_month_date"
            type="month"
            placeholder="选择年月"
            format="YYYY-MM"
            value-format="YYYY-MM"
            @change="handleYearMonthDateChange"
          />
        </el-form-item>
        
        <el-form-item label="年月值" prop="year_month">
          <el-input 
            v-model="addYearMonthData.year_month"
            placeholder="如：202401"
            :disabled="true"
          />
        </el-form-item>
        
        <el-form-item label="描述">
          <el-input 
            v-model="addYearMonthData.description"
            type="textarea"
            :rows="2"
            placeholder="可选，描述该期次的特点"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showAddYearMonth = false">取消</el-button>
        <el-button 
          type="primary" 
          :loading="addingYearMonth"
          @click="handleAddYearMonth"
        >
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, ArrowRight } from '@element-plus/icons-vue'
import { getSourceTypes, getYearMonthCategories, createYearMonthCategory } from '@/api/categories'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({
      sourceType: '',
      yearMonthCategoryId: null
    })
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

// 响应式数据
const selectedSourceType = ref(props.modelValue?.sourceType || '')
const selectedYearMonth = ref(props.modelValue?.yearMonthCategoryId || null)
const sourceTypes = ref([])
const yearMonthCategories = ref([])
const loadingYearMonths = ref(false)
const showAddYearMonth = ref(false)
const addingYearMonth = ref(false)
const addYearMonthForm = ref()

// 新增年月期次表单数据
const addYearMonthData = reactive({
  source_type: '',
  year_month: '',
  year_month_date: '',
  description: ''
})

// 表单验证规则
const addYearMonthRules = {
  source_type: [
    { required: true, message: '请选择信息来源', trigger: 'change' }
  ],
  year_month: [
    { required: true, message: '请选择年月', trigger: 'change' }
  ]
}

// 计算属性
const isSelectionComplete = computed(() => {
  return selectedSourceType.value && selectedYearMonth.value
})

// 方法
const loadSourceTypes = async () => {
  try {
    const response = await getSourceTypes()
    const data = response.data?.data || response.data
    sourceTypes.value = data || []
  } catch (error) {
    console.error('获取信息来源类型失败:', error)
    ElMessage.error('获取信息来源类型失败')
  }
}

const loadYearMonthCategories = async (sourceType) => {
  if (!sourceType) return
  
  loadingYearMonths.value = true
  try {
    const response = await getYearMonthCategories(sourceType)
    const data = response.data?.data || response.data
    yearMonthCategories.value = data || []
  } catch (error) {
    console.error('获取年月分类失败:', error)
    ElMessage.error('获取年月分类失败')
    yearMonthCategories.value = []
  } finally {
    loadingYearMonths.value = false
  }
}

const handleSourceTypeChange = (value) => {
  selectedSourceType.value = value
  selectedYearMonth.value = null // 清空年月选择
  yearMonthCategories.value = []
  
  if (value) {
    loadYearMonthCategories(value)
    // 设置新增表单的信息来源
    addYearMonthData.source_type = value
  }
  
  emitChange()
}

const handleYearMonthChange = (value) => {
  selectedYearMonth.value = value
  emitChange()
}

const emitChange = () => {
  const selection = {
    sourceType: selectedSourceType.value,
    yearMonthCategoryId: selectedYearMonth.value
  }
  
  emit('update:modelValue', selection)
  emit('change', selection)
}

const getSourceTypeLabel = () => {
  const sourceType = sourceTypes.value.find(item => item.value === selectedSourceType.value)
  return sourceType?.label || ''
}

const getYearMonthLabel = () => {
  const category = yearMonthCategories.value.find(item => item.id === selectedYearMonth.value)
  return category?.name || ''
}

const handleYearMonthDateChange = (value) => {
  if (value) {
    // 将 YYYY-MM 格式转换为 YYYYMM 格式
    addYearMonthData.year_month = value.replace('-', '')
  } else {
    addYearMonthData.year_month = ''
  }
}

const handleAddYearMonth = async () => {
  if (!addYearMonthForm.value) return
  
  try {
    const valid = await addYearMonthForm.value.validate()
    if (!valid) return
    
    addingYearMonth.value = true
    
    const response = await createYearMonthCategory({
      source_type: addYearMonthData.source_type,
      year_month: addYearMonthData.year_month,
      description: addYearMonthData.description
    })
    
    ElMessage.success('新增年月期次成功')
    showAddYearMonth.value = false
    
    // 重新加载年月分类列表
    await loadYearMonthCategories(selectedSourceType.value)
    
    // 自动选择新创建的年月期次
    const newCategory = response.data?.data
    if (newCategory?.id) {
      selectedYearMonth.value = newCategory.id
      emitChange()
    }
    
    // 重置表单
    addYearMonthData.year_month = ''
    addYearMonthData.year_month_date = ''
    addYearMonthData.description = ''
    
  } catch (error) {
    console.error('创建年月期次失败:', error)
    ElMessage.error(error.message || '创建年月期次失败')
  } finally {
    addingYearMonth.value = false
  }
}

// 监听props变化
watch(() => props.modelValue, (newValue) => {
  if (newValue) {
    selectedSourceType.value = newValue.sourceType || ''
    selectedYearMonth.value = newValue.yearMonthCategoryId || null
    
    if (newValue.sourceType && newValue.sourceType !== selectedSourceType.value) {
      loadYearMonthCategories(newValue.sourceType)
    }
  }
}, { immediate: true, deep: true })

// 生命周期
onMounted(async () => {
  await loadSourceTypes()
  
  // 如果有初始值，加载对应的年月分类
  if (props.modelValue?.sourceType) {
    await loadYearMonthCategories(props.modelValue.sourceType)
  }
})

// 暴露给父组件的方法
defineExpose({
  isSelectionComplete
})
</script>

<style lang="scss" scoped>
.category-selector {
  .selector-title {
    font-size: 16px;
    font-weight: 600;
    color: #303133;
    margin-bottom: 8px;
  }

  .selector-desc {
    font-size: 14px;
    color: #909399;
    margin-bottom: 24px;
    line-height: 1.5;
  }

  .step-section {
    margin-bottom: 32px;

    .step-title {
      font-size: 14px;
      font-weight: 600;
      color: #606266;
      margin-bottom: 16px;
      display: flex;
      align-items: center;

      .step-number {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 20px;
        height: 20px;
        background-color: #409eff;
        color: white;
        border-radius: 50%;
        font-size: 12px;
        margin-right: 8px;
      }
    }

    .source-type-radio {
      display: block;
      margin-bottom: 16px;
      margin-right: 0;

      :deep(.el-radio__label) {
        width: 100%;
      }

      .source-type-content {
        padding: 16px;
        border: 1px solid #dcdfe6;
        border-radius: 8px;
        transition: all 0.3s ease;

        &:hover {
          border-color: #409eff;
          background-color: #f0f7ff;
        }

        .source-type-label {
          font-size: 16px;
          font-weight: 600;
          color: #303133;
          margin-bottom: 4px;
        }

        .source-type-desc {
          font-size: 13px;
          color: #909399;
          line-height: 1.4;
        }
      }

      &.is-checked {
        .source-type-content {
          border-color: #409eff;
          background-color: #f0f7ff;
        }
      }
    }

    .year-month-selection {
      .year-month-radio {
        display: inline-block;
        margin-right: 16px;
        margin-bottom: 12px;

        .year-month-content {
          padding: 12px 16px;
          border: 1px solid #dcdfe6;
          border-radius: 6px;
          text-align: center;
          min-width: 120px;
          transition: all 0.3s ease;

          &:hover {
            border-color: #409eff;
            background-color: #f0f7ff;
          }

          .year-month-label {
            font-size: 14px;
            font-weight: 600;
            color: #303133;
            margin-bottom: 2px;
          }

          .year-month-code {
            font-size: 12px;
            color: #909399;
          }
        }

        &.is-checked {
          .year-month-content {
            border-color: #409eff;
            background-color: #f0f7ff;
          }
        }
      }

      .add-year-month {
        margin-top: 16px;
        text-align: center;
      }

      .empty-year-months {
        text-align: center;
        padding: 40px 20px;
      }
    }
  }

  .selection-preview {
    padding: 20px;
    background-color: #f8f9fa;
    border-radius: 8px;
    border-left: 4px solid #409eff;

    .preview-title {
      font-size: 14px;
      font-weight: 600;
      color: #303133;
      margin-bottom: 16px;
    }

    .selection-path {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 12px;

      .path-arrow {
        color: #909399;
        font-size: 16px;
      }
    }

    .preview-desc {
      font-size: 13px;
      color: #606266;
      margin: 0;

      strong {
        color: #409eff;
        font-weight: 600;
      }
    }
  }
}

// 单选框选中状态样式
:deep(.el-radio.is-checked) {
  .el-radio__input .el-radio__inner {
    border-color: #409eff;
    background-color: #409eff;
  }
}

// 对话框样式
:deep(.el-dialog__body) {
  padding: 20px;
}
</style>