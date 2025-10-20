<template>
  <div class="system-introduction">
    <!-- 科技城市背景 -->
    <div class="city-background">
      <!-- 远景建筑群 -->
      <div class="building-layer layer-back">
        <div class="building tall-building-1"></div>
        <div class="building tall-building-2"></div>
        <div class="building tall-building-3"></div>
        <div class="building tall-building-4"></div>
        <div class="building tall-building-5"></div>
      </div>
      
      <!-- 中景建筑群 -->
      <div class="building-layer layer-mid">
        <div class="building mid-building-1"></div>
        <div class="building mid-building-2"></div>
        <div class="building mid-building-3"></div>
        <div class="building mid-building-4"></div>
        <div class="building mid-building-5"></div>
        <div class="building mid-building-6"></div>
      </div>
      
      <!-- 近景建筑群 -->
      <div class="building-layer layer-front">
        <div class="building front-building-1"></div>
        <div class="building front-building-2"></div>
        <div class="building front-building-3"></div>
        <div class="building front-building-4"></div>
      </div>
      
      <!-- 科技连线网络 -->
      <div class="tech-network">
        <div class="network-line line-1"></div>
        <div class="network-line line-2"></div>
        <div class="network-line line-3"></div>
        <div class="network-line line-4"></div>
        <div class="network-line line-5"></div>
        <div class="network-line line-6"></div>
      </div>
      
      <!-- 发光节点 -->
      <div class="glow-nodes">
        <div class="node node-1"></div>
        <div class="node node-2"></div>
        <div class="node node-3"></div>
        <div class="node node-4"></div>
        <div class="node node-5"></div>
        <div class="node node-6"></div>
        <div class="node node-7"></div>
        <div class="node node-8"></div>
      </div>
      
      <!-- 科技网格 -->
      <div class="tech-grid"></div>
    </div>

    <div class="page-header">
      <p class="page-subtitle">AI辅助审核工程结算材料价格</p>
      <h1 class="page-title">系统简介</h1>
    </div>

    <div class="introduction-grid">
      <div 
        v-for="(item, index) in introductionItems" 
        :key="index"
        class="introduction-card"
        :class="`card-${index + 1}`"
      >
        <div class="card-icon">
          <el-icon :size="24">
            <component :is="iconComponents[item.icon]" />
          </el-icon>
        </div>
        <div class="card-title">{{ item.title }}</div>
        <div class="card-content">{{ item.content }}</div>
        <div class="card-decoration"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { TrendCharts, MagicStick, OfficeBuilding, Trophy } from '@element-plus/icons-vue'

const iconComponents = {
  TrendCharts,
  MagicStick, 
  OfficeBuilding,
  Trophy
}

const introductionItems = ref([
  {
    title: '创建背景',
    content: '材料费用在工程造价中占比较高，直接影响投资决策，传统人工询价方式效率低下且容易出现偏差。随着建设项目中无信息价材料的使用日益广泛，准确高效的材料价格审核将成为审定工程结算价的关键环节。',
    icon: 'TrendCharts'
  },
  {
    title: '主要功能',
    content: '集成AI智能分析与大数据技术，实现工程结算书中材料清单的智能识别与分类，对无信息价材料进行精准价格分析和风险评估，对市场信息价材料进行快速的价格核对，并生成分析报告，有效辅助工程结算定价。',
    icon: 'MagicStick'
  },
  {
    title: '适用范围', 
    content: '本系统适用于房建、市政及其他土建工程的结算审核或施工图预算复核等场景，尤其适合包含新技术、新材料、新工艺、新服务的项目，用于辅助材料定价和合理性评估。',
    icon: 'OfficeBuilding'
  },
  {
    title: '核心优势',
    content: '通过新兴技术与传统业务深度融合，实现辅助建设项目精细化投资管控，同步提升审核工作时效和定案成果质量，并以数据溯源与证据链管理为支撑，为避免争议提供基础保障。',
    icon: 'Trophy'
  }
])
</script>

