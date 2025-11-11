# InsCash Admin Web

React + Ant Design 管理后台原型，支持“首页、数据大盘、申请管理、申请详情、用户档案、催收工作台、运营配置、App 升级”等核心视图，并内置 API 封装，可在无真实后端时 fallback 到 mock 数据。

## 快速开始

```bash
cd apps/admin-web
cp .env.development.example .env.development # 若已存在则忽略
npm install
npm run dev -- --host
```
访问 `http://localhost:5173` 即可预览。若要预览打包结果：

```bash
npm run build && npm run preview -- --host
```

## 主要目录

```
src/
├─ App.tsx                # 路由定义
├─ layouts/               # AdminLayout、Sidebar、Topbar
├─ pages/                 # Dashboard、DailyStats、Applications、Collections 等
├─ mocks/data.ts          # 前端 fallback 数据
├─ services/http.ts       # API 请求封装
├─ services/api.ts        # 业务 API（带 mock fallback）
├─ styles/global.less     # 全局样式
└─ constants/             # 导航配置等
```

## 环境变量

- `VITE_API_BASE_URL`：后端 BFF 地址（例如 `http://localhost:3000`）。未配置或请求失败时自动回退到 `mocks/data.ts`。

## 当前特性

- 申请管理：列表筛选、分页、跳转申请详情与用户档案。
- 申请详情：基本信息 + 审批节点 + 历史记录。
- 用户档案：身份信息、风控状态、标签/风险提示。
- 催收工作台：案件列表、Drawer 工作台、PTP/外呼/跟进表单，支持本地记录。
- Dashboard / Daily Stats / Ops Config / App 升级等基础页面。

## 下一步建议

1. 与真实 BFF API 契约对齐，逐步移除 `services/api.ts` 中的 mock fallback。
2. 对 `Collections`、`Applications` 等页面做 `React.lazy` 拆包，降低首屏 bundle。
3. 使用 MSW + Vitest/RTL 为服务层与关键组件补充测试，保障持续演进质量。
4. 接入权限管理（菜单/按钮）与多语言配置，满足正式运营需求。
