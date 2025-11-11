# 开发上下文与进度记录（当前窗口）

## 初始设定
- **架构角色**：我扮演资深架构师/技术负责人/交付经理，以任务分解表为牵引按序实现后端服务；优先 FastAPI 技术栈，并在虚拟环境中运行所有服务。所有的回答用中文。
- **沟通偏好**：遇到网络/兼容问题时优先自行定位；Python 版本为 3.9，禁止使用 `| None` 语法；调试阶段可提供固定数据，但完成后需恢复随机/真实逻辑；服务间接口通过 curl 示例验证。
- **运行习惯**：每个服务单独创建 `.venv`，通过 `uvicorn app.main:app --reload --port <port>` 启动；日志需在终端查看，必要时加调试接口。

## 已交付服务

### auth-svc（T1/T2）
- 目录：`services/auth-svc/`，端口 8080。
- 功能：`POST /auth/otp`（速率限制、OTP 生成）、`POST /auth/token`（OTP 校验、JWT/Refresh Token 签发）。
- 依赖：可选 Redis；默认 fallback 内存。OTP 默认随机，调试时可在 `OTPService` 固定 code。
- 验证：curl 先请求 OTP，再用返回的 `requestId` + 终端日志中的 code 调 TOKEN。

### user-svc（T3/T4）
- 目录：`services/user-svc/`，端口 8081。
- `PUT /users/{id}/device`：存储/更新设备指纹，幂等更新 `lastActiveAt`；SQLite `user.db`。
- `PUT /users/{id}/kyc`：接受 KYC 元数据与状态，写入 DB 并生成 `kyc/<userId>.json` 快照。
- 注意：启用 `jsonable_encoder` 处理 datetime；日志在服务终端查看。

### risk-svc（T5）
- 目录：`services/risk-svc/`，端口 8082。
- `POST /risk/evaluations`：基于 KYC 状态、设备授权、逾期天数等规则返回 `decision/score/reasons`；供 loan-svc 调用。

### loan-svc（T6~T8）
- 目录：`services/loan-svc/`，端口 8083。
- `GET /loan/products`：读取 `products.json`，支持 `productId` 过滤。
- `POST /loans`、`POST /loans/{id}/submit`：创建草稿、提交申请并调用 risk stub。
- `GET /loans/{id}/contracts`：生成合同文本（`contracts/<loanId>.txt`）并返回 URL/过期时间。
- 所有 `Optional` 类型已适配 Python 3.9（使用 `typing.Optional`）。

### payment-svc（T9）
- 目录：`services/payment-svc/`，端口 8084。
- `POST /payments/disbursements`：生成 reqNo、保存状态、调用模拟通道；`POST /callbacks/mock-channel` 用于回调。
- 调试接口 `GET /payments/disbursements` 可查看当前内存中的放款记录。

### ledger-svc（T10）
- 目录：`services/ledger-svc/`，端口 8085。
- `POST /ledger/entries`：校验借贷平衡（Decimal 18,4），生成 `entryId` 并在内存存储 entry。

### payment-svc + loan-svc（T11）
- payment-svc 增加 `POST /payments/repayments`（登记主动/回调还款，写入内存仓储并调用 loan-svc 刷新账单）、`GET /payments/repayments`（调试列表），并通过 `REPAYMENT_POSTED` 事件日志输出；新增 `LOAN_SVC_BASE_URL` 配置，金额统一使用 `Decimal(18,4)`。
- loan-svc 新增账单调度模块（`LoanBillingService`），创建贷款草稿时即初始化 schedule，`POST /loans/{loanId}/repayments` 接口扣减应还金额，支持多次/部分还款并在结清时标记 `REPAID`。
- 还款请求按照 txnRef 幂等，payment-svc 成功调用后会记录 `appliedAmount/remainingDue`，重复请求直接返回已有结果；两端均保持 3.9 兼容写法。
- 调试方式：同时启动 loan-svc 与 payment-svc，先调用 loan-svc 的 `POST /loans` 创建草稿，再用 `apps/payment-svc/sample.http` 里的还款示例触发账单扣减，可通过 `GET /payments/repayments` 或 loan-svc 还款接口返回体查看剩余应还。

## 运行提示与偏好
- 所有服务都需在对应目录下 `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`。
- Python 3.9 不支持 `| None`，请使用 `Optional[...]` 并导入 `typing.Optional`。
- 日志需在 uvicorn 终端查看，必要时增加调试接口（如 payment-svc 的列表接口）。
- `curl` 是默认验证方式；每个服务 README 中记录了示例。
- 若服务重启，内存仓库数据会清空（payment-svc、ledger-svc 等），这是预期行为；如需持久化，需后续接入 DB/Redis。

此文档供下一窗口继续开发或优化时参考。顺序继续 T11 及后续任务，并延续上述约定。