<style lang="scss" scoped>
.system-introduction {
  padding: 24px;
  min-height: 100vh;
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #e6f3ff 0%, #cce7ff 25%, #99d6ff 50%, #66c4ff 75%, #3399ff 100%);
}

// 科技城市背景
.city-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  opacity: 0.3;
}

// 建筑层级系统
.building-layer {
  position: absolute;
  bottom: 0;
  width: 100%;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  padding: 0 5%;
}

.layer-back {
  z-index: 1;
  opacity: 0.4;
  filter: blur(1px);
}

.layer-mid {
  z-index: 2;
  opacity: 0.6;
  filter: blur(0.5px);
}

.layer-front {
  z-index: 3;
  opacity: 0.8;
}

.building {
  position: relative;
  background: linear-gradient(180deg, 
    rgba(59, 130, 246, 0.8) 0%, 
    rgba(29, 78, 216, 0.9) 50%, 
    rgba(30, 58, 138, 1) 100%
  );
  border-radius: 2px 2px 0 0;
  
  // 窗户效果
  &::before {
    content: '';
    position: absolute;
    top: 5%;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: 
      repeating-linear-gradient(0deg, 
        transparent 0px, transparent 8px,
        rgba(59, 130, 246, 0.3) 8px, rgba(59, 130, 246, 0.3) 12px
      ),
      repeating-linear-gradient(90deg,
        transparent 0px, transparent 12px,
        rgba(59, 130, 246, 0.3) 12px, rgba(59, 130, 246, 0.3) 16px
      );
  }
  
  // 楼顶天线
  &::after {
    content: '';
    position: absolute;
    top: -10px;
    left: 50%;
    transform: translateX(-50%);
    width: 2px;
    height: 15px;
    background: rgba(59, 130, 246, 0.8);
    box-shadow: 0 0 4px rgba(59, 130, 246, 0.6);
  }
}

// 远景建筑
.tall-building-1 { width: 60px; height: 400px; }
.tall-building-2 { width: 80px; height: 520px; }
.tall-building-3 { width: 70px; height: 450px; }
.tall-building-4 { width: 90px; height: 380px; }
.tall-building-5 { width: 65px; height: 480px; }

// 中景建筑
.mid-building-1 { width: 75px; height: 320px; }
.mid-building-2 { width: 95px; height: 420px; }
.mid-building-3 { width: 85px; height: 360px; }
.mid-building-4 { width: 110px; height: 280px; }
.mid-building-5 { width: 70px; height: 340px; }
.mid-building-6 { width: 100px; height: 380px; }

// 近景建筑
.front-building-1 { width: 120px; height: 250px; }
.front-building-2 { width: 140px; height: 200px; }
.front-building-3 { width: 100px; height: 180px; }
.front-building-4 { width: 130px; height: 220px; }

// 科技连线网络
.tech-network {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 4;
}

.network-line {
  position: absolute;
  background: linear-gradient(45deg, 
    transparent 0%, 
    rgba(59, 130, 246, 0.6) 20%, 
    rgba(147, 197, 253, 0.8) 50%, 
    rgba(59, 130, 246, 0.6) 80%, 
    transparent 100%
  );
  animation: networkPulse 4s ease-in-out infinite;
  
  &::before {
    content: '';
    position: absolute;
    width: 100%;
    height: 100%;
    background: inherit;
    filter: blur(2px);
    opacity: 0.5;
  }
}

.line-1 {
  top: 20%;
  left: 10%;
  width: 200px;
  height: 2px;
  transform: rotate(25deg);
  animation-delay: 0s;
}

.line-2 {
  top: 40%;
  right: 15%;
  width: 180px;
  height: 2px;
  transform: rotate(-15deg);
  animation-delay: 1s;
}

.line-3 {
  top: 60%;
  left: 25%;
  width: 150px;
  height: 2px;
  transform: rotate(45deg);
  animation-delay: 2s;
}

