# risk-svc (Evaluation Stub)

实现任务 **T5**：`POST /risk/evaluations`，用于接收贷款申请信息并返回风控决策（APPROVE/REVIEW/REJECT），同时记录规则命中日志。

## 特性
- 简单规则：根据设备授权、KYC 状态、申请金额等条件给分。
- 返回 score、decision、reasons 列表，方便 loan-svc 对接。
- 模拟事件日志（当前写入内存/控制台，后续可接 Kafka）。

## 运行
```bash
cd services/risk-svc
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8082
```

## 接口示例
```http
POST /risk/evaluations
Content-Type: application/json

{
  "userId": "U10002",
  "loan": {
    "loanId": "L20250101001",
    "amount": 500,
    "termDays": 14,
    "productId": "P_BASIC"
  },
  "signals": {
    "device": {"privacyConsent": true},
    "kyc": {"status": "APPROVED"},
    "history": {"overdueDays": 0}
  }
}
```

响应：
```json
{
  "decision": "APPROVE",
  "score": 712,
  "reasons": []
}
```

## TODO
1. 接入规则引擎/配置中心，支持热更新。
2. 输出 Kafka 事件供 report-svc/loan-svc 监听。
3. 增加命中日志查询 API。
