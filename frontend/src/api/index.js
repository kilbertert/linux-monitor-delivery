/**
 * API 请求模块
 */
import axios from 'axios'

const API_BASE = 'http://172.21.144.1:8000'

const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
apiClient.interceptors.request.use(
  config => config,
  error => Promise.reject(error)
)

// 响应拦截器
apiClient.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// 获取当前指标
export function getCurrentMetrics() {
  return apiClient.get('/metrics/current')
}

// 获取 CPU 指标
export function getCpuMetrics() {
  return apiClient.get('/metrics/cpu')
}

// 获取内存指标
export function getMemoryMetrics() {
  return apiClient.get('/metrics/memory')
}

// 获取磁盘指标
export function getDiskMetrics() {
  return apiClient.get('/metrics/disk')
}

// 获取网络指标
export function getNetworkMetrics() {
  return apiClient.get('/metrics/network')
}

// 获取历史指标
export function getHistoryMetrics(metricType, startTime, endTime, limit = 100) {
  return apiClient.get('/metrics/history', {
    params: { metric_type: metricType, start_time: startTime, end_time: endTime, limit }
  })
}

// 获取系统信息
export function getSystemInfo() {
  return apiClient.get('/metrics/system/info')
}

// 健康检查
export function healthCheck() {
  return apiClient.get('/health')
}

export default apiClient
