# 已导入真题清单

当前本地 SQLite 题库包含 2023、2024 英语一各 4 篇完整阅读，共 **8 篇 / 40 题**。

| 年份 | 试卷 | 篇章 | 题号 | 答案序列 | 状态 |
| --- | --- | --- | --- | --- | --- |
| 2024 | 英语一 | Text 1 | 21–25 | DDABA | 已导入，5 题解析完整 |
| 2024 | 英语一 | Text 2 | 26–30 | ABDCB | 已导入，5 题解析完整 |
| 2024 | 英语一 | Text 3 | 31–35 | BCCDB | 已导入，5 题解析完整 |
| 2024 | 英语一 | Text 4 | 36–40 | ABADB | 已导入，5 题解析完整 |
| 2023 | 英语一 | Text 1 | 21–25 | CBACD | 已导入，5 题解析完整 |
| 2023 | 英语一 | Text 2 | 26–30 | ADBCD | 已导入，5 题解析完整 |
| 2023 | 英语一 | Text 3 | 31–35 | ACAAD | 已导入，5 题解析完整 |
| 2023 | 英语一 | Text 4 | 36–40 | BCABD | 已导入，5 题解析完整 |

## 导入方式

- 阅读训练页 → `添加真题` → PDF 自动导入
- 或使用 CLI：

```bash
python scripts/auto_import.py \
  --pdf ~/2024年考研英语一真题.pdf \
  --year 2024 --exam 英语一 --text-number 2 \
  --answer-key "26-30 ABDCB"
```

题号由 `text_number` 自动映射为 21–25 / 26–30 / 31–35 / 36–40，不再使用 1–5。

## 来源

- 真题 PDF：[Fantasia1999/kaoyanzhenti](https://github.com/Fantasia1999/kaoyanzhenti)
- 2024 答案：[中国考研网 2024 英语一 Text 1–3](http://h.chinakaoyan.com:8080/info/article/id/527401.shtml)、[Text 4](http://www.chinakaoyan.com/info/article/id/527381.shtml)
- 2023 答案：[新东方在线 2023 英语一阅读答案](https://m.koolearn.com/kaoyan/20221224/1578642.html)

## 共享快照

为了让其他成员不用重新跑 PDF + DeepSeek 导入，导入内容额外导出为：

```text
server/data/demo_snapshot.json
```

恢复：

```bash
cd server
python scripts/load_demo.py
# 清空已有 auto_ 导入后重建：
python scripts/load_demo.py --reset
```

快照只包含 `auto_` 文章、句子、题目、选项分析与拆解缓存；基础词库、示例文章、演示单词与练习记录仍由 `seed.py` 生成。更新数据后可运行 `python scripts/export_demo.py` 重新导出。

## 数据边界

- 原始 PDF 不提交 Git；`server/data/app.db` 被忽略。
- 为课程测试，导入全文以 `server/data/demo_snapshot.json` 形式随仓库提供；请勿再分发到公开渠道。
- 解析由 DeepSeek 生成，已校验每题只有一个“正确”选项，且与答案序列一致。
- 答案序列是人工核对后的结果；如果发现某题题干或选项有 OCR 偏差，可直接在题库中修正。
- 当前题库同时保留 2 篇内置示例文章，用于长难句与对话工作流演示；阅读训练页在同年同 Text 存在完整导入版时，优先显示导入版。
