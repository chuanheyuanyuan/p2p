# channel-svc

Channel attribution & funnel API for InsCash admin.

## Features (T15)
- `POST /channels/attributions` ingest Kochava/渠道回传，按 `installId + event` 幂等。
- `GET /channels/funnel` 汇总安装→注册→申请→放款漏斗及成本。
- SQLite + SQLAlchemy-free实现，便于快速验证；生产可替换为 Postgres/ClickHouse。

## Run
```bash
cd services/channel-svc
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8085
```

## Env
- `CHANNEL_DB_PATH`（可选）：自定义 SQLite 路径，默认 `./channel.db`。

## TODO
1. 接入 Kafka 归因事件，替换同步 API。
2. 增加用户查询 & 分渠道成本 API。
3. 与 report-svc 对账，输出 Kochava/渠道 KPI。
