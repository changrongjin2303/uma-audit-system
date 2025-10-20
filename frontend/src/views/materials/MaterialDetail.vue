<template>
  <div class="material-detail-container">
    <!-- 加载状态 -->
    <div v-if="loading" v-loading="loading" style="height: 200px;" />
    
    <template v-else-if="material">
      <!-- 材料标题栏 -->
      <div class="page-header">
        <div class="header-content">
          <div class="title-section">
            <h1 class="page-title">{{ material.name }}</h1>
            <el-tag :type="getCategoryType(material.category)" class="category-tag">
              {{ getCategoryText(material.category) }}
            </el-tag>
          </div>
          <p class="page-subtitle">
            <span class="spec-info">
              <el-icon><Box /></el-icon>
              {{ material.specification || '无规格' }}
            </span>
            <span class="unit-info">
              <el-icon><Promotion /></el-icon>
              {{ material.unit }}
            </span>
            <span class="region-info">
              <el-icon><Location /></el-icon>
              {{ getRegionText(material.region) }}
            </span>
          </p>
        </div>
        <div class="header-actions">
          <el-button @click="$router.back()">
            返回
          </el-button>
          <el-button
            type="warning"
            :icon="StarFilled"
            @click="toggleFavorite"
            :loading="favoriteLoading"
          >
            {{ material.is_favorite ? '取消收藏' : '添加收藏' }}
          </el-button>
          <el-button
            type="primary"
            :icon="Edit"
            @click="showEditDialog = true"
          >
            编辑
          </el-button>
        </div>
      </div>

      <!-- 价格信息卡片 -->
      <el-row :gutter="20" class="price-row">
        <el-col :xs="24" :sm="12" :lg="8">
          <div class="price-card current">
            <div class="price-icon">
              <el-icon><Money /></el-icon>
            </div>
            <div class="price-content">
              <div class="price-number">¥{{ formatNumber(material.price) }}</div>
              <div class="price-label">当前价格</div>
              <div class="price-time">{{ formatDate(material.updated_at) }}</div>
            </div>
          </div>
        </el-col>
        
        <el-col :xs="24" :sm="12" :lg="8">
          <div class="price-card average">
            <div class="price-icon">
              <el-icon><TrendCharts /></el-icon>
            </div>
            <div class="price-content">
              <div class="price-number">¥{{ formatNumber(priceStats.avgPrice) }}</div>
              <div class="price-label">平均价格</div>
              <div class="price-time">近30天</div>
            </div>
          </div>
        </el-col>
        
        <el-col :xs="24" :sm="12" :lg="8">
          <div class="price-card trend">
            <div class="price-icon">
              <el-icon><Promotion /></el-icon>
            </div>
            <div class="price-content">
              <div class="price-number" :class="getTrendClass()">
                {{ priceStats.priceChange >= 0 ? '+' : '' }}{{ priceStats.priceChange }}%
              </div>
              <div class="price-label">价格趋势</div>
              <div class="price-time">月环比</div>
            </div>
          </div>
        </el-col>
      </el-row>

      <!-- 主要内容区域 -->
      <el-row :gutter="20" class="content-row">
        <!-- 左侧：材料信息 -->
        <el-col :xs="24" :lg="8">
          <!-- 基本信息 -->
          <el-card class="info-card">
            <template #header>
              <span class="card-title">基本信息</span>
            </template>
            
            <div class="info-list">
              <div class="info-item">
                <span class="label">材料名称:</span>
                <span class="value">{{ material.name }}</span>
              </div>
              <div class="info-item">
                <span class="label">规格型号:</span>
                <span class="value">{{ material.specification || '无' }}</span>
              </div>
              <div class="info-item">
                <span class="label">计量单位:</span>
                <span class="value">{{ material.unit }}</span>
              </div>
              <div class="info-item">
                <span class="label">材料分类:</span>
                <span class="value">{{ getCategoryText(material.category) }}</span>
              </div>
              <div class="info-item">
                <span class="label">适用地区:</span>
                <span class="value">{{ getRegionText(material.region) }}</span>
              </div>
              <div class="info-item">
                <span class="label">数据来源:</span>
                <span class="value">
                  <el-tag :type="getSourceType(material.source)" size="small">
                    {{ getSourceText(material.source) }}
                  </el-tag>
                </span>
              </div>
              <div class="info-item">
                <span class="label">创建时间:</span>
                <span class="value">{{ formatDate(material.created_at) }}</span>
              </div>
              <div class="info-item">
                <span class="label">更新时间:</span>
                <span class="value">{{ formatDate(material.updated_at) }}</span>
              </div>
            </div>
            
            <div v-if="material.remarks" class="remarks">
              <h4>备注信息</h4>
              <p>{{ material.remarks }}</p>
            </div>
          </el-card>

          <!-- 使用统计 -->
          <el-card class="usage-card">
            <template #header>
              <span class="card-title">使用统计</span>
            </template>
            
            <div class="usage-stats">
              <div class="usage-item">
                <div class="usage-number">{{ usageStats.projectCount }}</div>
                <div class="usage-label">项目使用</div>
              </div>
              <div class="usage-item">
                <div class="usage-number">{{ usageStats.matchCount }}</div>
                <div class="usage-label">匹配次数</div>
              </div>
              <div class="usage-item">
                <div class="usage-number">{{ usageStats.viewCount }}</div>
                <div class="usage-label">查看次数</div>
              </div>
            </div>

            <div class="usage-chart">
              <!-- TODO: 添加使用趋势图表 -->
              <el-empty description="使用趋势图表开发中" :image-size="60" />
            </div>
          </el-card>
        </el-col>

        <!-- 右侧：价格历史和别名管理 -->
        <el-col :xs="24" :lg="16">
          <!-- 价格历史 -->
          <el-card class="history-card">
            <template #header>
              <div class="card-header">
                <span class="card-title">价格历史</span>
                <div class="header-actions">
                  <el-button
                    type="primary"
                    size="small"
                    :icon="Plus"
                    @click="showPriceDialog = true"
                  >
                    更新价格
                  </el-button>
                  <el-button
                    size="small"
                    :icon="TrendCharts"
                    @click="showTrendChart = !showTrendChart"
                  >
                    {{ showTrendChart ? '隐藏' : '显示' }}图表
                  </el-button>
                </div>
              </div>
            </template>

            <!-- 价格趋势图 -->
            <div v-if="showTrendChart" class="trend-chart">
              <div class="chart-container">
                <!-- TODO: 集成图表库显示价格趋势 -->
                <el-empty description="价格趋势图表开发中" :image-size="80" />
              </div>
            </div>

            <!-- 价格历史列表 -->
            <el-table
              v-loading="historyLoading"
              :data="priceHistory"
              stripe
              style="width: 100%"
            >
              <el-table-column prop="price" label="价格" width="120">
                <template #default="{ row }">
                  ¥{{ formatNumber(row.price) }}
                </template>
              </el-table-column>
              <el-table-column prop="change_reason" label="变更原因" min-width="150" />
              <el-table-column prop="source" label="数据来源" width="120">
                <template #default="{ row }">
                  <el-tag :type="getSourceType(row.source)" size="small">
                    {{ getSourceText(row.source) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="created_at" label="记录时间" width="180">
                <template #default="{ row }">
                  {{ formatDate(row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column prop="created_by_name" label="记录人" width="100" />
            </el-table>

            <!-- 分页 -->
            <div v-if="priceHistory.length > 0" class="pagination-wrapper">
              <el-pagination
                v-model:current-page="historyPagination.page"
                v-model:page-size="historyPagination.size"
                :total="historyPagination.total"
                :page-sizes="[10, 20, 50, 100, 500, 1000, 2000]"
                background
                layout="total, sizes, prev, pager, next"
                @size-change="handleHistorySizeChange"
                @current-change="handleHistoryPageChange"
              />
            </div>
          </el-card>

          <!-- 材料别名 -->
          <el-card class="alias-card">
            <template #header>
              <div class="card-header">
                <span class="card-title">材料别名</span>
                <div class="header-actions">
                  <el-button
                    type="primary"
                    size="small"
                    :icon="Plus"
                    @click="showAliasDialog = true"
                  >
                    添加别名
                  </el-button>
                </div>
              </div>
            </template>

            <div v-if="aliases.length === 0" class="empty-aliases">
              <el-empty description="暂无别名" :image-size="60">
                <el-button type="primary" @click="showAliasDialog = true">
                  添加第一个别名
                </el-button>
              </el-empty>
            </div>

            <div v-else class="aliases-list">
              <el-tag
                v-for="alias in aliases"
                :key="alias.id"
                :closable="true"
                size="large"
                class="alias-tag"
                @close="deleteAlias(alias)"
              >
                {{ alias.alias }}
              </el-tag>
            </div>
          </el-card>

          <!-- 相关材料推荐 -->
          <el-card class="recommendations-card">
            <template #header>
              <span class="card-title">相关材料推荐</span>
            </template>

            <div v-if="recommendations.length === 0" class="empty-recommendations">
              <el-empty description="暂无推荐" :image-size="60" />
            </div>

            <div v-else class="recommendations-list">
              <div
                v-for="item in recommendations"
                :key="item.id"
                class="recommendation-item"
                @click="$router.push(`/materials/${item.id}`)"
              >
                <div class="item-info">
                  <div class="item-name">{{ item.name }}</div>
                  <div class="item-meta">
                    <span class="item-spec">{{ item.specification || '无规格' }}</span>
                    <span class="item-price">¥{{ formatNumber(item.price) }}/{{ item.unit }}</span>
                  </div>
                </div>
                <div class="item-similarity">
                  相似度: {{ item.similarity }}%
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 编辑材料对话框 -->
      <el-dialog
        v-model="showEditDialog"
        title="编辑材料"
        width="600px"
        :close-on-click-modal="false"
      >
        <el-form
          ref="editFormRef"
          :model="editForm"
          :rules="editRules"
          label-width="100px"
        >
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="材料名称" prop="name">
                <el-input v-model="editForm.name" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="规格型号">
                <el-input v-model="editForm.specification" />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="单位" prop="unit">
                <el-input v-model="editForm.unit" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="参考价格" prop="price">
                <el-input v-model="editForm.price" type="number" step="0.01" />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="材料分类" prop="category">
                <el-select v-model="editForm.category" style="width: 100%">
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
                <el-select v-model="editForm.region" style="width: 100%">
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
            <el-select v-model="editForm.source" style="width: 100%">
              <el-option label="政府信息价" value="government" />
              <el-option label="市场调研" value="market" />
              <el-option label="供应商报价" value="supplier" />
              <el-option label="历史数据" value="historical" />
              <el-option label="其他" value="other" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="备注">
            <el-input
              v-model="editForm.remarks"
              type="textarea"
              :rows="3"
              maxlength="200"
              show-word-limit
            />
          </el-form-item>
        </el-form>
        
        <template #footer>
          <el-button @click="showEditDialog = false">取消</el-button>
          <el-button
            type="primary"
            :loading="updating"
            @click="handleUpdate"
          >
            更新
          </el-button>
        </template>
      </el-dialog>

      <!-- 更新价格对话框 -->
      <el-dialog
        v-model="showPriceDialog"
        title="更新价格"
        width="400px"
        :close-on-click-modal="false"
      >
        <el-form
          ref="priceFormRef"
          :model="priceForm"
          :rules="priceRules"
          label-width="100px"
        >
          <el-form-item label="新价格" prop="price">
            <el-input
              v-model="priceForm.price"
              type="number"
              step="0.01"
              placeholder="请输入新价格"
            />
          </el-form-item>
          
          <el-form-item label="变更原因" prop="change_reason">
            <el-input
              v-model="priceForm.change_reason"
              type="textarea"
              :rows="3"
              placeholder="请说明价格变更的原因"
              maxlength="200"
              show-word-limit
            />
          </el-form-item>
          
          <el-form-item label="数据来源" prop="source">
            <el-select v-model="priceForm.source" style="width: 100%">
              <el-option label="政府信息价" value="government" />
              <el-option label="市场调研" value="market" />
              <el-option label="供应商报价" value="supplier" />
              <el-option label="其他" value="other" />
            </el-select>
          </el-form-item>
        </el-form>
        
        <template #footer>
          <el-button @click="showPriceDialog = false">取消</el-button>
          <el-button
            type="primary"
            :loading="updatingPrice"
            @click="handlePriceUpdate"
          >
            更新价格
          </el-button>
        </template>
      </el-dialog>

      <!-- 添加别名对话框 -->
      <el-dialog
        v-model="showAliasDialog"
        title="添加材料别名"
        width="400px"
        :close-on-click-modal="false"
      >
        <el-form
          ref="aliasFormRef"
          :model="aliasForm"
          :rules="aliasRules"
          label-width="80px"
        >
          <el-form-item label="别名" prop="alias">
            <el-input
              v-model="aliasForm.alias"
              placeholder="请输入材料别名"
              maxlength="100"
              show-word-limit
            />
          </el-form-item>
        </el-form>
        
        <template #footer>
          <el-button @click="showAliasDialog = false">取消</el-button>
          <el-button
            type="primary"
            :loading="addingAlias"
            @click="handleAliasAdd"
          >
            添加
          </el-button>
        </template>
      </el-dialog>
    </template>

    <!-- 材料不存在 -->
    <el-result
      v-else
      icon="warning"
      title="材料不存在"
      sub-title="您访问的材料不存在或已被删除"
    >
      <template #extra>
        <el-button type="primary" @click="$router.push('/materials/base')">
          返回材料库
        </el-button>
      </template>
    </el-result>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Box,
  Promotion,
  Location,
  StarFilled,
  Edit,
  Money,
  TrendCharts,
  Plus
} from '@element-plus/icons-vue'
import { formatDate, formatNumber } from '@/utils'
import {
  getBaseMaterial,
  updateBaseMaterial,
  getMaterialPriceHistory,
  updateMaterialPrice,
  getMaterialAliases,
  addMaterialAlias,
  deleteMaterialAlias,
  markMaterialAsFavorite,
  unmarkMaterialAsFavorite,
  getMaterialRecommendations
} from '@/api/materials'

const route = useRoute()
const router = useRouter()

// 响应式数据
const loading = ref(false)
const updating = ref(false)
const updatingPrice = ref(false)
const addingAlias = ref(false)
const favoriteLoading = ref(false)
const historyLoading = ref(false)
const showEditDialog = ref(false)
const showPriceDialog = ref(false)
const showAliasDialog = ref(false)
const showTrendChart = ref(false)

const material = ref(null)
const priceHistory = ref([])
const aliases = ref([])
const recommendations = ref([])

// 统计数据
const priceStats = reactive({
  avgPrice: 0,
  priceChange: 0
})

const usageStats = reactive({
  projectCount: 0,
  matchCount: 0,
  viewCount: 0
})

// 分页数据
const historyPagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

// 编辑表单
const editForm = reactive({
  name: '',
  specification: '',
  unit: '',
  price: '',
  category: '',
  region: '',
  source: '',
  remarks: ''
})

const editRules = {
  name: [
    { required: true, message: '请输入材料名称', trigger: 'blur' }
  ],
  unit: [
    { required: true, message: '请输入单位', trigger: 'blur' }
  ],
  price: [
    { required: true, message: '请输入参考价格', trigger: 'blur' },
    { pattern: /^\d+(\.\d{1,2})?$/, message: '请输入有效的价格', trigger: 'blur' }
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

// 价格更新表单
const priceForm = reactive({
  price: '',
  change_reason: '',
  source: ''
})

const priceRules = {
  price: [
    { required: true, message: '请输入新价格', trigger: 'blur' },
    { pattern: /^\d+(\.\d{1,2})?$/, message: '请输入有效的价格', trigger: 'blur' }
  ],
  change_reason: [
    { required: true, message: '请说明变更原因', trigger: 'blur' }
  ],
  source: [
    { required: true, message: '请选择数据来源', trigger: 'change' }
  ]
}

// 别名表单
const aliasForm = reactive({
  alias: ''
})

const aliasRules = {
  alias: [
    { required: true, message: '请输入材料别名', trigger: 'blur' },
    { min: 2, max: 100, message: '别名长度在 2 到 100 个字符', trigger: 'blur' }
  ]
}

// 获取材料详情
const fetchMaterial = async () => {
  loading.value = true
  try {
    const response = await getBaseMaterial(route.params.id)
    material.value = response.data
    
    // 复制到编辑表单
    Object.assign(editForm, response.data)
  } catch (error) {
    ElMessage.error('获取材料详情失败')
    console.error('获取材料详情失败:', error)
  } finally {
    loading.value = false
  }
}

// 获取价格历史
const fetchPriceHistory = async () => {
  historyLoading.value = true
  try {
    const params = {
      page: historyPagination.page,
      size: historyPagination.size
    }
    const response = await getMaterialPriceHistory(route.params.id, params)
    priceHistory.value = response.data.items
    historyPagination.total = response.data.total
    
    // 计算价格统计
    if (response.data.stats) {
      Object.assign(priceStats, response.data.stats)
    }
  } catch (error) {
    console.error('获取价格历史失败:', error)
  } finally {
    historyLoading.value = false
  }
}

// 获取材料别名
const fetchAliases = async () => {
  try {
    const response = await getMaterialAliases(route.params.id)
    aliases.value = response.data
  } catch (error) {
    console.error('获取材料别名失败:', error)
  }
}

// 获取推荐材料
const fetchRecommendations = async () => {
  try {
    const response = await getMaterialRecommendations({
      material_id: route.params.id,
      limit: 5
    })
    recommendations.value = response.data
  } catch (error) {
    console.error('获取推荐材料失败:', error)
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

const getRegionText = (region) => {
  const textMap = {
    'beijing': '北京',
    'shanghai': '上海',
    'guangzhou': '广州',
    'shenzhen': '深圳',
    'national': '全国'
  }
  return textMap[region] || region
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

const getTrendClass = () => {
  if (priceStats.priceChange > 0) return 'trend-up'
  if (priceStats.priceChange < 0) return 'trend-down'
  return 'trend-stable'
}

// 操作方法
const toggleFavorite = async () => {
  favoriteLoading.value = true
  try {
    if (material.value.is_favorite) {
      await unmarkMaterialAsFavorite(material.value.id)
      material.value.is_favorite = false
      ElMessage.success('取消收藏成功')
    } else {
      await markMaterialAsFavorite(material.value.id)
      material.value.is_favorite = true
      ElMessage.success('添加收藏成功')
    }
  } catch (error) {
    ElMessage.error('操作失败')
    console.error('收藏操作失败:', error)
  } finally {
    favoriteLoading.value = false
  }
}

const handleUpdate = async () => {
  updating.value = true
  try {
    await updateBaseMaterial(material.value.id, editForm)
    ElMessage.success('更新成功')
    showEditDialog.value = false
    await fetchMaterial()
  } catch (error) {
    ElMessage.error('更新失败')
    console.error('更新失败:', error)
  } finally {
    updating.value = false
  }
}

const handlePriceUpdate = async () => {
  updatingPrice.value = true
  try {
    await updateMaterialPrice(material.value.id, priceForm)
    ElMessage.success('价格更新成功')
    showPriceDialog.value = false
    
    // 重置表单
    Object.assign(priceForm, {
      price: '',
      change_reason: '',
      source: ''
    })
    
    // 刷新数据
    await Promise.all([fetchMaterial(), fetchPriceHistory()])
  } catch (error) {
    ElMessage.error('价格更新失败')
    console.error('价格更新失败:', error)
  } finally {
    updatingPrice.value = false
  }
}

const handleAliasAdd = async () => {
  addingAlias.value = true
  try {
    await addMaterialAlias(material.value.id, aliasForm.alias)
    ElMessage.success('别名添加成功')
    showAliasDialog.value = false
    aliasForm.alias = ''
    await fetchAliases()
  } catch (error) {
    ElMessage.error('别名添加失败')
    console.error('别名添加失败:', error)
  } finally {
    addingAlias.value = false
  }
}

const deleteAlias = async (alias) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除别名 "${alias.alias}" 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await deleteMaterialAlias(material.value.id, alias.id)
    ElMessage.success('删除成功')
    await fetchAliases()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
      console.error('删除失败:', error)
    }
  }
}

// 分页处理
const handleHistorySizeChange = (size) => {
  historyPagination.size = size
  historyPagination.page = 1
  fetchPriceHistory()
}

const handleHistoryPageChange = (page) => {
  historyPagination.page = page
  fetchPriceHistory()
}

// 生命周期
onMounted(() => {
  fetchMaterial()
  fetchPriceHistory()
  fetchAliases()
  fetchRecommendations()
  
  // 模拟使用统计数据
  Object.assign(usageStats, {
    projectCount: 5,
    matchCount: 23,
    viewCount: 156
  })
})
</script>

<style lang="scss" scoped>
.material-detail-container {
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

      .category-tag {
        font-size: 12px;
      }
    }

    .page-subtitle {
      font-size: 14px;
      color: $text-secondary;
      margin: 0;
      display: flex;
      align-items: center;
      gap: 16px;

      .spec-info,
      .unit-info,
      .region-info {
        display: flex;
        align-items: center;
        gap: 4px;
      }
    }
  }

  .header-actions {
    display: flex;
    gap: 12px;
  }
}

.price-row {
  margin-bottom: 20px;

  .price-card {
    background: white;
    border-radius: 8px;
    padding: 20px;
    display: flex;
    align-items: center;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    margin-bottom: 20px;

    .price-icon {
      width: 50px;
      height: 50px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-right: 16px;
      font-size: 20px;
      color: white;
    }

    .price-content {
      flex: 1;

      .price-number {
        font-size: 24px;
        font-weight: 700;
        color: $text-primary;
        line-height: 1;
        margin-bottom: 4px;

        &.trend-up {
          color: $color-danger;
        }

        &.trend-down {
          color: $color-success;
        }

        &.trend-stable {
          color: $text-secondary;
        }
      }

      .price-label {
        font-size: 14px;
        color: $text-secondary;
        margin-bottom: 2px;
      }

      .price-time {
        font-size: 12px;
        color: $text-placeholder;
      }
    }

    &.current .price-icon {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    &.average .price-icon {
      background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }

    &.trend .price-icon {
      background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
    }
  }
}

.content-row {
  .info-card,
  .usage-card,
  .history-card,
  .alias-card,
  .recommendations-card {
    margin-bottom: 20px;

    .card-title {
      font-size: 16px;
      font-weight: 600;
      color: $text-primary;
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .header-actions {
        display: flex;
        gap: 8px;
      }
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

    .remarks {
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

  .usage-card {
    .usage-stats {
      display: flex;
      justify-content: space-around;
      margin-bottom: 20px;

      .usage-item {
        text-align: center;

        .usage-number {
          font-size: 20px;
          font-weight: 600;
          color: $primary-color;
          margin-bottom: 4px;
        }

        .usage-label {
          font-size: 12px;
          color: $text-secondary;
        }
      }
    }

    .usage-chart {
      height: 200px;
      display: flex;
      align-items: center;
      justify-content: center;
    }
  }

  .history-card {
    .trend-chart {
      margin-bottom: 20px;

      .chart-container {
        height: 300px;
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: $bg-color-base;
        border-radius: 8px;
      }
    }

    .pagination-wrapper {
      display: flex;
      justify-content: center;
      margin-top: 20px;
    }
  }

  .alias-card {
    .empty-aliases {
      padding: 20px;
      text-align: center;
    }

    .aliases-list {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;

      .alias-tag {
        margin: 0;
        padding: 8px 12px;
        font-size: 14px;
      }
    }
  }

  .recommendations-card {
    .empty-recommendations {
      padding: 20px;
      text-align: center;
    }

    .recommendations-list {
      .recommendation-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 0;
        border-bottom: 1px solid $border-color-lighter;
        cursor: pointer;
        transition: background-color 0.3s;

        &:hover {
          background-color: $bg-color-base;
          margin: 0 -20px;
          padding-left: 20px;
          padding-right: 20px;
        }

        &:last-child {
          border-bottom: none;
        }

        .item-info {
          flex: 1;

          .item-name {
            font-size: 16px;
            font-weight: 500;
            color: $text-primary;
            margin-bottom: 4px;
          }

          .item-meta {
            display: flex;
            gap: 12px;
            font-size: 13px;
            color: $text-secondary;

            .item-price {
              font-weight: 500;
              color: $primary-color;
            }
          }
        }

        .item-similarity {
          font-size: 12px;
          color: $text-secondary;
          padding: 4px 8px;
          background-color: $bg-color-base;
          border-radius: 4px;
        }
      }
    }
  }
}

// 响应式设计
@media (max-width: $breakpoint-md) {
  .material-detail-container {
    padding: 10px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;

    .header-content .page-subtitle {
      flex-direction: column;
      align-items: flex-start;
      gap: 8px;
    }

    .header-actions {
      width: 100%;
      justify-content: flex-start;
    }
  }

  .price-row {
    .price-card {
      padding: 16px;

      .price-icon {
        width: 40px;
        height: 40px;
        font-size: 18px;
      }

      .price-content .price-number {
        font-size: 20px;
      }
    }
  }

  .usage-stats {
    flex-direction: column;
    gap: 16px !important;
  }

  .card-header {
    flex-direction: column;
    gap: 12px !important;
    align-items: flex-start !important;

    .header-actions {
      width: 100%;
      justify-content: flex-start;
    }
  }

  .aliases-list {
    .alias-tag {
      width: 100%;
      justify-content: space-between;
    }
  }
}
</style>