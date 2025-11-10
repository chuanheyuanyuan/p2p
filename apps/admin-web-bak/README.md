# InsCash Admin Web Prototype

静态原型用于分享后台管理系统交互稿，无需构建工具即可打开预览。

## 目录结构

```
apps/admin-web/
├── index.html   # 页面骨架 + sidebar + layout
├── main.js      # 视图切换逻辑与 mock 数据
└── styles.css   # 视觉风格（暗色侧栏 + 白色内容）
```

## 本地预览

### 方式 A：直接打开文件
1. 在 Finder/Explorer 中双击 `index.html`。
2. 浏览器将加载静态资源（在线字体依赖 Google Fonts，若网络受限可注释 `<link>`）。

### 方式 B：本地静态服务器（推荐）
```bash
cd apps/admin-web
python3 -m http.server 4173
```
然后访问 <http://localhost:4173/index.html>。若要分享局域网，可将 `localhost` 换成本机 IP。

## 生产化下一步
- 将整个 `apps/admin-web` 上传到 GitHub 仓库（如 `admin-web-demo`），启用 GitHub Pages 即可生成公网链接。
- 若后续迁移到 React + Ant Design，可以此结构为 UI 参考，逐步组件化每个视图（dashboard、平台每日统计、申请列表、催收列表、案件详情、运营配置、App 升级管理等）。
