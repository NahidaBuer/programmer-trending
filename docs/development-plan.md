# 开发计划

## 项目概述

本文档详细描述了程序员热榜聚合工具的开发计划，按线性顺序排列，每个阶段都有明确的功能点和验收标准。

## 开发阶段

### 阶段 1: 项目基础设置

#### 1.1 后端项目初始化

#### 1.2 前端项目初始化

#### 1.3 数据库设置

**验收标准**: 项目基础架构完整，依赖配置正确，数据库表结构创建成功。

### 阶段 2: 后端核心功能开发

**状态**: 🟡 部分完成 - FastAPI 基础架构已就绪，需要实现具体业务逻辑

#### 2.1 FastAPI 应用初始化 ✅

- [x] 创建 `main.py` FastAPI 应用入口
  - 应用生命周期管理 (startup/shutdown)
  - 数据库自动初始化
  - CORS 中间件配置
  - 请求 ID 追踪中间件
  - 全局异常处理
  - 健康检查接口 `/health`
- [x] 完善 API 路由结构 `/api/v1/`
  - sources 路由 (获取数据源)
  - items 路由 (获取条目列表和详情)
  - summaries 路由 (获取 AI 摘要)
- [x] 更新数据模型和 Schema
  - 完善 `SourceResponse`, `ItemResponse`, `SummaryResponse`
  - 添加分页支持 `PaginationMeta`, `ItemListResponse`
  - 统一 API 响应格式 `APIResponse`

#### 2.2 数据抓取模块

- [x] 创建 `backend/app/crawlers/base.py` 基础爬虫类
- [x] 实现 `backend/app/crawlers/hackernews.py` Hacker News 爬虫
  - 获取 HN 首页热门文章
  - 解析文章标题、URL、分数、作者等信息
  - 支持数据去重
- [x] 创建 `backend/app/services/crawl_service.py` 抓取服务
  - 协调多个爬虫
  - 数据入库逻辑
  - 错误处理和重试机制

#### 2.3 任务调度系统

- [x] 配置 APScheduler
- [x] 创建定时抓取任务
  - 每 120 分钟抓取一次 (配置文件中设置)
  - 可配置抓取间隔
- [x] 创建 `backend/app/tasks/scheduler.py` 任务调度器
- [x] 实现任务状态监控

#### 2.4 API 路由业务逻辑实现

- [x] 完善 `GET /api/v1/sources` - 获取数据源列表
- [x] 完善 `GET /api/v1/items` - 获取热榜条目列表
  - 支持分页 (page, page_size)
  - 支持按数据源过滤 (source_id)
  - 支持按日期过滤
- [x] 完善 `GET /api/v1/items/{item_id}` - 获取单条详情
- [x] 实现 `GET /api/v1/summaries/{item_id}` - 获取文章摘要
- [x] 实现 `POST /api/v1/refresh` - 手动触发抓取

**验收标准**: API 框架搭建完成，能够正常启动和响应请求。下一步需要实现数据抓取和业务逻辑。

### 阶段 3: AI 摘要功能 (基于 Google Gemini)

#### 3.1 AI 服务集成 (使用 Google Gemini)

- [ ] 创建 `backend/app/services/ai_service.py`
  - 集成 Google Gemini API (gemini-2.5-flash)
  - 支持 URL 上下文功能 (`url_context` tool)
  - 异步调用实现
  - 错误处理、重试机制和速率限制
- [ ] 添加环境变量配置
  - `GOOGLE_API_KEY`: Gemini API 密钥
  - `GEMINI_MODEL`: 默认 "gemini-2.5-flash"
  - `AI_SUMMARY_MAX_LENGTH`: 摘要字数限制 (默认 200)
  - `AI_SUMMARY_MAX_RETRIES`: 摘要生成最大重试次数 (默认 3)
- [ ] 删除之前残留的 deepseek 相关的环境变量

#### 3.2 摘要状态管理和存储

- [ ] 更新 `backend/app/models/summary.py` 数据库模型
  - 添加状态管理字段 (`status`, `retry_count`, `error_message`)
  - 支持摘要生成的完整生命周期追踪
  - 添加 Gemini 特有的元数据字段 (`generation_duration_ms`, `url_retrieval_status`)
  - 添加一个存储 json 的字段 `response_json` 用于 api 原始响应内容
- [ ] 创建数据库迁移文件同步模型变更
- [ ] 创建 `backend/app/tasks/summary_generator.py` 异步摘要生成任务
  - 定期查找需要生成摘要的条目
  - 使用 Gemini URL 上下文功能直接处理 HN 链接
  - 并发控制和失败降级策略
  - 集成到现有的 APScheduler 中
