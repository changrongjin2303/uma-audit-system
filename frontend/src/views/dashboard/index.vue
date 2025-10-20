<template>
  <div class="dashboard-container">
    <!-- 欢迎横幅 -->
    <div class="dashboard-header">
      <div class="welcome-content">
        <div class="welcome-text">
          <h1 class="welcome-title">
            欢迎回来，{{ userStore.displayName }}！
          </h1>
          <p class="welcome-subtitle">
            今天是 {{ formatDate(new Date()) }}，{{ greetingText }}
          </p>
        </div>
        <div class="welcome-avatar">
          <el-avatar :size="80" :src="userStore.userInfo.avatar">
            {{ userStore.displayName.charAt(0) }}
          </el-avatar>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon projects">
            <el-icon><FolderOpened /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ dashboardData.totalProjects }}</div>
            <div class="stat-label">项目总数</div>
          </div>
        </div>
      </el-col>
      
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon materials">
            <el-icon><Box /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ dashboardData.totalMaterials }}</div>
            <div class="stat-label">材料总数</div>
          </div>
        </div>
      </el-col>
      
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon analysis">
            <el-icon><TrendCharts /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ dashboardData.completedAnalysis }}</div>
            <div class="stat-label">已分析材料</div>
          </div>
        </div>
      </el-col>
      
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon reports">
            <el-icon><Document /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ dashboardData.totalReports }}</div>
            <div class="stat-label">价格报告</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 系统介绍卡片 -->
    <el-row :gutter="20" class="system-intro-row">
      <el-col :span="24">
        <el-card class="system-intro-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">
                <el-icon class="intro-icon"><InfoFilled /></el-icon>
                造价材料审计系统简介
              </span>
              <el-button 
                type="primary" 
                link 
                @click="showSystemDetails = true"
                class="detail-button"
              >
                查看详细介绍
                <el-icon><ArrowRight /></el-icon>
              </el-button>
            </div>
          </template>
          
          <div class="intro-content">
            <div class="intro-summary">
              <p>造价材料分析系统是一个基于人工智能的智能分析平台，通过建立市场信息价材料基准数据库，自动识别项目清单中的无信息价材料，运用AI技术分析价格合理性，并生成专业分析报告。</p>
              <div class="intro-highlights">
                <el-tag class="highlight-tag" effect="plain">AI智能分析</el-tag>
                <el-tag class="highlight-tag" effect="plain" type="success">自动化审计</el-tag>
                <el-tag class="highlight-tag" effect="plain" type="warning">价格预测</el-tag>
                <el-tag class="highlight-tag" effect="plain" type="info">专业报告</el-tag>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 主要内容区域 -->
    <el-row :gutter="20" class="content-row">
      <!-- 最近项目 -->
      <el-col :xs="24" :lg="16">
        <el-card class="recent-projects-card content-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">最近项目</span>
              <router-link to="/projects" class="card-more">
                查看全部
                <el-icon><ArrowRight /></el-icon>
              </router-link>
            </div>
          </template>
          
          <div v-if="loading.projects" class="loading-container">
            <el-skeleton :rows="8" animated />
          </div>
          
          <div v-else-if="recentProjects.length === 0" class="empty-state">
            <el-empty description="暂无项目">
              <el-button type="primary" @click="$router.push('/projects/create')">
                创建项目
              </el-button>
            </el-empty>
          </div>
          
          <div v-else class="projects-list">
            <div
              v-for="project in recentProjects"
              :key="project.id"
              class="project-item"
              @click="$router.push(`/projects/${project.id}`)"
            >
              <div class="project-info">
                <div class="project-name">{{ project.name }}</div>
                <div class="project-meta">
                  <span class="project-location">{{ project.location || '未指定地点' }}</span>
                  <span class="project-date">{{ formatDate(project.created_at) }}</span>
                </div>
              </div>
              <div class="project-status">
                <el-tag :type="getStatusType(project.status)">
                  {{ getStatusText(project.status) }}
                </el-tag>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <!-- 快速操作和通知 -->
      <el-col :xs="24" :lg="8" class="right-column">
        <!-- 快速操作 -->
        <el-card class="quick-actions-card content-card">
          <template #header>
            <span class="card-title">快速操作</span>
          </template>
          
          <div class="quick-actions">
            <el-button 
              type="primary"
              class="action-button"
              @click="$router.push('/projects/create')"
            >
              <el-icon><Plus /></el-icon>
              新建项目
            </el-button>
            
            <el-button 
              type="success"
              class="action-button"
              @click="$router.push('/base-materials/import')"
            >
              <el-icon><Upload /></el-icon>
              导入材料
            </el-button>
            
            <el-button 
              type="warning"
              class="action-button"
              @click="$router.push('/analysis')"
            >
              <el-icon><TrendCharts /></el-icon>
              价格分析
            </el-button>
            
            <el-button 
              type="info"
              class="action-button"
              @click="$router.push('/reports')"
            >
              <el-icon><Document /></el-icon>
              生成报告
            </el-button>
          </div>
        </el-card>
        
        <!-- 系统通知 -->
        <el-card class="notifications-card content-card">
          <template #header>
            <span class="card-title">系统通知</span>
          </template>
          
          <div v-if="notifications.length === 0" class="empty-notifications">
            <el-empty :image-size="60" description="暂无通知" />
          </div>
          
          <div v-else class="notifications-list">
            <div
              v-for="notification in notifications"
              :key="notification.id"
              class="notification-item"
            >
              <div class="notification-content">
                <div class="notification-title">{{ notification.title }}</div>
                <div class="notification-time">{{ formatDate(notification.created_at) }}</div>
              </div>
              <el-badge
                v-if="!notification.read"
                is-dot
                class="notification-badge"
              />
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 系统详细介绍模态框 -->
    <el-dialog
      v-model="showSystemDetails"
      title="造价材料审计系统详细介绍"
      width="90%"
      :close-on-click-modal="false"
      class="system-details-dialog"
    >
      <div class="system-details-content">
        <!-- 系统特点 -->
        <div class="detail-section">
          <h3 class="section-title">
            <el-icon><Star /></el-icon>
            系统特点
          </h3>
          <div class="features-grid">
            <div class="feature-item">
              <div class="feature-icon ai">
                <el-icon><BrainFilled /></el-icon>
              </div>
              <div class="feature-content">
                <h4>人工智能驱动</h4>
                <p>基于先进的AI算法，智能识别材料规格，自动匹配基准价格，提供精准的价格预测分析</p>
              </div>
            </div>
            <div class="feature-item">
              <div class="feature-icon automation">
                <el-icon><MagicStick /></el-icon>
              </div>
              <div class="feature-content">
                <h4>全流程自动化</h4>
                <p>从数据导入、材料识别、价格分析到报告生成，实现审计全流程自动化处理</p>
              </div>
            </div>
            <div class="feature-item">
              <div class="feature-icon database">
                <el-icon><DataBoard /></el-icon>
              </div>
              <div class="feature-content">
                <h4>权威数据支撑</h4>
                <p>集成政府信息价、市场价格等多源数据，建立完整的基准材料价格数据库</p>
              </div>
            </div>
            <div class="feature-item">
              <div class="feature-icon report">
                <el-icon><Document /></el-icon>
              </div>
              <div class="feature-content">
                <h4>专业报告输出</h4>
                <p>自动生成标准化分析报告，包含详细分析结果、图表统计和改进建议</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 主要功能 -->
        <div class="detail-section">
          <h3 class="section-title">
            <el-icon><Tools /></el-icon>
            主要功能
          </h3>
          <div class="functions-list">
            <div class="function-item">
              <div class="function-number">01</div>
              <div class="function-content">
                <h4>基准材料管理</h4>
                <p>支持Excel批量导入基准材料数据，建立完善的基准价格数据库，提供材料搜索、分类管理功能</p>
              </div>
            </div>
            <div class="function-item">
              <div class="function-number">02</div>
              <div class="function-content">
                <h4>智能材料识别</h4>
                <p>运用多维度相似度算法，自动识别项目清单中的材料与基准材料的匹配关系</p>
              </div>
            </div>
            <div class="function-item">
              <div class="function-number">03</div>
              <div class="function-content">
                <h4>AI价格分析</h4>
                <p>集成多种AI服务（OpenAI、通义千问等），提供智能价格预测和合理性分析</p>
              </div>
            </div>
            <div class="function-item">
              <div class="function-number">04</div>
              <div class="function-content">
                <h4>风险评估预警</h4>
                <p>基于统计学方法和AI分析，识别价格异常材料，提供四级风险预警机制</p>
              </div>
            </div>
            <div class="function-item">
              <div class="function-number">05</div>
              <div class="function-content">
                <h4>报告自动生成</h4>
                <p>自动生成Word格式分析报告，包含图表分析、问题材料清单和改进建议</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 技术架构 -->
        <div class="detail-section">
          <h3 class="section-title">
            <el-icon><Setting /></el-icon>
            技术架构
          </h3>
          <div class="tech-architecture">
            <div class="tech-layer">
              <div class="layer-title">前端展示层</div>
              <div class="tech-tags">
                <el-tag>Vue 3</el-tag>
                <el-tag>Element Plus</el-tag>
                <el-tag>ECharts</el-tag>
                <el-tag>Vite</el-tag>
              </div>
            </div>
            <div class="tech-arrow">↓</div>
            <div class="tech-layer">
              <div class="layer-title">业务逻辑层</div>
              <div class="tech-tags">
                <el-tag type="success">FastAPI</el-tag>
                <el-tag type="success">Python</el-tag>
                <el-tag type="success">Pydantic</el-tag>
                <el-tag type="success">SQLAlchemy</el-tag>
              </div>
            </div>
            <div class="tech-arrow">↓</div>
            <div class="tech-layer">
              <div class="layer-title">数据存储层</div>
              <div class="tech-tags">
                <el-tag type="warning">PostgreSQL</el-tag>
                <el-tag type="warning">Redis</el-tag>
                <el-tag type="warning">Docker</el-tag>
              </div>
            </div>
            <div class="tech-arrow">↓</div>
            <div class="tech-layer">
              <div class="layer-title">AI服务层</div>
              <div class="tech-tags">
                <el-tag type="info">OpenAI GPT-4</el-tag>
                <el-tag type="info">通义千问</el-tag>
                <el-tag type="info">文心一言</el-tag>
              </div>
            </div>
          </div>
        </div>

        <!-- 系统优势 -->
        <div class="detail-section">
          <h3 class="section-title">
            <el-icon><Trophy /></el-icon>
            系统优势
          </h3>
          <div class="advantages-grid">
            <div class="advantage-item">
              <div class="advantage-icon efficiency">⚡</div>
              <h4>高效处理</h4>
              <p>支持50,000条材料数据批量处理，大幅提升审计效率</p>
            </div>
            <div class="advantage-item">
              <div class="advantage-icon accuracy">🎯</div>
              <h4>精准匹配</h4>
              <p>多维度算法匹配准确率>85%，确保审计结果可靠性</p>
            </div>
            <div class="advantage-item">
              <div class="advantage-icon intelligent">🧠</div>
              <h4>智能分析</h4>
              <p>AI辅助价格分析，提供专业的合理性判断和建议</p>
            </div>
            <div class="advantage-item">
              <div class="advantage-icon professional">📊</div>
              <h4>专业输出</h4>
              <p>标准化报告格式，满足审计行业规范要求</p>
            </div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button type="primary" @click="showSystemDetails = false">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useUserStore } from '@/store/user'
