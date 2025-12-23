<template>
  <div class="dataset-manager-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>数据集管理</span>
          <div>
            <el-button @click="showCreateDialog = true" style="margin-right: 10px;">
              <el-icon><Plus /></el-icon>
              创建数据集
            </el-button>
            <el-button type="primary" @click="handleUploadDataset">
              <el-icon><UploadFilled /></el-icon>
              上传数据集
            </el-button>
          </div>
        </div>
      </template>

      <!-- 搜索和筛选 -->
      <div class="toolbar">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索数据集名称或描述"
          style="width: 300px"
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>

      <!-- 提示信息 -->
      <el-alert
        v-if="!loading && datasets.length === 0"
        title="提示"
        type="warning"
        :closable="false"
        show-icon
        style="margin-bottom: 20px;"
      >
        <template #default>
          <span>当前没有数据集，请先创建数据集后再上传ZIP文件。</span>
        </template>
      </el-alert>

      <el-table :data="filteredDatasets" style="width: 100%" v-loading="loading" empty-text="暂无数据">
        <el-table-column prop="name" label="数据集名称" min-width="200">
          <template #default="{ row }">
            <div style="display: flex; align-items: center;">
              <el-icon style="margin-right: 8px;"><Document /></el-icon>
              <el-link type="primary" @click="viewDatasetDetail(row.id)">
                {{ row.name }}
              </el-link>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="300" show-overflow-tooltip />
        <el-table-column label="数据集统计" width="250" align="center">
          <template #default="{ row }">
            <div v-if="row.train_count || row.val_count || row.test_count" style="text-align: left; font-size: 12px;">
              <div>训练: {{ row.train_count || 0 }}张</div>
              <div>验证: {{ row.val_count || 0 }}张</div>
              <div>测试: {{ row.test_count || 0 }}张</div>
            </div>
            <span v-else style="color: #909399;">-</span>
          </template>
        </el-table-column>
        <el-table-column label="文件大小" width="120" align="center">
          <template #default="{ row }">
            <span v-if="row.file_size">{{ formatFileSize(row.file_size) }}</span>
            <span v-else style="color: #909399;">-</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="120" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.status === 'validated'" type="success" effect="plain">验证通过</el-tag>
            <el-tag v-else-if="row.status === 'failed'" type="danger" effect="plain">验证失败</el-tag>
            <el-tag v-else type="info" effect="plain">待验证</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewDatasetDetail(row.id)">
              <el-icon><View /></el-icon>
              查看
            </el-button>
            <el-button type="warning" link @click="editDataset(row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-dropdown @command="(cmd: string) => handleMoreAction(cmd, row)">
              <el-button type="primary" link>
                更多<el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="upload">
                    <el-icon><UploadFilled /></el-icon>
                    上传数据
                  </el-dropdown-item>
                  <el-dropdown-item command="delete" divided>
                    <el-icon><Delete /></el-icon>
                    删除
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建数据集对话框 -->
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
        <el-button @click="cancelCreate">取消</el-button>
        <el-button type="primary" @click="handleCreateDataset">确定</el-button>
      </template>
    </el-dialog>

    <!-- 编辑数据集对话框 -->
    <el-dialog v-model="showEditDialog" title="编辑数据集" width="500px">
      <el-form :model="editDatasetForm" :rules="datasetRules" ref="editFormRef" label-width="100px">
        <el-form-item label="数据集名称" prop="name">
          <el-input v-model="editDatasetForm.name" placeholder="请输入数据集名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="editDatasetForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入数据集描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="cancelEdit">取消</el-button>
        <el-button type="primary" @click="handleUpdateDataset">确定</el-button>
      </template>
    </el-dialog>

    <!-- 上传数据集对话框 -->
    <el-dialog 
      v-model="showUploadDialog" 
      :title="selectedDataset ? `上传数据 - ${selectedDataset.name}` : '上传数据集'" 
      width="800px"
    >
      <el-upload
        class="upload-demo"
        drag
        :auto-upload="false"
        :on-change="handleFileChange"
        :on-remove="handleFileRemove"
        :file-list="fileList"
        :limit="1"
        accept=".zip"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          将ZIP文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            只支持ZIP格式文件，请确保ZIP文件符合下方格式要求
          </div>
        </template>
      </el-upload>
      <div v-if="fileList.length > 0 && fileList[0]" class="upload-info">
        <p>已选择文件: <strong>{{ fileList[0].name }}</strong></p>
        <p v-if="fileList[0].size">文件大小: <strong>{{ formatFileSize(fileList[0].size) }}</strong></p>
      </div>

      <!-- 格式要求说明 -->
      <el-card class="format-requirements" shadow="never">
        <template #header>
          <div style="display: flex; align-items: center;">
            <el-icon style="margin-right: 8px;"><InfoFilled /></el-icon>
            <span>数据集格式要求</span>
          </div>
        </template>
        <div class="requirements-content">
          <p style="margin: 0 0 10px 0; font-weight: 500;">ZIP文件需包含以下结构：</p>
          <ul class="requirements-list">
            <li><code>data.yaml</code> - 数据集配置文件</li>
            <li><code>train/images/</code> - 训练图片目录</li>
            <li><code>train/labels/</code> - 训练标签目录</li>
            <li><code>valid/images/</code> - 验证图片目录</li>
            <li><code>valid/labels/</code> - 验证标签目录</li>
            <li><code>test/images/</code> - 测试图片目录（可选）</li>
            <li><code>test/labels/</code> - 测试标签目录（可选）</li>
          </ul>
        </div>
      </el-card>
      <template #footer>
        <el-button @click="cancelUpload">取消</el-button>
        <el-button type="primary" @click="handleUpload" :loading="uploading" :disabled="fileList.length === 0 || !selectedDataset">
          上传
        </el-button>
      </template>
    </el-dialog>

    <!-- 数据集详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="数据集详情"
      width="600px"
      @closed="cancelDetail"
    >
      <div v-if="detailDataset" class="dataset-detail">
        <!-- 数据集详情 -->
        <el-descriptions :column="1" border>
          <el-descriptions-item label="名称">{{ detailDataset.name }}</el-descriptions-item>
          <el-descriptions-item label="文件大小">
            {{ detailDataset.file_size ? formatFileSize(detailDataset.file_size) : '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag v-if="detailDataset.status === 'validated'" type="success" effect="plain">验证通过</el-tag>
            <el-tag v-else-if="detailDataset.status === 'failed'" type="danger" effect="plain">验证失败</el-tag>
            <el-tag v-else type="info" effect="plain">待验证</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="上传时间">
            {{ detailDataset.created_at ? formatDateTime(detailDataset.created_at) : '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="描述">
            {{ detailDataset.description || '无' }}
          </el-descriptions-item>
        </el-descriptions>

        <!-- 数据集统计信息 -->
        <div class="statistics-section">
          <h3>数据集统计信息</h3>
          <div class="statistics-cards">
            <el-card class="stat-card" shadow="hover">
              <div class="stat-number">{{ detailDataset.train_count || 0 }}</div>
              <div class="stat-label">训练图片</div>
            </el-card>
            <el-card class="stat-card" shadow="hover">
              <div class="stat-number">{{ detailDataset.val_count || 0 }}</div>
              <div class="stat-label">验证图片</div>
            </el-card>
            <el-card class="stat-card" shadow="hover">
              <div class="stat-number">{{ detailDataset.test_count || 0 }}</div>
              <div class="stat-label">测试图片</div>
            </el-card>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="cancelDetail">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { datasetApi, type Dataset } from '../api/dataset'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import type { UploadFile } from 'element-plus'
import {
  Plus,
  UploadFilled,
  View,
  Edit,
  Delete,
  Search,
  Document,
  ArrowDown,
  InfoFilled
} from '@element-plus/icons-vue'

const datasets = ref<Dataset[]>([])
const loading = ref(false)
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const showUploadDialog = ref(false)
const showDetailDialog = ref(false)
const datasetFormRef = ref<FormInstance>()
const editFormRef = ref<FormInstance>()
const uploading = ref(false)
const selectedDataset = ref<Dataset | null>(null)
const detailDataset = ref<Dataset | null>(null)
const fileList = ref<UploadFile[]>([])
const searchKeyword = ref('')

const newDataset = ref({
  name: '',
  description: ''
})

const editDatasetForm = ref({
  name: '',
  description: ''
})

const datasetRules: FormRules = {
  name: [{ required: true, message: '请输入数据集名称', trigger: 'blur' }]
}

const filteredDatasets = computed(() => {
  if (!searchKeyword.value) {
    return datasets.value
  }
  const keyword = searchKeyword.value.toLowerCase()
  return datasets.value.filter(dataset => 
    dataset.name.toLowerCase().includes(keyword) ||
    (dataset.description && dataset.description.toLowerCase().includes(keyword))
  )
})

const loadDatasets = async () => {
  loading.value = true
  try {
    datasets.value = await datasetApi.getDatasets() as any
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || error.message || '加载数据集列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  // 搜索功能由 computed 自动处理
}

const handleCreateDataset = async () => {
  if (!datasetFormRef.value) return
  
  await datasetFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await datasetApi.createDataset(newDataset.value)
        ElMessage.success('数据集创建成功')
        cancelCreate()
        await loadDatasets()
        // 创建成功后，自动打开上传对话框
        const createdDataset = datasets.value.find(d => d.name === newDataset.value.name)
        if (createdDataset) {
          // 延迟一下，确保数据已加载
          setTimeout(() => {
            showUploadDialogHandler(createdDataset)
          }, 300)
        }
      } catch (error: any) {
        ElMessage.error(error.response?.data?.message || '创建数据集失败')
      }
    }
  })
}

const cancelCreate = () => {
  showCreateDialog.value = false
  newDataset.value = { name: '', description: '' }
  if (datasetFormRef.value) {
    datasetFormRef.value.resetFields()
  }
}

const editDataset = (dataset: Dataset) => {
  selectedDataset.value = dataset
  editDatasetForm.value = {
    name: dataset.name,
    description: dataset.description || ''
  }
  showEditDialog.value = true
}

const handleUpdateDataset = async () => {
  if (!editFormRef.value || !selectedDataset.value) return
  
  const datasetId = selectedDataset.value.id
  await editFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await datasetApi.updateDataset(datasetId, editDatasetForm.value)
        ElMessage.success('更新成功')
        cancelEdit()
        loadDatasets()
      } catch (error: any) {
        ElMessage.error(error.response?.data?.message || '更新数据集失败')
      }
    }
  })
}

