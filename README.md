# YOLO 安全帽检测系统

基于 YOLO11n 的工程施工员安全帽检测项目，提供图片、视频和实时检测功能，支持模型管理和数据分析。

## 项目简介

本项目是一个完整的基于深度学习的施工安全帽检测系统，采用前后端分离架构。系统使用 YOLO11n 模型进行安全帽检测，支持图片上传检测、视频批量检测和实时摄像头检测。同时提供模型管理、数据集管理、用户管理和数据统计分析等完整功能。

## 技术栈

### 前端技术栈

- **HTML5/CSS3**：页面结构和样式
- **Vue.js 3**：前端响应式框架
- **TypeScript**：类型安全的 JavaScript 超集
- **Element Plus 2.4.1**：UI 组件库
- **ECharts 5.4.3**：前端图表库（可视化检测统计数据）
- **Vue Router 4**：前端路由管理
- **Axios**：HTTP 客户端
- **Vite**：前端构建工具

### 后端技术栈

- **Python 3.8+**：主要编程语言
- **Flask 2.3.3**：Web 应用框架
- **Flask-CORS 4.0.0**：跨域资源共享支持
- **Flask-SQLAlchemy 3.0.5**：ORM 数据库操作
- **Flask-Migrate 4.0.5**：数据库迁移工具
- **Ultralytics 8.0.200**：YOLO 模型库（基于 YOLO11n 实现安全帽检测）
- **PyTorch 2.0+**：深度学习框架
- **Pillow 10.0.1**：图像处理库（图片预处理、格式转换）
- **OpenCV 4.8+**：计算机视觉库
- **PyJWT 2.8+**：JWT 认证
- **SQLite**：轻量级数据库
- **Watchdog 2.0+**：文件监控（Flask 调试模式需要）

## 功能模块

### 用户管理

- **用户登录**：支持用户名密码登录，JWT Token 认证
- **用户注册**：新用户可注册账号，支持邮箱验证
- **账户验证**：确保系统安全性（仅授权用户可使用检测功能）
- **角色管理**：支持管理员和普通用户两种角色
- **错误提示**：友好的中文错误提示信息

### 安全帽检测

- **图片检测**：
  - 支持本地施工场景图片上传（JPG/PNG 格式）
  - 基于 YOLO11n 模型进行施工员安全帽佩戴状态检测
  - 分类：佩戴安全帽、未佩戴安全帽
  - 结果展示：显示检测结果及置信度，支持单张图片多目标检测结果标注
  - 模型选择：支持选择不同的检测模型
  - **模型验证**：选择未训练完成的模型时会提示警告，并询问是否继续使用

- **视频检测**：
  - 支持视频文件上传（MP4/AVI 格式）
  - 批量处理视频帧，生成检测结果视频
  - 提供检测摘要统计和关键帧展示
  - **模型验证**：选择未训练完成的模型时会提示警告

- **实时检测**：
  - 基于摄像头进行实时安全帽检测
  - 实时显示检测统计和检测历史
  - 支持开始/停止检测控制
  - **模型验证**：选择未训练完成的模型时会提示警告

- **多模型支持**：提供已训练通用安全帽检测模型和定制化训练模型两种选择

### 模型管理（管理员功能）

- **模型列表**：查看所有可用模型，显示模型类型、创建时间等信息
- **模型创建**：创建新的通用或定制模型
- **模型删除**：删除不需要的模型
- **模型详情**：
  - 查看模型基本信息
  - 查看性能指标（mAP、精确率、召回率、F1 值）
  - 查看训练数据（损失曲线、性能指标曲线）
- **模型训练**：支持使用数据集训练自定义模型
- **训练状态**：显示模型是否已完成训练（通过 metrics 字段判断）

### 数据集管理（管理员功能）

- **数据集列表**：查看所有数据集，显示数据集名称、状态、文件大小、图片数量等信息
- **数据集创建**：创建新的数据集，支持添加描述信息
- **数据集上传**：
  - **ZIP 文件上传**：支持上传 ZIP 格式的数据集包
  - **格式验证**：自动验证数据集目录结构是否符合要求
  - **自动统计**：自动统计训练集、验证集、测试集的图片数量
  - **状态管理**：显示数据集验证状态（待验证、验证通过、验证失败）
- **数据集详情**：查看数据集详细信息，包括：
  - 基本信息（名称、大小、状态、上传时间）
  - 统计信息（训练图片数、验证图片数、测试图片数）
