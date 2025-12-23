# YOLO 安全帽检测系统 - 前端

## 技术栈

- Vue.js 3
- TypeScript
- Element Plus 2.4.1
- ECharts 5.4.3
- Vue Router 4
- Axios
- Vite

## 安装步骤

1. 安装依赖：
```bash
npm install
```

2. 启动开发服务器：
```bash
npm run dev
```

应用将在 http://localhost:5173 启动

3. 构建生产版本：
```bash
npm run build
```

## 项目结构

```
src/
├── api/          # API 接口定义
├── components/   # 组件
├── layouts/      # 布局组件
├── router/       # 路由配置
├── views/         # 页面视图
├── App.vue        # 根组件
└── main.ts        # 入口文件
```

## 功能模块

- 用户登录/注册
- 图片检测
- 视频检测
- 实时检测
- 模型管理（管理员）
- 数据集管理（管理员）
- 用户管理（管理员）
- 控制台统计（管理员）

## 配置

后端 API 地址在 `vite.config.ts` 中配置，默认代理到 `http://localhost:5000`

