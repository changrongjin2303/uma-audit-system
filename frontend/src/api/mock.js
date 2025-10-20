/**
 * API模拟服务 - 用于前端开发和测试
 */

// 模拟延迟
const delay = (ms = 300) => new Promise(resolve => setTimeout(resolve, ms))

// 模拟项目数据
const mockProjects = [
  {
    id: 1,
    name: "测试项目001",
    description: "这是一个测试项目，用于验证项目创建功能",
    region: "beijing",
    status: "processing",
    created_at: "2024-01-15T10:30:00Z",
    updated_at: "2024-01-15T14:20:00Z",
    user_id: 1,
    material_count: 156,
    analyzed_count: 89,
    total_amount: 1234567.89
  },
  {
    id: 2,
    name: "办公楼装修项目",
    description: "某办公楼的装修改造项目材料价格审计",
    region: "shanghai",
    status: "completed",
    created_at: "2024-01-10T09:15:00Z",
    updated_at: "2024-01-12T16:45:00Z",
    user_id: 1,
    material_count: 234,
    analyzed_count: 234,
    total_amount: 2345678.90
  }
]

// 模拟用户数据
const mockUser = {
  id: 1,
  username: "test_user",
  email: "test@example.com",
  full_name: "测试用户",
  role: "auditor",
  is_active: true,
  created_at: "2024-01-01T00:00:00Z"
}

// Mock API响应
export const mockAPI = {
  // 用户认证
  async login(credentials) {
    await delay()
    if (credentials.username === 'test' && credentials.password === 'test123') {
      return {
        access_token: 'mock_token_' + Date.now(),
        token_type: 'bearer',
        user: mockUser
      }
    }
    throw new Error('用户名或密码错误')
  },

  async getCurrentUser() {
    await delay()
    return mockUser
  },

  // 项目管理
  async getProjects() {
    await delay()
    return {
      items: mockProjects,
      total: mockProjects.length,
      page: 1,
      size: 20,
      pages: 1
    }
  },

  async createProject(projectData) {
    await delay()
    
    // 模拟项目创建
    const newProject = {
      id: mockProjects.length + 1,
      ...projectData,
      status: "draft",
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      user_id: 1,
      material_count: 0,
      analyzed_count: 0,
      total_amount: 0
    }
    
    mockProjects.push(newProject)
    return newProject
  },

  async getProject(id) {
    await delay()
    const project = mockProjects.find(p => p.id === parseInt(id))
    if (!project) {
      throw new Error('项目不存在')
    }
    return project
  },

  async updateProject(id, updateData) {
    await delay()
    const projectIndex = mockProjects.findIndex(p => p.id === parseInt(id))
    if (projectIndex === -1) {
      throw new Error('项目不存在')
    }
    
    mockProjects[projectIndex] = {
      ...mockProjects[projectIndex],
      ...updateData,
      updated_at: new Date().toISOString()
    }
    
    return mockProjects[projectIndex]
  },

  async deleteProject(id) {
    await delay()
    const projectIndex = mockProjects.findIndex(p => p.id === parseInt(id))
    if (projectIndex === -1) {
      throw new Error('项目不存在')
    }
    
    mockProjects.splice(projectIndex, 1)
    return { message: '项目删除成功' }
  },

  // 基准材料管理
  async getBaseMaterials() {
    await delay()
    return {
      items: [
        {
          id: 1,
          name: "水泥",
          category: "building",
          unit: "吨",
          reference_price: 450.00,
          region: "beijing",
          source: "government",
          updated_at: "2024-01-15T00:00:00Z"
        },
        {
          id: 2,
          name: "钢筋",
          category: "building", 
          unit: "吨",
          reference_price: 4200.00,
          region: "beijing",
          source: "government",
          updated_at: "2024-01-15T00:00:00Z"
        }
      ],
      total: 2,
      page: 1,
      size: 20,
      pages: 1
    }
  },

  // 其他API...
  async getAnalysisResults() {
    await delay()
    return { items: [], total: 0 }
  },

  async getReports() {
    await delay()
    return { items: [], total: 0 }
  }
}

// 检查是否启用Mock模式
export const isMockMode = () => {
  // 强制禁用Mock模式，直接使用后端API
  return false
  // return process.env.NODE_ENV === 'development' && 
  //        (localStorage.getItem('useMockAPI') === 'true' || 
  //         import.meta.env.VITE_USE_MOCK_API === 'true')
}

// 启用Mock模式
export const enableMockMode = () => {
  localStorage.setItem('useMockAPI', 'true')
  console.log('✅ Mock API模式已启用')
}

// 禁用Mock模式
export const disableMockMode = () => {
  localStorage.removeItem('useMockAPI')
  console.log('❌ Mock API模式已禁用')
}