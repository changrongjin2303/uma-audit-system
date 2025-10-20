import { request } from '@/utils/request'

// 批量分析项目材料价格
export function batchAnalyzeMaterials(projectId, data = {}, config = {}) {
  // 提取config选项，避免传递到后端
  const { __skipLoading, ...apiData } = data
  const requestConfig = { 
    timeout: 300000, // AI分析需要更长时间，设置为5分钟
    ...config 
  }
  if (__skipLoading) {
    requestConfig.__skipLoading = true
  }
  return request.post(`/analysis/${projectId}/analyze`, apiData, requestConfig)
}

// 分析单个材料价格
export function analyzeSingleMaterial(materialId, data = {}, config = {}) {
  const requestConfig = { 
    timeout: 120000, // 单个材料分析，设置为2分钟
    ...config 
  }
  return request.post(`/analysis/materials/${materialId}/analyze`, data, requestConfig)
}

// 分析市场信息价材料价格差异
export function analyzePricedMaterials(projectId, data = {}, config = {}) {
  // 提取config选项，避免传递到后端
  const { __skipLoading, ...apiData } = data
  const requestConfig = { 
    timeout: 300000, // 市场信息价材料分析需要更长时间，设置为5分钟
    ...config 
  }
  if (__skipLoading) {
    requestConfig.__skipLoading = true
  }
  return request.post(`/analysis/${projectId}/analyze-priced-materials`, apiData, requestConfig)
}

// 获取项目分析结果
export function getProjectAnalysisResults(projectId, params = {}) {
  return request.get(`/analysis/${projectId}/analysis-results`, params)
}

// 获取市场信息价材料分析结果
export function getProjectPricedMaterialsAnalysis(projectId, params = {}) {
  return request.get(`/analysis/${projectId}/priced-materials-analysis`, params)
}

// 获取单个材料分析结果
export function getMaterialAnalysisResult(materialId) {
  return request.get(`/analysis/materials/${materialId}/analysis`)
}

// 删除单个材料的分析结果
export function deleteMaterialAnalysis(materialId) {
  return request.delete(`/analysis/materials/${materialId}/analysis`)
}

// 获取项目分析统计信息
export function getProjectAnalysisStatistics(projectId) {
  return request.get(`/analysis/${projectId}/analysis-statistics`)
}

// 获取有分析结果的项目列表
export function getProjectsWithAnalysis() {
  return request.get('/analysis/projects-with-results')
}

// 获取可用AI服务列表
export function getAvailableAIServices() {
  return request.get('/analysis/ai-services/available')
}

// 测试AI服务可用性
export function testAIServiceAvailability(serviceId) {
  return request.post('/analysis/ai-services/test', { service_id: serviceId })
}

// 获取单个材料的详细分析结果（包括原始材料信息、匹配的市场信息价材料信息和分析结果）
export function getMaterialAnalysisDetail(materialId) {
  return request.get(`/analysis/materials/${materialId}/analysis-detail`)
}

// 获取分析配置
export function getAnalysisConfig() {
  return request.get('/analysis/config')
}

// 更新分析配置
export function updateAnalysisConfig(config) {
  return request.put('/analysis/config', config)
}

// 获取分析任务列表
export function getAnalysisTasks(params = {}) {
  return request.get('/analysis/tasks', params)
}

// 获取分析任务详情
export function getAnalysisTask(taskId) {
  return request.get(`/analysis/tasks/${taskId}`)
}

// 取消分析任务
export function cancelAnalysisTask(taskId) {
  return request.post(`/analysis/tasks/${taskId}/cancel`)
}

// 重试分析任务
export function retryAnalysisTask(taskId) {
  return request.post(`/analysis/tasks/${taskId}/retry`)
}

// 获取分析历史记录
export function getAnalysisHistory(materialId, params = {}) {
  return request.get(`/analysis/materials/${materialId}/history`, params)
}

// 批量重新分析
export function batchReanalyze(materialIds, options = {}) {
  return request.post('/analysis/batch-reanalyze', {
    material_ids: materialIds,
    ...options
  })
}

