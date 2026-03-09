<template>
  <div class="system-info">
    <h3>系统信息</h3>
    <div class="info-grid">
      <div class="info-item">
        <span class="label">主机名</span>
        <span class="value">{{ systemData.hostname || info.hostname || '-' }}</span>
      </div>
      <div class="info-item">
        <span class="label">平台</span>
        <span class="value">{{ systemData.platform || info.platform || '-' }}</span>
      </div>
      <div class="info-item">
        <span class="label">CPU 型号</span>
        <span class="value">{{ systemData.model || info.model || '-' }}</span>
      </div>
      <div class="info-item">
        <span class="label">CPU 核心数</span>
        <span class="value">{{ systemData.count || cpuCount || '-' }}</span>
      </div>
      <div class="info-item">
        <span class="label">内存总量</span>
        <span class="value">{{ systemData.memory_total ? systemData.memory_total + ' GB' : (info.memory_total ? info.memory_total + ' GB' : '-') }}</span>
      </div>
      <div class="info-item">
        <span class="label">磁盘总量</span>
        <span class="value">{{ systemData.disk_total ? systemData.disk_total + ' GB' : (info.disk_total ? info.disk_total + ' GB' : '-') }}</span>
      </div>
      <div class="info-item">
        <span class="label">运行时间</span>
        <span class="value">{{ systemUptime }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getSystemInfo } from '../api'

const props = defineProps({
  data: {
    type: Object,
    default: () => ({})
  }
})

const info = ref({})
const systemData = ref({})
const cpuCount = ref(0)

// 从实时数据中提取系统信息
const systemInfoFromData = computed(() => {
  if (props.data?.cpu?.count) {
    return {
      count: props.data.cpu.count
    }
  }
  return {}
})

// 运行时间计算
const systemUptime = computed(() => {
  const uptime = systemData.value.uptime || info.value.uptime
  if (!uptime) return '-'
  const now = Date.now() / 1000
  const up = now - uptime
  if (up <= 0) return '-'
  const days = Math.floor(up / 86400)
  const hours = Math.floor((up % 86400) / 3600)
  const minutes = Math.floor((up % 3600) / 60)
  return `${days}天 ${hours}小时 ${minutes}分钟`
})

async function fetchSystemInfo() {
  try {
    const data = await getSystemInfo()
    systemData.value = data
    cpuCount.value = data.count || 0
  } catch (e) {
    console.error('获取系统信息失败:', e)
  }
}

function updateInfo(data) {
  if (data) {
    info.value = data
    // 从实时数据中提取 CPU 核心数
    if (data.cpu?.count) {
      cpuCount.value = data.cpu.count
    }
  }
}

onMounted(() => {
  fetchSystemInfo()
})

defineExpose({ updateInfo, fetchSystemInfo })
</script>

<style scoped>
.system-info {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.system-info h3 {
  margin: 0 0 12px 0;
  color: #333;
  font-size: 16px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.info-item {
  display: flex;
  flex-direction: column;
}

.info-item .label {
  color: #999;
  font-size: 12px;
  margin-bottom: 4px;
}

.info-item .value {
  color: #333;
  font-size: 14px;
  word-break: break-all;
}
</style>
