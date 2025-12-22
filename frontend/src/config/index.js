/**
 * 全局配置文件
 */

// 应用配置
export const APP_CONFIG = {
  title: import.meta.env.VITE_APP_TITLE || '材料价格AI分析系统',
  version: import.meta.env.VITE_APP_VERSION || '1.0.0',
  description: import.meta.env.VITE_APP_DESCRIPTION || '基于AI的智能价格分析平台',
  author: 'Claude AI Assistant',
  email: 'support@audit-system.com',
  github: 'https://github.com/audit-system',
  homepage: 'https://audit-system.com'
}

// API配置
export const API_CONFIG = {
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: Number(import.meta.env.VITE_API_TIMEOUT) || 60000,  // 增加到60秒
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest'
  },
  // 特殊接口的超时配置
  specialTimeouts: {
    importMaterials: 300000,      // 材料导入：5分钟
    batchAnalysis: 600000,        // 批量分析：10分钟
    generateReport: 180000,       // 生成报告：3分钟
    uploadLargeFile: 300000       // 大文件上传：5分钟
  }
}

// 上传配置
export const UPLOAD_CONFIG = {
  sizeLimit: Number(import.meta.env.VITE_UPLOAD_SIZE_LIMIT) || 52428800, // 50MB
  allowedTypes: (import.meta.env.VITE_UPLOAD_ALLOWED_TYPES || '.xlsx,.xls,.csv,.pdf,.doc,.docx').split(','),
  chunkSize: 1024 * 1024 * 2, // 2MB
  concurrent: 3, // 并发上传数
  retries: 3 // 重试次数
}

// 文件类型映射
export const FILE_TYPES = {
  excel: ['.xlsx', '.xls'],
  csv: ['.csv'],
  pdf: ['.pdf'],
  word: ['.doc', '.docx'],
  image: ['.jpg', '.jpeg', '.png', '.gif', '.webp'],
  archive: ['.zip', '.rar', '.7z', '.tar', '.gz']
}

// 材料分类
export const MATERIAL_CATEGORIES = {
  building: {
    label: '建筑材料',
    color: 'primary',
    icon: 'Building'
  },
  decoration: {
    label: '装修材料',
    color: 'success',
    icon: 'Brush'
  },
  machinery: {
    label: '机械设备',
    color: 'warning',
    icon: 'Tools'
  },
  labor: {
    label: '人工费',
    color: 'info',
    icon: 'User'
  },
  other: {
    label: '其他',
    color: 'default',
    icon: 'More'
  }
}

// 地区配置
export const REGIONS = {
  beijing: '北京',
  shanghai: '上海',
  guangzhou: '广州',
  shenzhen: '深圳',
  chengdu: '成都',
  chongqing: '重庆',
  wuhan: '武汉',
  nanjing: '南京',
  hangzhou: '杭州',
  xian: '西安',
  national: '全国'
}

// 数据来源
export const DATA_SOURCES = {
  government: {
    label: '政府信息价',
    color: 'success',
    icon: 'Flag'
  },
  market: {
    label: '市场调研',
    color: 'primary',
    icon: 'TrendCharts'
  },
  supplier: {
    label: '供应商报价',
    color: 'warning',
    icon: 'Shop'
  },
  historical: {
    label: '历史数据',
    color: 'info',
    icon: 'Clock'
  },
  other: {
    label: '其他',
    color: 'default',
    icon: 'More'
  }
}

// 项目状态
export const PROJECT_STATUS = {
  draft: {
    label: '草稿',
    color: 'info',
    icon: 'Edit'
  },
  processing: {
    label: '处理中',
    color: 'warning',
    icon: 'Loading'
  },
  completed: {
    label: '已完成',
    color: 'success',
    icon: 'Check'
  },
  failed: {
    label: '失败',
    color: 'danger',
    icon: 'Close'
  }
}

// 分析状态
export const ANALYSIS_STATUS = {
  pending: {
    label: '待分析',
    color: 'info',
    icon: 'Clock'
  },
  processing: {
    label: '分析中',
    color: 'warning',
    icon: 'Loading'
  },
  completed: {
    label: '已完成',
    color: 'success',
    icon: 'Check'
  },
  failed: {
    label: '失败',
    color: 'danger',
    icon: 'Close'
  }
}

// 风险等级
export const RISK_LEVELS = {
  normal: {
    label: '正常',
    color: 'success',
    icon: 'CircleCheck',
    threshold: 0
  },
  low: {
    label: '低风险',
    color: 'primary',
    icon: 'Check',
    threshold: 15
  },
  medium: {
    label: '中风险',
    color: 'warning',
    icon: 'Warning',
    threshold: 30
  },
  high: {
    label: '高风险',
    color: 'danger',
    icon: 'Close',
    threshold: 50
  },
  critical: {
    label: '极高风险',
    color: 'danger',
    icon: 'CircleClose',
    threshold: 100
  }
}

// 报告类型
export const REPORT_TYPES = {
  price_analysis: {
    label: '价格分析报告',
    color: 'primary',
    icon: 'TrendCharts'
  },
  material_audit: {
    label: '材料价格报告',
    color: 'success',
    icon: 'DocumentChecked'
  },
  project_summary: {
    label: '项目总结报告',
    color: 'warning',
    icon: 'Document'
  },
  risk_assessment: {
    label: '风险评估报告',
    color: 'danger',
    icon: 'Warning'
  },
  cost_optimization: {
    label: '成本优化报告',
    color: 'info',
    icon: 'Promotion'
  }
}

