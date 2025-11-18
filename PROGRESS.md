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
- `notify-svc`（T13）上线，聚合短信/Email/Push/WhatsApp 模板：
  - 目录：`services/notify-svc/`，端口 8009，对应 DB `notify.db`。
  - `POST /notifications/send`：要求 `X-Idempotency-Key`，根据 `templates/catalog.json` 渲染正文，校验变量与渠道必填字段；立即触发 mock 通道或根据 `sendAt` 标记 `SCHEDULED`。
  - `GET /notifications/tasks/{taskId}`：查询任务详情、变量、渲染正文与错误信息。
  - 模块化 `template_engine` + `channel_client`，输出 `NOTIFY_ENQUEUED/NOTIFY_SENT/NOTIFY_FAILED/CHANNEL_DISPATCHED` 事件，供后续串联 loan/payment/collection。
  - TODO：接入真实通道、补充模板 CRUD、增加调度/重试与告警。
- `ops-svc`（T16）为运营配置提供 CRUD + 审批服务：
  - 目录：`services/ops-svc/`，端口 8021，主 DB `ops.db`（SQLite）。
  - `POST/PUT/GET/DELETE /ops/products`：产品配置带版本号，更新触发审批链 + 审计记录。
  - `POST /ops/grades`, `POST /ops/rules`：管理等级/策略，支持 `active` 字段与 `GET` 查询。
  - `POST /ops/reload` + `GET /ops/audit`：热加载 + 审计流水，所有变更写日志（`ops_audit`）。
  - 附带 README、sample.http、pytest 测试与 `scripts/verify_channel_api.py`（改名或新增适配 ops），便于运营/QA 验证。
- `bff-admin`（T18）补齐 Admin Web 聚合层：
  - 目录：`services/bff-admin/`，端口 8002，默认直接读取 loan/payment/collection/user SQLite 并返回前端所需 JSON。
  - `POST /admin/v1/auth/login` + `GET /admin/v1/auth/me`：内置账号签发 JWT，后续路由均校验 `Bearer`。
  - `GET /admin/v1/applications`/`/{id}`/`/export`：输出申请列表、详情（含审批历史/文档）与导出任务号；`GET /admin/v1/users/{userId}` 聚合设备/KYC 档案。
  - `GET /admin/v1/collections/cases`/`/{id}`：加载催收案件、行动、PTP 记录；`GET /admin/v1/dashboard`、`/reports/daily`、`POST /reports/daily/export` 提供运营看板与日报。
  - README.vibe/sample.http 更新，新增 `pytest services/bff-admin/tests/test_bff_admin.py` 覆盖登录、申请、催收、报表串联流。
- `bff-mobile`（T17）上线借款端聚合层：
  - 目录：`services/bff-mobile/`，端口 8001，依赖 loan-svc 聚合 borrower Dashboard 与贷款列表，`POST /mobile/v1/loans` 自动注入 `userId` 并透传幂等头。
  - `GET /mobile/v1/dashboard` 返回应还金额、活动贷款与产品推荐；`GET /mobile/v1/loans` 列出借款记录，所有接口校验 `X-User-Id`。
  - README.vibe/sample.http/Taskfile run 指令同步更新，`tests/test_mobile_bff.py` 借助 stub client 覆盖聚合/创建逻辑，requirements 精简为 fastapi/httpx/pytest。
- `observability-svc`（T20）提供统一观测与审计：
  - 目录：`infra/observability/`，端口 8030，FastAPI `POST/GET /audit/events` 将事件写入 `audit.db` 并支持 actor/action/time 过滤，启动即执行过期数据清理（默认 90 天）。
  - 内置 `otel-collector-config.yaml` 与 `dashboards/` 模板占位，可直接运行 OTel Collector 将 trace/log/metrics 写入本地文件，后续接入 Grafana/Loki。
  - README 记录安装、curl 示例、TODO；新增 `GET /audit/events/{id}` 与 `/metrics`，新增 Kafka/ClickHouse 管道 stub（写入本地 log）、JWT Bearer 鉴权（复用 auth-svc secret、提取 `service` claim 写入 `sourceService`）、`dashboards/audit-overview.json` Grafana 模板，以及 `tests/test_audit_api.py` 覆盖创建/过滤/详情/metrics/管道，`Taskfile` 同步增加 `task run:observability`。

