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
- `POST /ledger/entries`：校验借贷平衡（Decimal 18,4），生成 `entryId` 并写入 `ledger.db`（SQLite）便于对账。

### payment-svc + loan-svc（T11）
- payment-svc 增加 `POST /payments/repayments`（登记主动/回调还款，写入 `payment.db` 并调用 loan-svc 刷新账单）、`GET /payments/repayments`（调试列表），并通过 `REPAYMENT_POSTED` 事件日志输出；新增 `LOAN_SVC_BASE_URL` 配置，金额统一使用 `Decimal(18,4)`。
- loan-svc 新增账单调度模块（`LoanBillingService`），创建贷款草稿时即初始化 schedule，`POST /loans/{loanId}/repayments` 接口扣减应还金额，支持多次/部分还款并在结清时标记 `REPAID`；贷款草稿与还款计划统一持久化到 `loan.db`。
- 还款请求按照 txnRef 幂等，payment-svc 成功调用后会记录 `appliedAmount/remainingDue`，重复请求直接返回已有结果；两端均保持 3.9 兼容写法。
- 调试方式：同时启动 loan-svc 与 payment-svc，先调用 loan-svc 的 `POST /loans` 创建草稿，再用 `apps/payment-svc/sample.http` 里的还款示例触发账单扣减，可通过 `GET /payments/repayments` 或 loan-svc 还款接口返回体查看剩余应还。

- 目录：`services/collection-svc/`，端口 8086。内置 `AssignmentService`，可通过 `COLLECTOR_POOL` 环境变量覆盖坐席轮询列表，案件与行动存储在 `collection.db`。
- `POST /collections/cases`：创建催收案件，按 loanId 防重，校验 bucket/金额并自动分案，同时打印 `CASE_CREATED` 事件。
- `GET /collections/cases`、`GET /collections/cases/{id}`：支持 bucket/status/assignedTo 过滤，返回案件及历史动作。
- `POST /collections/cases/{id}/actions`：记录 CALL/SMS/N0TE 等动作，允许带 `status`、`ptpAmount/ptpDueAt` 触发状态流转，输出 `CASE_ACTION_LOGGED` / `PTP_PROMISE_SET` 事件。
- `POST /events/loan`：监听 loan-svc 的 `OVERDUE_BUCKET_CHANGED`/`DUE_TODAY` 等事件自动建案或刷新 bucket + principal，并输出 `CASE_BUCKET_SYNCED`。
- `POST /events/payment`：消费 payment-svc 的 `REPAYMENT_POSTED`，自动更新 principalDue，结清后转 `PAID`，逾期的 PTP 违约则转 `BROKEN_PTP`，并输出 `CASE_PAYMENT_APPLIED`。
- 状态机校验非法迁移、已结清案件拒绝再写；调试请求见 `apps/collection-svc/sample.http`。
- `report-svc`（T14）搭建日指标服务：
  - 目录：`services/report-svc/`，端口 8012，读取 `loan.db`/`payment.db`/`collection.db` 聚合申请/放款/还款/催收指标，并缓存到 `report.db`。
  - `GET /reports/daily`：必填 `businessDate`，支持 `forceRefresh`，返回 `metrics`、`notes`、`sources` 及生成时间；若数据缺失会自动计算后写库。
  - `POST /reports/daily/refresh`：手动触发重算，返回 `missingMetrics`/`generatedAt`，便于与调度器集成。
  - `GET /reports/aging`：按 bucket/全量统计催收案件的状态与数量。
  - 提供 README、sample.http、调试指令，后续可替换为 Kafka/ClickHouse 数据管道并补齐注册/登录/首逾口径。


## 运行提示与偏好
- 所有服务都需在对应目录下 `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`。
- Python 3.9 不支持 `| None`，请使用 `Optional[...]` 并导入 `typing.Optional`。
- 日志需在 uvicorn 终端查看，必要时增加调试接口（如 payment-svc 的列表接口）。
- `curl` 是默认验证方式；每个服务 README 中记录了示例。
- 当前 payment-svc、loan-svc、ledger-svc、collection-svc 均已落地 SQLite（*.db）；重启不会丢失数据，但仍建议后续替换为托管数据库/Redis 配置。

此文档供下一窗口继续开发或优化时参考。顺序继续 T11 及后续任务，并延续上述约定。

## 当前交付状态
- loan-svc/payment-svc/ledger-svc/collection-svc 均已落地 SQLite，本地数据库文件分别为 `loan.db`、`payment.db`、`ledger.db`、`collection.db`，初始化逻辑在各自 `app/database.py` 中随 import 执行。
- `临时文件` 中记录了手动验证脚本，可按 “loan → payment → ledger → collection” 顺序跑通，并通过 `sqlite3` 查询验证入库数据。
- ledger-svc 新 repository 使用 JSON 序列化分录行写入 DB；collection-svc 新增 `/events/loan`、`/events/payment` 接口并持久化催收案件/行动，事件日志输出保持不变。
- 待办：根据需要把 SQLite 替换为 Postgres/Redis，并为 ledger-svc/collection-svc 增加查询接口或迁移脚本。
