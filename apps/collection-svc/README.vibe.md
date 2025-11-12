# Collection Service · README.vibe.md

> Domain: 催收建案与工作台

## ⚡ Quickstart
1. `cd services/collection-svc && uvicorn app.main:app --reload --port 8086`（或使用 `task run:collection-svc` 结合 `COLLECTOR_POOL` 环境变量）。
2. `task lint` / `task test` — 统一代码质量与测试（基于 ruff + pytest）。
3. 使用 VS Code REST Client 打开 `sample.http`，即可在 vibe coding 中快速回放接口。

## 🔌 API 快速体验
- 默认本地地址：`http://localhost:8086`
- 推荐带上 `X-Request-Id` 方便链路追踪。
- 事件钩子：CASE_CREATED, CASE_ACTION_LOGGED, PTP_PROMISE_SET, CASE_BUCKET_SYNCED, CASE_PAYMENT_APPLIED。

## 🧰 文件约定
- `app/` 目录放 FastAPI 入口、路由与依赖。
- `domain/` 目录放 Pydantic/SQLModel 聚合（待创建）。
- `README.vibe.md` + `sample.http` 永远同步更新，供 vibe/LLM 获取上下文。

## 👀 观测 & 调试
- 健康检查：`GET /healthz`（所有服务需实现）。
- 指标：`/metrics` 暴露 Prometheus 采集结果。
- 日志：建议使用 `structlog` 并包含 `trace_id`、`span_id`、`principal` 字段。

> 现已支持 `POST /collections/cases`、`GET /collections/cases`、`POST /collections/cases/{id}/actions`、`POST /events/loan`、`POST /events/payment`。如需对接真实 Kafka/DB，可在此基础上扩展。