.line-4 {
  top: 30%;
  left: 40%;
  width: 120px;
  height: 2px;
  transform: rotate(-30deg);
  animation-delay: 0.5s;
}

.line-5 {
  bottom: 35%;
  right: 25%;
  width: 160px;
  height: 2px;
  transform: rotate(20deg);
  animation-delay: 1.5s;
}

.line-6 {
  top: 45%;
  left: 55%;
  width: 140px;
  height: 2px;
  transform: rotate(-40deg);
  animation-delay: 2.5s;
}

@keyframes networkPulse {
  0%, 100% { 
    opacity: 0.3;
    transform: scale(1) rotate(var(--rotation, 0deg));
  }
  50% { 
    opacity: 1;
    transform: scale(1.05) rotate(var(--rotation, 0deg));
  }
}

// 发光节点
.glow-nodes {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 5;
}

.node {
  position: absolute;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: radial-gradient(circle, 
    rgba(59, 130, 246, 1) 0%, 
    rgba(59, 130, 246, 0.8) 30%, 
    rgba(59, 130, 246, 0.4) 70%, 
    transparent 100%
  );
  box-shadow: 
    0 0 10px rgba(59, 130, 246, 0.8),
    0 0 20px rgba(59, 130, 246, 0.4),
    0 0 30px rgba(59, 130, 246, 0.2);
  animation: nodeGlow 3s ease-in-out infinite;
}

.node-1 { top: 25%; left: 15%; animation-delay: 0s; }
.node-2 { top: 35%; right: 20%; animation-delay: 0.5s; }
.node-3 { top: 55%; left: 30%; animation-delay: 1s; }
.node-4 { top: 45%; right: 30%; animation-delay: 1.5s; }
.node-5 { bottom: 40%; left: 45%; animation-delay: 2s; }
.node-6 { top: 65%; right: 15%; animation-delay: 2.5s; }
.node-7 { top: 15%; left: 60%; animation-delay: 3s; }
.node-8 { bottom: 25%; right: 40%; animation-delay: 0.3s; }

@keyframes nodeGlow {
  0%, 100% { 
    transform: scale(1);
    opacity: 0.6;
  }
  50% { 
    transform: scale(1.5);
    opacity: 1;
  }
}

// 科技网格
.tech-grid {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: 
    linear-gradient(rgba(59, 130, 246, 0.1) 1px, transparent 1px),
    linear-gradient(90deg, rgba(59, 130, 246, 0.1) 1px, transparent 1px);
  background-size: 40px 40px;
  animation: gridPulse 6s ease-in-out infinite;
  z-index: 0;
}

@keyframes gridPulse {
  0%, 100% { opacity: 0.2; }
  50% { opacity: 0.5; }
}

.page-header {
  text-align: center;
  margin-bottom: 60px;
  position: relative;
  z-index: 10;

  .page-subtitle {
    font-size: 34px;
    font-weight: 500;
    color: #64748b;
    margin: 0 0 20px 0;
    letter-spacing: 2px;
    text-align: center;
  }

  .page-title {
    font-size: 48px;
    font-weight: 800;
    color: #1e3a8a;
    margin: 0;
    letter-spacing: 3px;
    text-shadow: 0 2px 4px rgba(255, 255, 255, 0.8);
    animation: titleGlow 3s ease-in-out infinite alternate;
  }
}

@keyframes titleGlow {
  from { text-shadow: 0 2px 4px rgba(255, 255, 255, 0.8); }
  to { text-shadow: 0 2px 8px rgba(255, 255, 255, 1), 0 0 20px rgba(30, 58, 138, 0.3); }
}

.introduction-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 40px;
  max-width: 1400px;
  margin: 0 auto;
  position: relative;
  z-index: 10;
}

