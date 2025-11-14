# ops-svc · 运营配置服务（T16）

FastAPI 服务，提供运营产品/等级/策略 CRUD 和配置热加载。配置变化写入 SQLite `ops.db`，并记录 audit 日志。

## 能力
- `POST /ops/products`：新建产品并生成版本号。
- `PUT /ops/products/{product_id}`：变更产品配置，版本号自动 +1；自动写审计记录。
- `GET /ops/products` / `DELETE /ops/products/{product_id}`：查询/移除产品。
- `POST /ops/grades` & `GET /ops/grades`：运营等级配置。
- `POST /ops/rules` & `GET /ops/rules`：审批/策略规则。
- `POST /ops/reload`：热加载入口 + audit 记录。
- `GET /ops/audit`：查询最近的变更记录。

## 运行
```bash
cd services/ops-svc
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8021
```

## 环境变量
- `OPS_DB_PATH`：自定义 SQLite 文件。
- `X-Admin-Token` 头必填，默认 `admin-token`。

## 测试
```bash
cd services/ops-svc
source .venv/bin/activate
pytest
python scripts/verify_ops_api.py
```
