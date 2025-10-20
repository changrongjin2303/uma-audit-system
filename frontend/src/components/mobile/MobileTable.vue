<template>
  <div class="mobile-table" :class="{ 'is-mobile': isMobile }">
    <!-- 移动端卡片布局 -->
    <div v-if="isMobile" class="mobile-cards">
      <div class="table-header" v-if="showHeader">
        <slot name="header">
          <h3>{{ title }}</h3>
          <div class="header-actions">
            <slot name="headerActions" />
          </div>
        </slot>
      </div>

      <!-- 搜索和筛选 -->
      <div class="search-bar" v-if="searchable">
        <el-input
          v-model="searchValue"
          placeholder="搜索..."
          clearable
          prefix-icon="Search"
          @input="handleSearch"
        />
      </div>

      <!-- 卡片列表 -->
      <div class="cards-container" ref="cardsContainer">
        <div
          v-for="(item, index) in visibleData"
          :key="getRowKey ? getRowKey(item) : index"
          class="table-card"
          @click="handleRowClick(item, index)"
        >
          <slot name="card" :row="item" :index="index">
            <!-- 默认卡片布局 -->
            <div class="card-content">
              <div
                v-for="column in displayColumns"
                :key="column.prop"
                class="card-field"
              >
                <label class="field-label">{{ column.label }}</label>
                <div class="field-value">
                  <slot
                    :name="column.prop"
                    :row="item"
                    :column="column"
                    :index="index"
                  >
                    {{ getFieldValue(item, column.prop) }}
                  </slot>
                </div>
              </div>
            </div>
            
            <!-- 操作按钮 -->
            <div class="card-actions" v-if="$slots.actions">
              <slot name="actions" :row="item" :index="index" />
            </div>
          </slot>
        </div>

        <!-- 无数据 -->
        <div v-if="visibleData.length === 0" class="empty-data">
          <el-empty :description="emptyText" />
        </div>

        <!-- 加载更多 -->
        <div v-if="infiniteScroll && !finished" class="load-more" ref="loadMore">
          <el-button
            v-if="!loading"
            type="text"
            @click="loadMoreData"
            :disabled="loading"
          >
            加载更多
          </el-button>
          <div v-else class="loading-indicator">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>加载中...</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 桌面端表格布局 -->
    <el-table
      v-else
      :data="visibleData"
      :loading="loading"
      :empty-text="emptyText"
      v-bind="tableProps"
      @row-click="handleRowClick"
      @selection-change="handleSelectionChange"
      @sort-change="handleSortChange"
    >
      <el-table-column
        v-if="selectable"
        type="selection"
        width="55"
        :selectable="selectableCallback"
      />
      
      <el-table-column
        v-for="column in displayColumns"
        :key="column.prop"
        :prop="column.prop"
        :label="column.label"
        :width="column.width"
        :min-width="column.minWidth"
        :sortable="column.sortable"
        :formatter="column.formatter"
        :show-overflow-tooltip="column.showOverflowTooltip !== false"
      >
        <template #default="{ row, column: col, $index }">
          <slot
            :name="column.prop"
            :row="row"
            :column="col"
            :index="$index"
          >
            {{ getFieldValue(row, column.prop) }}
          </slot>
        </template>
      </el-table-column>

      <el-table-column
        v-if="$slots.actions"
        label="操作"
        :width="actionsWidth"
        fixed="right"
      >
        <template #default="{ row, $index }">
          <slot name="actions" :row="row" :index="$index" />
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="table-pagination" v-if="pagination && !infiniteScroll">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="pageSizes"
        :layout="paginationLayout"
        :background="!isMobile"
        :size="isMobile ? 'small' : 'default'"
        :hide-on-single-page="isMobile"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { Search, Loading } from '@element-plus/icons-vue'
import { useResponsive, useInfiniteScroll, DEVICE_TYPES } from '@/utils/mobile'

