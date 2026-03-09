<template>
  <div class="chart-container">
    <h3>内存使用</h3>
    <v-chart class="chart" :option="chartOption" autoresize />
    <div class="memory-info">
      <span>已用: {{ used }} GB</span>
      <span>可用: {{ available }} GB</span>
      <span>总计: {{ total }} GB</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { GaugeChart } from 'echarts/charts'
import { TooltipComponent } from 'echarts/components'
import VChart from 'vue-echarts'

use([CanvasRenderer, GaugeChart, TooltipComponent])

const props = defineProps({
  data: {
    type: Object,
    default: () => ({})
  }
})

const used = ref(0)
const available = ref(0)
const total = ref(0)

const chartOption = computed(() => ({
  tooltip: {
    formatter: '{a} <br/>{b}: {c}%'
  },
  series: [
    {
      name: '内存使用率',
      type: 'gauge',
      min: 0,
      max: 100,
      progress: {
        show: true,
        width: 18
      },
      axisLine: {
        lineStyle: {
          width: 18
        }
      },
      axisTick: {
        show: false
      },
      splitLine: {
        length: 15,
        lineStyle: {
          width: 2,
          color: '#999'
        }
      },
      axisLabel: {
        distance: 25,
        color: '#999',
        fontSize: 14,
        formatter: '{value}%'
      },
      anchor: {
        show: true,
        showAbove: true,
        size: 25,
        itemStyle: {
          borderWidth: 10
        }
      },
      title: {
        show: false
      },
      detail: {
        valueAnimation: true,
        fontSize: 30,
        offsetCenter: [0, '70%'],
        formatter: '{value}%'
      },
      data: [
        {
          value: props.data.percent || 0,
          name: '内存'
        }
      ]
    }
  ]
}))

function updateChart(data) {
  if (data) {
    used.value = data.used || 0
    available.value = data.available || 0
    total.value = data.total || 0
  }
}

defineExpose({ updateChart })
</script>

<style scoped>
.chart-container {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.chart-container h3 {
  margin: 0 0 12px 0;
  color: #333;
  font-size: 16px;
}

.chart {
  height: 250px;
  width: 100%;
}

.memory-info {
  display: flex;
  justify-content: space-around;
  margin-top: 12px;
  color: #666;
  font-size: 14px;
}
</style>
