# collection-svc (Collections Case Stub)

任务 T12：实现催收建案与分案，提供基础工作台接口：
- `POST /collections/cases`：根据贷款与 bucket 创建案件、自动或手动分案。
- `GET /collections/cases` / `GET /collections/cases/{id}`：查看案件及行动记录。
- `POST /collections/cases/{id}/actions`：记录催收动作、PTP 承诺并驱动状态流转。
- `POST /events/loan`：接收 loan-svc 的 `DUE_TODAY/OVERDUE_BUCKET_CHANGED` 等事件，自动建案或同步 bucket。
- `POST /events/payment`：消费 payment-svc 的 `REPAYMENT_POSTED`，根据剩余应还自动结案/破约 PTP。

## 运行
```bash
cd services/collection-svc
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8086
```

> 通过环境变量 `COLLECTOR_POOL`（JSON 数组或逗号分隔字符串）可覆盖默认分案坐席列表；案件与行动数据保存在本地 `collection.db`。

## 体验
1. `POST /events/loan` 或 `POST /collections/cases`（见 `apps/collection-svc/sample.http`）创建案件，收到 `caseId`。
2. 使用 `POST /collections/cases/{caseId}/actions` 记录通话、短信等动作，可附带 `ptpAmount/ptpDueAt`、`status`。
3. payment-svc 完成还款后调用 `POST /events/payment`，服务自动把案件标记为 `PAID` 或 `BROKEN_PTP`。
4. `GET /collections/cases` 可按 `bucket/status/assignedTo` 过滤，数据默认写入本地 SQLite，可挂载卷做持久化。

## TODO
- 接入真实事件源（如 loan-svc 的 `OVERDUE_BUCKET_CHANGED`）自动建案。
- 落库 Postgres + 审计日志，增加 WebSocket 推送给催收工作台。
- 与 notify-svc 集成，自动发送催收提醒/确认 PTP。
