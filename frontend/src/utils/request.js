import axios from 'axios'
import { ElMessage, ElMessageBox, ElLoading } from 'element-plus'
import { useUserStore } from '@/store/user'
import { getToken } from '@/utils/auth'
import router from '@/router'
import { API_CONFIG } from '@/config'

// 创建axios实例
const service = axios.create({
  baseURL: API_CONFIG.baseURL, // 使用配置文件中的baseURL
  timeout: API_CONFIG.timeout, // 使用配置文件中的timeout
  withCredentials: false // 跨域请求不携带cookie
})

// 全局loading实例
let loadingInstance = null
let loadingCount = 0

// 显示loading
const showLoading = (config) => {
  // 支持跳过loading的标记
  if (config.showLoading !== false && !config.__skipLoading) {
    loadingCount++
    if (loadingCount === 1) {
      loadingInstance = ElLoading.service({
        lock: true,
        text: config.loadingText || '加载中...',
        background: 'rgba(0, 0, 0, 0.7)'
      })
    }
  } else if (config.__skipLoading) {
    console.log('跳过全局loading，使用自定义进度显示')
  }
}

// 隐藏loading
const hideLoading = () => {
  loadingCount--
  if (loadingCount <= 0) {
    loadingCount = 0
    if (loadingInstance) {
      loadingInstance.close()
      loadingInstance = null
    }
  }
}

// 生成请求ID
const generateRequestId = () => {
  return 'req_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
}

// request拦截器
service.interceptors.request.use(
  config => {
    console.log('🚀 请求拦截器:', config.url, '配置:', { 
      __skipLoading: config.__skipLoading,
      showLoading: config.showLoading 
    })
    // 显示loading
    showLoading(config)

    // 在请求头中添加token
    const token = getToken()
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    
    // 添加请求ID用于追踪
    config.headers['X-Request-ID'] = generateRequestId()
    
    // 设置请求头
    if (!config.headers['Content-Type']) {
      config.headers['Content-Type'] = 'application/json'
    }

    // 处理文件上传
    if (config.headers['Content-Type'] === 'multipart/form-data') {
      // 让axios自动设置Content-Type，包含boundary
      delete config.headers['Content-Type']
    }

    // 处理特殊接口的超时设置
    if (config.specialTimeout) {
      config.timeout = API_CONFIG.specialTimeouts[config.specialTimeout] || config.timeout
      console.log(`🕐 设置特殊超时 ${config.specialTimeout}: ${config.timeout}ms`)
    }

    // 添加时间戳防止缓存
    if (config.method === 'get' && config.noCache !== false) {
      config.params = {
        ...config.params,
        _t: Date.now()
      }
    }
    
    console.log('Request:', {
      method: config.method?.toUpperCase(),
      url: config.url,
      data: config.data,
      params: config.params
    })
    
    return config
  },
  error => {
    hideLoading()
    console.error('请求错误:', error)
    ElMessage.error('请求配置错误')
    return Promise.reject(error)
  }
)

// 处理未授权
const handleUnauthorized = () => {
  const userStore = useUserStore()
  
  ElMessageBox.confirm(
    '登录状态已过期，请重新登录',
    '系统提示',
    {
      confirmButtonText: '重新登录',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    userStore.logout()
    router.push('/login')
  }).catch(() => {
    // 用户取消，不做任何操作
  })
}

// 处理表单验证错误
const handleValidationError = (data) => {
  if (data.errors && typeof data.errors === 'object') {
    const errorMessages = []
    Object.keys(data.errors).forEach(field => {
      const fieldErrors = data.errors[field]
      if (Array.isArray(fieldErrors)) {
        errorMessages.push(...fieldErrors)
      } else {
        errorMessages.push(fieldErrors)
      }
    })
    
    if (errorMessages.length > 0) {
      ElMessage.error(errorMessages.join('; '))
      return
    }
  }
  
  ElMessage.error(data.message || '表单验证失败')
}