- **数据集删除**：删除不需要的数据集
- **搜索功能**：支持按名称或描述搜索数据集

#### 数据集格式要求

上传的 ZIP 文件需包含以下目录结构：

```
dataset.zip
├── data.yaml          # 数据集配置文件（可选，但推荐）
├── train/             # 训练集目录
│   ├── images/        # 训练图片目录
│   └── labels/        # 训练标签目录
├── valid/             # 验证集目录
│   ├── images/        # 验证图片目录
│   └── labels/        # 验证标签目录
└── test/              # 测试集目录（可选）
    ├── images/        # 测试图片目录
    └── labels/        # 测试标签目录
```

**必需目录**：
- `train/images/` - 训练图片目录
- `train/labels/` - 训练标签目录
- `valid/images/` - 验证图片目录
- `valid/labels/` - 验证标签目录

**可选目录**：
- `test/images/` - 测试图片目录
- `test/labels/` - 测试标签目录
- `data.yaml` - 数据集配置文件（可选，但推荐）

系统会自动验证目录结构，如果缺少必需目录，上传将失败并显示错误信息。

### 用户管理（管理员功能）

- **用户列表**：查看所有系统用户，显示用户名、邮箱、角色、创建时间
- **用户创建**：创建新用户账号，支持设置用户名、邮箱、密码、角色
- **用户编辑**：修改用户信息（邮箱、角色）
- **用户删除**：删除用户账号
- **错误处理**：友好的错误提示，如邮箱重复等

### 数据统计（管理员功能）

- **检测统计**：总检测次数、佩戴/未佩戴统计、检测率
- **趋势分析**：检测趋势图表（折线图）
- **分布统计**：检测结果分布（饼图）
- **每日统计**：每日检测数量统计（柱状图）
- **历史记录**：查看历史检测记录

### 模型数据查看

- **训练数据展示**：查看模型训练过程中的损失曲线、迭代次数等核心数据和指标
- **验证结果展示**：查看模型在测试集上的漏检率、误检率、精准率等性能表现
- **精度统计**：展示模型检测精度（mAP）、召回率、F1 值等关键指标

## 项目结构

```
yolo-helmet/
├── web-front/                      # 前端项目（Vue 3 + TypeScript）
│   ├── src/
│   │   ├── api/            # API 接口定义
│   │   │   ├── auth.ts     # 认证接口
│   │   │   ├── detect.ts   # 检测接口
│   │   │   ├── model.ts    # 模型管理接口
│   │   │   ├── dataset.ts  # 数据集管理接口
│   │   │   ├── user.ts     # 用户管理接口
│   │   │   ├── statistics.ts # 统计接口
│   │   │   └── index.ts    # Axios 配置
│   │   ├── components/     # 组件
│   │   ├── layouts/        # 布局组件
│   │   │   └── MainLayout.vue # 主布局（包含侧边栏）
│   │   ├── router/         # 路由配置
│   │   │   └── index.ts
│   │   ├── views/          # 页面视图
│   │   │   ├── Login.vue      # 登录页
│   │   │   ├── Register.vue   # 注册页
│   │   │   ├── Home.vue        # 首页
│   │   │   ├── DetectImage.vue # 图片检测
│   │   │   ├── DetectVideo.vue # 视频检测
│   │   │   ├── DetectRealtime.vue # 实时检测
│   │   │   ├── ModelManager.vue  # 模型管理
│   │   │   ├── ModelInfo.vue     # 模型详情
│   │   │   ├── DatasetManager.vue # 数据集管理
│   │   │   ├── UserManager.vue    # 用户管理
│   │   │   └── Console.vue        # 数据统计
│   │   ├── App.vue         # 根组件
│   │   ├── main.ts         # 入口文件
│   │   └── style.css       # 全局样式
│   ├── package.json
│   ├── vite.config.ts      # Vite 配置（包含 API 代理）
│   └── README.md
├── web-backend/            # 后端项目
│   ├── routes/             # 路由模块
│   │   ├── __init__.py     # 路由注册
│   │   ├── auth.py         # 认证路由
│   │   ├── detect.py       # 检测路由
│   │   ├── models.py       # 模型管理路由
│   │   ├── datasets.py     # 数据集管理路由
│   │   ├── users.py        # 用户管理路由
│   │   └── statistics.py   # 统计路由
│   ├── utils/              # 工具模块
│   │   ├── auth.py         # 认证工具（JWT）
│   │   └── detection.py    # 检测服务（YOLO）
│   ├── instance/           # 实例文件夹（Flask 约定）
│   │   └── yolo_helmet.db  # SQLite 数据库文件
│   ├── models/             # 模型文件目录
│   ├── uploads/            # 上传文件目录
│   │   ├── images/         # 上传的图片
│   │   ├── videos/         # 上传的视频
│   │   ├── results/        # 检测结果文件
│   │   └── datasets/       # 数据集文件
│   ├── models.py           # 数据库模型
│   ├── config.py           # 配置文件
│   ├── extensions.py       # Flask 扩展初始化
│   ├── app.py              # 应用入口
│   ├── init_db.py          # 数据库初始化
│   ├── requirements.txt    # 依赖列表
│   └── README.md
├── images/                 # 项目截图和示例图片
└── README.md              # 项目说明文档（本文件）
```

