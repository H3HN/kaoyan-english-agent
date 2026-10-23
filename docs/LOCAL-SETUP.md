# 本地启动与配置教程

本文档面向第一次拉取仓库的成员，覆盖 Web 工作台、FastAPI 后端、测试数据恢复和 DeepSeek 配置。

## 1. 环境要求

| 依赖 | 建议版本 | 检查命令 |
| --- | --- | --- |
| Python | 3.11 / 3.12 | `python3 --version` |
| Node.js | 20+ / 24+ | `node --version` |
| npm | 10+ | `npm --version` |
| Git | 任意较新版本 | `git --version` |

当前验证环境：Python 3.12.12、Node 24.19.0、npm 11.17.0。

## 2. 拉取代码

```bash
git clone https://github.com/H3HN/kaoyan-english-agent.git
cd kaoyan-english-agent
```

## 3. 安装后端依赖

在仓库根目录创建虚拟环境：

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r server/requirements.txt
```

后端依赖：FastAPI、Uvicorn、Pydantic、OpenAI SDK、python-dotenv、pypdf、httpx。

## 4. 配置 LLM（可选）

复制模板：

```bash
cp server/.env.example server/.env
```

编辑 `server/.env`：

```dotenv
LLM_API_KEY=你的 DeepSeek Key
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
```

说明：

- `server/.env` 已在 `.gitignore` 中，**不要提交**。
- 不填 Key 也能启动。题库、阅读训练、长难句页面、已缓存的拆解、单词本、报告都可用。
- 以下能力需要 Key：
  - 新句子的五步拆解（首次约 5–10 秒，之后缓存）
  - PDF 自动导入与选项分析
  - 熟词僻义、复习计划等开放讲解
- `VITE_API_BASE` 只用于生产构建的 API 地址，**不要把 Key 放进任何 `VITE_*` 变量**，否则会被打包进前端。

DeepSeek Key 获取入口：DeepSeek 开放平台 → API Keys。Key 只保存在服务端 `.env`。

## 5. 初始化数据库与测试数据

首次启动 FastAPI 会自动建表并导入基础数据：

- 5,064 条考研词条
- 2 篇示例文章 / 8 句 / 3 题
- 8 条陷阱规则
- 7 个演示单词 / 20 条练习记录

如果要把共享的 8 篇完整真题也恢复：

```bash
cd server
python scripts/load_demo.py
```

如果已有旧的 `auto_` 导入数据，需要清空后恢复：

```bash
python scripts/load_demo.py --reset
```

恢复后的规模：

```text
10 个 passage / 43 题 / 153 句
8 篇导入文章 / 40 题 / 145 句
5 条已缓存句子拆解
7 个演示单词 / 20 条练习记录
```

快照文件：`server/data/demo_snapshot.json`，不含原始 PDF、`.env` 或 `app.db`。

## 6. 启动后端

```bash
cd server
../.venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

或已激活虚拟环境时：

```bash
cd server
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

验证：

```bash
curl http://127.0.0.1:8000/api/health
```

关键字段：

```json
{
  "status": "ok",
  "database": "SQLite",
  "llm_configured": true,
  "llm_model": "deepseek-chat"
}
```

未配置 Key 时 `llm_configured` 为 `false`，属于正常降级。

OpenAPI 文档：http://localhost:8000/docs

## 7. 启动前端

另开一个终端：

```bash
cd web
npm install
npm run dev
```

打开 http://localhost:5173。

Vite 已配置 `/api` 代理到 `http://127.0.0.1:8000`，前端不需要知道后端端口。

生产构建：

```bash
cd web
npm run build
npm run preview
```

如果前后端分开部署：

```bash
VITE_API_BASE=https://your-api.example.com/api npm run build
```

## 8. 启动旧版 Streamlit（可选）

当前主力前端是 React；Streamlit 仅保留为早期 MVP。

```bash
pip install -r kaoyan_agent/requirements.txt
cd kaoyan_agent
../.venv/bin/streamlit run app.py \
  --server.port 8501 \
  --server.address 0.0.0.0 \
  --server.headless true
```

打开 http://localhost:8501。

根目录 `./run.sh` 只启动 Streamlit，不会启动 FastAPI 或 React；需要 Web 工作台时按第 6、7 节分别启动。

## 9. 配置项速查

| 配置 | 位置 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `LLM_API_KEY` | `server/.env` | 空 | DeepSeek Key；空则降级 |
| `LLM_BASE_URL` | `server/.env` | `https://api.deepseek.com/v1` | OpenAI 兼容地址 |
| `LLM_MODEL` | `server/.env` | `deepseek-chat` | 模型名 |
| `VITE_API_BASE` | 前端构建环境 | `/api` | 生产 API 前缀 |
| 数据库 | `server/data/app.db` | 自动创建 | SQLite，已忽略 |
| 后端端口 | 启动命令 | `8000` | Uvicorn |
| 前端端口 | `web/vite.config.ts` | `5173` | Vite |
| Streamlit 端口 | 启动命令 | `8501` | 旧版 |

## 10. 重置与备份

### 只重置用户学习状态

```bash
# 先停止后端
rm -f server/data/app.db server/data/app.db-wal server/data/app.db-shm
# 重新启动后端，自动 seed
```

### 重置后恢复完整题库

```bash
cd server
python scripts/load_demo.py
```

### 备份数据库

```bash
cp server/data/app.db server/data/app.db.bak
```

### 重新导出快照

修改过导入文章后：

```bash
cd server
python scripts/export_demo.py
```

## 11. 常见问题

### `could not read Username for 'https://github.com'`

Git 没有认证。配置 PAT 或 deploy key，不要把 token 写进代码。

### 前端请求 `/api/*` 返回 500 / ECONNREFUSED

FastAPI 没启动，或端口不是 8000。先访问：

```bash
curl http://127.0.0.1:8000/api/health
```

### `llm_configured: false`

- `server/.env` 不存在或位置不对
- `LLM_API_KEY` 为空
- 修改 `.env` 后没有重启 Uvicorn

### DeepSeek 返回 401 / 429

- 401：Key 错误或已失效
- 429：额度/速率限制
- 工具链、题库和阅读训练不受影响，只影响生成类功能

### PDF 导入失败

- 扫描版 PDF 没有文本层，需要 OCR
- URL 需要可公开访问，不能是登录页
- 导入是同步请求，可能需要 20–60 秒
- 本地 PDF 建议用 CLI：

```bash
cd server
python scripts/auto_import.py --pdf ~/2024英语一.pdf \
  --year 2024 --exam 英语一 --text-number 2 \
  --answer-key "26-30 ABDCB"
```

### 端口被占用

```bash
lsof -i :8000
lsof -i :5173
```

### 数据库被锁

停止所有 Uvicorn reloader / 脚本，再重试。SQLite 是单写入者模型。

## 12. 安全与边界

- `.env`、`*.db`、`*.pdf`、日志、截图、构建产物均在 `.gitignore` 中。
- 不要把 `LLM_API_KEY` 发给别人，也不要写进前端变量。
- 仓库是公开仓库，测试快照包含课程用真题全文；不要把它再分发到公开渠道。
- 当前没有登录、多用户隔离和权限系统，不要直接部署到公网多用户环境。
