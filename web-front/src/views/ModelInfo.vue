<template>
  <div class="model-info-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>模型详情 - {{ model?.name }}</span>
          <el-button @click="$router.back()">返回</el-button>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="基本信息" name="info">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="模型ID">{{ model?.id }}</el-descriptions-item>
            <el-descriptions-item label="模型名称">{{ model?.name }}</el-descriptions-item>
            <el-descriptions-item label="模型类型">
              <el-tag :type="model?.type === 'general' ? 'success' : 'warning'">
                {{ model?.type === 'general' ? '通用模型' : '定制模型' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ model?.created_at }}</el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>

        <el-tab-pane label="性能指标" name="metrics">
          <el-card v-if="model?.metrics && !model.metrics.error">
            <el-row :gutter="20">
              <el-col :span="6">
                <div class="metric-card">
                  <div class="metric-value">
                    {{ model.metrics.map !== undefined && !isNaN(model.metrics.map) 
                      ? (model.metrics.map * 100).toFixed(2) + '%' 
                      : '-' }}
                  </div>
                  <div class="metric-label">mAP</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="metric-card">
                  <div class="metric-value">
                    {{ model.metrics.precision !== undefined && !isNaN(model.metrics.precision) 
                      ? (model.metrics.precision * 100).toFixed(2) + '%' 
                      : '-' }}
                  </div>
                  <div class="metric-label">精确率</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="metric-card">
                  <div class="metric-value">
                    {{ model.metrics.recall !== undefined && !isNaN(model.metrics.recall) 
                      ? (model.metrics.recall * 100).toFixed(2) + '%' 
                      : '-' }}
                  </div>
                  <div class="metric-label">召回率</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="metric-card">
                  <div class="metric-value">
                    {{ model.metrics.f1 !== undefined && !isNaN(model.metrics.f1) 
                      ? (model.metrics.f1 * 100).toFixed(2) + '%' 
                      : '-' }}
                  </div>
                  <div class="metric-label">F1值</div>
                </div>
              </el-col>
            </el-row>
          </el-card>
          <el-card v-else-if="model?.metrics && model.metrics.error" class="error-card">
            <el-alert
              :title="`训练失败: ${model.metrics.error}`"
              type="error"
              :closable="false"
            />
          </el-card>
          <el-empty v-else description="暂无性能指标数据" />
        </el-tab-pane>

        <el-tab-pane label="训练数据" name="training">
          <div v-if="trainingData && trainingData.epochs && trainingData.epochs.length > 0" class="training-charts">
            <el-card style="margin-bottom: 20px">
              <template #header>
                <span>损失曲线</span>
              </template>
              <div style="padding: 10px 0;">
                <div style="font-size: 14px; color: #909399; margin-bottom: 10px;">训练损失曲线</div>
                <div ref="lossChartRef" style="height: 300px"></div>
              </div>
            </el-card>
            <el-card>
              <template #header>
                <span>性能指标曲线</span>
              </template>
              <div style="padding: 10px 0;">
                <div style="font-size: 14px; color: #909399; margin-bottom: 10px;">性能指标曲线</div>
                <div ref="metricsChartRef" style="height: 300px"></div>
              </div>
            </el-card>
          </div>
          <el-empty v-else description="暂无训练数据（模型文件或训练数据文件不存在）" />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import { modelApi, type Model, type ModelTrainingData } from '../api/model'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import type { ECharts } from 'echarts'

const route = useRoute()
const model = ref<Model | null>(null)
const trainingData = ref<ModelTrainingData | null>(null)
const activeTab = ref('info')
const lossChartRef = ref<HTMLDivElement | null>(null)
const metricsChartRef = ref<HTMLDivElement | null>(null)

let lossChart: ECharts | null = null
let metricsChart: ECharts | null = null

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

const loadModel = async () => {
  const id = parseInt(route.params.id as string)
  try {
    model.value = await modelApi.getModel(id)
    
    // 对于自定义模型，尝试加载训练数据
    // 只有在模型文件明确不存在时才不加载训练数据
    // 如果file_exists为undefined或true，都尝试加载
    if (model.value.type === 'custom' && model.value.status === 'completed') {
      // 只有当file_exists明确为false时才跳过
      if (model.value && (model.value as any).file_exists === false) {
        ElMessage.warning('模型文件不存在，无法显示训练数据')
        trainingData.value = null
        return
      }
      
      try {
        const data = await modelApi.getModelTrainingData(id)
        // 检查是否有错误或数据为空
        if (data && !(data as any).error && data.epochs && data.epochs.length > 0) {
          trainingData.value = data
          await nextTick()
          // 如果当前在训练数据tab，初始化图表
          if (activeTab.value === 'training') {
            initCharts()
          }
        } else {
          trainingData.value = null
        }
      } catch (error: any) {
        // 如果返回404或错误，不显示训练数据
        if (error.response?.status === 404) {
          trainingData.value = null
        } else {
          console.error('Failed to load training data:', error)
          trainingData.value = null
        }
      }
    } else {
      trainingData.value = null
    }
  } catch (error) {
    ElMessage.error('加载模型信息失败')
  }
}

const initCharts = () => {
  if (!trainingData.value) return

  // Loss chart
  if (lossChartRef.value && trainingData.value) {
    lossChart = initChart(lossChartRef.value, lossChart, (chart) => {
      chart.setOption({
        title: { text: '训练损失曲线' },
        tooltip: { trigger: 'axis' },
        legend: { data: ['训练损失', '验证损失'] },
        xAxis: { type: 'category', data: trainingData.value!.epochs.map(e => `Epoch ${e}`) },
        yAxis: { type: 'value' },
        series: [
          {
            name: '训练损失',
            type: 'line',
            data: trainingData.value!.train_loss
          },
          {
            name: '验证损失',
            type: 'line',
            data: trainingData.value!.val_loss
          }
        ]
      })
    })
  }

  // Metrics chart
  if (metricsChartRef.value && trainingData.value) {
    metricsChart = initChart(metricsChartRef.value, metricsChart, (chart) => {
      chart.setOption({
        title: { text: '性能指标曲线' },
        tooltip: { trigger: 'axis' },
        legend: { data: ['mAP', '精确率', '召回率'] },
        xAxis: { type: 'category', data: trainingData.value!.epochs.map(e => `Epoch ${e}`) },
        yAxis: { type: 'value', max: 1 },
        series: [
          {
            name: 'mAP',
            type: 'line',
            data: trainingData.value!.map
          },
          {
            name: '精确率',
            type: 'line',
            data: trainingData.value!.precision
          },
          {
            name: '召回率',
            type: 'line',
            data: trainingData.value!.recall
          }
        ]
      })
    })
  }
}

// 监听tab切换，当切换到训练数据tab时初始化图表
watch(activeTab, (newTab) => {
  if (newTab === 'training' && trainingData.value) {
    // 使用 nextTick 和 setTimeout 确保 tab 内容已渲染
    nextTick(() => {
      requestAnimationFrame(() => {
        setTimeout(() => {
          initCharts()
        }, 100)
      })
    })
  }
})

// 窗口大小变化时调整图表
const handleResize = () => {
  if (lossChart) lossChart.resize()
  if (metricsChart) metricsChart.resize()
}

onMounted(() => {
  loadModel()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (lossChart) lossChart.dispose()
  if (metricsChart) metricsChart.dispose()
})
</script>

<style scoped>
.model-info-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metric-card {
  text-align: center;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 4px;
}

.metric-value {
  font-size: 32px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 10px;
}

.metric-label {
  font-size: 14px;
  color: #909399;
}

.training-charts {
  margin-top: 20px;
}
</style>

