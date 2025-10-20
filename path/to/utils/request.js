import axios from 'axios'

const request = axios.create({
  baseURL: '/api',
  timeout: 5000
})

// 添加请求拦截器
request.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`
  }
  return config
})

// 添加响应拦截器
request.interceptors.response.use(
  response => response.data,
  error => {
    console.error('Request failed:', error)
    return Promise.reject(error)
  }
)

export default request