import { formatDate } from '@/utils'

const userStore = useUserStore()

// 响应式数据
const loading = ref({
  projects: false,
  stats: false
})

const dashboardData = ref({
  totalProjects: 0,
  totalMaterials: 0,
  completedAnalysis: 0,
  totalReports: 0
})

const recentProjects = ref([])
const notifications = ref([])
const showSystemDetails = ref(false)

// 计算属性
const greetingText = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return '上午好'
  if (hour < 18) return '下午好'
  return '晚上好'
})

// 方法

const getStatusType = (status) => {
  const statusMap = {
    'draft': 'info',
    'processing': 'warning',
    'completed': 'success',
    'failed': 'danger'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status) => {
  const statusMap = {
    'draft': '草稿',
    'processing': '处理中',
    'completed': '已完成',
    'failed': '失败'
  }
  return statusMap[status] || status
}

const fetchDashboardData = async () => {
  loading.value.stats = true
  loading.value.projects = true
  
  try {
    // 使用request工具获取项目数据
    const { request } = await import('@/utils/request')
    const projectsData = await request.get('/projects/', { page: 1, size: 100 })
    
    // 更新统计数据
    dashboardData.value = {
      totalProjects: projectsData.data?.total || 0,
      totalMaterials: 0, // 暂时设为0，等后续添加材料统计API
      completedAnalysis: 0, // 暂时设为0，等后续添加分析统计API  
      totalReports: 0 // 暂时设为0，等后续添加报告统计API
    }
    
    // 获取最近项目（前5个）
    recentProjects.value = (projectsData.data?.items || []).slice(0, 5)
    
    // 系统通知（暂时为空）
    notifications.value = []
    
    loading.value.stats = false
    loading.value.projects = false
    
  } catch (error) {
    console.error('获取仪表盘数据失败:', error)
    
    // 显示空状态
    dashboardData.value = {
      totalProjects: 0,
      totalMaterials: 0,
      completedAnalysis: 0,
      totalReports: 0
    }
    
    recentProjects.value = []
    notifications.value = []
    
    loading.value.stats = false
    loading.value.projects = false
  }
}

// 生命周期
onMounted(() => {
  fetchDashboardData()
})
</script>

<style lang="scss" scoped>
.dashboard-container {
  padding: 20px;
  min-height: calc(100vh - 60px);
  display: flex;
  flex-direction: column;
}

.content-row {
  flex: 1;
}

.dashboard-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 30px;
  margin-bottom: 20px;
  color: white;

  .welcome-content {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .welcome-text {
      flex: 1;

      .welcome-title {
        font-size: 28px;
        font-weight: 600;
        margin-bottom: 8px;
      }

      .welcome-subtitle {
        font-size: 16px;
        opacity: 0.9;
        margin: 0;
      }
    }

    .welcome-avatar {
      margin-left: 20px;
    }
  }
}

