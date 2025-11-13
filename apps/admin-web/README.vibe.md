# Admin Web · README.vibe.md

> Domain：后台审批/催收/运营配置 · Stack：React + Vite + TypeScript + AntD + React Query + Zustand

## ⚡ Quickstart
1. `cd apps/admin-web`
2. `npm install`
3. 配置 `.env.development` 中的 `VITE_API_BASE_URL`（指向 bff-admin，默认 `http://localhost:3000`；缺省时自动走 mock）。
4. `npm run dev -- --host`
5. 浏览器打开 `http://localhost:5173/login`，使用 mock 账号登录。

## 🔐 Auth & RBAC
- 登录页位于 `/login`，接口封装在 `src/services/api.ts` 的 `adminLogin`；成功后通过 Zustand (`src/store/auth.ts`) 持久化 Token/角色。
- 菜单与路由均通过 `RoleGuard` + `navSections` 的 `roles` 配置过滤；无权限时跳转 `/403`。
- 默认 mock 账号：
  - `ops.lead / admin123`：超级管理员，可访问全量菜单；
  - `collector.jr / collector123`：催收坐席，仅可访问催收菜单；
  - `analyst / analyst123`：数据分析，仅可访问报表。

## 🧱 架构约定
- 所有接口请求集中在 `src/services/api.ts`，统一经 `services/http.ts` 注入 `Authorization` header。
- 数据请求全部通过 React Query（`src/main.tsx` 注入 `QueryClientProvider`），分页/详情等均以 `queryKey` 管理。
- 全局状态采用 Zustand（`src/store/auth.ts`），并提供 `select*` selector 便于组件订阅。
- Mock 数据位于 `src/mocks/data.ts`，若无真实 BFF 会在 `services/api` 中自动 fallback。

## 🧪 Testing
- `npm run test` —— Vitest + React Testing Library，当前覆盖 Sidebar RBAC 过滤（`src/components/__tests__/Sidebar.test.tsx`）。
- `vite.config.ts` 已开启 jsdom + jest-dom，并输出 text/lcov 覆盖率。

## 📌 TODO
- BFF `/admin/v1/auth/*` 落地后替换 mock 逻辑，并串联真实权限矩阵。
- 为 Applications/Collections 等关键流程补充更多组件测试与 Story，方便设计 Review。
