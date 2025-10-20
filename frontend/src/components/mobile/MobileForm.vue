<template>
  <div class="mobile-form" :class="{ 'is-mobile': isMobile }">
    <el-form
      ref="formRef"
      :model="modelValue"
      :rules="rules"
      :label-position="labelPosition"
      :label-width="labelWidth"
      :size="formSize"
      :disabled="disabled"
      :validate-on-rule-change="false"
      @submit.prevent
    >
      <!-- 表单组 -->
      <div
        v-for="(group, groupIndex) in formGroups"
        :key="groupIndex"
        class="form-group"
      >
        <!-- 组标题 -->
        <div v-if="group.title" class="group-title">
          <h3>{{ group.title }}</h3>
          <p v-if="group.description">{{ group.description }}</p>
        </div>

        <!-- 表单字段 -->
        <div class="form-fields">
          <el-form-item
            v-for="field in group.fields"
            :key="field.prop"
            :prop="field.prop"
            :label="field.label"
            :required="field.required"
            :error="field.error"
            :class="{
              'full-width': field.fullWidth || isMobile,
              'half-width': field.halfWidth && !isMobile,
              'mobile-field': isMobile
            }"
          >
            <!-- 输入框 -->
            <el-input
              v-if="field.type === 'input'"
              v-model="modelValue[field.prop]"
              :type="field.inputType || 'text'"
              :placeholder="field.placeholder"
              :disabled="field.disabled"
              :readonly="field.readonly"
              :clearable="field.clearable !== false"
              :show-password="field.showPassword"
              :maxlength="field.maxLength"
              :show-word-limit="field.showWordLimit"
              :prefix-icon="field.prefixIcon"
              :suffix-icon="field.suffixIcon"
              @change="handleFieldChange(field.prop, $event)"
              @blur="handleFieldBlur(field.prop)"
              @focus="handleFieldFocus(field.prop)"
            />

            <!-- 数字输入框 -->
            <el-input-number
              v-else-if="field.type === 'number'"
              v-model="modelValue[field.prop]"
              :min="field.min"
              :max="field.max"
              :step="field.step"
              :precision="field.precision"
              :disabled="field.disabled"
              :controls="!isMobile"
              :controls-position="isMobile ? undefined : 'right'"
              class="full-width-number"
              @change="handleFieldChange(field.prop, $event)"
            />

            <!-- 选择器 -->
            <el-select
              v-else-if="field.type === 'select'"
              v-model="modelValue[field.prop]"
              :placeholder="field.placeholder"
              :disabled="field.disabled"
              :clearable="field.clearable !== false"
              :multiple="field.multiple"
              :filterable="field.filterable"
              :allow-create="field.allowCreate"
              :remote="field.remote"
              :remote-method="field.remoteMethod"
              :loading="field.loading"
              class="full-width"
              @change="handleFieldChange(field.prop, $event)"
            >
              <el-option
                v-for="option in field.options"
                :key="option.value"
                :label="option.label"
                :value="option.value"
                :disabled="option.disabled"
              />
            </el-select>

            <!-- 日期选择器 -->
            <el-date-picker
              v-else-if="field.type === 'date'"
              v-model="modelValue[field.prop]"
              :type="field.dateType || 'date'"
              :placeholder="field.placeholder"
              :disabled="field.disabled"
              :clearable="field.clearable !== false"
              :format="field.format"
              :value-format="field.valueFormat"
              :start-placeholder="field.startPlaceholder"
              :end-placeholder="field.endPlaceholder"
              class="full-width"
              @change="handleFieldChange(field.prop, $event)"
            />

            <!-- 时间选择器 -->
            <el-time-picker
              v-else-if="field.type === 'time'"
              v-model="modelValue[field.prop]"
              :placeholder="field.placeholder"
              :disabled="field.disabled"
              :clearable="field.clearable !== false"
              :format="field.format"
              :value-format="field.valueFormat"
              class="full-width"
              @change="handleFieldChange(field.prop, $event)"
            />

            <!-- 开关 -->
            <el-switch
              v-else-if="field.type === 'switch'"
              v-model="modelValue[field.prop]"
              :disabled="field.disabled"
              :active-text="field.activeText"
              :inactive-text="field.inactiveText"
              :active-value="field.activeValue"
              :inactive-value="field.inactiveValue"
              @change="handleFieldChange(field.prop, $event)"
            />

            <!-- 单选框组 -->
            <el-radio-group
              v-else-if="field.type === 'radio'"
              v-model="modelValue[field.prop]"
              :disabled="field.disabled"
              :size="field.size"
              @change="handleFieldChange(field.prop, $event)"
            >
              <el-radio
                v-for="option in field.options"
                :key="option.value"
                :label="option.value"
                :disabled="option.disabled"
              >
                {{ option.label }}
              </el-radio>
            </el-radio-group>

            <!-- 复选框组 -->
            <el-checkbox-group
              v-else-if="field.type === 'checkbox'"
              v-model="modelValue[field.prop]"
              :disabled="field.disabled"
              :min="field.min"
              :max="field.max"
              @change="handleFieldChange(field.prop, $event)"
            >
              <el-checkbox
                v-for="option in field.options"
                :key="option.value"
                :label="option.value"
                :disabled="option.disabled"
              >
                {{ option.label }}
              </el-checkbox>
            </el-checkbox-group>

            <!-- 文本域 -->
            <el-input
              v-else-if="field.type === 'textarea'"
              v-model="modelValue[field.prop]"
              type="textarea"
              :placeholder="field.placeholder"
              :disabled="field.disabled"
              :readonly="field.readonly"
              :rows="field.rows || (isMobile ? 3 : 4)"
              :maxlength="field.maxLength"
              :show-word-limit="field.showWordLimit"
              :autosize="field.autosize"
              @change="handleFieldChange(field.prop, $event)"
            />

            <!-- 评分 -->
            <el-rate
              v-else-if="field.type === 'rate'"
              v-model="modelValue[field.prop]"
              :max="field.max || 5"
              :disabled="field.disabled"
              :allow-half="field.allowHalf"
              :show-text="field.showText"
              :show-score="field.showScore"
              :texts="field.texts"
              @change="handleFieldChange(field.prop, $event)"
            />

            <!-- 滑块 -->
            <el-slider
              v-else-if="field.type === 'slider'"
              v-model="modelValue[field.prop]"
              :min="field.min || 0"
              :max="field.max || 100"
              :step="field.step || 1"
              :disabled="field.disabled"
              :show-input="field.showInput && !isMobile"
              :show-input-controls="!isMobile"
              :range="field.range"
              :marks="field.marks"
              @change="handleFieldChange(field.prop, $event)"
            />

            <!-- 文件上传 -->
            <el-upload
              v-else-if="field.type === 'upload'"
              :action="field.action"
              :headers="field.headers"
              :data="field.data"
              :name="field.name || 'file'"
              :multiple="field.multiple"
              :accept="field.accept"
              :file-list="modelValue[field.prop] || []"
              :disabled="field.disabled"
              :limit="field.limit"
              :show-file-list="field.showFileList !== false"
              :list-type="field.listType || (isMobile ? 'text' : 'picture-card')"
              :before-upload="field.beforeUpload"
              :on-success="(response, file, fileList) => handleUploadSuccess(field.prop, response, file, fileList)"
              :on-error="field.onError"
              :on-remove="(file, fileList) => handleUploadRemove(field.prop, file, fileList)"
            >
              <template v-if="field.listType !== 'picture-card'">
                <el-button :size="isMobile ? 'small' : 'default'">
                  <el-icon><Upload /></el-icon>
                  {{ field.uploadText || '上传文件' }}
                </el-button>
              </template>
              <template v-else>
                <el-icon><Plus /></el-icon>
              </template>
            </el-upload>

            <!-- 自定义组件 -->
            <component
              v-else-if="field.type === 'custom' && field.component"
              :is="field.component"
              v-model="modelValue[field.prop]"
              v-bind="field.componentProps"
              @change="handleFieldChange(field.prop, $event)"
            />

            <!-- 字段帮助文本 -->
            <div v-if="field.help" class="field-help">
              {{ field.help }}
            </div>
          </el-form-item>
        </div>
      </div>

      <!-- 表单操作按钮 -->
      <div class="form-actions" v-if="showActions">
        <slot name="actions">
          <el-button
            v-if="showCancel"
            :size="isMobile ? 'large' : 'default'"
            @click="handleCancel"
          >
            {{ cancelText }}
          </el-button>
          <el-button
            type="primary"
            :size="isMobile ? 'large' : 'default'"
            :loading="loading"
            @click="handleSubmit"
          >
            {{ submitText }}
          </el-button>
        </slot>
      </div>
    </el-form>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { Upload, Plus } from '@element-plus/icons-vue'