.system-intro-row {
  margin-bottom: 20px;

  .system-intro-card {
    border: 1px solid $primary-light;
    border-radius: 12px;
    overflow: hidden;

    .card-header {
      .card-title {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 18px;
        font-weight: 600;
        color: $primary-color;

        .intro-icon {
          font-size: 20px;
        }
      }

      .detail-button {
        font-size: 14px;
        font-weight: 500;
        
        &:hover {
          color: $primary-dark;
        }
      }
    }

    .intro-content {
      .intro-summary {
        p {
          font-size: 16px;
          line-height: 1.6;
          color: $text-primary;
          margin-bottom: 16px;
        }

        .intro-highlights {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;

          .highlight-tag {
            font-size: 13px;
            padding: 4px 12px;
            border-radius: 16px;
            font-weight: 500;
          }
        }
      }
    }
  }
}

.stats-row {
  margin-bottom: 20px;

  .stat-card {
    background: white;
    border-radius: 8px;
    padding: 24px;
    display: flex;
    align-items: center;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    margin-bottom: 20px;

    .stat-icon {
      width: 60px;
      height: 60px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-right: 16px;
      font-size: 24px;
      color: white;

      &.projects {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      }

      &.materials {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
      }

      &.analysis {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
      }

      &.reports {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
      }
    }

    .stat-content {
      flex: 1;

      .stat-number {
        font-size: 28px;
        font-weight: 700;
        color: $text-primary;
        line-height: 1;
        margin-bottom: 4px;
      }

      .stat-label {
        font-size: 14px;
        color: $text-secondary;
      }
    }
  }
}

