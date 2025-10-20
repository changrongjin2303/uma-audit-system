/**
 * 移动端适配工具
 */

import { ref, reactive, onMounted, onBeforeUnmount } from 'vue'

/**
 * 设备类型枚举
 */
export const DEVICE_TYPES = {
  MOBILE: 'mobile',
  TABLET: 'tablet', 
  DESKTOP: 'desktop'
}

/**
 * 断点配置
 */
export const BREAKPOINTS = {
  mobile: 768,
  tablet: 1024,
  desktop: 1440
}

/**
 * 检测设备类型
 * @returns {String} 设备类型
 */
export const detectDevice = () => {
  const width = window.innerWidth

  if (width <= BREAKPOINTS.mobile) {
    return DEVICE_TYPES.MOBILE
  } else if (width <= BREAKPOINTS.tablet) {
    return DEVICE_TYPES.TABLET
  } else {
    return DEVICE_TYPES.DESKTOP
  }
}

/**
 * 检测是否为移动设备
 * @returns {Boolean} 是否为移动设备
 */
export const isMobile = () => {
  return detectDevice() === DEVICE_TYPES.MOBILE
}

/**
 * 检测是否为平板设备
 * @returns {Boolean} 是否为平板设备
 */
export const isTablet = () => {
  return detectDevice() === DEVICE_TYPES.TABLET
}

/**
 * 检测是否为桌面设备
 * @returns {Boolean} 是否为桌面设备
 */
export const isDesktop = () => {
  return detectDevice() === DEVICE_TYPES.DESKTOP
}

/**
 * 检测是否支持触摸
 * @returns {Boolean} 是否支持触摸
 */
export const supportTouch = () => {
  return 'ontouchstart' in window || navigator.maxTouchPoints > 0
}

/**
 * 获取视口尺寸
 * @returns {Object} 视口尺寸信息
 */
export const getViewport = () => {
  return {
    width: window.innerWidth,
    height: window.innerHeight,
    availWidth: screen.availWidth,
    availHeight: screen.availHeight,
    devicePixelRatio: window.devicePixelRatio || 1
  }
}

/**
 * 响应式状态管理 Hook
 * @returns {Object} 响应式状态对象
 */
export const useResponsive = () => {
  const state = reactive({
    device: detectDevice(),
    viewport: getViewport(),
    isMobile: isMobile(),
    isTablet: isTablet(),
    isDesktop: isDesktop(),
    supportTouch: supportTouch()
  })

  const updateState = () => {
    state.device = detectDevice()
    state.viewport = getViewport()
    state.isMobile = isMobile()
    state.isTablet = isTablet()
    state.isDesktop = isDesktop()
  }

  let resizeTimer = null
  const handleResize = () => {
    clearTimeout(resizeTimer)
    resizeTimer = setTimeout(updateState, 100)
  }

  onMounted(() => {
    window.addEventListener('resize', handleResize)
    window.addEventListener('orientationchange', handleResize)
  })

  onBeforeUnmount(() => {
    window.removeEventListener('resize', handleResize)
    window.removeEventListener('orientationchange', handleResize)
    clearTimeout(resizeTimer)
  })

  return state
}

/**
 * 触摸手势处理 Hook
 * @param {Object} element - DOM元素引用
 * @returns {Object} 手势处理对象
 */
