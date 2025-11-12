# report-svc · 平台每日统计（T14）

提供最小可用的日度经营指标查询 API，聚合 loan/payment/collection 域的 SQLite 数据，按需刷新缓存，供 BFF/Admin Web 查询。

## 能力
- `GET /reports/daily?businessDate=YYYY-MM-DD`：返回指定业务日期的指标；若无缓存或携带 `forceRefresh=true` 将实时扫描各服务的 SQLite 并落库 `report.db`。
- `POST /reports/daily/refresh?businessDate=YYYY-MM-DD`：手动触发重算，返回最新生成时间与缺失指标列表。
- `GET /reports/aging?bucket=D7`：统计催收案件的分布与状态，可按 bucket 过滤。
- 健康检查 `GET /healthz`。

## 数据来源
- `loan.db`：`loan_applications`（申请/提交数量）。
- `payment.db`：`disbursements`、`repayments`（放款/还款笔数与金额，金额以 Decimal(18,4) 输出）。
- `collection.db`：`collection_cases`（建案/结案数量、各 bucket/状态分布）。
- 如果某个 DB 不存在，指标默认 0 并在响应 `notes` 中给出提示，同时在 `metrics.sources` 标记布尔值，方便排查。

## 运行
```bash
cd services/report-svc
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8012
```

## 示例
```bash
# 查询日指标并强制刷新
curl "http://localhost:8012/reports/daily?businessDate=2024-11-20&forceRefresh=true"

# 手动刷新
curl -X POST "http://localhost:8012/reports/daily/refresh?businessDate=2024-11-20"

# 催收 aging
curl "http://localhost:8012/reports/aging?bucket=D7"
```

> TODO：接入 Kafka/ClickHouse，覆盖注册/登录/复贷率、首逾率等高级指标，并补充告警/监控。