.introduction-card {
  position: relative;
  border-radius: 25px;
  padding: 45px 35px;
  min-height: 240px;
  display: flex;
  flex-direction: column;
  transition: all 0.6s cubic-bezier(0.23, 1, 0.320, 1);
  cursor: pointer;
  overflow: hidden;
  
  // 毛玻璃效果
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 
    0 25px 45px rgba(0, 0, 0, 0.1),
    0 0 0 1px rgba(255, 255, 255, 0.05),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);

  // 3D 效果
  transform: perspective(1000px) rotateX(0deg) rotateY(0deg);
  transform-style: preserve-3d;

  &:hover {
    transform: perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(-8px);
    box-shadow: 
      0 15px 30px rgba(0, 0, 0, 0.15),
      0 0 0 1px rgba(255, 255, 255, 0.1),
      inset 0 1px 0 rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(25px);
    -webkit-backdrop-filter: blur(25px);
  }

  // 装饰元素
  .card-decoration {
    position: absolute;
    top: 0;
    right: 0;
    width: 100px;
    height: 100px;
    background: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, transparent 70%);
    border-radius: 0 25px 0 100px;
    pointer-events: none;
  }

  .card-icon {
    position: absolute;
    top: 25px;
    right: 25px;
    width: 60px;
    height: 60px;
    border-radius: 16px;
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(147, 197, 253, 0.25) 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(59, 130, 246, 0.2);
    transition: all 0.3s ease;
    box-shadow: 
      0 4px 12px rgba(59, 130, 246, 0.1),
      inset 0 1px 0 rgba(255, 255, 255, 0.1);
    
    .el-icon {
      color: rgba(30, 58, 138, 0.8);
      transition: all 0.3s ease;
    }
  }

  &:hover .card-icon {
    transform: scale(1.1);
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.25) 0%, rgba(147, 197, 253, 0.35) 100%);
    border-color: rgba(59, 130, 246, 0.3);
    box-shadow: 
      0 6px 20px rgba(59, 130, 246, 0.2),
      inset 0 1px 0 rgba(255, 255, 255, 0.2);
    
    .el-icon {
      color: rgba(30, 58, 138, 1);
      transform: scale(1.1);
    }
  }

  .card-title {
    font-size: 26px;
    font-weight: 700;
    color: #1f2937;
    margin-bottom: 24px;
    margin-top: 0;
    line-height: 1.2;
    text-shadow: 0 1px 2px rgba(255,255,255,0.5);
    position: relative;
    z-index: 2;
  }

  .card-content {
    font-size: 18px;
    line-height: 1.8;
    color: #374151;
    flex: 1;
    text-align: justify;
    letter-spacing: 0.5px;
    text-shadow: 0 1px 2px rgba(255,255,255,0.3);
    position: relative;
    z-index: 2;
    text-indent: 2em;
  }
}

// 移除自动浮动，卡片默认静止

// 响应式设计
@media (max-width: 1024px) {
  .introduction-grid {
    grid-template-columns: 1fr;
    gap: 35px;
    max-width: 700px;
  }
  
  .page-header .page-subtitle {
    font-size: 30px;
    margin-bottom: 18px;
  }

  .page-header .page-title {
    font-size: 40px;
  }
  
  .introduction-card {
    min-height: 210px;
    padding: 32px 28px;
  }
}

@media (max-width: 768px) {
  .system-introduction {
    padding: 16px;
  }

  .page-header {
    margin-bottom: 50px;

    .page-subtitle {
      font-size: 26px;
      margin-bottom: 15px;
    }

    .page-title {
      font-size: 32px;
      letter-spacing: 2px;
    }
  }

  .introduction-grid {
    gap: 25px;
  }

  .introduction-card {
    padding: 25px 20px;
    min-height: 170px;

    .card-icon {
      width: 50px;
      height: 50px;
      top: 20px;
      right: 20px;
      font-size: 24px;
    }

    .card-title {
      font-size: 22px;
      margin-bottom: 20px;
    }

    .card-content {
      font-size: 17px;
      line-height: 1.7;
    }
  }

  .city-background {
    opacity: 0.2;
  }
  
  .building {
    transform: scale(0.7);
  }
  
  .network-line {
    width: 80% !important;
  }
  
  .node {
    width: 6px;
    height: 6px;
  }
}

