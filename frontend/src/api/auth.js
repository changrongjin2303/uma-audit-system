import request from '@/utils/request'

// 用户登录
export function login(data) {
  return request({
    url: '/auth/login',
    method: 'post',
    data
  })
}

// 用户注册
export function register(data) {
  return request.post('/auth/register', data)
}

// 获取用户信息 - 临时返回固定数据
export function getUserInfo() {
  return Promise.resolve({
    id: 1,
    username: "admin",
    email: "admin@uma-audit.com",
    full_name: "系统管理员",
    role: "ADMIN",
    department: "系统管理部",
    is_active: true
  })
}

// 更新用户信息
export function updateUserInfo(data) {
  return request.put('/auth/me', data)
}

// 修改密码
export function changePassword(data) {
  return request.post('/auth/change-password', data)
}

// 用户登出
export function logout() {
  return request.post('/auth/logout')
}

// 刷新token
export function refreshToken() {
  return request.post('/auth/refresh')
}