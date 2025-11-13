# Channel Service · README.vibe.md

> Domain: 渠道投放与归因

## ⚡ Quickstart
1. `cd services/channel-svc && python3 -m venv .venv && source .venv/bin/activate`
2. `pip install -r requirements.txt`
3. `uvicorn app.main:app --reload --port 8011`

## 🔌 API
- `POST /channels/attributions`
  - Body: `installId/channel/campaign/event/cost/occurredAt`
  - 幂等：`installId + event`，成功返回 204。
- `GET /channels/funnel?startDate=2025-11-10&endDate=2025-11-12&channel=facebook`
  - 返回安装→注册→申请→放款 + spend，默认最近 7 天、`channel=all`。
- 健康检查：`GET /healthz`

## 🧪 Testing
```bash
cd services/channel-svc
source .venv/bin/activate
pytest
```

## 👀 调试提示
- `CHANNEL_DB_PATH` 环境变量可切换 SQLite 路径，方便多实例测试。
- `apps/channel-svc/sample.http` 提供完整上报/漏斗查询示例。
- 日志中 `event=CHANNEL_ATTRIBUTION_RECORDED` / `CHANNEL_FUNNEL_QUERY` 便于追踪链路。
