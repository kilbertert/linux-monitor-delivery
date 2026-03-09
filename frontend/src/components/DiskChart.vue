<template>
  <div class="chart-container">
    <h3>磁盘 I/O</h3>
    <v-chart class="chart" :option="chartOption" autoresize />
  </div>
</template>

<script setup>
import { ref, defineProps } from 'vue'
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
  }
})

const chartOption = ref({
  tooltip: {
    trigger: 'axis'
  },
  legend: {
    data: ['读取', '写入'],
    bottom: 0
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '15%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: []
  },
  yAxis: {
    type: 'value',
    axisLabel: {
      formatter: '{value} MB/s'
    }
  },
  series: [
    {
      name: '读取',
      type: 'line',
      smooth: true,
      symbol: 'none',
      areaStyle: {
        color: 'rgba(64, 158, 255, 0.3)'
      },
      lineStyle: {
        color: '#409EFF',
        width: 2
      },
      data: []
    },
    {
      name: '写入',
      type: 'line',
      smooth: true,
      symbol: 'none',
      areaStyle: {
        color: 'rgba(245, 108, 108, 0.3)'
      },
      lineStyle: {
        color: '#F56C6C',
        width: 2
      },
      data: []
    }
  ]
})

function updateChart(data) {
  const timestamps = data.map(d => {
    const date = new Date(d.timestamp)
    return `${date.getHours()}:${date.getMinutes()}:${date.getSeconds()}`
  })
  
  chartOption.value = {
    ...chartOption.value,
    xAxis: {
      ...chartOption.value.xAxis,
      data: timestamps
    },
    series: [
      {
        ...chartOption.value.series[0],
        data: data.map(d => d.disk ? d.disk.read_rate : 0)
      },
      {
        ...chartOption.value.series[1],
        data: data.map(d => d.disk ? d.disk.write_rate : 0)
      }
    ]
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
