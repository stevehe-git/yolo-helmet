<template>
  <div class="detect-video-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>视频检测</span>
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
      
      <el-upload
        class="upload-demo"
        drag
        :auto-upload="false"
        :on-change="handleFileChange"
        :show-file-list="false"
        accept="video/*"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          将视频拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持 mp4/avi 格式视频
          </div>
        </template>
      </el-upload>

      <div v-if="selectedFile" class="file-info">
        <div class="file-info-left">
          <p>已选择文件: {{ selectedFile.name }}</p>
          <div class="confidence-control">
            <span class="confidence-label">置信度阈值:</span>
            <el-slider
              v-model="confidenceThreshold"
              :min="0.1"
              :max="1.0"
              :step="0.05"
              :disabled="detecting"
              :format-tooltip="(val: number) => `${(val * 100).toFixed(0)}%`"
              style="width: 200px; margin: 0 10px;"
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
              :disabled="detecting"
              :format-tooltip="(val: number) => `${val} FPS`"
              style="width: 200px; margin: 0 10px;"
            />
            <span class="fps-value">{{ detectionFps }} FPS</span>
            <el-tooltip content="降低检测帧率可以减少处理时间，但可能会跳过部分帧" placement="top">
              <el-icon style="margin-left: 5px; color: #909399; cursor: help;"><QuestionFilled /></el-icon>
            </el-tooltip>
          </div>
        </div>
        <div class="file-info-right">
          <el-button type="primary" @click="handleDetect" :loading="detecting">
            开始检测
          </el-button>
          <el-button @click="clearFile">清除</el-button>
        </div>
      </div>

      <el-progress
        v-if="detecting"
        :percentage="progress"
        :status="progress === 100 ? 'success' : undefined"
        style="margin-top: 20px"
      />

      <div v-if="detectResult" class="result-section">
        <el-divider>检测结果</el-divider>
        
        <el-card style="margin-bottom: 20px">
          <template #header>
            <span>检测摘要</span>
          </template>
          <el-row :gutter="20">
            <el-col :span="4">
              <el-tooltip content="视频文件的总帧数，表示视频包含多少帧画面" placement="top">
                <div class="summary-item">
                  <div class="summary-value">{{ detectResult.summary.total_frames }}</div>
                  <div class="summary-label">总帧数</div>
                </div>
              </el-tooltip>
            </el-col>
            <el-col :span="4">
              <el-tooltip content="从检测帧中采样收集的关键帧数量，用于前端展示。最多收集30个关键帧，包含有检测和无检测的帧" placement="top">
                <div class="summary-item">
                  <div class="summary-value" style="color: #E6A23C;">{{ detectResult.frame_results?.length || 0 }}</div>
                  <div class="summary-label">原始关键帧</div>
                </div>
              </el-tooltip>
            </el-col>
            <el-col :span="4">
              <el-tooltip content="根据检测FPS设置，实际进行检测的帧数。系统会根据检测帧率跳过部分帧以提高处理速度" placement="top">
                <div class="summary-item">
                  <div class="summary-value" style="color: #909399;">{{ (detectResult.summary as any).detected_frames || '-' }}</div>
                  <div class="summary-label">检测帧数</div>
                </div>
              </el-tooltip>
            </el-col>
            <el-col :span="4">
              <el-tooltip content="所有检测帧中检测到的目标总数。这是所有检测帧的检测结果累加，一个检测帧可能包含多个目标" placement="top">
                <div class="summary-item">
                  <div class="summary-value">{{ detectResult.summary.total_detections }}</div>
                  <div class="summary-label">总检测数</div>
                </div>
              </el-tooltip>
            </el-col>
            <el-col :span="4">
              <el-tooltip content="在所有检测帧中，检测到佩戴安全帽的目标总数" placement="top">
                <div class="summary-item">
                  <div class="summary-value success">{{ detectResult.summary.with_helmet }}</div>
                  <div class="summary-label">佩戴安全帽</div>
                </div>
              </el-tooltip>
            </el-col>
            <el-col :span="4">
              <el-tooltip content="在所有检测帧中，检测到未佩戴安全帽的目标总数" placement="top">
                <div class="summary-item">
                  <div class="summary-value danger">{{ detectResult.summary.without_helmet }}</div>
                  <div class="summary-label">未佩戴安全帽</div>
                </div>
              </el-tooltip>
            </el-col>
          </el-row>
        </el-card>

        <el-card>
          <template #header>
            <span>视频预览</span>
          </template>
          <video 
            ref="videoPlayer"
            controls 
            style="width: 100%"
            preload="metadata"
            @error="handleVideoError"
            @loadedmetadata="handleVideoLoaded"
            @canplay="handleVideoCanPlay"
            @loadstart="handleVideoLoadStart"
          >
            <!-- MP4格式 - 广泛支持，包括Safari和移动设备 -->
            <source :src="detectResult.video_url" type="video/mp4" />
            <p>您的浏览器不支持HTML5视频播放。请使用现代浏览器（如Chrome、Firefox、Safari或Edge）访问。</p>
          </video>
        </el-card>

        <el-card style="margin-top: 20px" v-if="detectResult">
          <template #header>
            <span>关键帧检测结果</span>
          </template>
          <el-row :gutter="20" v-if="filteredFrameResults && filteredFrameResults.length > 0">
            <el-col :span="8" v-for="(frame, index) in filteredFrameResults" :key="index">
              <div class="frame-result">
                <img :src="`data:image/jpeg;base64,${frame.image}`" alt="Frame" />
                <div class="frame-stats">
                  <span>检测数: {{ frame.stats.total }}</span>
                  <span class="success">✓ {{ frame.stats.with_helmet }}</span>
                  <span class="danger">✗ {{ frame.stats.without_helmet }}</span>
                </div>
              </div>
            </el-col>
          </el-row>
          <el-empty v-else description="没有检测到任何目标" />
        </el-card>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { detectApi, type VideoDetectResult } from '../api/detect'
