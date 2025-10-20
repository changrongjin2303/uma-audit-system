/**
 * 性能优化工具
 */

import { ref, onMounted, onBeforeUnmount } from 'vue'

/**
 * 防抖函数
 * @param {Function} func - 要防抖的函数
 * @param {Number} wait - 等待时间(ms)
 * @param {Boolean} immediate - 是否立即执行
 * @returns {Function} 防抖后的函数
 */
export const debounce = (func, wait, immediate = false) => {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      timeout = null
      if (!immediate) func(...args)
    }
    const callNow = immediate && !timeout
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
    if (callNow) func(...args)
  }
}

/**
 * 节流函数
 * @param {Function} func - 要节流的函数
 * @param {Number} limit - 限制时间(ms)
 * @returns {Function} 节流后的函数
 */
export const throttle = (func, limit) => {
  let inThrottle
  return function executedFunction(...args) {
    if (!inThrottle) {
      func.apply(this, args)
      inThrottle = true
      setTimeout(() => inThrottle = false, limit)
    }
  }
}

/**
 * 延迟执行函数
 * @param {Number} ms - 延迟时间(ms)
 * @returns {Promise} Promise对象
 */
export const sleep = (ms) => {
  return new Promise(resolve => setTimeout(resolve, ms))
}

/**
 * 性能监控Hook
 * @returns {Object} 性能数据对象
 */
export const usePerformance = () => {
  const performanceData = ref({
    loadTime: 0,
    renderTime: 0,
    memoryUsage: 0,
    networkStatus: 'online',
    connectionType: 'unknown'
  })

  const startTime = performance.now()

  // 监控页面加载性能
  const measureLoadTime = () => {
    if (window.performance && window.performance.timing) {
      const timing = window.performance.timing
      performanceData.value.loadTime = timing.loadEventEnd - timing.navigationStart
    }
  }

  // 监控渲染性能
  const measureRenderTime = () => {
    const endTime = performance.now()
    performanceData.value.renderTime = endTime - startTime
  }

  // 监控内存使用
  const measureMemoryUsage = () => {
    if (window.performance && window.performance.memory) {
      performanceData.value.memoryUsage = window.performance.memory.usedJSHeapSize
    }
  }

  // 监控网络状态
  const updateNetworkStatus = () => {
    performanceData.value.networkStatus = navigator.onLine ? 'online' : 'offline'
    
    if ('connection' in navigator) {
      performanceData.value.connectionType = navigator.connection.effectiveType || 'unknown'
    }
  }

  onMounted(() => {
    measureLoadTime()
    measureRenderTime()
    measureMemoryUsage()
    updateNetworkStatus()

    // 监听网络状态变化
    window.addEventListener('online', updateNetworkStatus)
    window.addEventListener('offline', updateNetworkStatus)

    // 定期更新内存使用情况
    const memoryTimer = setInterval(measureMemoryUsage, 5000)
    
    onBeforeUnmount(() => {
      window.removeEventListener('online', updateNetworkStatus)
      window.removeEventListener('offline', updateNetworkStatus)
      clearInterval(memoryTimer)
    })
  })

  return performanceData
}

/**
 * 图片懒加载Hook
 * @param {Object} options - 配置选项
 * @returns {Object} 懒加载对象
 */
export const useLazyLoad = (options = {}) => {
  const {
    root = null,
    rootMargin = '0px',
    threshold = 0.1,
    placeholder = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMSIgaGVpZ2h0PSIxIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9IiNmNWY3ZmEiLz48L3N2Zz4='
  } = options

  const observer = ref(null)
  const loadedImages = new Set()

  const createObserver = () => {
    if (!window.IntersectionObserver) {
      return null
    }

    return new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const img = entry.target
            const src = img.dataset.src
            
            if (src && !loadedImages.has(src)) {
              loadImage(img, src)
              observer.value?.unobserve(img)
            }
          }
        })
      },
      { root, rootMargin, threshold }
    )
  }

  const loadImage = (img, src) => {
    const image = new Image()
    
    image.onload = () => {
      img.src = src
      img.classList.add('loaded')
      loadedImages.add(src)
    }
    
    image.onerror = () => {
      img.classList.add('error')
    }
    
    image.src = src
  }

  const observe = (element) => {
    if (!observer.value) {
      observer.value = createObserver()
    }
    
    if (observer.value && element) {
      // 设置占位图
      if (!element.src) {
        element.src = placeholder
      }
      
      observer.value.observe(element)
    }
  }

  const unobserve = (element) => {
    if (observer.value && element) {
      observer.value.unobserve(element)
    }
  }

  const disconnect = () => {
    if (observer.value) {
      observer.value.disconnect()
      observer.value = null
    }
  }

  onBeforeUnmount(() => {
    disconnect()
  })

  return {
    observe,
    unobserve,
    disconnect
  }
}

/**
 * 代码分割加载Hook
 * @param {Function} importFunc - 动态import函数
 * @returns {Object} 异步组件对象
 */
export const useAsyncComponent = (importFunc) => {
  const component = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const loadComponent = async () => {
    loading.value = true
    error.value = null

    try {
      const module = await importFunc()
      component.value = module.default || module
    } catch (err) {
      error.value = err
      console.error('组件加载失败:', err)
    } finally {
      loading.value = false
    }
  }

  onMounted(() => {
    loadComponent()
  })

  return {
    component,
    loading,
    error,
    reload: loadComponent
  }
}

/**
 * 内存泄漏检测Hook
 * @returns {Object} 内存监控对象
 */
