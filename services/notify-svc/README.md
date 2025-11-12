# notify-svc (通知中心 · T13)

T13 交付：模板化通知中心，聚合短信/Email/Push/WhatsApp 触达能力，并对接可扩展的通道适配器。当前实现提供：

- `POST /notifications/send` —— 基于模板与变量渲染通知正文，校验渠道所需字段，写入 SQLite (`notify.db`) 并立即发送（或在 `sendAt` 之后调度）。
- `GET /notifications/tasks/{taskId}` —— 查询任务详情、状态、渲染后的正文及错误信息，可用于排查失败任务。
- 模板仓库：`templates/catalog.json`，使用 Jinja2 渲染，`requiredVariables` 控制变量校验。
- 幂等：必须携带 `X-Idempotency-Key`，重复请求直接返回首次提交结果。
- 事件日志：`NOTIFY_ENQUEUED` / `NOTIFY_SENT` / `NOTIFY_FAILED` / `CHANNEL_DISPATCHED` 便于串联链路。

## 运行方式
```bash
cd services/notify-svc
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8009
```

## 调用示例
```bash
curl -X POST http://localhost:8009/notifications/send \
  -H 'Content-Type: application/json' \
  -H 'X-Idempotency-Key: sms-loan-approved-001' \
  -d '{
        "channel": "sms",
        "template": "loan_approved",
        "audience": {"userId": "user-123", "phone": "233555000111"},
        "variables": {
          "borrowerName": "Ama",
          "loanId": "LN20241120001",
          "amount": "500 GHS",
          "dueDate": "2024-12-15"
        }
      }'
```

若 `sendAt` 早于当前时间，将立即调用 `channel_client` 模块完成发送并输出 `NOTIFY_SENT`；若 `sendAt` 在未来，则状态为 `SCHEDULED`，待后续调度器（下一阶段）消费。

## TODO
- 引入 Celery/任务调度以消费 `SCHEDULED` 任务，支持重试策略与告警。
- 接入真实短信/WhatsApp/Email 通道与签名校验；`channel_client.py` 现为 mock。
- 增加模板 CRUD (`/admin/notify/templates`) 配合 BFF & Admin Web。
- 将事件发送到 Kafka 供 report/collection 域消费。
