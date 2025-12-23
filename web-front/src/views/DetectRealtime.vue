<template>
  <div class="detect-realtime-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>实时检测</span>
          <el-select v-model="selectedModelId" placeholder="选择模型" style="width: 200px" clearable>
            <el-option
              v-for="model in models"
              :key="model.id"
              :label="model.name"
              :value="model.id"
            />
          </el-select>
        </div>
      </template>

      <div class="control-panel">
        <el-button
          type="primary"
          :disabled="isRunning"
          @click="startDetection"
          :loading="starting"
        >
          开始检测
        </el-button>
        <el-button
          type="danger"
          :disabled="!isRunning"
          @click="stopDetection"
          :loading="stopping"
        >
          停止检测
        </el-button>
        <el-button @click="clearCanvas">清除画面</el-button>
      </div>

      <div class="video-section">
        <el-row :gutter="20">
          <el-col :span="16">
            <el-card>
              <template #header>
                <span>实时画面</span>
              </template>
              <div class="video-container">
                <video
                  ref="videoElement"
                  autoplay
                  playsinline
                  class="video-element"
                ></video>
                <canvas ref="canvasElement" style="display: none"></canvas>
                <div v-if="!isRunning" class="placeholder">
                  <el-icon :size="60"><VideoCamera /></el-icon>
                  <p>点击"开始检测"启动实时检测</p>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card>
              <template #header>
                <span>检测统计</span>
              </template>
              <div class="stats">
                <div class="stat-item">
                  <span class="label">总检测数:</span>
                  <span class="value">{{ stats.total }}</span>
                </div>
                <div class="stat-item">
                  <span class="label">佩戴安全帽:</span>
                  <span class="value success">{{ stats.withHelmet }}</span>
                </div>
                <div class="stat-item">
                  <span class="label">未佩戴安全帽:</span>
                  <span class="value danger">{{ stats.withoutHelmet }}</span>
                </div>
                <div class="stat-item">
                  <span class="label">检测率:</span>
                  <span class="value">{{ detectionRate }}%</span>
                </div>
              </div>

              <el-divider />

              <div class="recent-detections">
                <h4>最近检测</h4>
                <el-scrollbar height="200px">
                  <div
                    v-for="(detection, index) in recentDetections"
                    :key="index"
                    class="detection-item"
                  >
                    <span class="detection-time">{{ detection.time }}</span>
                    <el-tag :type="detection.type === 'with_helmet' ? 'success' : 'danger'">
                      {{ detection.type === 'with_helmet' ? '佩戴' : '未佩戴' }}
                    </el-tag>
                    <span class="detection-confidence">
                      置信度: {{ (detection.confidence * 100).toFixed(1) }}%
                    </span>
                  </div>
                </el-scrollbar>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { detectApi } from '../api/detect'
import { modelApi, type Model } from '../api/model'
import { ElMessage } from 'element-plus'
import { VideoCamera } from '@element-plus/icons-vue'

const models = ref<Model[]>([])
const selectedModelId = ref<number | undefined>()
const videoElement = ref<HTMLVideoElement | null>(null)
const canvasElement = ref<HTMLCanvasElement | null>(null)
const isRunning = ref(false)
const starting = ref(false)
const stopping = ref(false)
const stats = ref({
  total: 0,
  withHelmet: 0,
  withoutHelmet: 0
})
const recentDetections = ref<Array<{
  time: string
  type: 'with_helmet' | 'without_helmet'
  confidence: number
}>>([])

let stream: MediaStream | null = null
let frameInterval: number | null = null

const detectionRate = computed(() => {
  if (stats.value.total === 0) return 0
  return ((stats.value.withHelmet / stats.value.total) * 100).toFixed(1)
})

