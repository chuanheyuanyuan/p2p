# Admin Web · README.vibe.md

> Domain：后台审批/催收/运营配置 · Stack：React + Vite + TypeScript + AntD + React Query + Zustand

## ⚡ Quickstart
1. `cd apps/admin-web`
2. `npm install`
3. 配置 `.env.development` 中的 `VITE_API_BASE_URL`（指向 bff-admin，默认 `http://localhost:8002`）与 `VITE_USE_MOCKS=false`，确保登录/申请列表命中真实后端。
4. `npm run dev -- --host`
5. 浏览器打开 `http://localhost:5173/login`，使用 mock 账号登录。

## 🔐 Auth & RBAC
- 登录页位于 `/login`，接口封装在 `src/services/api.ts` 的 `adminLogin`；成功后通过 Zustand (`src/store/auth.ts`) 持久化 Token/角色。
- 菜单与路由均通过 `RoleGuard` + `navSections` 的 `roles` 配置过滤；无权限时跳转 `/403`。
- 默认 mock 账号：
  - `ops.lead / admin123`：超级管理员，可访问全量菜单；
  - `collector.jr / collector123`：催收坐席，仅可访问催收菜单；
  - `analyst / analyst123`：数据分析，仅可访问报表；
  - `finance.lead / finance123`：财务放/还款与对账菜单；
  - `super.admin / super123`：超级管理员（拥有所有菜单，可用于联调 Finance 模块）。

## 🧱 架构约定
- 所有接口请求集中在 `src/services/api.ts`，统一经 `services/http.ts` 注入 `Authorization` header。
- 数据请求全部通过 React Query（`src/main.tsx` 注入 `QueryClientProvider`），分页/详情等均以 `queryKey` 管理。
- 全局状态采用 Zustand（`src/store/auth.ts`），并提供 `select*` selector 便于组件订阅。
- Mock 数据位于 `src/mocks/data.ts`，若需离线演示可将 `VITE_USE_MOCKS=true`；默认关闭回退，登录与申请列表若失败会直接提示错误。
- Dashboard & Daily Stats（M2）已接入 `fetchDashboardOverview`、`fetchDailyStats`，支持错误提示、Skeleton、导出任务触发（`exportDailyStats`）。
- Applications（M3）接入 `/admin/v1/applications/*`，提供筛选（Zustand 持久化）、导出任务（`exportApplications`），以及客户/审批摘要/历史/凭证多 Tab 详情。
- ApplicationDetail / UserProfile（M4）实现借款人档案四视图，聚合 KYC、设备、隐私授权、渠道轨迹与历史借还信息。
- Finance（M5）新增放款/还款/对账差异三 Tab，支持状态/渠道/日期筛选、失败重试、金额汇总与差异导出，角色受 `finance` & `super_admin` 控制。
- Collections（M6）在 `/collections` 整合催收九模块：案件池 + Drawer 工作台、绩效看板、坐席管理、外呼记录、号码池与语音任务等，全部走 React Query。
- OpsConfig（M7）扩展多 Tab（产品配置、等级策略、渠道链接、消息模板、审批规则、App 版本），在无后端时依赖 mock 数据并支持本地新增/启停模拟。

## 🧪 Testing
- `npm run test` —— Vitest + React Testing Library，当前覆盖 Sidebar RBAC 过滤（`src/components/__tests__/Sidebar.test.tsx`）。
- `vite.config.ts` 已开启 jsdom + jest-dom，并输出 text/lcov 覆盖率。

## 📌 TODO
- ✅ BFF `/admin/v1/auth|applications*` 已和 Admin Web M3 联调：默认直连 bff-admin，mock 仅在 `VITE_USE_MOCKS=true` 时启用。
- 为 Applications/Collections 等关键流程补充更多组件测试与 Story，方便设计 Review。
