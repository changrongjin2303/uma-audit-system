/**
 * API相关工具函数
 */

import { ElMessage, ElNotification } from 'element-plus'
import { RISK_LEVELS, PROJECT_STATUS, ANALYSIS_STATUS } from '@/config'

/**
 * 处理API响应数据
 * @param {Object} response - API响应对象
 * @param {Object} options - 处理选项
 * @returns {Object} 处理后的数据
 */
export function handleApiResponse(response, options = {}) {
  const { showMessage = false, defaultData = null } = options

  if (!response) {
    console.warn('API response is null or undefined')
    return defaultData
  }

  const { code, data, message } = response

  // 成功响应
  if (code === 200 || code === 0) {
    if (showMessage && message) {
      ElMessage.success(message)
    }
    return data
  }

  // 错误响应
  if (message) {
    ElMessage.error(message)
  }

  return defaultData
}

/**
 * 格式化API错误信息
 * @param {Error} error - 错误对象
 * @returns {Object} 格式化后的错误信息
 */
export function formatApiError(error) {
  let errorInfo = {
    code: 'UNKNOWN_ERROR',
    message: '未知错误',
    details: null,
    timestamp: new Date().toISOString()
  }

  if (!error) {
    return errorInfo
  }

  // HTTP错误
  if (error.response) {
    const { status, data } = error.response
    errorInfo.code = `HTTP_${status}`
    errorInfo.message = data?.message || data?.detail || `HTTP ${status} 错误`
    errorInfo.details = data
  }
  // 网络错误
  else if (error.request) {
    errorInfo.code = 'NETWORK_ERROR'
    errorInfo.message = '网络连接失败'
    errorInfo.details = {
      timeout: error.code === 'ECONNABORTED',
      offline: !navigator.onLine
    }
  }
  // 其他错误
  else {
    errorInfo.code = 'CLIENT_ERROR'
    errorInfo.message = error.message || '客户端错误'
    errorInfo.details = {
      name: error.name,
      stack: error.stack
    }
  }

  return errorInfo
}

/**
 * 发送错误通知
 * @param {Object} errorInfo - 错误信息
 * @param {Object} options - 通知选项
 */
export function notifyError(errorInfo, options = {}) {
  const {
    title = '操作失败',
    duration = 4500,
    showDetails = false,
    position = 'top-right'
  } = options

  let message = errorInfo.message

  if (showDetails && errorInfo.details) {
    message += `\n详细信息: ${JSON.stringify(errorInfo.details, null, 2)}`
  }

  ElNotification.error({
    title,
    message,
    duration,
    position,
    dangerouslyUseHTMLString: false
  })
}

/**
 * 构建查询参数
 * @param {Object} params - 参数对象
 * @param {Object} options - 构建选项
 * @returns {Object} 处理后的参数
 */
export function buildQueryParams(params = {}, options = {}) {
  const {
    removeEmpty = true,
    removeNull = true,
    removeUndefined = true,
    trimStrings = true,
    encodeValues = false
  } = options

  const result = {}

  Object.keys(params).forEach(key => {
    let value = params[key]

    // 移除空值
    if (removeEmpty && value === '') return
    if (removeNull && value === null) return
    if (removeUndefined && value === undefined) return

    // 字符串处理
    if (typeof value === 'string') {
      if (trimStrings) {
        value = value.trim()
      }
      if (encodeValues) {
        value = encodeURIComponent(value)
      }
    }

    // 数组处理
    if (Array.isArray(value)) {
      if (value.length === 0 && removeEmpty) return
      value = value.filter(item => item !== null && item !== undefined && item !== '')
      if (value.length === 0 && removeEmpty) return
    }

    result[key] = value
  })

  return result
}

/**
 * 处理分页参数
 * @param {Object} pagination - 分页对象
 * @returns {Object} 分页参数
 */
export function buildPaginationParams(pagination = {}) {
  const { page = 1, size = 20, total = 0 } = pagination

  return {
    page: Math.max(1, page),
    size: Math.min(Math.max(1, size), 100), // 限制每页最大100条
    offset: (Math.max(1, page) - 1) * Math.max(1, size)
  }
}

/**
 * 处理排序参数
 * @param {Object} sort - 排序对象
 * @returns {Object} 排序参数
 */
export function buildSortParams(sort = {}) {
  const { field, order } = sort

  if (!field) return {}

  return {
    sort_by: field,
    sort_order: order === 'descending' ? 'desc' : 'asc'
  }
}

