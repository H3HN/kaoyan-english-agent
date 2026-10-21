# 考研英语智学Agent

> 懂考研英语的AI辅导老师 — 福大智联团队出品

## 项目简介

面向备考考研英语一/英语二的在校大学生，构建领域专业化智能体，提供：

- **长难句逐句拆解**：找主干→剥离从句→划分修饰→逐层翻译→标注语法点
- **选项陷阱分析**：识别题型+标注陷阱类型（偷换概念/扩大范围/正反混淆/无中生有/过于绝对）+给出解题步骤
- **生词自动管理**：提取生词→判断大纲词→艾宾浩斯复习计划
- **学习记录分析**：统计各题型正确率，识别薄弱环节，生成备考建议

## 快速开始

```bash
cd kaoyan_agent
pip install -r requirements.txt
streamlit run app.py
```

浏览器自动打开 `http://localhost:8501`

> 未配置API Key时自动进入**演示模式**，可体验全部功能界面（AI回复为预设Mock）。

## 配置LLM（可选）

复制 `.env.example` 为 `.env`，填入API Key：

```bash
cp .env.example .env
```

推荐使用 **Kimi**（长文本能力强，适合阅读理解）：

```
LLM_API_KEY=你的Kimi_API_Key
LLM_BASE_URL=https://api.moonshot.cn/v1
LLM_MODEL=moonshot-v1-8k
```

或使用 **DeepSeek**：

```
LLM_API_KEY=你的DeepSeek_API_Key
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
```

或使用 **OpenAI GPT**：

```
LLM_API_KEY=你的OpenAI_API_Key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-3.5-turbo
```

## 功能页面

| 页面 | 功能 |
|------|------|
| 📊 首页仪表盘 | 总览统计 |
| 📖 阅读分析 | 导入真题，逐句拆解长难句 |
| 🎯 选项陷阱分析 | 分析选项陷阱，给出解题步骤，记录答题 |
| 📝 单词本与复习 | 单词管理+艾宾浩斯复习+今日复习 |
| 📈 学习报告 | 正确率统计+薄弱分析+备考建议 |
| ⚡ 定制效果对比 | 通用模型vs定制Agent对比展示 |
| 📚 领域知识库 | 题型方法论+陷阱分类+拆解方法 |

## 技术栈

| 层次 | 技术 |
|------|------|
| 前端 | Streamlit |
| Agent | LLM API（Kimi/GPT/DeepSeek）+ 提示词 + 工具调用 |
| NLP | 规则引擎（长难句拆解+陷阱识别） |
| 数据 | JSON持久化（单词本+学习记录） |
| 可视化 | Plotly |

## 项目结构

```
kaoyan_agent/
├── app.py              # Streamlit主应用（7个页面）
├── agent.py            # Agent核心（LLM+工具+流程编排）
├── config.py           # 配置管理
├── prompts.py          # 提示词模板
├── sentence_parser.py  # 长难句拆解引擎
├── question_analyzer.py# 选项陷阱分析引擎
├── wordbook.py         # 单词本+艾宾浩斯复习
├── study_record.py     # 学习记录+薄弱分析
├── sample_data.py      # 示例真题+大纲词汇+方法论
├── requirements.txt
├── .env.example
└── data/               # 运行时数据（自动生成）
    ├── wordbook.json
    └── study_records.json
```

## 领域知识来源

| 知识类型 | 来源 |
|---------|------|
| 考研大纲词汇 | 教育部考试中心大纲（约5500词） |
| 历年真题 | 2005-2025考研英语一/二真题 |
| 题型方法论 | 唐迟阅读/田静语法等名师方法论 |
| 长难句语法体系 | 田静《句句真研》五步拆解法 |
| 命题陷阱分类 | 考研辅导经验总结 |

## 团队

**福大智联** — 福州大学2026秋软工实践团队（13人）

## License

MIT