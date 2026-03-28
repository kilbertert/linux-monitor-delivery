/**
 * API 请求模块
 */
import axios from 'axios'

const runtimeHost = typeof window !== 'undefined' ? window.location.hostname : 'localhost'
const API_BASE = import.meta.env.VITE_API_BASE_URL || `http://${runtimeHost}:8000`

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

// ============ 指标相关 ============

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

// ============ 配置相关 ============

// 获取配置
export function getConfig() {
  return apiClient.get('/config')
}

// 更新配置
export function updateConfig(config) {
  return apiClient.post('/config', config)
}

// 重置配置
export function resetConfig() {
  return apiClient.post('/config/reset')
}

// ============ 告警相关 ============

// 获取告警规则
export function getAlertRules() {
  return apiClient.get('/alerts/rules')
}

// 更新告警规则
export function updateAlertRule(ruleName, update) {
  return apiClient.post(`/alerts/rules/${ruleName}`, update)
}

// 切换告警规则
export function toggleAlertRule(ruleName) {
  return apiClient.post(`/alerts/rules/${ruleName}/toggle`)
}

// ============ 进程相关 ============

// 获取进程列表
export function getProcesses(top = 10, sort = 'cpu') {
  return apiClient.get('/processes/', { params: { top, sort } })
}

// 获取 CPU 排行进程
export function getTopCpuProcesses(top = 10) {
  return apiClient.get('/processes/top/cpu', { params: { top } })
}

// 获取内存排行进程
export function getTopMemoryProcesses(top = 10) {
  return apiClient.get('/processes/top/memory', { params: { top } })
}

export default apiClient
