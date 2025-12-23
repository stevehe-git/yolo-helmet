<template>
  <el-container class="layout-container">
    <el-aside :width="isCollapse ? '64px' : '200px'" class="sidebar">
      <div class="logo">
        <el-icon :size="24" :style="{ marginRight: isCollapse ? '0' : '8px' }"><Lock /></el-icon>
        <h2 v-show="!isCollapse">安全帽检测</h2>
      </div>
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
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
        <el-menu-item index="/dataset/manager" v-if="isAdmin">
          <el-icon><Folder /></el-icon>
          <span>数据集管理</span>
        </el-menu-item>
        <el-menu-item index="/model/manager" v-if="isAdmin">
          <el-icon><Box /></el-icon>
          <span>模型管理</span>
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
    <el-container style="width: 100%; height: 100%;">
      <el-header class="header" style="width: 100%;">
        <div class="header-left">
          <el-button
            :icon="isCollapse ? Expand : Fold"
            circle
            @click="toggleCollapse"
            style="margin-right: 15px;"
          />
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
      <el-main class="main-content" style="width: 100%; height: calc(100vh - 60px);">
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
  ArrowDown,
  Lock,
  Fold,
  Expand
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

// 响应式状态
const currentUser = ref<User | null>(null)
const isCollapse = ref<boolean>(false)

// 计算属性
const isAdmin = computed(() => currentUser.value?.role === 'admin')
const activeMenu = computed(() => route.path)

// 方法
const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}

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
  width: 100%;
  height: 100vh;
  margin: 0;
  padding: 0;
  overflow: hidden;
}

.sidebar {
  background-color: #304156;
  overflow: hidden;
  flex-shrink: 0;
  transition: width 0.3s;
}

.logo {
  height: 60px;
  line-height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #2b3a4a;
  color: #fff;
  padding: 0 10px;
  overflow: hidden;
  white-space: nowrap;
}

.logo .el-icon {
  color: #fff;
  flex-shrink: 0;
}

.logo h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
  display: inline-block;
}

.sidebar-menu {
  border-right: none;
  height: calc(100vh - 60px);
  overflow-y: auto;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 200px;
}

.sidebar-menu.el-menu--collapse {
  width: 64px;
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
  width: 100%;
  height: 100%;
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
  overflow-x: hidden;
}
</style>

