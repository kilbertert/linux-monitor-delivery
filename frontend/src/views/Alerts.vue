<template>
  <div class="alerts">
    <header class="header">
      <h1>告警管理</h1>
      <router-link to="/" class="back-link">← 返回仪表盘</router-link>
    </header>

    <div class="content">
      <div class="summary">
        <div class="summary-item">
          <span class="label">启用规则</span>
          <span class="value">{{ enabledCount }}</span>
        </div>
        <div class="summary-item">
          <span class="label">禁用规则</span>
          <span class="value">{{ rules.length - enabledCount }}</span>
        </div>
        <button @click="fetchRules" class="btn">刷新</button>
      </div>

      <div class="rules-container">
        <h3>告警规则</h3>
        <div class="rules-list">
          <div v-for="rule in rules" :key="rule.name" class="rule-card" :class="{ disabled: !rule.enabled }">
            <div class="rule-header">
              <span class="rule-name">{{ rule.name }}</span>
              <el-switch 
                v-model="rule.enabled" 
                @change="toggleRule(rule.name)"
                :active-text="'启用'"
                :inactive-text="'禁用'"
              />
            </div>
            <div class="rule-body">
              <div class="rule-item">
                <span class="label">指标:</span>
                <span class="value">{{ rule.metric }}</span>
              </div>
              <div class="rule-item">
                <span class="label">条件:</span>
                <span class="value">{{ rule.operator }} {{ rule.threshold }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="alerts-log">
        <h3>告警记录</h3>
        <div class="log-list">
          <div v-for="(alert, index) in alertLogs" :key="index" class="alert-item">
            <span class="alert-time">{{ alert.timestamp }}</span>
            <span class="alert-rule">{{ alert.rule }}</span>
            <span class="alert-value">{{ alert.value?.toFixed(1) }} {{ alert.metric }}</span>
          </div>
          <div v-if="alertLogs.length === 0" class="empty">暂无告警记录</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { getAlertRules, toggleAlertRule } from '../api'

const rules = ref([])
const alertLogs = ref([])
let ws = null

const enabledCount = computed(() => rules.value.filter(r => r.enabled).length)

async function fetchRules() {
  try {
    const result = await getAlertRules()
    rules.value = result.rules || []
  } catch (e) {
    console.error('获取告警规则失败:', e)
  }
}

async function toggleRule(ruleName) {
  try {
    await toggleAlertRule(ruleName)
  } catch (e) {
    console.error('切换规则失败:', e)
    fetchRules()
  }
}

function connectWebSocket() {
  const wsUrl = `ws://172.21.144.1:8000/ws/metrics`
  try {
    ws = new WebSocket(wsUrl)
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        // 处理告警数据（需要后端推送）
      } catch (e) {
        console.error('解析失败:', e)
      }
    }
  } catch (e) {
    console.error('WebSocket 连接失败:', e)
  }
}

onMounted(() => {
  fetchRules()
  // connectWebSocket()
})

onUnmounted(() => {
  if (ws) ws.close()
})
</script>

<style scoped>
.alerts {
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

.summary {
  background: #fff;
  padding: 16px;
  border-radius: 8px;
  display: flex;
  gap: 24px;
  align-items: center;
  margin-bottom: 20px;
}

.summary-item {
  display: flex;
  flex-direction: column;
}

.summary-item .label {
  font-size: 14px;
  color: #666;
}

.summary-item .value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.btn {
  padding: 8px 20px;
  background: #409EFF;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-left: auto;
}

.rules-container {
  background: #fff;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.rules-container h3 {
  margin: 0 0 16px 0;
}

.rules-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.rule-card {
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 16px;
}

.rule-card.disabled {
  opacity: 0.6;
}

.rule-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.rule-name {
  font-weight: bold;
  color: #333;
}

.rule-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.rule-item {
  display: flex;
  gap: 8px;
}

.rule-item .label {
  color: #999;
}

.rule-item .value {
  color: #666;
}

.alerts-log {
  background: #fff;
  padding: 16px;
  border-radius: 8px;
}

.alerts-log h3 {
  margin: 0 0 16px 0;
}

.log-list {
  max-height: 300px;
  overflow-y: auto;
}

.alert-item {
  display: flex;
  gap: 16px;
  padding: 8px 0;
  border-bottom: 1px solid #eee;
}

.alert-time {
  color: #999;
  font-size: 14px;
}

.alert-rule {
  color: #F56C6C;
  font-weight: 500;
}

.alert-value {
  color: #666;
}

.empty {
  color: #999;
  text-align: center;
  padding: 20px;
}
</style>
