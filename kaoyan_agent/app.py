import streamlit as st
import json
import pandas as pd

from agent import KaoyanAgent
from sentence_parser import format_parse_result
from question_analyzer import format_analysis_result
from wordbook import (
    add_word, remove_word, get_all_words, get_review_words,
    review_word, get_wordbook_stats, get_review_schedule, is_outline_word
)
from study_record import (
    get_all_records, get_accuracy_by_type, get_overall_stats,
    get_weakness_types, generate_study_suggestions, get_recent_records
)
from sample_data import SAMPLE_QUESTIONS, QUESTION_TYPES, TRAP_TYPES, METHODLOGY
from config import LLM_API_KEY, LLM_MODEL

st.set_page_config(
    page_title="考研英语智学Agent",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "agent" not in st.session_state:
    st.session_state.agent = KaoyanAgent()
if "current_passage" not in st.session_state:
    st.session_state.current_passage = ""
if "current_question" not in st.session_state:
    st.session_state.current_question = None

agent = st.session_state.agent

st.sidebar.markdown("## 📚 考研英语智学Agent")
st.sidebar.markdown(f"**模型**：{agent.model}")
if LLM_API_KEY:
    st.sidebar.success("✅ LLM已连接")
else:
    st.sidebar.warning("⚠️ 演示模式（未配置API Key）")

page = st.sidebar.radio("功能导航", [
    "📊 首页仪表盘",
    "📖 阅读分析（长难句拆解）",
    "🎯 选项陷阱分析",
    "📝 单词本与复习",
    "📈 学习报告",
    "⚡ 定制效果对比",
    "📚 领域知识库"
])


def show_dashboard():
    st.title("📊 首页仪表盘")
    st.markdown("### 懂考研英语的AI辅导老师")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("内置真题", f"{len(SAMPLE_QUESTIONS)}篇")
    with col2:
        from sample_data import OUTLINE_WORDS
        st.metric("大纲词汇", f"{len(OUTLINE_WORDS)}词")
    with col3:
        wb_stats = get_wordbook_stats()
        st.metric("单词本", f"{wb_stats['total']}词")
    with col4:
        overall = get_overall_stats()
        st.metric("已练习", f"{overall['total']}题")

    st.markdown("---")
    st.markdown("### 🎯 核心功能")
    features = [
        ("📖 长难句拆解", "导入真题，逐句拆解长难句（找主干→剥离从句→划分修饰→翻译）"),
        ("🎯 选项陷阱分析", "识别题型+标注陷阱类型（偷换概念/扩大范围/正反混淆等）+给出解题步骤"),
        ("📝 单词本与复习", "自动提取生词→判断大纲词→艾宾浩斯复习计划"),
        ("📈 学习报告", "统计各题型正确率，分析薄弱环节，生成备考建议")
    ]
    for title, desc in features:
        st.markdown(f"**{title}**：{desc}")

    st.markdown("---")
    st.markdown("### ⚡ 定制效果")
    st.info("通用模型只会直译，不会讲考研出题陷阱。本Agent按考研辅导范式解析——"
            "拆长难句、识陷阱、管生词，让备考更高效。")
    if st.button("查看定制前后对比 →", key="go_compare"):
        st.session_state._page = "对比"
        st.rerun()


def show_reading_analysis():
    st.title("📖 阅读分析 — 长难句拆解")
    st.markdown("导入真题阅读文章，Agent逐句拆解长难句")

    tab1, tab2 = st.tabs(["选择内置真题", "自定义导入"])

    with tab1:
        q_options = [f"{q['year']}年{q['exam_type']} Text {q['text_number']}" for q in SAMPLE_QUESTIONS]
        selected = st.selectbox("选择真题", q_options)
        if st.button("加载并分析", key="load_builtin"):
            idx = q_options.index(selected)
            q = SAMPLE_QUESTIONS[idx]
            st.session_state.current_passage = q["passage"]
            st.session_state.current_question = q
            _do_analysis(q["passage"])

    with tab2:
        custom_text = st.text_area("粘贴阅读文章", height=200, placeholder="粘贴考研英语阅读文章全文...")
        if st.button("分析文章", key="analyze_custom") and custom_text:
            st.session_state.current_passage = custom_text
            _do_analysis(custom_text)

    if st.session_state.current_passage and not st.session_state.get("_analyzed", False):
        st.markdown("### 📄 当前文章")
        st.text_area("文章内容", st.session_state.current_passage, height=200, disabled=True)
        if st.button("拆解长难句", key="parse_current"):
            _do_analysis(st.session_state.current_passage)


def _do_analysis(passage):
    st.session_state._analyzed = True
    with st.spinner("Agent正在分析文章..."):
        result = agent.analyze_passage(passage)

    st.success(result["summary"])

    st.markdown("### 📄 原文")
    st.write(passage)

    st.markdown("### 📖 逐句拆解结果")
    for sent in result["sentences"]:
        with st.expander(f"第{sent['index']}句 {'⚠️长难句' if sent['is_long'] else '✅简单句'}", expanded=sent["is_long"]):
            st.markdown(f"**原文**：{sent['original']}")
            if sent["is_long"]:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**主干**")
                    st.code(sent["main_clause"])
                    st.markdown("**从句**")
                    for sc in sent["sub_clauses"]:
                        st.markdown(f"- {sc}")
                with col2:
                    st.markdown("**修饰**")
                    for mod in sent["modifiers"]:
                        st.markdown(f"- {mod}")
                    st.markdown("**语法点**")
                    for gp in sent["grammar_points"]:
                        st.markdown(f"- {gp}")
            st.markdown(f"**翻译**：{sent['translation']}")

    if result["extracted_words"]:
        st.markdown("### 📝 自动提取的生词")
        st.write("以下生词已自动加入单词本：")
        cols = st.columns(5)
        for i, w in enumerate(result["extracted_words"]):
            cols[i % 5].markdown(f"- {w} {'✅大纲词' if is_outline_word(w) else '⚠️非大纲词'}")


def show_option_analysis():
    st.title("🎯 选项陷阱分析")
    st.markdown("分析每个选项的陷阱类型，给出解题步骤")

    if not st.session_state.current_question:
        q_options = [f"{q['year']}年{q['exam_type']} Text {q['text_number']}" for q in SAMPLE_QUESTIONS]
        selected = st.selectbox("选择真题", q_options, key="opt_select")
        if st.button("加载题目", key="load_q"):
            idx = q_options.index(selected)
            st.session_state.current_question = SAMPLE_QUESTIONS[idx]
            st.rerun()
        return

    q = st.session_state.current_question
    st.markdown(f"### {q['year']}年{q['exam_type']} Text {q['text_number']}")
    st.markdown("#### 文章")
    st.write(q["passage"])

    for question in q["questions"]:
        st.markdown(f"---\n#### 第{question['number']}题")
        st.markdown(f"**题目**：{question['content']}")
        for label in ["A", "B", "C", "D"]:
            st.markdown(f"- **{label}.** {question['options'][label]}")

        if st.button(f"分析选项 →", key=f"analyze_q{question['number']}"):
            with st.spinner("Agent正在分析选项陷阱..."):
                result = agent.analyze_question(question, q["passage"])

            st.markdown("##### 分析结果")
            analysis = result["analysis"]
            st.markdown(f"**题型**：{analysis['question_type']}")
            st.markdown(f"**定位**：{analysis['location']}")

            st.markdown("##### 选项分析")
            for label in ["A", "B", "C", "D"]:
                info = analysis["options_analysis"].get(label, {})
                trap = info.get("trap_type", "")
                expl = info.get("explanation", "")
                if trap == "正确":
                    st.success(f"✅ **{label}.** {question['options'][label]}\n\n→ {trap}：{expl}")
                else:
                    st.error(f"❌ **{label}.** {question['options'][label]}\n\n→ {trap}：{expl}")

            st.markdown("##### 解题步骤")
            for i, step in enumerate(analysis["steps"], 1):
                st.markdown(f"{i}. {step}")

            st.markdown("##### 做题记录")
            user_ans = st.radio("你的答案是？", ["A", "B", "C", "D"], key=f"user_ans_{question['number']}", horizontal=True)
            if st.button("提交答案", key=f"submit_{question['number']}"):
                from study_record import add_record
                record = add_record(
                    question_id=f"{q['id']}_q{question['number']}",
                    question_type=analysis["question_type"],
                    user_answer=user_ans,
                    correct_answer=question["correct_answer"],
                    passage_id=q["id"]
                )
                if record["is_correct"]:
                    st.success(f"✅ 回答正确！正确答案：{question['correct_answer']}")
                else:
                    st.error(f"❌ 回答错误。正确答案：{question['correct_answer']}，你选了：{user_ans}")


def show_wordbook():
    st.title("📝 单词本与复习")

    wb_stats = get_wordbook_stats()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("总词数", wb_stats["total"])
    with col2:
        st.metric("大纲词", wb_stats["outline_count"])
    with col3:
        st.metric("待复习", wb_stats["due_count"])
    with col4:
        st.metric("平均掌握度", f"{wb_stats['avg_familiarity']*100:.0f}%")

    tab1, tab2, tab3 = st.tabs(["📋 全部单词", "🔄 今日复习", "➕ 添加单词"])

    with tab1:
        words = get_all_words()
        if not words:
            st.info("单词本为空，去阅读文章自动提取生词吧！")
        else:
            df_data = []
            for w in words:
                df_data.append({
                    "单词": w["spelling"],
                    "大纲词": "✅" if w["is_outline"] else "❌",
                    "来源": w["source"][:20] if w["source"] else "",
                    "复习次数": w["review_count"],
                    "掌握度": f"{w['familiarity']*100:.0f}%",
                    "下次复习": w["next_review_time"][:10]
                })
            st.dataframe(pd.DataFrame(df_data), use_container_width=True)

            word_to_remove = st.selectbox("选择要删除的单词", [""] + [w["spelling"] for w in words])
            if word_to_remove and st.button("删除"):
                success, msg = remove_word(word_to_remove)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    with tab2:
        due_words = get_review_words()
        if not due_words:
            st.success("🎉 今日无待复习单词！")
        else:
            st.markdown(f"**{len(due_words)}个单词待复习**")
            for w in due_words:
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.markdown(f"**{w['spelling']}** {'✅大纲词' if w['is_outline'] else ''}")
                        st.caption(f"已复习{w['review_count']}次 | 掌握度{w['familiarity']*100:.0f}%")
                    with col2:
                        if st.button("✅ 记住了", key=f"rem_{w['spelling']}"):
                            review_word(w["spelling"], True)
                            st.rerun()
                    with col3:
                        if st.button("❌ 没记住", key=f"for_{w['spelling']}"):
                            review_word(w["spelling"], False)
                            st.rerun()

    with tab3:
        new_word = st.text_input("输入单词")
        source = st.text_input("来源（可选）", placeholder="如：2024年真题Text1")
        if st.button("添加") and new_word:
            success, msg = add_word(new_word, source)
            if success:
                st.success(msg)
                st.markdown("**艾宾浩斯复习计划**：")
                for s in get_review_schedule(new_word):
                    st.markdown(f"- {s}")
            else:
                st.warning(msg)


def show_study_report():
    st.title("📈 学习报告")

    overall = get_overall_stats()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("总练习题数", overall["total"])
    with col2:
        st.metric("正确数", overall["correct"])
    with col3:
        st.metric("正确率", f"{overall['accuracy']*100:.0f}%")

    st.markdown("---")
    st.markdown("### 各题型正确率")
    accuracy = get_accuracy_by_type()
    if not accuracy:
        st.info("暂无练习记录，去选项分析页面做题吧！")
    else:
        df_data = []
        for qtype, info in accuracy.items():
            df_data.append({
                "题型": qtype,
                "题数": info["total"],
                "正确": info["correct"],
                "正确率": f"{info['accuracy']*100:.0f}%"
            })
        st.dataframe(pd.DataFrame(df_data), use_container_width=True)

        try:
            import plotly.express as px
            chart_data = pd.DataFrame([
                {"题型": qtype, "正确率": info["accuracy"]}
                for qtype, info in accuracy.items()
            ])
            fig = px.bar(chart_data, x="题型", y="正确率", title="各题型正确率",
                         color="正确率", color_continuous_scale="RdYlGn",
                         range_y=[0, 1])
            st.plotly_chart(fig, use_container_width=True)
        except ImportError:
            st.bar_chart(pd.DataFrame({qtype: [info["accuracy"]] for qtype, info in accuracy.items()}))

    st.markdown("---")
    st.markdown("### 薄弱环节")
    weak = get_weakness_types()
    if weak:
        for qtype, acc in weak:
            st.error(f"⚠️ {qtype}：正确率仅{acc*100:.0f}%，需要加强训练")
    else:
        if overall["total"] > 0:
            st.success("✅ 各题型正确率均达标")

    st.markdown("---")
    st.markdown("### 📝 备考建议")
    suggestions = generate_study_suggestions()
    for s in suggestions:
        st.markdown(f"- {s}")

    st.markdown("---")
    st.markdown("### 最近练习记录")
    recent = get_recent_records(10)
    if recent:
        df_data = []
        for r in recent:
            df_data.append({
                "题型": r["question_type"],
                "你的答案": r["user_answer"],
                "正确答案": r["correct_answer"],
                "结果": "✅" if r["is_correct"] else "❌",
                "时间": r["time"][:16]
            })
        st.dataframe(pd.DataFrame(df_data), use_container_width=True)


def show_comparison():
    st.title("⚡ 定制效果对比")
    st.markdown("### 通用模型 vs 领域定制Agent")

    comparison = agent.compare_customization()

    st.markdown("#### 场景一：长难句拆解")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### 🔴 通用模型")
        st.warning(comparison["场景1_长难句拆解"]["通用模型"])
    with col2:
        st.markdown("##### 🟢 定制Agent（五步拆解法）")
        agent_result = comparison["场景1_长难句拆解"]["定制Agent"]
        st.success(f"**第一步 找主干**：{agent_result['第一步_找主干']}")
        st.success(f"**第二步 剥离从句**：{agent_result['第二步_剥离从句']}")
        st.success(f"**第三步 划分修饰**：{agent_result['第三步_划分修饰']}")
        st.success(f"**第四步 逐层翻译**：{agent_result['第四步_逐层翻译']}")
        st.success(f"**第五步 语法点**：{', '.join(agent_result['第五步_语法点'])}")

    st.markdown("---\n#### 场景二：选项陷阱分析")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### 🔴 通用模型")
        st.warning(comparison["场景2_选项分析"]["通用模型"])
    with col2:
        st.markdown("##### 🟢 定制Agent")
        agent_result = comparison["场景2_选项分析"]["定制Agent"]
        st.success(f"**题型**：{agent_result['题型']}")
        st.success(f"**定位**：{agent_result['定位']}")
        for label in ["选项A", "选项B", "选项C", "选项D"]:
            st.success(f"**{label}**：{agent_result[label]}")
        st.success(f"**解题步骤**：{agent_result['解题步骤']}")

    st.markdown("---\n#### 场景三：生词管理")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### 🔴 通用模型")
        st.warning(comparison["场景3_生词管理"]["通用模型"])
    with col2:
        st.markdown("##### 🟢 定制Agent（复习闭环）")
        agent_result = comparison["场景3_生词管理"]["定制Agent"]
        for key, val in agent_result.items():
            if isinstance(val, list):
                st.success(f"**{key}**：{', '.join(val)}")
            else:
                st.success(f"**{key}**：{val}")

    st.markdown("---\n### 💡 定制方法总结")
    st.markdown("""
    | 定制维度 | 具体方法 |
    |---------|---------|
    | 领域知识库 | 考研大纲词汇5500词 + 历年真题 + 题型方法论 + 语法体系 + 陷阱分类 |
    | 提示词设计 | 角色设定为考研辅导老师，按五步法拆解，按五步法分析选项 |
    | 工具调用 | 长难句拆解工具 + 陷阱识别工具 + 单词本工具 + 艾宾浩斯复习工具 |
    | 流程编排 | 导入→拆解→分析→提取→复习→报告，形成完整学习闭环 |
    """)


def show_knowledge_base():
    st.title("📚 领域知识库")
    kb_info = agent.get_knowledge_base_info()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("大纲词汇数", kb_info["outline_words_count"])
        st.metric("内置真题数", kb_info["sample_questions_count"])
    with col2:
        st.metric("题型分类", f"{len(kb_info['question_types'])}种")
        st.metric("陷阱类型", f"{len(kb_info['trap_types'])}种")

    tab1, tab2, tab3 = st.tabs(["题型方法论", "陷阱类型", "拆解方法"])

    with tab1:
        for qtype, desc in kb_info["question_types"].items():
            st.markdown(f"**{qtype}**：{desc}")

    with tab2:
        for trap, desc in kb_info["trap_types"].items():
            st.markdown(f"**{trap}**：{desc}")

    with tab3:
        for method_name, steps in kb_info["methodology"].items():
            st.markdown(f"#### {method_name}")
            for step in steps:
                st.markdown(f"- {step}")


if page == "📊 首页仪表盘":
    show_dashboard()
elif page == "📖 阅读分析（长难句拆解）":
    show_reading_analysis()
elif page == "🎯 选项陷阱分析":
    show_option_analysis()
elif page == "📝 单词本与复习":
    show_wordbook()
elif page == "📈 学习报告":
    show_study_report()
elif page == "⚡ 定制效果对比":
    show_comparison()
elif page == "📚 领域知识库":
    show_knowledge_base()