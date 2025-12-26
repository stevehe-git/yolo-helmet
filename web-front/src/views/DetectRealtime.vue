<template>
  <div class="detect-realtime-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>实时检测</span>
          <el-select 
            v-model="selectedModelId" 
            placeholder="选择模型" 
            style="width: 250px" 
            clearable
            @change="handleModelChange"
          >
            <el-option
              v-for="model in models"
              :key="model.id"
              :label="model.name"
              :value="model.id"
            >
              <span>{{ model.name }}</span>
              <span style="float: right; color: #8492a6; font-size: 13px">
                {{ model.type === 'general' ? '通用' : '自定义' }}
                <el-tag v-if="model.status === 'failed'" type="danger" size="small" style="margin-left: 5px;">训练失败</el-tag>
                <el-tag v-else-if="model.status !== 'completed' && model.status !== 'published'" type="warning" size="small" style="margin-left: 5px;">未训练</el-tag>
              </span>
            </el-option>
          </el-select>
          <el-alert
            v-if="models.length === 0"
            title="未找到可用模型"
            type="warning"
            :closable="false"
            show-icon
            style="margin-top: 10px; width: 250px"
          >
            <template #default>
              <span>请先在模型管理中发布模型</span>
            </template>
          </el-alert>
        </div>
      </template>

      <div class="control-panel">
        <div class="control-group">
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
        <div class="confidence-control">
          <span class="confidence-label">置信度阈值:</span>
          <el-slider
            v-model="confidenceThreshold"
            :min="0.1"
            :max="1.0"
            :step="0.05"
            :disabled="isRunning"
            :format-tooltip="(val: number) => `${(val * 100).toFixed(0)}%`"
            style="width: 200px; margin: 0 10px;"
            @change="handleConfidenceChange"
          />
          <span class="confidence-value">{{ (confidenceThreshold * 100).toFixed(0) }}%</span>
        </div>
        <div class="fps-control">
          <span class="fps-label">检测帧率 (FPS):</span>
          <el-slider
            v-model="detectionFps"
            :min="1"
            :max="30"
            :step="1"
            :disabled="isRunning"
            :format-tooltip="(val: number) => `${val} FPS`"
            style="width: 200px; margin: 0 10px;"
          />
          <span class="fps-value">{{ detectionFps }} FPS</span>
          <el-tooltip content="降低检测帧率可以减少处理时间，提高实时性" placement="top">
            <el-icon style="margin-left: 5px; color: #909399; cursor: help;"><QuestionFilled /></el-icon>
          </el-tooltip>
        </div>
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
import { ElMessage, ElMessageBox } from 'element-plus'
import { VideoCamera } from '@element-plus/icons-vue'

const models = ref<Model[]>([])
const selectedModelId = ref<number | undefined>()
const videoElement = ref<HTMLVideoElement | null>(null)
const canvasElement = ref<HTMLCanvasElement | null>(null)
const isRunning = ref(false)
const starting = ref(false)
const stopping = ref(false)
const confidenceThreshold = ref(0.25) // 默认置信度阈值
const detectionFps = ref(5) // 默认检测帧率：5 FPS
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

const handleModelChange = (modelId: number | undefined) => {
  if (modelId) {
    const model = models.value.find(m => m.id === modelId)
    if (model && model.status !== 'completed' && model.status !== 'published') {
      ElMessage.warning({
        message: `模型"${model.name}"尚未训练完成，可能无法正常使用`,
        duration: 5000
      })
    }
  }
}

