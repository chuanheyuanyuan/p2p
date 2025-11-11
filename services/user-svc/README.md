# user-svc (Device API)

实现任务 **T3：设备指纹写入**，提供 `PUT /users/{userId}/device` 接口，用于保存/更新设备指纹、授权信息，并回写最后活跃时间。

## 功能
- 幂等写入：`userId + fingerprint` 唯一，重复上报只更新时间/最后活跃时间。
- 校验渠道：平台、App 版本、是否授权隐私等字段。
- 默认使用 SQLite，后续可替换为 Postgres；提供健康检查 `/healthz`。

## 运行
```bash
cd services/user-svc
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8081
```

## 环境变量
| 变量 | 默认 | 说明 |
| --- | --- | --- |
| `USER_DB_PATH` | `./user.db` | SQLite 路径 |

## 接口示例
```http
PUT /users/U10002/device
Content-Type: application/json

{
  "deviceId": "device-abc",
  "fingerprint": "fp-123",
  "platform": "android",
  "appVersion": "1.0.17",
  "privacyConsent": true,
  "locationConsent": false
}
```

响应：
```json
{
  "userId": "U10002",
  "deviceId": "device-abc",
  "fingerprint": "fp-123",
  "platform": "android",
  "appVersion": "1.0.17",
  "privacyConsent": true,
  "locationConsent": false,
  "lastActiveAt": "2025-01-01T08:00:00Z"
}
```

## Roadmap
1. 与 user-svc 主数据合并，补充 `GET /users/{id}` 等接口。
2. 接入 Redis 做幂等锁及设备风险检测。
3. 将事件推送到 Kafka（`DEVICE_REGISTERED`）。
