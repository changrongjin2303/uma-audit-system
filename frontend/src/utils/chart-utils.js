/**
 * 图表工具函数
 */

import * as echarts from 'echarts'

/**
 * 默认主题配置
 */
export const DEFAULT_THEME = {
  color: [
    '#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399',
    '#53A8FF', '#85CE61', '#EEBE77', '#F78989', '#A6A9AD'
  ],
  backgroundColor: '#fff',
  textStyle: {
    color: '#303133',
    fontSize: 12,
    fontFamily: '"Helvetica Neue", Helvetica, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "微软雅黑", Arial, sans-serif'
  },
  title: {
    textStyle: {
      fontSize: 16,
      fontWeight: 'bold',
      color: '#303133'
    }
  },
  legend: {
    textStyle: {
      color: '#606266',
      fontSize: 12
    }
  },
  tooltip: {
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    textStyle: {
      color: '#fff',
      fontSize: 12
    },
    borderWidth: 0,
    borderRadius: 4
  }
}

/**
 * 注册默认主题
 */
export const registerDefaultTheme = () => {
  echarts.registerTheme('default', DEFAULT_THEME)
}

/**
 * 响应式配置
 */
export const RESPONSIVE_CONFIG = {
  mobile: {
    grid: {
      left: '5%',
      right: '5%',
      top: '15%',
      bottom: '15%',
      containLabel: true
    },
    legend: {
      orient: 'horizontal',
      bottom: '5%'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    }
  },
  desktop: {
    grid: {
      left: '3%',
      right: '4%',
      top: '10%',
      bottom: '8%',
      containLabel: true
    },
    legend: {
      top: '5%'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    }
  }
}

/**
 * 获取响应式配置
 * @param {String} deviceType - 设备类型 'mobile' | 'desktop'
 * @returns {Object} 响应式配置
 */
export const getResponsiveConfig = (deviceType = 'desktop') => {
  return RESPONSIVE_CONFIG[deviceType] || RESPONSIVE_CONFIG.desktop
}

/**
 * 检测设备类型
 * @returns {String} 设备类型
 */
export const detectDeviceType = () => {
  return window.innerWidth <= 768 ? 'mobile' : 'desktop'
}

/**
 * 格式化数字
 * @param {Number} value - 数值
 * @param {Object} options - 格式化选项
 * @returns {String} 格式化后的字符串
 */
export const formatNumber = (value, options = {}) => {
  const {
    decimals = 2,
    unit = '',
    prefix = '',
    suffix = '',
    separator = ','
  } = options

  if (typeof value !== 'number' || isNaN(value)) {
    return '0'
  }

  let formatted = value.toFixed(decimals)
  
  // 添加千分位分隔符
  if (separator) {
    formatted = formatted.replace(/\B(?=(\d{3})+(?!\d))/g, separator)
  }

  return `${prefix}${formatted}${unit}${suffix}`
}

/**
 * 格式化价格
 * @param {Number} price - 价格
 * @param {Object} options - 格式化选项
 * @returns {String} 格式化后的价格
 */
export const formatPrice = (price, options = {}) => {
  const { currency = '¥', decimals = 2 } = options
  return formatNumber(price, { prefix: currency, decimals })
}

/**
 * 格式化百分比
 * @param {Number} value - 数值 (0-1)
 * @param {Object} options - 格式化选项
 * @returns {String} 格式化后的百分比
 */
export const formatPercentage = (value, options = {}) => {
  const { decimals = 1 } = options
  return formatNumber(value * 100, { suffix: '%', decimals })
}

/**
 * 生成渐变色
 * @param {String} startColor - 开始颜色
 * @param {String} endColor - 结束颜色
 * @param {String} direction - 渐变方向 'horizontal' | 'vertical'
 * @returns {Object} ECharts渐变配置
 */
export const createGradient = (startColor, endColor, direction = 'vertical') => {
  const isVertical = direction === 'vertical'
  
  return {
    type: 'linear',
    x: 0,
    y: isVertical ? 0 : 1,
    x2: isVertical ? 0 : 1,
    y2: isVertical ? 1 : 0,
    colorStops: [
      { offset: 0, color: startColor },
      { offset: 1, color: endColor }
    ]
  }
}

