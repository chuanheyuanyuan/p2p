# Admin BFF · README.vibe.md

> Domain: 后台运营聚合层

## ⚡ Quickstart
1. `cd services/bff-admin && uvicorn app.main:app --reload --port 8002` 启动服务（或运行 `pytest services/bff-admin/tests/test_bff_admin.py -q` 快速验证）。
2. `pip install -r services/bff-admin/requirements.txt` 安装依赖；若使用 `task run:bff-admin` 请确保 `Taskfile` 指向 `services/bff-admin`。
3. 使用 VS Code REST Client 打开 `apps/bff-admin/sample.http`，即可在 vibe coding 中快速回放接口。

## 🔌 API 快速体验
- 默认本地地址：`http://localhost:8002`
- 推荐带上 `X-Request-Id` 方便链路追踪。
- 事件钩子：ADMIN_AUDIT_LOGGED, BACKOFFICE_ALERT。

## 🧰 文件约定
- `app/` 目录放 FastAPI 入口、路由与依赖。
- `domain/` 目录放 Pydantic/SQLModel 聚合（待创建）。
- `README.vibe.md` + `sample.http` 永远同步更新，供 vibe/LLM 获取上下文。

## 👀 观测 & 调试
- 健康检查：`GET /healthz`（所有服务需实现）。
- 指标：`/metrics` 暴露 Prometheus 采集结果。
- 日志：建议使用 `structlog` 并包含 `trace_id`、`span_id`、`principal` 字段。

> TODO: 在实现阶段记得更新本文件，确保步骤与端点和代码保持一致。
