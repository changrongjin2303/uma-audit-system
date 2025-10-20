/**
 * API测试和调试工具
 */

import request from '@/utils/request'
import { ElMessage, ElNotification } from 'element-plus'

class ApiTester {
  constructor() {
    this.testResults = []
    this.isRunning = false
  }

  /**
   * 执行API测试
   * @param {Array} testCases - 测试用例数组
   * @param {Object} options - 测试选项
   */
  async runTests(testCases, options = {}) {
    const {
      verbose = true,
      stopOnError = false,
      timeout = 30000,
      concurrent = false
    } = options

    this.isRunning = true
    this.testResults = []

    if (verbose) {
      ElNotification.info({
        title: 'API测试',
        message: `开始执行 ${testCases.length} 个测试用例`,
        duration: 2000
      })
    }

    try {
      const results = concurrent
        ? await this._runTestsConcurrent(testCases, { timeout, stopOnError })
        : await this._runTestsSequential(testCases, { timeout, stopOnError, verbose })

      const summary = this._generateSummary(results)
      
      if (verbose) {
        this._displaySummary(summary)
      }

      return {
        results,
        summary,
        success: summary.failedCount === 0
      }
    } finally {
      this.isRunning = false
    }
  }

  /**
   * 顺序执行测试用例
   */
  async _runTestsSequential(testCases, options) {
    const { timeout, stopOnError, verbose } = options
    const results = []

    for (let i = 0; i < testCases.length; i++) {
      const testCase = testCases[i]
      
      if (verbose) {
        console.log(`执行测试 ${i + 1}/${testCases.length}: ${testCase.name}`)
      }

      const result = await this._executeTestCase(testCase, timeout)
      results.push(result)
      this.testResults.push(result)

      if (result.status === 'failed' && stopOnError) {
        break
      }
    }

    return results
  }

  /**
   * 并发执行测试用例
   */
  async _runTestsConcurrent(testCases, options) {
    const { timeout } = options
    
    const promises = testCases.map(testCase => 
      this._executeTestCase(testCase, timeout)
    )

    const results = await Promise.allSettled(promises)
    
    return results.map(result => result.value || {
      status: 'failed',
      error: result.reason,
      duration: 0
    })
  }

  /**
   * 执行单个测试用例
   */
  async _executeTestCase(testCase, timeout) {
    const startTime = Date.now()
    
    try {
      // 验证测试用例格式
      if (!this._validateTestCase(testCase)) {
        throw new Error('测试用例格式不正确')
      }

      // 执行前置条件
      if (testCase.before) {
        await testCase.before()
      }

      // 执行API请求
      const response = await Promise.race([
        this._makeApiRequest(testCase),
        new Promise((_, reject) => 
          setTimeout(() => reject(new Error('请求超时')), timeout)
        )
      ])

      // 验证响应
      const validationResult = await this._validateResponse(response, testCase.expect)
      
      // 执行后置条件
      if (testCase.after) {
        await testCase.after(response)
      }

      const duration = Date.now() - startTime

      return {
        name: testCase.name,
        status: validationResult.success ? 'passed' : 'failed',
        response,
        validation: validationResult,
        duration,
        timestamp: new Date().toISOString()
      }
    } catch (error) {
      const duration = Date.now() - startTime
      
      return {
        name: testCase.name,
        status: 'failed',
        error: error.message,
        duration,
        timestamp: new Date().toISOString()
      }
    }
  }

  /**
   * 验证测试用例格式
   */
  _validateTestCase(testCase) {
    const required = ['name', 'method', 'url']
    return required.every(field => testCase[field])
  }

  /**
   * 发起API请求
   */
  async _makeApiRequest(testCase) {
    const { method, url, data, params, headers } = testCase

    const config = {
      method: method.toLowerCase(),
      url,
      showLoading: false,
      showSuccessMessage: false
    }

    if (data) config.data = data
    if (params) config.params = params
    if (headers) config.headers = { ...config.headers, ...headers }

    return await request[method.toLowerCase()](url, data || params, config)
  }

