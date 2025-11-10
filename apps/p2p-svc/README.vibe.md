# P2P Service (Phase 2) · README.vibe.md

> Domain: 资金方账户与撮合

## ⚡ Quickstart
1. `task run:p2p-svc` — 启动本服务（若 `app/main.py` 尚未创建会给出提示）。
2. `task lint` / `task test` — 统一代码质量与测试（基于 ruff + pytest）。
3. 使用 VS Code REST Client 打开 `sample.http`，即可在 vibe coding 中快速回放接口。

## 🔌 API 快速体验
- 默认本地地址：`http://localhost:8013`
- 推荐带上 `X-Request-Id` 方便链路追踪。
- 事件钩子：FUNDS_DEPOSITED, MATCH_EXECUTED。

## 🧰 文件约定
- `app/` 目录放 FastAPI 入口、路由与依赖。
- `domain/` 目录放 Pydantic/SQLModel 聚合（待创建）。
- `README.vibe.md` + `sample.http` 永远同步更新，供 vibe/LLM 获取上下文。

## 👀 观测 & 调试
- 健康检查：`GET /healthz`（所有服务需实现）。
- 指标：`/metrics` 暴露 Prometheus 采集结果。
- 日志：建议使用 `structlog` 并包含 `trace_id`、`span_id`、`principal` 字段。

> TODO: 在实现阶段记得更新本文件，确保步骤与端点和代码保持一致。