const startDetection = async () => {
  starting.value = true
  try {
    // Request camera access
    stream = await navigator.mediaDevices.getUserMedia({ video: true })
    if (videoElement.value) {
      videoElement.value.srcObject = stream
    }

    // Start backend detection
    await detectApi.startRealtime(selectedModelId.value)

    isRunning.value = true
    startFrameCapture()
    ElMessage.success('实时检测已启动')
  } catch (error: any) {
    ElMessage.error('无法访问摄像头: ' + (error.message || '未知错误'))
  } finally {
    starting.value = false
  }
}

const stopDetection = async () => {
  stopping.value = true
  try {
    await detectApi.stopRealtime()
    
    if (stream) {
      stream.getTracks().forEach(track => track.stop())
      stream = null
    }
    
    if (frameInterval) {
      clearInterval(frameInterval)
      frameInterval = null
    }
    
    if (videoElement.value) {
      videoElement.value.srcObject = null
    }
    
    isRunning.value = false
    ElMessage.success('实时检测已停止')
  } catch (error: any) {
    ElMessage.error('停止检测失败')
  } finally {
    stopping.value = false
  }
}

const startFrameCapture = () => {
  frameInterval = window.setInterval(async () => {
    if (!videoElement.value || !canvasElement.value || !isRunning.value) return

    try {
      const result = await detectApi.getRealtimeFrame()
      
      // Update stats
      result.detections.forEach(detection => {
        stats.value.total++
        if (detection.class === 'with_helmet') {
          stats.value.withHelmet++
        } else {
          stats.value.withoutHelmet++
        }

        // Add to recent detections
        recentDetections.value.unshift({
          time: new Date().toLocaleTimeString(),
          type: detection.class === 'with_helmet' ? 'with_helmet' : 'without_helmet',
          confidence: detection.confidence
        })
        
        if (recentDetections.value.length > 10) {
          recentDetections.value.pop()
        }
      })

      // Draw result on canvas (simplified - in real implementation, draw bounding boxes)
      const ctx = canvasElement.value.getContext('2d')
      if (ctx && videoElement.value) {
        canvasElement.value.width = videoElement.value.videoWidth
        canvasElement.value.height = videoElement.value.videoHeight
        ctx.drawImage(videoElement.value, 0, 0)
        // Draw detections would go here
      }
    } catch (error) {
      console.error('Failed to get frame:', error)
    }
  }, 1000) // Capture every second
}

const clearCanvas = () => {
  stats.value = { total: 0, withHelmet: 0, withoutHelmet: 0 }
  recentDetections.value = []
}

onMounted(async () => {
  try {
    models.value = await modelApi.getModels()
  } catch (error) {
    console.error('Failed to load models:', error)
  }
})

onUnmounted(() => {
  if (stream) {
    stream.getTracks().forEach(track => track.stop())
  }
  if (frameInterval) {
    clearInterval(frameInterval)
  }
})
</script>

<style scoped>
.detect-realtime-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.control-panel {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}

.video-section {
  margin-top: 20px;
}

.video-container {
  position: relative;
  width: 100%;
  min-height: 400px;
  background: #000;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
}

.video-element {
  display: block;
  width: 100%;
  max-width: 100%;
  height: auto;
  max-height: 500px;
  object-fit: contain;
}

/* 当视频未加载时，确保容器有足够高度 */
.video-container {
  min-height: 500px;
}

.placeholder {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  color: #909399;
  z-index: 1;
}

.placeholder .el-icon {
  display: block;
  margin: 0 auto;
  color: #909399;
}

.placeholder p {
  margin-top: 20px;
  margin-bottom: 0;
  font-size: 14px;
}

.stats {
  margin-bottom: 20px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #ebeef5;
}

.stat-item:last-child {
  border-bottom: none;
}

.label {
  color: #606266;
}

.value {
  font-weight: bold;
  color: #409EFF;
}

.value.success {
  color: #67C23A;
}

.value.danger {
  color: #F56C6C;
}

.recent-detections h4 {
  margin: 0 0 15px 0;
  color: #303133;
}

.detection-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #ebeef5;
}

.detection-time {
  font-size: 12px;
  color: #909399;
}

.detection-confidence {
  font-size: 12px;
  color: #606266;
}
</style>

