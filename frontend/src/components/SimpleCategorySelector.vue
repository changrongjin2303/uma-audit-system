<template>
  <div class="simple-category-selector">
    <div class="selector-section">
      <h4>请选择信息来源类型</h4>
      <el-radio-group v-model="selectedSourceType" @change="handleSourceTypeChange">
        <el-radio-button value="provincial">
          <div class="source-type-content">
            <div class="source-type-label">省造价信息正刊</div>
            <div class="source-type-desc">省级造价信息发布机构发布的正式刊物</div>
          </div>
        </el-radio-button>
        <el-radio-button value="municipal">
          <div class="source-type-content">
            <div class="source-type-label">市造价信息正刊</div>
            <div class="source-type-desc">市级造价信息发布机构发布的正式刊物</div>
          </div>
        </el-radio-button>
      </el-radio-group>
    </div>

    <div v-if="selectedSourceType" class="selector-section">
      <h4>选择{{ selectedSourceType === 'provincial' ? '省份' : '城市' }}</h4>
      <div class="region-select">
        <el-select
          v-model="selectedRegion"
          :placeholder="`请选择${selectedSourceType === 'provincial' ? '省份' : '城市'}`"
          @change="handleRegionChange"
          clearable
          filterable
        >
          <el-option
            v-for="region in getRegionOptions(selectedSourceType)"
            :key="region.value"
            :label="region.label"
            :value="region.value"
          />
        </el-select>
        <p class="help-text">选择{{ selectedSourceType === 'provincial' ? '省份' : '城市' }}信息价发布地区</p>
      </div>
    </div>

    <div v-if="selectedSourceType && selectedRegion" class="selector-section">
      <h4>选择年月期次</h4>
      <div class="year-month-input">
        <el-date-picker
          v-model="yearMonthDate"
          type="month"
          placeholder="选择年月"
          format="YYYY年MM月"
          value-format="YYYY-MM"
          @change="handleYearMonthChange"
        />
        <p class="help-text">选择具体的期次年月，如"2024年01月"</p>
      </div>
      
      <div v-if="yearMonthDate" class="selection-summary">
        <el-alert
          :title="`已选择：${getSourceTypeLabel(selectedSourceType)} - ${selectedRegion} - ${formatYearMonth(yearMonthDate)}`"
          type="success"
          :closable="false"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({
      sourceType: '',
      yearMonth: ''
    })
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

const selectedSourceType = ref(props.modelValue?.sourceType || '')
const selectedRegion = ref(props.modelValue?.region || '')
const yearMonthDate = ref(props.modelValue?.yearMonth || '')

const getSourceTypeLabel = (type) => {
  const labels = {
    municipal: '市造价信息正刊',
    provincial: '省造价信息正刊'
  }
  return labels[type] || type
}

const formatYearMonth = (date) => {
  if (!date) return ''
  const [year, month] = date.split('-')
  return `${year}年${month}月`
}

// 省份选项数据
const provinceOptions = [
  { value: '北京', label: '北京市' },
  { value: '天津', label: '天津市' },
  { value: '河北', label: '河北省' },
  { value: '山西', label: '山西省' },
  { value: '内蒙古', label: '内蒙古自治区' },
  { value: '辽宁', label: '辽宁省' },
  { value: '吉林', label: '吉林省' },
  { value: '黑龙江', label: '黑龙江省' },
  { value: '上海', label: '上海市' },
  { value: '江苏', label: '江苏省' },
  { value: '浙江', label: '浙江省' },
  { value: '安徽', label: '安徽省' },
  { value: '福建', label: '福建省' },
  { value: '江西', label: '江西省' },
  { value: '山东', label: '山东省' },
  { value: '河南', label: '河南省' },
  { value: '湖北', label: '湖北省' },
  { value: '湖南', label: '湖南省' },
  { value: '广东', label: '广东省' },
  { value: '广西', label: '广西壮族自治区' },
  { value: '海南', label: '海南省' },
  { value: '重庆', label: '重庆市' },
  { value: '四川', label: '四川省' },
  { value: '贵州', label: '贵州省' },
  { value: '云南', label: '云南省' },
  { value: '西藏', label: '西藏自治区' },
  { value: '陕西', label: '陕西省' },
  { value: '甘肃', label: '甘肃省' },
  { value: '青海', label: '青海省' },
  { value: '宁夏', label: '宁夏回族自治区' },
  { value: '新疆', label: '新疆维吾尔自治区' }
]

