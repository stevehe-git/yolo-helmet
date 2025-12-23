<template>
  <el-container class="layout-container">
    <el-aside width="200px" class="sidebar">
      <div class="logo">
        <h2>安全帽检测</h2>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        class="sidebar-menu"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/home">
          <el-icon><HomeFilled /></el-icon>
          <span>首页</span>
        </el-menu-item>
        <el-sub-menu index="detect">
          <template #title>
            <el-icon><Camera /></el-icon>
            <span>安全帽检测</span>
          </template>
          <el-menu-item index="/detect/image">图片检测</el-menu-item>
          <el-menu-item index="/detect/video">视频检测</el-menu-item>
          <el-menu-item index="/detect/realtime">实时检测</el-menu-item>
        </el-sub-menu>
        <el-menu-item index="/model/manager" v-if="isAdmin">
          <el-icon><Box /></el-icon>
          <span>模型管理</span>
        </el-menu-item>
        <el-menu-item index="/dataset/manager" v-if="isAdmin">
          <el-icon><Folder /></el-icon>
          <span>数据集管理</span>
        </el-menu-item>
        <el-menu-item index="/user/manager" v-if="isAdmin">
          <el-icon><UserIcon /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        <el-menu-item index="/console" v-if="isAdmin">
          <el-icon><DataAnalysis /></el-icon>
          <span>控制台</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <span class="title">{{ pageTitle }}</span>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-icon><UserIcon /></el-icon>
              {{ currentUser?.username }}
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { authApi, type User } from '../api/auth'
import { ElMessage } from 'element-plus'
import {
  HomeFilled,
  Camera,
  VideoCamera,
  Monitor,
  Box,
  Folder,
  User as UserIcon,
  DataAnalysis,
  ArrowDown
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const currentUser = ref<User | null>(null)
const isAdmin = computed(() => currentUser.value?.role === 'admin')

const activeMenu = computed(() => route.path)

const pageTitle = computed(() => {
  const titles: Record<string, string> = {
    '/home': '首页',
    '/detect/image': '图片检测',
    '/detect/video': '视频检测',
    '/detect/realtime': '实时检测',
    '/model/manager': '模型管理',
    '/dataset/manager': '数据集管理',
    '/user/manager': '用户管理',
    '/console': '控制台'
  }
  return titles[route.path] || '安全帽检测系统'
})

const handleCommand = (command: string) => {
  if (command === 'logout') {
    authApi.logout().then(() => {
      localStorage.removeItem('token')
      router.push('/login')
      ElMessage.success('已退出登录')
    })
  }
}

onMounted(() => {
  authApi.getCurrentUser().then((user) => {
    currentUser.value = user
  }).catch(() => {
    router.push('/login')
  })
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.sidebar {
  background-color: #304156;
  overflow: hidden;
}

.logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  background-color: #2b3a4a;
  color: #fff;
}

.logo h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
}

.sidebar-menu {
  border-right: none;
  height: calc(100vh - 60px);
  overflow-y: auto;
}

.header {
  background-color: #fff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}

.header-left .title {
  font-size: 20px;
  font-weight: 500;
  color: #303133;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: #606266;
}

.user-info .el-icon {
  margin-right: 5px;
}

.main-content {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}
</style>

