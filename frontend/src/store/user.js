import { defineStore } from 'pinia'
import { login, logout, getUserInfo } from '@/api/auth'
import { getToken, setToken, removeToken } from '@/utils/auth'
import router from '@/router'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: getToken(),
    userInfo: {
      id: null,
      username: '',
      email: '',
      full_name: '',
      role: '',
      department: '',
      phone: '',
      is_active: true,
      is_verified: false
    },
    permissions: []
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
    isAdmin: (state) => state.userInfo.role === 'admin',
    isManager: (state) => state.userInfo.role === 'manager',
    isAuditor: (state) => state.userInfo.role === 'auditor',
    isCostEngineer: (state) => state.userInfo.role === 'cost_engineer',
    displayName: (state) => state.userInfo.full_name || state.userInfo.username || '用户',
    roleText: (state) => {
      const roleMap = {
        admin: '系统管理员',
        manager: '项目经理',
        auditor: '审计员',
        cost_engineer: '造价工程师'
      }
      return roleMap[state.userInfo.role] || '未知角色'
    }
  },

  actions: {
    // 登录
    async login(loginForm) {
      try {
        const response = await login(loginForm)
        
        // 适配后端API返回格式
        let token, user
        if (response.access_token) {
          // 后端API标准格式: {access_token, user}
          token = response.access_token
          user = response.user
        } else {
          // 其他格式处理
          token = response.data?.token || response.data?.access_token
          user = response.data?.user || response.user
        }
        
        this.token = token
        setToken(token)
        
        // 直接使用登录响应中的用户信息，避免额外的API调用
        if (user) {
          this.userInfo = user
        }
        
        return response
      } catch (error) {
        console.error('登录失败:', error)
        throw error
      }
    },

    // 获取用户信息
    async getUserInfo() {
      try {
        const response = await getUserInfo()
        this.userInfo = response
        
        return response
      } catch (error) {
        console.error('获取用户信息失败:', error)
        throw error
      }
    },

    // 登出
    async logout() {
      try {
        if (this.token) {
          await logout()
        }
      } catch (error) {
        console.error('登出请求失败:', error)
      } finally {
        this.resetState()
        router.push('/login')
      }
    },

    // 重置状态
    resetState() {
      this.token = ''
      this.userInfo = {
        id: null,
        username: '',
        email: '',
        full_name: '',
        role: '',
        department: '',
        phone: '',
        is_active: true,
        is_verified: false
      }
      this.permissions = []
      removeToken()
    },

    // 检查登录状态
    async checkLoginStatus() {
      if (this.token) {
        try {
          await this.getUserInfo()
        } catch (error) {
          console.error('检查登录状态失败:', error)
          this.resetState()
        }
      }
    },

    // 更新用户信息
    updateUserInfo(userInfo) {
      this.userInfo = { ...this.userInfo, ...userInfo }
    },

    // 刷新token
    async refreshToken() {
      try {
        // 这里可以实现token刷新逻辑
        // const response = await refreshToken()
        // this.token = response.access_token
        // setToken(response.access_token)
      } catch (error) {
        console.error('刷新token失败:', error)
        this.logout()
      }
    },

    // 修改密码
    async changePassword(passwordData) {
      try {
        // 这里调用修改密码API
        // await changePassword(passwordData)
        return true
      } catch (error) {
        console.error('修改密码失败:', error)
        throw error
      }
    },

    // 检查权限
    hasPermission(permission) {
      return this.permissions.includes(permission) || this.isAdmin
    },

    // 检查角色
    hasRole(role) {
      if (Array.isArray(role)) {
        return role.includes(this.userInfo.role)
      }
      return this.userInfo.role === role
    }
  },

  persist: {
    key: 'user-store',
    storage: localStorage,
    paths: ['token'] // 只持久化token
  }
})