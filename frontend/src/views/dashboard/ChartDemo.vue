<template>
  <div class="workflow-page">
    <div class="page-header">
      <h1 class="page-title">系统操作流程</h1>
      <p class="page-subtitle"></p>
    </div>

    <!-- 用户自定义Mermaid流程图 -->
    <div class="mermaid-workflow">
      <div class="mermaid-card">
        <div class="mermaid-header">
          <h2 class="mermaid-title">送审材料价格智能识别与分析流程概览</h2>
        </div>
        
        <div class="legend">
          <span><span class="dot step-dot"></span>起止/处理节点</span>
          <span><span class="dot data-dot"></span>数据/清单</span>
          <span><span class="dot decision-dot"></span>判断/对比</span>
          <span><span class="dot result-dot"></span>结果/输出</span>
        </div>
        
        <div class="flow-wrapper">
          <div ref="mermaidRef" class="mermaid">
            <!-- Mermaid图表将通过JavaScript渲染到这里 -->
          </div>
        </div>
      </div>
    </div>


    <div class="workflow-container">
      <!-- 阶段1：数据输入 -->
      <div class="workflow-stage" data-stage="1">
        <div class="stage-card input-stage">
          <div class="stage-header">
            <div class="stage-number">01</div>
            <div class="stage-info">
              <h3 class="stage-title">数据输入阶段</h3>
              <p class="stage-desc">准备项目材料清单和基准数据库</p>
            </div>
            <div class="stage-icon">
              <el-icon><Upload /></el-icon>
            </div>
          </div>
          
          <div class="stage-content">
            <div class="content-section">
              <h4 class="section-title">
                <el-icon><DocumentAdd /></el-icon>
                输入资料
              </h4>
              <ul class="content-list">
                <li>项目材料清单Excel文件</li>
                <li>基准材料价格数据库</li>
                <li>政府信息价数据</li>
                <li>市场价格参考数据</li>
              </ul>
            </div>
            
            <div class="content-section">
              <h4 class="section-title">
                <el-icon><Setting /></el-icon>
                处理过程
              </h4>
              <ul class="content-list">
                <li>Excel文件解析和验证</li>
                <li>数据格式标准化</li>
                <li>数据质量检查和清洗</li>
                <li>材料信息结构化存储</li>
              </ul>
            </div>
            
            <div class="content-section">
              <h4 class="section-title">
                <el-icon><SuccessFilled /></el-icon>
                输出结果
              </h4>
              <ul class="content-list">
                <li>标准化项目材料清单</li>
                <li>完整基准材料数据库</li>
                <li>数据质量报告</li>
                <li>待分析材料列表</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <!-- 流程箭头 -->
      <div class="workflow-arrow">
        <div class="arrow-line"></div>
        <div class="arrow-head">
          <el-icon><ArrowDown /></el-icon>
        </div>
        <div class="arrow-text">智能匹配</div>
      </div>

      <!-- 阶段2：智能识别 -->
      <div class="workflow-stage" data-stage="2">
        <div class="stage-card recognition-stage">
          <div class="stage-header">
            <div class="stage-number">02</div>
            <div class="stage-info">
              <h3 class="stage-title">智能识别阶段</h3>
              <p class="stage-desc">运用AI算法智能识别和匹配材料</p>
            </div>
            <div class="stage-icon">
              <el-icon><Search /></el-icon>
            </div>
          </div>
          
          <div class="stage-content">
            <div class="content-section">
              <h4 class="section-title">
                <el-icon><DataBoard /></el-icon>
                输入资料
              </h4>
              <ul class="content-list">
                <li>项目材料清单数据</li>
                <li>基准材料数据库</li>
                <li>材料规格参数</li>
                <li>历史匹配记录</li>
              </ul>
            </div>
            
            <div class="content-section">
              <h4 class="section-title">
                <el-icon><MagicStick /></el-icon>
                处理过程
              </h4>
              <ul class="content-list">
                <li>多维度相似度算法计算</li>
                <li>材料名称智能匹配</li>
                <li>规格参数对比分析</li>
                <li>机器学习模型识别</li>
              </ul>
            </div>
            
            <div class="content-section">
              <h4 class="section-title">
                <el-icon><Select /></el-icon>
                输出结果
              </h4>
              <ul class="content-list">
                <li>市场信息价材料清单（已匹配）</li>
                <li>无信息价材料清单（待分析）</li>
                <li>匹配置信度评分</li>
                <li>异常材料提示</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <!-- 流程箭头 -->
      <div class="workflow-arrow">
        <div class="arrow-line"></div>
        <div class="arrow-head">
          <el-icon><ArrowDown /></el-icon>
        </div>
        <div class="arrow-text">AI分析</div>
      </div>

      <!-- 阶段3：AI价格分析 -->
      <div class="workflow-stage" data-stage="3">
        <div class="stage-card analysis-stage">
          <div class="stage-header">
            <div class="stage-number">03</div>
            <div class="stage-info">
              <h3 class="stage-title">AI价格分析阶段</h3>
              <p class="stage-desc">运用多AI服务进行价格预测和合理性分析</p>
            </div>
            <div class="stage-icon">
              <el-icon><TrendCharts /></el-icon>
            </div>
          </div>
          
          <div class="stage-content">
            <div class="content-section">
              <h4 class="section-title">
                <el-icon><Box /></el-icon>
                输入资料
              </h4>
              <ul class="content-list">
                <li>无信息价材料清单</li>
                <li>材料技术参数</li>
                <li>地区价格指数</li>
                <li>市场趋势数据</li>
              </ul>
            </div>
            
            <div class="content-section">
              <h4 class="section-title">
                <el-icon><Cpu /></el-icon>
                处理过程
              </h4>
              <ul class="content-list">
                <li>多AI服务并发调用</li>
                <li>价格区间智能预测</li>
                <li>合理性统计学分析</li>
                <li>风险等级评估计算</li>
              </ul>
            </div>
            
            <div class="content-section">
              <h4 class="section-title">
                <el-icon><DataAnalysis /></el-icon>
                输出结果
              </h4>
              <ul class="content-list">
                <li>价格预测区间</li>
                <li>置信度评分</li>
                <li>风险等级分类</li>
                <li>异常价格预警</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <!-- 流程箭头 -->
      <div class="workflow-arrow">
        <div class="arrow-line"></div>
        <div class="arrow-head">
          <el-icon><ArrowDown /></el-icon>
        </div>
        <div class="arrow-text">生成报告</div>
      </div>

      <!-- 阶段4：报告生成 -->
      <div class="workflow-stage" data-stage="4">
        <div class="stage-card report-stage">
          <div class="stage-header">
            <div class="stage-number">04</div>
            <div class="stage-info">
              <h3 class="stage-title">报告生成阶段</h3>
              <p class="stage-desc">自动生成专业分析报告和分析结论</p>
            </div>
            <div class="stage-icon">
              <el-icon><Document /></el-icon>
            </div>
          </div>
          
          <div class="stage-content">
            <div class="content-section">
              <h4 class="section-title">
                <el-icon><Files /></el-icon>
                输入资料
              </h4>
              <ul class="content-list">
                <li>AI价格分析结果</li>
                <li>风险评估数据</li>
                <li>统计分析数据</li>
                <li>项目基本信息</li>
              </ul>
            </div>
            
            <div class="content-section">
              <h4 class="section-title">
                <el-icon><EditPen /></el-icon>
                处理过程
              </h4>
              <ul class="content-list">
                <li>Word报告模板填充</li>
                <li>图表自动生成</li>
                <li>统计数据汇总</li>
                <li>改进建议智能生成</li>
              </ul>
            </div>
            
            <div class="content-section">
              <h4 class="section-title">
                <el-icon><Check /></el-icon>
                最终输出
              </h4>
              <ul class="content-list">
                <li>专业分析报告（Word）</li>
                <li>价格分析图表</li>
                <li>风险材料清单</li>
                <li>审计结论和建议</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import mermaid from 'mermaid'