## 安装和运行

### 环境要求

- **Python**: 3.8+
- **Node.js**: 16+
- **npm**: 8+
- **pip**: 最新版本

### 后端安装

1. 进入后端目录：
```bash
cd web-backend
```

2. 创建虚拟环境（推荐）：
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. 安装依赖：
```bash
python3 -m pip install -r requirements.txt
```

**注意**：如果使用 `python3` 命令，请使用 `python3 -m pip install -r requirements.txt` 确保安装到正确的 Python 环境。

4. 初始化数据库：
```bash
python3 init_db.py
```

这将创建数据库表并创建默认管理员账户：
- 用户名: `admin`
- 密码: `admin123`

5. 启动后端服务：
```bash
python3 app.py
```

后端服务将在 `http://localhost:5000` 启动

### 前端安装

1. 进入前端目录：
```bash
cd web-front
```

2. 安装依赖：
```bash
npm install
```

3. 启动开发服务器：
```bash
npm run dev
```

前端应用将在 `http://localhost:5173` 启动

4. 构建生产版本：
```bash
npm run build
```

构建产物将输出到 `dist/` 目录

## API 文档

### 认证接口

#### 用户注册
- **POST** `/api/auth/register`
- **请求体**：
```json
{
  "username": "string",
  "password": "string",
  "email": "string (可选)"
}
```

#### 用户登录
- **POST** `/api/auth/login`
- **请求体**：
```json
{
  "username": "string",
  "password": "string"
}
```
- **响应**：
```json
{
  "token": "jwt_token",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin"
  }
}
```

#### 获取当前用户信息
- **GET** `/api/auth/me`
- **请求头**：`Authorization: Bearer <token>`

#### 用户登出
- **POST** `/api/auth/logout`
- **请求头**：`Authorization: Bearer <token>`

### 检测接口

#### 图片检测
- **POST** `/api/detect/image`
- **请求头**：`Authorization: Bearer <token>`
- **请求体**：`multipart/form-data`
  - `image`: 图片文件
  - `model_id`: 模型ID（可选）
- **响应**：
```json
{
  "image": "base64_encoded_image",
  "detections": [
    {
      "class": "with_helmet",
      "confidence": 0.95,
      "bbox": [100, 100, 200, 200]
    }
  ],
  "stats": {
    "total": 5,
    "with_helmet": 3,
    "without_helmet": 2
  }
}
```

#### 视频检测
- **POST** `/api/detect/video`
- **请求头**：`Authorization: Bearer <token>`
- **请求体**：`multipart/form-data`
  - `video`: 视频文件
  - `model_id`: 模型ID（可选）
- **响应**：包含检测结果视频 URL、关键帧和统计摘要

#### 实时检测
- **POST** `/api/detect/realtime/start` - 启动实时检测
- **POST** `/api/detect/realtime/stop` - 停止实时检测
- **GET** `/api/detect/realtime/frame` - 获取实时检测帧

### 模型管理接口（需要管理员权限）

- **GET** `/api/models` - 获取模型列表
- **GET** `/api/models/<id>` - 获取模型详情
- **POST** `/api/models` - 创建模型
  ```json
  {
    "name": "模型名称",
    "type": "general" 或 "custom"
  }
  ```
- **DELETE** `/api/models/<id>` - 删除模型
- **POST** `/api/models/train` - 训练模型
- **GET** `/api/models/<id>/training` - 获取训练数据（损失曲线等）
- **GET** `/api/models/<id>/metrics` - 获取模型指标（mAP、精确率、召回率、F1值）

