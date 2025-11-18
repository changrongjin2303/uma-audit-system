<template>
  <div class="base-materials-container">
    <!-- 页面标题和工具栏 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">市场信息价材料管理</h1>
        <p class="page-subtitle">管理市场信息价材料数据库，建立价格分析的基础数据</p>
      </div>
      <div class="header-actions">
        <el-button 
          type="success" 
          :icon="Upload" 
          @click="handleImportMaterials"
        >
          导入材料
        </el-button>
        <el-button 
          type="primary" 
          :icon="Plus" 
          @click="handleCreateMaterial"
        >
          新建材料
        </el-button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="search-card">
      <el-form :model="searchForm" :inline="true" class="search-form">
        <el-form-item label="材料名称">
          <el-input
            v-model="searchForm.name"
            placeholder="请输入材料名称"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="规格型号">
          <div style="display:flex;align-items:center;gap:8px;">
            <el-select
              v-model="searchForm.specification"
              filterable
              allow-create
              default-first-option
              clearable
              placeholder="请选择规格型号"
              :loading="loadingSpecs"
              style="width: 200px"
            >
              <el-option
                v-for="spec in specOptions"
                :key="spec"
                :label="spec"
                :value="spec"
              />
            </el-select>
            <el-button :icon="Search" @click="fetchSpecOptions">匹配型号</el-button>
          </div>
        </el-form-item>
        <el-form-item label="期刊类型">
          <el-select
            v-model="searchForm.price_type"
            placeholder="选择期刊类型"
            clearable
            style="width: 200px"
          >
            <el-option label="省刊" value="provincial" />
            <el-option label="市刊" value="municipal" />
          </el-select>
        </el-form-item>
        <el-form-item label="地区">
          <el-select
            v-model="searchForm.region"
            placeholder="选择地区"
            clearable
            style="width: 200px"
          >
            <el-option
              v-for="region in availableRegions"
              :key="region.value"
              :label="region.label"
              :value="region.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="期数">
          <el-date-picker
            v-model="searchForm.price_date"
            type="month"
            placeholder="选择期数"
            value-format="YYYY-MM"
            style="width: 200px"
            clearable
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">
            搜索
          </el-button>
          <el-button @click="handleReset">
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 材料列表 -->
    <el-card class="materials-card">
      <!-- 批量操作工具栏 -->
      <div class="table-toolbar">
        <div class="toolbar-left">
          <template v-if="selectedCount > 0">
            <el-button type="danger" :icon="Delete" @click="handleBatchDelete">
              批量删除 ({{ selectedCount }})
            </el-button>
            <el-button type="warning" :icon="Edit" @click="handleBatchEdit">批量编辑</el-button>
            <el-divider direction="vertical" />
            <el-switch
              v-model="allSelected"
              inline-prompt
              active-text="全选所有页"
              inactive-text="仅选本页"
              @change="() => syncSelectionOnPage(materialTableRef, materials)"
            />
          </template>
        </div>
        <div class="toolbar-right">
          <el-tooltip content="刷新">
            <el-button :icon="Refresh" @click="fetchMaterials" />
          </el-tooltip>
          <el-tooltip content="导出数据">
            <el-button :icon="Download" @click="handleExport" />
          </el-tooltip>
        </div>
      </div>

      <!-- 材料表格 -->
      <el-table
        ref="materialTableRef"
        v-loading="loading"
        :data="materials"
        :row-key="row => row.id"
        :reserve-selection="true"
        @selection-change="onSelectionChange"
        stripe
        style="width: 100%"
        class="materials-table"
        :height="tableHeight"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="material_code" label="编码" width="120">
          <template #default="{ row }">
            <span>{{ row.material_code || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="材料名称" min-width="200" />
        <el-table-column prop="specification" label="规格型号" width="150">
          <template #default="{ row }">
            <span>{{ row.specification || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column prop="price_excluding_tax" label="除税信息价" width="120">
          <template #default="{ row }">
            ¥{{ formatNumber(row.price_excluding_tax || row.price || 0) }}
          </template>
        </el-table-column>
        <el-table-column prop="price_including_tax" label="含税信息价" width="120">
          <template #default="{ row }">
            ¥{{ formatNumber(row.price_including_tax || (row.price * 1.13) || 0) }}
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" width="150">
          <template #default="{ row }">
            <span>{{ row.remark || row.verification_notes || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="journal_type" label="期刊" width="120">
          <template #default="{ row }">
            <el-tag
              :type="getJournalType(row)"
              size="small"
            >
              {{ getJournalText(row) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="issue_period" label="期数" width="110">
          <template #default="{ row }">
            <span>{{ row.issue_period || getPeriodText(row) || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="region" label="适用地区" width="100">
          <template #default="{ row }">
            {{ getApplicableRegionText(row) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button
                type="primary"
                link
                size="small"
                :icon="View"
                @click="viewMaterial(row)"
              >
                查看
              </el-button>
              <el-button
                type="primary"
                link
                size="small"
                :icon="Edit"
                @click="editMaterial(row)"
              >
                编辑
              </el-button>
              <el-button
                type="danger"
                link
                size="small"
                :icon="Delete"
                @click="deleteMaterial(row)"
              >
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div v-if="materials.length > 0" class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100, 500, 1000, 2000]"
          :pager-count="11"
          background
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
      
      <!-- 空状态 -->
      <el-empty v-else description="暂无材料数据">
        <el-button type="primary" @click="$router.push('/materials/import')">
          导入材料数据
        </el-button>
      </el-empty>
    </el-card>

    <!-- 导入材料功能已移动到专门的Excel上传页面 -->

    <!-- 新建/编辑材料对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="isEditing ? '编辑材料' : '新建材料'"
      width="600px"
      :close-on-click-modal="false"
      @close="handleDialogClose"
    >
      <el-form
        ref="materialFormRef"
        :model="materialForm"
        :rules="materialRules"
        label-width="100px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="材料名称" prop="name">
              <el-input v-model="materialForm.name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="规格型号" prop="specification">
              <el-input v-model="materialForm.specification" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="单位" prop="unit">
              <el-input v-model="materialForm.unit" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="参考价格" prop="price">
              <el-input v-model="materialForm.price" type="number" step="0.01" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="材料分类" prop="category">
              <el-select v-model="materialForm.category" style="width: 100%">
                <el-option label="建筑材料" value="building" />
                <el-option label="装修材料" value="decoration" />
                <el-option label="机械设备" value="machinery" />
                <el-option label="人工费" value="labor" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="适用地区" prop="region">
              <el-select v-model="materialForm.region" style="width: 100%">
                <el-option label="北京" value="beijing" />
                <el-option label="上海" value="shanghai" />
                <el-option label="广州" value="guangzhou" />
                <el-option label="深圳" value="shenzhen" />
                <el-option label="全国" value="national" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="数据来源" prop="source">
          <el-select v-model="materialForm.source" style="width: 100%">
            <el-option label="政府信息价" value="government" />
            <el-option label="市场调研" value="market" />
            <el-option label="供应商报价" value="supplier" />
            <el-option label="历史数据" value="historical" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="备注">
          <el-input
            v-model="materialForm.remarks"
            type="textarea"
            :rows="3"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="handleDialogClose">取消</el-button>
        <el-button
          type="primary"
          :loading="submitting"
          @click="handleMaterialSubmit"
        >
          {{ isEditing ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 材料详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="材料详情"
      width="600px"
      :close-on-click-modal="false"
    >
      <div class="material-detail">
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="detail-item">
              <label>材料名称：</label>
              <span>{{ currentMaterial.name }}</span>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="detail-item">
              <label>规格型号：</label>
              <span>{{ currentMaterial.specification || '-' }}</span>
            </div>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="detail-item">
              <label>单位：</label>
              <span>{{ currentMaterial.unit }}</span>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="detail-item">
              <label>参考价格：</label>
              <span>¥{{ currentMaterial.price }}</span>
            </div>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="detail-item">
              <label>材料分类：</label>
              <span>{{ currentMaterial.category || '-' }}</span>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="detail-item">
              <label>适用地区：</label>
              <span>{{ currentMaterial.region }}</span>
            </div>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="detail-item">
              <label>数据来源：</label>
              <span>{{ currentMaterial.source || '-' }}</span>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="detail-item">
              <label>是否验证：</label>
              <el-tag :type="currentMaterial.is_verified ? 'success' : 'warning'">
                {{ currentMaterial.is_verified ? '已验证' : '未验证' }}
              </el-tag>
            </div>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="detail-item">
              <label>创建时间：</label>
              <span>{{ formatDate(currentMaterial.created_at) }}</span>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="detail-item">
              <label>更新时间：</label>
              <span>{{ formatDate(currentMaterial.updated_at) }}</span>
            </div>
          </el-col>
        </el-row>
        
        <el-row v-if="currentMaterial.remarks" :gutter="20">
          <el-col :span="24">
            <div class="detail-item">
              <label>备注：</label>
              <p>{{ currentMaterial.remarks }}</p>
            </div>
          </el-col>
        </el-row>
      </div>
      
      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
        <el-button type="primary" @click="editMaterial(currentMaterial)">编辑</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onActivated, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter, useRoute } from 'vue-router'
import {
  Plus,
  Upload,
  Search,
  Refresh,
  Delete,
  Download,
  Edit,
  View,
  UploadFilled
} from '@element-plus/icons-vue'
import { formatDate, formatNumber } from '@/utils'
import { getBaseMaterials, createBaseMaterial, updateBaseMaterial, deleteBaseMaterial, batchDeleteBaseMaterials, getRegions, searchSimilarBaseMaterials } from '@/api/materials'
import { useSelectionAcrossPages } from '@/composables/useSelectionAcrossPages'

// 使用路由
const router = useRouter()
const route = useRoute()

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const importing = ref(false)
// const showUploadDialog = ref(false) // 已移除，直接跳转到上传页面
const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const isEditing = ref(false)
const currentMaterial = ref({})
const materialFormRef = ref()
const uploadStep = ref(0)

const materials = ref([])
const selectedMaterials = ref([])
const materialTableRef = ref()
const {
  allSelected,
  selectedIds: selectedMaterialIds,
  excludedIds,
  toggleSelectAll,
  clearAll: clearAllSelection,
  handleSelectionChange,
  syncSelectionOnPage,
  getSelectedIds,
  createSelectedCount
} = useSelectionAcrossPages('id')
const selectedCount = createSelectedCount(() => pagination.total)
const uploadFileList = ref([])
const excelColumns = ref([])
const previewData = ref([])

// 搜索表单
const searchForm = reactive({
  name: '',
  specification: '',
  price_type: '',
  region: '',
  price_date: ''
})

// 规格候选与联动
const specOptions = ref([])
const loadingSpecs = ref(false)
let specTimer = null

const fetchSpecOptions = async () => {
  loadingSpecs.value = true
  try {
    const resp = await getBaseMaterials({
      page: 1,
      page_size: 200,
      name: searchForm.name,
      price_type: searchForm.price_type,
      region: searchForm.region,
      price_date: searchForm.price_date,
      _t: Date.now()
    }, { __skipLoading: true })
    const result = resp.data?.data || resp.data || resp
    const items = result.items || result.materials || []
    const set = new Set()
    items.forEach(i => { if (i.specification) set.add(i.specification) })
    specOptions.value = Array.from(set)

    if (specOptions.value.length === 0 && searchForm.name && searchForm.name.trim()) {
      const similarResp = await searchSimilarBaseMaterials(searchForm.name, 50)
      const similar = similarResp.data || similarResp
      const list = Array.isArray(similar) ? similar : (similar.items || [])
      const set2 = new Set(specOptions.value)
      list.forEach(i => { if (i.specification) set2.add(i.specification) })
      specOptions.value = Array.from(set2)
    }
  } catch (e) {
    specOptions.value = []
  } finally {
    loadingSpecs.value = false
  }
}

watch(() => searchForm.name, (nv) => {
  if (specTimer) {
    clearTimeout(specTimer)
  }
  specTimer = setTimeout(() => {
    if (nv && nv.trim()) {
      fetchSpecOptions()
    } else {
      specOptions.value = []
      searchForm.specification = ''
    }
  }, 300)
})

// 可用地区选项
const availableRegions = ref([])

// 分页数据
const pagination = reactive({
  page: 1,
  size: 100,
  total: 0
})

// 字段映射
const fieldMapping = reactive({
  name: '',
  specification: '',
  unit: '',
  price: '',
  category: '',
  region: ''
})

// 导入结果
const importResult = reactive({
  success: false,
  message: '',
  successCount: 0,
  failedCount: 0
})

// 材料表单
const materialForm = reactive({
  id: null,  // 添加id字段用于编辑
  name: '',
  specification: '',
  unit: '',
  price: '',
  category: '',
  region: '',
  source: '',
  remarks: '',
  effective_date: new Date().toISOString()  // 默认当前时间
})

// 重置表单
const resetMaterialForm = () => {
  Object.assign(materialForm, {
    id: null,
    name: '',
    specification: '',
    unit: '',
    price: '',
    category: '',
    region: '',
    source: '',
    remarks: '',
    effective_date: new Date().toISOString()
  })
  isEditing.value = false
}

// 表单验证规则
const materialRules = {
  name: [
    { required: true, message: '请输入材料名称', trigger: 'blur' }
  ],
  unit: [
    { required: true, message: '请输入单位', trigger: 'blur' }
  ],
  price: [
    { required: true, message: '请输入参考价格', trigger: 'blur' },
    { 
      validator: (rule, value, callback) => {
        if (value === '' || value === null || value === undefined) {
          callback(new Error('请输入参考价格'))
        } else if (isNaN(value) || Number(value) <= 0) {
          callback(new Error('请输入有效的价格'))
        } else {
          callback()
        }
      }, 
      trigger: 'blur' 
    }
  ],
  category: [
    { required: true, message: '请选择材料分类', trigger: 'change' }
  ],
  region: [
    { required: true, message: '请选择适用地区', trigger: 'change' }
  ],
  source: [
    { required: true, message: '请选择数据来源', trigger: 'change' }
  ]
}

// 计算属性
const canNextStep = computed(() => {
  if (uploadStep.value === 0) return uploadFileList.value.length > 0
  if (uploadStep.value === 1) return fieldMapping.name && fieldMapping.unit && fieldMapping.price
  return true
})

// 获取材料列表
const fetchMaterials = async () => {
  loading.value = true
  try {
    // 构建查询参数
    const params = {
      page: pagination.page,
      page_size: pagination.size,
      name: searchForm.name,
      specification: searchForm.specification,
      price_type: searchForm.price_type,
      region: searchForm.region,
      price_date: searchForm.price_date,
      // 添加时间戳防止缓存
      _t: Date.now()
    }
    
    const response = await getBaseMaterials(params, { __skipLoading: true })
    console.log('获取基准材料数据响应:', response)
    const result = response.data?.data || response.data || response
    
    materials.value = result.items || result.materials || []
    pagination.total = result.total || 0
    await nextTick()
    syncSelectionOnPage(materialTableRef, materials.value)
    console.log(`加载了 ${materials.value.length} 个基准材料，总数: ${pagination.total}`)
    
  } catch (error) {
    console.error('加载基准材料失败:', error)
    ElMessage.error('加载失败: ' + (error.message || error))
    materials.value = []
    pagination.total = 0
  } finally {
    loading.value = false
  }
}

// 状态相关方法
const getCategoryType = (category) => {
  const typeMap = {
    'building': 'primary',
    'decoration': 'success',
    'machinery': 'warning',
    'labor': 'info',
    'other': 'default'
  }
  return typeMap[category] || 'default'
}

const getCategoryText = (category) => {
  const textMap = {
    'building': '建筑材料',
    'decoration': '装修材料',
    'machinery': '机械设备',
    'labor': '人工费',
    'other': '其他'
  }
  return textMap[category] || category
}

// 获取期数文本
const getPeriodText = (row) => {
  // 优先使用price_date字段
  if (row.price_date) {
    const [year, month] = row.price_date.split('-')
    return `${year}年${month}月`
  }

  // 兼容旧数据：从category解析
  if (row.category) {
    const parts = row.category.split('-')
    if (parts.length >= 3) {
      const year = parts[1]
      const month = parts[2]
      return `${year}年${month}月`
    }
  }

  return '-'
}

// 获取期刊显示文本
const getJournalText = (row) => {
  // 优先使用price_type + province/city 字段构建期刊信息
  if (row.price_type && (row.province || row.city)) {
    const province = getProvinceText(row.province)
    const city = getCityText(row.city)

    if (row.price_type === 'provincial') {
      // 省刊：显示省份 + 省刊
      return `${province}省刊`
    } else if (row.price_type === 'municipal' && city) {
      // 市刊：显示城市 + 市刊
      return `${city}市刊`
    }
  }

  // 兼容旧数据：使用journal_type字段
  if (row.journal_type) {
    return row.journal_type
  }

  // 从category字段解析
  if (row.category) {
    const parts = row.category.split('-')
    if (parts.length >= 3) {
      const type = parts[0] === 'municipal' ? '市刊' : '省刊'
      return type
    }
  }

  return '-'
}

// 获取期刊标签类型
const getJournalType = (row) => {
  if (row.price_type === 'provincial') {
    return 'success'
  } else if (row.price_type === 'municipal') {
    return 'primary'
  }

  // 兼容旧数据
  if (row.journal_type && row.journal_type.includes('省')) {
    return 'success'
  }

  return 'primary'
}

// 获取适用地区文本
const getApplicableRegionText = (row) => {
  // 省刊显示省份名称
  if (row.price_type === 'provincial') {
    if (row.province) {
      return getProvinceText(row.province) + '省'
    }
    return '浙江省' // 默认显示浙江省
  }

  // 市刊显示具体适用地区
  if (row.price_type === 'municipal' && row.region) {
    return getRegionText(row.region)
  }

  // 兼容旧数据
  if (row.journal_type && row.journal_type.includes('省') && row.province) {
    return getProvinceText(row.province) + '省'
  }

  if (row.journal_type && row.journal_type.includes('市') && row.region) {
    return getRegionText(row.region)
  }

  return '-'
}

// 地区代码到中文的映射
const getRegionText = (region) => {
  if (!region) return '-'

  // 如果已经是中文，直接返回
  if (/[\u4e00-\u9fa5]/.test(region)) {
    return region
  }

  // 英文代码到中文的映射
  const textMap = {
    'beijing': '北京市',
    'shanghai': '上海市',
    'guangzhou': '广州市',
    'shenzhen': '深圳市',
    'hangzhou': '杭州市',
    'nanjing': '南京市',
    'suzhou': '苏州市',
    'wuxi': '无锡市',
    'national': '全国',
    'zhejiang': '浙江省',
    'jiangsu': '江苏省',
    'guangdong': '广东省'
  }

  return textMap[region] || region
}

// 省份代码到中文的映射
const getProvinceText = (province) => {
  if (!province) return ''

  if (/[\u4e00-\u9fa5]/.test(province)) {
    return province.replace(/省$/, '') // 去掉末尾的"省"字
  }

  const provinceMap = {
    'zhejiang': '浙江',
    'jiangsu': '江苏',
    'guangdong': '广东',
    'shandong': '山东',
    'beijing': '北京',
    'shanghai': '上海',
    'tianjin': '天津',
    'chongqing': '重庆'
  }

  return provinceMap[province] || province
}

// 城市代码到中文的映射
const getCityText = (city) => {
  if (!city) return ''

  if (/[\u4e00-\u9fa5]/.test(city)) {
    return city.replace(/市$/, '') // 去掉末尾的"市"字
  }

  const cityMap = {
    'hangzhou': '杭州',
    'ningbo': '宁波',
    'wenzhou': '温州',
    'nanjing': '南京',
    'suzhou': '苏州',
    'wuxi': '无锡',
    'guangzhou': '广州',
    'shenzhen': '深圳',
    'beijing': '北京',
    'shanghai': '上海'
  }

  return cityMap[city] || city
}

const getSourceType = (source) => {
  const typeMap = {
    'government': 'success',
    'market': 'primary',
    'supplier': 'warning',
    'historical': 'info',
    'other': 'default'
  }
  return typeMap[source] || 'default'
}

const getSourceText = (source) => {
  const textMap = {
    'government': '政府信息价',
    'market': '市场调研',
    'supplier': '供应商报价',
    'historical': '历史数据',
    'other': '其他'
  }
  return textMap[source] || source
}

// 搜索和重置
const handleSearch = () => {
  pagination.page = 1
  fetchMaterials()
}

const handleReset = () => {
  Object.assign(searchForm, {
    name: '',
    specification: '',
    price_type: '',
    region: '',
    price_date: ''
  })
  specOptions.value = []
  pagination.page = 1
  fetchMaterials()
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

// 选择处理（跨页全选封装 + 同步本地选中项）
const onSelectionChange = (selection) => {
  handleSelectionChange(selection, materials.value)
  selectedMaterials.value = selection
}

// 上传步骤控制
const nextStep = () => {
  if (uploadStep.value < 3) {
    uploadStep.value++
  }
}

const prevStep = () => {
  if (uploadStep.value > 0) {
    uploadStep.value--
  }
}

const closeUploadDialog = () => {
  showUploadDialog.value = false
  uploadStep.value = 0
  uploadFileList.value = []
  excelColumns.value = []
  previewData.value = []
  Object.assign(fieldMapping, {
    name: '',
    specification: '',
    unit: '',
    price: '',
    category: '',
    region: ''
  })
}

// 文件上传处理
const handleUploadFileChange = (file) => {
  // 模拟解析Excel列名
  setTimeout(() => {
    excelColumns.value = ['材料名称', '规格型号', '单位', '参考价格', '分类', '地区']
  }, 500)
}

const beforeUpload = () => {
  return false
}

const downloadTemplate = () => {
  ElMessage.info('下载模板功能开发中...')
}

const startImport = async () => {
  importing.value = true
  try {
    // TODO: 调用导入API
    // 模拟导入过程
    setTimeout(() => {
      importResult.success = true
      importResult.message = '材料数据导入成功'
      importResult.successCount = previewData.value.length
      importResult.failedCount = 0
      uploadStep.value = 3
      importing.value = false
      fetchMaterials() // 刷新列表
    }, 2000)
  } catch (error) {
    importResult.success = false
    importResult.message = '导入失败: ' + error.message
    uploadStep.value = 3
    importing.value = false
  }
}

// CRUD操作
const viewMaterial = (material) => {
  currentMaterial.value = material
  showDetailDialog.value = true
}

// 导入材料 - 跳转到材料导入页面
const handleImportMaterials = () => {
  // 跳转到材料导入页面
  router.push('/materials/import')
}

// 新建材料
const handleCreateMaterial = () => {
  resetMaterialForm()
  showCreateDialog.value = true
}

// 编辑材料
const editMaterial = (material) => {
  isEditing.value = true
  Object.assign(materialForm, {
    id: material.id,
    name: material.name,
    specification: material.specification || '',
    unit: material.unit,
    price: material.price,
    category: material.category || '',
    region: material.region || '',
    source: material.source || '',
    remarks: material.remarks || '',
    effective_date: material.effective_date || new Date().toISOString()
  })
  showCreateDialog.value = true
}

// 对话框关闭处理
const handleDialogClose = () => {
  showCreateDialog.value = false
  resetMaterialForm()
}

const deleteMaterial = async (material) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除材料 "${material.name}" 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 调用删除API
    await deleteBaseMaterial(material.id)
    ElMessage.success('删除成功')
    fetchMaterials()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleMaterialSubmit = async () => {
  console.log('开始提交材料表单')
  submitting.value = true
  try {
    // 表单验证
    if (materialFormRef.value) {
      console.log('开始表单验证')
      try {
        const isValid = await materialFormRef.value.validate()
        if (!isValid) {
          console.log('表单验证失败')
          submitting.value = false
          return
        }
        console.log('表单验证通过')
      } catch (validationError) {
        console.log('表单验证出错:', validationError)
        submitting.value = false
        return
      }
    }
    
    if (isEditing.value) {
      // 更新材料
      console.log('更新材料，ID:', materialForm.id, '数据:', materialForm)
      const result = await updateBaseMaterial(materialForm.id, materialForm)
      console.log('更新结果:', result)
      ElMessage.success('更新成功')
    } else {
      // 创建材料
      console.log('创建材料，数据:', materialForm)
      const result = await createBaseMaterial(materialForm)
      console.log('创建结果:', result)
      ElMessage.success('创建成功')
    }
    
    handleDialogClose()  // 使用统一的关闭处理
    fetchMaterials()
  } catch (error) {
    console.error('材料操作失败:', error)
    ElMessage.error('操作失败: ' + (error.message || error))
  } finally {
    submitting.value = false
  }
}

const handleBatchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除已选择的 ${selectedCount.value} 个材料吗？`,
      '批量删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 计算跨页选中ID
    const fetchAllIds = async () => {
      const size = 1000
      let page = 1
      const ids = []
      while (true) {
        const resp = await getBaseMaterials({
          page,
          page_size: size,
          name: searchForm.name,
          price_type: searchForm.price_type,
          region: searchForm.region,
          price_date: searchForm.price_date
        })
        const result = resp.data?.data || resp.data || resp
        const list = result.items || result.materials || []
        list.forEach(item => ids.push(item.id))
        const total = result.total || 0
        if (page * size >= total || list.length < size) break
        page += 1
      }
      return ids
    }

    loading.value = true
    const ids = await getSelectedIds(fetchAllIds)
    await batchDeleteBaseMaterials(ids)
    
    ElMessage.success(`成功删除 ${ids.length} 个材料`)
    clearAllSelection()
    fetchMaterials()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败: ' + (error.message || '未知错误'))
    }
  } finally {
    loading.value = false
  }
}

const handleBatchEdit = () => {
  ElMessage.info('批量编辑功能开发中...')
}

const handleExport = () => {
  ElMessage.info('导出功能开发中...')
}

// 获取可用地区选项
const fetchAvailableRegions = async (priceType = null) => {
  try {
    const response = await getRegions(priceType, { __skipLoading: true })
    const regions = response.data?.regions || response.regions || []

    // 转换为选项格式
    availableRegions.value = regions
      .filter(region => region && region.trim()) // 过滤空值
      .sort() // 排序
      .map(region => ({
        label: getRegionDisplayText(region, priceType),
        value: region
      }))

    console.log('获取到的地区选项:', availableRegions.value)
  } catch (error) {
    console.error('获取地区选项失败:', error)
    // 设置默认地区选项
    availableRegions.value = [
      { label: '杭州市区', value: 'hangzhou' },
      { label: '浙江省', value: 'zhejiang' },
      { label: '全国', value: 'national' }
    ]
  }
}

// 根据期刊类型获取地区显示文本
const getRegionDisplayText = (region, priceType) => {
  if (priceType === 'provincial') {
    // 省刊显示省份中文名
    const provinceMap = {
      'zhejiang': '浙江省',
      'jiangsu': '江苏省',
      'guangdong': '广东省',
      'shandong': '山东省',
      'beijing': '北京市',
      'shanghai': '上海市',
      'tianjin': '天津市',
      'chongqing': '重庆市'
    }
    return provinceMap[region] || region
  } else {
    // 市刊显示原始地区名称
    return getRegionText(region)
  }
}

// 生命周期
onMounted(() => {
  fetchAvailableRegions() // 先获取地区选项
  fetchMaterials()
})

// 页面激活时重新获取数据（解决从其他页面跳转过来时数据不更新的问题）
onActivated(() => {
  fetchMaterials()
})

// 监听路由变化，确保每次进入页面都刷新数据
watch(() => route.path, (newPath) => {
  // 当路由变化且当前页面是基准材料页面时，刷新数据
  if (newPath === '/materials/base' || newPath.includes('/materials/base')) {
    console.log('路由切换到基准材料页面，刷新数据')
    fetchMaterials()
  }
})

// 监听路由查询参数，处理从Excel上传页面跳转过来的情况
watch(() => route.query, (newQuery) => {
  // 如果有刷新标记，立即刷新数据
  if (newQuery.refresh === 'true') {
    console.log('检测到刷新标记，刷新基准材料数据')
    fetchMaterials()
    // 清除URL中的刷新参数，避免重复刷新
    const newQuery = { ...route.query }
    delete newQuery.refresh
    router.replace({ query: newQuery })
  }
}, { immediate: true })

// 监听期刊类型变化，自动更新地区选项
watch(() => searchForm.price_type, async (newPriceType) => {
  console.log('期刊类型改变:', newPriceType)

  // 清空当前地区选择
  searchForm.region = ''

  // 根据新的期刊类型获取对应的地区选项
  await fetchAvailableRegions(newPriceType)
}, { immediate: false })

// 计算表格高度
const tableHeight = computed(() => {
  // 简单的计算方式：window高度减去其他组件的估算高度
  const windowHeight = window.innerHeight || 800
  const otherHeight = 400 // 估算其他组件高度（导航、头部、搜索、工具栏、分页等）
  return Math.max(400, windowHeight - otherHeight) // 最小400px
})
</script>

<style lang="scss" scoped>
.base-materials-container {
  min-height: calc(100vh - 60px); // 最小高度，减去顶部导航栏高度
  display: flex;
  flex-direction: column;
  padding: 20px;
  box-sizing: border-box;

  .page-header {
    flex-shrink: 0; // 不允许页头收缩
    margin-bottom: 20px;
  }

  .search-card {
    flex-shrink: 0; // 不允许搜索栏收缩
    margin-bottom: 20px;
  }

  .materials-card {
    flex-grow: 1; // 占据剩余空间
    min-height: 500px; // 设置最小高度确保有足够空间
  }
}

// 操作按钮样式
.action-buttons {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: nowrap;
  
  .el-button {
    margin: 0;
    padding: 2px 6px;
    font-size: 12px;
    height: auto;
    min-height: 22px;
    white-space: nowrap;
    
    &.is-link {
      padding: 2px 4px;
    }
  }
}

// 材料详情样式
.material-detail {
  .detail-item {
    margin-bottom: 16px;
    display: flex;
    align-items: flex-start;
    
    label {
      font-weight: 500;
      color: $text-primary;
      min-width: 80px;
      flex-shrink: 0;
    }
    
    span, p {
      color: $text-regular;
      flex: 1;
      word-break: break-all;
    }
    
    p {
      margin: 0;
      line-height: 1.5;
    }
  }
  
  .el-row {
    margin-bottom: 0;
    
    &:not(:last-child) {
      margin-bottom: 12px;
    }
  }
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
    gap: 12px;
  }
}

.search-card {
  margin-bottom: 20px;

  .search-form {
    display: flex;
    flex-wrap: wrap;
    gap: 12px 16px;

    .el-form-item {
      margin-bottom: 12px;
    }
  }
}

.materials-card {
  display: flex;
  flex-direction: column;
  height: 100%; // 确保卡片占满父容器

  :deep(.el-card__body) {
    padding: 20px;
    display: flex;
    flex-direction: column;
    flex: 1; // 让卡片body占满卡片空间
    min-height: 0; // 允许flex收缩
  }

  .table-toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    flex-shrink: 0; // 不允许工具栏收缩

    .toolbar-left {
      display: flex;
      gap: 12px;
    }

    .toolbar-right {
      display: flex;
      gap: 8px;
    }
  }

  // 表格容器
  .materials-table {
    // 确保表格有固定高度以启用滚动
    :deep(.el-table__body-wrapper) {
      overflow-y: auto; // 启用垂直滚动
      overflow-x: auto; // 启用水平滚动
    }

    // 确保表格在各种缩放下都能正常显示
    :deep(.el-table__fixed-right) {
      z-index: 10;
    }

    // 确保表格头部固定
    :deep(.el-table__header-wrapper) {
      z-index: 2;
    }
  }

  .pagination-wrapper {
    display: flex;
    justify-content: center;
    margin-top: 20px;
    padding: 15px 0 20px 0; // 增加底部内边距确保完整显示
    flex-shrink: 0; // 不允许分页组件收缩
    background: white; // 确保背景色
    border-top: 1px solid #ebeef5; // 添加顶部边框作为分隔
    position: relative; // 确保层级
    z-index: 5; // 确保在表格之上
    min-height: 60px; // 确保最小高度

    // 在小屏幕或高缩放比例下的响应式处理
    .el-pagination {
      flex-wrap: wrap; // 允许分页元素换行
      justify-content: center;

      // 调整分页按钮间距
      .btn-prev,
      .btn-next,
      .el-pager li {
        margin: 2px;
      }
    }
  }

  // 空状态
  .el-empty {
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
}

// 上传对话框样式
.upload-container {
  .upload-steps {
    margin-bottom: 32px;
  }

  .step-content {
    min-height: 300px;
    
    .template-section {
      margin-top: 24px;
      text-align: center;
    }

    .mapping-section {
      h3 {
        font-size: 16px;
        margin-bottom: 8px;
      }

      .mapping-tip {
        font-size: 14px;
        color: $text-secondary;
        margin-bottom: 20px;
      }
    }

    .preview-section {
      h3 {
        font-size: 16px;
        margin-bottom: 8px;
      }

      .preview-tip {
        font-size: 14px;
        color: $text-secondary;
        margin-bottom: 20px;
      }

      .preview-more {
        text-align: center;
        margin-top: 16px;
      }
    }

    .result-section {
      .result-stats {
        margin-bottom: 16px;
        
        p {
          margin: 4px 0;
          font-size: 14px;
        }
      }
    }
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

// 响应式设计
@media (max-width: $breakpoint-md) {
  .base-materials-container {
    padding: 10px;
    height: 100vh; // 保持全屏高度

    .materials-card {
      // 移动端表格调整
      :deep(.el-card__body) {
        padding: 10px;
      }

      .el-table {
        // 移动端表格字体调整
        font-size: 12px;
      }

      .pagination-wrapper {
        padding: 15px 0; // 移动端增加更多间距

        .el-pagination {
          // 移动端分页器调整
          .el-pagination__sizes,
          .el-pagination__jump {
            display: none; // 隐藏不必要的元素
          }
        }
      }
    }
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

  .search-form {
    .el-form-item {
      width: 100% !important;
      margin-bottom: 16px !important;
    }
  }

  .table-toolbar {
    flex-direction: column;
    gap: 12px;

    .toolbar-left,
    .toolbar-right {
      width: 100%;
      justify-content: flex-start;
    }
  }
}
</style>
