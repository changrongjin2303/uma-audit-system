// 测试API数据映射
const sampleApiResponse = {
  "project_id": 21,
  "results": [
    {
      "id": 139,
      "material_id": 3140,
      "status": "completed",
      "predicted_price_min": 1.2,
      "predicted_price_max": 3.5,
      "predicted_price_avg": 2.3,
      "confidence_score": 0.85,
      "is_reasonable": false,
      "price_variance": 95.6521739130435,
      "risk_level": null,
      "material_name": "双绞线缆 UTP5e",
      "specification": "",
      "unit": "m",
      "project_price": 4.5,
      "quantity": 1269.78
    }
  ],
  "total": 1
};

// 使用和前端相同的映射逻辑
const analysisResults = sampleApiResponse.results || [];
const differences = analysisResults.map(item => {
  const projectPrice = parseFloat(item.project_price || 0);
  const avgPrice = parseFloat(item.predicted_price_avg || 0);
  const unitDiff = projectPrice - avgPrice;
  const totalDiff = unitDiff * parseFloat(item.quantity || 0);
  const diffRate = avgPrice > 0 ? (unitDiff / avgPrice) : 0;
  
  return {
    material_id: item.material_id,
    material_name: item.material_name || '未知材料',
    specification: item.specification || '',
    unit: item.unit || '',
    quantity: parseFloat(item.quantity || 0),
    project_unit_price: projectPrice,
    base_unit_price: avgPrice,
    unit_price_difference: unitDiff,
    total_price_difference: totalDiff,
    price_difference_rate: diffRate,
    has_difference: !item.is_reasonable,
    difference_level: item.is_reasonable ? 'normal' : (Math.abs(diffRate) > 0.5 ? 'high' : (Math.abs(diffRate) > 0.3 ? 'medium' : 'low')),
    base_material_name: item.material_name + '（AI预测价）',
    analysis_status: item.status || 'completed'
  }
});

const totalAnalyzed = differences.length;
const totalDifferences = differences.filter(d => d.has_difference).length;
const totalDifferenceAmount = differences.reduce((sum, d) => sum + (d.total_price_difference || 0), 0);

const summary = {
  total_analyzed: totalAnalyzed,
  total_differences: totalDifferences,
  difference_rate: totalAnalyzed > 0 ? totalDifferences / totalAnalyzed : 0,
  total_difference_amount: totalDifferenceAmount,
  level_distribution: {
    normal: differences.filter(d => d.difference_level === 'normal').length,
    low: differences.filter(d => d.difference_level === 'low').length,
    medium: differences.filter(d => d.difference_level === 'medium').length,
    high: differences.filter(d => d.difference_level === 'high').length
  }
};

console.log('映射结果测试:');
console.log('数据长度:', differences.length);
console.log('第一条数据:', JSON.stringify(differences[0], null, 2));
console.log('统计摘要:', JSON.stringify(summary, null, 2));