import { useResponsive, DEVICE_TYPES } from '@/utils/mobile'

export default {
  name: 'MobileForm',
  components: {
    Upload,
    Plus
  },
  props: {
    // 表单数据
    modelValue: {
      type: Object,
      required: true
    },
    // 字段配置
    fields: {
      type: Array,
      default: () => []
    },
    // 验证规则
    rules: {
      type: Object,
      default: () => ({})
    },
    // 表单分组
    groups: {
      type: Array,
      default: null
    },
    // 是否禁用
    disabled: {
      type: Boolean,
      default: false
    },
    // 加载状态
    loading: {
      type: Boolean,
      default: false
    },
    // 是否显示操作按钮
    showActions: {
      type: Boolean,
      default: true
    },
    // 是否显示取消按钮
    showCancel: {
      type: Boolean,
      default: true
    },
    // 提交按钮文本
    submitText: {
      type: String,
      default: '提交'
    },
    // 取消按钮文本
    cancelText: {
      type: String,
      default: '取消'
    }
  },
  emits: ['update:modelValue', 'submit', 'cancel', 'field-change', 'field-focus', 'field-blur'],
  setup(props, { emit }) {
    const formRef = ref(null)
    const responsive = useResponsive()

    // 计算属性
    const isMobile = computed(() => responsive.device === DEVICE_TYPES.MOBILE)
    
    const formSize = computed(() => {
      return isMobile.value ? 'large' : 'default'
    })

    const labelPosition = computed(() => {
      return isMobile.value ? 'top' : 'right'
    })

    const labelWidth = computed(() => {
      return isMobile.value ? '100%' : '120px'
    })

    const formGroups = computed(() => {
      if (props.groups) {
        return props.groups
      }
      
      // 默认单组
      return [{
        title: '',
        description: '',
        fields: props.fields
      }]
    })

    // 方法
    const handleFieldChange = (prop, value) => {
      emit('update:modelValue', {
        ...props.modelValue,
        [prop]: value
      })
      emit('field-change', { prop, value })
    }

    const handleFieldFocus = (prop) => {
      emit('field-focus', prop)
    }

    const handleFieldBlur = (prop) => {
      emit('field-blur', prop)
    }

    const handleUploadSuccess = (prop, response, file, fileList) => {
      handleFieldChange(prop, fileList)
    }

    const handleUploadRemove = (prop, file, fileList) => {
      handleFieldChange(prop, fileList)
    }

    const handleSubmit = async () => {
      if (!formRef.value) return

      try {
        await formRef.value.validate()
        emit('submit', props.modelValue)
      } catch (error) {
        console.error('表单验证失败:', error)
      }
    }

    const handleCancel = () => {
      emit('cancel')
    }

    const validate = () => {
      return formRef.value?.validate()
    }

    const validateField = (prop) => {
      return formRef.value?.validateField(prop)
    }

    const resetFields = () => {
      formRef.value?.resetFields()
    }

    const clearValidate = (props) => {
      formRef.value?.clearValidate(props)
    }

    // 暴露方法
    defineExpose({
      validate,
      validateField,
      resetFields,
      clearValidate
    })

    return {
      formRef,
      responsive,
      isMobile,
      formSize,
      labelPosition,
      labelWidth,
      formGroups,
      handleFieldChange,
      handleFieldFocus,
      handleFieldBlur,
      handleUploadSuccess,
      handleUploadRemove,
      handleSubmit,
      handleCancel
    }
  }
}
</script>

