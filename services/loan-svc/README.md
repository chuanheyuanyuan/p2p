# loan-svc (Product Config API)

完成 T6：提供 `GET /loan/products`，返回可用贷款产品的额度/期限/费率配置，并支持缓存热加载（当前为内存模拟）。

## 特性
- 产品配置写在 `products.json`（或内存常量），字段包含 amountRange、termOptions、feeRate、currency。
- 支持查询参数过滤（productId），便于 BFF 只拿特定产品。
- 后续可替换为数据库/配置中心，并注入缓存策略。

## 运行
```bash
cd services/loan-svc
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8083
```

## 接口
- `GET /loan/products`：返回全部产品。
- `GET /loan/products?productId=P_BASIC`：指定产品。
- `POST /loans`：创建贷款草稿。
- `POST /loans/{loanId}/submit`：提交申请并获得决策（调用 risk stub）。
- `GET /loans/{loanId}/contracts`：生成合同快照（stub，返回本地文件路径）。

## TODO
1. 增加配置刷新接口（POST /loan/products/reload）。
2. 带上渠道/用户等级维度的动态费率。
3. 与报告服务对账，确保费率与账务一致。
