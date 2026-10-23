# 前后端分离架构说明

## 1. 运行拓扑

```
React 19 + Vite (5173)
        │  /api/*
        ▼
Vite dev proxy ──────────────► FastAPI (8000)
                                  │
                                  ├── SQLite: server/data/app.db
                                  ├── tools.py     四个确定性工具
                                  ├── workflows.py 三类工作流
                                  └── seed.py      知识库导入
```

前端不再直接持有领域数据。页面通过 `web/src/lib/api.ts` 请求后端；单词本、答题记录、工具调用链都来自 SQLite。`localStorage` 只作为后端不可用时的离线兜底。

## 2. 领域数据资产

| 资产 | 位置 | 规模 / 说明 |
| --- | --- | --- |
| 考研词库 | `server/data/kaoyan_vocab.txt` | 公共词库去重后 5,064 条，含基础释义 |
| 熟词僻义 | `server/data/rare_meanings.json` | 27 个高频熟词僻义，另补充 6 个常用词 |
| 真题切片 | `server/data/exam_slices.json` | 2023 / 2024 英语一 Text 1，8 句、3 题 |
| 陷阱规则 | `server/seed.py` | 8 条（核心六类 + 过度推理 / 张冠李戴） |
| 用户单词本 | `user_vocab_book` | 生词、语境、SM-2 参数、下次复习 |
| 练习记录 | `practice_records` | 答案、正误、陷阱类型、时间 |

词频说明：`exam_frequency` 是**当前已导入切片语料内的出现次数**，不是 2010–2026 全量统计。这是为了避免伪造数据；导入更多真题后重新执行统计即可。

## 3. 四个工具

实现：`server/tools.py`。每次调用返回 `{tool, args, summary, duration_ms}`，并汇总到工作流的 `tool_trace`。

| 工具 | 输入 | 输出 | 解决的幻觉 |
| --- | --- | --- | --- |
| `check_syllabus_vocab` | 文本或词表 | 大纲属性、等级、释义、熟词僻义、切片频次 | 不知道是否超纲、不知道考频 |
| `search_past_exams` | 查询词 / 语法标签 | 真题切片 + 强制出处 | 举例无来源、编造真题 |
| `add_to_vocab_book` | 单词、语境、出处 | 单词本记录 + 下次复习 | 聊完即忘、不联动软件状态 |
| `record_trap_mistake` | 题目、选项 | 练习记录 + 陷阱类型 | 错题不留痕、薄弱分析无数据 |

## 4. 三类工作流

实现：`server/workflows.py`。

### 长难句

```
sentence_id
  → check_syllabus_vocab(原句)
  → search_past_exams(语法标签)
  → 返回句子、Top 词条、真题出处、tool_trace
```

前端长难句页把 `tool_trace` 渲染成执行记录，把词条渲染成“大纲词核验”卡片，把出处渲染成“真题溯源”卡片，并提供“加入单词本”按钮。

### 选项分析

```
question_id + user_answer
  → search_past_exams(定位句片段)
  → record_trap_mistake(题目, 选项)
  → 返回正误、陷阱类型、出处、tool_trace
```

前端提交答案后调用该接口；后端写入 `practice_records`，前端同时做即时镜像，避免刷新前报告不动。

### 对话

意图路由到句子 / 选项 / 熟词僻义 / 复习计划 / 段落主旨 / 单词本归档。

- “解析这个句子的从句” → 句子工作流 + 词库 + 真题出处
- “address 有哪些熟词僻义” → `check_syllabus_vocab`
- “把 inescapable 加入单词本” → `add_to_vocab_book`，前端收到工具链后刷新单词本
- “安排复习计划” → 读取 `user_vocab_book` 与 `practice_records`

对话采用“工具层 + 生成层”两段式：工具层先查词库、真题与学习状态，DeepSeek 只负责把事实组织成讲解。`tool_trace` 与 `citations` 由后端返回，不经过模型；未配置 Key 或调用失败时自动回退确定性答案。

## 5. API

| 方法 | 路径 | 作用 |
| --- | --- | --- |
| GET | `/api/health` | 服务与知识库统计 |
| GET | `/api/meta` | 词条 / 切片 / 题量 / 陷阱数 |
| GET | `/api/state` | 前端启动时同步单词本与记录 |
| GET | `/api/sentences` | 真题句子切片 |
| GET | `/api/questions` | 题目列表 |
| GET | `/api/knowledge` | 陷阱规则与知识库元数据 |
| POST | `/api/workflow/sentence` | 句子工作流 |
| POST | `/api/workflow/options` | 选项工作流 |
| POST | `/api/workflow/chat` | 对话工作流 |
| GET/POST | `/api/wordbook` | 单词本读取 / 新增 |
| DELETE | `/api/wordbook/{spelling}` | 删除单词 |
| POST | `/api/wordbook/review` | 复习反馈 |
| POST | `/api/records` | 通用答题记录 |
| GET | `/api/report` | 学情聚合 |
| GET | `/api/vocab/search` | 词库检索 |
| POST | `/api/tools/check-vocab` | 工具直连 |
| GET | `/api/tools/search-exams` | 工具直连 |
| GET | `/api/agent/runs` | 最近工作流执行日志 |

OpenAPI 文档：http://localhost:8000/docs

## 5.1 LLM 配置

```bash
cd server
cp .env.example .env
# 填写 LLM_API_KEY / LLM_BASE_URL / LLM_MODEL
```

DeepSeek 示例：

```text
LLM_API_KEY=...
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
```

`server/.env` 已被 `.gitignore` 忽略。前端对话回答中的 `llm_used` 字段表示是否经过 DeepSeek 生成；工具链与出处不依赖该字段。

## 6. 数据库

`server/db.py` 定义 8 张表：

- `syllabus_vocabulary`
- `exam_passages`
- `exam_sentences`
- `exam_questions`
- `trap_rules`
- `user_vocab_book`
- `practice_records`
- `agent_runs`

`user_vocab_book` 预留 `easiness`、`interval_days`、`repetition`，可以继续升级为完整 SM-2；当前复习反馈采用“记住则间隔翻倍、忘记回到 1 天”的简化策略。

## 7. 前端接线点

| 页面 | 接口 | 展示 |
| --- | --- | --- |
| 首页 | `/api/meta` | 真实词条数、切片数、FastAPI 连接状态 |
| 长难句 | `/api/workflow/sentence` | 工具链、词库核验、真题溯源、加入单词本 |
| 选项 | `/api/workflow/options` | 诊断工具链、错题归档、出处 |
| AI 对话 | `/api/workflow/chat` | 结构化回答、Tool Trace、出处 |
| 单词本 | `/api/state`、`/api/wordbook/*` | SQLite 持久化、复习落库 |
| 学习报告 | `/api/state` | 练习记录来自后端并本地聚合 |
| 知识库 | `/api/meta` | 8 条陷阱、真实词条数 |

## 8. 已知边界

- 全量 5,500 大纲词与 2010–2026 全量真题尚未完整导入；当前是可运行的垂直切片。
- 词频只统计当前切片，不能对外宣称“历年考频”。
- 对话有 DeepSeek 生成层，但句子拆解、选项分析仍由确定性规则 + 静态结构展示，LLM 尚未覆盖这两条工作流。
- 无登录与用户隔离；当前是单用户演示库。
- 复习算法是简化 SM-2，不是严格实现。
