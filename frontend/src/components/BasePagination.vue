<template>
  <div class="pagination-wrapper">
    <el-pagination
      v-model:current-page="innerPage"
      v-model:page-size="innerSize"
      :total="total"
      :page-sizes="pageSizes"
      :pager-count="pagerCount"
      :layout="layout"
      background
      @current-change="onPageChange"
      @size-change="onSizeChange"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  // 与 el-pagination 对齐的 v-model 命名，便于无缝替换
  currentPage: { type: Number, default: 1 },
  pageSize: { type: Number, default: 20 },
  total: { type: Number, default: 0 },
  pageSizes: {
    type: Array,
    default: () => [10, 20, 50, 100, 500, 1000, 2000]
  },
  pagerCount: { type: Number, default: 11 },
  layout: {
    type: String,
    default: 'total, sizes, prev, pager, next, jumper'
  }
})

const emit = defineEmits([
  'update:currentPage',
  'update:pageSize',
  // 同时透传 Element Plus 的事件名，便于现有监听不改动
  'current-change',
  'size-change',
  // 也提供语义化别名（可选）
  'page-change'
])

const innerPage = computed({
  get: () => props.currentPage,
  set: (val) => emit('update:currentPage', val)
})

const innerSize = computed({
  get: () => props.pageSize,
  set: (val) => emit('update:pageSize', val)
})

const onPageChange = (page) => {
  emit('current-change', page)
  emit('page-change', page)
}

const onSizeChange = (size) => {
  emit('size-change', size)
}
</script>

<style lang="scss" scoped>
.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
</style>

