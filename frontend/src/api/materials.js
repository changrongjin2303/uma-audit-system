import { request } from '@/utils/request'

// 获取基准材料列表
export function getBaseMaterials(params, config = {}) {
  return request.get('/base-materials/', params, config)
}

// 获取基准材料详情
export function getBaseMaterial(id) {
  return request.get(`/base-materials/${id}`)
}

// 创建基准材料
export function createBaseMaterial(data) {
  return request.post('/base-materials/', data)
}

// 更新基准材料
export function updateBaseMaterial(id, data) {
  return request.put(`/base-materials/${id}`, data)
}

// 删除基准材料
export function deleteBaseMaterial(id) {
  return request.delete(`/base-materials/${id}`)
}

// 批量删除基准材料
export function batchDeleteBaseMaterials(ids) {
  return request.post('/base-materials/batch-operation', { 
    material_ids: ids,
    operation: 'delete'
  })
}

// 批量更新基准材料
export function batchUpdateBaseMaterials(data) {
  return request.post('/base-materials/batch-update', data)
}

// 上传基准材料文件
export function uploadBaseMaterials(file, onUploadProgress) {
  const formData = new FormData()
  formData.append('file', file)
  
  return request.post('/base-materials/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    onUploadProgress
  })
}

// 导入基准材料数据
export function importBaseMaterials(data) {
  return request.post('/base-materials/import-materials', data, {
    specialTimeout: 'importMaterials',  // 使用特殊超时配置（5分钟）
    __skipLoading: true,  // 跳过全局loading，使用自定义进度显示
    loadingText: '正在导入材料数据，请耐心等待...'
  })
}

// 导出基准材料数据
export function exportBaseMaterials(params) {
  return request.download('/base-materials/export', params)
}

// 获取基准材料导入模板
export function downloadBaseMaterialTemplate() {
  return request.download('/base-materials/template')
}

// 获取Excel文件预览数据
export function getPreviewData(file, options = {}) {
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
  
  return request.post('/base-materials/get-preview-data', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 解析Excel文件结构
export function parseExcelStructure(file, options = {}) {
  const formData = new FormData()
  formData.append('file', file)
  
  // 如果指定了工作表名称，作为参数传递
  if (options.sheet_name) {
    formData.append('sheet_name', options.sheet_name)
  }
  
  return request.post('/base-materials/parse-excel', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 预览导入数据
export function previewImportData(data) {
  return request.post('/base-materials/preview-import', data)
}

// 获取材料分类选项
export function getMaterialCategories() {
  return request.get('/base-materials/categories/')
}

// 获取地区选项
export function getRegions(priceType, config = {}) {
  const params = priceType ? { price_type: priceType } : {}
  return request.get('/base-materials/regions/list', params, config)
}

// 获取数据来源选项
export function getDataSources() {
  return request.get('/base-materials/sources/')
}

// 搜索材料（用于匹配）
export function searchMaterials(params) {
  return request.get('/base-materials/search', params)
}

// 获取材料匹配建议
export function getMaterialMatchSuggestions(materialName) {
  return request.get(`/base-materials/match-suggestions`, {
    name: materialName
  })
}

// 验证材料数据
export function validateMaterialData(data) {
  return request.post('/base-materials/validate', data)
}

// 获取材料统计信息
export function getMaterialStatistics() {
  return request.get('/base-materials/statistics')
}

// 获取价格历史记录
export function getMaterialPriceHistory(materialId, params) {
  return request.get(`/base-materials/${materialId}/price-history`, params)
}

// 更新材料价格
export function updateMaterialPrice(materialId, priceData) {
  return request.post(`/base-materials/${materialId}/update-price`, priceData)
}

// 批量更新材料价格
export function batchUpdateMaterialPrices(data) {
  return request.post('/base-materials/batch-update-prices', data)
}

// 获取材料别名
export function getMaterialAliases(materialId) {
  return request.get(`/base-materials/${materialId}/aliases`)
}

// 添加材料别名
export function addMaterialAlias(materialId, alias) {
  return request.post(`/base-materials/${materialId}/aliases`, { alias })
}

// 删除材料别名
export function deleteMaterialAlias(materialId, aliasId) {
  return request.delete(`/base-materials/${materialId}/aliases/${aliasId}`)
}

// 同步政府信息价数据
export function syncGovernmentPrices(region) {
  return request.post('/base-materials/sync-government-prices', { region })
}

// 获取同步任务状态
export function getSyncTaskStatus(taskId) {
  return request.get(`/base-materials/sync-tasks/${taskId}`)
}

// 获取材料使用频率统计
export function getMaterialUsageStats(params) {
  return request.get('/base-materials/usage-stats', params)
}

// 获取材料价格趋势
export function getMaterialPriceTrend(materialId, params) {
  return request.get(`/base-materials/${materialId}/price-trend`, params)
}

// 比较材料价格
export function compareMaterialPrices(materialIds, params) {
  return request.post('/base-materials/compare-prices', {
    material_ids: materialIds,
    ...params
  })
}

// 获取材料推荐
export function getMaterialRecommendations(params) {
  return request.get('/base-materials/recommendations', params)
}

// 标记材料为常用
export function markMaterialAsFavorite(materialId) {
  return request.post(`/base-materials/${materialId}/favorite`)
}

export function searchSimilarBaseMaterials(materialName, limit = 50) {
  return request.get('/base-materials/search-similar', {
    material_name: materialName,
    limit
  })
}

// 取消材料常用标记
export function unmarkMaterialAsFavorite(materialId) {
  return request.delete(`/base-materials/${materialId}/favorite`)
}

// 获取常用材料列表
export function getFavoriteMaterials(params) {
  return request.get('/base-materials/favorites', params)
}

// 获取最近使用的材料
export function getRecentMaterials(params) {
  return request.get('/base-materials/recent', params)
}

// 获取热门材料
export function getPopularMaterials(params) {
  return request.get('/base-materials/popular', params)
}

// 材料数据质量检查
export function checkMaterialDataQuality() {
  return request.get('/base-materials/data-quality-check')
}

// 修复材料数据质量问题
export function fixMaterialDataQuality(issues) {
  return request.post('/base-materials/fix-data-quality', { issues })
}

// 获取材料审核列表
export function getMaterialAuditList(params) {
  return request.get('/base-materials/audit-list', params)
}

// 审核材料
export function auditMaterial(materialId, auditData) {
  return request.post(`/base-materials/${materialId}/audit`, auditData)
}

// 批量审核材料
export function batchAuditMaterials(data) {
  return request.post('/base-materials/batch-audit', data)
}
