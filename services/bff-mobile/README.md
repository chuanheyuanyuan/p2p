# bff-mobile · 借款端聚合层（T17）

FastAPI 服务，面向借款 App 暴露精简 API，内部聚合 loan-svc / payment-svc / user-svc。

## 能力
- `GET /mobile/v1/dashboard`：基于 loan-svc 聚合借款人最近贷款、应还金额与推荐产品。
- `GET /mobile/v1/loans`：查看当前账号的全部贷款草稿/在途/已结清记录。
- `POST /mobile/v1/loans`：按产品/金额/期限创建贷款草稿，自动注入 `userId`。
- 所有接口均要求 `X-User-Id` 请求头，可选 `X-Device-Id` 透传给下游。

## 快速开始
```bash
cd services/bff-mobile
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

默认依赖本地 loan-svc（`http://127.0.0.1:8083`），可通过下述环境变量覆盖：

- `BFF_MOBILE_LOAN_BASE_URL`
- `BFF_MOBILE_PAYMENT_BASE_URL`
- `BFF_MOBILE_USER_BASE_URL`
- `BFF_MOBILE_HTTP_TIMEOUT`（秒，默认 5）

## 测试
```bash
cd services/bff-mobile
source .venv/bin/activate
pytest -q
```

## 后续路线
1. 接入 auth-svc 校验 Borrower JWT，而非纯 header。
2. 聚合 payment-svc 账单 & repayment timeline。
3. 缓存 Dashboard 数据，补充 `/mobile/v1/profile` 等端点。
