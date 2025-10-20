import { ref, computed } from 'vue'

// 通用：跨页选择/全选所有逻辑
// 使用方式：
// const sel = useSelectionAcrossPages('id')
// el-table 增加 :row-key="row => row.id" :reserve-selection="true"
// @selection-change="(s)=>sel.handleSelectionChange(s, currentPageRows)"
// 页面切换或数据刷新后：sel.syncSelectionOnPage(tableRef, currentPageRows)
export function useSelectionAcrossPages(rowKey = 'id') {
  const allSelected = ref(false) // 是否全选（所有页）
  const selectedIds = ref(new Set()) // 常规模式：显式选择的ID集合
  const excludedIds = ref(new Set()) // 全选模式：被取消的ID集合

  const clearAll = () => {
    allSelected.value = false
    selectedIds.value.clear()
    excludedIds.value.clear()
  }

  const toggleSelectAll = (enable = true) => {
    allSelected.value = enable
    selectedIds.value.clear()
    excludedIds.value.clear()
  }

  const handleSelectionChange = (selection, pageRows = []) => {
    const pageIds = new Set(pageRows.map(r => (typeof rowKey === 'function' ? rowKey(r) : r[rowKey])))
    if (allSelected.value) {
      const selectedPageIds = new Set(selection.map(r => (typeof rowKey === 'function' ? rowKey(r) : r[rowKey])))
      // 在全选模式下，记录本页未选中的为排除项；选中的从排除项移除
      pageIds.forEach(id => {
        if (!selectedPageIds.has(id)) excludedIds.value.add(id)
        else excludedIds.value.delete(id)
      })
    } else {
      // 非全选模式：先移除本页旧选择，再加入本页新选择
      pageIds.forEach(id => selectedIds.value.delete(id))
      selection.forEach(r => {
        const id = typeof rowKey === 'function' ? rowKey(r) : r[rowKey]
        selectedIds.value.add(id)
      })
    }
  }

  const syncSelectionOnPage = (tableRef, pageRows = []) => {
    if (!tableRef?.value) return
    tableRef.value.clearSelection()
    pageRows.forEach(row => {
      const id = typeof rowKey === 'function' ? rowKey(row) : row[rowKey]
      const shouldSelect = allSelected.value
        ? !excludedIds.value.has(id)
        : selectedIds.value.has(id)
      if (shouldSelect) tableRef.value.toggleRowSelection(row, true)
    })
  }

  const getSelectedIds = async (getAllIdsFn) => {
    if (allSelected.value) {
      const allIds = await Promise.resolve(getAllIdsFn ? getAllIdsFn() : [])
      return allIds.filter(id => !excludedIds.value.has(id))
    }
    return Array.from(selectedIds.value)
  }

  const createSelectedCount = (totalRef) => computed(() => {
    const total = typeof totalRef === 'function' ? totalRef() : (totalRef?.value ?? 0)
    return allSelected.value ? Math.max(0, (total || 0) - excludedIds.value.size) : selectedIds.value.size
  })

  return {
    allSelected,
    selectedIds,
    excludedIds,
    toggleSelectAll,
    clearAll,
    handleSelectionChange,
    syncSelectionOnPage,
    getSelectedIds,
    createSelectedCount
  }
}

