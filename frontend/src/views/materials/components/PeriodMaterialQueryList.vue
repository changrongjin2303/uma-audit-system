<template>
  <div class="period-material-list">
    <el-table
      v-loading="loading"
      :data="materials"
      :row-key="row => row.id"
      stripe
      style="width: 100%"
      size="small"
      border
    >
      <el-table-column prop="material_code" label="编码" width="120">
        <template #default="{ row }">
          <span>{{ row.material_code || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="name" label="材料名称" min-width="200" show-overflow-tooltip />
      <el-table-column prop="specification" label="规格型号" width="150" show-overflow-tooltip>
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
      <el-table-column prop="is_verified" label="收藏状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_verified ? 'success' : 'info'" size="small">
            {{ row.is_verified ? '已收藏' : '未收藏' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <div class="action-buttons">
            <el-button
              type="primary"
              link
              size="small"
              @click="$emit('view', row)"
            >
              查看
            </el-button>
            <el-button 
              :type="row.is_verified ? 'warning' : 'success'" 
              link 
              size="small" 
              @click="toggleFavorite(row)"
            >
              {{ row.is_verified ? '取消收藏' : '收藏' }}
            </el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-wrapper" v-if="total > 0">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="size"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        size="small"
        @size-change="fetchMaterials"
        @current-change="fetchMaterials"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { formatNumber } from '@/utils'
import { getBaseMaterials, updateBaseMaterial } from '@/api/materials'
import { ElMessage } from 'element-plus'

const props = defineProps({
  period: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['view', 'refresh-parent'])

const loading = ref(false)
const materials = ref([])
const page = ref(1)
const size = ref(20)
const total = ref(0)

const fetchMaterials = async () => {
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: size.value,
      price_date: props.period.price_date,
      price_type: props.period.price_type,
      region: props.period.region,
      _t: Date.now()
    }
    
    // Adjust region parameter based on period type to match backend search logic
    if (props.period.price_type === 'provincial') {
        params.region = props.period.province
    } else if (props.period.price_type === 'municipal') {
        params.region = props.period.region
    } else {
        params.region = props.period.region
    }

    const response = await getBaseMaterials(params, { __skipLoading: true })
    const result = response.data?.data || response.data || response
    
    materials.value = result.items || result.materials || []
    total.value = result.total || 0
  } catch (error) {
    console.error('加载材料失败:', error)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

// 切换收藏状态
const toggleFavorite = async (material) => {
  try {
    const isCurrentlyFavorite = material.is_verified
    const newFavoriteStatus = !isCurrentlyFavorite
    
    // 更新材料收藏状态
    await updateBaseMaterial(material.id, {
      is_verified: newFavoriteStatus
    })
    
    // 更新本地数据
    material.is_verified = newFavoriteStatus
    
    if (newFavoriteStatus) {
      ElMessage.success(`材料 "${material.name}" 已添加到收藏`)
    } else {
      ElMessage.success(`材料 "${material.name}" 已取消收藏`)
    }
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error('操作失败: ' + (error.message || '未知错误'))
  }
}

onMounted(() => {
  fetchMaterials()
})

// Expose fetch method
defineExpose({ fetchMaterials })
</script>

<style scoped lang="scss">
.period-material-list {
  padding: 10px 20px;
  background-color: #f8f9fa;
  
  .pagination-wrapper {
    display: flex;
    justify-content: flex-end;
    margin-top: 10px;
  }
  
  .action-buttons {
    display: flex;
    gap: 4px;
  }
}
</style>

