<template>
  <div class="console-container">
    <el-row :gutter="20">
      <el-col :span="6" v-for="stat in statCards" :key="stat.label">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>检测趋势</span>
          </template>
          <div ref="trendChartRef" style="height: 300px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>检测分布</span>
          </template>
          <div ref="distributionChartRef" style="height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>每日检测统计</span>
          </template>
          <div ref="dailyChartRef" style="height: 400px"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { statisticsApi } from '../api/statistics'
import * as echarts from 'echarts'
import type { ECharts } from 'echarts'

const statistics = ref({
  total_detections: 0,
  with_helmet: 0,
  without_helmet: 0,
  detection_rate: 0,
  daily_stats: [] as Array<{ date: string; count: number }>
})

const trendChartRef = ref<HTMLDivElement | null>(null)
const distributionChartRef = ref<HTMLDivElement | null>(null)
const dailyChartRef = ref<HTMLDivElement | null>(null)

let trendChart: ECharts | null = null
let distributionChart: ECharts | null = null
let dailyChart: ECharts | null = null

const statCards = computed(() => [
  {
    label: '总检测次数',
    value: statistics.value.total_detections
  },
  {
    label: '佩戴安全帽',
    value: statistics.value.with_helmet
  },
  {
    label: '未佩戴安全帽',
    value: statistics.value.without_helmet
  },
  {
    label: '检测率',
    value: `${(statistics.value.detection_rate * 100).toFixed(1)}%`
  }
])

// 检查DOM元素是否有有效的尺寸
const checkElementSize = (element: HTMLElement | null): boolean => {
  if (!element) return false
  const rect = element.getBoundingClientRect()
  return rect.width > 0 && rect.height > 0
}

// 初始化单个图表
const initChart = (chartRef: HTMLElement | null, chartInstance: ECharts | null, setOptionFn: (chart: ECharts) => void): ECharts | null => {
  if (!chartRef) return null
  
  // 检查元素尺寸
  if (!checkElementSize(chartRef)) {
    // 如果元素没有尺寸，延迟初始化
    setTimeout(() => {
      if (checkElementSize(chartRef)) {
        const chart = echarts.init(chartRef)
        setOptionFn(chart)
      }
    }, 100)
    return null
  }
  
  // 如果已有实例，先销毁
  if (chartInstance) {
    chartInstance.dispose()
  }
  
  try {
    const chart = echarts.init(chartRef)
    setOptionFn(chart)
    return chart
  } catch (error) {
    console.error('Failed to init chart:', error)
    return null
  }
}

const loadStatistics = async () => {
  try {
    const stats = await statisticsApi.getStatistics()
    statistics.value = stats
    await nextTick()
    // 使用 requestAnimationFrame 确保 DOM 完全渲染
    requestAnimationFrame(() => {
      setTimeout(() => {
        initCharts()
      }, 50)
    })
  } catch (error) {
    console.error('Failed to load statistics:', error)
  }
}

const initCharts = () => {
  // Trend chart
  if (trendChartRef.value) {
    const dates = statistics.value.daily_stats.map(s => s.date)
    const counts = statistics.value.daily_stats.map(s => s.count)
    
    trendChart = initChart(trendChartRef.value, trendChart, (chart) => {
      chart.setOption({
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: dates },
        yAxis: { type: 'value' },
        series: [{
          data: counts,
          type: 'line',
          smooth: true,
          areaStyle: {}
        }]
      })
    })
  }

  // Distribution chart
  if (distributionChartRef.value) {
    distributionChart = initChart(distributionChartRef.value, distributionChart, (chart) => {
      chart.setOption({
        tooltip: { trigger: 'item' },
        series: [{
          type: 'pie',
          radius: '60%',
          data: [
            { value: statistics.value.with_helmet, name: '佩戴安全帽' },
            { value: statistics.value.without_helmet, name: '未佩戴安全帽' }
          ],
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }]
      })
    })
  }

  // Daily chart - 显示 image, video, realtime 三种类型的检测次数
  if (dailyChartRef.value) {
    const dates = statistics.value.daily_stats.map(s => s.date)
    const imageCounts = statistics.value.daily_stats.map(s => s.image || 0)
    const videoCounts = statistics.value.daily_stats.map(s => s.video || 0)
    const realtimeCounts = statistics.value.daily_stats.map(s => s.realtime || 0)
    
    dailyChart = initChart(dailyChartRef.value, dailyChart, (chart) => {
      chart.setOption({
        tooltip: { 
          trigger: 'axis',
          axisPointer: { type: 'shadow' }
        },
        legend: {
          data: ['图片检测', '视频检测', '实时检测'],
          top: 10
        },
        xAxis: { 
          type: 'category', 
          data: dates,
          axisLabel: {
            rotate: 45,
            interval: 0
          }
        },
        yAxis: { type: 'value' },
        series: [
          {
            name: '图片检测',
            data: imageCounts,
            type: 'bar',
            itemStyle: {
              color: '#5470c6'
            }
          },
          {
            name: '视频检测',
            data: videoCounts,
            type: 'bar',
            itemStyle: {
              color: '#91cc75'
            }
          },
          {
            name: '实时检测',
            data: realtimeCounts,
            type: 'bar',
            itemStyle: {
              color: '#fac858'
            }
          }
        ]
      })
    })
  }
}

// 窗口大小变化时调整图表
const handleResize = () => {
  if (trendChart) trendChart.resize()
  if (distributionChart) distributionChart.resize()
  if (dailyChart) dailyChart.resize()
}

onMounted(() => {
  loadStatistics()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (trendChart) trendChart.dispose()
  if (distributionChart) distributionChart.dispose()
  if (dailyChart) dailyChart.dispose()
})
</script>

<style scoped>
.console-container {
  padding: 20px;
}

.stat-card {
  margin-bottom: 20px;
}

.stat-content {
  text-align: center;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 10px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}
</style>

