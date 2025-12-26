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
              <span>请先在模型管理中创建或上传模型</span>
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
        <p>已选择文件: {{ selectedFile.name }}</p>
        <el-button type="primary" @click="handleDetect" :loading="detecting">
          开始检测
        </el-button>
        <el-button @click="clearFile">清除</el-button>
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
            <el-col :span="6">
              <div class="summary-item">
                <div class="summary-value">{{ detectResult.summary.total_frames }}</div>
                <div class="summary-label">总帧数</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="summary-item">
                <div class="summary-value">{{ detectResult.summary.total_detections }}</div>
                <div class="summary-label">总检测数</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="summary-item">
                <div class="summary-value success">{{ detectResult.summary.with_helmet }}</div>
                <div class="summary-label">佩戴安全帽</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="summary-item">
                <div class="summary-value danger">{{ detectResult.summary.without_helmet }}</div>
                <div class="summary-label">未佩戴安全帽</div>
              </div>
            </el-col>
          </el-row>
        </el-card>

        <el-card>
          <template #header>
            <span>视频预览</span>
          </template>
          <video :src="detectResult.video_url" controls style="width: 100%"></video>
        </el-card>

        <el-card style="margin-top: 20px">
          <template #header>
            <span>关键帧检测结果</span>
          </template>
          <el-row :gutter="20">
            <el-col :span="8" v-for="(frame, index) in detectResult.frame_results.slice(0, 6)" :key="index">
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
        </el-card>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { detectApi, type VideoDetectResult } from '../api/detect'
import { modelApi, type Model } from '../api/model'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { UploadFile } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'

const models = ref<Model[]>([])
const selectedModelId = ref<number | undefined>()
const selectedFile = ref<File | null>(null)
const detecting = ref(false)
const progress = ref(0)
const detectResult = ref<VideoDetectResult | null>(null)

const handleFileChange = (file: UploadFile) => {
  selectedFile.value = file.raw as File
  detectResult.value = null
}

const clearFile = () => {
  selectedFile.value = null
  detectResult.value = null
  progress.value = 0
}

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
    if (selectedModelId.value) {
      formData.append('model_id', selectedModelId.value.toString())
    }

    const result = await detectApi.detectVideo(formData)
    detectResult.value = result
    progress.value = 100
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
    models.value = await modelApi.getModels()
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
  align-items: center;
  gap: 15px;
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
  font-size: 12px;
  color: #606266;
}

.frame-stats .success {
  color: #67C23A;
}

.frame-stats .danger {
  color: #F56C6C;
}
</style>

