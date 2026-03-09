<template>
  <div class="chart-container">
    <h3>CPU 使用率</h3>
    <v-chart class="chart" :option="chartOption" autoresize />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, defineProps } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent, LegendComponent])

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  isLive: {
    type: Boolean,
    default: true
  }
})

const chartOption = ref({
  tooltip: {
    trigger: 'axis',
    formatter: '{b}<br />CPU: {c}%'
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
    data: []
  },
  yAxis: {
    type: 'value',
    min: 0,
    max: 100,
    axisLabel: {
      formatter: '{value}%'
    }
  },
  series: [
    {
      name: 'CPU使用率',
      type: 'line',
      smooth: true,
      symbol: 'none',
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(64, 158, 255, 0.5)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.1)' }
          ]
        }
      },
      lineStyle: {
        color: '#409EFF',
        width: 2
      },
      data: []
    }
  ]
})

// 更新图表数据
function updateChart(data) {
  // 支持两种数据格式：
  // 1. 历史数据: [{cpu: {percent: 10}, memory: {...}, ...}, ...]
  // 2. 单条数据: {cpu: {percent: 10}, ...}
  
  if (!data || (Array.isArray(data) && data.length === 0)) {
    return
  }
  
  let timestamps = []
  let values = []
  
  if (Array.isArray(data)) {
    // 历史数据数组
    timestamps = data.map(d => {
      const date = new Date(d.timestamp || d.timestamp || Date.now())
      return `${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}:${String(date.getSeconds()).padStart(2, '0')}`
    })
    values = data.map(d => d.cpu?.percent || d.cpu_percent || 0)
  } else {
    // 单条实时数据
    timestamps = [new Date().toLocaleTimeString()]
    values = [data.cpu?.percent || data.cpu_percent || 0]
  }

  chartOption.value = {
    ...chartOption.value,
    xAxis: {
      ...chartOption.value.xAxis,
      data: timestamps
    },
    series: [{
      ...chartOption.value.series[0],
      data: values
    }]
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
</style>
