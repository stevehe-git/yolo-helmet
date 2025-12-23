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
├── web-front/                      # 前端项目（Vue 3 + TypeScript）
│   ├── src/
│   │   ├── api/                    # API 接口定义
│   │   │   ├── auth.ts            # 认证接口
│   │   │   ├── detect.ts          # 检测接口
│   │   │   ├── model.ts           # 模型管理接口
│   │   │   ├── dataset.ts         # 数据集管理接口
│   │   │   ├── user.ts            # 用户管理接口
│   │   │   ├── statistics.ts      # 统计接口
│   │   │   └── index.ts           # API 配置
│   │   ├── components/            # 可复用组件
│   │   ├── layouts/               # 布局组件
│   │   │   └── MainLayout.vue     # 主布局
│   │   ├── router/                # 路由配置
│   │   │   └── index.ts           # 路由定义
│   │   ├── views/                 # 页面视图
│   │   │   ├── Login.vue          # 登录页
│   │   │   ├── Register.vue       # 注册页
│   │   │   ├── Home.vue           # 首页
│   │   │   ├── DetectImage.vue    # 图片检测页
│   │   │   ├── DetectVideo.vue    # 视频检测页
│   │   │   ├── DetectRealtime.vue # 实时检测页
│   │   │   ├── ModelManager.vue   # 模型管理页
│   │   │   ├── ModelInfo.vue      # 模型详情页
│   │   │   ├── DatasetManager.vue # 数据集管理页
│   │   │   ├── UserManager.vue    # 用户管理页
│   │   │   └── Console.vue        # 控制台统计页
│   │   ├── App.vue                # 根组件
│   │   └── main.ts                # 入口文件
│   ├── public/                    # 静态资源
│   ├── package.json               # 依赖配置
│   ├── vite.config.ts             # Vite 配置
│   └── tsconfig.json              # TypeScript 配置
├── web-backend/                   # 后端项目（Flask + Python）
│   ├── routes/                    # 路由模块
│   │   ├── __init__.py           # 路由注册
│   │   ├── auth.py               # 认证路由（登录、注册）
│   │   ├── detect.py             # 检测路由（图片、视频、实时）
│   │   ├── models.py             # 模型管理路由
│   │   ├── datasets.py           # 数据集管理路由
│   │   ├── users.py              # 用户管理路由
│   │   └── statistics.py         # 统计路由
│   ├── utils/                     # 工具模块
│   │   ├── auth.py               # 认证工具（JWT）
│   │   └── detection.py          # 检测服务（YOLO）
│   ├── instance/                  # 实例文件夹（自动创建）
│   │   └── yolo_helmet.db        # SQLite 数据库文件
│   ├── uploads/                   # 上传文件目录（自动创建）
│   │   ├── images/               # 上传的图片
│   │   ├── videos/                # 上传的视频
│   │   ├── results/               # 检测结果文件
│   │   └── datasets/              # 数据集文件
│   ├── models/                    # 模型文件目录（自动创建）
│   ├── models.py                  # 数据库模型（User, Model, Dataset, Detection）
│   ├── config.py                  # 配置文件
│   ├── extensions.py              # Flask 扩展初始化
│   ├── app.py                     # 应用入口
│   ├── init_db.py                 # 数据库初始化脚本
│   ├── requirements.txt           # Python 依赖列表
│   └── README.md                  # 后端说明文档
├── images/                        # 项目截图和示例图片
└── README.md                      # 项目说明文档（本文件）
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
   - 数据库文件：`web-backend/instance/yolo_helmet.db`（自动创建）
   - 首次运行需要执行 `init_db.py` 初始化数据库
   - 初始化时会创建默认管理员账户和通用模型

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

- 开发服务器支持热重载（HMR）
- API 代理配置在 `vite.config.ts` 中，默认代理到 `http://localhost:5000`
- 使用 TypeScript 进行类型检查
- 组件采用 Composition API 风格
- 路由配置在 `src/router/index.ts`

### 后端开发

- 使用 Flask 开发模式（`debug=True`）
- 数据库迁移使用 Flask-Migrate（可选）
- API 响应格式统一为 JSON
- 错误处理统一返回错误消息
- 文件上传使用 Werkzeug 的 `secure_filename` 确保安全

### 数据库模型

- **User**：用户表（用户名、邮箱、密码哈希、角色）
- **Model**：模型表（名称、类型、路径、指标）
- **Dataset**：数据集表（名称、描述、图片数量、状态）
- **Detection**：检测记录表（用户ID、模型ID、检测类型、统计信息）

## 项目截图

项目包含丰富的界面截图，位于 `images/` 目录，包括：

- 登录/注册界面
- 首页（管理员/普通用户）
- 图片检测页面
- 视频检测页面
- 实时检测页面
- 模型管理页面
- 数据集管理页面
- 用户管理页面
- 控制台统计页面
- 软件架构图
- 技术栈图

## 常见问题

### Q: 如何修改默认端口？

**A:** 
- 后端：修改 `web-backend/app.py` 中的 `port=5000`
- 前端：修改 `web-front/vite.config.ts` 中的 `server.port`

### Q: 如何配置 GPU 加速？

**A:** 
1. 安装 CUDA 版本的 PyTorch：
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```
2. 确保系统已安装 CUDA 驱动
3. 检测服务会自动使用 GPU（如果可用）

### Q: 如何添加新的检测类别？

**A:** 
1. 训练包含新类别的 YOLO 模型
2. 修改 `web-backend/utils/detection.py` 中的 `class_names` 字典
3. 上传新模型到系统

### Q: 数据库迁移后如何恢复？

**A:** 
```bash
cd web-backend
rm instance/yolo_helmet.db
python init_db.py
```

### Q: 如何部署到生产环境？

**A:** 
1. 使用 Gunicorn 或 uWSGI 运行 Flask 应用
2. 使用 Nginx 作为反向代理
3. 前端构建后部署静态文件
4. 配置 HTTPS 和 SSL 证书
5. 修改 `SECRET_KEY` 和默认密码
6. 使用 PostgreSQL 或 MySQL 替代 SQLite

## 许可证

本项目仅供学习和研究使用。

## 贡献

欢迎提交 Issue 和 Pull Request。在提交 PR 前，请确保：

1. 代码符合项目规范
2. 已通过测试
3. 更新了相关文档

## 更新日志

### v1.0.0
- 初始版本发布
- 支持图片、视频、实时检测
- 完整的用户管理和权限控制
- 模型和数据集管理功能
- 数据统计分析功能
