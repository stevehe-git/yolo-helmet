<template>
  <div class="dataset-manager-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>数据集管理</span>
          <el-button type="primary" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon>
            创建数据集
          </el-button>
        </div>
      </template>

      <el-table :data="datasets" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="数据集名称" />
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="image_count" label="图片数量" width="120" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="250">
          <template #default="{ row }">
            <el-button type="primary" link @click="showUploadDialog(row)">
              上传数据
            </el-button>
            <el-button type="info" link @click="viewDataset(row.id)">
              查看详情
            </el-button>
            <el-button type="danger" link @click="deleteDataset(row.id)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showCreateDialog" title="创建数据集" width="500px">
      <el-form :model="newDataset" :rules="datasetRules" ref="datasetFormRef" label-width="100px">
        <el-form-item label="数据集名称" prop="name">
          <el-input v-model="newDataset.name" placeholder="请输入数据集名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="newDataset.description"
            type="textarea"
            :rows="3"
            placeholder="请输入数据集描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreateDataset">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showUploadDialog" :title="`上传数据 - ${selectedDataset?.name}`" width="600px">
      <el-upload
        class="upload-demo"
        drag
        :auto-upload="false"
        :on-change="handleFileChange"
        :file-list="fileList"
        multiple
        accept="image/*"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          将图片拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持批量上传图片文件
          </div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="showUploadDialog = false">取消</el-button>
        <el-button type="primary" @click="handleUpload" :loading="uploading">
          上传
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { datasetApi, type Dataset } from '../api/dataset'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import type { UploadFile } from 'element-plus'
import { Plus, UploadFilled } from '@element-plus/icons-vue'

const datasets = ref<Dataset[]>([])
const showCreateDialog = ref(false)
const showUploadDialog = ref(false)
const datasetFormRef = ref<FormInstance>()
const uploading = ref(false)
const selectedDataset = ref<Dataset | null>(null)
const fileList = ref<UploadFile[]>([])

const newDataset = ref({
  name: '',
  description: ''
})

const datasetRules: FormRules = {
  name: [{ required: true, message: '请输入数据集名称', trigger: 'blur' }]
}

const loadDatasets = async () => {
  try {
    datasets.value = await datasetApi.getDatasets()
  } catch (error) {
    ElMessage.error('加载数据集列表失败')
  }
}

const handleCreateDataset = async () => {
  if (!datasetFormRef.value) return
  
  await datasetFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await datasetApi.createDataset(newDataset.value)
        ElMessage.success('数据集创建成功')
        showCreateDialog.value = false
        newDataset.value = { name: '', description: '' }
        loadDatasets()
      } catch (error: any) {
        ElMessage.error(error.response?.data?.message || '创建数据集失败')
      }
    }
  })
}

const showUploadDialogHandler = (dataset: Dataset) => {
  selectedDataset.value = dataset
  fileList.value = []
  showUploadDialog.value = true
}

const handleFileChange = (file: UploadFile) => {
  fileList.value.push(file)
}

const handleUpload = async () => {
  if (!selectedDataset.value || fileList.value.length === 0) {
    ElMessage.warning('请选择要上传的文件')
    return
  }

  uploading.value = true
  try {
    const formData = new FormData()
    fileList.value.forEach(file => {
      if (file.raw) {
        formData.append('images', file.raw)
      }
    })

    await datasetApi.uploadDataset(selectedDataset.value.id, formData)
    ElMessage.success('上传成功')
    showUploadDialog.value = false
    fileList.value = []
    loadDatasets()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || '上传失败')
  } finally {
    uploading.value = false
  }
}

const viewDataset = async (id: number) => {
  try {
    const dataset = await datasetApi.getDataset(id)
    ElMessageBox.alert(
      `数据集名称: ${dataset.name}\n描述: ${dataset.description || '无'}\n图片数量: ${dataset.image_count}`,
      '数据集详情'
    )
  } catch (error) {
    ElMessage.error('获取数据集详情失败')
  }
}

const deleteDataset = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除该数据集吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await datasetApi.deleteDataset(id)
    ElMessage.success('删除成功')
    loadDatasets()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  loadDatasets()
})
</script>

<style scoped>
.dataset-manager-container {
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
</style>

