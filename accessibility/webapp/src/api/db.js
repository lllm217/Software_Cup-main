// 数据库接口（Mock）。以后接真实后端时，只替换这里的实现，不改函数签名与调用方式。

export const SUBJECTS = ['软件安全', '人工智能导论']

// 与后端 agents/accessibility_profile.py::OPTIONS 顺序一一对应：
// goal / foundation / format / duration / difficulty / feedback。
// SSVEP 打分 1~5 分即对应每题的第 1~5 个选项。
export const PROFILE_QUESTIONS = [
  { id: 'goal', text: '你本次学习最主要的目标是什么？', options: ['建立基础认知', '完成课程或备考', '解决实际问题', '提升项目与实践能力', '探索个人兴趣'] },
  { id: 'foundation', text: '你对所选科目的基础掌握情况如何？', options: ['零基础', '了解少量概念', '学过基础课程', '能独立完成基础任务', '有相关项目经验'] },
  { id: 'format', text: '你更愿意使用哪些学习资料？', options: ['图文讲解', '视频演示', '具体案例', '交互练习', '项目实战'] },
  { id: 'duration', text: '你通常希望每次学习持续多久？', options: ['15 分钟以内', '15–30 分钟', '30–60 分钟', '60 分钟以上', '根据内容灵活安排'] },
  { id: 'difficulty', text: '学习时你最希望获得哪些方面的帮助？', options: ['理解抽象概念', '补充前置知识', '将知识应用到实践', '保持专注与学习动力', '梳理重点与复习'] },
  { id: 'feedback', text: '遇到难题时，你更希望获得怎样的引导？', options: ['先给少量提示，自己尝试', '分步骤讲解思路', '展示完整示例后再练习', '先复习相关基础', '通过小测发现薄弱点'] },
]

export function dbGetSubjects() {
  return [...SUBJECTS]
}

export function dbGetProfileQuestions() {
  return [...PROFILE_QUESTIONS]
}

export function dbSaveProfileAnswer(userId, questionId, score) {
  console.log(`[db] save_profile_answer user=${userId} q=${questionId} score=${score}`)
  // TODO: 换成真实后端 HTTP 调用
}

export function dbGetLearningContent(subject, learningPath, step) {
  const name = learningPath?.[step] ?? '未知步骤'
  return `【${subject}】学习内容：${name}（Mock 文字板，第 ${step + 1} 步）`
}

export function dbGetQuizQuestion(subject, learningPath, step) {
  const name = learningPath?.[step] ?? '未知步骤'
  return [
    { id: `${subject}_${name}_q1`, text: `【${subject}·${name}】第1题（Mock）：请选择 A/B/C/D`, answer: 'A' },
    { id: `${subject}_${name}_q2`, text: `【${subject}·${name}】第2题（Mock）：请选择 A/B/C/D`, answer: 'B' },
  ]
}

export function dbSubmitQuizAnswer(userId, questionId, answer) {
  console.log(`[db] submit_quiz_answer user=${userId} q=${questionId} answer=${answer}`)
  // TODO: 换成真实后端 HTTP 调用
}