export const useMemoryLeak = () => {
  const eventListeners = new Map()
  const timers = new Set()
  const observers = new Set()

  // 跟踪事件监听器
  const addEventListener = (element, event, handler, options) => {
    element.addEventListener(event, handler, options)
    
    const key = `${element.tagName}-${event}-${handler.name}`
    eventListeners.set(key, { element, event, handler, options })
  }

  // 跟踪定时器
  const setTimeout = (callback, delay) => {
    const id = window.setTimeout(callback, delay)
    timers.add(id)
    return id
  }

  const setInterval = (callback, delay) => {
    const id = window.setInterval(callback, delay)
    timers.add(id)
    return id
  }

  // 跟踪观察者
  const addObserver = (observer) => {
    observers.add(observer)
  }

  // 清理所有资源
  const cleanup = () => {
    // 清理事件监听器
    eventListeners.forEach(({ element, event, handler, options }) => {
      element.removeEventListener(event, handler, options)
    })
    eventListeners.clear()

    // 清理定时器
    timers.forEach(id => {
      clearTimeout(id)
      clearInterval(id)
    })
    timers.clear()

    // 清理观察者
    observers.forEach(observer => {
      if (observer.disconnect) {
        observer.disconnect()
      }
    })
    observers.clear()
  }

  onBeforeUnmount(() => {
    cleanup()
  })

  return {
    addEventListener,
    setTimeout,
    setInterval,
    addObserver,
    cleanup
  }
}

/**
 * 缓存管理工具
 */
export class CacheManager {
  constructor(maxSize = 100, ttl = 5 * 60 * 1000) { // 默认5分钟TTL
    this.cache = new Map()
    this.maxSize = maxSize
    this.ttl = ttl
  }

  set(key, value, customTtl) {
    // 如果缓存已满，删除最旧的项
    if (this.cache.size >= this.maxSize) {
      const firstKey = this.cache.keys().next().value
      this.cache.delete(firstKey)
    }

    const expiresAt = Date.now() + (customTtl || this.ttl)
    this.cache.set(key, { value, expiresAt })
  }

  get(key) {
    const item = this.cache.get(key)
    
    if (!item) return null

    if (Date.now() > item.expiresAt) {
      this.cache.delete(key)
      return null
    }

    return item.value
  }

  has(key) {
    const item = this.cache.get(key)
    
    if (!item) return false

    if (Date.now() > item.expiresAt) {
      this.cache.delete(key)
      return false
    }

    return true
  }

  delete(key) {
    return this.cache.delete(key)
  }

  clear() {
    this.cache.clear()
  }

  size() {
    return this.cache.size
  }

  // 清理过期项
  cleanup() {
    const now = Date.now()
    for (const [key, item] of this.cache.entries()) {
      if (now > item.expiresAt) {
        this.cache.delete(key)
      }
    }
  }
}

/**
 * 批量处理工具
 * @param {Function} processor - 处理函数
 * @param {Object} options - 配置选项
 * @returns {Function} 批量处理函数
 */
export const createBatchProcessor = (processor, options = {}) => {
  const {
    batchSize = 50,
    delay = 0,
    maxWait = 1000
  } = options

  let batch = []
  let timer = null
  let firstItemTime = null

  const processBatch = async () => {
    if (batch.length === 0) return

    const currentBatch = [...batch]
    batch = []
    firstItemTime = null
    
    if (timer) {
      clearTimeout(timer)
      timer = null
    }

    try {
      await processor(currentBatch)
    } catch (error) {
      console.error('批量处理失败:', error)
    }
  }

  const scheduleProcessing = () => {
    if (timer) return

    const elapsed = firstItemTime ? Date.now() - firstItemTime : 0
    const remainingWait = Math.max(0, maxWait - elapsed)
    const waitTime = Math.min(delay, remainingWait)

    timer = setTimeout(processBatch, waitTime)
  }

  return (item) => {
    if (batch.length === 0) {
      firstItemTime = Date.now()
    }

    batch.push(item)

    if (batch.length >= batchSize) {
      processBatch()
    } else {
      scheduleProcessing()
    }
  }
}

/**
 * 资源预加载工具
 */
export class ResourcePreloader {
  constructor() {
    this.preloaded = new Set()
  }

  preloadImage(src) {
    if (this.preloaded.has(src)) {
      return Promise.resolve()
    }

    return new Promise((resolve, reject) => {
      const img = new Image()
      img.onload = () => {
        this.preloaded.add(src)
        resolve()
      }
      img.onerror = reject
      img.src = src
    })
  }

  preloadImages(srcs) {
    return Promise.all(srcs.map(src => this.preloadImage(src)))
  }

  preloadScript(src) {
    if (this.preloaded.has(src)) {
      return Promise.resolve()
    }

    return new Promise((resolve, reject) => {
      const script = document.createElement('script')
      script.onload = () => {
        this.preloaded.add(src)
        resolve()
      }
      script.onerror = reject
      script.src = src
      document.head.appendChild(script)
    })
  }

  preloadCSS(href) {
    if (this.preloaded.has(href)) {
      return Promise.resolve()
    }

    return new Promise((resolve, reject) => {
      const link = document.createElement('link')
      link.rel = 'stylesheet'
      link.onload = () => {
        this.preloaded.add(href)
        resolve()
      }
      link.onerror = reject
      link.href = href
      document.head.appendChild(link)
    })
  }

  isPreloaded(src) {
    return this.preloaded.has(src)
  }
}

// 创建全局实例
export const globalCache = new CacheManager()
export const resourcePreloader = new ResourcePreloader()

export default {
  debounce,
  throttle,
  sleep,
  usePerformance,
  useLazyLoad,
  useAsyncComponent,
  useMemoryLeak,
  CacheManager,
  createBatchProcessor,
  ResourcePreloader,
  globalCache,
  resourcePreloader
}