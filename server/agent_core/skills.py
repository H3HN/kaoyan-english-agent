"""Skill catalog exposed to the LLM intent router.

The model is allowed to choose only these names. It never emits free-form
actions or code; arguments are validated by the router before dispatch.
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class SkillSpec(BaseModel):
    name: str
    description: str
    examples: list[str] = Field(default_factory=list)
    args: dict[str, str] = Field(default_factory=dict)


SKILLS: list[SkillSpec] = [
    SkillSpec(
        name="flashcard_review",
        description="开始背单词、刷闪卡、复习今日词、到期词。必须直接打开闪卡。",
        examples=["我要开始背诵今日单词", "开始背单词", "抽查一下到期词", "复习今天的单词"],
    ),
    SkillSpec(
        name="reader_home",
        description="想泛读/读长文但没有提供正文，进入泛读首页选文章。",
        examples=["我要泛读一篇长文", "进入泛读", "打开泛读功能", "我想读点外刊"],
    ),
    SkillSpec(
        name="reader",
        description="用户提供了一篇长英文正文，要求泛读。正文由后端从消息中提取。",
        examples=["泛读这篇：<长文>", "带我读这篇长文章：..."],
    ),
    SkillSpec(
        name="listening_home",
        description="想练听力/听写，但没有提供正文，进入听力首页选素材。",
        examples=["进入听力", "我想练听力", "打开听写"],
    ),
    SkillSpec(
        name="listening",
        description="用户提供了英文正文，要求听力听写。正文由后端提取。",
        examples=["用这段做听力听写：...", "听写这篇：..."],
    ),
    SkillSpec(
        name="writing_home",
        description="想写作/作文但没有提供作文正文，进入写作首页选题目。",
        examples=["进入写作", "我想练作文", "打开写作批改"],
    ),
    SkillSpec(
        name="writing",
        description="用户提供了一篇英文作文，或明确给出作文标题，要求写作/批改。",
        examples=["批改这篇作文：...", "我想进行标题为Love的写作训练", "以 Love 为题写一篇作文"],
        args={"prompt": "writing title if explicitly provided"},
    ),
    SkillSpec(
        name="studio_home",
        description="进入 Studio/学习首页、选择训练模式。",
        examples=["进入Studio", "开始学习", "打开长难句首页", "继续学习"],
    ),
    SkillSpec(
        name="reading_home",
        description="进入阅读训练首页选真题，不自动选文章。",
        examples=["进入阅读", "开始做阅读", "打开阅读训练"],
    ),
    SkillSpec(
        name="vocab_home",
        description="进入词汇/词本首页。",
        examples=["进入词汇", "打开词本", "去记忆舱"],
    ),
    SkillSpec(
        name="summarize_content",
        description="概括当前画布文章/段落/听力的主旨、结构、大意。需要当前 active_content。",
        examples=["概括一下主旨大意", "这篇文章讲了什么", "梳理文章结构", "总结一下"],
    ),
    SkillSpec(
        name="recommend",
        description="让 Agent 推荐今天读哪一篇真题阅读。",
        examples=["今天读什么", "推荐一篇阅读", "带我去做一篇真题"],
    ),
    SkillSpec(
        name="practice",
        description="让 Agent 直接给一道题做，而不是讲方法。",
        examples=["随便给我一道题", "来一道阅读题", "练一道题"],
    ),
    SkillSpec(
        name="schedule",
        description="生成/安排学习计划。",
        examples=["安排三天学习计划", "根据错题排计划", "今天怎么安排"],
    ),
    SkillSpec(
        name="diagnosis",
        description="分析当前错题、选项陷阱、错因。",
        examples=["分析这道题", "我错在哪", "剖析四个选项"],
    ),
    SkillSpec(
        name="similar_sentences",
        description="找同款语法/同结构句子。",
        examples=["找同款语法句", "有没有同结构句子"],
    ),
    SkillSpec(
        name="explain_sentence",
        description="解释当前句的语法/从句/为什么这样写。",
        examples=["为什么这里用that", "这个从句是什么", "解释一下当前句"],
    ),
    SkillSpec(
        name="sentence",
        description="拆解一个句子或定位当前句。若提供了英文句子，正文由后端提取。",
        examples=["拆解这句话：...", "分析这个长难句", "五步拆解 current sentence"],
    ),
    SkillSpec(
        name="word_insight",
        description="查一个单词/短语的释义、词性、熟词僻义。参数 word 为英文词。",
        examples=["novel 是什么意思", "解析单词 novel", "看看这个词"],
        args={"word": "English word or phrase"},
    ),
    SkillSpec(
        name="save_sentence",
        description="把当前句子保存到句库。",
        examples=["收藏这句", "保存这个句子"],
    ),
    SkillSpec(
        name="explain_word_in_sentence",
        description="解释当前句中的某个词。",
        examples=["这个单词在句子里什么意思", "它的词性是什么"],
    ),
    SkillSpec(
        name="add_word_to_sentence",
        description="把当前句中的词加入生词本并保存原句。",
        examples=["把这个词加入生词本", "收了这个词"],
    ),
    SkillSpec(
        name="batch_vocab",
        description="把当前段落/文章/提供的文本里的生词整理入库。",
        examples=["把这篇里的生词整理入库", "提取本段核心词"],
    ),
    SkillSpec(
        name="rare_words",
        description="查当前句/选区的熟词僻义。",
        examples=["这句里的熟词僻义", "查一下熟词僻义"],
    ),
    SkillSpec(
        name="clarify",
        description="用户想学习，但当前没有对应功能/信息不足；简短说明可选项，不要长篇解释。",
        examples=["我要练口语", "我要学翻译", "帮我学英语"],
    ),
    SkillSpec(
        name="generic",
        description="普通英语知识问答或闲聊，不需要打开画布或执行工具。",
        examples=["什么是同位语", "你好", "虚拟语气怎么用"],
    ),
]

SKILL_NAMES = {skill.name for skill in SKILLS}
SKILLS_BY_NAME = {skill.name: skill for skill in SKILLS}


def catalog_for_prompt() -> list[dict]:
    return [skill.model_dump() for skill in SKILLS]
