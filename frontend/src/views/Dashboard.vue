<template>
  <div class="dashboard">
    <header class="header">
      <h1>Linux 运行监控系统</h1>
      <div class="header-actions">
        <router-link to="/history" class="history-link">历史数据</router-link>
        <div class="status">
          <span :class="['status-dot', connected ? 'online' : 'offline']"></span>
          {{ connected ? '已连接' : '未连接' }}
        </div>
      </div>
    </header>

    <div class="content">
      <div class="grid">
        <CpuChart ref="cpuChartRef" :data="historyData" />
        <MemoryGauge ref="memoryChartRef" :data="currentData.memory" />
        <DiskChart ref="diskChartRef" :data="historyData" />
        <NetworkChart ref="networkChartRef" :data="historyData" />
        <SystemInfo ref="systemInfoRef" :data="currentData" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import CpuChart from '../components/CpuChart.vue'
import MemoryGauge from '../components/MemoryGauge.vue'
import DiskChart from '../components/DiskChart.vue'
import NetworkChart from '../components/NetworkChart.vue'
import SystemInfo from '../components/SystemInfo.vue'
import { getCurrentMetrics } from '../api'

const cpuChartRef = ref(null)
const memoryChartRef = ref(null)
const diskChartRef = ref(null)
const networkChartRef = ref(null)
const systemInfoRef = ref(null)

const connected = ref(false)
const currentData = ref({})
const historyData = ref([])

let ws = null
let pollTimer = null

// WebSocket 连接
function connectWebSocket() {
  const wsUrl = `ws://${window.location.host}/ws/metrics`
  // 尝试连接，使用轮询作为后备
  try {
    ws = new WebSocket(wsUrl)
    
    ws.onopen = () => {
      console.log('WebSocket 已连接')
      connected.value = true
      ws.send(JSON.stringify({ action: 'subscribe', metrics: ['cpu', 'memory', 'disk', 'network'], interval: 1 }))
    }
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.cpu) {
          updateData(data)
        }
      } catch (e) {
        console.error('解析 WebSocket 数据失败:', e)
      }
    }
    
    ws.onclose = () => {
      console.log('WebSocket 已断开')
      connected.value = false
      // 5秒后重连
      setTimeout(connectWebSocket, 5000)
    }
    
    ws.onerror = (error) => {
      console.error('WebSocket 错误:', error)
      connected.value = false
    }
  } catch (e) {
    console.error('WebSocket 连接失败:', e)
    startPolling()
  }
}

// 轮询获取数据（WebSocket 后备）
function startPolling() {
  pollTimer = setInterval(async () => {
    try {
      const data = await getCurrentMetrics()
      updateData(data)
      connected.value = true
    } catch (e) {
      console.error('获取数据失败:', e)
      connected.value = false
    }
  }, 1000)
}

function updateData(data) {
  currentData.value = data
  
  // 添加到历史数据
  historyData.value.push({ ...data })
  
  // 限制历史数据长度
  if (historyData.value.length > 60) {
    historyData.value.shift()
  }
  
  // 更新图表
  if (cpuChartRef.value) cpuChartRef.value.updateChart(historyData.value)
  if (memoryChartRef.value) memoryChartRef.value.updateChart(data.memory)
  if (diskChartRef.value) diskChartRef.value.updateChart(historyData.value)
  if (networkChartRef.value) networkChartRef.value.updateChart(historyData.value)
  if (systemInfoRef.value) systemInfoRef.value.updateInfo(data)
}

onMounted(() => {
  connectWebSocket()
})

onUnmounted(() => {
  if (ws) ws.close()
  if (pollTimer) clearInterval(pollTimer)
})
</script>

<style scoped>
.dashboard {
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

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.history-link {
  color: #409EFF;
  text-decoration: none;
  font-size: 14px;
}

.history-link:hover {
  text-decoration: underline;
}

.status {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #666;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-dot.online {
  background: #67C23A;
}

.status-dot.offline {
  background: #F56C6C;
}

.content {
  padding: 24px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

@media (max-width: 1200px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>