/**
 * 合并API参数
 * @param {Object} baseParams - 基础参数
 * @param {Object} extraParams - 额外参数
 * @returns {Object} 合并后的参数
 */
export function mergeApiParams(baseParams = {}, extraParams = {}) {
  return {
    ...baseParams,
    ...extraParams
  }
}

/**
 * 验证必需参数
 * @param {Object} params - 参数对象
 * @param {Array} required - 必需的参数名数组
 * @throws {Error} 参数验证失败时抛出错误
 */
export function validateRequiredParams(params, required) {
  const missing = required.filter(key => {
    const value = params[key]
    return value === undefined || value === null || value === ''
  })

  if (missing.length > 0) {
    throw new Error(`缺少必需参数: ${missing.join(', ')}`)
  }
}

/**
 * 转换API响应数据为前端格式
 * @param {Object} apiData - API返回的数据
 * @param {Object} mapping - 字段映射配置
 * @returns {Object} 转换后的数据
 */
export function transformApiData(apiData, mapping = {}) {
  if (!apiData || typeof apiData !== 'object') {
    return apiData
  }

  const result = {}

  Object.keys(apiData).forEach(key => {
    const mappedKey = mapping[key] || key
    let value = apiData[key]

    // 递归处理嵌套对象
    if (value && typeof value === 'object' && !Array.isArray(value) && !(value instanceof Date)) {
      value = transformApiData(value, mapping)
    }
    // 处理数组
    else if (Array.isArray(value)) {
      value = value.map(item => {
        if (typeof item === 'object' && item !== null) {
          return transformApiData(item, mapping)
        }
        return item
      })
    }

    result[mappedKey] = value
  })

  return result
}

/**
 * 生成API缓存键
 * @param {String} endpoint - 接口端点
 * @param {Object} params - 请求参数
 * @returns {String} 缓存键
 */
export function generateCacheKey(endpoint, params = {}) {
  const paramStr = JSON.stringify(buildQueryParams(params), Object.keys(params).sort())
  return `api_${endpoint}_${btoa(paramStr).replace(/[/+=]/g, '')}`
}

/**
 * 批量处理API请求
 * @param {Array} requests - 请求数组
 * @param {Object} options - 批处理选项
 * @returns {Promise} 批处理结果
 */
export async function batchApiRequests(requests, options = {}) {
  const {
    concurrency = 5,
    retries = 3,
    retryDelay = 1000,
    onProgress = null,
    failFast = false
  } = options

  const results = []
  const errors = []
  let completed = 0

  // 执行单个请求
  const executeRequest = async (request, index) => {
    let attempts = 0
    
    while (attempts < retries) {
      try {
        const result = await request()
        results[index] = { status: 'fulfilled', value: result }
        completed++
        
        if (onProgress) {
          onProgress(completed, requests.length)
        }
        
        return result
      } catch (error) {
        attempts++
        
        if (attempts >= retries) {
          const errorInfo = formatApiError(error)
          errors.push({ index, error: errorInfo })
          results[index] = { status: 'rejected', reason: errorInfo }
          
          if (failFast) {
            throw error
          }
        } else {
          // 等待后重试
          await new Promise(resolve => setTimeout(resolve, retryDelay * attempts))
        }
      }
    }
  }

  // 分批执行
  const batches = []
  for (let i = 0; i < requests.length; i += concurrency) {
    const batch = requests.slice(i, i + concurrency)
    batches.push(batch.map((request, batchIndex) => 
      executeRequest(request, i + batchIndex)
    ))
  }

  // 执行所有批次
  for (const batch of batches) {
    if (failFast) {
      await Promise.all(batch)
    } else {
      await Promise.allSettled(batch)
    }
  }

  return {
    results,
    errors,
    success: errors.length === 0,
    successCount: results.filter(r => r.status === 'fulfilled').length,
    errorCount: errors.length
  }
}

/**
 * API请求重试装饰器
 * @param {Function} apiFunction - API函数
 * @param {Object} options - 重试选项
 * @returns {Function} 装饰后的函数
 */
