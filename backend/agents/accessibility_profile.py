"""Six-question adapter. Reuse questionnaire_rules; do not invent 27 answers."""
from agents.questionnaire_rules import derive_profile

OPTIONS = {
    "goal": ["建立基础认知", "完成课程或备考", "解决实际问题", "提升项目与实践能力", "探索个人兴趣"],
    "foundation": ["零基础", "了解少量概念", "学过基础课程", "能独立完成基础任务", "有相关项目经验"],
    "format": ["图文讲解", "视频演示", "具体案例", "交互练习", "项目实战"],
    "duration": ["15 分钟以内", "15–30 分钟", "30–60 分钟", "60 分钟以上", "根据内容灵活安排"],
    "difficulty": ["理解抽象概念", "补充前置知识", "将知识应用到实践", "保持专注与学习动力", "梳理重点与复习"],
    "feedback": ["先给少量提示，自己尝试", "分步骤讲解思路", "展示完整示例后再练习", "先复习相关基础", "通过小测发现薄弱点"],
}


def validate_answers(answers):
    for key, options in OPTIONS.items():
        values = answers.get(key)
        if not isinstance(values, list) or not values or len(set(values)) != len(values):
            raise ValueError(f"请完成 {key} 问题")
        if any(not isinstance(v, str) or v not in options for v in values):
            raise ValueError(f"{key} 含无效选项")
        if key not in {"format", "difficulty"} and len(values) != 1:
            raise ValueError(f"{key} 只能单选")


def build_accessibility_profile(answers, course, scores):
    validate_answers(answers)
    course = "软件安全技术" if course == "软件安全" else course
    if course not in {"人工智能导论", "软件安全技术"}:
        raise ValueError("请选择支持的课程")
    # Only map semantically equivalent answers. Duration per session is not
    # weekly study time (q17), and self-reported foundation is not coding skill.
    mapped = {
        "q18": [["G"], ["A"], ["B"], ["F"], ["D"]][OPTIONS["goal"].index(answers["goal"][0])],
        "q15": [dict(zip(OPTIONS["format"], "ABCDE"))[v] for v in answers["format"]],
        "q19": [dict(zip(OPTIONS["difficulty"], ["C", "E", "D", "F", "E"]))[v] for v in answers["difficulty"]],
    }
    profile = derive_profile(mapped, course)
    profile["base_level"] = OPTIONS["foundation"].index(answers["foundation"][0]) + 1
    # Preserve an actual pace rating if the original SSVEP questionnaire exists;
    # otherwise the repository's neutral speed default remains in effect.
    if len(scores) == 6:
        profile["learn_speed"] = scores[4]
    focus_min = [15, 25, 45, 60, 25][OPTIONS["duration"].index(answers["duration"][0])]
    summary = (
        f"你希望{answers['goal'][0]}，当前基础为“{answers['foundation'][0]}”，"
        f"偏好{'、'.join(answers['format'])}；重点支持{'、'.join(answers['difficulty'])}。"
        f"建议以{focus_min}分钟为一轮，采用“{answers['feedback'][0]}”的引导方式。"
        "该画像由自评答案与问卷规则生成，基础与节奏可在学习中继续调整。"
    )
    return profile, summary, mapped, focus_min