### 数据集管理接口（需要管理员权限）

- **GET** `/api/datasets` - 获取数据集列表
- **GET** `/api/datasets/<id>` - 获取数据集详情
- **POST** `/api/datasets` - 创建数据集
  ```json
  {
    "name": "数据集名称",
    "description": "描述（可选）"
  }
  ```
- **DELETE** `/api/datasets/<id>` - 删除数据集
- **POST** `/api/datasets/<id>/upload` - 上传数据集 ZIP 文件
  - **请求体**：`multipart/form-data`
    - `zip` 或 `file`: ZIP 文件
  - **响应**：
  ```json
  {
    "message": "数据集上传成功，共 1000 张图片",
    "image_count": 1000,
    "train_count": 700,
    "val_count": 200,
    "test_count": 100,
    "file_size": 104857600,
    "status": "validated",
    "warnings": []
  }
  ```

### 用户管理接口（需要管理员权限）

- **GET** `/api/users` - 获取用户列表
- **GET** `/api/users/<id>` - 获取用户详情
- **POST** `/api/users` - 创建用户
  ```json
  {
    "username": "用户名",
    "email": "邮箱",
    "password": "密码",
    "role": "user" 或 "admin"
  }
  ```
- **PUT** `/api/users/<id>` - 更新用户
- **DELETE** `/api/users/<id>` - 删除用户

### 统计接口（需要管理员权限）

- **GET** `/api/statistics` - 获取统计数据
  - 返回：总检测次数、佩戴/未佩戴统计、检测率、每日统计
- **GET** `/api/statistics/history` - 获取检测历史
  - 查询参数：`days`（可选，默认30天）

## 使用说明

### 首次使用

1. 启动后端服务（端口 5000）
2. 启动前端服务（端口 5173）
3. 访问 `http://localhost:5173`
4. 使用默认管理员账户登录：
   - 用户名: `admin`
   - 密码: `admin123`

### 普通用户功能

1. **注册账号**：在登录页面点击"注册"创建新账号

2. **图片检测**：
   - 进入"图片检测"页面
   - 上传图片文件（JPG/PNG 格式）
   - 选择模型（可选，系统会提示未训练完成的模型）
   - 点击"开始检测"
   - 查看检测结果和统计信息

3. **视频检测**：
   - 进入"视频检测"页面
   - 上传视频文件（MP4/AVI 格式）
   - 选择模型（可选）
   - 等待处理完成
   - 查看检测结果视频和统计摘要

4. **实时检测**：
   - 进入"实时检测"页面
   - 选择模型（可选）
   - 点击"开始检测"（需要允许浏览器访问摄像头）
   - 查看实时检测结果和统计
   - 点击"停止检测"结束检测

### 管理员功能

除了普通用户功能外，管理员还可以：

1. **模型管理**：
   - 创建新模型（通用模型或自定义模型）
   - 查看模型详情和训练数据
   - 训练自定义模型（需要先上传数据集）
   - 删除模型

2. **数据集管理**：
   - 创建数据集（输入名称和描述）
   - 上传数据集 ZIP 文件（系统会自动验证格式）
   - 查看数据集详情和统计信息
   - 删除数据集

3. **用户管理**：
   - 创建用户账号
   - 编辑用户信息（邮箱、角色）
   - 删除用户

4. **数据统计**：
   - 查看系统检测统计
   - 查看趋势图表和分布图表
   - 查看历史检测记录

## 注意事项

1. **YOLO 模型**：
   - 首次运行会自动下载 YOLO11n 模型（约 6MB）
   - 模型文件保存在 `web-backend/models/` 目录
   - 类别映射需要根据实际训练模型调整
   - 未训练完成的模型在使用时会提示警告

2. **文件上传**：
   - 图片文件大小建议不超过 10MB
   - 视频文件大小建议不超过 500MB
   - 上传的文件保存在 `web-backend/uploads/` 目录
   - 数据集 ZIP 文件会自动解压并验证结构

3. **数据库**：
   - 默认使用 SQLite 数据库
   - 数据库文件位于 `instance/` 目录（Flask 约定）
   - 数据库文件：`web-backend/instance/yolo_helmet.db`（自动创建）
   - 首次运行需要执行 `init_db.py` 初始化数据库
   - 初始化时会创建默认管理员账户和通用模型