  /**
   * 验证响应数据
   */
  async _validateResponse(response, expectations) {
    if (!expectations) {
      return { success: true, message: '无验证规则' }
    }

    const errors = []

    // 验证状态码
    if (expectations.status && response.code !== expectations.status) {
      errors.push(`状态码不匹配: 期望 ${expectations.status}, 实际 ${response.code}`)
    }

    // 验证响应结构
    if (expectations.schema) {
      const schemaErrors = this._validateSchema(response.data, expectations.schema)
      errors.push(...schemaErrors)
    }

    // 验证响应数据
    if (expectations.data) {
      const dataErrors = this._validateData(response.data, expectations.data)
      errors.push(...dataErrors)
    }

    // 自定义验证函数
    if (expectations.custom && typeof expectations.custom === 'function') {
      try {
        const customResult = await expectations.custom(response)
        if (!customResult.success) {
          errors.push(customResult.message || '自定义验证失败')
        }
      } catch (error) {
        errors.push(`自定义验证异常: ${error.message}`)
      }
    }

    return {
      success: errors.length === 0,
      errors,
      message: errors.length === 0 ? '验证通过' : errors.join('; ')
    }
  }

  /**
   * 验证数据结构
   */
  _validateSchema(data, schema) {
    const errors = []

    const validateObject = (obj, schemaObj, path = '') => {
      Object.keys(schemaObj).forEach(key => {
        const fieldPath = path ? `${path}.${key}` : key
        const expectedType = schemaObj[key]
        const actualValue = obj[key]

        if (actualValue === undefined) {
          errors.push(`缺少字段: ${fieldPath}`)
          return
        }

        if (typeof expectedType === 'string') {
          if (typeof actualValue !== expectedType) {
            errors.push(`字段类型不匹配: ${fieldPath} (期望 ${expectedType}, 实际 ${typeof actualValue})`)
          }
        } else if (typeof expectedType === 'object' && !Array.isArray(expectedType)) {
          if (typeof actualValue === 'object' && !Array.isArray(actualValue)) {
            validateObject(actualValue, expectedType, fieldPath)
          } else {
            errors.push(`字段类型不匹配: ${fieldPath} (期望 object)`)
          }
        }
      })
    }

    if (typeof data === 'object' && typeof schema === 'object') {
      validateObject(data, schema)
    }

    return errors
  }

  /**
   * 验证数据内容
   */
  _validateData(actual, expected) {
    const errors = []

    const compareValues = (actualVal, expectedVal, path = '') => {
      if (typeof expectedVal === 'function') {
        // 使用函数验证
        try {
          const result = expectedVal(actualVal)
          if (!result) {
            errors.push(`数据验证失败: ${path}`)
          }
        } catch (error) {
          errors.push(`数据验证异常: ${path} - ${error.message}`)
        }
      } else if (Array.isArray(expectedVal)) {
        if (!Array.isArray(actualVal)) {
          errors.push(`类型不匹配: ${path} (期望数组)`)
        } else if (expectedVal.length > 0) {
          // 验证数组元素
          actualVal.forEach((item, index) => {
            compareValues(item, expectedVal[0], `${path}[${index}]`)
          })
        }
      } else if (typeof expectedVal === 'object' && expectedVal !== null) {
        if (typeof actualVal !== 'object' || actualVal === null) {
          errors.push(`类型不匹配: ${path} (期望对象)`)
        } else {
          Object.keys(expectedVal).forEach(key => {
            compareValues(actualVal[key], expectedVal[key], path ? `${path}.${key}` : key)
          })
        }
      } else if (actualVal !== expectedVal) {
        errors.push(`值不匹配: ${path} (期望 ${expectedVal}, 实际 ${actualVal})`)
      }
    }

    compareValues(actual, expected)
    return errors
  }

