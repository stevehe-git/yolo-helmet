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

- **Python 3**：主要编程语言
- **Flask 2.3.3**：Web 应用框架
- **Flask-CORS 4.0.0**：跨域资源共享支持
- **Flask-SQLAlchemy**：ORM 数据库操作
- **Flask-Migrate**：数据库迁移工具
- **Ultralytics 8.0.200**：YOLO 模型库（基于 YOLO11n 实现安全帽检测）
- **PyTorch 2.0+**：深度学习框架
- **Pillow 10.0.1**：图像处理库（图片预处理、格式转换）
- **OpenCV**：计算机视觉库
- **PyJWT**：JWT 认证
- **SQLite**：轻量级数据库

## 功能模块

### 用户管理

- **用户登录**：支持用户名密码登录，JWT Token 认证
- **用户注册**：新用户可注册账号，支持邮箱验证
- **账户验证**：确保系统安全性（仅授权用户可使用检测功能）
- **角色管理**：支持管理员和普通用户两种角色

### 安全帽检测

- **图片检测**：
  - 支持本地施工场景图片上传（JPG/PNG 格式）
  - 基于 YOLO11n 模型进行施工员安全帽佩戴状态检测
  - 分类：佩戴安全帽、未佩戴安全帽
  - 结果展示：显示检测结果及置信度，支持单张图片多目标检测结果标注
  - 展示 Top3 预测结果（针对疑似目标）

- **视频检测**：
  - 支持视频文件上传（MP4/AVI 格式）
  - 批量处理视频帧，生成检测结果视频
  - 提供检测摘要统计和关键帧展示

- **实时检测**：
  - 基于摄像头进行实时安全帽检测
  - 实时显示检测统计和检测历史

- **多模型支持**：提供已训练通用安全帽检测模型和定制化训练模型两种选择

### 模型管理（管理员功能）

- **模型列表**：查看所有可用模型
- **模型创建**：创建新的通用或定制模型
- **模型删除**：删除不需要的模型
- **模型详情**：
  - 查看模型基本信息
  - 查看性能指标（mAP、精确率、召回率、F1 值）
  - 查看训练数据（损失曲线、性能指标曲线）

### 数据集管理（管理员功能）

- **数据集列表**：查看所有数据集
- **数据集创建**：创建新的数据集
- **数据上传**：批量上传训练图片
- **数据集删除**：删除不需要的数据集

### 用户管理（管理员功能）

- **用户列表**：查看所有系统用户
- **用户创建**：创建新用户账号
- **用户编辑**：修改用户信息（邮箱、角色）
- **用户删除**：删除用户账号

### 数据统计（管理员功能）

- **检测统计**：总检测次数、佩戴/未佩戴统计、检测率
- **趋势分析**：检测趋势图表（折线图）
- **分布统计**：检测结果分布（饼图）
- **每日统计**：每日检测数量统计（柱状图）

### 模型数据查看

- **训练数据展示**：查看模型训练过程中的损失曲线、迭代次数等核心数据和指标
- **验证结果展示**：查看模型在测试集上的漏检率、误检率、精准率等性能表现
- **精度统计**：展示模型检测精度（mAP）、召回率、F1 值等关键指标

## 项目结构

```
yolo-helmet/
├── web-front/              # 前端项目
│   ├── src/
│   │   ├── api/            # API 接口定义
│   │   ├── components/     # 组件
│   │   ├── layouts/        # 布局组件
│   │   ├── router/         # 路由配置
│   │   ├── views/          # 页面视图
│   │   ├── App.vue         # 根组件
│   │   └── main.ts         # 入口文件
│   ├── package.json
│   └── vite.config.ts
├── web-backend/            # 后端项目
│   ├── routes/             # 路由模块
│   │   ├── auth.py         # 认证路由
│   │   ├── detect.py       # 检测路由
│   │   ├── models.py       # 模型管理路由
│   │   ├── datasets.py     # 数据集管理路由
│   │   ├── users.py        # 用户管理路由
│   │   └── statistics.py   # 统计路由
│   ├── utils/              # 工具模块
│   │   ├── auth.py         # 认证工具
│   │   └── detection.py    # 检测服务
│   ├── models.py           # 数据库模型
│   ├── config.py           # 配置文件
│   ├── app.py              # 应用入口
│   ├── init_db.py          # 数据库初始化
│   └── requirements.txt    # 依赖列表
├── images/                 # 项目截图和示例图片
└── README.md              # 项目说明文档
```

## 安装和运行

### 环境要求

- **Python**: 3.8+
- **Node.js**: 16+
- **npm**: 8+

### 后端安装

1. 进入后端目录：
```bash
cd web-backend
```

2. 创建虚拟环境（推荐）：
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 初始化数据库：
```bash
python init_db.py
```

