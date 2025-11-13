# channel-svc · 渠道归因（T15）

FastAPI 服务，用于接收 Kochava/渠道归因事件并输出漏斗统计。

## 能力
- `POST /channels/attributions`：接收 `install/register/apply/disburse` 事件，按 `installId + event` 幂等写入 `channel.db`。
- `GET /channels/funnel`：按日期/渠道聚合安装→放款漏斗与 spend，默认最近 7 天。
- 事件、统计均存储在 SQLite，方便本地验证，可平滑迁移到 Postgres/ClickHouse。

## 运行
```bash
cd services/channel-svc
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8011
```

## 环境变量
- `CHANNEL_DB_PATH`（可选）：自定义 SQLite 路径，默认 `./channel.db`。

## 测试
```bash
cd services/channel-svc
source .venv/bin/activate
pytest
```

## TODO
1. 接入 Kafka/ClickHouse，替换同步 API。
2. 增加 campaign 维度成本 API 与报表对账。
3. 与 report-svc 对齐漏斗指标，输出渠道 KPI。
