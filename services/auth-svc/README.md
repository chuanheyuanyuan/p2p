# auth-svc (OTP)

FastAPI 服务实现任务 T1：`POST /auth/otp`，具备：

- OTP 生成（默认 6 位数字）、5 分钟有效期。
- Redis/内存双模存储；按手机号 15 分钟 3 次速率限制。
- 模拟 SMS/WhatsApp 通道（控制台日志）；后续可替换为真实供应商。

## 配置

通过环境变量或 `.env`（使用 `pydantic-settings`）：

| 变量 | 默认 | 说明 |
| --- | --- | --- |
| `REDIS_URL` | 空（使用内存） | Redis 连接串，如 `redis://localhost:6379/0` |
| `OTP_CODE_LENGTH` | 6 | OTP 位数 |
| `OTP_TTL_SECONDS` | 300 | OTP 有效期（秒） |
| `OTP_RATE_LIMIT_COUNT` | 3 | 单号码窗口内次数 |
| `OTP_RATE_LIMIT_WINDOW_SECONDS` | 900 | 速率限制窗口（秒） |
| `OTP_PROVIDER_CHANNELS` | `sms,whatsapp` | 允许的通道 |

## 运行

```bash
cd services/auth-svc
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

## 接口示例

```http
POST /auth/otp
Content-Type: application/json

{
  "phone": "233555000111",
  "countryCode": "+233",
  "channel": "sms"
}
```

响应

```json
{
  "requestId": "9fe3c5af4d4040ad94150f915e52f679",
  "expireAt": "2025-01-01T12:05:00Z"
}
```

若同一号码 15 分钟内超过 3 次，返回 `429 Too Many Requests`。

```http
POST /auth/token
Content-Type: application/json

{
  "requestId": "9fe3c5af4d4040ad94150f915e52f679",
  "otpCode": "123456",
  "deviceId": "device-abc"
}
```

响应

```json
{
  "accessToken": "eyJhbGciOi...",
  "refreshToken": "eyJhbGciOi...",
  "expiresIn": 900
}
```

## 待办
- 接入真实 SMS 网关（Twilio/Infobip），使用模板变量。
- 在 `OTPRecord` 中记录 deviceId / source，用于风控。
- 与 T2（OTP 校验）对接：验证 `requestId + code` 并签发 JWT。
