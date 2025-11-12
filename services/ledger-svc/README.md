# ledger-svc (Double-entry API)

任务 T10：实现双分录记账接口 `POST /ledger/entries`，对放款/还款等事件进行记账，并校验借贷平衡。

## 功能
- 接收 `refType/refId` 和多条分录行，每行包含 `account`, `debit`, `credit`, `currency`, `memo`。
- 校验：Σdebit == Σcredit，金额使用 Decimal(18,4) 精度。
- 使用本地 `ledger.db`（SQLite）持久化分录，返回 `entryId`，便于后续对账/查询。

## 运行
```bash
cd services/ledger-svc
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8085
```

## 示例
```http
POST /ledger/entries
Content-Type: application/json

{
  "refType": "loan",
  "refId": "L20250101001",
  "lines": [
    {"account":"cash","debit":0,"credit":500,"currency":"GHS"},
    {"account":"loan_principal","debit":500,"credit":0,"currency":"GHS"}
  ]
}
```

响应：
```json
{"entryId":"EN_1700000000_1","refType":"loan","refId":"L20250101001","status":"POSTED"}
```

## TODO
- 接入 Redis 幂等锁
- 消费事件流，与报表/风险服务对账
- 添加 `GET /ledger/entries?refId=` 查询接口
