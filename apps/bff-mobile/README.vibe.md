# Mobile BFF · README.vibe.md

> Domain: 借款端聚合层

## ⚡ Quickstart
1. `cd services/bff-mobile && python3 -m venv .venv && source .venv/bin/activate`，`pip install -r requirements.txt`。
2. `uvicorn app.main:app --reload --port 8001` 或 `task run:bff-mobile`（需将 Taskfile 中路径指向 `services/bff-mobile`）。
3. `pytest services/bff-mobile/tests -q` 校验聚合逻辑，`ruff` 可选。
4. 使用 VS Code REST Client 打开 `sample.http`，附带 `X-User-Id` 请求头即可回放接口。

## 🔌 API 快速体验
- 默认本地地址：`http://localhost:8001`
- 请求头：`X-User-Id`（必填）和 `X-Device-Id`（可选），方便 BFF 注入身份。
- 推荐带上 `X-Request-Id` 方便链路追踪。
- 事件钩子：MOBILE_SESSION_LOGGED, APP_VERSION_ALERT。

## 🧰 文件约定
- `app/` 目录放 FastAPI 入口、路由与依赖。
- `domain/` 目录放 Pydantic/SQLModel 聚合（待创建）。
- `README.vibe.md` + `sample.http` 永远同步更新，供 vibe/LLM 获取上下文。

## 👀 观测 & 调试
- 健康检查：`GET /healthz`（所有服务需实现）。
- 指标：`/metrics` 暴露 Prometheus 采集结果。
- 日志：建议使用 `structlog` 并包含 `trace_id`、`span_id`、`principal` 字段。

> 当前 BFF 已落地 `/mobile/v1/dashboard`、`/mobile/v1/loans`，聚合 loan-svc / payment-svc，后续补充更多 borrower API。
