<template>
  <div class="project-material-detail">
    <!-- 加载状态 -->
    <div v-if="loading" v-loading="loading" style="height: 300px;" />
    
    <!-- 材料详情内容 -->
    <template v-else-if="material">
      <!-- 页面标题 -->
      <div class="page-header">
        <div class="header-content">
          <h1 class="page-title">{{ material.material_name }}</h1>
          <p class="page-subtitle">
            <span>项目材料详情</span>
            <el-divider direction="vertical" />
            <span>{{ material.specification || '无规格' }}</span>
          </p>
        </div>
        <div class="header-actions">
          <el-button @click="$router.back()">
            <el-icon><ArrowLeft /></el-icon>
            返回
          </el-button>
        </div>
      </div>

      <!-- 材料信息卡片 -->
      <el-row :gutter="20">
        <!-- 基本信息 -->
        <el-col :xs="24" :lg="12">
          <el-card class="info-card">
            <template #header>
              <div class="card-header">
                <span>基本信息</span>
              </div>
            </template>
            
            <div class="info-list">
              <div class="info-item">
                <span class="label">材料名称：</span>
                <span class="value">{{ material.material_name }}</span>
              </div>
              <div class="info-item">
                <span class="label">规格型号：</span>
                <span class="value">{{ material.specification || '无' }}</span>
              </div>
              <div class="info-item">
                <span class="label">计量单位：</span>
                <span class="value">{{ material.unit }}</span>
              </div>
              <div class="info-item">
                <span class="label">数量：</span>
                <span class="value">{{ formatNumber(material.quantity) }}</span>
              </div>
              <div class="info-item">
                <span class="label">单价：</span>
                <span class="value price">¥{{ formatNumber(material.unit_price) }}</span>
              </div>
              <div class="info-item">
                <span class="label">总价：</span>
                <span class="value total-price">¥{{ formatNumber(material.total_price) }}</span>
              </div>
              <div class="info-item">
                <span class="label">分类：</span>
                <span class="value">{{ material.category || '未分类' }}</span>
              </div>
              <div class="info-item">
                <span class="label">Excel行号：</span>
                <span class="value">{{ material.row_number || '无' }}</span>
              </div>
            </div>
          </el-card>
        </el-col>

        <!-- 匹配状态 -->
        <el-col :xs="24" :lg="12">
          <el-card class="info-card">
            <template #header>
              <div class="card-header">
                <span>匹配状态</span>
              </div>
            </template>
            
            <div class="match-info">
              <div class="match-status">
                <el-tag 
                  :type="material.is_matched ? 'success' : 'info'" 
                  size="large"
                  class="status-tag"
                >
                  {{ material.is_matched ? '已匹配' : '未匹配' }}
                </el-tag>
              </div>

              <div v-if="material.is_matched" class="match-details">
                <div class="info-item">
                  <span class="label">匹配得分：</span>
                  <span class="value">
                    <el-progress 
                      :percentage="material.match_score ? (material.match_score * 100) : 0"
                      :color="getScoreColor(material.match_score)"
                      :stroke-width="8"
                      text-inside
                    />
                  </span>
                </div>
                <div class="info-item">
                  <span class="label">匹配方法：</span>
                  <span class="value">{{ getMatchMethodText(material.match_method) }}</span>
                </div>
                <div v-if="matchedBaseMaterial" class="matched-material">
                  <h4>匹配的市场信息价材料</h4>
                  <div class="base-material-card">
                    <div class="info-item">
                      <span class="label">材料名称：</span>
                      <span class="value">{{ matchedBaseMaterial.name }}</span>
                    </div>
                    <div class="info-item">
                      <span class="label">规格：</span>
                      <span class="value">{{ matchedBaseMaterial.specification || '无' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="label">单位：</span>
                      <span class="value">{{ matchedBaseMaterial.unit }}</span>
                    </div>
                    <div class="info-item">
                      <span class="label">基准价格：</span>
                      <span class="value base-price">¥{{ formatNumber(matchedBaseMaterial.price) }}</span>
                    </div>
                    <div class="info-item">
                      <span class="label">地区：</span>
                      <span class="value">{{ matchedBaseMaterial.region || '全国' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="label">数据来源：</span>
                      <span class="value">{{ matchedBaseMaterial.source || '无' }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div v-if="!material.is_matched" class="no-match">
                <el-empty description="该材料未找到匹配的市场信息价材料">
                  <el-button type="primary" @click="searchSimilarMaterials">
                    搜索相似材料
                  </el-button>
                </el-empty>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 价格比较 -->
      <el-card v-if="material.is_matched && matchedBaseMaterial" class="price-comparison">
        <template #header>
          <div class="card-header">
            <span>价格分析对比</span>
          </div>
        </template>
        
        <div class="comparison-content">
          <div class="price-item project-price">
            <div class="price-label">项目材料单价</div>
            <div class="price-value">¥{{ formatNumber(material.unit_price) }}</div>
          </div>
          
          <div class="comparison-arrow">
            <el-icon><ArrowRight /></el-icon>
          </div>
          
          <div class="price-item base-price">
            <div class="price-label">市场信息价材料单价</div>
            <div class="price-value">¥{{ formatNumber(matchedBaseMaterial.price) }}</div>
          </div>
          
          <div class="price-diff">
            <div class="diff-label">价格差异</div>
            <div class="diff-value" :class="getDiffClass()">
              {{ getPriceDifference() }}
            </div>
            <div class="diff-percentage" :class="getDiffClass()">
              ({{ getPriceDifferencePercentage() }})
            </div>
          </div>
        </div>
      </el-card>

      <!-- 备注信息 -->
      <el-card v-if="material.notes" class="notes-card">
        <template #header>
          <div class="card-header">
            <span>备注信息</span>
          </div>
        </template>
        <div class="notes-content">
          {{ material.notes }}
        </div>
      </el-card>

      <!-- 操作按钮 -->
      <div class="actions">
        <el-button v-if="!material.is_matched" type="primary" @click="startMatching">
          开始匹配
        </el-button>
        <el-button v-if="material.is_matched" @click="cancelMatch">
          取消匹配
        </el-button>
        <el-button @click="editMaterial">
          编辑材料
        </el-button>
      </div>
    </template>

    <!-- 材料不存在 -->
    <el-empty v-else description="材料不存在或已被删除">
      <el-button type="primary" @click="$router.back()">
        返回材料列表
      </el-button>
    </el-empty>

    <!-- 编辑材料对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑材料信息"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        :rules="editFormRules"
        label-width="100px"
      >
        <el-form-item label="材料名称" prop="material_name">
          <el-input v-model="editForm.material_name" placeholder="请输入材料名称" />
        </el-form-item>
        
        <el-form-item label="规格型号">
          <el-input v-model="editForm.specification" placeholder="请输入规格型号" />
        </el-form-item>
        
        <el-form-item label="计量单位" prop="unit">
          <el-input v-model="editForm.unit" placeholder="请输入计量单位" />
        </el-form-item>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="数量" prop="quantity">
              <el-input-number 
                v-model="editForm.quantity" 
                :min="0.01" 
                :precision="2"
                :step="1"
                style="width: 100%"
                placeholder="请输入数量"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单价" prop="unit_price">
              <el-input-number 
                v-model="editForm.unit_price" 
                :min="0.01" 
                :precision="2"
                :step="0.01"
                style="width: 100%"
                placeholder="请输入单价"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="材料分类">
          <el-input v-model="editForm.category" placeholder="请输入材料分类" />
        </el-form-item>
        
        <el-form-item label="备注信息">
          <el-input
            v-model="editForm.notes"
            type="textarea"
            :rows="3"
            placeholder="请输入备注信息"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showEditDialog = false">取消</el-button>
          <el-button type="primary" :loading="loading" @click="saveEdit">
            保存
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import { getProjectMaterial, cancelProjectMaterialMatch, updateProjectMaterial } from '@/api/projects'
import { getBaseMaterial } from '@/api/materials'
import { formatDate, formatNumber } from '@/utils'
import { ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()

// 响应式数据
const loading = ref(false)
const material = ref(null)
const matchedBaseMaterial = ref(null)
const showEditDialog = ref(false)
const editForm = ref({
  material_name: '',
  specification: '',
  unit: '',
  quantity: 0,
  unit_price: 0,
  category: '',
  notes: ''
})
const editFormRef = ref()

// 获取材料详情
const fetchMaterialDetail = async () => {
  loading.value = true
  try {
    const projectId = route.params.projectId
    const materialId = route.params.materialId
    
    // 获取项目材料详情
    const materialData = await getProjectMaterial(projectId, materialId)
    material.value = materialData
    
    // 如果已匹配，获取对应的基准材料信息
    if (materialData.is_matched && materialData.matched_material_id) {
      try {
        const baseMaterialData = await getBaseMaterial(materialData.matched_material_id)
        matchedBaseMaterial.value = baseMaterialData
      } catch (error) {
        console.warn('获取匹配的基准材料失败:', error)
      }
    }
  } catch (error) {
    console.error('获取材料详情失败:', error)
    ElMessage.error('获取材料详情失败')
  } finally {
    loading.value = false
  }
}

// 获取匹配方法文本
const getMatchMethodText = (method) => {
  const methodMap = {
    'auto_matched': '自动匹配',
    'user_confirmed': '人工确认',
    'fuzzy_match': '模糊匹配',
    'exact_match': '精确匹配'
  }
  return methodMap[method] || method || '未知'
}

// 获取匹配得分颜色
const getScoreColor = (score) => {
  if (!score) return '#909399'
  if (score >= 0.9) return '#67c23a'
  if (score >= 0.7) return '#e6a23c'
  return '#f56c6c'
}

// 计算价格差异
const getPriceDifference = () => {
  if (!matchedBaseMaterial.value || !material.value) return '0.00'
  const diff = material.value.unit_price - matchedBaseMaterial.value.price
  return (diff >= 0 ? '+' : '') + formatNumber(Math.abs(diff))
}

// 计算价格差异百分比
const getPriceDifferencePercentage = () => {
  if (!matchedBaseMaterial.value || !material.value || matchedBaseMaterial.value.price === 0) return '0%'
  const percentage = ((material.value.unit_price - matchedBaseMaterial.value.price) / matchedBaseMaterial.value.price) * 100
  return (percentage >= 0 ? '+' : '') + percentage.toFixed(1) + '%'
}

// 获取差异样式类
const getDiffClass = () => {
  if (!matchedBaseMaterial.value || !material.value) return ''
  const diff = material.value.unit_price - matchedBaseMaterial.value.price
  if (diff > 0) return 'positive'
  if (diff < 0) return 'negative'
  return 'neutral'
}

// 操作方法
const searchSimilarMaterials = () => {
  ElMessage.info('搜索相似材料功能开发中...')
}

const startMatching = () => {
  ElMessage.info('开始匹配功能开发中...')
}

const cancelMatch = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要取消该材料的匹配吗？取消后该材料将变为未匹配状态。',
      '取消匹配确认',
      {
        confirmButtonText: '确定取消',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    loading.value = true
    await cancelProjectMaterialMatch(route.params.projectId, route.params.materialId)
    
    ElMessage.success('已取消材料匹配')
    
    // 重新获取材料详情
    await fetchMaterialDetail()
    
    // 提示用户操作成功，询问是否返回项目详情页面
    try {
      await ElMessageBox.confirm(
        '材料匹配已取消，是否返回项目详情页面查看更新后的材料列表？',
        '操作完成',
        {
          confirmButtonText: '返回项目详情',
          cancelButtonText: '留在当前页面',
          type: 'success'
        }
      )
      
      // 用户选择返回，带上刷新参数
      router.push({
        path: `/projects/${route.params.projectId}`,
        query: { refresh: 'materials', timestamp: Date.now() }
      })
      
    } catch {
      // 用户选择留在当前页面，不做任何操作
    }
    
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消匹配失败:', error)
      ElMessage.error('取消匹配失败: ' + (error.response?.data?.detail || error.message || '未知错误'))
    }
  } finally {
    loading.value = false
  }
}

const editMaterial = () => {
  if (material.value) {
    // 初始化编辑表单
    editForm.value = {
      material_name: material.value.material_name || '',
      specification: material.value.specification || '',
      unit: material.value.unit || '',
      quantity: material.value.quantity || 0,
      unit_price: material.value.unit_price || 0,
      category: material.value.category || '',
      notes: material.value.notes || ''
    }
    showEditDialog.value = true
  }
}

// 保存材料编辑
const saveEdit = async () => {
  if (!editFormRef.value) return
  
  try {
    // 表单验证
    await editFormRef.value.validate()
    
    loading.value = true
    
    // 调用更新API
    await updateProjectMaterial(route.params.projectId, route.params.materialId, {
      material_name: editForm.value.material_name,
      specification: editForm.value.specification || null,
      unit: editForm.value.unit,
      quantity: Number(editForm.value.quantity),
      unit_price: Number(editForm.value.unit_price),
      category: editForm.value.category || null,
      notes: editForm.value.notes || null
    })
    
    ElMessage.success('材料信息更新成功')
    showEditDialog.value = false
    
    // 重新获取材料详情
    await fetchMaterialDetail()
    
    // 提示用户操作成功，询问是否返回项目详情页面
    try {
      await ElMessageBox.confirm(
        '材料信息已更新，是否返回项目详情页面查看更新后的材料列表？',
        '操作完成',
        {
          confirmButtonText: '返回项目详情',
          cancelButtonText: '留在当前页面',
          type: 'success'
        }
      )
      
      // 用户选择返回，带上刷新参数
      router.push({
        path: `/projects/${route.params.projectId}`,
        query: { refresh: 'materials', timestamp: Date.now() }
      })
      
    } catch {
      // 用户选择留在当前页面，不做任何操作
    }
    
  } catch (error) {
    console.error('更新材料失败:', error)
    ElMessage.error('更新材料失败: ' + (error.response?.data?.detail || error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

// 表单验证规则
const editFormRules = {
  material_name: [
    { required: true, message: '请输入材料名称', trigger: 'blur' },
    { min: 2, max: 200, message: '材料名称长度在2到200个字符', trigger: 'blur' }
  ],
  unit: [
    { required: true, message: '请输入计量单位', trigger: 'blur' }
  ],
  quantity: [
    { required: true, message: '请输入数量', trigger: 'blur' },
    { type: 'number', min: 0.01, message: '数量必须大于0', trigger: 'blur' }
  ],
  unit_price: [
    { required: true, message: '请输入单价', trigger: 'blur' },
    { type: 'number', min: 0.01, message: '单价必须大于0', trigger: 'blur' }
  ]
}

// 页面初始化
onMounted(() => {
  fetchMaterialDetail()
})
</script>

<style lang="scss" scoped>
.project-material-detail {
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
      color: #909399;
      font-size: 14px;
      margin: 0;
    }
  }
}

.info-card {
  margin-bottom: 20px;

  .card-header {
    font-weight: 600;
    color: #303133;
  }
}

.info-list {
  .info-item {
    display: flex;
    margin-bottom: 16px;
    align-items: flex-start;

    .label {
      width: 100px;
      color: #909399;
      font-size: 14px;
      flex-shrink: 0;
    }

    .value {
      color: #303133;
      font-size: 14px;
      flex: 1;

      &.price {
        color: #e6a23c;
        font-weight: 600;
      }

      &.total-price {
        color: #67c23a;
        font-weight: 600;
        font-size: 16px;
      }

      &.base-price {
        color: #409eff;
        font-weight: 600;
      }
    }
  }
}

.match-info {
  .match-status {
    margin-bottom: 20px;
    text-align: center;

    .status-tag {
      font-size: 16px;
      padding: 8px 16px;
    }
  }

  .match-details {
    .info-item {
      margin-bottom: 16px;
    }

    .matched-material {
      margin-top: 24px;

      h4 {
        margin: 0 0 16px 0;
        color: #303133;
        font-size: 16px;
      }

      .base-material-card {
        background: #f8f9fa;
        padding: 16px;
        border-radius: 8px;
        border: 1px solid #e4e7ed;
      }
    }
  }

  .no-match {
    text-align: center;
    padding: 40px 0;
  }
}

.price-comparison {
  margin: 20px 0;

  .comparison-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px;
    color: white;

    .price-item {
      text-align: center;
      flex: 1;

      .price-label {
        font-size: 14px;
        opacity: 0.9;
        margin-bottom: 8px;
      }

      .price-value {
        font-size: 24px;
        font-weight: 600;
      }
    }

    .comparison-arrow {
      font-size: 24px;
      margin: 0 20px;
    }

    .price-diff {
      text-align: center;
      flex: 1;

      .diff-label {
        font-size: 14px;
        opacity: 0.9;
        margin-bottom: 8px;
      }

      .diff-value {
        font-size: 20px;
        font-weight: 600;
        margin-bottom: 4px;

        &.positive {
          color: #f56c6c;
        }

        &.negative {
          color: #67c23a;
        }

        &.neutral {
          color: #909399;
        }
      }

      .diff-percentage {
        font-size: 14px;
        opacity: 0.9;
      }
    }
  }
}

.notes-card {
  margin: 20px 0;

  .notes-content {
    padding: 16px;
    background: #f8f9fa;
    border-radius: 8px;
    border: 1px solid #e4e7ed;
    color: #606266;
    line-height: 1.6;
  }
}

.actions {
  text-align: center;
  margin-top: 30px;

  .el-button {
    margin: 0 8px;
  }
}

// 响应式适配
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;

    .header-actions {
      width: 100%;
    }
  }

  .price-comparison .comparison-content {
    flex-direction: column;
    gap: 20px;

    .comparison-arrow {
      transform: rotate(90deg);
      margin: 0;
    }
  }
}
</style>