import {
  Upload, DocumentAdd, Setting, SuccessFilled, ArrowDown, Search,
  DataBoard, MagicStick, Select, TrendCharts, Box, Cpu, DataAnalysis,
  Document, Files, EditPen, Check, Trophy, Plus
} from '@element-plus/icons-vue'

const mermaidRef = ref()

// 初始化Mermaid
const initMermaid = async () => {
  try {
    // 清除已有内容
    if (mermaidRef.value) {
      mermaidRef.value.innerHTML = ''
    }
    
    mermaid.initialize({
      startOnLoad: false,
      theme: "base",
      themeVariables: {
        primaryColor: "#3b82f6",
        primaryTextColor: "#ffffff", 
        primaryBorderColor: "#1d4ed8",
        lineColor: "#64748b",
        secondaryColor: "#0ea5e9",
        tertiaryColor: "#10b981",
        background: "#f8fafc",
        mainBkg: "#f8fafc"
      },
      flowchart: {
        htmlLabels: true
      }
    })
    
    await nextTick()
    
    const graphDefinition = `
      flowchart LR
        classDef step fill:#3b82f6,stroke:#1d4ed8,color:#fff
        classDef data fill:#10b981,stroke:#059669,color:#fff  
        classDef decision fill:#06b6d4,stroke:#0891b2,color:#fff
        classDef result fill:#818cf8,stroke:#6366f1,color:#fff
        classDef source fill:#10b981,stroke:#059669,color:#fff

        A[创建项目]:::step --> B[设置基期信息价]:::step
        B --> C[Excel上传项目报审材料清单]:::data
        S[系统内置市场信息价材料库]:::source --> E[数据解析/类型验证处理]:::step
        C --> E

        E --> F[材料识别/智能匹配分析]:::step
        F --> G[无信息价材料清单]:::data
        F --> H[市场信息价材料清单]:::data

        G --> I{AI对比分析价格}:::decision
        M[市场价大数据]:::source --> I
        I --> K[无信息价材料分析结果]:::result

        H --> J{AI对比分析价格}:::decision
        J --> N[市场信息价材料分析结果]:::result

        K --> Z[分析报告]:::result
        N --> Z
    `
    
    if (mermaidRef.value) {
      const { svg } = await mermaid.render('mermaid-flow', graphDefinition)
      mermaidRef.value.innerHTML = svg
    }
  } catch (error) {
    console.error('Mermaid initialization error:', error)
    // 降级处理，显示简单提示
    if (mermaidRef.value) {
      mermaidRef.value.innerHTML = '<p style="color: #94a3b8; text-align: center; padding: 40px;">流程图正在加载...</p>'
    }
  }
}