/**
 * 获取系列颜色
 * @param {Number} index - 系列索引
 * @returns {String} 颜色值
 */
export const getSeriesColor = (index) => {
  const colors = DEFAULT_THEME.color
  return colors[index % colors.length]
}

/**
 * 生成仪表盘配置
 * @param {Number} value - 当前值
 * @param {Object} options - 配置选项
 * @returns {Object} 仪表盘配置
 */
export const createGaugeOption = (value, options = {}) => {
  const {
    min = 0,
    max = 100,
    title = '仪表盘',
    unit = '',
    splitNumber = 10,
    colors = [
      [0.2, '#67C23A'],
      [0.8, '#E6A23C'],
      [1, '#F56C6C']
    ]
  } = options

  return {
    title: {
      text: title,
      left: 'center',
      top: '10%',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    series: [{
      name: title,
      type: 'gauge',
      min: min,
      max: max,
      splitNumber: splitNumber,
      radius: '80%',
      axisLine: {
        lineStyle: {
          width: 30,
          color: colors
        }
      },
      pointer: {
        itemStyle: {
          color: 'auto'
        }
      },
      axisTick: {
        distance: -30,
        length: 8,
        lineStyle: {
          color: '#fff',
          width: 2
        }
      },
      splitLine: {
        distance: -30,
        length: 30,
        lineStyle: {
          color: '#fff',
          width: 4
        }
      },
      axisLabel: {
        color: 'auto',
        distance: 40,
        fontSize: 12
      },
      detail: {
        valueAnimation: true,
        formatter: `{value}${unit}`,
        color: 'auto',
        fontSize: 24,
        offsetCenter: [0, '70%']
      },
      data: [{
        value: value,
        name: title
      }]
    }]
  }
}

/**
 * 生成水球图配置
 * @param {Number} percentage - 百分比 (0-100)
 * @param {Object} options - 配置选项
 * @returns {Object} 水球图配置
 */
export const createLiquidFillOption = (percentage, options = {}) => {
  const {
    title = '完成度',
    color = ['#409EFF', '#67C23A'],
    backgroundColor = '#E1E9FE'
  } = options

  return {
    title: {
      text: title,
      left: 'center',
      top: '10%'
    },
    series: [{
      type: 'liquidFill',
      data: [percentage / 100],
      color: color,
      backgroundStyle: {
        color: backgroundColor
      },
      label: {
        fontSize: 24,
        fontWeight: 'bold',
        formatter: `${percentage}%`
      }
    }]
  }
}

/**
 * 获取图表默认配置
 * @param {String} type - 图表类型
 * @returns {Object} 默认配置
 */
export const getDefaultOption = (type) => {
  const baseConfig = {
    animation: true,
    animationDuration: 1000,
    animationEasing: 'cubicInOut'
  }

  const configs = {
    bar: {
      ...baseConfig,
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' }
      },
      grid: getResponsiveConfig(detectDeviceType()).grid
    },
    line: {
      ...baseConfig,
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'cross' }
      },
      grid: getResponsiveConfig(detectDeviceType()).grid
    },
    pie: {
      ...baseConfig,
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'vertical',
        left: 'left'
      }
    },
    scatter: {
      ...baseConfig,
      tooltip: {
        trigger: 'item'
      },
      grid: getResponsiveConfig(detectDeviceType()).grid
    },
    radar: {
      ...baseConfig,
      tooltip: {
        trigger: 'item'
      }
    }
  }

  return configs[type] || baseConfig
}

/**
 * 合并图表配置
 * @param {Object} baseOption - 基础配置
 * @param {Object} customOption - 自定义配置
 * @returns {Object} 合并后的配置
 */
export const mergeOption = (baseOption, customOption) => {
  return echarts.util.merge(baseOption, customOption, true)
}

/**
 * 图表自适应处理
 * @param {Object} chartInstance - 图表实例
 * @param {Number} delay - 延迟时间
 */
