import { request } from '@/utils/request'
import { mockAPI, isMockMode } from './mock'

// API调用辅助函数 - 自动降级到Mock
async function apiCall(apiFunc, mockFunc, ...args) {
  if (isMockMode()) {
    console.log('🎭 使用Mock API数据')
    return mockFunc(...args)
  }
  
  try {
    return await apiFunc(...args)
  } catch (error) {
    // 如果API调用失败，自动启用Mock模式
    if (error.code === 'ECONNABORTED' || error.message.includes('timeout') || error.message.includes('Network Error')) {
      console.warn('⚠️ 后端API不可用，自动切换到Mock模式')
      localStorage.setItem('useMockAPI', 'true')
      return mockFunc(...args)
    }
    throw error
  }
}

// 获取项目列表
export function getProjectList(params) {
  return apiCall(
    () => request.get('/projects/', params),
    () => mockAPI.getProjects(params),
    params
  )
}

// 获取项目列表（别名，兼容不同页面的调用）
export const getProjectsList = getProjectList

// 获取项目详情
export function getProject(id) {
  return request.get(`/projects/${id}`)
}

// 创建项目
export function createProject(data) {
  return apiCall(
    () => request.post('/projects/', data),
    (data) => mockAPI.createProject(data),
    data
  )
}

// 更新项目
export function updateProject(id, data) {
  return request.put(`/projects/${id}`, data)
}

// 删除项目
export function deleteProject(id) {
  return request.delete(`/projects/${id}`)
}

// 上传Excel文件
export function uploadExcel(projectId, file, onUploadProgress) {
  const formData = new FormData()
  formData.append('file', file)
  
  return request.post(`/projects/${projectId}/upload-excel`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    onUploadProgress
  })
}

// 导入材料数据
export function importMaterials(projectId, data) {
  return request.post(`/projects/${projectId}/import-materials`, data)
}

// 获取项目材料列表
export function getProjectMaterials(projectId, params = {}, config = {}) {
  return request.get(`/projects/${projectId}/materials`, params, config)
}

// 获取单个项目材料详情
export function getProjectMaterial(projectId, materialId) {
  return request.get(`/projects/${projectId}/materials/${materialId}`)
}

// 获取项目统计信息
export function getProjectStats(projectId, config = {}) {
  return request.get(`/projects/${projectId}/stats`, {}, config)
}

// 批量删除项目
export function batchDeleteProjects(ids) {
  return request.post('/projects/batch-delete', { ids })
}

// 复制项目
export function duplicateProject(id, data) {
  return request.post(`/projects/${id}/duplicate`, data)
}

// 导出项目数据
export function exportProject(id, format = 'excel') {
  return request.download(`/projects/${id}/export`, { format })
}

// 删除项目材料
export function deleteProjectMaterial(projectId, materialId) {
  return request.delete(`/projects/${projectId}/materials/${materialId}`)
}

// 解析项目材料Excel文件结构
export function parseProjectMaterialExcel(projectId, file, options = {}) {
  const formData = new FormData()
  formData.append('file', file)
  
  if (options.sheet_name) {
    formData.append('sheet_name', options.sheet_name)
  }
  
  return request.post(`/projects/${projectId}/parse-material-excel`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 获取项目材料预览数据
export function getProjectMaterialPreviewData(projectId, file, options = {}) {
  const formData = new FormData()
  formData.append('file', file)
  
  if (options.sheet_name) {
    formData.append('sheet_name', options.sheet_name)
  }
  if (options.max_rows) {
    formData.append('max_rows', options.max_rows)
  }
  
  return request.post(`/projects/${projectId}/get-preview-data`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 直接添加项目材料数据
export function addProjectMaterials(projectId, materials) {
  return request.post(`/projects/${projectId}/add-materials`, materials)
}

// 取消项目材料匹配
export function cancelProjectMaterialMatch(projectId, materialId) {
  return request.post(`/projects/${projectId}/materials/${materialId}/cancel-match`)
}

// 更新项目材料信息
export function updateProjectMaterial(projectId, materialId, data) {
  return request.put(`/projects/${projectId}/materials/${materialId}`, data)
}

// 批量删除项目材料
export function batchDeleteProjectMaterials(projectId, materialIds) {
  return request.post(`/projects/${projectId}/materials/batch-delete`, materialIds)
}