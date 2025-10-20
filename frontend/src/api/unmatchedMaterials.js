import { request } from '@/utils/request'

// 获取无市场信息价材料列表
export function getUnmatchedMaterials(params) {
  return request.get('/unmatched-materials/', params)
}

// 获取无市场信息价材料详情
export function getUnmatchedMaterial(id) {
  return request.get(`/unmatched-materials/${id}`)
}

// 创建无市场信息价材料
export function createUnmatchedMaterial(data) {
  return request.post('/unmatched-materials/', data)
}

// 更新无市场信息价材料
export function updateUnmatchedMaterial(id, data) {
  return request.put(`/unmatched-materials/${id}`, data)
}

// 删除无市场信息价材料
export function deleteUnmatchedMaterial(id) {
  return request.delete(`/unmatched-materials/${id}`)
}

// 批量删除无市场信息价材料
export function batchDeleteUnmatchedMaterials(ids) {
  return request.post('/unmatched-materials/batch-operation', {
    material_ids: ids,
    operation: 'delete'
  })
}

// 获取Excel文件预览数据
export function getUnmatchedPreviewData(file, options = {}) {
  const formData = new FormData()
  formData.append('file', file)

  // 如果指定了工作表名称，作为参数传递
  if (options.sheet_name) {
    formData.append('sheet_name', options.sheet_name)
  }

  // 如果指定了最大行数
  if (options.max_rows) {
    formData.append('max_rows', options.max_rows)
  }

  return request.post('/unmatched-materials/get-preview-data', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 解析Excel文件结构
export function parseUnmatchedExcelStructure(file, options = {}) {
  const formData = new FormData()
  formData.append('file', file)

  // 如果指定了工作表名称，作为参数传递
  if (options.sheet_name) {
    formData.append('sheet_name', options.sheet_name)
  }

  return request.post('/unmatched-materials/parse-excel', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 导入无市场信息价材料数据
export function importUnmatchedMaterials(data) {
  return request.post('/unmatched-materials/import-materials', data, {
    specialTimeout: 'importMaterials',  // 使用特殊超时配置（5分钟）
    __skipLoading: true,  // 跳过全局loading，使用自定义进度显示
    loadingText: '正在导入无市场信息价材料数据，请耐心等待...'
  })
}

// 获取材料分类选项
export function getUnmatchedMaterialCategories() {
  return request.get('/unmatched-materials/categories/list')
}

// 搜索相似材料
export function searchSimilarUnmatchedMaterials(params) {
  return request.get('/unmatched-materials/search-similar', params)
}
