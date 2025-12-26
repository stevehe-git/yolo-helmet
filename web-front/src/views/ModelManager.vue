<template>
  <div class="model-manager-container">
    <!-- 顶部操作栏 -->
    <div class="header-actions">
      <h2>模型管理</h2>
      <div class="action-buttons">
        <el-button @click="loadModels">
          <el-icon><Refresh /></el-icon>
          刷新列表
        </el-button>
        <el-button type="primary" @click="handleCreateModel">
          <el-icon><Plus /></el-icon>
          创建模型
        </el-button>
        <el-button type="success" @click="showImportDialog = true">
          <el-icon><Upload /></el-icon>
          导入模型
        </el-button>
      </div>
    </div>

    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="搜索">
          <el-input
            v-model="searchForm.keyword"
            placeholder="搜索模型名称或描述"
            clearable
            style="width: 300px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleClearSearch">清空</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 模型列表表格 -->
    <el-card class="table-card">
      <el-table :data="models" style="width: 100%" v-loading="loading">
        <el-table-column prop="name" label="模型名称" min-width="150" />
        <el-table-column label="模型类型" width="120" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.type === 'general'" type="success" effect="plain">通用模型</el-tag>
            <el-tag v-else type="primary" effect="plain">自定义模型</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <span>{{ row.description || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="训练数据集" min-width="150">
          <template #default="{ row }">
            <span>{{ row.dataset_name || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="基础模型" min-width="120">
          <template #default="{ row }">
            <span>{{ getBaseModelName(row.training_params?.base_model) || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="训练参数" min-width="150">
          <template #default="{ row }">
            <div v-if="row.training_params">
              <div>迭代: {{ row.training_params.epochs || '-' }}</div>
              <div>批次: {{ row.training_params.batch || '-' }}</div>
            </div>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" min-width="120">
          <template #default="{ row }">
            <el-tag v-if="row.status === 'published'" type="info">已发布</el-tag>
            <el-tag v-else-if="row.status === 'completed'" type="success">训练完成</el-tag>
            <el-tag v-else-if="row.status === 'training'" type="warning">训练中</el-tag>
            <el-tag v-else-if="row.status === 'failed'" type="danger">训练失败</el-tag>
            <el-tag v-else type="info">待训练</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="训练结果" min-width="200">
          <template #default="{ row }">
            <div v-if="row.metrics && !row.metrics.error">
              <div>精确度: {{ (row.metrics.precision || 0).toFixed(3) }}</div>
              <div>召回率: {{ (row.metrics.recall || 0).toFixed(3) }}</div>
              <div>mAP@0.5: {{ (row.metrics.map || 0).toFixed(3) }}</div>
              <div>适应度: {{ (row.metrics.f1 || 0).toFixed(3) }}</div>
            </div>
            <div v-else-if="row.metrics && row.metrics.error" style="color: #f56c6c;">
              <span>训练失败: {{ row.metrics.error }}</span>
            </div>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="320" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewModelInfo(row.id)">
              查看
            </el-button>
            <el-button type="primary" link @click="handleEdit(row)">
              编辑
            </el-button>
            <!-- 训练按钮：只要不是completed和published状态，就显示 -->
            <el-button
              v-if="row.status !== 'completed' && row.status !== 'published' && row.type === 'custom'"
              type="success"
              link
              @click="handleTrain(row)"
              :disabled="row.status === 'training'"
            >
              <el-icon><VideoPlay /></el-icon>
              {{ row.status === 'training' ? '训练中...' : '训练' }}
            </el-button>
            <el-button
              v-if="row.status === 'published'"
              type="warning"
              link
              @click="handleUnpublish(row.id)"
            >
              取消发布
            </el-button>
            <el-button
              v-else-if="row.status === 'completed'"
              type="success"
              link
              @click="handlePublish(row.id)"
            >
              发布
            </el-button>
            <el-button type="danger" link @click="deleteModel(row.id)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑模型对话框（合并） -->
    <el-dialog v-model="showModelDialog" :title="editingModel ? '编辑模型' : '创建模型'" width="600px" :close-on-click-modal="false">
      <el-form :model="modelForm" :rules="editingModel ? editModelRules : modelRules" ref="modelFormRef" label-width="120px">
        <el-form-item label="模型名称" prop="name">
          <el-input v-model="modelForm.name" placeholder="请输入模型名称" />
        </el-form-item>
        <el-form-item v-if="editingModel" label="模型类型" prop="type">
          <el-select v-model="modelForm.type" placeholder="选择模型类型" style="width: 100%">
            <el-option label="通用模型" value="general" />
            <el-option label="自定义模型" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="modelForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入模型描述"
          />
        </el-form-item>
        <el-form-item label="训练数据集" prop="dataset_id">
          <el-select v-model="modelForm.dataset_id" placeholder="请选择数据集" style="width: 100%">
            <el-option
              v-for="dataset in datasets"
              :key="dataset.id"
              :label="`${dataset.name} (${dataset.train_count || 0}训练/${dataset.val_count || 0}验证)`"
              :value="dataset.id"
              :disabled="dataset.status !== 'validated'"
            >
              <span>{{ dataset.name }}</span>
              <el-tag v-if="dataset.status === 'validated'" type="success" size="small" style="margin-left: 10px;">已验证</el-tag>
              <el-tag v-else type="warning" size="small" style="margin-left: 10px;">未验证</el-tag>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="基础模型" prop="base_model">
          <el-select v-model="modelForm.base_model" placeholder="选择基础模型" style="width: 100%">
            <el-option label="YOLOv8n (小型模型)" value="yolov8n.pt" />
            <el-option label="YOLOv8s (中型模型)" value="yolov8s.pt" />
            <el-option label="YOLOv8m (大型模型)" value="yolov8m.pt" />
            <el-option label="YOLOv8l (大型模型)" value="yolov8l.pt" />
            <el-option label="YOLOv8x (超大型模型)" value="yolov8x.pt" />
          </el-select>
        </el-form-item>
        <el-form-item label="迭代次数" prop="epochs">
          <el-input-number v-model="modelForm.epochs" :min="1" :max="1000" :step="10" style="width: 100%" />
          <div style="color: #909399; font-size: 12px; margin-top: 5px;">建议值：100-300</div>
        </el-form-item>
        <el-form-item label="批次大小" prop="batch">
          <el-input-number v-model="modelForm.batch" :min="1" :max="64" :step="1" style="width: 100%" />
          <div style="color: #909399; font-size: 12px; margin-top: 5px;">建议值：8-16（根据显存调整）</div>
        </el-form-item>
        <el-form-item label="训练设备" prop="device">
          <el-radio-group v-model="modelForm.device">
            <el-radio label="cpu">CPU</el-radio>
            <el-radio label="gpu">GPU</el-radio>
          </el-radio-group>
          <div style="color: #909399; font-size: 12px; margin-top: 5px;">选择训练使用的设备，GPU训练速度更快但需要支持CUDA的显卡</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="cancelModelDialog">取消</el-button>
        <el-button type="primary" @click="handleSaveModel" :loading="creating || updating">
          {{ (creating || updating) ? (editingModel ? '更新中...' : '创建中...') : (editingModel ? '确定' : '创建') }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 导入模型对话框 -->
    <el-dialog v-model="showImportDialog" title="导入模型" width="600px">
      <el-form :model="importModelForm" :rules="importModelRules" ref="importFormRef" label-width="120px">
        <el-form-item label="模型文件" prop="model_file">
          <el-upload
            :auto-upload="false"
            :on-change="handleFileChange"
            :limit="1"
            accept=".pt"
            :file-list="fileList"
          >
            <el-button type="primary">
              <el-icon><Upload /></el-icon>
              选择文件
            </el-button>
            <template #tip>
              <div class="el-upload__tip">
                只支持.pt格式的YOLO模型文件，文件大小不超过500MB
              </div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item label="模型名称" prop="name">
          <el-input
            v-model="importModelForm.name"
            placeholder="请输入模型名称"
          />
        </el-form-item>
        <el-form-item label="模型类型" prop="type">
          <el-select v-model="importModelForm.type" placeholder="选择模型类型" style="width: 100%">
            <el-option label="通用模型" value="general" />
            <el-option label="自定义模型" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="模型描述" prop="description">
          <el-input
            v-model="importModelForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入模型描述（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="cancelImport">取消</el-button>
        <el-button type="primary" @click="handleImportModel" :loading="importing">
          {{ importing ? '导入中...' : '确定导入' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { modelApi, type Model } from '../api/model'
import { datasetApi, type Dataset } from '../api/dataset'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Plus, Refresh, Search, VideoPlay, Upload } from '@element-plus/icons-vue'

const router = useRouter()
const models = ref<Model[]>([])
const datasets = ref<Dataset[]>([])
const loading = ref(false)
const showModelDialog = ref(false)
const showImportDialog = ref(false)
const modelFormRef = ref<FormInstance>()
const importFormRef = ref<FormInstance>()
const updating = ref(false)
const creating = ref(false)
const importing = ref(false)
const editingModel = ref<Model | null>(null)

const searchForm = ref({
  keyword: ''
})

const modelForm = ref({
  name: '',
  type: 'custom' as 'general' | 'custom',
  description: '',
  dataset_id: undefined as number | undefined,
  base_model: 'yolov8n.pt',
  epochs: 100,
  batch: 8,
  device: 'cpu' as 'cpu' | 'gpu'
})


const editModelRules: FormRules = {
  name: [{ required: true, message: '请输入模型名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择模型类型', trigger: 'change' }]
}

const importModelForm = ref({
  name: '',
  type: 'general' as 'general' | 'custom',
  description: '',
  model_file: null as File | null
})

const fileList = ref<any[]>([])

const importModelRules: FormRules = {
  name: [{ required: true, message: '请输入模型名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择模型类型', trigger: 'change' }],
  model_file: [{ required: true, message: '请选择要导入的模型文件', trigger: 'change' }]
}

const modelRules: FormRules = {
  name: [{ required: true, message: '请输入模型名称', trigger: 'blur' }],
  dataset_id: [{ required: true, message: '请选择训练数据集', trigger: 'change' }],
  base_model: [{ required: true, message: '请选择基础模型', trigger: 'change' }],
  epochs: [{ required: true, message: '请输入迭代次数', trigger: 'blur' }],
  batch: [{ required: true, message: '请输入批次大小', trigger: 'blur' }]
}

// 获取基础模型显示名称
const getBaseModelName = (baseModel?: string): string => {
  if (!baseModel) return '-'
  // 移除.pt后缀并格式化
  const name = baseModel.replace('.pt', '')
  return name.toUpperCase()
}

const loadModels = async () => {
  try {
    loading.value = true
    const response: any = await modelApi.getModels(searchForm.value.keyword)
    models.value = Array.isArray(response) ? response : response.data || []
  } catch (error) {
    ElMessage.error('加载模型列表失败')
  } finally {
    loading.value = false
  }
}

const loadDatasets = async () => {
  try {
    const response: any = await datasetApi.getDatasets()
    datasets.value = Array.isArray(response) ? response : response.data || []
  } catch (error) {
    ElMessage.error('加载数据集列表失败')
  }
}

const handleSearch = () => {
  loadModels()
}

const handleClearSearch = () => {
  searchForm.value.keyword = ''
  loadModels()
}

const handleCreateModel = () => {
  editingModel.value = null
  modelForm.value = {
    name: '',
    type: 'custom',
    description: '',
    dataset_id: undefined,
    base_model: 'yolov8n.pt',
    epochs: 100,
    batch: 8,
    device: 'cpu'
  }
  showModelDialog.value = true
  loadDatasets()
}

const cancelModelDialog = () => {
  showModelDialog.value = false
  editingModel.value = null
  modelForm.value = {
    name: '',
    type: 'custom',
    description: '',
    dataset_id: undefined,
    base_model: 'yolov8n.pt',
    epochs: 100,
    batch: 8,
    device: 'cpu'
  }
  if (modelFormRef.value) {
    modelFormRef.value.resetFields()
  }
}

const handleFileChange = (file: any) => {
  importModelForm.value.model_file = file.raw
  fileList.value = [file]
}

const cancelImport = () => {
  showImportDialog.value = false
  importModelForm.value = {
    name: '',
    type: 'general',
    description: '',
    model_file: null
  }
  fileList.value = []
  if (importFormRef.value) {
    importFormRef.value.resetFields()
  }
}

const handleImportModel = async () => {
  if (!importFormRef.value) return
  
  await importFormRef.value.validate(async (valid) => {
    if (valid) {
      if (!importModelForm.value.model_file) {
        ElMessage.warning('请选择要导入的模型文件')
        return
      }
      
      try {
        importing.value = true
        
        const formData = new FormData()
        formData.append('model_file', importModelForm.value.model_file)
        formData.append('name', importModelForm.value.name)
        formData.append('type', importModelForm.value.type)
        if (importModelForm.value.description) {
          formData.append('description', importModelForm.value.description)
        }
        
        const response: any = await modelApi.importModel(formData)
        
        ElMessage.success(response.data?.message || '模型导入成功')
        cancelImport()
        loadModels()
      } catch (error: any) {
        ElMessage.error(error.response?.data?.message || error.message || '导入模型失败')
      } finally {
        importing.value = false
      }
    }
  })
}

const handleSaveModel = async () => {
  if (!modelFormRef.value) return
  
  await modelFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (editingModel.value) {
          // 编辑模型
          updating.value = true
          await modelApi.updateModel(editingModel.value.id, {
            name: modelForm.value.name,
            type: modelForm.value.type,
            description: modelForm.value.description,
            training_params: {
              dataset_id: modelForm.value.dataset_id,
              base_model: modelForm.value.base_model,
              epochs: modelForm.value.epochs,
              batch: modelForm.value.batch,
              imgsz: 640,
              device: modelForm.value.device
            }
          })
          ElMessage.success('模型更新成功')
        } else {
          // 创建模型
          creating.value = true
          await modelApi.createModel({
            name: modelForm.value.name,
            type: 'custom',
            description: modelForm.value.description,
            dataset_id: modelForm.value.dataset_id,
            base_model: modelForm.value.base_model,
            epochs: modelForm.value.epochs,
            batch: modelForm.value.batch,
            imgsz: 640,
            device: modelForm.value.device
          })
          ElMessage.success('模型创建成功，可以在模型列表中查看并开始训练')
        }
        cancelModelDialog()
        loadModels()
      } catch (error: any) {
        ElMessage.error(error.response?.data?.message || error.message || (editingModel.value ? '更新模型失败' : '创建模型失败'))
      } finally {
        creating.value = false
        updating.value = false
      }
    }
  })
}

const viewModelInfo = (id: number) => {
  router.push(`/model/info/${id}`)
}

const deleteModel = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除该模型吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await modelApi.deleteModel(id)
    ElMessage.success('删除成功')
    loadModels()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleEdit = (model: Model) => {
  editingModel.value = model
  const trainingParams = model.training_params || {}
  modelForm.value = {
    name: model.name,
    type: model.type || 'custom',
    description: model.description || '',
    dataset_id: trainingParams.dataset_id,
    base_model: trainingParams.base_model || 'yolov8n.pt',
    epochs: trainingParams.epochs || 100,
    batch: trainingParams.batch || 8,
    device: trainingParams.device || 'cpu'
  }
  showModelDialog.value = true
  loadDatasets()
}

const handleTrain = async (model: Model) => {
  // 检查是否有训练参数
  if (!model.training_params || !model.training_params.dataset_id) {
    ElMessage.error('模型未配置训练参数，请先编辑模型设置训练参数')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要开始训练模型"${model.name}"吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      }
    )
    
    await modelApi.trainModel({
      model_id: model.id
    })
    
    ElMessage.success('训练任务已启动，请稍后查看训练结果')
    loadModels()
    
    // 启动轮询检查训练状态
    startTrainingStatusPolling(model.id)
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.message || error.message || '训练启动失败')
    }
  }
}