export default {
  name: 'MobileTable',
  components: {
    Search,
    Loading
  },
  props: {
    // 表格数据
    data: {
      type: Array,
      default: () => []
    },
    // 列配置
    columns: {
      type: Array,
      default: () => []
    },
    // 表格标题
    title: {
      type: String,
      default: ''
    },
    // 是否显示表头
    showHeader: {
      type: Boolean,
      default: true
    },
    // 是否可搜索
    searchable: {
      type: Boolean,
      default: false
    },
    // 是否可选择
    selectable: {
      type: Boolean,
      default: false
    },
    // 选择回调
    selectableCallback: {
      type: Function,
      default: () => true
    },
    // 行点击
    rowKey: {
      type: [String, Function],
      default: null
    },
    // 是否启用分页
    pagination: {
      type: Boolean,
      default: true
    },
    // 是否启用无限滚动
    infiniteScroll: {
      type: Boolean,
      default: false
    },
    // 分页大小选项
    pageSizes: {
      type: Array,
      default: () => [10, 20, 50, 100]
    },
    // 默认分页大小
    defaultPageSize: {
      type: Number,
      default: 20
    },
    // 总数
    total: {
      type: Number,
      default: 0
    },
    // 加载状态
    loading: {
      type: Boolean,
      default: false
    },
    // 空数据文本
    emptyText: {
      type: String,
      default: '暂无数据'
    },
    // 操作列宽度
    actionsWidth: {
      type: [String, Number],
      default: 150
    },
    // 表格属性
    tableProps: {
      type: Object,
      default: () => ({})
    }
  },
  emits: [
    'row-click',
    'selection-change',
    'sort-change',
    'search',
    'size-change',
    'current-change',
    'load-more'
  ],
  setup(props, { emit }) {
    const responsive = useResponsive()
    const cardsContainer = ref(null)
    const loadMore = ref(null)
    
    const searchValue = ref('')
    const currentPage = ref(1)
    const pageSize = ref(props.defaultPageSize)
    const finished = ref(false)

    // 计算属性
    const isMobile = computed(() => responsive.device === DEVICE_TYPES.MOBILE)

    const displayColumns = computed(() => {
      if (isMobile.value) {
        // 移动端只显示主要列
        return props.columns.filter(col => col.important !== false).slice(0, 4)
      }
      return props.columns
    })

    const paginationLayout = computed(() => {
      if (isMobile.value) {
        return 'prev, pager, next'
      } else if (responsive.device === DEVICE_TYPES.TABLET) {
        return 'total, prev, pager, next'
      } else {
        return 'total, sizes, prev, pager, next, jumper'
      }
    })

    const filteredData = computed(() => {
      let data = props.data

      // 搜索过滤
      if (searchValue.value && props.searchable) {
        const keyword = searchValue.value.toLowerCase()
        data = data.filter(item => {
          return props.columns.some(col => {
            const value = getFieldValue(item, col.prop)
            return String(value).toLowerCase().includes(keyword)
          })
        })
      }

      return data
    })

    const visibleData = computed(() => {
      if (props.infiniteScroll) {
        return filteredData.value
      }

      const start = (currentPage.value - 1) * pageSize.value
      const end = start + pageSize.value
      return filteredData.value.slice(start, end)
    })

    // 无限滚动
    const infiniteScrollHook = useInfiniteScroll(
      async () => {
        emit('load-more')
        return []
      },
      {
        disabled: !props.infiniteScroll,
        distance: 50
      }
    )

    // 方法
    const getRowKey = (row) => {
      if (typeof props.rowKey === 'function') {
        return props.rowKey(row)
      } else if (typeof props.rowKey === 'string') {
        return row[props.rowKey]
      }
      return null
    }

    const getFieldValue = (row, prop) => {
      if (!prop) return ''
      
      const keys = prop.split('.')
      let value = row
      
      for (const key of keys) {
        value = value?.[key]
        if (value === undefined || value === null) {
          return ''
        }
      }
      
      return value
    }

    const handleRowClick = (row, index) => {
      emit('row-click', row, index)
    }

    const handleSelectionChange = (selection) => {
      emit('selection-change', selection)
    }

    const handleSortChange = (sort) => {
      emit('sort-change', sort)
    }

    const handleSearch = (value) => {
      emit('search', value)
    }

    const handleSizeChange = (size) => {
      pageSize.value = size
      currentPage.value = 1
      emit('size-change', size)
    }

    const handleCurrentChange = (page) => {
      currentPage.value = page
      emit('current-change', page)
    }

    const loadMoreData = () => {
      infiniteScrollHook.load()
    }

    // 监听滚动事件（移动端无限滚动）
    const handleScroll = () => {
      if (props.infiniteScroll && isMobile.value && cardsContainer.value) {
        infiniteScrollHook.handleScroll({
          target: cardsContainer.value
        })
      }
    }

    // 生命周期
    onMounted(() => {
      if (props.infiniteScroll && isMobile.value && cardsContainer.value) {
        cardsContainer.value.addEventListener('scroll', handleScroll, { passive: true })
      }
    })

    onBeforeUnmount(() => {
      if (cardsContainer.value) {
        cardsContainer.value.removeEventListener('scroll', handleScroll)
      }
    })

    // 监听设备变化
    watch(() => responsive.device, (newDevice) => {
      if (newDevice === DEVICE_TYPES.MOBILE) {
        // 切换到移动端时，调整分页大小
        if (pageSize.value > 20) {
          pageSize.value = 20
        }
      }
    })

    return {
      responsive,
      cardsContainer,
      loadMore,
      searchValue,
      currentPage,
      pageSize,
      finished,
      isMobile,
      displayColumns,
      paginationLayout,
      visibleData,
      loading: infiniteScrollHook.loading,
      getRowKey,
      getFieldValue,
      handleRowClick,
      handleSelectionChange,
      handleSortChange,
      handleSearch,
      handleSizeChange,
      handleCurrentChange,
      loadMoreData
    }
  }
}
</script>

