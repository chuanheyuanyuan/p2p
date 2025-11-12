# Notify Service · README.vibe.md

> Domain: 多渠道通知

## ⚡ Quickstart
1. `cd services/notify-svc && python3 -m venv .venv && source .venv/bin/activate`
2. `pip install -r requirements.txt`
3. `uvicorn app.main:app --reload --port 8009`

## 🔌 API
- `POST /notifications/send` —— 必须带 `X-Idempotency-Key`，提交模板、变量与受众，立即生成发送任务；成功会触发 `NOTIFY_ENQUEUED` 与 `NOTIFY_SENT`（或 `NOTIFY_FAILED`）。
- `GET /notifications/tasks/{taskId}` —— 查询任务状态、正文、错误信息，方便排障。
- 健康检查：`GET /healthz`

## 🧰 目录说明
- `app/config.py`：服务配置、模板路径。
- `app/template_engine.py`：加载 `templates/catalog.json` 并用 Jinja2 渲染，强校验 `requiredVariables`。
- `app/channel_client.py`：Mock 通道适配器，检查渠道所需的受众字段。
- `app/repository.py`：SQLite (`notify.db`) 持久化任务，与幂等键 (`idempotency_key`) 关联。

## 👀 调试提示
- `sample.http` 覆盖“放款成功”“到期提醒”两个模板调用，可直接在 VS Code 里回放。
- 事件日志：`NOTIFY_ENQUEUED`/`NOTIFY_SENT`/`NOTIFY_FAILED`/`CHANNEL_DISPATCHED`，用于串联 loan/payment → notify → collection 链路。
- 若携带 `sendAt` 且在未来，任务状态为 `SCHEDULED`，待后续调度器消费（当前版本暂未实现）。
