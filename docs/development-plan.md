# 开发计划

## 项目概述

本文档详细描述了程序员热榜聚合工具的开发计划，按线性顺序排列，每个阶段都有明确的功能点和验收标准。

## 开发阶段

### 阶段 1: 项目基础设置

#### 1.1 后端项目初始化

- [x] 更新 `backend/pyproject.toml` 添加必要依赖
  - fastapi
  - uvicorn[standard]
  - sqlalchemy[asyncio]
  - alembic
  - pydantic
  - httpx
  - apscheduler
  - python-multipart
  - python-dotenv
- [x] 创建 `backend/.env.example` 文件
- [x] 创建 `backend/app/` 目录结构
- [x] 设置 `backend/app/core/config.py` 配置管理
- [x] 设置 `backend/app/core/database.py` 数据库连接
- [x] 设置 `backend/app/core/logging.py` 日志配置

#### 1.2 前端项目初始化

- [ ] 初始化 React + TypeScript + Vite 项目
- [ ] 配置 Tailwind CSS v4
- [ ] 创建 `frontend/src/` 目录结构
- [ ] 设置 TypeScript 严格模式
- [ ] 配置 ESLint 和 Prettier
- [ ] 创建 `frontend/.env.example` 文件

#### 1.3 数据库设置

- [ ] 创建 Alembic 迁移配置
- [ ] 设计并创建数据库表结构
  - `sources` 表
  - `items` 表
  - `summaries` 表
- [ ] 编写数据库模型 (`backend/app/models/`)
- [ ] 编写 Pydantic 模式 (`backend/app/schemas/`)

**验收标准**: 项目基础架构完整，依赖配置正确，数据库表结构创建成功。

### 阶段 2: 后端核心功能开发

#### 2.1 数据抓取模块

- [ ] 创建 `backend/app/crawlers/base.py` 基础爬虫类
- [ ] 实现 `backend/app/crawlers/hackernews.py` Hacker News 爬虫
  - 获取 HN 首页热门文章
  - 解析文章标题、URL、分数、作者等信息
  - 支持数据去重
- [ ] 创建 `backend/app/services/crawl_service.py` 抓取服务
  - 协调多个爬虫
  - 数据入库逻辑
  - 错误处理和重试机制

#### 2.2 任务调度系统

- [ ] 配置 APScheduler
- [ ] 创建定时抓取任务
  - 每 120 分钟抓取一次 HN
  - 可配置抓取间隔
- [ ] 创建 `backend/app/tasks/scheduler.py` 任务调度器
- [ ] 实现任务状态监控

#### 2.3 API 路由开发

- [ ] 创建 `backend/app/api/v1/` 目录
- [ ] 实现 `GET /api/v1/sources` - 获取数据源列表
- [ ] 实现 `GET /api/v1/items` - 获取热榜条目列表
  - 支持分页 (page, page_size)
  - 支持按数据源过滤
  - 支持按日期过滤
- [ ] 实现 `GET /api/v1/items/{item_id}` - 获取单条详情
- [ ] 实现 `POST /api/v1/refresh` - 手动触发抓取

**验收标准**: 能够正常抓取 HN 数据并存储到数据库，API 接口功能完整且正确。

### 阶段 3: AI 摘要功能

#### 3.1 AI 服务集成

- [ ] 创建 `backend/app/services/ai_service.py`
  - 集成 DeepSeek API
  - 支持异步调用
  - 错误处理和重试
- [ ] 创建摘要生成任务
  - 异步处理新抓取的文章
  - 并发控制
  - 失败重试机制

#### 3.2 摘要存储和查询

- [ ] 扩展 `backend/app/models/summary.py`
- [ ] 实现 `GET /api/v1/items/{item_id}/summary` - 获取文章摘要
- [ ] 实现摘要生成的状态跟踪

#### 3.3 AI 对话代理

- [ ] 实现 `POST /api/v1/chat` - LLM 对话接口
  - 接收消息和上下文
  - 代理调用 DeepSeek API
  - 支持流式和非流式响应
- [ ] 实现输入验证和安全限制

**验收标准**: AI 摘要功能正常工作，对话代理接口完整可用。

### 阶段 4: 前端界面开发

#### 4.1 基础组件和布局

- [ ] 创建 `frontend/src/components/Layout.tsx` 基础布局
- [ ] 创建 `frontend/src/components/Header.tsx` 页面头部
- [ ] 创建 `frontend/src/components/Footer.tsx` 页面底部
- [ ] 设置响应式设计
- [ ] 配置路由系统

