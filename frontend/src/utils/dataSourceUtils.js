const DEFAULT_NOTE = '注：电商平台价格多为"参考价"或起批价，需要甄别是否含税、是否国标；中标价最贴近真实市场成交水平。'

const RELIABILITY_TEXT_MAPPING = [
  { keywords: ['极高', '五星', '5星', '★★★★★'], value: 5 },
  { keywords: ['较高', '★★★★'], value: 4 },
  { keywords: ['中等', '★★★'], value: 3 },
  { keywords: ['较低', '★★'], value: 2 },
  { keywords: ['低', '★'], value: 1 }
]

const normalizeString = (value) => {
  if (value === null || value === undefined) {
    return ''
  }
  return String(value).trim()
}

const formatDataCount = (value) => {
  const text = normalizeString(value)
  if (!text) {
    return '—'
  }
  if (/条|笔|家|份|项/.test(text)) {
    return text
  }
  if (!Number.isNaN(Number(text))) {
    return `${text}条`
  }
  return text
}

const formatTimeliness = (value) => {
  const text = normalizeString(value)
  return text || '—'
}

const formatPriceReference = (value) => {
  if (value === null || value === undefined || value === '') {
    return ''
  }
  if (typeof value === 'number') {
    return `参考价 ¥${value.toFixed(2)}`
  }
  const text = String(value).trim()
  if (!text) {
    return ''
  }
  if (text.startsWith('参考价')) {
    return text
  }
  return `参考价 ${text}`
}

const formatPriceRange = (minPrice, maxPrice) => {
  // 处理数字类型
  const min = typeof minPrice === 'number' ? minPrice : parseFloat(minPrice)
  const max = typeof maxPrice === 'number' ? maxPrice : parseFloat(maxPrice)
  
  // 如果两个值都无效，返回空字符串
  if (isNaN(min) && isNaN(max)) {
    return '—'
  }
  
  // 如果只有一个值有效
  if (isNaN(min) && !isNaN(max)) {
    return `≤ ¥${max.toFixed(2)}`
  }
  if (!isNaN(min) && isNaN(max)) {
    return `≥ ¥${min.toFixed(2)}`
  }
  
  // 如果两个值都有效
  if (min === max) {
    return `¥${min.toFixed(2)}`
  }
  
  return `¥${min.toFixed(2)} ~ ¥${max.toFixed(2)}`
}

const deduplicateSources = (sources) => {
  const seen = new Set()
  return sources.filter(source => {
    if (!source) {
      return false
    }
    const key = `${source.source_type || ''}__${source.platform_examples || ''}`
    if (seen.has(key)) {
      return false
    }
    seen.add(key)
    return true
  })
}

const parseReliabilityValue = (text, fallbackScore) => {
  if (typeof fallbackScore === 'number' && !Number.isNaN(fallbackScore)) {
    return Math.max(0, Math.min(5, fallbackScore))
  }

  const normalized = normalizeString(text)
  if (!normalized) {
    return null
  }

  const starMatches = normalized.match(/★/g)
  const halfMatches = normalized.match(/☆/g)
  if (starMatches) {
    let value = starMatches.length
    if (halfMatches && halfMatches.length > 0 && value < 5) {
      // Treat presence of hollow star at end as half rating if string contains ".5" hint
      if (/0\.5|半/.test(normalized)) {
        value += 0.5
      }
    }
    return Math.max(0, Math.min(5, value))
  }

  const numericMatch = normalized.match(/(\d+(?:\.\d+)?)/)
  if (numericMatch) {
    const num = parseFloat(numericMatch[1])
    if (num <= 5) {
      return num
    }
    if (num <= 100) {
      return Math.round((num / 20) * 10) / 10
    }
  }

  for (const item of RELIABILITY_TEXT_MAPPING) {
    if (item.keywords.some(keyword => normalized.includes(keyword))) {
      return item.value
    }
  }

  return null
}

