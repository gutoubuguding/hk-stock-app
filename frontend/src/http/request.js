import axios from 'axios'

const instance = axios.create({
  baseURL: '/api',
  timeout: 300000, // 5分钟 - AI分析需要较长时间
})

// 请求拦截器
instance.interceptors.request.use(
  (config) => {
    const token = sessionStorage.getItem('token')
    if (token) {
      config.headers.token = token
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
instance.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    if (error.response && error.response.status === 401) {
      // 未登录，跳转登录页
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default function request(config) {
  return instance(config)
}
