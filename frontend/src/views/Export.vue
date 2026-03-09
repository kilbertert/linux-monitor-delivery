<template>
  <div class="export">
    <header class="header">
      <h1>数据导出</h1>
      <router-link to="/" class="back-link">← 返回仪表盘</router-link>
    </header>

    <div class="content">
      <div class="export-form">
        <h3>导出历史数据</h3>
        
        <div class="form-group">
          <label>指标类型</label>
          <select v-model="metricType">
            <option value="cpu">CPU 使用率</option>
            <option value="memory">内存使用</option>
            <option value="disk">磁盘 I/O</option>
            <option value="network">网络带宽</option>
          </select>
        </div>

        <div class="form-group">
          <label>时间范围</label>
          <select v-model="timeRange" @change="onTimeRangeChange">
            <option value="1h">最近 1 小时</option>
            <option value="6h">最近 6 小时</option>
            <option value="24h">最近 24 小时</option>
            <option value="7d">最近 7 天</option>
            <option value="30d">最近 30 天</option>
          </select>
        </div>

        <div class="form-group">
          <label>数据条数</label>
          <select v-model="limit">
            <option :value="100">100 条</option>
            <option :value="500">500 条</option>
            <option :value="1000">1000 条</option>
            <option :value="5000">5000 条</option>
          </select>
        </div>

        <div class="form-actions">
          <button @click="doExport" class="btn btn-primary">导出 CSV</button>
          <button @click="fetchPreview" class="btn btn-secondary">预览数据</button>
        </div>
      </div>

      <div class="preview" v-if="previewData.length > 0">
        <h3>数据预览 (前 20 条)</h3>
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>时间</th>
                <th>{{ metricLabel }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, index) in previewData.slice(0, 20)" :key="index">
                <td>{{ formatTime(row.timestamp) }}</td>
                <td>{{ formatValue(row) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p class="hint">共 {{ previewData.length }} 条数据，点击"导出 CSV"下载完整数据</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { getHistoryMetrics } from '../api'

const metricType = ref('cpu')
const timeRange = ref('1h')
const limit = ref(1000)
const previewData = ref([])

const metricLabels = {
  cpu: 'CPU %',
  memory: '内存 %',
  disk: '磁盘 MB/s',
  network: '网络 KB/s'
}

const metricLabel = computed(() => metricLabels[metricType.value])

function getTimeRange() {
  const now = Date.now()
  const ranges = {
    '1h': now - 3600 * 1000,
    '6h': now - 6 * 3600 * 1000,
    '24h': now - 24 * 3600 * 1000,
    '7d': now - 7 * 24 * 3600 * 1000,
    '30d': now - 30 * 24 * 3600 * 1000
  }
  return ranges[timeRange.value]
}

function onTimeRangeChange() {
  previewData.value = []
}

async function fetchPreview() {
  try {
    const endTime = Date.now()
    const startTime = getTimeRange()
    
    const result = await getHistoryMetrics(metricType.value, startTime, endTime, limit.value)
    previewData.value = result.data || []
  } catch (e) {
    console.error('获取预览数据失败:', e)
  }
}

async function doExport() {
  const endTime = Date.now()
  const startTime = getTimeRange()
  
  const url = `http://172.21.144.1:8000/export/csv?metric_type=${metricType.value}&start_time=${startTime}&end_time=${endTime}&limit=${limit.value}`
  
  // 创建下载链接
  const link = document.createElement('a')
  link.href = url
  link.download = `${metricType.value}_${timeRange.value}_${Date.now()}.csv`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

function formatTime(timestamp) {
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN')
}

function formatValue(row) {
  if (metricType.value === 'cpu') {
    return row.cpu_percent?.toFixed(2) + '%'
  } else if (metricType.value === 'memory') {
    return row.percent?.toFixed(2) + '%'
  } else if (metricType.value === 'disk') {
    const mb = (row.read_bytes + row.write_bytes) / (1024 * 1024)
    return mb.toFixed(2) + ' MB/s'
  } else if (metricType.value === 'network') {
    const kb = (row.bytes_sent + row.bytes_recv) / 1024
    return kb.toFixed(2) + ' KB/s'
  }
  return '-'
}
</script>

<style scoped>
.export {
  min-height: 100vh;
  background: #f5f7fa;
}

.header {
  background: #fff;
  padding: 16px 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header h1 {
  margin: 0;
  font-size: 20px;
  color: #333;
}

.back-link {
  color: #409EFF;
  text-decoration: none;
}

.content {
  padding: 24px;
}

.export-form {
  background: #fff;
  padding: 24px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.export-form h3 {
  margin: 0 0 20px 0;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #666;
}

.form-group select {
  width: 100%;
  max-width: 300px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}

.btn {
  padding: 10px 24px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-primary {
  background: #409EFF;
  color: #fff;
}

.btn-primary:hover {
  background: #66b1ff;
}

.btn-secondary {
  background: #67C23A;
  color: #fff;
}

.btn-secondary:hover {
  background: #85CE61;
}

.preview {
  background: #fff;
  padding: 24px;
  border-radius: 8px;
}

.preview h3 {
  margin: 0 0 16px 0;
}

.table-container {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

th {
  background: #f5f7fa;
  font-weight: 500;
}

.hint {
  margin-top: 12px;
  color: #999;
  font-size: 14px;
}
</style>