// 调整分析结果
export function adjustAnalysisResult(materialId, adjustmentData) {
  return request.post(`/analysis/materials/${materialId}/adjust`, adjustmentData)
}

// 批量调整分析结果
export function batchAdjustAnalysisResults(adjustments) {
  return request.post('/analysis/batch-adjust', { adjustments })
}

// 导出分析结果
export function exportAnalysisResults(projectId, params = {}) {
  return request.download(`/analysis/${projectId}/export`, params)
}

// 获取分析质量报告
export function getAnalysisQualityReport(projectId) {
  return request.get(`/analysis/${projectId}/quality-report`)
}

// 获取AI服务使用统计
export function getAIServiceUsageStats(params = {}) {
  return request.get('/analysis/ai-usage-stats', params)
}

// 获取分析性能指标
export function getAnalysisPerformanceMetrics(params = {}) {
  return request.get('/analysis/performance-metrics', params)
}

// 获取分析错误日志
export function getAnalysisErrorLogs(params = {}) {
  return request.get('/analysis/error-logs', params)
}

// 获取价格预测模型信息
export function getPricePredictionModels() {
  return request.get('/analysis/prediction-models')
}

// 更新价格预测模型
export function updatePricePredictionModel(modelId, data) {
  return request.put(`/analysis/prediction-models/${modelId}`, data)
}

// 训练价格预测模型
export function trainPricePredictionModel(modelId, trainingData) {
  return request.post(`/analysis/prediction-models/${modelId}/train`, trainingData)
}

// 获取模型训练状态
export function getModelTrainingStatus(taskId) {
  return request.get(`/analysis/model-training/${taskId}/status`)
}

// 评估模型性能
export function evaluateModelPerformance(modelId, evaluationData) {
  return request.post(`/analysis/prediction-models/${modelId}/evaluate`, evaluationData)
}

// 获取分析结果对比
export function compareAnalysisResults(materialIds, params = {}) {
  return request.post('/analysis/compare-results', {
    material_ids: materialIds,
    ...params
  })
}

// 获取分析置信度分布
export function getConfidenceDistribution(projectId) {
  return request.get(`/analysis/${projectId}/confidence-distribution`)
}

// 获取价格偏差分析
export function getPriceDeviationAnalysis(projectId, params = {}) {
  return request.get(`/analysis/${projectId}/price-deviation`, params)
}

// 获取异常价格检测结果
export function getAbnormalPriceDetection(projectId, params = {}) {
  return request.get(`/analysis/${projectId}/abnormal-prices`, params)
}

// 标记异常价格
export function markAbnormalPrice(materialId, reason) {
  return request.post(`/analysis/materials/${materialId}/mark-abnormal`, { reason })
}

// 取消异常标记
export function unmarkAbnormalPrice(materialId) {
  return request.delete(`/analysis/materials/${materialId}/mark-abnormal`)
}

// 获取分析建议
export function getAnalysisSuggestions(projectId) {
  return request.get(`/analysis/${projectId}/suggestions`)
}

// 应用分析建议
export function applyAnalysisSuggestion(suggestionId) {
  return request.post(`/analysis/suggestions/${suggestionId}/apply`)
}

// 忽略分析建议
export function ignoreAnalysisSuggestion(suggestionId, reason) {
  return request.post(`/analysis/suggestions/${suggestionId}/ignore`, { reason })
}

// 获取分析进度
export function getAnalysisProgress(projectId) {
  return request.get(`/analysis/${projectId}/progress`)
}

// 获取实时分析状态
export function getRealTimeAnalysisStatus() {
  return request.get('/analysis/realtime-status')
}

// 暂停分析任务
export function pauseAnalysisTask(taskId) {
  return request.post(`/analysis/tasks/${taskId}/pause`)
}

// 恢复分析任务
export function resumeAnalysisTask(taskId) {
  return request.post(`/analysis/tasks/${taskId}/resume`)
}