  /**
   * 生成测试摘要
   */
  _generateSummary(results) {
    const total = results.length
    const passed = results.filter(r => r.status === 'passed').length
    const failed = results.filter(r => r.status === 'failed').length
    const totalDuration = results.reduce((sum, r) => sum + r.duration, 0)
    const averageDuration = total > 0 ? totalDuration / total : 0

    return {
      total,
      passed,
      failed: failed,
      passedCount: passed,
      failedCount: failed,
      successRate: total > 0 ? (passed / total * 100).toFixed(2) : 0,
      totalDuration,
      averageDuration: Math.round(averageDuration)
    }
  }

  /**
   * 显示测试摘要
   */
  _displaySummary(summary) {
    const { total, passed, failed, successRate, totalDuration } = summary

    const message = `
测试完成: ${total} 个用例
通过: ${passed} 个
失败: ${failed} 个
成功率: ${successRate}%
总耗时: ${totalDuration}ms
    `.trim()

    if (failed === 0) {
      ElNotification.success({
        title: 'API测试完成',
        message,
        duration: 5000
      })
    } else {
      ElNotification.error({
        title: 'API测试完成',
        message,
        duration: 5000
      })
    }

    console.group('API测试结果')
    console.log('摘要:', summary)
    console.log('详细结果:', this.testResults)
    console.groupEnd()
  }

  /**
   * 获取测试结果
   */
  getResults() {
    return this.testResults
  }

  /**
   * 清空测试结果
   */
  clearResults() {
    this.testResults = []
  }

  /**
   * 导出测试结果
   */
  exportResults(format = 'json') {
    const data = {
      timestamp: new Date().toISOString(),
      summary: this._generateSummary(this.testResults),
      results: this.testResults
    }

    let content = ''
    let filename = `api-test-results-${Date.now()}`
    let mimeType = 'application/json'

    switch (format.toLowerCase()) {
      case 'json':
        content = JSON.stringify(data, null, 2)
        filename += '.json'
        break
      case 'csv':
        content = this._convertToCSV(this.testResults)
        filename += '.csv'
        mimeType = 'text/csv'
        break
      default:
        throw new Error(`不支持的导出格式: ${format}`)
    }

    // 创建下载
    const blob = new Blob([content], { type: mimeType })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  }

  /**
   * 转换为CSV格式
   */
  _convertToCSV(results) {
    if (results.length === 0) return ''

    const headers = ['名称', '状态', '耗时(ms)', '错误信息', '时间戳']
    const rows = results.map(result => [
      `"${result.name}"`,
      `"${result.status}"`,
      result.duration,
      `"${result.error || ''}"`,
      `"${result.timestamp}"`
    ])

    return [headers.join(','), ...rows.map(row => row.join(','))].join('\n')
  }
}

// 预定义的测试用例模板
export const testTemplates = {
  // 基本GET请求
  basicGet: (url, name = 'GET请求测试') => ({
    name,
    method: 'GET',
    url,
    expect: {
      status: 200,
      schema: {
        code: 'number',
        data: 'object',
        message: 'string'
      }
    }
  }),

  // 基本POST请求
  basicPost: (url, data, name = 'POST请求测试') => ({
    name,
    method: 'POST',
    url,
    data,
    expect: {
      status: 200
    }
  }),

  // 分页请求测试
  paginationTest: (url, name = '分页请求测试') => ({
    name,
    method: 'GET',
    url,
    params: { page: 1, size: 10 },
    expect: {
      status: 200,
      schema: {
        code: 'number',
        data: 'object',
        message: 'string'
      },
      data: {
        items: (items) => Array.isArray(items),
        total: (total) => typeof total === 'number' && total >= 0
      }
    }
  }),

  // 文件上传测试
  uploadTest: (url, file, name = '文件上传测试') => ({
    name,
    method: 'POST',
    url,
    data: file,
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    expect: {
      status: 200
    }
  })
}

// 创建默认实例
const apiTester = new ApiTester()

export { ApiTester }
export default apiTester