// response拦截器
service.interceptors.response.use(
  response => {
    console.log('✅ 响应成功拦截器: 隐藏loading')
    hideLoading()
    
    const { data, config } = response
    
    console.log('Response:', {
      method: config.method?.toUpperCase(),
      url: config.url,
      status: response.status,
      data: data
    })

    // 处理文件下载
    if (config.responseType === 'blob') {
      return response
    }
    
    // FastAPI成功响应直接返回数据
    return data
  },
  error => {
    console.log('❌ 响应错误拦截器: 隐藏loading')
    hideLoading()
    
    console.error('Response Error:', error)

    // 网络错误处理
    if (!error.response) {
      if (error.code === 'ECONNABORTED') {
        ElMessage.error('请求超时，请检查网络连接')
      } else {
        ElMessage.error('网络错误，请检查网络连接')
      }
      return Promise.reject(error)
    }

    const { status, data } = error.response

    // HTTP状态码错误处理
    switch (status) {
      case 400:
        ElMessage.error(data?.message || '请求参数错误')
        break
      case 401:
        handleUnauthorized()
        break
      case 403:
        ElMessage.error('访问被禁止')
        break
      case 404:
        ElMessage.error('请求的接口不存在')
        break
      case 413:
        ElMessage.error('上传文件过大')
        break
      case 422:
        // 处理表单验证错误
        if (data.detail && Array.isArray(data.detail)) {
          const message = data.detail.map(item => item.msg).join(', ')
          ElMessage.error(message)
        } else {
          ElMessage.error(data.detail || data.message || '数据验证错误')
        }
        break
      case 500:
        ElMessage.error('服务器内部错误')
        break
      case 502:
        ElMessage.error('网关错误')
        break
      case 503:
        ElMessage.error('服务暂时不可用')
        break
      case 504:
        ElMessage.error('网关超时')
        break
      default:
        ElMessage.error(data?.message || `请求失败 (${status})`)
    }

    return Promise.reject(error)
  }
)

// 封装常用请求方法
export const request = {
  get(url, params = {}, config = {}) {
    return service.get(url, { params, ...config })
  },
  
  post(url, data = {}, config = {}) {
    return service.post(url, data, config)
  },
  
  put(url, data = {}, config = {}) {
    return service.put(url, data, config)
  },
  
  delete(url, config = {}) {
    return service.delete(url, config)
  },
  
  patch(url, data = {}, config = {}) {
    return service.patch(url, data, config)
  },
  
  upload(url, formData, config = {}) {
    return service.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      ...config
    })
  },
  
  download(url, params = {}, config = {}) {
    return service({
      method: 'get',
      url,
      params,
      responseType: 'blob',
      timeout: 300000, // 下载超时5分钟
      showLoading: true,
      loadingText: '正在下载...',
      ...config
    }).then(response => {
      // 处理文件下载
      const blob = response.data
      const contentDisposition = response.headers['content-disposition']
      let filename = 'download'
      
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1].replace(/['"]/g, '')
          // 解码文件名
          filename = decodeURIComponent(filename)
        }
      }
      
      // 创建下载链接
      const downloadUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(downloadUrl)
      
      return response
    })
  }
}

// 取消请求的工具
export const CancelToken = axios.CancelToken
export const isCancel = axios.isCancel

// 创建可取消的请求
export const createCancelableRequest = () => {
  const source = CancelToken.source()
  
  const request = (config) => {
    return service({
      ...config,
      cancelToken: source.token
    })
  }
  
  const cancel = (message) => {
    source.cancel(message)
  }
  
  return { request, cancel }
}

// 批量请求工具
export const batchRequest = (requests, config = {}) => {
  const { concurrency = 5, failFast = false } = config
  
  if (requests.length <= concurrency) {
    return failFast 
      ? Promise.all(requests)
      : Promise.allSettled(requests)
  }
  
  // 分批执行
  const results = []
  let currentIndex = 0
  
  const executeNext = () => {
    const batch = requests.slice(currentIndex, currentIndex + concurrency)
    currentIndex += concurrency
    
    const batchPromise = failFast
      ? Promise.all(batch)
      : Promise.allSettled(batch)
    
    return batchPromise.then(batchResults => {
      results.push(...batchResults)
      
      if (currentIndex < requests.length) {
        return executeNext()
      }
      
      return results
    })
  }
  
  return executeNext()
}

// 请求重试工具
export const retryRequest = (requestFn, options = {}) => {
  const { 
    maxRetries = 3, 
    delay = 1000, 
    backoff = 2, 
    retryCondition = (error) => error.response?.status >= 500 
  } = options
  
  let retryCount = 0
  
  const executeRequest = () => {
    return requestFn().catch(error => {
      if (retryCount >= maxRetries || !retryCondition(error)) {
        throw error
      }
      
      retryCount++
      const retryDelay = delay * Math.pow(backoff, retryCount - 1)
      
      console.log(`Request failed, retrying in ${retryDelay}ms (attempt ${retryCount}/${maxRetries})`)
      
      return new Promise(resolve => {
        setTimeout(resolve, retryDelay)
      }).then(executeRequest)
    })
  }
  
  return executeRequest()
}

export { service }
export default request