import { modelApi, type Model } from '../api/model'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { UploadFile } from 'element-plus'
import { UploadFilled, QuestionFilled } from '@element-plus/icons-vue'

const models = ref<Model[]>([])
const selectedModelId = ref<number | undefined>()
const selectedFile = ref<File | null>(null)
const detecting = ref(false)
const confidenceThreshold = ref(0.25) // 默认置信度阈值
const detectionFps = ref(10) // 默认检测帧率：10 FPS
const progress = ref(0)
const detectResult = ref<VideoDetectResult | null>(null)

// 过滤掉检测数为0的帧
const filteredFrameResults = computed(() => {
  if (!detectResult.value || !detectResult.value.frame_results || !Array.isArray(detectResult.value.frame_results)) {
    return []
  }
  return detectResult.value.frame_results.filter((frame: any) => frame && frame.stats && frame.stats.total > 0)
})

const handleFileChange = (file: UploadFile) => {
  selectedFile.value = file.raw as File
  detectResult.value = null
}

const clearFile = () => {
  selectedFile.value = null
  detectResult.value = null
  progress.value = 0
}

const handleVideoError = (event: any) => {
  const video = event.target as HTMLVideoElement
  const error = video.error
  let errorMessage = '视频加载失败'
  
  if (error) {
    switch (error.code) {
      case error.MEDIA_ERR_ABORTED:
        errorMessage = '视频加载被中止'
        break
      case error.MEDIA_ERR_NETWORK:
        errorMessage = '网络错误，无法加载视频'
        break
      case error.MEDIA_ERR_DECODE:
        errorMessage = '视频解码失败'
        break
      case error.MEDIA_ERR_SRC_NOT_SUPPORTED:
        errorMessage = '视频格式不支持或文件不存在'
        break
      default:
        errorMessage = `视频加载失败 (错误代码: ${error.code})`
    }
  }
  
  console.error('视频加载失败:', {
    error,
    src: video.src,
    currentSrc: video.currentSrc,
    networkState: video.networkState,
    readyState: video.readyState,
    sources: Array.from(video.querySelectorAll('source')).map(s => ({
      src: s.src,
      type: s.type
    }))
  })
  
  ElMessage.error(errorMessage)
}

const handleVideoLoaded = () => {
  console.log('视频元数据加载成功')
}

const handleVideoCanPlay = () => {
  console.log('视频可以播放')
}

const handleVideoLoadStart = () => {
  console.log('视频开始加载:', detectResult.value?.video_url)
}

