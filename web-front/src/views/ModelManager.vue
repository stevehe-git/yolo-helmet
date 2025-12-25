<template>
  <div class="model-manager-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>模型管理</span>
          <el-button type="primary" @click="showCreateDialogHandler">
            <el-icon><Plus /></el-icon>
            创建模型
          </el-button>
        </div>
      </template>

      <el-table :data="models" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="模型名称" />
        <el-table-column prop="type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="row.type === 'general' ? 'success' : 'warning'">
              {{ row.type === 'general' ? '通用模型' : '定制模型' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="metrics" label="性能指标" width="200">
          <template #default="{ row }">
            <div v-if="row.metrics && row.metrics.map !== undefined && !isNaN(row.metrics.map)">
              <div>mAP: {{ (row.metrics.map * 100).toFixed(2) }}%</div>
              <div>精确率: {{ (row.metrics.precision * 100).toFixed(2) }}%</div>
              <div>召回率: {{ (row.metrics.recall * 100).toFixed(2) }}%</div>
            </div>
            <span v-else>未训练</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="320">
          <template #default="{ row }">
            <el-button type="success" link @click="handleTrainDirect(row)" v-if="row.type === 'custom'">
              <el-icon><VideoPlay /></el-icon>
              训练
            </el-button>
            <el-button type="primary" link @click="editModel(row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button type="primary" link @click="viewModelInfo(row.id)">
              查看详情
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
          <el-select v-model="newModel.dataset_id" placeholder="选择数据集" style="width: 100%">
            <el-option
              v-for="dataset in datasets"
              :key="dataset.id"
              :label="dataset.name"
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
            <el-option label="yolov8n (小型模型)" value="yolov8n.pt" />
            <el-option label="yolovn (小型模型)" value="yolov11n.pt" />
          </el-select>
        </el-form-item>
        <el-form-item label="迭代次数" prop="epochs">
          <el-input-number v-model="newModel.epochs" :min="1" :max="1000" :step="10" style="width: 100%" />
          <div style="color: #909399; font-size: 12px; margin-top: 5px;">建议值：100-300</div>
        </el-form-item>
        <el-form-item label="批次大小" prop="batch">
          <el-input-number v-model="newModel.batch" :min="1" :max="64" :step="1" style="width: 100%" />
          <div style="color: #909399; font-size: 12px; margin-top: 5px;">建议值：4-32（根据显存调整）</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="cancelCreate">取消</el-button>
        <el-button type="primary" @click="handleCreateAndTrain" :loading="creating">
          {{ creating ? '创建中...' : '创建并开始训练' }}
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
          <el-select v-model="editModelForm.dataset_id" placeholder="选择数据集" style="width: 100%">
            <el-option
              v-for="dataset in datasets"
              :key="dataset.id"
              :label="dataset.name"
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
            <el-option label="yolov8n (小型模型)" value="yolov8n.pt" />
            <el-option label="yolov11n (小型模型)" value="yolov11n.pt" />
          </el-select>
        </el-form-item>
        <el-form-item label="迭代次数" prop="epochs">
          <el-input-number v-model="editModelForm.epochs" :min="1" :max="1000" :step="10" style="width: 100%" />
          <div style="color: #909399; font-size: 12px; margin-top: 5px;">建议值：100-300</div>
        </el-form-item>
        <el-form-item label="批次大小" prop="batch">
          <el-input-number v-model="editModelForm.batch" :min="1" :max="64" :step="1" style="width: 100%" />
          <div style="color: #909399; font-size: 12px; margin-top: 5px;">建议值：4-32（根据显存调整）</div>
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { modelApi, type Model } from '../api/model'
import { datasetApi, type Dataset } from '../api/dataset'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Plus, VideoPlay, Edit } from '@element-plus/icons-vue'

const router = useRouter()
const models = ref<Model[]>([])
const datasets = ref<Dataset[]>([])
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const modelFormRef = ref<FormInstance>()
const editFormRef = ref<FormInstance>()
const training = ref(false)
const updating = ref(false)
const editingModel = ref<Model | null>(null)

const newModel = ref({
  name: '',
  description: '',
  dataset_id: undefined as number | undefined,
  base_model: 'yolo11n.pt',
  epochs: 100,
  batch: 8
})

const editModelForm = ref({
  name: '',
  description: '',
  dataset_id: undefined as number | undefined,
  base_model: 'yolo11n.pt',
  epochs: 100,
  batch: 8
})

const creating = ref(false)

const modelRules: FormRules = {
  name: [{ required: true, message: '请输入模型名称', trigger: 'blur' }],
  dataset_id: [{ required: true, message: '请选择训练数据集', trigger: 'change' }],
  base_model: [{ required: true, message: '请选择基础模型', trigger: 'change' }],
  epochs: [{ required: true, message: '请输入迭代次数', trigger: 'blur' }],
  batch: [{ required: true, message: '请输入批次大小', trigger: 'blur' }]
}

const loadModels = async () => {
  try {
    models.value = await modelApi.getModels()
  } catch (error) {
    ElMessage.error('加载模型列表失败')
  }
}

const loadDatasets = async () => {
  try {
    datasets.value = await datasetApi.getDatasets()
  } catch (error) {
    ElMessage.error('加载数据集列表失败')
  }
}

const cancelCreate = () => {
  showCreateDialog.value = false
  newModel.value = {
    name: '',
    description: '',
    dataset_id: undefined,
    base_model: 'yolo11n.pt',
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
        const createdModel = await modelApi.createModel({
          name: newModel.value.name,
          type: 'custom',
          description: newModel.value.description,
          dataset_id: newModel.value.dataset_id,
          base_model: newModel.value.base_model,
          epochs: newModel.value.epochs,
          batch: newModel.value.batch,
          imgsz: 640
        })
        
        // 创建成功后立即开始训练（使用保存的参数）
        await modelApi.trainModel({
          model_id: createdModel.id
        })
        
        ElMessage.success('模型创建成功，训练任务已启动，请稍后查看训练结果')
        cancelCreate()
        loadModels()
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

const showCreateDialogHandler = () => {
  newModel.value = {
    name: '',
    description: '',
    dataset_id: undefined,
    base_model: 'yolo11n.pt',
    epochs: 100,
    batch: 8
  }
  showCreateDialog.value = true
  loadDatasets()
}

const editModel = (model: Model) => {
  editingModel.value = model
  const trainingParams = model.training_params || {}
  editModelForm.value = {
    name: model.name,
    description: model.description || '',
    dataset_id: trainingParams.dataset_id,
    base_model: trainingParams.base_model || 'yolo11n.pt',
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
    base_model: 'yolo11n.pt',
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

const handleTrainDirect = async (model: Model) => {
  try {
    training.value = true
    await modelApi.trainModel({
      model_id: model.id
    })
    
    ElMessage.success('训练任务已启动，请稍后查看训练结果')
    loadModels()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || error.message || '训练启动失败')
  } finally {
    training.value = false
  }
}

onMounted(() => {
  loadModels()
  loadDatasets()
})
</script>

<style scoped>
.model-manager-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>