这将创建数据库表并创建默认管理员账户：
- 用户名: `admin`
- 密码: `admin123`

5. 启动后端服务：
```bash
python app.py
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

## API 文档

### 认证接口

- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户登出
- `GET /api/auth/me` - 获取当前用户信息

### 检测接口

- `POST /api/detect/image` - 图片检测
  - 请求：`multipart/form-data`，包含 `image` 文件和可选的 `model_id`
  - 响应：检测结果（标注后的图片、检测框、统计信息）

- `POST /api/detect/video` - 视频检测
  - 请求：`multipart/form-data`，包含 `video` 文件和可选的 `model_id`
  - 响应：检测结果视频 URL、关键帧结果、统计摘要

- `POST /api/detect/realtime/start` - 启动实时检测
- `POST /api/detect/realtime/stop` - 停止实时检测
- `GET /api/detect/realtime/frame` - 获取实时检测帧

### 模型管理接口（需要管理员权限）

- `GET /api/models` - 获取模型列表
- `GET /api/models/<id>` - 获取模型详情
- `POST /api/models` - 创建模型
- `DELETE /api/models/<id>` - 删除模型
- `POST /api/models/train` - 训练模型
- `GET /api/models/<id>/training` - 获取训练数据
- `GET /api/models/<id>/metrics` - 获取模型指标

### 数据集管理接口（需要管理员权限）

- `GET /api/datasets` - 获取数据集列表
- `GET /api/datasets/<id>` - 获取数据集详情
- `POST /api/datasets` - 创建数据集
- `DELETE /api/datasets/<id>` - 删除数据集
- `POST /api/datasets/<id>/upload` - 上传数据集图片

### 用户管理接口（需要管理员权限）

- `GET /api/users` - 获取用户列表
- `GET /api/users/<id>` - 获取用户详情
- `POST /api/users` - 创建用户
- `PUT /api/users/<id>` - 更新用户
- `DELETE /api/users/<id>` - 删除用户

### 统计接口（需要管理员权限）

- `GET /api/statistics` - 获取统计数据
- `GET /api/statistics/history` - 获取检测历史

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
   - 上传图片文件
   - 选择模型（可选）
   - 点击"开始检测"
   - 查看检测结果和统计信息
3. **视频检测**：
   - 进入"视频检测"页面
   - 上传视频文件
   - 等待处理完成
   - 查看检测结果视频和统计摘要
4. **实时检测**：
   - 进入"实时检测"页面
   - 点击"开始检测"（需要允许浏览器访问摄像头）
   - 查看实时检测结果和统计

### 管理员功能

除了普通用户功能外，管理员还可以：

1. **模型管理**：
   - 创建新模型
   - 查看模型详情和训练数据
   - 删除模型
2. **数据集管理**：
   - 创建数据集
   - 上传训练图片
   - 删除数据集
3. **用户管理**：
   - 创建用户账号
   - 编辑用户信息
   - 删除用户
4. **数据统计**：
   - 查看系统检测统计
   - 查看趋势图表和分布图表

## 注意事项

1. **YOLO 模型**：
   - 首次运行会自动下载 YOLO11n 模型（约 6MB）
   - 模型文件保存在 `web-backend/models/` 目录
   - 类别映射需要根据实际训练模型调整

2. **文件上传**：
   - 图片文件大小建议不超过 10MB
   - 视频文件大小建议不超过 500MB
   - 上传的文件保存在 `web-backend/uploads/` 目录

3. **数据库**：
   - 默认使用 SQLite 数据库
   - 数据库文件：`web-backend/yolo_helmet.db`
   - 首次运行需要执行 `init_db.py` 初始化数据库

4. **实时检测**：
   - 需要浏览器支持摄像头访问
   - 建议使用 Chrome 或 Firefox 浏览器
   - HTTPS 环境下摄像头访问更稳定

5. **性能优化**：
   - 视频检测处理时间取决于视频长度和分辨率
   - 建议使用 GPU 加速（需要安装 CUDA 版本的 PyTorch）
   - 大文件处理可能需要较长时间

6. **安全建议**：
   - 生产环境请修改默认管理员密码
   - 修改 `config.py` 中的 `SECRET_KEY`
   - 配置 HTTPS 和防火墙规则

## 开发说明

### 前端开发

- 开发服务器支持热重载
- API 代理配置在 `vite.config.ts` 中
- 使用 TypeScript 进行类型检查

### 后端开发

- 使用 Flask 开发模式（`debug=True`）
- 数据库迁移使用 Flask-Migrate
- API 响应格式统一为 JSON

## 许可证

本项目仅供学习和研究使用。

## 贡献

欢迎提交 Issue 和 Pull Request。
