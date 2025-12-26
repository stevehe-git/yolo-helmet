<template>
  <div class="detect-image-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>图片检测</span>
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
        accept="image/*"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          将图片拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持 jpg/png 格式图片
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

      <div v-if="detectResult" class="result-section">
        <el-divider>检测结果</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="image-preview">
              <img :src="`data:image/jpeg;base64,${detectResult.image}`" alt="检测结果" />
            </div>
          </el-col>
          <el-col :span="12">
            <el-card>
              <template #header>
                <span>检测统计</span>
              </template>
              <div class="stats">
                <div class="stat-item">
                  <span class="label">总检测数:</span>
                  <span class="value">{{ detectResult.stats.total }}</span>
                </div>
                <div class="stat-item">
                  <span class="label">佩戴安全帽:</span>
                  <span class="value success">{{ detectResult.stats.with_helmet }}</span>
                </div>
                <div class="stat-item">
                  <span class="label">未佩戴安全帽:</span>
                  <span class="value danger">{{ detectResult.stats.without_helmet }}</span>
                </div>
              </div>
              
              <el-divider />
              
              <div class="detections-list">
                <h4>检测详情</h4>
                <el-table :data="detectResult.detections" style="width: 100%">
                  <el-table-column prop="class" label="类别" width="120" />
                  <el-table-column prop="confidence" label="置信度" width="120">
                    <template #default="{ row }">
                      <span>{{ (row.confidence * 100).toFixed(2) }}%</span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="bbox" label="位置">
                    <template #default="{ row }">
                      <span>[{{ row.bbox.join(', ') }}]</span>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { detectApi, type DetectResult } from '../api/detect'
import { modelApi, type Model } from '../api/model'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { UploadFile } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'

const models = ref<Model[]>([])
const selectedModelId = ref<number | undefined>()
const selectedFile = ref<File | null>(null)
const detecting = ref(false)
const detectResult = ref<DetectResult | null>(null)

const handleFileChange = (file: UploadFile) => {
  selectedFile.value = file.raw as File
  detectResult.value = null
}

const clearFile = () => {
  selectedFile.value = null
  detectResult.value = null
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
  }
  return true
}

const handleDetect = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择图片')
    return
  }

  // 验证模型
  const isModelValid = await validateModel()
  if (!isModelValid) {
    return
  }

  detecting.value = true
  try {
    const formData = new FormData()
    formData.append('image', selectedFile.value)
    if (selectedModelId.value) {
      formData.append('model_id', selectedModelId.value.toString())
    }

    const result = await detectApi.detectImage(formData)
    detectResult.value = result
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
.detect-image-container {
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

.image-preview {
  width: 100%;
  text-align: center;
}

.image-preview img {
  max-width: 100%;
  border-radius: 4px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
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

.detections-list h4 {
  margin: 0 0 15px 0;
  color: #303133;
}
</style>