export const handleResize = (chartInstance, delay = 300) => {
  if (!chartInstance) return

  let resizeTimer = null
  
  const resize = () => {
    if (resizeTimer) {
      clearTimeout(resizeTimer)
    }
    
    resizeTimer = setTimeout(() => {
      if (chartInstance && !chartInstance.isDisposed()) {
        chartInstance.resize()
      }
    }, delay)
  }

  window.addEventListener('resize', resize)
  
  return () => {
    window.removeEventListener('resize', resize)
    if (resizeTimer) {
      clearTimeout(resizeTimer)
    }
  }
}

/**
 * 导出图表为图片
 * @param {Object} chartInstance - 图表实例
 * @param {Object} options - 导出选项
 * @returns {String} 图片base64数据
 */
export const exportChartAsImage = (chartInstance, options = {}) => {
  const {
    type = 'png',
    pixelRatio = 1,
    backgroundColor = '#fff'
  } = options

  if (!chartInstance) return null

  return chartInstance.getDataURL({
    type: type,
    pixelRatio: pixelRatio,
    backgroundColor: backgroundColor
  })
}

/**
 * 下载图表图片
 * @param {Object} chartInstance - 图表实例
 * @param {String} filename - 文件名
 * @param {Object} options - 导出选项
 */
export const downloadChart = (chartInstance, filename = 'chart', options = {}) => {
  const dataURL = exportChartAsImage(chartInstance, options)
  
  if (!dataURL) return

  const link = document.createElement('a')
  link.download = `${filename}.${options.type || 'png'}`
  link.href = dataURL
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

/**
 * 颜色工具
 */
export const colorUtils = {
  /**
   * 十六进制转RGB
   */
  hexToRgb: (hex) => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    } : null
  },

  /**
   * RGB转十六进制
   */
  rgbToHex: (r, g, b) => {
    return `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)}`
  },

  /**
   * 调整颜色透明度
   */
  setOpacity: (color, opacity) => {
    const rgb = colorUtils.hexToRgb(color)
    return rgb ? `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, ${opacity})` : color
  }
}

/**
 * 数据处理工具
 */
export const dataUtils = {
  /**
   * 数据分组
   */
  groupBy: (array, key) => {
    return array.reduce((result, item) => {
      const group = item[key]
      if (!result[group]) {
        result[group] = []
      }
      result[group].push(item)
      return result
    }, {})
  },

  /**
   * 数据排序
   */
  sortBy: (array, key, order = 'asc') => {
    return [...array].sort((a, b) => {
      const aVal = a[key]
      const bVal = b[key]
      
      if (order === 'desc') {
        return bVal > aVal ? 1 : bVal < aVal ? -1 : 0
      } else {
        return aVal > bVal ? 1 : aVal < bVal ? -1 : 0
      }
    })
  },

  /**
   * 数据筛选
   */
  filterBy: (array, filters) => {
    return array.filter(item => {
      return Object.keys(filters).every(key => {
        const filterValue = filters[key]
        const itemValue = item[key]
        
        if (Array.isArray(filterValue)) {
          return filterValue.includes(itemValue)
        } else {
          return itemValue === filterValue
        }
      })
    })
  },

  /**
   * 数据聚合
   */
  aggregate: (array, key, operation = 'sum') => {
    const values = array.map(item => item[key]).filter(val => typeof val === 'number')
    
    switch (operation) {
      case 'sum':
        return values.reduce((sum, val) => sum + val, 0)
      case 'avg':
        return values.length > 0 ? values.reduce((sum, val) => sum + val, 0) / values.length : 0
      case 'max':
        return Math.max(...values)
      case 'min':
        return Math.min(...values)
      case 'count':
        return values.length
      default:
        return 0
    }
  }
}

export default {
  DEFAULT_THEME,
  RESPONSIVE_CONFIG,
  registerDefaultTheme,
  getResponsiveConfig,
  detectDeviceType,
  formatNumber,
  formatPrice,
  formatPercentage,
  createGradient,
  getSeriesColor,
  createGaugeOption,
  createLiquidFillOption,
  getDefaultOption,
  mergeOption,
  handleResize,
  exportChartAsImage,
  downloadChart,
  colorUtils,
  dataUtils
}