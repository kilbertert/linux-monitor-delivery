<template>
  <div class="history">
    <header class="header">
      <h1>历史数据查询</h1>
      <router-link to="/" class="back-link">← 返回仪表盘</router-link>
    </header>

    <div class="content">
      <div class="controls">
        <div class="control-group">
          <label>指标类型</label>
          <select v-model="metricType">
            <option value="cpu">CPU 使用率</option>
            <option value="memory">内存使用</option>
            <option value="disk">磁盘 I/O</option>
            <option value="network">网络带宽</option>
          </select>
        </div>
        
        <div class="control-group">
          <label>时间范围</label>
          <select v-model="timeRange" @change="onTimeRangeChange">
            <option value="1h">最近 1 小时</option>
            <option value="6h">最近 6 小时</option>
            <option value="24h">最近 24 小时</option>
            <option value="7d">最近 7 天</option>
          </select>
        </div>
        
        <div class="control-group">
          <label>数据条数</label>
          <select v-model="limit">
            <option :value="50">50 条</option>
            <option :value="100">100 条</option>
            <option :value="200">200 条</option>
          </select>
        </div>
        
        <button @click="fetchHistory" class="btn">查询</button>
      </div>

      <div class="chart-container">
        <v-chart class="chart" :option="chartOption" autoresize />
      </div>

      <div class="data-table" v-if="tableData.length > 0">
        <h3>数据详情</h3>
        <table>
          <thead>
            <tr>
              <th>时间</th>
              <th>{{ metricLabel }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in tableData" :key="index">
              <td>{{ formatTime(item.timestamp) }}</td>
              <td>{{ formatValue(item) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { getHistoryMetrics } from '../api'

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent, LegendComponent])

const metricType = ref('cpu')
const timeRange = ref('1h')
const limit = ref(100)
const historyData = ref([])

const metricLabels = {
  cpu: 'CPU %',
  memory: '内存 %',
  disk: '磁盘 MB/s',
  network: '网络 KB/s'
}

const metricLabel = computed(() => metricLabels[metricType.value])

const tableData = computed(() => {
  return [...historyData.value].reverse().slice(0, 20)
})

const chartOption = computed(() => {
  const data = [...historyData.value].reverse()
  const timestamps = data.map(d => {
    const date = new Date(d.timestamp)
    return `${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`
  })
  
  let values = []
  let seriesName = ''
  
  if (metricType.value === 'cpu') {
    values = data.map(d => d.cpu_percent)
    seriesName = 'CPU %'
  } else if (metricType.value === 'memory') {
    values = data.map(d => d.percent)
    seriesName = '内存 %'
  } else if (metricType.value === 'disk') {
    values = data.map(d => (d.read_bytes + d.write_bytes) / (1024 * 1024))
    seriesName = '磁盘 MB/s'
  } else if (metricType.value === 'network') {
    values = data.map(d => (d.bytes_sent + d.bytes_recv) / 1024)
    seriesName = '网络 KB/s'
  }

  return {
    tooltip: {
      trigger: 'axis'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: timestamps
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: seriesName,
        type: 'line',
        smooth: true,
        symbol: 'none',
        areaStyle: {
          color: 'rgba(64, 158, 255, 0.2)'
        },
        data: values
      }
    ]
  }
})

function getTimeRange() {
  const now = Date.now()
  const ranges = {
    '1h': now - 3600 * 1000,
    '6h': now - 6 * 3600 * 1000,
    '24h': now - 24 * 3600 * 1000,
    '7d': now - 7 * 24 * 3600 * 1000
  }
  return ranges[timeRange.value]
}

async function fetchHistory() {
  try {
    const endTime = Date.now()
    const startTime = getTimeRange()
    
    const result = await getHistoryMetrics(metricType.value, startTime, endTime, limit.value)
    historyData.value = result.data || []
  } catch (e) {
    console.error('获取历史数据失败:', e)
  }
}

function onTimeRangeChange() {
  fetchHistory()
}

function formatTime(timestamp) {
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN')
}

function formatValue(item) {
  if (metricType.value === 'cpu') {
    return item.cpu_percent?.toFixed(2) + '%'
  } else if (metricType.value === 'memory') {
    return item.percent?.toFixed(2) + '%'
  } else if (metricType.value === 'disk') {
    const mb = (item.read_bytes + item.write_bytes) / (1024 * 1024)
    return mb.toFixed(2) + ' MB/s'
  } else if (metricType.value === 'network') {
    const kb = (item.bytes_sent + item.bytes_recv) / 1024
    return kb.toFixed(2) + ' KB/s'
  }
  return '-'
}

onMounted(() => {
  fetchHistory()
})
</script>

<style scoped>
.history {
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

.controls {
  background: #fff;
  padding: 16px;
  border-radius: 8px;
  display: flex;
  gap: 16px;
  align-items: flex-end;
  margin-bottom: 20px;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.control-group label {
  font-size: 14px;
  color: #666;
}

.control-group select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.btn {
  padding: 8px 20px;
  background: #409EFF;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn:hover {
  background: #66b1ff;
}

.chart-container {
  background: #fff;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.chart {
  height: 400px;
}

.data-table {
  background: #fff;
  padding: 16px;
  border-radius: 8px;
}

.data-table h3 {
  margin: 0 0 12px 0;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 8px 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

th {
  background: #f5f7fa;
  font-weight: 500;
}
</style>
