<template>
  <div class="model-manager-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>模型管理</span>
          <el-button type="primary" @click="showCreateDialog = true">
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
            <div v-if="row.metrics">
              <div>mAP: {{ (row.metrics.map * 100).toFixed(2) }}%</div>
              <div>精确率: {{ (row.metrics.precision * 100).toFixed(2) }}%</div>
              <div>召回率: {{ (row.metrics.recall * 100).toFixed(2) }}%</div>
            </div>
            <span v-else>未训练</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
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

    <el-dialog v-model="showCreateDialog" title="创建模型" width="500px">
      <el-form :model="newModel" :rules="modelRules" ref="modelFormRef" label-width="100px">
        <el-form-item label="模型名称" prop="name">
          <el-input v-model="newModel.name" placeholder="请输入模型名称" />
        </el-form-item>
        <el-form-item label="模型类型" prop="type">
          <el-select v-model="newModel.type" placeholder="请选择模型类型">
            <el-option label="通用模型" value="general" />
            <el-option label="定制模型" value="custom" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreateModel">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { modelApi, type Model } from '../api/model'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const router = useRouter()
const models = ref<Model[]>([])
const showCreateDialog = ref(false)
const modelFormRef = ref<FormInstance>()

const newModel = ref({
  name: '',
  type: 'general'
})

const modelRules: FormRules = {
  name: [{ required: true, message: '请输入模型名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择模型类型', trigger: 'change' }]
}

const loadModels = async () => {
  try {
    models.value = await modelApi.getModels()
  } catch (error) {
    ElMessage.error('加载模型列表失败')
  }
}

const handleCreateModel = async () => {
  if (!modelFormRef.value) return
  
  await modelFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await modelApi.createModel(newModel.value)
        ElMessage.success('模型创建成功')
        showCreateDialog.value = false
        newModel.value = { name: '', type: 'general' }
        loadModels()
      } catch (error: any) {
        ElMessage.error(error.response?.data?.message || '创建模型失败')
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

onMounted(() => {
  loadModels()
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

