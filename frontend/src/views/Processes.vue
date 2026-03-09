<template>
  <div class="processes">
    <header class="header">
      <h1>进程监控</h1>
      <router-link to="/" class="back-link">← 返回仪表盘</router-link>
    </header>

    <div class="content">
      <div class="controls">
        <div class="control-group">
          <label>排序方式</label>
          <select v-model="sortBy">
            <option value="cpu">按 CPU 占用</option>
            <option value="memory">按内存占用</option>
          </select>
        </div>
        
        <div class="control-group">
          <label>显示数量</label>
          <select v-model="topN">
            <option :value="10">10 个</option>
            <option :value="20">20 个</option>
            <option :value="50">50 个</option>
          </select>
        </div>
        
        <button @click="fetchProcesses" class="btn">刷新</button>
        <button @click="autoRefresh" class="btn btn-secondary">{{ autoRefreshInterval ? '停止自动刷新' : '自动刷新' }}</button>
      </div>

      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>PID</th>
              <th>进程名称</th>
              <th>CPU %</th>
              <th>内存 %</th>
              <th>状态</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="proc in processes" :key="proc.pid">
              <td>{{ proc.pid }}</td>
              <td>{{ proc.name }}</td>
              <td :class="{'high': proc.cpu_percent > 50}">{{ proc.cpu_percent?.toFixed(1) }}%</td>
              <td :class="{'high': proc.memory_percent > 50}">{{ proc.memory_percent?.toFixed(1) }}%</td>
              <td>{{ proc.status }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { getTopCpuProcesses, getTopMemoryProcesses } from '../api'

const sortBy = ref('cpu')
const topN = ref(10)
const processes = ref([])
const autoRefreshInterval = ref(null)

async function fetchProcesses() {
  try {
    let result
    if (sortBy.value === 'cpu') {
      result = await getTopCpuProcesses(topN.value)
    } else {
      result = await getTopMemoryProcesses(topN.value)
    }
    processes.value = result.processes || []
  } catch (e) {
    console.error('获取进程失败:', e)
  }
}

function autoRefresh() {
  if (autoRefreshInterval.value) {
    clearInterval(autoRefreshInterval.value)
    autoRefreshInterval.value = null
  } else {
    fetchProcesses()
    autoRefreshInterval.value = setInterval(fetchProcesses, 2000)
  }
}

watch([sortBy, topN], () => {
  fetchProcesses()
  if (autoRefreshInterval.value) {
    clearInterval(autoRefreshInterval.value)
    autoRefreshInterval.value = setInterval(fetchProcesses, 2000)
  }
})

onMounted(() => {
  fetchProcesses()
})

onUnmounted(() => {
  if (autoRefreshInterval.value) {
    clearInterval(autoRefreshInterval.value)
  }
})
</script>

<style scoped>
.processes {
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

.btn-secondary {
  background: #67C23A;
}

.btn-secondary:hover {
  background: #85CE61;
}

.table-container {
  background: #fff;
  padding: 16px;
  border-radius: 8px;
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

.high {
  color: #F56C6C;
  font-weight: bold;
}
</style>
