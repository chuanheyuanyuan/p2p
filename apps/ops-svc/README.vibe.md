# Ops Service · README.vibe.md

> Domain: 运营配置与审批

## ⚡ Quickstart
1. `cd services/ops-svc && python3 -m venv .venv && source .venv/bin/activate`
2. `pip install -r requirements.txt`
3. `uvicorn app.main:app --reload --port 8021`

## 🔌 API
- `POST /ops/products` 项目创建 + `X-Admin-Token` 头。
- `PUT /ops/products/{productId}` 更新版本；`version` 会自动+1。
- `GET /ops/products` / `DELETE /ops/products/{productId}` 及 `POST /ops/grades` / `POST /ops/rules` 等 CRUD。
- `POST /ops/reload` 触发热加载，日志输出 `event=OPS_RELOAD`。
- `GET /ops/audit` 查看最近变更。

## 🧪 Testing
```bash
cd services/ops-svc
source .venv/bin/activate
pytest
```

## 👀 Tips
- `apps/ops-svc/sample.http` 包含典型 config/grade/rule 场景。
- 使用 `X-Admin-Token: admin-token` 模拟 admin 权限。
- 运行 `python services/ops-svc/scripts/verify_ops_api.py` 可快速复现 CRUD + 热加载。
