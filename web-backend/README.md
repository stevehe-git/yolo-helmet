# YOLO 安全帽检测系统 - 后端

基于 Flask 和 YOLO11n 的施工安全帽检测后端服务。

## 技术栈

- **Python 3.8+**：主要编程语言
- **Flask 2.3.3**：Web 应用框架
- **Flask-CORS 4.0.0**：跨域资源共享支持
- **Flask-SQLAlchemy 3.0.5**：ORM 数据库操作
- **Flask-Migrate 4.0.5**：数据库迁移工具
- **Ultralytics 8.0.200**：YOLO 模型库（基于 YOLO11n 实现安全帽检测）
- **PyTorch 2.0+**：深度学习框架
- **Pillow 10.0.1**：图像处理库
- **OpenCV**：计算机视觉库
- **PyJWT**：JWT 认证
- **SQLAlchemy 2.0+**：数据库 ORM
- **Watchdog 2.0+**：文件监控（Flask 调试模式需要）

## 环境要求

- Python 3.8 或更高版本
- pip 包管理器
- 建议使用虚拟环境（venv）

## 安装步骤

### 1. 创建虚拟环境（推荐）

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

**注意**：如果使用 `python3` 命令，请使用 `python3 -m pip install -r requirements.txt` 确保安装到正确的 Python 环境。

### 3. 初始化数据库

```bash
python3 init_db.py
```

这将：
- 创建数据库表
- 创建默认管理员账户（用户名：`admin`，密码：`admin123`）
- 创建默认通用模型

### 4. 运行应用

```bash
python3 app.py
```

服务器将在 `http://localhost:5000` 启动

## 项目结构

```
web-backend/
├── app.py                 # 应用入口文件
├── config.py              # 配置文件
├── models.py              # 数据库模型
├── extensions.py          # Flask 扩展初始化
├── init_db.py             # 数据库初始化脚本
├── requirements.txt       # 依赖列表
├── routes/                # 路由模块
│   ├── __init__.py        # 路由注册
│   ├── auth.py            # 认证路由
│   ├── detect.py          # 检测路由
│   ├── models.py          # 模型管理路由
│   ├── datasets.py        # 数据集管理路由
│   ├── users.py           # 用户管理路由
│   └── statistics.py     # 统计路由
└── utils/                 # 工具模块
    ├── auth.py            # 认证工具（JWT）
    └── detection.py       # 检测服务（YOLO）
```

## 配置说明

配置文件：`config.py`

主要配置项：
- `SECRET_KEY`：JWT 密钥（生产环境请修改）
- `SQLALCHEMY_DATABASE_URI`：数据库连接字符串（默认 SQLite）
- `UPLOAD_FOLDER`：文件上传目录
- `MODELS_FOLDER`：模型文件目录
- `DEFAULT_MODEL`：默认模型文件名
- `CONFIDENCE_THRESHOLD`：检测置信度阈值（默认 0.25）
- `IOU_THRESHOLD`：IoU 阈值（默认 0.45）

## API 端点

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
- **POST** `/api/datasets/<id>/upload` - 上传数据集图片（支持批量上传）

### 用户管理接口（需要管理员权限）

- **GET** `/api/users` - 获取用户列表
- **GET** `/api/users/<id>` - 获取用户详情
- **POST** `/api/users` - 创建用户
- **PUT** `/api/users/<id>` - 更新用户
- **DELETE** `/api/users/<id>` - 删除用户

### 统计接口（需要管理员权限）

- **GET** `/api/statistics` - 获取统计数据
  - 返回：总检测次数、佩戴/未佩戴统计、检测率、每日统计
- **GET** `/api/statistics/history` - 获取检测历史
  - 查询参数：`days`（可选，默认30天）

## 默认账户

初始化数据库后会自动创建以下管理员账户：

- **用户名**: `admin`
- **密码**: `admin123`

**重要**：生产环境请务必修改默认密码！

## 文件目录

- `uploads/` - 上传的文件（图片、视频）
  - `uploads/images/` - 上传的图片
  - `uploads/videos/` - 上传的视频
  - `uploads/results/` - 检测结果文件
  - `uploads/datasets/` - 数据集文件
- `models/` - 模型文件目录
- `yolo_helmet.db` - SQLite 数据库文件

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

## 故障排除

### 1. ModuleNotFoundError: No module named 'flask_cors'

**原因**：依赖包未安装或安装到了错误的 Python 环境

**解决方案**：
```bash
# 确保使用正确的 Python 环境
python3 -m pip install -r requirements.txt
```

### 2. ImportError: cannot import name 'EVENT_TYPE_CLOSED' from 'watchdog.events'

**原因**：watchdog 版本过旧

**解决方案**：
```bash
python3 -m pip install --upgrade watchdog
```

### 3. 404 错误：路由未找到

**原因**：前端代理配置问题或后端路由未正确注册

**解决方案**：
- 检查前端 `vite.config.ts` 中的代理配置
- 确保后端路由已正确注册（检查 `routes/__init__.py`）

### 4. 数据库初始化失败

**原因**：数据库文件权限问题或 SQLAlchemy 版本不兼容

**解决方案**：
```bash
# 删除旧数据库文件重新初始化
rm yolo_helmet.db
python3 init_db.py
```

### 5. YOLO 模型下载失败

**原因**：网络问题或 Ultralytics 版本问题

**解决方案**：
- 检查网络连接
- 手动下载模型文件到 `models/` 目录
- 或使用镜像源安装依赖

### 6. 视频检测处理缓慢

**原因**：视频文件过大或未使用 GPU 加速

**解决方案**：
- 使用 GPU 版本的 PyTorch（需要 CUDA）
- 减小视频分辨率
- 增加服务器处理能力

## 性能优化建议

1. **使用 GPU 加速**：安装 CUDA 版本的 PyTorch 可大幅提升检测速度
2. **数据库优化**：生产环境建议使用 PostgreSQL 或 MySQL 替代 SQLite
3. **文件存储**：大文件建议使用对象存储服务（如 S3、OSS）
4. **缓存机制**：对频繁访问的数据添加缓存
5. **异步处理**：视频检测等耗时操作建议使用任务队列（如 Celery）

## 安全建议

1. **修改默认密钥**：生产环境务必修改 `config.py` 中的 `SECRET_KEY`
2. **修改默认密码**：首次登录后立即修改管理员密码
3. **使用 HTTPS**：生产环境配置 SSL/TLS 证书
4. **限制文件上传**：配置合理的文件大小和类型限制
5. **数据库安全**：使用强密码，限制数据库访问权限
6. **API 限流**：防止恶意请求，建议使用 Flask-Limiter

## 开发说明

### 调试模式

开发模式下，Flask 会自动重载代码更改。确保已安装 `watchdog>=2.0.0`。

### 数据库迁移

使用 Flask-Migrate 进行数据库迁移：

```bash
# 初始化迁移（首次）
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

## 许可证

本项目仅供学习和研究使用。
