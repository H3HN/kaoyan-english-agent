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

## 真题自动导入

`POST /api/exams/auto-import` 支持：

- 公开 PDF URL：`{"url": "...pdf", "year": 2024, "exam_type": "英语一", "text_number": 1, "answer_key": "21-25 BCDAB"}`
- 原始文本：把 `url` 换成 `text`
- 自动抽取 Text N 的文章、5 道题与选项；题号按 21–25 / 26–30 / 31–35 / 36–40 自动映射
- 提供答案序列时按序列覆盖；未提供时使用模型推断，返回 `answer_source=inferred`
- 批量生成选项陷阱分析；结果写入 SQLite

命令行入口：

```bash
python scripts/auto_import.py --url https://example.com/2024.pdf \
  --year 2024 --exam 英语一 --text-number 1 --answer-key 21-25BCDAB
```

也可以 `--pdf` 传本地 PDF，或 `--text-file` 传纯文本。

> 不内置、不再分发真题 PDF。PDF 由使用者提供；请遵守来源站点的版权与使用条款。推荐用于已获授权的公开教学 PDF。

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

对话采用“工具层 + 生成层”两段式：

1. 工具层先查大纲词、真题切片与单词本；
2. 证据敏感意图（长难句拆解、选项分析、单词本归档）直接返回确定性结果，不让模型改写事实；
3. 开放讲解意图（熟词僻义、复习计划）才交给 DeepSeek 组织语言；
4. `tool_trace` 与 `citations` 由后端返回，不经过模型；
5. Key 未配置或调用失败时，自动回退到确定性答案。

配置 `server/.env`：

```text
LLM_API_KEY=...
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
```

`prompts.py` 固化生成层 System Prompt，`llm.py` 负责调用与 JSON 清洗。

## 数据说明

词库来自 [KyleBing/english-vocabulary](https://github.com/KyleBing/english-vocabulary)（BSD-3-Clause），仅用于课程演示；真题切片来自项目内置示例。真题频次为**当前切片语料内的出现次数**，不是 2010–2026 全量统计。当前去重后 5,064 条，接近大纲 5,500 词规模；全量真题需要继续导入，表结构已预留。

## 前端

```bash
cd ../web
npm run dev
# http://localhost:5173
```


## 自动导入真题

支持三种输入：公开 PDF URL、本地 PDF、纯文本。后端会抽取 Text N，调用 DeepSeek 结构化文章/题目/答案，并批量生成选项分析。

```bash
# 公开 PDF
python scripts/auto_import.py --url https://example.com/2024.pdf \
  --year 2024 --exam 英语一 --text-number 1 --answer-key BCDAB

# 本地 PDF
python scripts/auto_import.py --pdf ~/2024英语一.pdf \
  --year 2024 --text-number 1

# 纯文本
python scripts/auto_import.py --text-file passage.txt \
  --year 2024 --text-number 1
```

说明：

- 不提供答案序列时，模型会推断答案，返回 `answer_source=inferred`，需要在页面核对。
- 不内置、不再分发真题 PDF；URL 与文件由使用者提供。
- 自动导入依赖 DeepSeek，`server/.env` 中必须配置 `LLM_API_KEY`。