export const useTouch = (element) => {
  const touchData = reactive({
    startX: 0,
    startY: 0,
    endX: 0,
    endY: 0,
    deltaX: 0,
    deltaY: 0,
    direction: null,
    distance: 0,
    duration: 0,
    startTime: 0
  })

  const handlers = reactive({
    onSwipeLeft: null,
    onSwipeRight: null,
    onSwipeUp: null,
    onSwipeDown: null,
    onTap: null,
    onLongPress: null,
    onPinch: null
  })

  let longPressTimer = null

  const handleTouchStart = (event) => {
    if (!supportTouch()) return

    const touch = event.touches[0]
    touchData.startX = touch.clientX
    touchData.startY = touch.clientY
    touchData.startTime = Date.now()

    // 长按检测
    if (handlers.onLongPress) {
      longPressTimer = setTimeout(() => {
        handlers.onLongPress(touchData)
      }, 500)
    }
  }

  const handleTouchMove = (event) => {
    if (!supportTouch()) return
    
    clearTimeout(longPressTimer)
    
    const touch = event.touches[0]
    touchData.endX = touch.clientX
    touchData.endY = touch.clientY
    touchData.deltaX = touchData.endX - touchData.startX
    touchData.deltaY = touchData.endY - touchData.startY
  }

  const handleTouchEnd = () => {
    if (!supportTouch()) return

    clearTimeout(longPressTimer)
    
    touchData.duration = Date.now() - touchData.startTime
    touchData.distance = Math.sqrt(
      touchData.deltaX ** 2 + touchData.deltaY ** 2
    )

    // 判断手势类型
    if (touchData.distance < 10 && touchData.duration < 300) {
      // 点击
      touchData.direction = 'tap'
      if (handlers.onTap) {
        handlers.onTap(touchData)
      }
    } else if (touchData.distance > 50) {
      // 滑动
      const absX = Math.abs(touchData.deltaX)
      const absY = Math.abs(touchData.deltaY)

      if (absX > absY) {
        // 水平滑动
        if (touchData.deltaX > 0) {
          touchData.direction = 'right'
          if (handlers.onSwipeRight) {
            handlers.onSwipeRight(touchData)
          }
        } else {
          touchData.direction = 'left'
          if (handlers.onSwipeLeft) {
            handlers.onSwipeLeft(touchData)
          }
        }
      } else {
        // 垂直滑动
        if (touchData.deltaY > 0) {
          touchData.direction = 'down'
          if (handlers.onSwipeDown) {
            handlers.onSwipeDown(touchData)
          }
        } else {
          touchData.direction = 'up'
          if (handlers.onSwipeUp) {
            handlers.onSwipeUp(touchData)
          }
        }
      }
    }
  }

  onMounted(() => {
    if (element.value && supportTouch()) {
      element.value.addEventListener('touchstart', handleTouchStart, { passive: true })
      element.value.addEventListener('touchmove', handleTouchMove, { passive: true })
      element.value.addEventListener('touchend', handleTouchEnd, { passive: true })
    }
  })

  onBeforeUnmount(() => {
    if (element.value && supportTouch()) {
      element.value.removeEventListener('touchstart', handleTouchStart)
      element.value.removeEventListener('touchmove', handleTouchMove)
      element.value.removeEventListener('touchend', handleTouchEnd)
    }
    clearTimeout(longPressTimer)
  })

  return {
    touchData,
    handlers
  }
}

/**
 * 虚拟滚动 Hook
 * @param {Object} options - 配置选项
 * @returns {Object} 虚拟滚动对象
 */
export const useVirtualScroll = (options = {}) => {
  const {
    itemHeight = 50,
    containerHeight = 400,
    buffer = 5,
    data = ref([])
  } = options

  const state = reactive({
    scrollTop: 0,
    startIndex: 0,
    endIndex: 0,
    visibleData: [],
    totalHeight: 0,
    offsetY: 0
  })

  const visibleCount = Math.ceil(containerHeight / itemHeight)

  const updateVisibleData = () => {
    const total = data.value.length
    state.totalHeight = total * itemHeight

    state.startIndex = Math.max(0, Math.floor(state.scrollTop / itemHeight) - buffer)
    state.endIndex = Math.min(total, state.startIndex + visibleCount + buffer * 2)
    
    state.offsetY = state.startIndex * itemHeight
    state.visibleData = data.value.slice(state.startIndex, state.endIndex)
  }

  const handleScroll = (event) => {
    state.scrollTop = event.target.scrollTop
    updateVisibleData()
  }

  const scrollToIndex = (index) => {
    state.scrollTop = index * itemHeight
    updateVisibleData()
  }

  return {
    state,
    handleScroll,
    scrollToIndex,
    updateVisibleData
  }
}

/**
 * 懒加载 Hook
 * @param {Function} loadMore - 加载更多数据的函数
 * @param {Object} options - 配置选项
 * @returns {Object} 懒加载对象
 */
