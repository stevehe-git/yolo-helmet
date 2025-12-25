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
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          创建模型
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
            <el-button type="primary" link @click="editModel(row)">
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

    <!-- 创建模型对话框 -->
    <el-dialog v-model="showCreateDialog" title="创建模型" width="600px" :close-on-click-modal="false">
      <el-form :model="newModel" :rules="modelRules" ref="modelFormRef" label-width="120px">
        <el-form-item label="模型名称" prop="name">
          <el-input v-model="newModel.name" placeholder="请输入模型名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="newModel.description"
            type="textarea"
            :rows="3"
            placeholder="请输入模型描述"
          />
        </el-form-item>
        <el-form-item label="训练数据集" prop="dataset_id">
          <el-select v-model="newModel.dataset_id" placeholder="请选择数据集" style="width: 100%">
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
          <el-select v-model="newModel.base_model" placeholder="选择基础模型" style="width: 100%">
            <el-option label="YOLOv8n (小型模型)" value="yolov8n.pt" />
            <el-option label="YOLOv8s (中型模型)" value="yolov8s.pt" />
            <el-option label="YOLOv8m (大型模型)" value="yolov8m.pt" />
            <el-option label="YOLOv8l (大型模型)" value="yolov8l.pt" />
            <el-option label="YOLOv8x (超大型模型)" value="yolov8x.pt" />
          </el-select>
        </el-form-item>
        <el-form-item label="迭代次数" prop="epochs">
          <el-input-number v-model="newModel.epochs" :min="1" :max="1000" :step="10" style="width: 100%" />
          <div style="color: #909399; font-size: 12px; margin-top: 5px;">建议值：100-300</div>
        </el-form-item>
        <el-form-item label="批次大小" prop="batch">
          <el-input-number v-model="newModel.batch" :min="1" :max="64" :step="1" style="width: 100%" />
          <div style="color: #909399; font-size: 12px; margin-top: 5px;">建议值：8-16（根据显存调整）</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="cancelCreate">取消</el-button>
        <el-button type="primary" @click="handleCreateAndTrain" :loading="creating">
          {{ creating ? '创建并训练中...' : '创建并开始训练' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 编辑模型对话框 -->
    <el-dialog v-model="showEditDialog" title="编辑模型" width="600px" :close-on-click-modal="false">
      <el-form :model="editModelForm" :rules="modelRules" ref="editFormRef" label-width="120px">
        <el-form-item label="模型名称" prop="name">
          <el-input v-model="editModelForm.name" placeholder="请输入模型名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="editModelForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入模型描述"
          />
        </el-form-item>
        <el-form-item label="训练数据集" prop="dataset_id">
          <el-select v-model="editModelForm.dataset_id" placeholder="请选择数据集" style="width: 100%">
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
          <el-select v-model="editModelForm.base_model" placeholder="选择基础模型" style="width: 100%">
            <el-option label="YOLOv8n (小型模型)" value="yolov8n.pt" />
            <el-option label="YOLOv8s (中型模型)" value="yolov8s.pt" />
            <el-option label="YOLOv8m (大型模型)" value="yolov8m.pt" />
            <el-option label="YOLOv8l (大型模型)" value="yolov8l.pt" />
            <el-option label="YOLOv8x (超大型模型)" value="yolov8x.pt" />
          </el-select>
        </el-form-item>
        <el-form-item label="迭代次数" prop="epochs">
          <el-input-number v-model="editModelForm.epochs" :min="1" :max="1000" :step="10" style="width: 100%" />
          <div style="color: #909399; font-size: 12px; margin-top: 5px;">建议值：100-300</div>
        </el-form-item>
        <el-form-item label="批次大小" prop="batch">
          <el-input-number v-model="editModelForm.batch" :min="1" :max="64" :step="1" style="width: 100%" />
          <div style="color: #909399; font-size: 12px; margin-top: 5px;">建议值：8-16（根据显存调整）</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="cancelEdit">取消</el-button>
        <el-button type="primary" @click="handleUpdateModel" :loading="updating">
          {{ updating ? '更新中...' : '确定' }}
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
import { Plus, Refresh, Search, VideoPlay } from '@element-plus/icons-vue'

const router = useRouter()
const models = ref<Model[]>([])
const datasets = ref<Dataset[]>([])
const loading = ref(false)
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const modelFormRef = ref<FormInstance>()
const editFormRef = ref<FormInstance>()
const updating = ref(false)
const creating = ref(false)
const editingModel = ref<Model | null>(null)

const searchForm = ref({
  keyword: ''
})

const newModel = ref({
  name: '',
  description: '',
  dataset_id: undefined as number | undefined,
  base_model: 'yolov8n.pt',
  epochs: 100,
  batch: 8
})

const editModelForm = ref({
  name: '',
  description: '',
  dataset_id: undefined as number | undefined,
  base_model: 'yolov8n.pt',
  epochs: 100,
  batch: 8
})

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

const cancelCreate = () => {
  showCreateDialog.value = false
  newModel.value = {
    name: '',
    description: '',
    dataset_id: undefined,
    base_model: 'yolov8n.pt',
    epochs: 100,
    batch: 8
  }
  if (modelFormRef.value) {
    modelFormRef.value.resetFields()
  }
}

const handleCreateAndTrain = async () => {
  if (!modelFormRef.value) return
  
  await modelFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        creating.value = true
        
        // 创建模型并保存训练参数
        const createdModelResponse: any = await modelApi.createModel({
          name: newModel.value.name,
          type: 'custom',
          description: newModel.value.description,
          dataset_id: newModel.value.dataset_id,
          base_model: newModel.value.base_model,
          epochs: newModel.value.epochs,
          batch: newModel.value.batch,
          imgsz: 640
        })
        
        // 提取模型ID
        const createdModel: any = createdModelResponse?.data || createdModelResponse
        const modelId = createdModel?.id
        
        if (!modelId) {
          throw new Error('创建模型失败：未返回模型ID')
        }
        
        // 创建成功后立即开始训练
        await modelApi.trainModel({
          model_id: modelId,
          dataset_id: newModel.value.dataset_id!,
          epochs: newModel.value.epochs,
          batch: newModel.value.batch,
          imgsz: 640,
          base_model: newModel.value.base_model
        })
        
        ElMessage.success('模型创建成功，训练任务已启动，请稍后查看训练结果')
        cancelCreate()
        loadModels()
        
        // 启动轮询检查训练状态
        startTrainingStatusPolling(modelId)
      } catch (error: any) {
        ElMessage.error(error.response?.data?.message || error.message || '创建模型失败')
      } finally {
        creating.value = false
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

const editModel = (model: Model) => {
  editingModel.value = model
  const trainingParams = model.training_params || {}
  editModelForm.value = {
    name: model.name,
    description: model.description || '',
    dataset_id: trainingParams.dataset_id,
    base_model: trainingParams.base_model || 'yolov8n.pt',
    epochs: trainingParams.epochs || 100,
    batch: trainingParams.batch || 8
  }
  showEditDialog.value = true
  loadDatasets()
}

const cancelEdit = () => {
  showEditDialog.value = false
  editingModel.value = null
  editModelForm.value = {
    name: '',
    description: '',
    dataset_id: undefined,
    base_model: 'yolov8n.pt',
    epochs: 100,
    batch: 8
  }
  if (editFormRef.value) {
    editFormRef.value.resetFields()
  }
}

const handleUpdateModel = async () => {
  if (!editFormRef.value || !editingModel.value) return

  await editFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        updating.value = true
        await modelApi.updateModel(editingModel.value!.id, {
          name: editModelForm.value.name,
          description: editModelForm.value.description,
          training_params: {
            dataset_id: editModelForm.value.dataset_id,
            base_model: editModelForm.value.base_model,
            epochs: editModelForm.value.epochs,
            batch: editModelForm.value.batch,
            imgsz: 640
          }
        })
        
        ElMessage.success('模型更新成功')
        cancelEdit()
        loadModels()
      } catch (error: any) {
        ElMessage.error(error.response?.data?.message || error.message || '更新模型失败')
      } finally {
        updating.value = false
      }
    }
  })
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
  
  // 开始轮询，每5秒检查一次
  const interval = window.setInterval(async () => {
    try {
      const response: any = await modelApi.getModels()
      const updatedModels: Model[] = Array.isArray(response) ? response : response.data || []
      const model = updatedModels.find((m: Model) => m.id === modelId)
      
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
          loadModels()
          return
        }
        
        // 检查是否训练完成（有指标且没有错误）
        if (model.status === 'completed' && model.metrics && model.metrics.map !== undefined && !isNaN(model.metrics.map) && !(model.metrics as any).error) {
          ElMessage.success({
            message: `模型"${model.name}"训练完成！mAP: ${(model.metrics.map * 100).toFixed(2)}%`,
            duration: 5000
          })
          clearInterval(interval)
          trainingPollingIntervals.delete(modelId)
          loadModels()
          return
        }
      }
    } catch (error) {
      console.error('Error polling training status:', error)
    }
  }, 5000)
  
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