<style scoped>
.mobile-form {
  width: 100%;
}

.form-group {
  margin-bottom: 24px;
}

.group-title {
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ebeef5;
}

.group-title h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.group-title p {
  margin: 0;
  font-size: 13px;
  color: #909399;
  line-height: 1.4;
}

.form-fields {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.form-fields :deep(.el-form-item) {
  margin-bottom: 0;
}

.form-fields :deep(.full-width) {
  grid-column: 1 / -1;
}

.form-fields :deep(.half-width) {
  grid-column: span 1;
}

/* 移动端样式 */
.is-mobile .form-fields {
  grid-template-columns: 1fr;
  gap: 20px;
}

.is-mobile .form-fields :deep(.mobile-field) {
  grid-column: 1;
}

.is-mobile :deep(.el-form-item__label) {
  padding: 0 0 8px 0;
  line-height: 1.4;
  font-weight: 500;
}

.is-mobile :deep(.el-form-item__content) {
  line-height: 1.4;
}

/* 输入组件全宽样式 */
:deep(.full-width),
:deep(.full-width-number) {
  width: 100%;
}

:deep(.full-width-number .el-input-number) {
  width: 100%;
}

/* 字段帮助文本 */
.field-help {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  line-height: 1.4;
}

/* 表单操作按钮 */
.form-actions {
  margin-top: 32px;
  text-align: right;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.form-actions :deep(.el-button) {
  margin-left: 12px;
}

.form-actions :deep(.el-button:first-child) {
  margin-left: 0;
}

/* 移动端按钮样式 */
.is-mobile .form-actions {
  text-align: center;
  margin-top: 24px;
}

.is-mobile .form-actions :deep(.el-button) {
  width: 120px;
  height: 44px;
  margin: 0 6px;
}

/* 移动端组件样式优化 */
.is-mobile :deep(.el-input__inner),
.is-mobile :deep(.el-textarea__inner) {
  height: 44px;
  line-height: 44px;
  font-size: 16px; /* 防止iOS缩放 */
}

.is-mobile :deep(.el-textarea__inner) {
  height: auto;
  min-height: 88px;
  line-height: 1.4;
  padding: 12px;
}

.is-mobile :deep(.el-select .el-input .el-input__inner) {
  height: 44px;
  line-height: 44px;
}

.is-mobile :deep(.el-date-editor .el-input__inner) {
  height: 44px;
  line-height: 44px;
}

.is-mobile :deep(.el-slider) {
  margin: 16px 0;
}

.is-mobile :deep(.el-rate) {
  height: 44px;
  line-height: 44px;
}

/* 上传组件移动端优化 */
.is-mobile :deep(.el-upload) {
  width: 100%;
}

.is-mobile :deep(.el-upload .el-button) {
  width: 100%;
  height: 44px;
}

/* 响应式断点 */
@media (max-width: 768px) {
  .form-group {
    margin-bottom: 20px;
  }
  
  .group-title {
    margin-bottom: 16px;
    padding-bottom: 8px;
  }
  
  .form-fields {
    gap: 16px;
  }
  
  .form-actions {
    margin-top: 20px;
    padding-top: 16px;
  }
}

/* 平板优化 */
@media (min-width: 769px) and (max-width: 1024px) {
  .form-fields {
    gap: 20px;
  }
  
  .form-fields :deep(.el-form-item__label) {
    font-size: 14px;
  }
}
</style>