// 添加滚动动画效果
const observeStages = () => {
  const stages = document.querySelectorAll('.workflow-stage')
  const arrows = document.querySelectorAll('.workflow-arrow')
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('animate-in')
      }
    })
  }, { threshold: 0.3 })

  stages.forEach(stage => observer.observe(stage))
  arrows.forEach(arrow => observer.observe(arrow))
}

onMounted(() => {
  nextTick(() => {
    initMermaid()
    observeStages()
  })
})
</script>

<style lang="scss" scoped>
.workflow-page {
  padding: 24px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: calc(100vh - 60px);
}

// Mermaid 流程图样式
.mermaid-workflow {
  margin-bottom: 40px;
  padding: 0 24px;
}

.mermaid-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.mermaid-header {
  text-align: center;
  margin-bottom: 25px;
  
  .mermaid-title {
    font-size: 24px;
    font-weight: 700;
    color: #1e293b;
    margin: 0;
    letter-spacing: 1px;
  }
}

.legend {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  padding: 15px 20px;
  margin-bottom: 20px;
  background: rgba(248, 250, 252, 0.8);
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  font-size: 13px;
  color: #475569;
  
  .dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 6px;
    vertical-align: -1px;
  }
  
  .step-dot {
    background: #3b82f6;
  }
  
  .data-dot {
    background: #10b981;
  }
  
  .decision-dot {
    background: #06b6d4;
  }
  
  .result-dot {
    background: #818cf8;
  }
}

.flow-wrapper {
  overflow: auto;
  -webkit-overflow-scrolling: touch;
  background: #f8fafc;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e2e8f0;
  
  .mermaid {
    min-width: 900px;
    display: flex;
    justify-content: center;
    
    svg {
      max-width: 100%;
      height: auto;
      background: transparent !important;
    }
  }
}

.workflow-container {
  margin: 0 auto;
  padding: 0 24px;
}

.workflow-stage {
  margin-bottom: 40px;
  opacity: 0;
  transform: translateY(50px);
  transition: all 0.6s ease;
  
  &.animate-in {
    opacity: 1;
    transform: translateY(0);
  }
}

.stage-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-8px);
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  }
}

.stage-header {
  display: flex;
  align-items: center;
  padding: 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  
  .stage-number {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.2);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    font-weight: bold;
    margin-right: 20px;
    border: 2px solid rgba(255, 255, 255, 0.3);
  }
  
  .stage-info {
    flex: 1;
    
    .stage-title {
      font-size: 22px;
      font-weight: 600;
      margin: 0 0 8px 0;
    }
    
    .stage-desc {
      font-size: 14px;
      opacity: 0.9;
      margin: 0;
      line-height: 1.5;
    }
  }
  
  .stage-icon {
    font-size: 36px;
    opacity: 0.8;
  }
}

// 不同阶段的颜色主题
.input-stage .stage-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.recognition-stage .stage-header {
  background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
}

