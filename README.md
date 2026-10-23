# 考研英语智学 Agent · 学习平台

面向考研英语一/英语二的阅读训练工作台，仓库包含两个前端形态：

| 目录 | 形态 | 说明 |
| --- | --- | --- |
| `kaoyan_agent/` | Streamlit 单体应用 | 早期可运行 MVP，含规则拆解、单词本、学习记录与 LLM 对话降级 |
| `server/` | FastAPI + SQLite | 领域知识库、四个工具、三类工作流、PDF 自动导入与学习状态持久化 |
| `web/` | React 19 + Vite + Tailwind CSS v4 | 统一设计系统的新前端工作台，覆盖 8 个页面，通过 `/api` 调用后端 |

## 启动 Streamlit 版本

```bash
cd kaoyan_agent
pip install -r requirements.txt
streamlit run app.py
# http://localhost:8501
```

或使用仓库根目录的 `./run.sh`。

## 启动后端（FastAPI）

```bash
cd server
../.venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000 --reload
# http://localhost:8000/docs
```

首次启动自动初始化 `server/data/app.db`，导入 5,064 条考研词库、8 个真题句子切片、3 道题、8 条陷阱规则与演示学习数据。

## 启动 React 工作台

```bash
cd web
npm install
npm run dev
# http://localhost:5173
```

Vite 已配置 `/api` 代理到 `http://127.0.0.1:8000`。

生产构建：

```bash
cd web
npm run build
npm run preview
```

## 设计系统

- 画布：`#F8FAFC`；卡片：`#FFFFFF` + `#E2E8F0` 边框 + 轻阴影。
- 深色 Banner：`#1E293B`，16px 圆角；普通卡片 12px；按钮 / Tag 8px。
- 功能色：蓝（拆解）、绿（正确 / 定制）、青（知识）、黄（复习）、紫（AI / 练习）、红（错误 / 对照）。
- 左侧 240px 固定导航，右侧自适应工作区；指标行宽屏 4 列。
- 所有功能卡片带 4px 左色条，悬浮时 `-translate-y-0.5` + `shadow-md`。

## 前后端边界

- 前端：只负责页面、交互与工具链可视化；通过 `web/src/lib/api.ts` 调用 `/api`。
- 后端：SQLite 领域库、`check_syllabus_vocab` / `search_past_exams` / `add_to_vocab_book` / `record_trap_mistake` 四个工具，以及句子 / 选项 / 对话三类工作流。
- 状态：单词本与答题记录写入 SQLite；前端仍保留 `localStorage` 作为离线兜底。
- 生成层：工具检索与状态写入是确定性的；证据敏感问题直接返回工具结果，只有开放讲解使用 DeepSeek，`tool_trace` 与真题出处始终来自工具层，LLM 失败自动回退。
- 真题导入：选项分析页「添加真题」支持手动录入，也支持公开 PDF URL 自动抽取文章/题目/选项；答案序列可选，未提供时标记为 AI 推断。
- 数据：公共考研词库（BSD-3-Clause，去重后 5,064 条）与项目内置真题切片；频次是**当前切片语料内的出现次数**，不是 2010–2026 全量统计。

## 文档

- [前后端分离架构](docs/ARCHITECTURE.md)
- [答辩演示与追问准备](docs/DEFENSE-NOTES.md)
- [后端运行说明](server/README.md)
- [前端运行说明](web/README.md)

## 团队

福大智联 · 2026 秋软工实践。