const videoPlayer = ref<HTMLVideoElement | null>(null)

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
  // 必须选择模型
  if (!selectedModelId.value) {
    ElMessage.warning('请先选择模型')
    return false
  }
  
  try {
    const model = models.value.find(m => m.id === selectedModelId.value)
    if (!model) {
      ElMessage.error('选择的模型不存在，请重新选择')
      return false
    }
    
    // 检查模型是否训练完成（通用模型默认是completed状态，不需要metrics）
    if (model.status !== 'completed' && model.status !== 'published') {
      try {
        await ElMessageBox.confirm(
          `模型"${model.name}"尚未训练完成，是否继续使用？`,
          '模型未训练',
          {
            confirmButtonText: '继续使用',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
      } catch (error: any) {
        if (error === 'cancel') {
          selectedModelId.value = undefined
        }
        return false
      }
    }
  } catch (error) {
    ElMessage.error('模型验证失败')
    return false
  }
  return true
}

const handleDetect = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择视频')
    return
  }

  // 验证模型
  const isModelValid = await validateModel()
  if (!isModelValid) {
    return
  }

  detecting.value = true
  progress.value = 0
  
  // Simulate progress
  const progressInterval = setInterval(() => {
    if (progress.value < 90) {
      progress.value += 10
    }
  }, 1000)

  try {
    const formData = new FormData()
    formData.append('video', selectedFile.value)
    // 验证模型后，selectedModelId.value 一定存在
    formData.append('model_id', selectedModelId.value!.toString())
    formData.append('confidence', confidenceThreshold.value.toString())
    formData.append('detection_fps', detectionFps.value.toString())

    const response = await detectApi.detectVideo(formData)
    // 响应拦截器已经返回了 response.data，所以直接使用 response
    detectResult.value = response as unknown as VideoDetectResult
    progress.value = 100
    
    // 确保视频URL是完整的绝对路径
    if (detectResult.value && detectResult.value.video_url) {
      // 如果URL不是以http开头，添加当前域名
      if (!detectResult.value.video_url.startsWith('http')) {
        const baseURL = window.location.origin
        detectResult.value.video_url = baseURL + detectResult.value.video_url
      }
      console.log('视频URL:', detectResult.value.video_url)
      
      // 等待DOM更新后，强制重新加载视频
      await nextTick()
      if (videoPlayer.value) {
        videoPlayer.value.load()
        console.log('视频元素已加载，尝试播放')
      }
    }
    
    ElMessage.success('检测完成')
  } catch (error: any) {
    const errorMessage = error.response?.data?.message || error.message || '检测失败'
    
    // 检查是否是模型相关错误
    if (errorMessage.includes('model') || errorMessage.includes('模型') || 
        errorMessage.includes('Model') || errorMessage.includes('not found') ||
        errorMessage.includes('不存在') || errorMessage.includes('无法加载')) {
      ElMessage.error({
        message: '模型加载失败，请检查模型文件是否存在或选择其他模型',
        duration: 5000
      })
    } else {
      ElMessage.error(errorMessage)
    }
  } finally {
    detecting.value = false
    clearInterval(progressInterval)
  }
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
</script>

<style scoped>
.detect-video-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.upload-demo {
  margin-bottom: 20px;
}

.file-info {
  margin-top: 20px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 15px;
}

.file-info-left {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.file-info-right {
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
  font-size: 14px;
  white-space: nowrap;
}

.confidence-value {
  color: #409EFF;
  font-weight: bold;
  min-width: 50px;
  text-align: right;
}

.result-section {
  margin-top: 30px;
}

.summary-item {
  text-align: center;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 4px;
}

.summary-value {
  font-size: 32px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 10px;
}

.summary-value.success {
  color: #67C23A;
}

.summary-value.danger {
  color: #F56C6C;
}

.summary-label {
  font-size: 14px;
  color: #909399;
}

.frame-result {
  margin-bottom: 20px;
}

.frame-result img {
  width: 100%;
  border-radius: 4px;
  margin-bottom: 10px;
}

.frame-stats {
  display: flex;
  justify-content: space-around;
  font-size: 16px;
  color: #606266;
  font-weight: 500;
}

.frame-stats .success {
  color: #67C23A;
}

.frame-stats .danger {
  color: #F56C6C;
}
</style>

