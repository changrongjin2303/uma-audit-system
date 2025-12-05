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
      <el-table-column prop="remark" label="备注" width="150" show-overflow-tooltip>
        <template #default="{ row }">
          <span>{{ row.remark || row.verification_notes || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <div class="action-buttons">
            <el-button
              type="primary"
              link
              size="small"
              :icon="View"
              @click="$emit('view', row)"
            >
              查看
            </el-button>
            <el-button
              type="primary"
              link
              size="small"
              :icon="Edit"
              @click="$emit('edit', row)"
            >
              编辑
            </el-button>
            <el-button
              type="danger"
              link
              size="small"
              :icon="Delete"
              @click="handleDelete(row)"
            >
              删除
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
import { ref, onMounted, watch } from 'vue'
import { View, Edit, Delete } from '@element-plus/icons-vue'
import { formatNumber } from '@/utils'
import { getBaseMaterials, deleteBaseMaterial } from '@/api/materials'
import { ElMessage, ElMessageBox } from 'element-plus'

const props = defineProps({
  period: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['view', 'edit', 'refresh-parent'])

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
      // 省刊时 province 需要匹配
      // 市刊时 region 需要匹配 (backend logic handles this via region param mostly, but let's be specific if needed)
      // The backend `get_materials` uses `region` param to match either province or region depending on price_type.
      // So passing `region: props.period.region` should work if `props.period.region` contains the correct value (province name for provincial, city name for municipal).
      // Wait, `get_material_periods` returns `region`, `province`, `city`.
      // If `price_type` is 'provincial', `region` in `BaseMaterial` table stores 'XX省' usually?
      // Let's check backend `get_material_periods`: it selects `region`.
      _t: Date.now()
    }
    
    // Adjust region parameter based on period type to match backend search logic
    if (props.period.price_type === 'provincial') {
        params.region = props.period.province
    } else if (props.period.price_type === 'municipal') {
        params.region = props.period.region // likely the city name or region code
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

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除材料 "${row.name}" 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await deleteBaseMaterial(row.id)
    ElMessage.success('删除成功')
    fetchMaterials()
    emit('refresh-parent') // Notify parent to maybe update counts
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
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