const validateModel = async (): Promise<boolean> => {
  if (selectedModelId.value) {
    try {
      const model = models.value.find(m => m.id === selectedModelId.value)
      if (!model) {
        ElMessage.error('选择的模型不存在，请重新选择')
        return false
      }
      
      // 检查模型是否训练完成（通用模型默认是completed状态，不需要metrics）
      if (model.status !== 'completed' && model.status !== 'published') {
        await ElMessageBox.confirm(
          `模型"${model.name}"尚未训练完成，是否继续使用？`,
          '模型未训练',
          {
            confirmButtonText: '继续使用',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
      }
    } catch (error: any) {
      if (error === 'cancel') {
        selectedModelId.value = undefined
      }
      return false
    }
  }
  return true
}

const startDetection = async () => {
  // 验证模型
  const isModelValid = await validateModel()
  if (!isModelValid) {
    return
  }

  starting.value = true
  try {
    // Request camera access
    stream = await navigator.mediaDevices.getUserMedia({ video: true })
    if (videoElement.value) {
      videoElement.value.srcObject = stream
    }

    // Start backend detection with confidence threshold
    await detectApi.startRealtime(selectedModelId.value, confidenceThreshold.value)

    isRunning.value = true
    startFrameCapture()
    ElMessage.success('实时检测已启动')
  } catch (error: any) {
    const errorMessage = error.message || '未知错误'
    
    // 检查是否是模型相关错误
    if (errorMessage.includes('model') || errorMessage.includes('模型') || 
        errorMessage.includes('Model') || errorMessage.includes('not found') ||
        errorMessage.includes('不存在') || errorMessage.includes('无法加载')) {
      ElMessage.error({
        message: '模型加载失败，请检查模型文件是否存在或选择其他模型',
        duration: 5000
      })
    } else if (errorMessage.includes('摄像头') || errorMessage.includes('camera') || 
               errorMessage.includes('permission') || errorMessage.includes('权限')) {
      ElMessage.error('无法访问摄像头: ' + errorMessage)
    } else {
      ElMessage.error('启动失败: ' + errorMessage)
    }
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

const handleConfidenceChange = () => {
  // 置信度改变时，如果正在运行，会在下一帧自动应用新阈值
  if (isRunning.value) {
    ElMessage.info('置信度已更新，将在下一帧应用')
  }
}

const startFrameCapture = () => {
  // 根据检测帧率计算间隔时间（毫秒）
  const getInterval = () => Math.max(100, 1000 / detectionFps.value)
  
  const captureFrame = async () => {
    if (!videoElement.value || !canvasElement.value || !isRunning.value) return

    const canvas = canvasElement.value
    const ctx = canvas.getContext('2d')
    if (!ctx) return
    
    canvas.width = videoElement.value.videoWidth
    canvas.height = videoElement.value.videoHeight
    ctx.drawImage(videoElement.value, 0, 0)
    
    // 将canvas转换为blob并发送到后端
    canvas.toBlob(async (blob) => {
      if (!blob || !isRunning.value) return
      
      try {
        const formData = new FormData()
        formData.append('image', blob, 'frame.jpg')
        formData.append('confidence', confidenceThreshold.value.toString())
        formData.append('fps', detectionFps.value.toString())
        
        const response = await detectApi.detectRealtimeFrame(formData)
        const result = response.data || response
        
        // Update stats
        if (result.detections && Array.isArray(result.detections)) {
          result.detections.forEach((detection: any) => {
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
        }

        // Draw result on canvas with detections
        if (result.image && canvasElement.value) {
          const img = new Image()
          img.onload = () => {
            if (canvasElement.value) {
              const resultCtx = canvasElement.value.getContext('2d')
              if (resultCtx) {
                resultCtx.clearRect(0, 0, canvasElement.value.width, canvasElement.value.height)
                resultCtx.drawImage(img, 0, 0, canvasElement.value.width, canvasElement.value.height)
              }
            }
          }
          img.src = `data:image/jpeg;base64,${result.image}`
        }
      } catch (error: any) {
        const errorMessage = error.response?.data?.message || error.message || '获取检测帧失败'
        
        // 检查是否是模型相关错误
        if (errorMessage.includes('model') || errorMessage.includes('模型') || 
            errorMessage.includes('Model') || errorMessage.includes('not found') ||
            errorMessage.includes('不存在') || errorMessage.includes('无法加载') ||
            errorMessage.includes('not active')) {
          ElMessage.error({
            message: '模型检测失败，请检查模型状态',
            duration: 3000
          })
          // 停止检测
          stopDetection()
        } else {
          console.error('Failed to detect frame:', error)
        }
      }
    }, 'image/jpeg', 0.8)
  }
  
  // 启动定时器
  if (frameInterval) {
    clearInterval(frameInterval)
  }
  frameInterval = window.setInterval(captureFrame, getInterval())
}

const clearCanvas = () => {
  stats.value = { total: 0, withHelmet: 0, withoutHelmet: 0 }
  recentDetections.value = []
}

onMounted(async () => {
  try {
    // 只获取已发布的模型
    const response: any = await modelApi.getModels(undefined, 'published')
    models.value = Array.isArray(response) ? response : response.data || []
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
  flex-direction: column;
  gap: 15px;
}

.control-group {
  display: flex;
  gap: 10px;
}

.confidence-control {
  display: flex;
  align-items: center;
  gap: 10px;
}

.confidence-label {
  color: #606266;
  font-size: 26px;
  white-space: nowrap;
}

.confidence-value {
  color: #409EFF;
  font-weight: bold;
  min-width: 50px;
  text-align: right;
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
  font-size: 26px;
  color: #606266;
}
</style>