const cancelEdit = () => {
  showEditDialog.value = false
  selectedDataset.value = null
  editDatasetForm.value = { name: '', description: '' }
  if (editFormRef.value) {
    editFormRef.value.resetFields()
  }
}

const handleUploadDataset = () => {
  // 如果没有数据集，提示先创建
  if (datasets.value.length === 0) {
    ElMessageBox.confirm(
      '当前没有数据集，请先创建数据集后再上传ZIP文件。',
      '提示',
      {
        confirmButtonText: '创建数据集',
        cancelButtonText: '取消',
        type: 'warning'
      }
    ).then(() => {
      showCreateDialog.value = true
    }).catch(() => {
      // 用户取消
    })
    return
  }
  
  // 如果只有一个数据集，直接使用
  if (datasets.value.length === 1) {
    const dataset = datasets.value[0]
    if (dataset) {
      showUploadDialogHandler(dataset)
    }
  } else {
    // 多个数据集，提示用户从表格中选择
    ElMessage.info('请从表格中选择要上传数据的数据集，然后点击"更多" -> "上传数据"')
  }
}

const showUploadDialogHandler = (dataset: Dataset) => {
  selectedDataset.value = dataset
  fileList.value = []
  showUploadDialog.value = true
}

const handleMoreAction = (command: string, row: Dataset) => {
  if (command === 'upload') {
    showUploadDialogHandler(row)
  } else if (command === 'delete') {
    deleteDataset(row.id)
  }
}