.analysis-stage .stage-header {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.report-stage .stage-header {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stage-content {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 30px;
  padding: 30px;
}

.content-section {
  .section-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 16px;
    font-weight: 600;
    color: #2c3e50;
    margin: 0 0 16px 0;
    padding-bottom: 8px;
    border-bottom: 2px solid #ecf0f1;
  }
  
  .content-list {
    list-style: none;
    padding: 0;
    margin: 0;
    
    li {
      padding: 8px 0;
      font-size: 14px;
      line-height: 1.5;
      color: #34495e;
      position: relative;
      padding-left: 20px;
      
      &:before {
        content: '●';
        position: absolute;
        left: 0;
        color: #3498db;
        font-weight: bold;
      }
    }
  }
}

.workflow-arrow {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 20px 0;
  opacity: 0;
  transform: scale(0.8);
  transition: all 0.5s ease 0.2s;
  
  &.animate-in {
    opacity: 1;
    transform: scale(1);
  }
  
  .arrow-line {
    width: 4px;
    height: 40px;
    background: linear-gradient(to bottom, #3498db, #2980b9);
    border-radius: 2px;
  }
  
  .arrow-head {
    margin: -2px 0 8px 0;
    font-size: 24px;
    color: #2980b9;
    animation: bounce 2s infinite;
  }
  
  .arrow-text {
    font-size: 14px;
    color: #7f8c8d;
    font-weight: 500;
    background: white;
    padding: 4px 12px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-6px);
  }
  60% {
    transform: translateY(-3px);
  }
}

.workflow-summary {
  margin-top: 60px;
}

.summary-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  
  .summary-header {
    background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
    padding: 30px;
    text-align: center;
    
    .summary-icon {
      font-size: 48px;
      color: #e67e22;
      margin-bottom: 16px;
    }
    
    h3 {
      font-size: 24px;
      font-weight: 600;
      color: #2c3e50;
      margin: 0;
    }
  }
  
  .summary-content {
    padding: 40px 30px;
  }
}

.value-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 30px;
}

.value-item {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
  transition: all 0.3s ease;
  
  &:hover {
    background: #e3f2fd;
    transform: translateY(-2px);
  }
  
  .value-icon {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    flex-shrink: 0;
  }
  
  .value-text {
    flex: 1;
    
    h4 {
      font-size: 18px;
      font-weight: 600;
      color: #2c3e50;
      margin: 0 0 8px 0;
    }
    
    p {
      font-size: 14px;
      color: #7f8c8d;
      margin: 0;
      line-height: 1.5;
    }
  }
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
  
  .page-title {
    font-size: 32px;
    font-weight: 600;
    color: #2c3e50;
    margin: 0 0 12px 0;
    letter-spacing: 2px;
  }
  
  .page-subtitle {
    font-size: 16px;
    color: #7f8c8d;
    margin: 0;
    line-height: 1.6;
  }
}

// 横向流程图样式
.horizontal-workflow {
  margin-bottom: 40px;
  overflow-x: auto;
  padding: 20px 0;
  
  .workflow-container-horizontal {
    min-width: 1200px;
    width: fit-content;
    margin: 0 auto;
    padding: 40px;
    background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
    border-radius: 20px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    position: relative;
  }
}

// 流程层级样式
.workflow-layer {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 20px 0;
  
  &.decision-layer {
    justify-content: center;
  }
  
  &.branch-layer {
    justify-content: space-around;
    max-width: 800px;
    margin: 40px auto;
  }
  
  &.final-layer {
    justify-content: center;
    gap: 30px;
  }
}