### admin-web（T19 · M1 登录 & RBAC）
- 技术栈调整为 React Query + Zustand：所有列表/详情数据改用 React Query，`src/services/http.ts` 自动注入 `Authorization`，mock 兜底仍在 `services/api.ts`。
- 新增 `/login` 页面与 `RequireAuth/RoleGuard`：登录成功后写入 Zustand（含 token/roles/permissions），菜单与路由按 `navSections.roles` 自动过滤，403 页面提示角色不足。
- `Sidebar` RBAC 过滤已写 Vitest+RTL 单测（`npm run test`），默认 mock 账号包括 `ops.lead`、`collector.jr`、`analyst`，方便验证不同视角。
- 文档更新：`apps/admin-web/README.md`/`README.vibe.md` 说明登录流程与角色；`apps/bff-admin/sample.http` 增加 `/admin/v1/auth/login`/`/auth/me` 示例，便于后端联调。

### admin-web（T19 · M2 Dashboard + Daily Stats）
- Dashboard 页面接入 `fetchDashboardOverview`，对接 `/admin/v1/dashboard`（mock fallback），新增 KPI 卡片、逾期概览、催回进度、今日指标、新客转化率，支持 Skeleton、错误提示与重试按钮。
- Daily Stats 页面扩展 React Query 状态、摘要统计（`summarizeDailyStats`）、导出按钮（触发 `/admin/v1/reports/daily/export`），并通过 `Alert` 告警接口拉取失败。
- 新增 `exportDailyStats` Service、`dashboardMock` 数据结构及 `Dashboard` 组件加载态；补充 `apps/admin-web/src/utils/__tests__/dailyStats.test.ts` 单侧保障聚合逻辑。
- 文档/sample 更新：`README.md`、`README.vibe.md` 说明 M2 功能；`apps/bff-admin/sample.http` 增加 dashboard/daily APIs 及导出示例；`整体开发计划.md` 标记 M2 进度。

### admin-web（T19 · M3 申请列表 & 详情）
- `Applications` 页面升级：全面对接 bff-admin `/admin/v1/auth|applications`，React Query + Zustand 持久化筛选（贷款编号/关键字/手机号/时间/渠道/产品/状态/App 版本/复借），增加批量选中后触发批量导出/复核的交互提示，并显示剩余本金、风险评分、上次还款等字段。
- `ApplicationDetail` 拆分为“概览（含指标卡）+贷款信息+还款概览+客户画像+审批摘要+审批流程+历史+凭证”多 Tab，展示 BFF 返回的剩余本金、原始金额、风险评分、命中原因以及下载链接。
- `services/api.ts`、`mocks/data.ts` 对齐 BFF 字段（productId/outstandingAmount/lastPaidAt 等），Status/Tag 渲染逻辑同步更新；Vitest 持续覆盖格式化/Sidebar 用例。
- bff-admin 新增可配置筛选参数（startDate/endDate/product/channel/repeat 等）与合成字段（phone/channel/level），pytest 用例补充 repeat/date 过滤，README/临时文件同步说明。

### admin-web（T19 · M4 Borrower 360 档案）
- bff-admin `/admin/v1/users/{userId}` 聚合 user-svc、loan-svc、collection-svc，输出 `loanSummary`、`device`、`kyc`、`collectionSummary` 等结构，pytest 新增用户档案断言。
- admin-web `UserProfile` 重构为 Borrower 360：顶部指标卡 + 身份/贷款/催收/风控/KYC/设备多卡片，展示剩余本金、活跃贷款、授权状态及标签。
- `mocks/data.ts`、`README.md` 同步新字段说明；执行 `pytest` 与 `npm run test -- --passWithNoTests` 验证。

### admin-web（T19 · M5 财务放/还款对账）
- bff-admin 新增 `/admin/v1/finance/disbursements|repayments|reconciliations`，聚合 payment.db/ledger.db 多维筛选，提供分页与 pytest 覆盖。
- admin-web `/finance` 页面以 Tabs 呈现放款/还款/对账明细，具备多条件筛选、批量导出提示及金额格式化。
- `services/api.ts`、`mocks/data.ts` 补充财务相关类型与 fallback，README/临时文件同步说明，执行 `pytest` 与 `npm run test -- --passWithNoTests`。

### admin-web（T19 · M4 借款人档案 & 审批四 Tab）
- `applicationDetailsMock` / `userProfilesMock` 补齐 KYC、设备、隐私授权、渠道轨迹、历史借还等字段；ApplicationDetail 拆分 `BorrowerProfileTab/ApprovalTimelineTab/HistoryTab/DocumentsTab`，新增“借款人档案”视图并沿用 React Query Skeleton/错误处理。
- `UserProfile` 页面升级为“概览/KYC/设备/借还”四 Tab，展示账号状态、授信额度、标签/风险提示与渠道轨迹，方便财务/催收联动；相关文档（README、README.vibe、整体开发计划、sample.http）同步描述。

