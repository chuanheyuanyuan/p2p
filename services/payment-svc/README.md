# payment-svc (Disbursement Stub)

任务 T9：实现放款指令与通道回调。提供：
- `POST /payments/disbursements`：创建放款请求，返回 `reqNo`，并模拟发送到通道。
- `POST /callbacks/mock-channel`：通道回调接口，更新状态并返回 ack。

## 运行
```bash
cd services/payment-svc
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8084
```

## 流程
1. 借款系统调用 `POST /payments/disbursements`，包含 `loanId`、`amount`、`account` 等。
2. 服务生成 `reqNo` 存入内存，初始状态 `PENDING`。
3. 通道模拟器（`channel_client.py`）异步调用 `/callbacks/mock-channel`，返回 `SUCCESS` 或 `FAILED`，并更新状态。
4. 后续可扩展为真实第三方通道 + Kafka 事件。

## TODO
- 持久化到数据库 + 幂等锁。
- 接入真实放款通道、签名校验。
- 发布 `DISBURSED` 事件供 ledger/loan-svc 消费。