const normalizeEntryObject = (entry) => {
  if (!entry || typeof entry !== 'object') {
    return null
  }

  const sourceType = normalizeString(
    entry.source_type || entry['source_type'] || entry.type ||
    entry['来源类型'] || entry['来源类型/类别'] || entry.category ||
    entry['类别'] || entry.name || entry.source
  ) || '未知来源'

  const platformExamples = normalizeString(
    entry.platform_examples || entry.platform || entry.examples ||
    entry.example || entry['平台/项目示例'] || entry['平台示例'] ||
    entry['平台或项目示例'] || entry['典型项目'] || entry.name || entry.source
  ) || '—'

  const dataCountValue = entry.data_count ?? entry['数据量'] ?? entry.count ?? entry.data_volume ?? entry.quantity
  const dataCount = formatDataCount(dataCountValue)

  const timeliness = formatTimeliness(
    entry.timeliness || entry['时效性'] || entry.time_range || entry.effective_date || entry.period || entry['更新时间']
  )

  const reliabilityText = normalizeString(
    entry.reliability || entry.reliability_rating || entry['可靠性评级'] ||
    entry['可靠性'] || entry.rating || entry.level
  ) || '—'

  const reliabilityScore = parseReliabilityValue(reliabilityText, entry.reliability_score)

  // 解析价格区间
  const priceRangeMin = entry.price_range_min ?? entry['price_range_min'] ?? entry['价格区间最低'] ?? entry.min_price
  const priceRangeMax = entry.price_range_max ?? entry['price_range_max'] ?? entry['价格区间最高'] ?? entry.max_price
  const priceRange = formatPriceRange(priceRangeMin, priceRangeMax)

  // 解析样本描述
  const sampleDescription = normalizeString(
    entry.sample_description || entry['sample_description'] || entry['样本描述'] || entry['样本说明']
  ) || '—'

  // 解析可选补充
  const notes = normalizeString(
    entry.notes || entry['notes'] || entry['可选补充'] || entry['备注'] || entry['补充说明']
  ) || '—'

  return {
    source_type: sourceType,
    platform_examples: platformExamples,
    data_count: dataCount,
    timeliness,
    reliability: reliabilityText,
    reliability_value: reliabilityScore,
    price_reference: formatPriceReference(entry.price || entry['参考价格']),
    price_range: priceRange,
    price_range_min: typeof priceRangeMin === 'number' ? priceRangeMin : (priceRangeMin ? parseFloat(priceRangeMin) : null),
    price_range_max: typeof priceRangeMax === 'number' ? priceRangeMax : (priceRangeMax ? parseFloat(priceRangeMax) : null),
    sample_description: sampleDescription,
    notes: notes
  }
}

const parseDataSourcePart = (segment, target) => {
  const [rawLabel, rawValue] = segment.split(/[:：]/)
  const label = normalizeString(rawLabel)
  const value = normalizeString(rawValue)

  if (!value) {
    if (!target.source_type) {
      target.source_type = label
    } else if (!target.platform_examples) {
      target.platform_examples = label
    } else if (!target.data_count) {
      target.data_count = label
    } else if (!target.timeliness) {
      target.timeliness = label
    } else if (!target.reliability) {
      target.reliability = label
    }
    return
  }

  if (/(来源|类型)/.test(label) && !target.source_type) {
    target.source_type = value
    return
  }
  if (/(平台|示例|案例|项目)/.test(label) && !target.platform_examples) {
    target.platform_examples = value
    return
  }
  if (/(量|条|笔|数量|案例数)/.test(label) && !target.data_count) {
    target.data_count = value
    return
  }
  if (/(时效|时间|周期|月份|更新)/.test(label) && !target.timeliness) {
    target.timeliness = value
    return
  }
  if (/(可靠|评级|评分|星)/.test(label) && !target.reliability) {
    target.reliability = value
    return
  }

  if (!target.platform_examples) {
    target.platform_examples = value
  } else if (!target.data_count) {
    target.data_count = value
  } else if (!target.timeliness) {
    target.timeliness = value
  } else if (!target.reliability) {
    target.reliability = value
  }
}

const normalizeEntryString = (entry) => {
  const text = normalizeString(entry)
  if (!text) {
    return null
  }

  const target = {
    source_type: '',
    platform_examples: '',
    data_count: '',
    timeliness: '',
    reliability: ''
  }

  const segments = text
    .split(/[\n\r\t\|,，；;]+/)
    .map(segment => segment.trim())
    .filter(Boolean)

  segments.forEach(segment => parseDataSourcePart(segment, target))

  target.source_type = target.source_type || segments[0] || '未知来源'
  target.platform_examples = target.platform_examples || target.source_type
  target.data_count = formatDataCount(target.data_count)
  target.timeliness = formatTimeliness(target.timeliness)
  target.reliability = normalizeString(target.reliability) || '—'

  return {
    ...target,
    reliability_value: parseReliabilityValue(target.reliability)
  }
}

