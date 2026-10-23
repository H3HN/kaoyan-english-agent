# 研英智学 · 前端工作台

基于 React 19 + Vite + Tailwind CSS v4 的考研英语学习工作台。视觉规范统一为「现代极简学术工作台」：`#F8FAFC` 画布、白色卡片、`#1E293B` 深色 Banner、4px 功能色侧条，以及统一的 12 / 16px 圆角。

## 本地运行

先启动后端（见 `../server/README.md`），再启动前端：

```bash
cd web
npm install
npm run dev
```

打开 `http://localhost:5173`。Vite 已将 `/api` 代理到 `http://127.0.0.1:8000`。

生产环境可用 `VITE_API_BASE=https://your-api.example.com/api npm run build` 指定后端地址。

生产构建：

```bash
npm run build
npm run preview
```

## 页面

| 路由 | 页面 |
| --- | --- |
| `/` | 首页仪表盘 |
| `/sentence` | 长难句拆解 |
| `/options` | 阅读真题训练 |
| `/chat` | AI 对话 |
| `/wordbook` | 单词本与复习 |
| `/report` | 学习报告 |
| `/comparison` | 定制效果对比 |
| `/knowledge` | 领域知识库 |

## 前后端数据流

- 首页调用 `/api/meta` 显示真实的词条、切片与陷阱数量。
- 长难句页调用 `/api/workflow/sentence`，渲染 `tool_trace`、大纲词核验与真题溯源。
- 选项页提交后调用 `/api/workflow/options`，后端写入错题并返回陷阱类型与出处。
- AI 对话调用 `/api/workflow/chat`，应答由 FastAPI 工作流生成；后端不可用时显示错误提示，不再使用写死的本地示例。
- 单词本通过 `/api/state`、`/api/wordbook` 与 SQLite 同步；`localStorage` 仅作离线兜底。

AI 对话调用 `/api/workflow/chat`：FastAPI 先执行工具检索；长难句、选项、核心词、主旨等证据敏感问题直接返回确定性结果，熟词僻义与复习计划等开放讲解才使用 DeepSeek；回答底部标记“DeepSeek 生成”。后端未配置 Key 或调用失败时自动回退。`web/src/lib/api.ts` 是唯一 API 客户端。

## 设计约束

- 全局画布 `bg-slate-50`，内容卡片 `bg-white` + `border-slate-200` + 轻阴影。
- Banner 统一使用 `rounded-2xl bg-slate-800`，白色标题、`text-slate-300` 副标。
- 功能卡片左侧 4px 色条：蓝（句子）、绿（选项）、紫（AI）、黄（单词）、青（知识）。
- 指标行宽屏固定 4 列；内容区使用 12 列 / 2 列栅格。
- 所有可点击卡片具备 `hover:-translate-y-0.5 hover:shadow-md` 过渡。