<style scoped>
.mobile-table {
  width: 100%;
}

/* 移动端样式 */
.mobile-cards {
  width: 100%;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid #ebeef5;
  margin-bottom: 16px;
}

.table-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.search-bar {
  margin-bottom: 16px;
}

.cards-container {
  max-height: 60vh;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

.table-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 12px;
  padding: 16px;
  border: 1px solid #ebeef5;
  transition: all 0.3s ease;
  -webkit-tap-highlight-color: transparent;
}

.table-card:active {
  background-color: #f5f7fa;
  transform: scale(0.98);
}

.card-content {
  margin-bottom: 12px;
}

.card-field {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  min-height: 32px;
}

.card-field:last-child {
  margin-bottom: 0;
}

.field-label {
  font-size: 13px;
  color: #909399;
  min-width: 80px;
  flex-shrink: 0;
}

.field-value {
  font-size: 14px;
  color: #303133;
  text-align: right;
  flex: 1;
  word-break: break-all;
}

.card-actions {
  border-top: 1px solid #f0f2f5;
  padding-top: 12px;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.card-actions :deep(.el-button) {
  min-width: 60px;
  height: 32px;
  font-size: 12px;
}

.empty-data {
  text-align: center;
  padding: 40px 0;
}

.load-more {
  text-align: center;
  padding: 16px 0;
}

.loading-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #909399;
  font-size: 14px;
}

/* 桌面端分页 */
.table-pagination {
  margin-top: 20px;
  text-align: right;
}

.is-mobile .table-pagination {
  text-align: center;
  margin-top: 16px;
}

.is-mobile :deep(.el-pagination) {
  justify-content: center;
}

.is-mobile :deep(.el-pagination .el-pager li) {
  min-width: 32px;
  height: 32px;
  line-height: 32px;
  font-size: 14px;
}

/* 响应式断点 */
@media (max-width: 768px) {
  .table-card {
    margin-bottom: 8px;
    padding: 12px;
    border-radius: 6px;
  }

  .card-field {
    margin-bottom: 6px;
    min-height: 28px;
  }

  .field-label {
    font-size: 12px;
    min-width: 70px;
  }

  .field-value {
    font-size: 13px;
  }

  .card-actions {
    padding-top: 8px;
  }
}

/* 平板样式优化 */
@media (min-width: 769px) and (max-width: 1024px) {
  .table-card {
    padding: 18px;
    margin-bottom: 16px;
  }

  .card-field {
    margin-bottom: 10px;
  }
}

/* 滚动条样式 */
.cards-container::-webkit-scrollbar {
  width: 4px;
}

.cards-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 2px;
}

.cards-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 2px;
}

.cards-container::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>