const cancelUpload = () => {
  showUploadDialog.value = false
  fileList.value = []
  selectedDataset.value = null
}

const handleFileChange = (file: UploadFile) => {
  // 只允许ZIP文件
  if (file.raw && !file.name.toLowerCase().endsWith('.zip')) {
    ElMessage.error('只支持ZIP格式文件')
    const index = fileList.value.findIndex(f => f.uid === file.uid)
    if (index > -1) {
      fileList.value.splice(index, 1)
    }
    return
  }
  // 限制只能上传一个文件
  if (fileList.value.length > 0) {
    fileList.value = [file]
  } else {
    fileList.value.push(file)
  }
}

const handleFileRemove = (file: UploadFile) => {
  const index = fileList.value.findIndex(f => f.uid === file.uid)
  if (index > -1) {
    fileList.value.splice(index, 1)
  }
}

const handleUpload = async () => {
  if (!selectedDataset.value || fileList.value.length === 0) {
    ElMessage.warning('请选择要上传的ZIP文件')
    return
  }

  // 验证文件格式
  const file = fileList.value[0]
  if (!file || !file.name.toLowerCase().endsWith('.zip')) {
    ElMessage.error('只支持ZIP格式文件')
    return
  }

  uploading.value = true
  try {
    const formData = new FormData()
    if (file.raw) {
      formData.append('zip', file.raw)
    } else {
      ElMessage.error('文件读取失败，请重新选择')
      uploading.value = false
      return
    }

    const result: any = await datasetApi.uploadDataset(selectedDataset.value.id, formData)
    
    // 显示成功消息
    if (result?.warnings && result.warnings.length > 0) {
      ElMessage.warning({
        message: result.message || '数据集上传成功，但有警告',
        duration: 5000
      })
      // 显示详细警告
      setTimeout(() => {
        ElMessageBox.alert(
          result.warnings.join('\n'),
          '格式警告',
          { type: 'warning' }
        )
      }, 500)
    } else {
      ElMessage.success(result?.message || '数据集上传成功')
    }
    
    cancelUpload()
    loadDatasets()
  } catch (error: any) {
    // 显示详细错误信息
    let errorMessage = error.response?.data?.message || error.message || '上传失败'
    
    if (error.response?.data?.errors && Array.isArray(error.response.data.errors)) {
      errorMessage = error.response.data.errors.join('\n')
      ElMessageBox.alert(
        errorMessage,
        '格式验证失败',
        { type: 'error' }
      )
    } else {
      ElMessage.error(errorMessage)
    }
  } finally {
    uploading.value = false
  }
}

