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
import { ref, computed, onMounted, nextTick } from 'vue'
import { statisticsApi } from '../api/statistics'
import * as echarts from 'echarts'

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

const loadStatistics = async () => {
  try {
    const stats = await statisticsApi.getStatistics()
    statistics.value = stats
    await nextTick()
    initCharts()
  } catch (error) {
    console.error('Failed to load statistics:', error)
  }
}

const initCharts = () => {
  // Trend chart
  if (trendChartRef.value) {
    const trendChart = echarts.init(trendChartRef.value)
    const dates = statistics.value.daily_stats.map(s => s.date)
    const counts = statistics.value.daily_stats.map(s => s.count)
    
    trendChart.setOption({
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
  }

  // Distribution chart
  if (distributionChartRef.value) {
    const distributionChart = echarts.init(distributionChartRef.value)
    distributionChart.setOption({
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
  }

  // Daily chart
  if (dailyChartRef.value) {
    const dailyChart = echarts.init(dailyChartRef.value)
    const dates = statistics.value.daily_stats.map(s => s.date)
    const counts = statistics.value.daily_stats.map(s => s.count)
    
    dailyChart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: dates },
      yAxis: { type: 'value' },
      series: [{
        data: counts,
        type: 'bar',
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#83bff6' },
            { offset: 0.5, color: '#188df0' },
            { offset: 1, color: '#188df0' }
          ])
        }
      }]
    })
  }
}

onMounted(() => {
  loadStatistics()
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