// 城市选项数据
const cityOptions = [
  { value: '北京', label: '北京市' },
  { value: '上海', label: '上海市' },
  { value: '广州', label: '广州市' },
  { value: '深圳', label: '深圳市' },
  { value: '天津', label: '天津市' },
  { value: '重庆', label: '重庆市' },
  { value: '成都', label: '成都市' },
  { value: '杭州', label: '杭州市' },
  { value: '武汉', label: '武汉市' },
  { value: '西安', label: '西安市' },
  { value: '苏州', label: '苏州市' },
  { value: '郑州', label: '郑州市' },
  { value: '南京', label: '南京市' },
  { value: '青岛', label: '青岛市' },
  { value: '长沙', label: '长沙市' },
  { value: '大连', label: '大连市' },
  { value: '宁波', label: '宁波市' },
  { value: '无锡', label: '无锡市' },
  { value: '济南', label: '济南市' },
  { value: '沈阳', label: '沈阳市' }
]

const getRegionOptions = (sourceType) => {
  return sourceType === 'provincial' ? provinceOptions : cityOptions
}

const isComplete = computed(() => {
  return selectedSourceType.value && selectedRegion.value && yearMonthDate.value
})

const handleSourceTypeChange = (value) => {
  selectedSourceType.value = value
  selectedRegion.value = '' // 重置地区选择
  yearMonthDate.value = '' // 重置年月选择
  emitChange()
}

const handleRegionChange = (value) => {
  selectedRegion.value = value
  emitChange()
}

const handleYearMonthChange = (value) => {
  yearMonthDate.value = value
  emitChange()
}

const emitChange = () => {
  const selection = {
    sourceType: selectedSourceType.value,
    region: selectedRegion.value,
    yearMonth: yearMonthDate.value,
    isComplete: isComplete.value
  }
  
  emit('update:modelValue', selection)
  emit('change', selection)
}

// 监听外部值变化
watch(
  () => props.modelValue,
  (newValue) => {
    if (newValue) {
      selectedSourceType.value = newValue.sourceType || ''
      selectedRegion.value = newValue.region || ''
      yearMonthDate.value = newValue.yearMonth || ''
    }
  },
  { deep: true, immediate: true }
)
</script>

<style scoped>
.simple-category-selector {
  max-width: 600px;
}

.selector-section {
  margin-bottom: 24px;
}

.selector-section h4 {
  margin: 0 0 16px 0;
  color: #303133;
  font-weight: 600;
}

.source-type-content {
  text-align: left;
}

.source-type-label {
  font-weight: 600;
  color: inherit;
  margin-bottom: 6px;
  font-size: 16px;
}

.source-type-desc {
  font-size: 13px;
  color: inherit;
  opacity: 0.8;
  line-height: 1.4;
}

.year-month-input {
  margin-bottom: 16px;
}

.help-text {
  margin: 8px 0 0 0;
  font-size: 12px;
  color: #909399;
}

.selection-summary {
  margin-top: 16px;
}

:deep(.el-radio-group) {
  display: flex;
  flex-direction: row;
  gap: 12px;
  flex-wrap: wrap;
}

:deep(.el-radio-button) {
  margin: 0;
  flex: 1;
}

:deep(.el-radio-button__inner) {
  width: 100%;
  text-align: left;
  padding: 16px 20px;
  border-radius: 8px;
  border: 2px solid #dcdfe6;
  background: #ffffff;
  transition: all 0.3s ease;
  min-width: 200px;
}

:deep(.el-radio-button__inner:hover) {
  border-color: #409eff;
  background: #ecf5ff;
}

:deep(.el-radio-button.is-active .el-radio-button__inner) {
  border-color: #409eff;
  background: #409eff;
  color: #ffffff;
}

:deep(.el-radio-button.is-active .el-radio-button__inner .source-type-desc) {
  color: rgba(255, 255, 255, 0.8);
}
</style>