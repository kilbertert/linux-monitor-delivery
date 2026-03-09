<template>
  <div class="chart-container">
    <h3>网络带宽</h3>
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
    data: ['上传', '下载'],
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
      formatter: '{value} KB/s'
    }
  },
  series: [
    {
      name: '上传',
      type: 'line',
      smooth: true,
      symbol: 'none',
      areaStyle: {
        color: 'rgba(103, 194, 58, 0.3)'
      },
      lineStyle: {
        color: '#67C23A',
        width: 2
      },
      data: []
    },
    {
      name: '下载',
      type: 'line',
      smooth: true,
      symbol: 'none',
      areaStyle: {
        color: 'rgba(230, 162, 60, 0.3)'
      },
      lineStyle: {
        color: '#E6A23C',
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
  
  // 需要历史数据来绘制曲线，这里先显示实时速率
  const latest = data[data.length - 1] || {}
  
  chartOption.value = {
    ...chartOption.value,
    xAxis: {
      ...chartOption.value.xAxis,
      data: timestamps
    },
    series: [
      {
        ...chartOption.value.series[0],
        data: data.map(d => d.network ? d.network.send_rate : 0)
      },
      {
        ...chartOption.value.series[1],
        data: data.map(d => d.network ? d.network.recv_rate : 0)
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
