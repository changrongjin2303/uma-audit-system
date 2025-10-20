import { request } from '@/utils/request'

// 生成分析报告
export function generateReport(data) {
  return request.post('/reports/generate', data, {
    timeout: 300000, // 5分钟超时
    showLoading: true,
    loadingText: '正在生成报告，请耐心等待...'
  })
}

// 获取报告列表
export function getReportsList(params = {}) {
  return request.get('/reports/', params)
}

// 获取报告详情
export function getReport(reportId) {
  return request.get(`/reports/${reportId}`)
}

// 下载报告
export function downloadReport(reportId, format = 'docx') {
  return request.download(`/reports/${reportId}/download`, { format })
}

// 预览报告
export function previewReport(reportId) {
  return request.get(`/reports/${reportId}/preview`)
}

// 按项目预览报告（后端提供 /reports/project/{project_id}/preview）
export function previewReportByProject(projectId) {
  return request.get(`/reports/project/${projectId}/preview`)
}

// 删除报告
export function deleteReport(reportId) {
  return request.delete(`/reports/${reportId}`)
}

// 批量删除报告
export function batchDeleteReports(reportIds) {
  return request.post('/reports/batch-delete/', { report_ids: reportIds })
}

// 更新报告信息
export function updateReport(reportId, data) {
  return request.put(`/reports/${reportId}`, data)
}

// 分享报告
export function shareReport(reportId, shareData) {
  return request.post(`/reports/${reportId}/share`, shareData)
}

// 取消分享
export function unshareReport(reportId) {
  return request.delete(`/reports/${reportId}/share`)
}

// 获取报告模板列表
export function getReportTemplates() {
  return request.get('/reports/templates/')
}

// 获取报告模板详情
export function getReportTemplate(templateId) {
  return request.get(`/reports/templates/${templateId}`)
}

// 创建报告模板
export function createReportTemplate(data) {
  return request.post('/reports/templates', data)
}

// 更新报告模板
export function updateReportTemplate(templateId, data) {
  return request.put(`/reports/templates/${templateId}`, data)
}

// 删除报告模板
export function deleteReportTemplate(templateId) {
  return request.delete(`/reports/templates/${templateId}`)
}

// 获取报告类型
export function getReportTypes() {
  return request.get('/reports/types')
}

// 获取报告状态选项
export function getReportStatuses() {
  return request.get('/reports/statuses')
}

// 获取报告生成进度
export function getReportProgress(reportId) {
  return request.get(`/reports/${reportId}/progress`)
}

// 取消报告生成
export function cancelReportGeneration(reportId) {
  return request.post(`/reports/${reportId}/cancel`)
}

// 重新生成报告
export function regenerateReport(reportId, options = {}) {
  return request.post(`/reports/${reportId}/regenerate`, options)
}

// 获取报告统计信息
export function getReportStatistics(params = {}) {
  return request.get('/reports/statistics', params)
}

// 获取报告生成历史
export function getReportGenerationHistory(params = {}) {
  return request.get('/reports/generation-history', params)
}

// 批量生成报告
export function batchGenerateReports(data) {
  return request.post('/reports/batch-generate', data)
}

// 获取批量生成任务状态
export function getBatchGenerationStatus(taskId) {
  return request.get(`/reports/batch-tasks/${taskId}/status`)
}

// 导出报告列表
export function exportReportsList(params = {}) {
  return request.download('/reports/export-list', params)
}

// 获取报告审批列表
export function getReportApprovals(params = {}) {
  return request.get('/reports/approvals', params)
}

// 提交报告审批
export function submitReportApproval(reportId, approvalData) {
  return request.post(`/reports/${reportId}/submit-approval`, approvalData)
}

// 审批报告
export function approveReport(reportId, approvalData) {
  return request.post(`/reports/${reportId}/approve`, approvalData)
}

// 拒绝报告
export function rejectReport(reportId, rejectionData) {
  return request.post(`/reports/${reportId}/reject`, rejectionData)
}

// 撤回报告审批
export function withdrawReportApproval(reportId) {
  return request.post(`/reports/${reportId}/withdraw-approval`)
}

// 获取报告版本列表
export function getReportVersions(reportId) {
  return request.get(`/reports/${reportId}/versions`)
}

// 比较报告版本
export function compareReportVersions(reportId, versionIds) {
  return request.post(`/reports/${reportId}/compare-versions`, { version_ids: versionIds })
}

// 恢复报告版本
export function restoreReportVersion(reportId, versionId) {
  return request.post(`/reports/${reportId}/restore-version`, { version_id: versionId })
}

// 获取报告评论列表
export function getReportComments(reportId, params = {}) {
  return request.get(`/reports/${reportId}/comments`, params)
}

// 添加报告评论
export function addReportComment(reportId, commentData) {
  return request.post(`/reports/${reportId}/comments`, commentData)
}

