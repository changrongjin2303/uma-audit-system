import { request } from '@/utils/request'

// 批量匹配项目材料
export function matchProjectMaterials(projectId, options = {}) {
  return request.post(`/matching/${projectId}/match-materials`, {
    batch_size: options.batchSize ?? 100,
    auto_match_threshold: options.autoMatchThreshold ?? 0.85,
    base_price_date: options.basePriceDate ?? null,
    base_price_province: options.basePriceProvince ?? null,
    base_price_city: options.basePriceCity ?? null,
    base_price_district: options.basePriceDistrict ?? null,
    enable_hierarchical_matching: Boolean(options.enableHierarchicalMatching)
  })
}

// 获取项目材料匹配统计信息
export function getMatchingStatistics(projectId) {
  return request.get(`/matching/${projectId}/matching-statistics`)
}

// 获取单个材料的匹配候选项
export function getMaterialMatchCandidates(materialId, topK = 10) {
  return request.get(`/matching/materials/${materialId}/match-candidates`, {
    params: { top_k: topK }
  })
}

// 确认材料匹配
export function confirmMaterialMatch(materialId, baseMaterialId, userConfirmed = true) {
  return request.post(`/matching/materials/${materialId}/confirm-match`, {}, {
    params: {
      base_material_id: baseMaterialId,
      user_confirmed: userConfirmed
    }
  })
}

// 取消材料匹配
export function unmatchMaterial(materialId) {
  return request.delete(`/matching/materials/${materialId}/match`)
}