export const useInfiniteScroll = (loadMore, options = {}) => {
  const {
    distance = 100,
    disabled = false,
    immediate = true
  } = options

  const loading = ref(false)
  const finished = ref(false)
  const error = ref(null)

  const load = async () => {
    if (loading.value || finished.value || disabled) return

    loading.value = true
    error.value = null

    try {
      const result = await loadMore()
      if (!result || result.length === 0) {
        finished.value = true
      }
    } catch (err) {
      error.value = err
    } finally {
      loading.value = false
    }
  }

  const handleScroll = (event) => {
    if (loading.value || finished.value || disabled) return

    const { scrollTop, scrollHeight, clientHeight } = event.target
    
    if (scrollTop + clientHeight >= scrollHeight - distance) {
      load()
    }
  }

  onMounted(() => {
    if (immediate) {
      load()
    }
  })

  return {
    loading,
    finished,
    error,
    load,
    handleScroll
  }
}

/**
 * 移动端适配样式
 */
export const getMobileStyles = (device) => {
  const commonStyles = {
    '-webkit-tap-highlight-color': 'transparent',
    '-webkit-touch-callout': 'none',
    '-webkit-user-select': 'none',
    'user-select': 'none'
  }

  const deviceStyles = {
    [DEVICE_TYPES.MOBILE]: {
      ...commonStyles,
      fontSize: '14px',
      padding: '12px',
      minHeight: '44px', // iOS最小点击区域
      lineHeight: '1.4'
    },
    [DEVICE_TYPES.TABLET]: {
      ...commonStyles,
      fontSize: '16px',
      padding: '16px',
      minHeight: '48px',
      lineHeight: '1.5'
    },
    [DEVICE_TYPES.DESKTOP]: {
      fontSize: '14px',
      padding: '12px 16px',
      minHeight: '32px',
      lineHeight: '1.5'
    }
  }

  return deviceStyles[device] || deviceStyles[DEVICE_TYPES.DESKTOP]
}

/**
 * 获取移动端表格配置
 * @param {String} device - 设备类型
 * @returns {Object} 表格配置
 */
export const getMobileTableConfig = (device) => {
  if (device === DEVICE_TYPES.MOBILE) {
    return {
      size: 'small',
      showHeader: false,
      stripe: true,
      border: false,
      fit: true,
      maxHeight: 400,
      scrollbarAlwaysOn: false
    }
  } else if (device === DEVICE_TYPES.TABLET) {
    return {
      size: 'small',
      showHeader: true,
      stripe: true,
      border: true,
      fit: true,
      maxHeight: 500,
      scrollbarAlwaysOn: true
    }
  } else {
    return {
      size: 'default',
      showHeader: true,
      stripe: false,
      border: true,
      fit: false,
      maxHeight: null,
      scrollbarAlwaysOn: true
    }
  }
}

/**
 * 获取移动端分页配置
 * @param {String} device - 设备类型
 * @returns {Object} 分页配置
 */
export const getMobilePaginationConfig = (device) => {
  if (device === DEVICE_TYPES.MOBILE) {
    return {
      size: 'small',
      layout: 'prev, pager, next',
      pageSizes: [10, 20],
      pageSize: 10,
      background: true,
      hideOnSinglePage: true
    }
  } else if (device === DEVICE_TYPES.TABLET) {
    return {
      size: 'default',
      layout: 'total, prev, pager, next',
      pageSizes: [10, 20, 50],
      pageSize: 20,
      background: true,
      hideOnSinglePage: false
    }
  } else {
    return {
      size: 'default',
      layout: 'total, sizes, prev, pager, next, jumper',
      pageSizes: [10, 20, 50, 100],
      pageSize: 20,
      background: false,
      hideOnSinglePage: false
    }
  }
}

export default {
  DEVICE_TYPES,
  BREAKPOINTS,
  detectDevice,
  isMobile,
  isTablet,
  isDesktop,
  supportTouch,
  getViewport,
  useResponsive,
  useTouch,
  useVirtualScroll,
  useInfiniteScroll,
  getMobileStyles,
  getMobileTableConfig,
  getMobilePaginationConfig
}