const viewDatasetDetail = async (id: number) => {
  try {
    // 从列表中查找数据集
    const dataset = datasets.value.find(d => d.id === id)
    if (dataset) {
      detailDataset.value = dataset
      showDetailDialog.value = true
    } else {
      // 如果列表中没有，从API获取
      const fetchedDataset = await datasetApi.getDataset(id) as any
      detailDataset.value = fetchedDataset
      showDetailDialog.value = true
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || error.message || '加载数据集详情失败')
  }
}

const cancelDetail = () => {
  showDetailDialog.value = false
  detailDataset.value = null
}

const formatDateTime = (dateTimeStr: string) => {
  if (!dateTimeStr) return '-'
  try {
    const date = new Date(dateTimeStr)
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    const seconds = String(date.getSeconds()).padStart(2, '0')
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
  } catch (e) {
    return dateTimeStr
  }
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const deleteDataset = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除该数据集吗？删除后无法恢复！', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await datasetApi.deleteDataset(id)
    ElMessage.success('删除成功')
    loadDatasets()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.message || '删除失败')
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

.toolbar {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.upload-demo {
  margin-bottom: 20px;
}

.upload-info {
  margin-top: 15px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
  text-align: center;
}

.upload-info p {
  margin: 5px 0;
  color: #606266;
}

.format-requirements {
  margin-bottom: 20px;
  border: 1px solid #e4e7ed;
}

.requirements-content {
  font-size: 14px;
  color: #606266;
}

.requirements-list {
  margin: 10px 0 0 20px;
  padding: 0;
  line-height: 2;
}

.requirements-list li {
  margin: 5px 0;
}

.requirements-list code {
  background-color: #f5f7fa;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  color: #409eff;
}

.dataset-detail {
  padding: 10px 0;
}

.statistics-section {
  margin-top: 30px;
}

.statistics-section h3 {
  margin: 0 0 20px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.statistics-cards {
  display: flex;
  gap: 15px;
  justify-content: space-between;
}

.stat-card {
  flex: 1;
  text-align: center;
  cursor: pointer;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-number {
  font-size: 36px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 10px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}
</style>