// 报告状态
export const REPORT_STATUS = {
  generating: {
    label: '生成中',
    color: 'warning',
    icon: 'Loading'
  },
  completed: {
    label: '已完成',
    color: 'success',
    icon: 'Check'
  },
  failed: {
    label: '生成失败',
    color: 'danger',
    icon: 'Close'
  },
  shared: {
    label: '已分享',
    color: 'info',
    icon: 'Share'
  },
  archived: {
    label: '已归档',
    color: 'default',
    icon: 'FolderOpened'
  }
}

// AI模型配置
export const AI_MODELS = {
  'gpt-4': {
    label: 'GPT-4',
    provider: 'OpenAI',
    description: '最先进的大语言模型，分析准确度高',
    costPer1000Tokens: 0.03,
    maxTokens: 8192
  },
  'gpt-3.5-turbo': {
    label: 'GPT-3.5 Turbo',
    provider: 'OpenAI',
    description: '性价比较高的模型，速度快',
    costPer1000Tokens: 0.002,
    maxTokens: 4096
  },
  'qwen-max': {
    label: '通义千问-Max',
    provider: '阿里云',
    description: '阿里云大模型，对中文理解好',
    costPer1000Tokens: 0.02,
    maxTokens: 6000
  },
  'qwen-plus': {
    label: '通义千问-Plus',
    provider: '阿里云',
    description: '性价比版本，适合批量处理',
    costPer1000Tokens: 0.004,
    maxTokens: 6000
  }
}

// 系统配置
export const SYSTEM_CONFIG = {
  theme: import.meta.env.VITE_SYSTEM_THEME || 'light',
  language: import.meta.env.VITE_SYSTEM_LANGUAGE || 'zh-CN',
  timezone: import.meta.env.VITE_SYSTEM_TIMEZONE || 'Asia/Shanghai',
  
  // 分页配置
  pagination: {
    pageSizes: [10, 20, 50, 100],
    defaultSize: 20,
    layout: 'total, sizes, prev, pager, next, jumper'
  },
  
  // 表格配置
  table: {
    stripe: true,
    border: false,
    size: 'default',
    showHeader: true,
    highlightCurrentRow: true
  },
  
  // 表单配置
  form: {
    labelWidth: '100px',
    labelPosition: 'right',
    size: 'default',
    validateOnRuleChange: true,
    showMessage: true,
    inlineMessage: false
  },
  
  // 消息配置
  message: {
    duration: 3000,
    showClose: true,
    center: false,
    offset: 20
  }
}

// 缓存配置
export const CACHE_CONFIG = {
  // 本地存储key前缀
  prefix: 'audit_system_',
  
  // 缓存时间（毫秒）
  ttl: {
    userInfo: 24 * 60 * 60 * 1000, // 24小时
    menuData: 30 * 60 * 1000, // 30分钟
    dictData: 60 * 60 * 1000, // 1小时
    projectList: 10 * 60 * 1000, // 10分钟
    materialList: 5 * 60 * 1000, // 5分钟
    analysisResult: 30 * 60 * 1000 // 30分钟
  }
}

// 性能配置
export const PERFORMANCE_CONFIG = {
  // 虚拟滚动阈值
  virtualScrollThreshold: 100,
  
  // 懒加载配置
  lazyLoad: {
    threshold: 0.1,
    rootMargin: '50px'
  },
  
  // 防抖延迟
  debounceDelay: 300,
  
  // 节流延迟
  throttleDelay: 100,
  
  // 批量处理大小
  batchSize: 50,
  
  // 并发请求数
  concurrentRequests: 5
}

// 安全配置
export const SECURITY_CONFIG = {
  // 密码规则
  password: {
    minLength: 8,
    maxLength: 20,
    requireUppercase: true,
    requireLowercase: true,
    requireNumbers: true,
    requireSpecialChars: true,
    specialChars: '!@#$%^&*()_+-=[]{}|;:,.<>?'
  },
  
  // 会话配置
  session: {
    timeout: 2 * 60 * 60 * 1000, // 2小时
    renewBefore: 10 * 60 * 1000, // 过期前10分钟续期
    maxConcurrentSessions: 3
  },
  
  // 上传安全
  upload: {
    allowedMimeTypes: [
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'text/csv',
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ],
    maxFileSize: 50 * 1024 * 1024, // 50MB
    scanForVirus: true,
    quarantinePath: '/tmp/quarantine'
  }
}

// 导出默认配置
export default {
  APP_CONFIG,
  API_CONFIG,
  UPLOAD_CONFIG,
  FILE_TYPES,
  MATERIAL_CATEGORIES,
  REGIONS,
  DATA_SOURCES,
  PROJECT_STATUS,
  ANALYSIS_STATUS,
  RISK_LEVELS,
  REPORT_TYPES,
  REPORT_STATUS,
  AI_MODELS,
  SYSTEM_CONFIG,
  CACHE_CONFIG,
  PERFORMANCE_CONFIG,
  SECURITY_CONFIG
}
