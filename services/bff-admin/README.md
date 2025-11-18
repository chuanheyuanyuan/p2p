# bff-admin · 管理端聚合服务（T18）

提供 Admin Web 访问的统一聚合接口，串联 loan/payment/collection/user/report 等 SQLite 数据源，补齐登录鉴权、应用列表、催收、基础报表等最小能力。

## 功能
- `POST /admin/v1/auth/login` + `GET /admin/v1/auth/me`：基于 SQLite `admin.db` 中的账号发放 JWT（作用域 `admin`），支持自定义账号列表与密码盐。
- `GET /admin/v1/applications`：分页返回贷款申请及账单状态，支持 `status`/`userId`/`loanId`/`keyword` 查询。
- `GET /admin/v1/applications/{id}`：聚合基本信息/客户画像/审批记录/文档列表。
- `POST /admin/v1/applications/export`：生成导出任务占位符（`taskId`）。
- `GET /admin/v1/users/{userId}`：从 `user.db` 的设备/kyc 表推导档案视图。
- `GET /admin/v1/collections/cases` + `GET /admin/v1/collections/cases/{id}`：读取 `collection.db` 案件及行动轨迹。
- `GET /admin/v1/dashboard`：基于 `loan.db`/`payment.db`/`collection.db` 快速计算概览 KPI。
- `GET /admin/v1/reports/daily` + `POST /admin/v1/reports/daily/export`：输出按日指标（支持起止日期 + 分页），并返回导出任务号。
- `GET /healthz`：健康检查。

所有 `/admin/v1/*` 路由（除 login）均依赖 `Authorization: Bearer <token>`。

## 运行方式
```bash
cd services/bff-admin
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8002
```

环境变量（均带前缀 `BFF_ADMIN_`）：

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `LOAN_DB_PATH` | `services/loan-svc/loan.db` | 贷款 SQLite 路径 |
| `PAYMENT_DB_PATH` | `services/payment-svc/payment.db` | 放/还款 SQLite |
| `COLLECTION_DB_PATH` | `services/collection-svc/collection.db` | 催收 SQLite |
| `USER_DB_PATH` | `services/user-svc/user.db` | 用户设备/KYC SQLite |
| `ADMIN_DB_PATH` | `services/bff-admin/admin.db` | 管理员账号 SQLite |
| `ADMIN_PASSWORD_SALT` | `bff-admin-static-salt` | 登录密码 PBKDF2 盐（修改后需重新 seed） |
| `ADMIN_USERS` | 内置 3 个账号 | 可通过 `.env` 重写 JSON |

### 认证与调试

- 首次启动时会自动在 `ADMIN_DB_PATH` 初始化 `admin_users` 表，并使用 `ADMIN_USERS` 中的默认账号/密码进行 seed。
- 可以通过以下 `curl` 命令快速自检：

```bash
# 登录并保存 token
TOKEN=$(curl -s http://localhost:8002/admin/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"ops.lead","password":"admin123"}' | jq -r '.accessToken')

# 查看当前会话
curl http://localhost:8002/admin/v1/auth/me -H "Authorization: Bearer $TOKEN"
```

## 本地验证
```bash
# 1. 启动 loan/payment/collection/user/report 服务各自写入 sqlite
# 2. 启动 bff-admin 并使用 VS Code REST Client 运行 apps/bff-admin/sample.http

# 自动化测试
pytest services/bff-admin/tests/test_bff_admin.py -q
```

> Admin Web (`apps/admin-web`) 只需将 `VITE_API_BASE_URL` 指向 `http://localhost:8002` 即可命中真实聚合接口，详细字段请参考 `app/schemas.py`。
