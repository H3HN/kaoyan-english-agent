# 研英智学 Agent · FastAPI 后端

前后端分离架构中的领域服务层。负责 SQLite 知识库、四个确定性工具、三类工作流与学习状态持久化。

## 启动

```bash
cd server
../.venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/api/health
- 前端开发服务器通过 Vite proxy 把 `/api` 转发到 8000。

首次启动会初始化 `data/app.db` 并导入：

- 考研词库 5,064 条（公共词库去重并补充内置真题词，来源见 `data/LICENSE-vocabulary`）
- 2023 / 2024 英语一 Text 1 共 8 个句子切片、3 道题
- 8 条陷阱规则
- 7 个演示单词与 20 条练习记录

## 数据表

`syllabus_vocabulary`、`exam_passages`、`exam_sentences`、`exam_questions`、`trap_rules`、`user_vocab_book`、`practice_records`、`agent_runs`。

## 工具

| 工具 | 作用 |
| --- | --- |
| `check_syllabus_vocab` | 大纲属性、等级、真题切片频次、熟词僻义 |
| `search_past_exams` | 真题切片检索与出处标注 |
| `add_to_vocab_book` | 生词 + 语境写入单词本，初始化 SM-2 |
| `record_trap_mistake` | 错题与陷阱类型写入练习记录 |

## 工作流

- `POST /api/workflow/sentence`：词库核查 + 真题检索，返回工具调用链
- `POST /api/workflow/options`：定位 + 陷阱归档 + 出处
- `POST /api/workflow/chat`：意图路由，调用上述工具并返回结构化回答

当前回答由确定性规则与数据库检索生成。`prompts.py` 已固化 LLM 生成层的 System Prompt；接入时在 `workflows.py` 中把工具结果与引用作为上下文传给模型，工具层与检索层保持不变。

## 数据说明

词库来自 [KyleBing/english-vocabulary](https://github.com/KyleBing/english-vocabulary)（BSD-3-Clause），仅用于课程演示；真题切片来自项目内置示例。真题频次为**当前切片语料内的出现次数**，不是 2010–2026 全量统计。当前去重后 5,064 条，接近大纲 5,500 词规模；全量真题需要继续导入，表结构已预留。

## 前端

```bash
cd ../web
npm run dev
# http://localhost:5173
```
