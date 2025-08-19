# 数据库

采用 alembic 管理数据库迁移

开发环境：

```bash
# 修改模型后
uv run alembic revision --autogenerate -m "Add new field"
uv run alembic upgrade head
uv run uvicorn main:app  # 不会自动创建/修改表
```

生产部署：

```bash
# 部署时
uv run alembic upgrade head  # 确保数据库是最新版本
uv run uvicorn main:app      # 应用启动，只测试连接
```

全新环境：

```bash
# 首次部署
uv run alembic upgrade head  # 创建所有表
uv run uvicorn main:app      # 启动应用
```
