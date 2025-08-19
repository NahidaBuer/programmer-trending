# 程序员热榜聚合工具

一个面向程序员的热榜聚合工具，支持多平台数据抓取、AI 内容分析和智能摘要生成。

## 技术栈

- **前端**: React 19 + TypeScript + Vite + Tailwind CSS
- **后端**: FastAPI + Python 3.13 + SQLAlchemy + APScheduler
- **AI**: DeepSeek API
- **数据库**: PostgreSQL (生产) / SQLite (开发)
- **部署**: Docker + Docker Compose

## 数据源

MVP 版本先做：

- Hacker News

后续考虑追加：

- GitHub Trending
- 掘金
- V2EX
- Linux DO
- NodeSeek

## 快速开始

### 环境要求

- Python 3.13+
- Node.js 18+
- uv (Python 包管理器)
- pnpm

### 安装依赖

```bash
# 后端
cd backend
uv sync

# 前端
cd frontend
pnpm install
```

### 配置环境变量

```bash
# 后端配置
cp backend/.env.example backend/.env
# 编辑 backend/.env 填入真实配置

# 前端配置
cp frontend/.env.example frontend/.env
# 编辑 frontend/.env 填入真实配置
```

### 运行开发服务器

```bash
# 后端 (端口 8000)
cd backend
uv run uvicorn main:app --reload

# 前端 (端口 5173)
cd frontend
npm run dev
```

### Docker 部署

```bash
# 构建并启动所有服务
docker-compose up --build

# 后台运行
docker-compose up -d
```

## 项目结构

```
chat-demo/
├── frontend/                 # React 前端
│   ├── src/
│   │   ├── components/      # 可复用组件
│   │   ├── pages/          # 页面组件
│   │   ├── api/            # API 调用封装
│   │   ├── types/          # TypeScript 类型定义
│   │   └── utils/          # 工具函数
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── api/            # API 路由
│   │   ├── core/           # 核心配置
│   │   ├── models/         # SQLAlchemy 模型
│   │   ├── schemas/        # Pydantic 模式
│   │   ├── services/       # 业务逻辑
│   │   ├── tasks/          # APScheduler 任务
│   │   ├── crawlers/       # 爬虫模块
│   │   └── utils/          # 工具函数
└── .cursor/rules/           # Cursor AI 开发规则
```

## 开发指南

详细的开发规范和架构设计请参考 `.cursor/rules/project-config.mdc`。

## 许可证

GPL-3 License
