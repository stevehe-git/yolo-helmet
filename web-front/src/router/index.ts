import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('../layouts/MainLayout.vue'),
    redirect: '/home',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'home',
        name: 'Home',
        component: () => import('../views/Home.vue')
      },
      {
        path: 'detect/image',
        name: 'ImageDetect',
        component: () => import('../views/DetectImage.vue')
      },
      {
        path: 'detect/video',
        name: 'VideoDetect',
        component: () => import('../views/DetectVideo.vue')
      },
      {
        path: 'detect/realtime',
        name: 'RealtimeDetect',
        component: () => import('../views/DetectRealtime.vue')
      },
      {
        path: 'model/manager',
        name: 'ModelManager',
        component: () => import('../views/ModelManager.vue')
      },
      {
        path: 'model/info/:id',
        name: 'ModelInfo',
        component: () => import('../views/ModelInfo.vue')
      },
      {
        path: 'dataset/manager',
        name: 'DatasetManager',
        component: () => import('../views/DatasetManager.vue')
      },
      {
        path: 'user/manager',
        name: 'UserManager',
        component: () => import('../views/UserManager.vue')
      },
      {
        path: 'console',
        name: 'Console',
        component: () => import('../views/Console.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if ((to.path === '/login' || to.path === '/register') && token) {
    next('/')
  } else {
    next()
  }
})

export default router