#### 4.2 热榜列表页面

- [ ] 创建 `frontend/src/pages/Home.tsx` 主页
- [ ] 创建 `frontend/src/components/ItemList.tsx` 文章列表组件
- [ ] 创建 `frontend/src/components/ItemCard.tsx` 文章卡片组件
- [ ] 实现数据获取和展示
- [ ] 实现分页功能
- [ ] 实现加载状态和错误处理

#### 4.3 文章详情页面

- [ ] 创建 `frontend/src/pages/ItemDetail.tsx` 文章详情页
- [ ] 展示文章基本信息
- [ ] 展示 AI 生成的摘要
- [ ] 添加返回列表功能

#### 4.4 数据源切换

- [ ] 实现 Tab 切换不同数据源
- [ ] 创建 `frontend/src/components/SourceTabs.tsx`
- [ ] 处理数据源切换逻辑

**验收标准**: 前端界面美观且功能完整，用户可以正常浏览热榜和查看详情。

### 阶段 5: 高级功能开发

#### 5.1 讨论清单功能

- [ ] 创建 `frontend/src/utils/discussionStorage.ts` localStorage 管理
- [ ] 创建 `frontend/src/components/DiscussionCartButton.tsx` 添加/移除按钮
- [ ] 创建 `frontend/src/components/DiscussionBadge.tsx` 徽标组件
- [ ] 实现讨论清单的增删改查
- [ ] 实现最多 10 条限制和去重逻辑

#### 5.2 对话页面

- [ ] 创建 `frontend/src/pages/Chat.tsx` 对话页面
  - 左侧上下文预览
  - 右侧对话框
  - 消息输入和发送
  - 对话历史展示
- [ ] 实现与后端对话 API 的集成
- [ ] 支持流式响应显示

#### 5.3 搜索和过滤功能

- [ ] 添加搜索框组件
- [ ] 实现文章标题搜索
- [ ] 实现按日期范围过滤
- [ ] 添加排序功能

**验收标准**: 讨论清单和对话功能完整可用，搜索过滤功能正常。

### 阶段 6: 优化和部署

#### 6.1 性能优化

- [ ] 实现前端数据缓存
- [ ] 优化数据库查询
- [ ] 添加分页性能优化
- [ ] 实现图片懒加载

#### 6.2 错误处理和监控

- [ ] 完善错误处理机制
- [ ] 添加请求 ID 追踪
- [ ] 实现日志记录
- [ ] 添加健康检查接口

#### 6.3 Docker 化部署

- [ ] 创建 `backend/Dockerfile`
- [ ] 创建 `frontend/Dockerfile`
- [ ] 完善 `docker-compose.yml`
  - 后端服务
  - 前端服务
  - PostgreSQL 数据库
  - 环境变量配置
- [ ] 编写部署文档

#### 6.4 测试

- [ ] 编写后端单元测试
- [ ] 编写前端组件测试
- [ ] 集成测试
- [ ] 性能测试

**验收标准**: 项目性能优化完成，可以正常部署运行，测试覆盖率达到要求。

## 里程碑检查点

### 里程碑 1: MVP 版本 (阶段 1-3)

- [ ] 基础架构完整
- [ ] HN 数据抓取功能
- [ ] AI 摘要生成
- [ ] 基础 API 接口
- [ ] 简单的前端展示

### 里程碑 2: 完整版本 (阶段 1-5)

- [ ] 完整的前后端功能
- [ ] 讨论清单功能
- [ ] AI 对话功能
- [ ] 搜索和过滤
- [ ] 良好的用户体验

### 里程碑 3: 生产版本 (阶段 1-6)

- [ ] 性能优化完成
- [ ] Docker 部署就绪
- [ ] 测试覆盖完整
- [ ] 文档齐全

## 开发优先级

1. **高优先级**: 阶段 1-2 (基础设置和数据抓取)
2. **中优先级**: 阶段 3-4 (AI 功能和前端界面)
3. **低优先级**: 阶段 5-6 (高级功能和优化)

## 风险评估

### 技术风险

- AI API 调用成本控制
- 数据抓取的稳定性和反爬虫应对
- 数据库性能优化

### 时间风险

- AI 集成可能需要额外调试时间
- 前端 UI/UX 可能需要多次迭代
- Docker 部署环境配置

### 缓解措施

- 设置 AI API 调用频率限制
- 实现完善的错误处理和重试机制
- 使用现有的成熟组件库

## 备注

- 每个功能点完成后需要进行测试验证
- 保持代码风格一致性
- 及时更新相关文档
- 定期进行代码审查