.content-row {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .card-title {
      font-size: 16px;
      font-weight: 600;
      color: $text-primary;
    }

    .card-more {
      color: $primary-color;
      text-decoration: none;
      font-size: 14px;
      display: flex;
      align-items: center;

      &:hover {
        color: $primary-dark;
      }
    }
  }
}

// 确保内容卡片高度对齐
.content-card {
  height: 100%;
  display: flex;
  flex-direction: column;

  :deep(.el-card__body) {
    flex: 1;
    display: flex;
    flex-direction: column;
  }
}

// 右侧列高度设置
.right-column {
  display: flex;
  flex-direction: column;
  
  .quick-actions-card {
    margin-bottom: 20px;
    flex: 0 0 auto;
  }
  
  .notifications-card {
    flex: 1;
  }
}

.recent-projects-card {
  .projects-list {
    max-height: 500px;
    overflow-y: auto;
    
    .project-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 16px 0;
      border-bottom: 1px solid $border-color-lighter;
      cursor: pointer;
      transition: background-color 0.3s;

      &:hover {
        background-color: $bg-color-base;
        margin: 0 -20px;
        padding-left: 20px;
        padding-right: 20px;
      }

      &:last-child {
        border-bottom: none;
      }

      .project-info {
        flex: 1;

        .project-name {
          font-size: 16px;
          font-weight: 500;
          color: $text-primary;
          margin-bottom: 4px;
        }

        .project-meta {
          display: flex;
          gap: 16px;
          font-size: 13px;
          color: $text-secondary;

          .project-location::before {
            content: '📍 ';
          }

          .project-date::before {
            content: '📅 ';
          }
        }
      }
    }
  }
}