// 获取分析队列状态
export function getAnalysisQueueStatus() {
  return request.get('/analysis/queue-status')
}

// 清空分析队列
export function clearAnalysisQueue() {
  return request.post('/analysis/clear-queue')
}

// 重新排队分析
export function requeueAnalysis(materialIds) {
  return request.post('/analysis/requeue', { material_ids: materialIds })
}

// 获取分析优先级设置
export function getAnalysisPriorities() {
  return request.get('/analysis/priorities')
}

// 设置分析优先级
export function setAnalysisPriority(materialId, priority) {
  return request.post(`/analysis/materials/${materialId}/priority`, { priority })
}

// 获取分析规则
export function getAnalysisRules() {
  return request.get('/analysis/rules')
}

// 创建分析规则
export function createAnalysisRule(ruleData) {
  return request.post('/analysis/rules', ruleData)
}

// 更新分析规则
export function updateAnalysisRule(ruleId, ruleData) {
  return request.put(`/analysis/rules/${ruleId}`, ruleData)
}

// 删除分析规则
export function deleteAnalysisRule(ruleId) {
  return request.delete(`/analysis/rules/${ruleId}`)
}

// 应用分析规则
export function applyAnalysisRule(ruleId, materialIds) {
  return request.post(`/analysis/rules/${ruleId}/apply`, { material_ids: materialIds })
}

// 获取分析报告模板
export function getAnalysisReportTemplates() {
  return request.get('/analysis/report-templates')
}

// 生成分析报告
export function generateAnalysisReport(projectId, templateId, options = {}) {
  return request.post(`/analysis/${projectId}/generate-report`, {
    template_id: templateId,
    ...options
  })
}

// 获取分析报告
export function getAnalysisReport(reportId) {
  return request.get(`/analysis/reports/${reportId}`)
}

// 下载分析报告
export function downloadAnalysisReport(reportId, format = 'pdf') {
  return request.download(`/analysis/reports/${reportId}/download`, { format })
}

// 分享分析报告
export function shareAnalysisReport(reportId, shareOptions) {
  return request.post(`/analysis/reports/${reportId}/share`, shareOptions)
}

// 获取分析洞察
export function getAnalysisInsights(projectId, params = {}) {
  return request.get(`/analysis/${projectId}/insights`, params)
}

// 获取价格趋势预测
export function getPriceTrendPrediction(materialId, params = {}) {
  return request.get(`/analysis/materials/${materialId}/trend-prediction`, params)
}

// 获取市场价格对比
export function getMarketPriceComparison(materialId, params = {}) {
  return request.get(`/analysis/materials/${materialId}/market-comparison`, params)
}

// 获取供应商价格分析
export function getSupplierPriceAnalysis(projectId, params = {}) {
  return request.get(`/analysis/${projectId}/supplier-price-analysis`, params)
}

// 获取区域价格差异分析
export function getRegionalPriceDifference(materialId, params = {}) {
  return request.get(`/analysis/materials/${materialId}/regional-difference`, params)
}

// 获取季节性价格分析
export function getSeasonalPriceAnalysis(materialId, params = {}) {
  return request.get(`/analysis/materials/${materialId}/seasonal-analysis`, params)
}

// 获取价格波动风险评估
export function getPriceVolatilityRisk(materialId, params = {}) {
  return request.get(`/analysis/materials/${materialId}/volatility-risk`, params)
}

// 获取成本优化建议
export function getCostOptimizationSuggestions(projectId, params = {}) {
  return request.get(`/analysis/${projectId}/cost-optimization`, params)
}

// 应用成本优化建议
export function applyCostOptimization(projectId, optimizationId) {
  return request.post(`/analysis/${projectId}/apply-optimization`, { 
    optimization_id: optimizationId 
  })
}

// 获取分析API使用量统计
export function getAnalysisAPIUsage(params = {}) {
  return request.get('/analysis/api-usage', params)
}

// 获取分析成本统计
export function getAnalysisCostStats(params = {}) {
  return request.get('/analysis/cost-stats', params)
}
