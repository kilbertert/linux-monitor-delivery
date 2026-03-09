<template>
  <div class="system-info">
    <h3>系统信息</h3>
    <div class="info-grid">
      <div class="info-item">
        <span class="label">主机名</span>
        <span class="value">{{ info.hostname || '-' }}</span>
      </div>
      <div class="info-item">
        <span class="label">平台</span>
        <span class="value">{{ info.platform || '-' }}</span>
      </div>
      <div class="info-item">
        <span class="label">CPU 型号</span>
        <span class="value">{{ info.model || '-' }}</span>
      </div>
      <div class="info-item">
        <span class="label">CPU 核心数</span>
        <span class="value">{{ info.count || '-' }}</span>
      </div>
      <div class="info-item">
        <span class="label">内存总量</span>
        <span class="value">{{ info.memory_total ? info.memory_total + ' GB' : '-' }}</span>
      </div>
      <div class="info-item">
        <span class="label">磁盘总量</span>
        <span class="value">{{ info.disk_total ? info.disk_total + ' GB' : '-' }}</span>
      </div>
      <div class="info-item">
        <span class="label">运行时间</span>
        <span class="value">{{ uptime }}</span>
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

const uptime = computed(() => {
  if (!info.value.uptime) return '-'
  const now = Date.now() / 1000
  const up = now - info.value.uptime
  const days = Math.floor(up / 86400)
  const hours = Math.floor((up % 86400) / 3600)
  const minutes = Math.floor((up % 3600) / 60)
  return `${days}天 ${hours}小时 ${minutes}分钟`
})

async function fetchInfo() {
  try {
    info.value = await getSystemInfo()
  } catch (e) {
    console.error('获取系统信息失败:', e)
  }
}

onMounted(() => {
  fetchInfo()
})

function updateInfo(data) {
  if (data) {
    info.value = data
  }
}

defineExpose({ updateInfo, fetchInfo })
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
