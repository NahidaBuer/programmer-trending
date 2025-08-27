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
```

### 前端 (React + TypeScript)

```bash
cd frontend

# 安装依赖
pnpm install

# 启动开发服务器 (端口 5173)
pnpm dev

# 构建
pnpm build
```

### Docker 部署

参见 [`backend/README.md`](./backend/README.md#docker-开发--部署)。

前端建议使用 `pnpm build` 构建为静态资源后，采取任意方式分发或部署，比如 nginx 或各类静态托管服务。

## 项目架构

### 技术栈

- **后端**: FastAPI + Python 3.13 + SQLAlchemy + APScheduler
- **前端**: React 19 + TypeScript + Vite + Tailwind CSS
- **数据库**: SQLite, 可选 PostgreSQL
- **AI**: Google Gemini API
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

## 核心功能模块

### 数据抓取

- 使用 APScheduler 定时抓取 Hacker News 等数据源
- 爬虫模块在 `backend/app/crawlers/` 目录
- 支持并发控制和失败重试

### AI 摘要生成

- 集成 Google Gemini API 生成内容摘要
- 异步任务处理，支持并发度控制
- 摘要结果存储在数据库中

### 前端功能

- 热榜列表展示
- AI 摘要查看
- 讨论清单功能 (localStorage 存储)
- LLM 对话代理 (通过后端调用 Google Gemini API)

## 数据库设计

主要表结构：

- `sources`: 数据源配置
- `items`: 热榜条目
- `summaries`: AI 摘要结果
