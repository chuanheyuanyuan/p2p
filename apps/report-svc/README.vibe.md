# Report Service · README.vibe.md

> Domain: 指标与看板 API

## ⚡ Quickstart
1. `cd services/report-svc && python3 -m venv .venv && source .venv/bin/activate`
2. `pip install -r requirements.txt`
3. `uvicorn app.main:app --reload --port 8012`

## 🔌 API
- `GET /reports/daily?businessDate=YYYY-MM-DD[&forceRefresh=true]` —— 汇总 loan/payment/collection SQLite 的指标并缓存到 `report.db`。
- `POST /reports/daily/refresh?businessDate=YYYY-MM-DD` —— 手动重算，返回 `missingMetrics`/`generatedAt`。
- `GET /reports/aging?bucket=D7` —— 查看催收案件 bucket 分布，可不带参数查询全量。
- 健康检查：`GET /healthz`

## 🧰 目录说明
- `services/report-svc/app`：FastAPI 入口、SQLite repository、指标计算器。
- `services/report-svc/report.db`：缓存每日指标（JSON）。
- `apps/report-svc/sample.http`：REST Client 示例，覆盖 daily/aging/refresh。

## 👀 调试
- `metrics.sources` 会标记 loan/payment/collection DB 是否存在；若缺失会在响应 `notes` 提示。
- 默认读取 `services/<svc>/*.db`，如需使用其他数据源可通过 `.env` 覆盖 `*_DB_PATH`。