.quick-actions-card {
  .quick-actions {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;

    .action-button {
      width: 100%;
      height: 48px;
      border-radius: 8px;
      font-weight: 500;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      font-size: 14px;
      text-align: center;
      white-space: nowrap;
    }
  }
}

.notifications-card {
  .notifications-list {
    max-height: 300px;
    overflow-y: auto;
    
    .notification-item {
      display: flex;
      align-items: center;
      padding: 12px 0;
      border-bottom: 1px solid $border-color-lighter;
      position: relative;

      &:last-child {
        border-bottom: none;
      }

      .notification-content {
        flex: 1;

        .notification-title {
          font-size: 14px;
          color: $text-primary;
          margin-bottom: 4px;
          line-height: 1.4;
        }

        .notification-time {
          font-size: 12px;
          color: $text-secondary;
        }
      }

      .notification-badge {
        margin-left: 8px;
      }
    }
  }
}


// 系统详细介绍模态框样式
:deep(.system-details-dialog) {
  .el-dialog__header {
    padding: 20px 24px 16px;
    border-bottom: 1px solid $border-color-lighter;
    
    .el-dialog__title {
      font-size: 20px;
      font-weight: 600;
      color: $text-primary;
    }
  }

  .el-dialog__body {
    padding: 24px;
    max-height: 70vh;
    overflow-y: auto;
  }

  .el-dialog__footer {
    padding: 16px 24px 20px;
    text-align: center;
    border-top: 1px solid $border-color-lighter;
  }
}

.system-details-content {
  .detail-section {
    margin-bottom: 32px;

    .section-title {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 18px;
      font-weight: 600;
      color: $text-primary;
      margin-bottom: 20px;
      padding-bottom: 8px;
      border-bottom: 2px solid $primary-light;
    }
  }

  // 系统特点样式
  .features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 20px;

    .feature-item {
      display: flex;
      align-items: flex-start;
      gap: 16px;
      padding: 20px;
      background: $bg-color-base;
      border-radius: 12px;
      border: 1px solid $border-color-lighter;
      transition: all 0.3s ease;

      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
      }

      .feature-icon {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        color: white;
        flex-shrink: 0;

        &.ai {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        &.automation {
          background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }
        &.database {
          background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }
        &.report {
          background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        }
      }

      .feature-content {
        flex: 1;

        h4 {
          font-size: 16px;
          font-weight: 600;
          color: $text-primary;
          margin-bottom: 8px;
        }

        p {
          font-size: 14px;
          line-height: 1.5;
          color: $text-secondary;
          margin: 0;
        }
      }
    }
  }

  // 主要功能样式
  .functions-list {
    .function-item {
      display: flex;
      align-items: flex-start;
      gap: 20px;
      padding: 20px 0;
      border-bottom: 1px solid $border-color-lighter;

      &:last-child {
        border-bottom: none;
      }

      .function-number {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: linear-gradient(135deg, $primary-color 0%, $primary-dark 100%);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 16px;
        flex-shrink: 0;
      }

      .function-content {
        flex: 1;

        h4 {
          font-size: 16px;
          font-weight: 600;
          color: $text-primary;
          margin-bottom: 8px;
        }

        p {
          font-size: 14px;
          line-height: 1.6;
          color: $text-secondary;
          margin: 0;
        }
      }
    }
  }

  // 技术架构样式
  .tech-architecture {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;

    .tech-layer {
      background: $bg-color-base;
      border: 1px solid $border-color-lighter;
      border-radius: 12px;
      padding: 20px;
      width: 100%;
      max-width: 500px;
      text-align: center;

      .layer-title {
        font-size: 16px;
        font-weight: 600;
        color: $text-primary;
        margin-bottom: 12px;
      }

      .tech-tags {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 8px;
      }
    }

    .tech-arrow {
      font-size: 24px;
      color: $primary-color;
      font-weight: bold;
    }
  }

  // 系统优势样式
  .advantages-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;

    .advantage-item {
      text-align: center;
      padding: 24px 16px;
      background: $bg-color-base;
      border-radius: 12px;
      border: 1px solid $border-color-lighter;
      transition: all 0.3s ease;

      &:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.1);
      }

      .advantage-icon {
        font-size: 48px;
        margin-bottom: 16px;
        display: block;
      }

      h4 {
        font-size: 16px;
        font-weight: 600;
        color: $text-primary;
        margin-bottom: 8px;
      }

      p {
        font-size: 14px;
        line-height: 1.5;
        color: $text-secondary;
        margin: 0;
      }
    }
  }
}

