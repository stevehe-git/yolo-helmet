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
          <el-card v-if="model?.metrics">
            <el-row :gutter="20">
              <el-col :span="6">
                <div class="metric-card">
                  <div class="metric-value">{{ (model.metrics.map * 100).toFixed(2) }}%</div>
                  <div class="metric-label">mAP</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="metric-card">
                  <div class="metric-value">{{ (model.metrics.precision * 100).toFixed(2) }}%</div>
                  <div class="metric-label">精确率</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="metric-card">
                  <div class="metric-value">{{ (model.metrics.recall * 100).toFixed(2) }}%</div>
                  <div class="metric-label">召回率</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="metric-card">
                  <div class="metric-value">{{ (model.metrics.f1 * 100).toFixed(2) }}%</div>
                  <div class="metric-label">F1值</div>
                </div>
              </el-col>
            </el-row>
          </el-card>
          <el-empty v-else description="暂无性能指标数据" />
        </el-tab-pane>

        <el-tab-pane label="训练数据" name="training">
          <div v-if="trainingData" class="training-charts">
            <el-card style="margin-bottom: 20px">
              <template #header>
                <span>损失曲线</span>
              </template>
              <div ref="lossChartRef" style="height: 300px"></div>
            </el-card>
            <el-card>
              <template #header>
                <span>性能指标曲线</span>
              </template>
              <div ref="metricsChartRef" style="height: 300px"></div>
            </el-card>
          </div>
          <el-empty v-else description="暂无训练数据" />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { modelApi, type Model, type ModelTrainingData } from '../api/model'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const route = useRoute()
const model = ref<Model | null>(null)
const trainingData = ref<ModelTrainingData | null>(null)
const activeTab = ref('info')
const lossChartRef = ref<HTMLDivElement | null>(null)
const metricsChartRef = ref<HTMLDivElement | null>(null)

const loadModel = async () => {
  const id = parseInt(route.params.id as string)
  try {
    model.value = await modelApi.getModel(id)
    if (model.value.type === 'custom') {
      trainingData.value = await modelApi.getModelTrainingData(id)
      await nextTick()
      initCharts()
    }
  } catch (error) {
    ElMessage.error('加载模型信息失败')
  }
}

const initCharts = () => {
  if (!trainingData.value) return

  // Loss chart
  if (lossChartRef.value) {
    const lossChart = echarts.init(lossChartRef.value)
    lossChart.setOption({
      title: { text: '训练损失曲线' },
      tooltip: { trigger: 'axis' },
      legend: { data: ['训练损失', '验证损失'] },
      xAxis: { type: 'category', data: trainingData.value.epochs.map(e => `Epoch ${e}`) },
      yAxis: { type: 'value' },
      series: [
        {
          name: '训练损失',
          type: 'line',
          data: trainingData.value.train_loss
        },
        {
          name: '验证损失',
          type: 'line',
          data: trainingData.value.val_loss
        }
      ]
    })
  }

  // Metrics chart
  if (metricsChartRef.value) {
    const metricsChart = echarts.init(metricsChartRef.value)
    metricsChart.setOption({
      title: { text: '性能指标曲线' },
      tooltip: { trigger: 'axis' },
      legend: { data: ['mAP', '精确率', '召回率'] },
      xAxis: { type: 'category', data: trainingData.value.epochs.map(e => `Epoch ${e}`) },
      yAxis: { type: 'value', max: 1 },
      series: [
        {
          name: 'mAP',
          type: 'line',
          data: trainingData.value.map
        },
        {
          name: '精确率',
          type: 'line',
          data: trainingData.value.precision
        },
        {
          name: '召回率',
          type: 'line',
          data: trainingData.value.recall
        }
      ]
    })
  }
}

onMounted(() => {
  loadModel()
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