4. **实时检测**：
   - 需要浏览器支持摄像头访问
   - 建议使用 Chrome 或 Firefox 浏览器
   - HTTPS 环境下摄像头访问更稳定
   - 需要用户授权才能访问摄像头

5. **性能优化**：
   - 视频检测处理时间取决于视频长度和分辨率
   - 建议使用 GPU 加速（需要安装 CUDA 版本的 PyTorch）
   - 大文件处理可能需要较长时间
   - 数据集上传和验证可能需要一些时间

6. **安全建议**：
   - 生产环境请修改默认管理员密码
   - 修改 `config.py` 中的 `SECRET_KEY`
   - 配置 HTTPS 和防火墙规则
   - 限制文件上传大小和类型

## 故障排除

### 1. ModuleNotFoundError: No module named 'flask_cors'

**原因**：依赖包未安装或安装到了错误的 Python 环境

**解决方案**：
```bash
# 确保使用正确的 Python 环境
python3 -m pip install -r requirements.txt
```

### 2. ImportError: cannot import name 'EVENT_TYPE_CLOSED' from 'watchdog.events'

**原因**：watchdog 版本过旧（系统级安装的旧版本）

**解决方案**：
```bash
# 升级 watchdog 到用户目录
python3 -m pip install --user --upgrade watchdog>=2.0.0
```

### 3. 404 错误：路由未找到

**原因**：前端代理配置问题或后端路由未正确注册

**解决方案**：
- 检查前端 `vite.config.ts` 中的代理配置（确保 `/api` 代理到 `http://localhost:5000`）
- 确保后端路由已正确注册（检查 `routes/__init__.py`）
- 确保后端服务正在运行

### 4. 数据库初始化失败

**原因**：数据库文件权限问题或 SQLAlchemy 版本不兼容

**解决方案**：
```bash
# 删除旧数据库文件重新初始化
rm web-backend/instance/yolo_helmet.db
cd web-backend
python3 init_db.py
```

### 5. YOLO 模型下载失败

**原因**：网络问题或 Ultralytics 版本问题

**解决方案**：
- 检查网络连接
- 手动下载模型文件到 `web-backend/models/` 目录
- 或使用镜像源安装依赖

### 6. 数据集上传失败：结构不符合要求

**原因**：ZIP 文件缺少必需的目录结构

**解决方案**：
- 检查 ZIP 文件是否包含 `train/images/`、`train/labels/`、`valid/images/`、`valid/labels/` 目录
- 确保目录结构正确（参考"数据集格式要求"部分）
- 查看错误信息了解具体缺少哪些目录

### 7. 500 错误：获取数据集列表失败

**原因**：数据库表结构与模型定义不匹配

**解决方案**：
- 检查数据库表是否包含所有必需字段（`file_size`、`status`、`train_count`、`val_count`、`test_count`）
- 如果缺少字段，需要运行数据库迁移脚本或重新初始化数据库

### 8. 视频检测处理缓慢

**原因**：视频文件过大或未使用 GPU 加速

**解决方案**：
- 使用 GPU 版本的 PyTorch（需要 CUDA）
- 减小视频分辨率
- 增加服务器处理能力
- 考虑使用异步任务队列（如 Celery）

### 9. 登录后显示"操作失败"但没有具体错误信息

**原因**：前端错误处理未正确显示后端错误消息

**解决方案**：
- 检查浏览器控制台查看详细错误
- 检查后端日志查看具体错误信息
- 确保后端返回了正确的错误消息格式

### 10. 创建用户时提示"邮箱已被使用"

**原因**：数据库中已存在相同邮箱的用户

**解决方案**：
- 使用不同的邮箱地址
- 或编辑现有用户而不是创建新用户

## 性能优化建议

1. **使用 GPU 加速**：安装 CUDA 版本的 PyTorch 可大幅提升检测速度
2. **数据库优化**：生产环境建议使用 PostgreSQL 或 MySQL 替代 SQLite
3. **文件存储**：大文件建议使用对象存储服务（如 S3、OSS）
4. **缓存机制**：对频繁访问的数据添加缓存
5. **异步处理**：视频检测等耗时操作建议使用任务队列（如 Celery）
6. **CDN 加速**：前端静态资源使用 CDN 加速
7. **负载均衡**：生产环境使用负载均衡器分发请求

## 安全建议