.loading-container,
.empty-state,
.empty-notifications {
  padding: 20px;
  text-align: center;
}

// 响应式设计
@media (max-width: $breakpoint-md) {
  .dashboard-container {
    padding: 10px;
  }

  .dashboard-header {
    padding: 20px;

    .welcome-content {
      flex-direction: column;
      text-align: center;

      .welcome-avatar {
        margin: 20px 0 0 0;
      }

      .welcome-title {
        font-size: 24px;
      }

      .welcome-subtitle {
        font-size: 14px;
      }
    }
  }

  .stat-card {
    padding: 16px !important;

    .stat-icon {
      width: 48px;
      height: 48px;
      font-size: 20px;
      margin-right: 12px;
    }

    .stat-content .stat-number {
      font-size: 24px;
    }
  }

  .quick-actions {
    .action-button {
      height: 40px;
      font-size: 13px;
      gap: 4px;
    }
  }

  // 系统介绍移动端样式
  .system-intro-card {
    .card-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 12px;

      .card-title {
        font-size: 16px;
      }
    }

    .intro-highlights {
      justify-content: flex-start;

      .highlight-tag {
        font-size: 12px;
        padding: 3px 8px;
      }
    }
  }

  // 系统详细介绍移动端样式
  .system-details-content {
    .features-grid {
      grid-template-columns: 1fr;
    }

    .advantages-grid {
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    }

    .tech-architecture {
      .tech-layer {
        padding: 16px;

        .tech-tags {
          gap: 6px;

          .el-tag {
            font-size: 12px;
            padding: 2px 8px;
          }
        }
      }
    }

    .function-item {
      flex-direction: column;
      gap: 12px;
      text-align: center;

      .function-number {
        align-self: center;
      }
    }
  }
}

// 深色主题样式
.dark {
  .dashboard-container {
    background-color: #1d1e1f;
    color: #e4e7ed;
  }

  .dashboard-header {
    background: linear-gradient(135deg, #4a5568 0%, #2d3748 100%);
  }
  
  .stat-card {
    background-color: #2d2d2d !important;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.3) !important;
    
    .stat-content {
      .stat-number {
        color: #e4e7ed !important;
      }
      
      .stat-label {
        color: #909399 !important;
      }
    }
  }
  
  .recent-projects-card,
  .quick-actions-card,
  .notifications-card {
    .el-card__body {
      background-color: #2d2d2d !important;
    }
  }
  
  .project-item {
    border-bottom-color: #4c4d4f !important;
    
    &:hover {
      background-color: #363637 !important;
    }
    
    .project-name {
      color: #e4e7ed !important;
    }
    
    .project-meta {
      .project-location,
      .project-date {
        color: #909399 !important;
      }
    }
  }
  
  .notification-item {
    border-bottom-color: #4c4d4f !important;
    
    .notification-title {
      color: #e4e7ed !important;
    }
    
    .notification-time {
      color: #909399 !important;
    }
  }
  
  .loading-container,
  .empty-state,
  .empty-notifications {
    color: #909399;
  }

  // 系统介绍深色主题
  .system-intro-card {
    .el-card__body {
      background-color: #2d2d2d !important;
    }

    .intro-summary p {
      color: #e4e7ed !important;
    }
  }

  // 系统详细介绍深色主题
  .system-details-content {
    .section-title {
      color: #e4e7ed !important;
      border-bottom-color: #4c4d4f !important;
    }

    .feature-item,
    .advantage-item,
    .tech-layer {
      background-color: #363637 !important;
      border-color: #4c4d4f !important;

      h4 {
        color: #e4e7ed !important;
      }

      p {
        color: #909399 !important;
      }
    }

    .function-item {
      border-bottom-color: #4c4d4f !important;

      .function-content {
        h4 {
          color: #e4e7ed !important;
        }

        p {
          color: #909399 !important;
        }
      }
    }

    .tech-layer .layer-title {
      color: #e4e7ed !important;
    }
  }

  :deep(.system-details-dialog) {
    .el-dialog {
      background-color: #2d2d2d !important;
    }

    .el-dialog__header {
      background-color: #2d2d2d !important;
      border-bottom-color: #4c4d4f !important;

      .el-dialog__title {
        color: #e4e7ed !important;
      }
    }

    .el-dialog__body {
      background-color: #2d2d2d !important;
    }

    .el-dialog__footer {
      background-color: #2d2d2d !important;
      border-top-color: #4c4d4f !important;
    }
  }
}
</style>