### admin-web（T19 · M5 财务放/还款对账）
- 新增 `/finance` 路由与 Finance 页面，角色限定 `finance/super_admin`；页面包含“放款管理/还款管理/对账差异”三 Tab，使用 React Query + AntD Table 展示金额汇总、状态/渠道/日期/关键词筛选与放款失败一键重试。
- `mocks/data.ts` 扩展 `FinanceDisbursement`/`FinanceRepayment`/`ReconciliationDiff` mock；`services/api.ts` 补充财务相关查询、导出、重试接口兜底逻辑，`apps/bff-admin/sample.http` 增加对应示例。
- 文档更新：`README.md`、`README.vibe.md` 记录 M5 能力，`整体开发计划.md` 标记前端路线进度，`临时文件` 说明调试步骤。

### admin-web（T19 · M7 运营配置 & App 升级）
- `/ops` 页面重构为多 Tab：产品配置、等级管理、渠道链接、消息模板、审批规则、App 版本清单，全部通过 React Query 拉取 mock 数据并允许本地新增/启停模拟。
- `mocks/data.ts` 增加 `opsProductsMock`、`gradeConfigsMock`、`channelLinksMock`、`messageTemplatesMock`、`approvalRulesMock`，`services/api.ts` 提供对应 fetch fallback。
- `README.md`、`README.vibe.md`、`apps/bff-admin/sample.http`、`整体开发计划.md` 与 `临时文件` 更新 M7 功能说明，便于后续 BFF 接口联调。

### admin-web（T19 · M8 报表中心首版）
- 新增 `ReportCenter` 页面与 `/report-center` 菜单，聚合平台 KPI、逾期迁移率、渠道漏斗、复借率，并展示分析备注。
- 过滤条件支持业务日期/渠道/产品，通过 React Query + Ant Design Form 触发 `fetchReportCenter`，与 bff-admin `/admin/v1/reports/center` 对齐，失败时 fallback 至 `reportCenterMock`。
- `services/api.ts` 增加 `ReportCenterQuery`/`fetchReportCenter`，`mocks/data.ts` 扩展 `ReportCenterData` 模型与 mock 数据，侧边栏/路由加入权限守卫（analyst/ops）。
- README 更新“当前特性”，强调 M8 报表中心预研版及数据来源/刷新节奏，并跑通 `npm run test` 验证。
- 报表中心支持导出任务：页面新增“导出”按钮，调用 `exportReportCenter`（POST `/admin/v1/reports/center/export`），成功提示任务号，失败时展示错误。
- 报表中心优化交互：新增“今日/昨日/近 7 天”快捷日期、Spin/Empty 状态，过滤与导出按钮共用 React Query 状态提示，提升体验。

### Sprint 9（Finance 聚合 & Borrower 360 增强）
- bff-admin 新增 `/admin/v1/finance/disbursements|repayments|reconciliations` 路由，复用 `list_disbursements/list_repayments/list_reconciliations` 访问 `payment.db`/`ledger.db`，统一 JWT 鉴权并在 `schemas` 中补全财务模型；`pytest services/bff-admin/tests/test_bff_admin.py` 覆盖 finance 列表断言。
- Admin Web `/finance` 页面落地，使用 React Query + Antd Table 显示放款/还款/对账列表，支持状态、渠道、日期过滤及分页，mock fallback 同步扩展；Borrower 360（UserProfile）UI 对接 bff-admin 返回的 `collectionSummary`、`loanSummary` 扩展字段。
- README/PROGRESS/整体开发计划 标记财务/360 里程碑，`npm run test` + `pytest` 验证通过。

### Sprint 10（催收九模块增强）
- bff-admin `collections` 路由扩展 `/cases/{id}/actions` 支持 Decimal PTP 金额/状态更新、`/stats` 返回案件池桶/状态分布；新增 `routers/finance.py` 对接 finance 聚合，并在测试夹具中丰富催收案件/行动种子，覆盖案件列表、详情、stats 与 action 场景。
- Admin Web `Collections` 页面完成案件池统计卡、查询表单（Bucket/状态/催收员）、Drawer 工作台、跟进/PTP 表单与 React Query 联动，实际调用 `fetchCollectionStats`、`createCollectionAction` 并在成功后刷新列表/详情缓存。
- README（apps/admin-web）补充 Finance/Collections 能力说明，`pytest services/bff-admin/tests/test_bff_admin.py` 与 `npm run test -- --passWithNoTests` 均通过，PROGRESS/整体开发计划同步记录 Sprint 10 里程碑。

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