export function withRetry(apiFunction, options = {}) {
  const {
    maxRetries = 3,
    baseDelay = 1000,
    maxDelay = 10000,
    backoffFactor = 2,
    retryCondition = (error) => error.response?.status >= 500
  } = options

  return async (...args) => {
    let lastError
    
    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        return await apiFunction(...args)
      } catch (error) {
        lastError = error
        
        // 最后一次尝试或不符合重试条件
        if (attempt === maxRetries || !retryCondition(error)) {
          throw error
        }
        
        // 计算延迟时间
        const delay = Math.min(
          baseDelay * Math.pow(backoffFactor, attempt),
          maxDelay
        )
        
        console.log(`API请求失败，${delay}ms后重试 (${attempt + 1}/${maxRetries})`)
        
        await new Promise(resolve => setTimeout(resolve, delay))
      }
    }
    
    throw lastError
  }
}

/**
 * 获取状态文本和样式
 * @param {String} status - 状态值
 * @param {String} type - 状态类型
 * @returns {Object} 状态信息
 */
export function getStatusInfo(status, type = 'project') {
  let statusConfig = {}

  switch (type) {
    case 'project':
      statusConfig = PROJECT_STATUS
      break
    case 'analysis':
      statusConfig = ANALYSIS_STATUS
      break
    case 'risk':
      statusConfig = RISK_LEVELS
      break
    default:
      return { label: status, color: 'default', icon: 'QuestionFilled' }
  }

  return statusConfig[status] || { label: status, color: 'default', icon: 'QuestionFilled' }
}

/**
 * 数据导出工具
 * @param {Array} data - 要导出的数据
 * @param {Object} options - 导出选项
 */
export function exportData(data, options = {}) {
  const {
    filename = 'export',
    format = 'json',
    headers = null
  } = options

  let content = ''
  let mimeType = 'application/json'
  let extension = '.json'

  switch (format.toLowerCase()) {
    case 'json':
      content = JSON.stringify(data, null, 2)
      break
    case 'csv':
      if (Array.isArray(data) && data.length > 0) {
        const csvHeaders = headers || Object.keys(data[0])
        const csvRows = data.map(row => 
          csvHeaders.map(header => `"${String(row[header] || '').replace(/"/g, '""')}"`).join(',')
        )
        content = [csvHeaders.join(','), ...csvRows].join('\n')
        mimeType = 'text/csv'
        extension = '.csv'
      }
      break
    case 'txt':
      content = Array.isArray(data) ? data.join('\n') : String(data)
      mimeType = 'text/plain'
      extension = '.txt'
      break
  }

  // 创建下载
  const blob = new Blob([content], { type: mimeType })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${filename}${extension}`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}

/**
 * 数据导入工具
 * @param {File} file - 要导入的文件
 * @param {Object} options - 导入选项
 * @returns {Promise} 导入结果
 */
export function importData(file, options = {}) {
  const { format = 'auto', encoding = 'utf-8' } = options

  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    
    reader.onload = (event) => {
      try {
        const content = event.target.result
        let data

        // 自动检测格式
        let fileFormat = format
        if (format === 'auto') {
          const extension = file.name.toLowerCase().split('.').pop()
          fileFormat = extension === 'csv' ? 'csv' : 'json'
        }

        switch (fileFormat) {
          case 'json':
            data = JSON.parse(content)
            break
          case 'csv':
            data = parseCSV(content)
            break
          default:
            data = content
        }

        resolve({
          data,
          filename: file.name,
          size: file.size,
          type: file.type,
          format: fileFormat
        })
      } catch (error) {
        reject(new Error(`文件解析失败: ${error.message}`))
      }
    }

    reader.onerror = () => {
      reject(new Error('文件读取失败'))
    }

    reader.readAsText(file, encoding)
  })
}

/**
 * 简单CSV解析器
 * @param {String} csvContent - CSV内容
 * @returns {Array} 解析后的数据
 */
function parseCSV(csvContent) {
  const lines = csvContent.split('\n').filter(line => line.trim())
  if (lines.length === 0) return []

  const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''))
  const data = []

  for (let i = 1; i < lines.length; i++) {
    const values = lines[i].split(',').map(v => v.trim().replace(/"/g, ''))
    const row = {}
    
    headers.forEach((header, index) => {
      row[header] = values[index] || ''
    })
    
    data.push(row)
  }

  return data
}

export default {
  handleApiResponse,
  formatApiError,
  notifyError,
  buildQueryParams,
  buildPaginationParams,
  buildSortParams,
  mergeApiParams,
  validateRequiredParams,
  transformApiData,
  generateCacheKey,
  batchApiRequests,
  withRetry,
  getStatusInfo,
  exportData,
  importData
}