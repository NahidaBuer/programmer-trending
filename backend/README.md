# Programmer Trending Backend

基于 FastAPI + Python 3.13 的程序员热榜后端服务。

## 功能特性

- 抓取多个技术社区的热门内容（Hacker News 等）
- 使用 Google Gemini API 生成 AI 摘要和翻译标题
- 定时任务自动抓取和生成摘要
- RESTful API 提供数据查询和聊天功能
- 支持分页、筛选和排序

## 快速开始

### 本地开发

```bash
# 安装依赖
uv sync

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 GOOGLE_API_KEY

# 运行数据库迁移
uv run alembic upgrade head

# 启动开发服务器
uv run uvicorn main:app --reload
```

### Docker 部署

#### 1. 使用 Docker Compose（推荐）

```bash
# 克隆项目
git clone <repository>
cd programmer-trending/backend

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，至少需要设置 GOOGLE_API_KEY

# 构建并启动
docker-compose up --build

# 后台运行
docker-compose up -d
```

#### 2. 手动 Docker 部署

```bash
# 构建镜像
docker build -t programmer-trending-backend .

# 创建数据目录
mkdir -p ./data ./logs

# 运行容器
docker run -d \
  --name programmer-trending \
  -p 8000:8000 \
  -e GOOGLE_API_KEY=your_api_key_here \
  -e DATABASE_URL=sqlite:///app/data/app.db \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --restart unless-stopped \
  programmer-trending-backend
```

## 重要提醒

### 数据库持久化

**⚠️ 重要**：使用 Docker 时，务必将 SQLite 数据库挂载到主机，避免容器重启时数据丢失：

```yaml
volumes:
  - ./data:/app/data # 数据库文件持久化
```

使用 SQLite 时，如果不挂载数据库，容器删除时所有数据都会丢失！

也可以使用 PostgreSQL 作为数据库，配置 `DATABASE_URL` 环境变量。

### 环境变量配置

必需的环境变量：

- `GOOGLE_API_KEY`: Google Gemini API 密钥
- `DATABASE_URL`: 数据库连接字符串（默认使用 SQLite）

可选配置：

- `CRAWL_INTERVAL_MINUTES`: 抓取间隔（默认 120 分钟）
- `SUMMARY_CONCURRENCY`: 摘要生成并发数（默认 3）
- `LOG_LEVEL`: 日志级别（默认 INFO）

## 数据库管理

### 开发环境

```bash
# 修改模型后创建迁移
uv run alembic revision --autogenerate -m "Add new field"

# 应用迁移
uv run alembic upgrade head

# 启动应用
uv run uvicorn main:app
```

### 生产部署

```bash
# 确保数据库是最新版本
uv run alembic upgrade head

# 启动应用
uv run uvicorn main:app
```

### Docker 环境

Docker 镜像启动时会自动运行数据库迁移，无需手动操作。

## API 端点

- `GET /health` - 健康检查
- `GET /api/v1/sources` - 获取数据源列表
- `GET /api/v1/items` - 获取文章列表（支持筛选、分页、排序）
- `GET /api/v1/summaries` - 获取摘要列表
- `POST /api/v1/chat` - AI 聊天对话

详细的 API 文档在应用启动后访问 http://localhost:8000/docs

## 注意事项

1. **API 密钥安全**：不要在代码中硬编码 API 密钥，使用环境变量
2. **数据备份**：定期备份 SQLite 数据库文件
3. **资源监控**：监控 API 调用频率，避免超出限额
4. **网络连接**：确保服务器能访问外部 API（Google Gemini）