@media (max-width: 480px) {
  .page-header .page-title {
    font-size: 28px;
    letter-spacing: 1px;
  }

  .introduction-card {
    padding: 20px 16px;
    min-height: 160px;

    .card-title {
      font-size: 20px;
      margin-bottom: 18px;
    }

    .card-content {
      font-size: 16px;
    }
  }
}

// 深色主题支持（保持毛玻璃效果）
.dark {
  .system-introduction {
    background: linear-gradient(135deg, #000000 0%, #1a1a2e 25%, #16213e 50%, #0f3460 75%, #533483 100%);
  }

  .city-background {
    opacity: 0.4;
    
    .building {
      background: linear-gradient(180deg, 
        rgba(79, 172, 254, 0.9) 0%, 
        rgba(59, 130, 246, 1) 50%, 
        rgba(37, 99, 235, 1) 100%
      );
      
      &::before {
        background-image: 
          repeating-linear-gradient(0deg, 
            transparent 0px, transparent 8px,
            rgba(147, 197, 253, 0.4) 8px, rgba(147, 197, 253, 0.4) 12px
          ),
          repeating-linear-gradient(90deg,
            transparent 0px, transparent 12px,
            rgba(147, 197, 253, 0.4) 12px, rgba(147, 197, 253, 0.4) 16px
          );
      }
      
      &::after {
        background: rgba(147, 197, 253, 1);
        box-shadow: 0 0 6px rgba(147, 197, 253, 0.8);
      }
    }
    
    .network-line {
      background: linear-gradient(45deg, 
        transparent 0%, 
        rgba(147, 197, 253, 0.8) 20%, 
        rgba(59, 130, 246, 1) 50%, 
        rgba(147, 197, 253, 0.8) 80%, 
        transparent 100%
      );
    }
    
    .node {
      background: radial-gradient(circle, 
        rgba(147, 197, 253, 1) 0%, 
        rgba(59, 130, 246, 0.9) 30%, 
        rgba(59, 130, 246, 0.5) 70%, 
        transparent 100%
      );
      box-shadow: 
        0 0 12px rgba(147, 197, 253, 0.9),
        0 0 24px rgba(59, 130, 246, 0.5),
        0 0 36px rgba(59, 130, 246, 0.3);
    }
    
    .tech-grid {
      background-image: 
        linear-gradient(rgba(147, 197, 253, 0.2) 1px, transparent 1px),
        linear-gradient(90deg, rgba(147, 197, 253, 0.2) 1px, transparent 1px);
    }
  }

  .introduction-card {
    background: rgba(0, 0, 0, 0.4);
    backdrop-filter: blur(25px);
    -webkit-backdrop-filter: blur(25px);
    border: 1px solid rgba(147, 197, 253, 0.2);
    
    &:hover {
      background: rgba(0, 0, 0, 0.3);
      backdrop-filter: blur(30px);
      -webkit-backdrop-filter: blur(30px);
      border: 1px solid rgba(147, 197, 253, 0.3);
    }
    
    .card-icon {
      background: linear-gradient(135deg, rgba(147, 197, 253, 0.2) 0%, rgba(59, 130, 246, 0.3) 100%);
      border-color: rgba(147, 197, 253, 0.3);
      
      .el-icon {
        color: rgba(147, 197, 253, 0.9);
      }
      
      &:hover {
        background: linear-gradient(135deg, rgba(147, 197, 253, 0.3) 0%, rgba(59, 130, 246, 0.4) 100%);
        border-color: rgba(147, 197, 253, 0.4);
        
        .el-icon {
          color: rgba(147, 197, 253, 1);
        }
      }
    }
  }
}
</style>