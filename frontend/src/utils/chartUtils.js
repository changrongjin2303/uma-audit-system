// 提取自 ReportDetail.vue 的图表数据准备逻辑
export const prepareChartData = (analysisData = [], guidanceData = []) => {
  const riskOrder = ['normal', 'low', 'medium', 'high', 'critical']
  const riskLabels = {
    normal: '正常',
    low: '低风险',
    medium: '中风险',
    high: '高风险',
    critical: '极高风险'
  }
  const riskColors = {
    normal: '#67C23A',
    low: '#409EFF',
    medium: '#E6A23C',
    high: '#F56C6C',
    critical: '#C039A5'
  }

  const normalizeNumber = (value) => {
    const num = Number(value)
    return Number.isFinite(num) ? num : 0
  }

  const analysisItems = (analysisData || []).map(item => {
    const quantity = normalizeNumber(item.quantity || item.quantity_value)
    const originalUnit = normalizeNumber(item.original_price)
    const aiUnit = normalizeNumber(item.ai_predicted_price || item.predicted_price)
    const originalTotal = item.original_total_price !== undefined
      ? normalizeNumber(item.original_total_price)
      : originalUnit * quantity
    const aiTotal = item.ai_total_price !== undefined
      ? normalizeNumber(item.ai_total_price)
      : aiUnit * quantity
    const adjustment = item.adjustment !== undefined
      ? normalizeNumber(item.adjustment)
      : originalTotal - aiTotal
    const riskLevel = (item.risk_level || '').toLowerCase()

    return {
      name: item.material_name || item.name || '材料',
      riskLevel: riskLevel || 'normal',
      adjustment,
      originalTotal,
      aiTotal
    }
  })

  const guidanceItems = (guidanceData || []).map(item => {
    const originalTotal = item.original_total_price !== undefined
      ? normalizeNumber(item.original_total_price)
      : normalizeNumber(item.original_price) * normalizeNumber(item.quantity)
    const guidanceTotal = item.guidance_total_price !== undefined
      ? normalizeNumber(item.guidance_total_price)
      : normalizeNumber(item.guidance_price) * normalizeNumber(item.quantity)
    const adjustment = item.adjustment !== undefined
      ? normalizeNumber(item.adjustment)
      : originalTotal - guidanceTotal

    return {
      name: item.material_name || item.name || '材料',
      adjustment,
      originalTotal,
      aiTotal: guidanceTotal
    }
  })

  const combinedRisk = analysisItems.reduce((acc, item) => {
    const key = riskLabels[item.riskLevel] ? item.riskLevel : 'normal'
    acc[key] = (acc[key] || 0) + 1
    return acc
  }, {})

  const riskDistribution = riskOrder
    .filter(key => combinedRisk[key])
    .map(key => ({ name: riskLabels[key], value: combinedRisk[key], itemStyle: { color: riskColors[key] } }))

  const adjustmentsMerged = [...analysisItems, ...guidanceItems]
    .filter(item => Math.abs(item.adjustment) > 1e-2)
    .sort((a, b) => Math.abs(b.adjustment) - Math.abs(a.adjustment))
    .slice(0, 10)

  const adjustmentTopList = adjustmentsMerged.map(item => ({
    name: item.name,
    value: Number(item.adjustment.toFixed(2))
  }))

  const analysisTotalsOriginal = analysisItems.reduce((sum, item) => sum + item.originalTotal, 0)
  const analysisTotalsAi = analysisItems.reduce((sum, item) => sum + item.aiTotal, 0)
  const guidanceTotalsOriginal = guidanceItems.reduce((sum, item) => sum + item.originalTotal, 0)
  const guidanceTotalsAi = guidanceItems.reduce((sum, item) => sum + item.aiTotal, 0)

  const totalsComparison = {
    categories: ['无信息价材料', '市场信息价材料'],
    originalTotals: [Number(analysisTotalsOriginal.toFixed(2)), Number(guidanceTotalsOriginal.toFixed(2))],
    aiTotals: [Number(analysisTotalsAi.toFixed(2)), Number(guidanceTotalsAi.toFixed(2))]
  }

  return {
    riskDistribution: riskDistribution.length > 0 ? riskDistribution : [{ name: '正常', value: 0 }],
    adjustmentTopList,
    totalsComparison
  }
}
