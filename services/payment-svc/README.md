# payment-svc (Disbursement Stub)

任务 T9/T11：实现放款指令、通道回调与还款登记。提供：
- `POST /payments/disbursements`：创建放款请求，返回 `reqNo`，并模拟发送到通道。
- `POST /callbacks/mock-channel`：通道回调接口，更新状态并返回 ack。
- `POST /payments/repayments`：登记主动还款，调用 loan-svc 刷新账单，返回剩余应还。
- `GET /payments/repayments`：调试接口，可查看当前内存中的还款记录。

## 运行
```bash
cd services/payment-svc
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8084
```

> 还款登记会调用 `loan-svc` 的 `/loans/{loanId}/repayments`，默认基地址为 `http://localhost:8083`，可通过环境变量 `LOAN_SVC_BASE_URL`/`LOAN_SVC_TIMEOUT` 调整。

## 流程
1. 借款系统调用 `POST /payments/disbursements`，包含 `loanId`、`amount`、`account` 等。
2. 服务生成 `reqNo` 存入内存，初始状态 `PENDING`。
3. 通道模拟器（`channel_client.py`）异步调用 `/callbacks/mock-channel`，返回 `SUCCESS` 或 `FAILED`，并更新状态。
4. 后续可扩展为真实第三方通道 + Kafka 事件。

## TODO
- 持久化到数据库 + 幂等锁。
- 接入真实放款通道、签名校验。
- 发布 `DISBURSED/REPAYMENT_POSTED` 事件供 ledger/loan-svc/collection-svc 消费。
- 通过配置中心管理 `loan_svc_base_url`、容错与重试。
