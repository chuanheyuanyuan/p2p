# Observability Stack（T20）

该目录提供一套本地可运行的观测与审计能力，覆盖链路追踪 (OpenTelemetry Collector)、审计事件 API 及 Grafana Dashboard 示例。

## 组件
1. **audit-svc** (`app/`)：FastAPI 服务，提供 `POST /audit/events`、`GET /audit/events`、`GET /audit/events/{id}`，入库到 `audit.db` 并支持按 actor/action/time 过滤；接口默认校验 `Authorization: Bearer <JWT>`（密钥通过 `OBS_JWT_SECRET/OBS_JWT_ALGORITHM` 配置），同时暴露 `/metrics` Prometheus 端点。
2. **otel-collector-config.yaml**：最小化 OTel Collector 配置，将 OTLP 日志/指标导出到本地文件并可转发到 Grafana Agent。
3. **dashboards/**（预留）：放置 JSON 模板，结合 Grafana 导入即可展示接口延迟、审计写入量等指标。

## 启动步骤
```bash
cd infra/observability
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8030
```

可通过 `Taskfile` 的 `task run:observability` 启动（需 Python 环境就绪），默认 JWT Secret `obs-jwt-secret`，可通过 `OBS_JWT_SECRET`/`OBS_JWT_ALGORITHM` 环境变量覆盖。

## API 示例
```bash
curl -X POST http://localhost:8030/audit/events   -H 'Content-Type: application/json'   -H 'Authorization: Bearer <JWT>'   -d '{
    "actorId": "ops.lead",
    "actorType": "ADMIN",
    "action": "APPROVE_LOAN",
    "resourceType": "LOAN",
    "resourceId": "LN123",
    "severity": "INFO",
    "payload": {"note": "auto approve"}
  }'

curl "http://localhost:8030/audit/events?actorId=ops.lead&limit=20" \
  -H "Authorization: Bearer <JWT>"

curl "http://localhost:8030/audit/events/<eventId>" \
  -H "Authorization: Bearer <JWT>"

curl http://localhost:8030/metrics
```

## OpenTelemetry Collector
示例配置位于 `otel-collector-config.yaml`，默认监听 4317/4318 端口，将接收到的 trace/logs/metrics 写入 `./otel-data/`，方便后续以 Loki/Tempo 取代。

运行：
```bash
otelcol --config infra/observability/otel-collector-config.yaml
```

## Grafana Dashboard
- 可通过 `dashboards/audit-overview.json` 导入，展示每分钟事件量、常见 action、Top actor。
- audit-svc 对外暴露 `/audit/events`，可被 Grafana Agent 抓取并写回 Loki 进行查询。

## 待办
1. 将当前文件写入 stub 替换为真实 Kafka Producer / ClickHouse Writer，并提供重试/监控。
2. 对接 auth-svc 的 token introspection，自动轮转密钥并在事件中记录租户/角色。
3. 扩展 Grafana dashboard 与告警模板（如异常事件峰值、接口延迟）。
