<template>
  <div class="home-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="welcome-card">
          <h1>欢迎使用安全帽检测系统</h1>
          <p>基于 YOLO11n 的工程施工员安全帽检测平台</p>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="8" v-for="card in featureCards" :key="card.title">
        <el-card class="feature-card" @click="handleCardClick(card.route)">
          <div class="card-content">
            <el-icon :size="40" :color="card.color">
              <component :is="card.icon" />
            </el-icon>
            <h3>{{ card.title }}</h3>
            <p>{{ card.description }}</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px" v-if="isAdmin">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>系统统计</span>
          </template>
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-value">{{ statistics.total_detections || 0 }}</div>
              <div class="stat-label">总检测次数</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ statistics.with_helmet || 0 }}</div>
              <div class="stat-label">佩戴安全帽</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ statistics.without_helmet || 0 }}</div>
              <div class="stat-label">未佩戴安全帽</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ (statistics.detection_rate * 100).toFixed(1) }}%</div>
              <div class="stat-label">检测率</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>快速操作</span>
          </template>
          <el-space direction="vertical" style="width: 100%">
            <el-button type="primary" @click="$router.push('/detect/image')" style="width: 100%">
              图片检测
            </el-button>
            <el-button type="success" @click="$router.push('/detect/video')" style="width: 100%">
              视频检测
            </el-button>
            <el-button type="warning" @click="$router.push('/detect/realtime')" style="width: 100%">
              实时检测
            </el-button>
          </el-space>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { statisticsApi } from '../api/statistics'
import { authApi, type User } from '../api/auth'
import { Camera, VideoCamera, Monitor, Box, Folder, User as UserIcon, DataAnalysis } from '@element-plus/icons-vue'

const router = useRouter()
const currentUser = ref<User | null>(null)
const statistics = ref({
  total_detections: 0,
  with_helmet: 0,
  without_helmet: 0,
  detection_rate: 0
})

const isAdmin = computed(() => currentUser.value?.role === 'admin')

const featureCards = computed(() => {
  const base = [
    {
      title: '图片检测',
      description: '上传图片进行安全帽检测',
      icon: 'Camera',
      color: '#409EFF',
      route: '/detect/image'
    },
    {
      title: '视频检测',
      description: '上传视频进行批量检测',
      icon: 'VideoCamera',
      color: '#67C23A',
      route: '/detect/video'
    },
    {
      title: '实时检测',
      description: '使用摄像头进行实时检测',
      icon: 'Monitor',
      color: '#E6A23C',
      route: '/detect/realtime'
    }
  ]
  
  if (isAdmin.value) {
    base.push(
      {
        title: '模型管理',
        description: '管理检测模型',
        icon: 'Box',
        color: '#F56C6C',
        route: '/model/manager'
      },
      {
        title: '数据集管理',
        description: '管理训练数据集',
        icon: 'Folder',
        color: '#909399',
        route: '/dataset/manager'
      },
      {
        title: '用户管理',
        description: '管理系统用户',
        icon: 'User',
        color: '#606266',
        route: '/user/manager'
      }
    )
  }
  
  return base
})

const handleCardClick = (route: string) => {
  router.push(route)
}

onMounted(async () => {
  try {
    currentUser.value = await authApi.getCurrentUser()
    if (isAdmin.value) {
      const stats = await statisticsApi.getStatistics()
      statistics.value = stats
    }
  } catch (error) {
    console.error('Failed to load data:', error)
  }
})
</script>

<style scoped>
.home-container {
  padding: 20px;
}

.welcome-card {
  text-align: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.welcome-card h1 {
  margin: 0 0 10px 0;
  font-size: 32px;
}

.welcome-card p {
  margin: 0;
  font-size: 16px;
  opacity: 0.9;
}

.feature-card {
  cursor: pointer;
  transition: all 0.3s;
  height: 200px;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.card-content {
  text-align: center;
  padding: 20px;
}

.card-content h3 {
  margin: 15px 0 10px 0;
  color: #303133;
}

.card-content p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.stat-item {
  text-align: center;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 10px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}
</style>