1. **修改默认密钥**：生产环境务必修改 `config.py` 中的 `SECRET_KEY`
2. **修改默认密码**：首次登录后立即修改管理员密码
3. **使用 HTTPS**：生产环境配置 SSL/TLS 证书
4. **限制文件上传**：配置合理的文件大小和类型限制
5. **数据库安全**：使用强密码，限制数据库访问权限
6. **API 限流**：防止恶意请求，建议使用 Flask-Limiter
7. **输入验证**：对所有用户输入进行验证和清理
8. **JWT 过期时间**：设置合理的 JWT Token 过期时间

## 系统架构

### 前端架构

- **框架**：Vue 3 Composition API + TypeScript
- **状态管理**：使用 localStorage 存储用户 token 和状态
- **路由守卫**：基于 Vue Router 的导航守卫实现权限控制
- **API 通信**：Axios 封装，统一错误处理和请求拦截
- **UI 组件**：Element Plus 组件库，提供完整的 UI 解决方案
- **数据可视化**：ECharts 用于统计图表展示

### 后端架构

- **框架**：Flask RESTful API
- **数据库**：SQLAlchemy ORM + SQLite（可扩展至 PostgreSQL/MySQL）
- **认证**：JWT Token 认证机制
- **文件处理**：支持图片、视频上传和处理
- **模型服务**：基于 Ultralytics YOLO 的检测服务
- **权限控制**：基于角色的访问控制（RBAC）

### 数据流

1. **检测流程**：
   - 用户上传图片/视频 → 后端接收文件 → YOLO 模型检测 → 结果标注 → 返回前端展示
2. **数据存储**：
   - 检测记录自动保存到数据库
   - 上传文件临时存储，检测完成后清理
   - 检测结果视频保存到 `uploads/results/`
3. **模型管理**：
   - 支持通用模型（YOLO11n）和自定义训练模型
   - 模型文件存储在 `models/` 目录
   - 模型元数据和指标存储在数据库

## 开发说明

### 前端开发

- 开发服务器支持热重载
- API 代理配置在 `vite.config.ts` 中（`/api` 代理到 `http://localhost:5000`）
- 使用 TypeScript 进行类型检查
- 使用 Element Plus 组件库
- 使用 Vue Router 进行路由管理

### 后端开发

- 使用 Flask 开发模式（`debug=True`）
- 数据库迁移使用 Flask-Migrate（可选）
- API 响应格式统一为 JSON
- 使用 Blueprint 组织路由
- 使用 JWT 进行身份认证

### 数据库迁移

使用 Flask-Migrate 进行数据库迁移：

```bash
# 初始化迁移（首次）
cd web-backend
flask db init

# 创建迁移
flask db migrate -m "描述"

# 应用迁移
flask db upgrade
```

### 日志配置

可以在 `app.py` 中添加日志配置：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 使用示例

### 使用 curl 测试登录

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### 使用 curl 测试图片检测

```bash
# 先登录获取 token
TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.token')

# 上传图片进行检测
curl -X POST http://localhost:5000/api/detect/image \
  -H "Authorization: Bearer $TOKEN" \
  -F "image=@test_image.jpg"
```

### 使用 curl 测试数据集上传

```bash
# 先创建数据集
DATASET_ID=$(curl -s -X POST http://localhost:5000/api/datasets \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"测试数据集","description":"这是一个测试数据集"}' | jq -r '.id')

# 上传数据集 ZIP 文件
curl -X POST http://localhost:5000/api/datasets/$DATASET_ID/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "zip=@dataset.zip"
```

## 许可证

本项目仅供学习和研究使用。

## 贡献

欢迎提交 Issue 和 Pull Request。

## 更新日志

### 最新更新

- ✅ 支持数据集 ZIP 文件上传
- ✅ 数据集格式自动验证
- ✅ 数据集统计信息显示（训练集、验证集、测试集数量）
- ✅ 模型训练状态验证（未训练模型使用提示）
- ✅ 改进的错误提示信息（中文）
- ✅ 数据集详情查看功能
- ✅ 侧边栏折叠/展开功能
- ✅ 全屏显示优化

## 更新日志

### v1.0.0
- 初始版本发布
- 支持图片、视频、实时检测
- 完整的用户管理和权限控制
- 模型和数据集管理功能
- 数据统计分析功能

欢迎提交 Issue 和 Pull Request。在提交 PR 前，请确保：
1. 代码符合项目规范
2. 已通过测试
3. 更新了相关文档