- [ ] 完善 `GET /api/v1/summaries/{item_id}` - 获取文章摘要
- [ ] 实现摘要生成状态查询和手动触发接口

#### 3.3 AI 对话代理 (基于 Gemini)

- [ ] 实现 `POST /api/v1/chat` - AI 对话接口
  - 使用 Gemini API 作为对话后端
  - 支持上下文管理 (可选携带 HN 文章链接)
  - 输入验证和内容安全过滤
  - 支持流式和非流式响应
- [ ] 支持基于 HN 文章的增强对话
  - 用户可以针对特定文章进行深入讨论
  - 利用 Gemini 的 URL 上下文能力提供准确回答
  - 集成项目内的文章摘要作为补充上下文

#### 3.4 优化和监控

- [ ] 实现 API 调用统计和成本追踪
- [ ] 智能缓存策略 (避免重复处理相同 URL)
- [ ] 请求去重和批量处理
- [ ] 摘要质量评估和异常处理机制

**验收标准**: AI 摘要功能正常工作，能够直接处理 HN 链接生成高质量中文摘要；对话代理接口完整可用，支持基于文章内容的深入讨论。

**技术优势**:

- 🔧 利用 Gemini URL 上下文功能，无需复杂网页爬取
- 💰 使用 Gemini 免费额度，成本可控
- 🌐 统一技术栈，摘要和对话都基于 Gemini
- 📈 支持降级策略，URL 无法访问时基于 HN 内容生成摘要

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

#### 4.3 数据源切换

- [ ] Tab 栏切换不同数据源
- [ ] 创建 `frontend/src/components/SourceTabs.tsx`
- [ ] 处理数据源切换逻辑

**验收标准**: 前端界面美观且功能完整，用户可以正常浏览热榜和查看详情。

### 阶段 5: 其他功能开发

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

- [ ] 实现按日期范围过滤
- [ ] 添加排序功能

**验收标准**: 讨论清单和对话功能完整可用，搜索过滤功能正常。

### 阶段 6: 优化和部署

#### 6.1 Docker 化部署

- [ ] 创建 `backend/Dockerfile`
- [ ] 创建 `frontend/Dockerfile`
- [ ] 完善 `docker-compose.yml`
  - 后端服务
  - 前端服务
  - PostgreSQL 数据库
  - 环境变量配置
- [ ] 编写部署文档

**验收标准**: 项目性能优化完成，可以正常部署运行。

## 里程碑检查点

### 里程碑 0: 基础框架 ✅ (2025-08-19 完成)

- [x] 项目结构初始化
- [x] FastAPI 应用搭建
- [x] 数据库连接配置
- [x] API 路由架构
- [x] 基础中间件 (CORS, 请求 ID, 异常处理)
- [x] 健康检查接口

### 里程碑 1: MVP 版本 (阶段 1-3) 🎯 目标

- [x] 基础架构完整
- [x] HN 数据抓取功能
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

## 批判性审查总结

### 计划完成情况

**✅ 已完成**:

- 阶段 1: 项目基础设置 (100%)
- 阶段 2.1: FastAPI 应用初始化 (100%)
- 阶段 2: 后端核心功能 (约 25% 完成)

**🟡 进行中**:

- 阶段 3: AI 摘要功能

**📅 待开始**:

- 阶段 4-6: 前端、其他功能、部署

### 发现的计划问题与改进

#### **缺少类型安全检查**

- **建议**: 应在每个阶段完成后运行类型检查 (`mypy --strict`)
- **现状**: 当前有一些类型标注不完整的警告

### 新发现的技术债务

1. **类型标注**: `main.py` 中间件函数需要完善类型注解
2. **模型同步**: 数据库模型可能需要新的迁移文件
3. **环境配置**: 缺少生产环境的配置示例

## 风险评估

### 技术风险

- AI API 调用成本控制
- 数据抓取的稳定性和反爬虫应对
- 数据库性能优化
- **新增**: 类型安全性 - 当前存在类型标注不完整的问题

### 时间风险

- AI 集成可能需要额外调试时间
- 前端 UI/UX 可能需要多次迭代
- Docker 部署环境配置
- **新增**: 数据库迁移可能需要重新生成

### 缓解措施

- 设置 AI API 调用频率限制
- 实现完善的错误处理和重试机制
- 使用现有的成熟组件库
- **新增**: 每个阶段完成后运行 `mypy --strict` 检查
- **新增**: 定期运行数据库迁移检查

## 备注

- 每个功能点完成后需要进行测试验证
- 保持代码风格一致性
- 及时更新相关文档
- 定期进行代码审查
