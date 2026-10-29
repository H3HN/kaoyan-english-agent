import streamlit as st
import pandas as pd

from agent import KaoyanAgent
from wordbook import (
    add_word, remove_word, get_all_words, get_review_words,
    review_word, get_wordbook_stats, get_review_schedule, is_outline_word
)
from study_record import (
    get_accuracy_by_type, get_overall_stats,
    get_weakness_types, generate_study_suggestions, get_recent_records
)
from sample_data import SAMPLE_QUESTIONS, QUESTION_TYPES, TRAP_TYPES, METHODLOGY
from config import LLM_API_KEY, LLM_MODEL

st.set_page_config(page_title="考研英语智学Agent", page_icon="📚", layout="wide")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700;900&display=swap');
*{font-family:'Noto Sans SC',sans-serif;}
.stApp{background:#f7f8fc;}
.main .block-container{padding-top:1.5rem;max-width:1150px;}
h1{font-size:1.7rem!important;font-weight:900!important;color:#1e293b!important;margin:0!important;}
h2{font-size:1.25rem!important;font5;font-weight:700!important;color:#1e293b!important;}
h3{font-size:1.05rem!important;font-weight:700!important;color:#334155!important;}

.hero{background:linear-gradient(135deg,#1e293b 0%,#334155 50%,#475569 100%);border-radius:16px;padding:30px 40px;color:#fff;margin-bottom:24px;box-shadow:0 4px 20px rgba(30,41,59,0.15);}
.hero h1{color:#fff!important;}
.hero p{color:#94a3b8;margin:8px 0 0 0;font-size:0.95rem;}

.card{background:#fff;border-radius:12px;padding:20px;box-shadow:0 2px 12px rgba(0,0,0,0.05);margin:6px 0;}
.card-blue{border-left:4px solid #3b82f6;}
.card-green{border-left:4px solid #10b981;}
.card-orange{border-left:4px solid #f59e0b;}
.card-red{border-left:4px solid #ef4444;}
.card-purple{border-left:4px solid #8b5cf6;}

.stat-card{background:#fff;border-radius:12px;padding:20px;text-align:center;box-shadow:0 2px 12px rgba(0,0,0,0.05);border-top:4px solid #3b82f6;transition:all 0.3s;}
.stat-card .val{font-size:2rem;font-weight:900;color:#1e293b;line-height:1.2;}
.stat-card .lbl{font-size:0.82rem;color:#64748b;margin-top:6px;font-weight:500;}

.tag{display:inline-block;padding:3px 12px;border-radius:6px;font-size:0.78rem;font-weight:600;}
.tag-green{background:#d1fae5;color:#065f46;}
.tag-red{background:#fee2e2;color:#991b1b;}
.tag-blue{background:#dbeafe;color:#1e40af;}
.tag-orange{background:#fef3c7;color:#92400e;}
.tag-purple{background:#ede9fe;color:#5b21b6;}
.tag-slate{background:#e2e8f0;color:#334155;}

.step{background:#f8fafc;border-left:4px solid #3b82f6;padding:12px 16px;border-radius:0 8px 8px 0;margin:6px 0;font-size:0.92rem;color:#475569;}
.step b{color:#1e293b;}

.opt-correct{background:#d1fae5;border-left:4px solid #10b981;border-radius:0 10px 10px 0;padding:14px 18px;margin:6px 0;}
.opt-wrong{background:#fee2e2;border-left:4px solid #ef4444;border-radius:0 10px 10px 0;padding:14px 18px;margin:6px 0;}

.section{font-size:1.15rem;font-weight:700;color:#1e293b;margin:24px 0 12px 0;padding-bottom:8px;border-bottom:2px solid #e2e8f0;}

div.stButton>button{border-radius:8px;font-weight:600;transition:all 0.2s;}
div.stButton>button:hover{transform:translateY(-1px);box-shadow:0 4px 12px rgba(59,130,246,0.2);}
div.stButton>button[kind="primary"]{background:#1e293b;border-color:#1e293b;}

.progress-bar{background:#e2e8f0;border-radius:8px;height:12px;overflow:hidden;}
.progress-fill{height:12px;border-radius:8px;transition:width 0.5s;}

.chat-msg{padding:14px 18px;border-radius:14px;margin:8px 0;max-width:85%;font-size:0.95rem;line-height:1.6;}
.chat-user{background:#1e293b;color:#fff;margin-left:auto;text-align:right;}
.chat-bot{background:#fff;border:1px solid #e2e8f0;color:#1e293b;box-shadow:0 1px 6px rgba(0,0,0,0.04);}

.feature-card{background:#fff;border-radius:12px;padding:22px;box-shadow:0 2px 12px rgba(0,0,0,0.05);border-left:4px solid #3b82f6;transition:all 0.3s;cursor:pointer;}
.feature-card:hover{transform:translateY(-3px);box-shadow:0 8px 24px rgba(0,0,0,0.08);}
.feature-card .ftitle{font-size:1.05rem;font-weight:700;color:#1e293b;}
.feature-card .fdesc{font-size:0.85rem;color:#64748b;margin-top:8px;line-height:1.5;}

.compare-left{background:#fee2e2;border-radius:12px;padding:20px;border:1px solid #fecaca;}
.compare-right{background:#d1fae5;border-radius:12px;padding:20px;border:1px solid #a7f3d0;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

if "agent" not in st.session_state:
    st.session_state.agent = KaoyanAgent()
if "current_passage" not in st.session_state:
    st.session_state.current_passage = ""
if "current_question" not in st.session_state:
    st.session_state.current_question = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

agent = st.session_state.agent

with st.sidebar:
    st.markdown("### 考研英语智学Agent")
    st.caption(f"模型: {LLM_MODEL if LLM_API_KEY else '演示模式'}")
    if LLM_API_KEY:
        st.markdown('<span class="tag tag-green">已连接</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="tag tag-orange">未连接</span>', unsafe_allow_html=True)
    st.markdown("---")
    page = st.radio("", ["首页","长难句拆解","选项分析","AI对话","单词本","学习报告","定制对比","知识库"])
    st.markdown("---")
    st.caption("福大智联 · 2026秋软工实践")


def hero(title, subtitle):
    st.markdown(f'<div class="hero"><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)

def stat_cards(data):
    cols = st.columns(len(data))
    for col, val, lbl, color in zip(cols, data, [d[2] for d in data], [d[3] for d in data]):
        pass
    for i, (col, val, lbl, color) in enumerate(zip(cols, data, [d[1] for d in data], [d[2] for d in data])):
        col.markdown(f'<div class="stat-card" style="border-top-color:{color};"><div class="val">{val}</div><div class="lbl">{lbl}</div></div>', unsafe_allow_html=True)


def show_dashboard():
    from sample_data import OUTLINE_WORDS
    wb = get_wordbook_stats()
    ov = get_overall_stats()

    hero("考研英语智学Agent", "长难句拆解 · 选项陷阱分析 · 智能单词管理 · 个性化备考建议")

    c1,c2,c3,c4 = st.columns(4)
    for col,val,lbl,color in [(c1,f"{len(SAMPLE_QUESTIONS)}","内置真题","#3b82f6"),(c2,f"{len(OUTLINE_WORDS)}","大纲词汇","#10b981"),(c3,f"{wb['total']}","单词本","#f59e0b"),(c4,f"{ov['total']}","已练习","#8b5cf6")]:
        col.markdown(f'<div class="stat-card" style="border-top-color:{color};"><div class="val">{val}</div><div class="lbl">{lbl}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section">核心功能</div>', unsafe_allow_html=True)
    features = [
        ("长难句拆解", "导入真题文章，逐句按五步法拆解：找主干→剥离从句→划分修饰→翻译→标注语法点", "#3b82f6"),
        ("选项陷阱分析", "识别题型，标注陷阱类型（偷换概念/扩大范围/正反混淆等），给出完整解题步骤", "#10b981"),
        ("AI对话", "直接向Agent提问任何考研英语问题，获得名师级辅导回复", "#8b5cf6"),
        ("单词本与复习", "自动提取生词，判断大纲词，按艾宾浩斯遗忘曲线安排科学复习", "#f59e0b"),
    ]
    cols = st.columns(2)
    for i,(title,desc,color) in enumerate(features):
        cols[i%2].markdown(f'<div class="feature-card" style="border-left-color:{color};"><div class="ftitle">{title}</div><div class="fdesc">{desc}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section">定制效果预览</div>', unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    c1.markdown('<div class="compare-left"><b style="color:#991b1b;">通用模型</b><br><br>直接翻译句子<br>泛泛说"选C"<br>翻译完就结束</div>', unsafe_allow_html=True)
    c2.markdown('<div class="compare-right"><b style="color:#065f46;">定制Agent</b><br><br>五步法拆解长难句<br>标注陷阱类型+解题步骤<br>生词提取→复习闭环</div>', unsafe_allow_html=True)

    if wb["due_count"] > 0:
        st.markdown(f'<div class="card card-orange" style="margin-top:16px;"><span class="tag tag-orange">待办</span> <b>{wb["due_count"]}</b> 个单词待复习，去「单词本」完成今日复习</div>', unsafe_allow_html=True)


def show_reading():
    hero("长难句拆解", "导入文章，Agent逐句按五步法系统拆解")
    tab1, tab2 = st.tabs(["内置真题", "自定义导入"])
    with tab1:
        opts = [f"{q['year']} {q['exam_type']} Text{q['text_number']}（{len(q['questions'])}题）" for q in SAMPLE_QUESTIONS]
        c1,c2 = st.columns([4,1])
        idx = c1.selectbox("选择真题", range(len(opts)), format_func=lambda i: opts[i])
        c2.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        if c2.button("加载分析", type="primary", use_container_width=True):
            q = SAMPLE_QUESTIONS[idx]
            st.session_state.current_passage = q["passage"]
            st.session_state.current_question = q
            _analyze(q["passage"])
    with tab2:
        txt = st.text_area("粘贴阅读文章", height=160, placeholder="Paste passage here...")
        if st.button("分析文章", type="primary") and txt:
            st.session_state.current_passage = txt
            _analyze(txt)


def _analyze(passage):
    with st.spinner("Agent分析中..."):
        r = agent.analyze_passage(passage)
    st.markdown(f'<div class="card card-green"><span class="tag tag-green">{r["summary"]}</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="section">原文</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="card" style="line-height:1.8;">{passage}</div>', unsafe_allow_html=True)
    st.markdown('<div class="section">逐句拆解</div>', unsafe_allow_html=True)
    for s in r["sentences"]:
        if s["is_long"]:
            with st.expander(f"第{s['index']}句 · 长难句", expanded=True):
                st.markdown(f'<div class="card" style="background:#fffbeb;border:1px solid #fde68a;"><b>原文</b><br>{s["original"]}</div>', unsafe_allow_html=True)
                c1,c2 = st.columns(2)
                c1.markdown('<div class="card card-blue"><b style="color:#1e40af;">第一步 · 找主干</b></div>', unsafe_allow_html=True)
                c1.code(s["main_clause"], language="text")
                c2.markdown('<div class="card card-purple"><b style="color:#5b21b6;">第五步 · 语法点</b></div>', unsafe_allow_html=True)
                for gp in s["grammar_points"]:
                    c2.markdown(f'<span class="tag tag-purple">{gp}</span>', unsafe_allow_html=True)
                if s["sub_clauses"]:
                    st.markdown('<div class="card card-blue"><b style="color:#1e40af;">第二步 · 剥离从句</b></div>', unsafe_allow_html=True)
                    for sc in s["sub_clauses"]: st.markdown(f'<div class="step">{sc}</div>', unsafe_allow_html=True)
                if s["modifiers"]:
                    st.markdown('<div class="card card-blue"><b style="color:#1e40af;">第三步 · 划分修饰</b></div>', unsafe_allow_html=True)
                    for m in s["modifiers"]: st.markdown(f'<div class="step">{m}</div>', unsafe_allow_html=True)
                st.markdown('<div class="card card-green"><b style="color:#065f46;">第四步 · 翻译</b></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="card" style="background:#ecfdf5;color:#065f46;">{s["translation"]}</div>', unsafe_allow_html=True)
        else:
            with st.expander(f"第{s['index']}句"):
                st.markdown(f'{s["original"]}')
                st.caption(f"翻译: {s['translation']}")
    if r["extracted_words"]:
        st.markdown('<div class="section">自动提取生词</div>', unsafe_allow_html=True)
        cols = st.columns(8)
        for i,w in enumerate(r["extracted_words"]):
            tag = "green" if is_outline_word(w) else "orange"
            label = "大纲" if is_outline_word(w) else "非大纲"
            cols[i%8].markdown(f'<div class="card" style="text-align:center;padding:10px;"><b style="color:#1e293b;">{w}</b><br><span class="tag tag-{tag}">{label}</span></div>', unsafe_allow_html=True)


def show_options():
    hero("选项陷阱分析", "识别题型 · 标注陷阱 · 给出解题步骤")
    if not st.session_state.current_question:
        opts = [f"{q['year']} {q['exam_type']} Text{q['text_number']}" for q in SAMPLE_QUESTIONS]
        idx = st.selectbox("选择真题", range(len(opts)), format_func=lambda i: opts[i])
        if st.button("加载题目", type="primary"):
            st.session_state.current_question = SAMPLE_QUESTIONS[idx]
            st.rerun()
        return
    q = st.session_state.current_question
    st.markdown(f'<div class="card card-blue"><b style="font-size:1.1rem;">{q["year"]} {q["exam_type"]} · Text {q["text_number"]}</b></div>', unsafe_allow_html=True)
    with st.expander("查看原文"): st.write(q["passage"])
    for question in q["questions"]:
        st.markdown(f'<div class="card card-blue"><h3>第{question["number"]}题</h3><p style="font-size:1.05rem;color:#334155;">{question["content"]}</p></div>', unsafe_allow_html=True)
        for label in ["A","B","C","D"]:
            st.markdown(f'<div class="card" style="padding:10px 16px;"><b style="color:#3b82f6;">{label}.</b> {question["options"][label]}</div>', unsafe_allow_html=True)
        if st.button("分析选项陷阱", key=f"a{question['number']}", type="primary"):
            with st.spinner("Agent分析中..."):
                r = agent.analyze_question(question, q["passage"])
            a = r["analysis"]
            st.markdown(f'<div class="card card-blue"><span class="tag tag-blue">{a["question_type"]}</span> <span class="tag tag-slate">{a["location"]}</span></div>', unsafe_allow_html=True)
            st.markdown('<div class="section">选项分析</div>', unsafe_allow_html=True)
            for label in ["A","B","C","D"]:
                info = a["options_analysis"].get(label, {})
                trap = info.get("trap_type","")
                expl = info.get("explanation","")
                cls = "opt-correct" if trap == "正确" else "opt-wrong"
                tcls = "tag-green" if trap == "正确" else "tag-red"
                st.markdown(f'<div class="{cls}"><b style="color:#1e293b;">{label}. {question["options"][label]}</b><br><span class="tag {tcls}">{trap}</span> <span style="color:#475569;">{expl}</span></div>', unsafe_allow_html=True)
            st.markdown('<div class="section">解题步骤</div>', unsafe_allow_html=True)
            for i,step in enumerate(a["steps"],1):
                st.markdown(f'<div class="step"><b>步骤 {i}</b> · {step}</div>', unsafe_allow_html=True)
            st.markdown("---")
            ua = st.radio("你的答案", ["A","B","C","D"], key=f"u{question['number']}", horizontal=True)
            if st.button("提交答案", key=f"s{question['number']}", type="primary"):
                from study_record import add_record
                rec = add_record(f"{q['id']}_q{question['number']}", a["question_type"], ua, question["correct_answer"], q["id"])
                if rec["is_correct"]:
                    st.markdown(f'<div class="card card-green" style="text-align:center;"><b style="color:#065f46;font-size:1.1rem;">回答正确</b><br>正确答案: {question["correct_answer"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="card card-red" style="text-align:center;"><b style="color:#991b1b;font-size:1.1rem;">回答错误</b><br>正确答案: {question["correct_answer"]} | 你的答案: {ua}</div>', unsafe_allow_html=True)


def show_chat():
    hero("AI对话", "直接向Agent提问任何考研英语问题")
    for msg in st.session_state.chat_history:
        cls = "chat-user" if msg["role"] == "user" else "chat-bot"
        st.markdown(f'<div class="chat-msg {cls}">{msg["content"]}</div>', unsafe_allow_html=True)
    with st.form("chat_form", clear_on_submit=True):
        c1,c2 = st.columns([6,1])
        user_input = c1.text_input("问Agent...", placeholder="如: 帮我拆解这个长难句 The study shows that...")
        submitted = c2.form_submit_button("发送", type="primary", use_container_width=True)
    if submitted and user_input:
        st.session_state.chat_history.append({"role":"user","content":user_input})
        with st.spinner("思考中..."):
            resp = agent.chat(user_input)
        st.session_state.chat_history.append({"role":"bot","content":resp})
        st.rerun()
    st.markdown('<div class="section">快捷提问</div>', unsafe_allow_html=True)
    qc1,qc2,qc3 = st.columns(3)
    def quick_ask(prompt):
        st.session_state.chat_history.append({"role":"user","content":prompt})
        with st.spinner("思考中..."):
            resp = agent.chat(prompt)
        st.session_state.chat_history.append({"role":"bot","content":resp})
        st.rerun()
    if qc1.button("拆解长难句示例"): quick_ask("请拆解: The technology that once seemed confined to science fiction has become an inescapable part of our daily lives.")
    if qc2.button("解释偷换概念"): quick_ask("请解释考研英语中'偷换概念'这种选项陷阱")
    if qc3.button("主旨题解题技巧"): quick_ask("主旨题的解题技巧是什么？")


def show_wordbook():
    hero("单词本与复习", "艾宾浩斯遗忘曲线 · 科学复习 · 掌握度追踪")
    wb = get_wordbook_stats()
    c1,c2,c3,c4 = st.columns(4)
    for col,val,lbl,color in [(c1,wb["total"],"总词数","#3b82f6"),(c2,wb["outline_count"],"大纲词","#10b981"),(c3,wb["due_count"],"待复习","#f59e0b"),(c4,f"{wb['avg_familiarity']*100:.0f}%","平均掌握度","#8b5cf6")]:
        col.markdown(f'<div class="stat-card" style="border-top-color:{color};"><div class="val">{val}</div><div class="lbl">{lbl}</div></div>', unsafe_allow_html=True)
    tab1,tab2,tab3 = st.tabs(["全部单词","今日复习","添加单词"])
    with tab1:
        words = get_all_words()
        if not words:
            st.markdown('<div class="card" style="text-align:center;color:#94a3b8;padding:40px;">单词本为空<br>去「长难句拆解」阅读文章自动提取生词</div>', unsafe_allow_html=True)
        else:
            for w in words:
                fc = "#10b981" if w["familiarity"]>0.7 else ("#f59e0b" if w["familiarity"]>0.3 else "#ef4444")
                c1,c2,c3 = st.columns([3,2,1])
                c1.markdown(f'<div class="card" style="padding:12px 16px;"><b style="color:#1e293b;font-size:1.05rem;">{w["spelling"]}</b> <span class="tag tag-{"green" if w["is_outline"] else "orange"}">{"大纲词" if w["is_outline"] else "非大纲"}</span><br><span style="font-size:0.8rem;color:#94a3b8;">来源: {w["source"][:20] if w["source"] else "手动添加"}</span></div>', unsafe_allow_html=True)
                c2.markdown(f'<div class="card" style="padding:12px;"><div class="progress-bar"><div class="progress-fill" style="background:{fc};width:{w["familiarity"]*100}%;"></div></div><div style="text-align:center;font-size:0.8rem;color:#64748b;margin-top:4px;">掌握度 {w["familiarity"]*100:.0f}%</div></div>', unsafe_allow_html=True)
                c3.markdown(f'<div class="card" style="padding:12px;text-align:center;"><span style="font-size:0.8rem;color:#64748b;">复习</span><br><b style="color:#1e293b;">{w["review_count"]}</b><br><span style="font-size:0.75rem;color:#94a3b8;">{w["next_review_time"][:10]}</span></div>', unsafe_allow_html=True)
            st.markdown("---")
            rm = st.selectbox("删除单词", [""]+[w["spelling"] for w in words])
            if rm and st.button("确认删除"): remove_word(rm); st.rerun()
    with tab2:
        due = get_review_words()
        if not due:
            st.markdown('<div class="card card-green" style="text-align:center;padding:40px;"><b style="color:#065f46;font-size:1.1rem;">今日无待复习单词</b></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="card card-orange"><span class="tag tag-orange">{len(due)}个单词待复习</span></div>', unsafe_allow_html=True)
            for w in due:
                c1,c2,c3 = st.columns([4,1,1])
                c1.markdown(f'<div class="card" style="padding:12px 16px;"><b style="color:#1e293b;">{w["spelling"]}</b> <span class="tag tag-{"green" if w["is_outline"] else "orange"}">{"大纲" if w["is_outline"] else ""}</span><br><span style="font-size:0.8rem;color:#94a3b8;">已复习{w["review_count"]}次 · 掌握{w["familiarity"]*100:.0f}%</span></div>', unsafe_allow_html=True)
                if c2.button("记住", key=f"r{w['spelling']}"): review_word(w["spelling"],True); st.rerun()
                if c3.button("没记住", key=f"f{w['spelling']}"): review_word(w["spelling"],False); st.rerun()
    with tab3:
        c1,c2 = st.columns([3,2])
        nw = c1.text_input("单词", placeholder="如: ubiquitous")
        src = c2.text_input("来源", placeholder="如: 2024真题Text1")
        if st.button("添加", type="primary") and nw:
            ok,msg = add_word(nw,src)
            if ok:
                st.markdown(f'<div class="card card-green"><span class="tag tag-green">{msg}</span></div>', unsafe_allow_html=True)
                st.markdown('<div class="section">艾宾浩斯复习计划</div>', unsafe_allow_html=True)
                for s in get_review_schedule(nw): st.markdown(f'<div class="step">{s}</div>', unsafe_allow_html=True)
            else: st.warning(msg)


def show_report():
    hero("学习报告", "正确率统计 · 薄弱环节分析 · 个性化备考建议")
    ov = get_overall_stats()
    c1,c2,c3 = st.columns(3)
    acc_c = "#10b981" if ov["accuracy"]>=0.7 else ("#f59e0b" if ov["accuracy"]>=0.5 else "#ef4444")
    for col,val,lbl,color in [(c1,ov["total"],"总练习题数","#3b82f6"),(c2,ov["correct"],"正确数","#10b981"),(c3,f"{ov['accuracy']*100:.0f}%","正确率",acc_c)]:
        col.markdown(f'<div class="stat-card" style="border-top-color:{color};"><div class="val">{val}</div><div class="lbl">{lbl}</div></div>', unsafe_allow_html=True)
    acc = get_accuracy_by_type()
    if not acc:
        st.markdown('<div class="card" style="text-align:center;color:#94a3b8;padding:40px;">暂无练习记录<br>去「选项分析」做题开始记录</div>', unsafe_allow_html=True)
        return
    st.markdown('<div class="section">各题型正确率</div>', unsafe_allow_html=True)
    for qt,info in acc.items():
        a = info["accuracy"]
        fc = "#10b981" if a>=0.7 else ("#f59e0b" if a>=0.5 else "#ef4444")
        c1,c2 = st.columns([1,3])
        c1.markdown(f'<div class="card" style="padding:8px 12px;"><b style="color:#1e293b;">{qt}</b><br><span style="font-size:0.8rem;color:#64748b;">{info["correct"]}/{info["total"]}题</span></div>', unsafe_allow_html=True)
        c2.markdown(f'<div style="padding:10px 0;"><div class="progress-bar"><div class="progress-fill" style="background:{fc};width:{a*100}%;"></div></div><div style="text-align:right;font-size:0.85rem;color:{fc};font-weight:700;margin$ margin-top:4px;">{a*100:.0f}%</div></div>', unsafe_allow_html=True)
    try:
        import plotly.express as px
        df = pd.DataFrame([{"题型":k,"正确率":v["accuracy"]} for k,v in acc.items()])
        fig = px.bar(df, x="题型", y="正确率", color="正确率", color_continuous_scale=[[0,"#ef4444"],[0.5,"#f59e0b"],[1,"#10b981"]], range_y=[0,1])
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    except: pass
    weak = get_weakness_types()
    if weak:
        st.markdown('<div class="section">薄弱环节</div>', unsafe_allow_html=True)
        for qt,a in weak: st.markdown(f'<div class="card card-red"><span class="tag tag-red">{qt}</span> <span style="color:#991b1b;">正确率 {a*100:.0f}%，需加强训练</span></div>', unsafe_allow_html=True)
    else:
        if ov["total"]>0: st.markdown('<div class="card card-green"><span class="tag tag-green">各题型均达标</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="section">备考建议</div>', unsafe_allow_html=True)
    for s in generate_study_suggestions(): st.markdown(f'<div class="step">{s}</div>', unsafe_allow_html=True)
    recent = get_recent_records(8)
    if recent:
        st.markdown('<div class="section">最近练习</div>', unsafe_allow_html=True)
        for r in recent:
            ri = "tag-green" if r["is_correct"] else "tag-red"
            rs = "正确" if r["is_correct"] else "错误"
            st.markdown(f'<div class="card" style="padding:10px 16px;display:flex;justify-content:space-between;"><div><span class="tag tag-blue">{r["question_type"]}</span> <span style="color:#475569;">选{r["user_answer"]} | 答案{r["correct_answer"]}</span></div><div><span class="tag {ri}">{rs}</span> <span style="font-size:0.8rem;color:#94a3b8;">{r["time"][:16]}</span></div></div>', unsafe_allow_html=True)


def show_comparison():
    hero("定制效果对比", "通用模型 vs 领域定制Agent · 展示定制的价值")
    cmp = agent.compare_customization()
    for sk, title in [("场景1_长难句拆解","场景一 · 长难句拆解"),("场景2_选项分析","场景二 · 选项陷阱分析"),("场景3_生词管理","场景三 · 生词管理闭环")]:
        st.markdown(f'<div class="section">{title}</div>', unsafe_allow_html=True)
        c1,c2 = st.columns(2)
        c1.markdown(f'<div class="compare-left"><b style="color:#991b1b;font-size:1.05rem;">通用模型</b><br><br>{cmp[sk]["通用模型"]}</div>', unsafe_allow_html=True)
        ar = cmp[sk]["定制Agent"]
        items = "".join(f'<div class="step"><b style="color:#065f46;">{k}</b>: {", ".join(v) if isinstance(v,list) else v}</div>' for k,v in ar.items())
        c2.markdown(f'<div class="compare-right"><b style="color:#065f46;font-size:1.05rem;">定制Agent</b><br>{items}</div>', unsafe_allow_html=True)
    st.markdown('<div class="section">定制方法</div>', unsafe_allow_html=True)
    methods = [
        ("领域知识库", "大纲词汇5500词 + 历年真题 + 题型方法论 + 语法体系 + 陷阱分类", "#3b82f6"),
        ("提示词设计", "角色设定为考研辅导老师，按五步法拆解，按五步法分析选项", "#10b981"),
        ("工具调用", "长难句拆解 + 陷阱识别 + 单词本 + 艾宾浩斯复习", "#f59e0b"),
        ("流程编排", "导入→拆解→分析→提取→复习→报告，完整学习闭环", "#8b5cf6"),
    ]
    cols = st.columns(2)
    for i,(title,desc,color) in enumerate(methods):
        cols[i%2].markdown(f'<div class="feature-card" style="border-left-color:{color};"><div class="ftitle">{title}</div><div class="fdesc">{desc}</div></div>', unsafe_allow_html=True)


def show_kb():
    hero("领域知识库", "考研英语领域知识体系 · Agent定制的根基")
    kb = agent.get_knowledge_base_info()
    c1,c2,c3,c4 = st.columns(4)
    for col,val,lbl,color in [(c1,kb["outline_words_count"],"大纲词汇","#3b82f6"),(c2,kb["sample_questions_count"],"内置真题","#10b981"),(c3,len(kb["question_types"]),"题型分类","#f59e0b"),(c4,len(kb["trap_types"]),"陷阱类型","#ef4444")]:
        col.markdown(f'<div class="stat-card" style="border-top-color:{color};"><div class="val">{val}</div><div class="lbl">{lbl}</div></div>', unsafe_allow_html=True)
    tab1,tab2,tab3 = st.tabs(["题型方法论","陷阱类型","拆解方法"])
    with tab1:
        for k,v in kb["question_types"].items(): st.markdown(f'<div class="card card-blue"><span class="tag tag-blue">{k}</span> <span style="color:#475569;">{v}</span></div>', unsafe_allow_html=True)
    with tab2:
        for k,v in kb["trap_types"].items(): st.markdown(f'<div class="card card-red"><span class="tag tag-red">{k}</span> <span style="color:#475569;">{v}</span></div>', unsafe_allow_html=True)
    with tab3:
        for name,steps in kb["methodology"].items():
            st.markdown(f'<div class="card card-purple"><b style="color:#5b21b6;font-size:1.05rem;">{name}</b></div>', unsafe_allow_html=True)
            for s in steps: st.markdown(f'<div class="step">{s}</div>', unsafe_allow_html=True)


PAGES = {"首页":show_dashboard,"长难句拆解":show_reading,"选项分析":show_options,"AI对话":show_chat,"单词本":show_wordbook,"学习报告":show_report,"定制对比":show_comparison,"知识库":show_kb}
PAGES[page]()