// 工作流节点样式
.workflow-node {
  display: flex;
  flex-direction: column;
  align-items: center;
  
  // 起始节点
  &.start-node {
    .node-circle {
      width: 80px;
      height: 80px;
      border-radius: 50%;
      background: linear-gradient(135deg, #4285f4 0%, #1976d2 100%);
      color: white;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      box-shadow: 0 6px 20px rgba(66, 133, 244, 0.3);
      transition: all 0.3s ease;
      
      &:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 25px rgba(66, 133, 244, 0.4);
      }
    }
    
    .node-label {
      margin-top: 12px;
      font-size: 18px;
      font-weight: 700;
      color: #2c3e50;
      text-align: center;
    }
  }
  
  // 处理节点
  &.process-node {
    .node-box {
      width: 140px;
      padding: 16px;
      background: white;
      border: 2px solid #e3f2fd;
      border-radius: 12px;
      text-align: center;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
      transition: all 0.3s ease;
      position: relative;
      overflow: hidden;
      
      &::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        transition: all 0.3s ease;
      }
      
      &:hover {
        transform: translateY(-4px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
      }
      
      .node-title {
        font-size: 16px;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 6px;
        line-height: 1.2;
      }
      
      .node-subtitle {
        font-size: 13px;
        color: #7f8c8d;
        line-height: 1.3;
      }
      
      // 不同类型节点的颜色
      &.upload-node {
        border-color: #667eea;
        &::before { background: linear-gradient(90deg, #667eea, #764ba2); }
        &:hover { border-color: #764ba2; }
      }
      
      &.parse-node {
        border-color: #f093fb;
        &::before { background: linear-gradient(90deg, #f093fb, #f5576c); }
        &:hover { border-color: #f5576c; }
      }
      
      &.identify-node {
        border-color: #4facfe;
        &::before { background: linear-gradient(90deg, #4facfe, #00f2fe); }
        &:hover { border-color: #00f2fe; }
      }
      
      &.analysis-node {
        border-color: #ffb347;
        &::before { background: linear-gradient(90deg, #ffb347, #ff8c42); }
        &:hover { border-color: #ff8c42; }
      }
      
      &.report-node {
        border-color: #43e97b;
        &::before { background: linear-gradient(90deg, #43e97b, #38f9d7); }
        &:hover { border-color: #38f9d7; }
      }
    }
  }
  
  // 决策节点
  &.decision-node {
    .diamond-container {
      position: relative;
      width: 150px;
      height: 150px;
      
      .diamond-shape {
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, #2196f3 0%, #1565c0 100%);
        transform: rotate(45deg);
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 6px 20px rgba(33, 150, 243, 0.3);
        transition: all 0.3s ease;
        
        &:hover {
          transform: rotate(45deg) scale(1.05);
          box-shadow: 0 8px 25px rgba(33, 150, 243, 0.4);
        }
        
        .diamond-content {
          transform: rotate(-45deg);
          text-align: center;
          color: white;
          padding: 10px;
          
          .diamond-title {
            font-size: 16px;
            font-weight: 700;
            margin-bottom: 4px;
            text-shadow: 0 1px 2px rgba(0,0,0,0.1);
          }
          
          .diamond-question {
            font-size: 12px;
            opacity: 0.95;
            font-weight: 500;
            line-height: 1.2;
          }
        }
      }
    }
  }
}

// 箭头样式
.workflow-arrow {
  display: flex;
  align-items: center;
  margin: 0 15px;
  
  &.right-arrow {
    .arrow-line {
      width: 40px;
      height: 3px;
      background: linear-gradient(90deg, #4285f4, #1976d2);
      border-radius: 2px;
      margin-right: 5px;
      transition: all 0.3s ease;
    }
    
    .arrow-tip {
      font-size: 16px;
      color: #1976d2;
      transition: all 0.3s ease;
      animation: arrow-pulse 2s infinite;
    }
    
    &:hover {
      .arrow-line {
        background: linear-gradient(90deg, #1976d2, #0d47a1);
        width: 45px;
      }
      
      .arrow-tip {
        color: #0d47a1;
        transform: scale(1.2);
      }
    }
  }
}

// 向下箭头
.workflow-down-arrow {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 20px 0;
  
  .down-arrow-line {
    width: 3px;
    height: 30px;
    background: linear-gradient(180deg, #4285f4, #1976d2);
    border-radius: 2px;
    margin-bottom: 5px;
    transition: all 0.3s ease;
  }
  
  .down-arrow-tip {
    font-size: 16px;
    color: #1976d2;
    transition: all 0.3s ease;
    animation: arrow-bounce 2s infinite;
  }
  
  &:hover {
    .down-arrow-line {
      background: linear-gradient(180deg, #1976d2, #0d47a1);
      height: 35px;
    }
    
    .down-arrow-tip {
      color: #0d47a1;
      transform: scale(1.2);
    }
  }
}

@keyframes arrow-pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.1);
  }
}

@keyframes arrow-bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-3px);
  }
  60% {
    transform: translateY(-1px);
  }
}

// 分支箭头容器
.branch-arrows-container {
  display: flex;
  justify-content: space-around;
  width: 600px;
  margin: 20px auto;
  position: relative;
  
  .branch-arrow {
    display: flex;
    flex-direction: column;
    align-items: center;
    
    &.left-branch-arrow {
      .left-line {
        width: 2px;
        height: 40px;
        background: linear-gradient(135deg, #4285f4, #1976d2);
        transform: rotate(-45deg);
        margin-bottom: 10px;
        transition: all 0.3s ease;
      }
      
      .left-tip {
        font-size: 18px;
        color: #1976d2;
        margin-bottom: 5px;
        animation: branch-glow 2s infinite alternate;
      }
    }
    
    &.right-branch-arrow {
      .right-line {
        width: 2px;
        height: 40px;
        background: linear-gradient(135deg, #4285f4, #1976d2);
        transform: rotate(45deg);
        margin-bottom: 10px;
        transition: all 0.3s ease;
      }
      
      .right-tip {
        font-size: 18px;
        color: #1976d2;
        margin-bottom: 5px;
        animation: branch-glow 2s infinite alternate;
      }
    }
    
    .branch-text {
      font-size: 12px;
      font-weight: 600;
      color: #4285f4;
      background: rgba(66, 133, 244, 0.1);
      padding: 2px 8px;
      border-radius: 10px;
      border: 1px solid rgba(66, 133, 244, 0.2);
    }
  }
}

@keyframes branch-glow {
  from {
    opacity: 0.8;
  }
  to {
    opacity: 1;
    text-shadow: 0 0 6px rgba(25, 118, 210, 0.3);
  }
}

// 分支处理区域
.branch-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 300px;
  
  .branch-header {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 16px;
    border-radius: 20px;
    margin-bottom: 15px;
    font-weight: 700;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
    
    &.green-header {
      background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
      color: #155724;
      border: 1px solid #c3e6cb;
      
      .check-icon {
        font-size: 16px;
        font-weight: 900;
      }
      
      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(21, 87, 36, 0.2);
      }
    }
    
    &.blue-header {
      background: linear-gradient(135deg, #cce7ff 0%, #b3d9ff 100%);
      color: #0056b3;
      border: 1px solid #b3d9ff;
      
      .tools-icon {
        font-size: 16px;
        font-weight: 900;
      }
      
      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 86, 179, 0.2);
      }
    }
  }
  
  .branch-process {
    .process-box {
      width: 260px;
      padding: 20px;
      border-radius: 12px;
      text-align: center;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
      transition: all 0.3s ease;
      
      &:hover {
        transform: translateY(-4px);
        box-shadow: 0 6px 24px rgba(0, 0, 0, 0.12);
      }
      
      .process-title {
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 6px;
        line-height: 1.2;
      }
      
      .process-subtitle {
        font-size: 14px;
        margin-bottom: 12px;
        opacity: 0.8;
        line-height: 1.3;
      }
      
      .process-details {
        .detail-line {
          font-size: 13px;
          text-align: left;
          margin-bottom: 4px;
          opacity: 0.9;
          line-height: 1.3;
        }
      }
      
      &.green-box {
        background: linear-gradient(135deg, #f0f9f0 0%, #e8f5e8 100%);
        color: #2d5a2d;
        border: 2px solid #c3e6cb;
        
        .process-title {
          color: #155724;
        }
      }
      
      &.blue-box {
        background: linear-gradient(135deg, #f0f8ff 0%, #e6f3ff 100%);
        color: #003d82;
        border: 2px solid #b3d9ff;
        
        .process-title {
          color: #0056b3;
        }
      }
    }
  }
}

// 汇聚箭头容器
.merge-arrows-container {
  display: flex;
  justify-content: center;
  gap: 100px;
  margin: 30px 0;
  
  .merge-arrow {
    display: flex;
    flex-direction: column;
    align-items: center;
    
    &.left-merge {
      .left-merge-line {
        width: 2px;
        height: 50px;
        background: linear-gradient(135deg, #4285f4, #1976d2);
        transform: rotate(45deg);
        margin-bottom: 10px;
      }
    }
    
    &.right-merge {
      .right-merge-line {
        width: 2px;
        height: 50px;
        background: linear-gradient(135deg, #4285f4, #1976d2);
        transform: rotate(-45deg);
        margin-bottom: 10px;
      }
    }
    
    .merge-tip {
      font-size: 18px;
      color: #1976d2;
      animation: merge-pulse 2s infinite alternate;
    }
  }
}

@keyframes merge-pulse {
  from {
    opacity: 0.8;
  }
  to {
    opacity: 1;
    text-shadow: 0 0 6px rgba(25, 118, 210, 0.3);
  }
}




// 汇聚处理样式
.flow-merge-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
  margin: 30px 0;
}

.merge-arrows {
  display: flex;
  gap: 40px;
  margin-bottom: 10px;
  
  .merge-arrow {
    font-size: 20px;
    color: #1976d2;
    font-weight: 900;
    text-shadow: 0 1px 2px rgba(25, 118, 210, 0.2);
    animation: merge-glow 2s ease-in-out infinite alternate;
  }
  
@keyframes merge-glow {
  from {
    opacity: 0.8;
  }
  to {
    opacity: 1;
    text-shadow: 0 1px 2px rgba(25, 118, 210, 0.3), 0 0 8px rgba(25, 118, 210, 0.2);
  }
}
}

.merge-label {
  font-size: 13px;
  color: #1976d2;
  font-weight: 600;
  margin-bottom: 15px;
  padding: 6px 16px;
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  border-radius: 20px;
  border: 1px solid #bbdefb;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  box-shadow: 0 2px 6px rgba(25, 118, 210, 0.1);
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 10px rgba(25, 118, 210, 0.2);
  }
}

.reasonability-node {
  background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
  border: 2px solid #ffb300;
  border-radius: 12px;
  padding: 16px 24px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(255, 179, 0, 0.2), 0 1px 4px rgba(255, 179, 0, 0.1);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, rgba(255,255,255,0.5) 0%, rgba(255,255,255,0.2) 100%);
    opacity: 0;
    transition: opacity 0.3s ease;
  }
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(255, 179, 0, 0.3), 0 2px 6px rgba(255, 179, 0, 0.15);
    
    &::before {
      opacity: 1;
    }
  }
  
  .node-title {
    font-size: 17px;
    font-weight: 700;
    color: #e65100;
    margin-bottom: 4px;
    text-shadow: 0 1px 2px rgba(230, 81, 0, 0.1);
    position: relative;
    z-index: 1;
  }
  
  .node-desc {
    font-size: 14px;
    color: #f57c00;
    font-weight: 500;
    position: relative;
    z-index: 1;
  }
}


// 响应式设计 - 平板
@media (max-width: 1024px) {
  .horizontal-workflow {
    .workflow-container-horizontal {
      min-width: 900px;
      padding: 30px 20px;
    }
  }
  
  .workflow-node.process-node .node-box {
    width: 120px;
    padding: 12px;
    
    .node-title {
      font-size: 12px;
    }
    
    .node-subtitle {
      font-size: 10px;
    }
  }
  
  .workflow-node.start-node {
    .node-circle {
      width: 70px;
      height: 70px;
      font-size: 20px;
    }
    
    .node-label {
      font-size: 14px;
    }
  }
  
  .workflow-node.decision-node .diamond-container {
    width: 120px;
    height: 120px;
    
    .diamond-shape .diamond-content {
      .diamond-title {
        font-size: 12px;
      }
      
      .diamond-question {
        font-size: 9px;
      }
    }
  }
  
  .branch-section {
    width: 250px;
    
    .branch-process .process-box {
      width: 220px;
      padding: 16px;
      
      .process-title {
        font-size: 14px;
      }
      
      .process-subtitle {
        font-size: 11px;
      }
      
      .process-details .detail-line {
        font-size: 10px;
      }
    }
  }
}

// 响应式设计 - 手机
@media (max-width: 768px) {
  .workflow-page {
    padding: 16px;
  }
  
  .workflow-container {
    padding: 0 16px;
  }
  
  .page-header {
    margin-bottom: 30px;
    
    .page-title {
      font-size: 24px;
      letter-spacing: 1px;
    }
  }
  
  .horizontal-workflow {
    // 在手机端改为垂直布局
    .workflow-container-horizontal {
      min-width: auto;
      width: 100%;
      padding: 20px 15px;
      
      // 重新安排为垂直流程
      .workflow-layer {
        flex-direction: column;
        gap: 15px;
        
        &.branch-layer {
          flex-direction: column;
          gap: 30px;
          max-width: 100%;
          margin: 30px auto;
        }
        
        &.final-layer {
          flex-direction: column;
          gap: 15px;
        }
      }
      
      // 横向箭头改为垂直
      .workflow-arrow.right-arrow {
        transform: rotate(90deg);
        margin: 10px 0;
        
        .arrow-line {
          width: 3px;
          height: 25px;
        }
        
        .arrow-tip {
          transform: rotate(90deg);
          font-size: 14px;
        }
      }
    }
  }
  
  .workflow-node {
    &.start-node {
      .node-circle {
        width: 60px;
        height: 60px;
        font-size: 18px;
      }
      
      .node-label {
        font-size: 14px;
      }
    }
    
    &.process-node .node-box {
      width: 200px;
      padding: 16px;
      
      .node-title {
        font-size: 13px;
      }
      
      .node-subtitle {
        font-size: 11px;
      }
    }
    
    &.decision-node .diamond-container {
      width: 100px;
      height: 100px;
      
      .diamond-shape .diamond-content {
        .diamond-title {
          font-size: 10px;
        }
        
        .diamond-question {
          font-size: 8px;
        }
      }
    }
  }
  
  // 分支箭头调整
  .branch-arrows-container {
    width: 300px;
    
    .branch-arrow {
      .left-line,
      .right-line {
        height: 30px;
      }
      
      .left-tip,
      .right-tip {
        font-size: 14px;
      }
      
      .branch-text {
        font-size: 11px;
      }
    }
  }
  
  // 分支区域调整
  .branch-section {
    width: 280px;
    
    .branch-header {
      font-size: 12px;
      padding: 6px 12px;
      
      .check-icon,
      .tools-icon {
        font-size: 14px;
      }
    }
    
    .branch-process .process-box {
      width: 260px;
      padding: 16px;
      
      .process-title {
        font-size: 14px;
      }
      
      .process-subtitle {
        font-size: 11px;
      }
      
      .process-details .detail-line {
        font-size: 10px;
      }
    }
  }
  
  // 汇聚箭头调整
  .merge-arrows-container {
    gap: 60px;
    
    .merge-arrow {
      .left-merge-line,
      .right-merge-line {
        height: 40px;
      }
      
      .merge-tip {
        font-size: 16px;
      }
    }
  }
  
  // 向下箭头调整
  .workflow-down-arrow {
    .down-arrow-line {
      height: 25px;
    }
    
    .down-arrow-tip {
      font-size: 14px;
    }
  }
}

// Mermaid 响应式设计
@media (max-width: 1024px) {
  .mermaid-card {
    padding: 20px;
  }
  
  .legend {
    gap: 15px;
    font-size: 12px;
  }
  
  .flow-wrapper {
    padding: 15px;
    
    .mermaid {
      min-width: 700px;
    }
  }
}

@media (max-width: 768px) {
  .mermaid-workflow {
    margin-bottom: 30px;
    padding: 0 16px;
  }
  
  .mermaid-header {
    .mermaid-title {
      font-size: 20px;
    }
    
    .mermaid-subtitle {
      font-size: 13px;
    }
  }
  
  .mermaid-card {
    padding: 16px;
  }
  
  .legend {
    gap: 12px;
    font-size: 11px;
    flex-direction: column;
    
    > span {
      display: flex;
      align-items: center;
    }
  }
  
  .flow-wrapper {
    padding: 12px;
    
    .mermaid {
      min-width: 600px;
    }
  }
}

// 响应式设计 - 小屏手机
@media (max-width: 480px) {
  .page-header .page-title {
    font-size: 20px;
    letter-spacing: 0.5px;
  }
  
  .mermaid-workflow {
    padding: 0 12px;
  }
  
  .workflow-container {
    padding: 0 12px;
  }
  
  .horizontal-workflow .workflow-container-horizontal {
    padding: 15px 10px;
  }
  
  .workflow-node {
    &.start-node {
      .node-circle {
        width: 50px;
        height: 50px;
        font-size: 16px;
      }
      
      .node-label {
        font-size: 12px;
      }
    }
    
    &.process-node .node-box {
      width: 180px;
      padding: 12px;
      
      .node-title {
        font-size: 12px;
      }
      
      .node-subtitle {
        font-size: 10px;
      }
    }
    
    &.decision-node .diamond-container {
      width: 90px;
      height: 90px;
      
      .diamond-shape .diamond-content {
        .diamond-title {
          font-size: 9px;
        }
        
        .diamond-question {
          font-size: 7px;
        }
      }
    }
  }
  
  .branch-arrows-container {
    width: 250px;
    
    .branch-arrow {
      .left-line,
      .right-line {
        height: 25px;
      }
      
      .left-tip,
      .right-tip {
        font-size: 12px;
      }
      
      .branch-text {
        font-size: 10px;
      }
    }
  }
  
  .branch-section {
    width: 240px;
    
    .branch-header {
      font-size: 11px;
      padding: 5px 10px;
      
      .check-icon,
      .tools-icon {
        font-size: 12px;
      }
    }
    
    .branch-process .process-box {
      width: 220px;
      padding: 14px;
      
      .process-title {
        font-size: 13px;
      }
      
      .process-subtitle {
        font-size: 10px;
      }
      
      .process-details .detail-line {
        font-size: 9px;
      }
    }
  }
  
  .merge-arrows-container {
    gap: 50px;
    
    .merge-arrow {
      .left-merge-line,
      .right-merge-line {
        height: 35px;
      }
      
      .merge-tip {
        font-size: 14px;
      }
    }
  }
}
</style>