// 删除报告评论
export function deleteReportComment(reportId, commentId) {
  return request.delete(`/reports/${reportId}/comments/${commentId}`)
}

// 回复报告评论
export function replyReportComment(reportId, commentId, replyData) {
  return request.post(`/reports/${reportId}/comments/${commentId}/reply`, replyData)
}

// 获取报告附件列表
export function getReportAttachments(reportId) {
  return request.get(`/reports/${reportId}/attachments`)
}

// 上传报告附件
export function uploadReportAttachment(reportId, file, onUploadProgress) {
  const formData = new FormData()
  formData.append('file', file)
  
  return request.post(`/reports/${reportId}/attachments`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    onUploadProgress
  })
}

// 下载报告附件
export function downloadReportAttachment(reportId, attachmentId) {
  return request.download(`/reports/${reportId}/attachments/${attachmentId}`)
}

// 删除报告附件
export function deleteReportAttachment(reportId, attachmentId) {
  return request.delete(`/reports/${reportId}/attachments/${attachmentId}`)
}

// 获取报告配置
export function getReportConfig() {
  return request.get('/reports/config')
}

// 更新报告配置
export function updateReportConfig(config) {
  return request.put('/reports/config', config)
}

// 获取报告格式选项
export function getReportFormats() {
  return request.get('/reports/formats')
}

// 获取报告水印设置
export function getReportWatermarkSettings() {
  return request.get('/reports/watermark-settings')
}

// 更新报告水印设置
export function updateReportWatermarkSettings(settings) {
  return request.put('/reports/watermark-settings', settings)
}

// 获取报告签名设置
export function getReportSignatureSettings() {
  return request.get('/reports/signature-settings')
}

// 更新报告签名设置
export function updateReportSignatureSettings(settings) {
  return request.put('/reports/signature-settings', settings)
}

// 验证报告数字签名
export function verifyReportSignature(reportId) {
  return request.post(`/reports/${reportId}/verify-signature`)
}

// 获取报告访问日志
export function getReportAccessLogs(reportId, params = {}) {
  return request.get(`/reports/${reportId}/access-logs`, params)
}

// 记录报告访问
export function logReportAccess(reportId, accessData) {
  return request.post(`/reports/${reportId}/log-access`, accessData)
}

// 获取报告分析洞察
export function getReportInsights(reportId) {
  return request.get(`/reports/${reportId}/insights`)
}

// 获取报告推荐
export function getReportRecommendations(params = {}) {
  return request.get('/reports/recommendations', params)
}

// 标记报告为收藏
export function favoriteReport(reportId) {
  return request.post(`/reports/${reportId}/favorite`)
}

// 取消收藏报告
export function unfavoriteReport(reportId) {
  return request.delete(`/reports/${reportId}/favorite`)
}

// 获取收藏报告列表
export function getFavoriteReports(params = {}) {
  return request.get('/reports/favorites', params)
}

// 获取最近查看的报告
export function getRecentReports(params = {}) {
  return request.get('/reports/recent', params)
}

// 搜索报告
export function searchReports(params = {}) {
  return request.get('/reports/search', params)
}

// 获取报告标签
export function getReportTags() {
  return request.get('/reports/tags')
}

// 为报告添加标签
export function addReportTag(reportId, tagData) {
  return request.post(`/reports/${reportId}/tags`, tagData)
}

// 删除报告标签
export function removeReportTag(reportId, tagId) {
  return request.delete(`/reports/${reportId}/tags/${tagId}`)
}

// 获取报告性能指标
export function getReportPerformanceMetrics(params = {}) {
  return request.get('/reports/performance-metrics', params)
}

// 获取报告质量评分
export function getReportQualityScore(reportId) {
  return request.get(`/reports/${reportId}/quality-score`)
}

// 提交报告质量反馈
export function submitReportQualityFeedback(reportId, feedbackData) {
  return request.post(`/reports/${reportId}/quality-feedback`, feedbackData)
}

// 获取报告使用统计
export function getReportUsageStatistics(reportId) {
  return request.get(`/reports/${reportId}/usage-statistics`)
}

// 归档报告
export function archiveReport(reportId) {
  return request.post(`/reports/${reportId}/archive`)
}

// 取消归档报告
export function unarchiveReport(reportId) {
  return request.post(`/reports/${reportId}/unarchive`)
}

// 获取归档报告列表
export function getArchivedReports(params = {}) {
  return request.get('/reports/archived', params)
}

// 永久删除报告
export function permanentlyDeleteReport(reportId) {
  return request.delete(`/reports/${reportId}/permanent`)
}

// 恢复已删除报告
export function restoreDeletedReport(reportId) {
  return request.post(`/reports/${reportId}/restore`)
}

// 获取回收站报告列表
export function getTrashedReports(params = {}) {
  return request.get('/reports/trash', params)
}

// 清空回收站
export function emptyReportsTrash() {
  return request.delete('/reports/trash/empty')
}