const parseMarkdownTableEntries = (text) => {
  const lines = text
    .split(/\r?\n/)
    .map(line => line.trim())
    .filter(Boolean)

  const tableLines = lines.filter(line => line.includes('|'))
  if (tableLines.length < 2) {
    return []
  }

  const headerIndex = tableLines.findIndex(line => line.includes('来源') && line.includes('数据'))
  const startIndex = headerIndex !== -1 ? headerIndex : 0
  const headerCells = tableLines[startIndex]
    .split('|')
    .map(cell => normalizeString(cell))
    .filter(cell => cell && !/^[-\s]+$/.test(cell))

  if (headerCells.length < 3) {
    return []
  }

  const separatorPattern = /^[-\s]+$/
  const entries = []

  for (let i = startIndex + 1; i < tableLines.length; i += 1) {
    const line = tableLines[i]
    const cells = line
      .split('|')
      .map(cell => cell.trim())
      .filter((cell, idx, arr) => {
        if ((idx === 0 || idx === arr.length - 1) && cell === '') {
          return false
        }
        return true
      })

    if (cells.length < headerCells.length || cells.every(cell => separatorPattern.test(cell))) {
      continue
    }

    const entry = {}
    headerCells.forEach((header, idx) => {
      if (idx < cells.length) {
        entry[header] = cells[idx]
      }
    })

    if (Object.keys(entry).length > 0) {
      entries.push(entry)
    }
  }

  return entries
}

const extractFromReasoning = (reasoning) => {
  const text = normalizeString(reasoning)
  if (!text) {
    return []
  }

  const tableEntries = parseMarkdownTableEntries(text)
  if (tableEntries.length > 0) {
    return tableEntries
      .map(normalizeEntryObject)
      .filter(Boolean)
  }

  const checks = [
    { keywords: ['政府采购'], source_type: '政府采购平台', platform_examples: '中国政府采购网', reliability: '★★★★☆' },
    { keywords: ['中标'], source_type: '中标公告', platform_examples: '公共资源交易中心', reliability: '★★★★☆' },
    { keywords: ['1688', '阿里巴巴'], source_type: 'B2B电商平台', platform_examples: '阿里巴巴1688', reliability: '★★★☆☆' },
    { keywords: ['厂商', '报价'], source_type: '厂家报盘', platform_examples: '厂家直供报价', reliability: '★★★☆☆' },
    { keywords: ['行业资讯', '期刊'], source_type: '行业造价信息', platform_examples: '工程造价信息刊物', reliability: '★★★★☆' }
  ]

  const results = []

  checks.forEach(item => {
    const hasAll = item.keywords.every(keyword => text.includes(keyword))
    if (hasAll) {
      results.push({
        source_type: item.source_type,
        platform_examples: item.platform_examples,
        data_count: '—',
        timeliness: '—',
        reliability: item.reliability,
        reliability_value: parseReliabilityValue(item.reliability)
      })
    }
  })

  return results
}

const coerceSources = (sources) => {
  if (Array.isArray(sources)) {
    return sources
  }

  if (!sources) {
    return []
  }

  if (typeof sources === 'string') {
    return sources
      .split(/[\n\r]+/)
      .map(item => item.trim())
      .filter(Boolean)
  }

  if (typeof sources === 'object') {
    return [sources]
  }

  return []
}

const normalizeDataSources = (sources) => {
  return coerceSources(sources)
    .map(item => {
      if (typeof item === 'string') {
        return normalizeEntryString(item)
      }
      if (typeof item === 'object' && item !== null) {
        return normalizeEntryObject(item)
      }
      return null
    })
    .filter(Boolean)
}

export const formatAnalysisDataSources = (analysisResult) => {
  if (!analysisResult) {
    return []
  }

  const normalized = normalizeDataSources(analysisResult.data_sources)
  if (normalized.length > 0) {
    return deduplicateSources(normalized)
  }

  const reasoningText = [
    analysisResult.analysis_reasoning,
    analysisResult.ai_explanation,
    analysisResult.reasoning,
    analysisResult.raw_response?.content,
    analysisResult.api_response?.content
  ].find(text => normalizeString(text))

  if (reasoningText) {
    return deduplicateSources(extractFromReasoning(reasoningText))
  }

  return []
}


export const getDataSourceNote = (analysisResult) => {
  if (!analysisResult) {
    return ''
  }
  const note = normalizeString(analysisResult.data_source_note || analysisResult.data_sources_note)
  return note || DEFAULT_NOTE
}

export const hasDataSources = (analysisResult) => formatAnalysisDataSources(analysisResult).length > 0
