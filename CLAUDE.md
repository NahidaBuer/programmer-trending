# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个程序员热榜聚合工具，用于抓取多个技术社区的热门内容，并通过 AI 生成摘要。项目采用前后端分离架构，后端使用 FastAPI，前端使用 React + TypeScript。

## 常用开发命令

### 后端 (FastAPI + Python)

```bash
cd backend

# 安装依赖
uv sync

# 启动开发服务器 (端口 8000)
uv run uvicorn main:app --reload

# 类型检查
mypy --strict

# 代码格式化 (如果使用 ruff)
ruff check .
ruff format .
```

### 前端 (React + TypeScript)

```bash
cd frontend

# 安装依赖
pnpm install

# 启动开发服务器 (端口 5173)
pnpm run dev

# 构建
pnpm run build

# 类型检查
pnpm run type-check
```

### Docker 部署

```bash
# 构建并启动所有服务
docker-compose up --build

# 后台运行
docker-compose up -d
```

## 项目架构

### 技术栈

- **后端**: FastAPI + Python 3.13 + SQLAlchemy + APScheduler
- **前端**: React 19 + TypeScript + Vite + Tailwind CSS
- **数据库**: PostgreSQL (生产) / SQLite (开发)
- **AI**: DeepSeek API
- **包管理**: 后端用 `uv`，前端用 `pnpm`

### 目录结构

```
backend/
  app/
    api/           # API 路由 (版本化 /api/v1)
    core/          # 核心配置 (环境变量、日志、依赖注入)
    models/        # SQLAlchemy 数据模型
    schemas/       # Pydantic 数据模式
    services/      # 业务逻辑 (抓取、AI 调用)
    tasks/         # APScheduler 定时任务
    crawlers/      # 各数据源爬虫 (Hacker News 等)
    utils/         # 公共工具函数
  migrations/      # Alembic 数据库迁移脚本

frontend/
  src/
    api/           # API 封装
    components/    # React 组件
    pages/         # 页面组件
    types/         # TypeScript 类型定义
    utils/         # 工具函数
```

## 开发约定

### Python 代码规范

- 全量类型注解，`mypy --strict` 必须通过
- 使用 `async/await` 异步编程
- HTTP 客户端使用 `httpx`
- 业务逻辑放在 `services/` 目录，路由层保持简洁

### TypeScript 代码规范

- 启用严格模式
- 组件尽量无状态，副作用集中在页面层
- 类型定义与后端 Pydantic 模式对齐

### API 设计

- 路径前缀: `/api/v1`
- 统一返回格式: `{ data: ..., error: null, meta: { requestId: "..." } }`
- 分页参数: `page` (默认 1), `page_size` (默认 20，最大 100)
- 时间格式: ISO8601 UTC

### 环境变量

后端通过 `backend/.env` 文件配置：

- `DATABASE_URL`: 数据库连接字符串
- `DEEPSEEK_API_KEY`: AI API 密钥
- `CRAWL_INTERVAL_MINUTES`: 抓取间隔 (默认 120)
- `SUMMARY_CONCURRENCY`: 摘要生成并发度

前端通过 `frontend/.env` 配置。

## 核心功能模块

### 数据抓取

- 使用 APScheduler 定时抓取 Hacker News 等数据源
- 爬虫模块在 `backend/app/crawlers/` 目录
- 支持并发控制和失败重试

### AI 摘要生成

- 集成 DeepSeek API 生成内容摘要
- 异步任务处理，支持并发度控制
- 摘要结果存储在数据库中

### 前端功能

- 热榜列表展示
- AI 摘要查看
- 讨论清单功能 (localStorage 存储)
- LLM 对话代理 (通过后端调用 AI API)

## 数据库设计

主要表结构：

- `sources`: 数据源配置
- `items`: 热榜条目
- `summaries`: AI 摘要结果

## 重要文件

- `.cursor/rules/project-config.mdc`: 详细的项目开发规则和架构设计
- `backend/pyproject.toml`: Python 项目配置
- `backend/main.py`: 后端入口文件 (当前为占位符)

## 开发状态

项目处于初始化阶段，主要文件结构已建立，但具体实现代码需要根据项目配置规则进行开发。