const handlePublish = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要发布该模型吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })
    await modelApi.publishModel(id)
    ElMessage.success('模型发布成功')
    loadModels()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.message || '发布失败')
    }
  }
}

const handleUnpublish = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要取消发布该模型吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await modelApi.unpublishModel(id)
    ElMessage.success('取消发布成功')
    loadModels()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.message || '取消发布失败')
    }
  }
}

// 训练状态轮询
let trainingPollingIntervals: Map<number, number> = new Map()

const startTrainingStatusPolling = (modelId: number) => {
  // 清除之前的轮询
  if (trainingPollingIntervals.has(modelId)) {
    clearInterval(trainingPollingIntervals.get(modelId))
  }
  
  // 开始轮询，每3秒检查一次（更频繁的检查以确保及时刷新）
  const interval = window.setInterval(async () => {
    try {
      // 直接刷新模型列表，确保数据是最新的
      await loadModels()
      
      // 从当前模型列表中查找对应的模型
      const model = models.value.find((m: Model) => m.id === modelId)
      
      if (model) {
        // 检查是否有错误
        if (model.metrics && (model.metrics as any).error) {
          ElMessage.error({
            message: `模型"${model.name}"训练失败: ${(model.metrics as any).error}`,
            duration: 0,
            showClose: true
          })
          clearInterval(interval)
          trainingPollingIntervals.delete(modelId)
          return
        }
        
        // 检查是否训练完成（状态为completed）
        if (model.status === 'completed') {
          // 如果有指标，显示成功消息
          if (model.metrics && model.metrics.map !== undefined && !isNaN(model.metrics.map) && !(model.metrics as any).error) {
            ElMessage.success({
              message: `模型"${model.name}"训练完成！mAP: ${(model.metrics.map * 100).toFixed(2)}%`,
              duration: 5000
            })
          } else {
            // 即使没有指标，只要状态是completed，也停止轮询并提示
            ElMessage.success({
              message: `模型"${model.name}"训练完成！`,
              duration: 5000
            })
          }
          clearInterval(interval)
          trainingPollingIntervals.delete(modelId)
          return
        }
        
        // 如果状态变为failed，也停止轮询
        if (model.status === 'failed') {
          clearInterval(interval)
          trainingPollingIntervals.delete(modelId)
          return
        }
      } else {
        // 如果找不到模型，可能是被删除了，停止轮询
        clearInterval(interval)
        trainingPollingIntervals.delete(modelId)
      }
    } catch (error) {
      console.error('Error polling training status:', error)
    }
  }, 3000) // 改为3秒轮询一次，更及时
  
  trainingPollingIntervals.set(modelId, interval)
  
  // 30分钟后自动停止轮询
  setTimeout(() => {
    if (trainingPollingIntervals.has(modelId)) {
      clearInterval(trainingPollingIntervals.get(modelId))
      trainingPollingIntervals.delete(modelId)
    }
  }, 30 * 60 * 1000)
}

onMounted(() => {
  loadModels()
  loadDatasets()
})

onUnmounted(() => {
  // 清理所有轮询
  trainingPollingIntervals.forEach((interval) => {
    clearInterval(interval)
  })
  trainingPollingIntervals.clear()
})
</script>

<style scoped>
.model-manager-container {
  padding: 20px;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-actions h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 500;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.search-card {
  margin-bottom: 20px;
}

.table-card {
  margin-top: 20px;
}
</style>
