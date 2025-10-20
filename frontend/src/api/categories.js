/**
 * 材料分类管理API
 */
import request from '@/utils/request'

const API_PREFIX = '/api/v1/material-categories'

/**
 * 获取分类树结构
 * @param {Object} params - 查询参数
 * @param {string} params.source_type - 信息来源类型 (municipal/provincial)
 * @param {boolean} params.include_inactive - 是否包含未启用的分类
 * @returns {Promise} 分类树数据
 */
export function getCategoryTree(params = {}) {
  return request({
    url: `${API_PREFIX}/tree`,
    method: 'get',
    params
  })
}

/**
 * 按层级获取分类
 * @param {number} level - 层级 (1=信息来源类型, 2=年月, 3=具体分类)
 * @param {Object} params - 查询参数
 * @param {number} params.parent_id - 父分类ID
 * @param {string} params.source_type - 信息来源类型
 * @returns {Promise} 分类列表
 */
export function getCategoriesByLevel(level, params = {}) {
  return request({
    url: `${API_PREFIX}/level/${level}`,
    method: 'get',
    params
  })
}

/**
 * 获取所有信息来源类型
 * @returns {Promise} 信息来源类型列表
 */
export function getSourceTypes() {
  return request({
    url: `${API_PREFIX}/source-types`,
    method: 'get'
  })
}

/**
 * 获取指定信息来源的年月分类
 * @param {string} sourceType - 信息来源类型
 * @returns {Promise} 年月分类列表
 */
export function getYearMonthCategories(sourceType) {
  return request({
    url: `${API_PREFIX}/year-month/${sourceType}`,
    method: 'get'
  })
}

/**
 * 创建年月分类
 * @param {Object} data - 创建数据
 * @param {string} data.source_type - 信息来源类型
 * @param {string} data.year_month - 年月
 * @param {string} data.description - 描述
 * @returns {Promise} 创建结果
 */
export function createYearMonthCategory(data) {
  return request({
    url: `${API_PREFIX}/year-month`,
    method: 'post',
    data
  })
}