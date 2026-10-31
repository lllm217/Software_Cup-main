<script setup>
import { computed, ref, watch } from 'vue'
import { ensureSession, generateProfile, enterMain } from '../api/profile'

const props = defineProps({
  userId: { type: String, required: true },
  course: { type: String, default: '' },
  scores: { type: Array, default: () => [] },
  auto: { type: Boolean, default: false },
})
const selectedCourse = ref(props.course || '人工智能导论')
watch(() => props.course, value => { if (value) selectedCourse.value = value })
const submitting = ref(false)
const error = ref('')
const generated = ref(null)
async function submit() {
  if (completed.value !== questions.length || submitting.value) return
  submitting.value = true
  error.value = ''
  try {
    const session = await ensureSession(props.userId)
    generated.value = await generateProfile(session, answers.value, selectedCourse.value,
      props.scores.length === 6 ? props.scores : [])
    enterMain(generated.value.handoff)
  } catch (err) {
    error.value = err.message || '生成失败，请检查后端服务后重试。'
  } finally { submitting.value = false }
}
const questions = [
  { id: 'goal', text: '你本次学习最主要的目标是什么？', options: ['建立基础认知', '完成课程或备考', '解决实际问题', '提升项目与实践能力', '探索个人兴趣'] },
  { id: 'foundation', text: '你对所选科目的基础掌握情况如何？', options: ['零基础', '了解少量概念', '学过基础课程', '能独立完成基础任务', '有相关项目经验'] },
  { id: 'format', text: '你更愿意使用哪些学习资料？', multiple: true, options: ['图文讲解', '视频演示', '具体案例', '交互练习', '项目实战'] },
  { id: 'duration', text: '你通常希望每次学习持续多久？', options: ['15 分钟以内', '15–30 分钟', '30–60 分钟', '60 分钟以上', '根据内容灵活安排'] },
  { id: 'difficulty', text: '学习时你最希望获得哪些方面的帮助？', multiple: true, options: ['理解抽象概念', '补充前置知识', '将知识应用到实践', '保持专注与学习动力', '梳理重点与复习'] },
  { id: 'feedback', text: '遇到难题时，你更希望获得怎样的引导？', options: ['先给少量提示，自己尝试', '分步骤讲解思路', '展示完整示例后再练习', '先复习相关基础', '通过小测发现薄弱点'] },
]
const answers = ref({})
const status = ref('')
const storageKey = computed(() => `ssvep:supplemental-profile:${props.userId}`)
const completed = computed(() => questions.filter(q => answers.value[q.id]?.length).length)

watch(storageKey, () => {
  answers.value = {}
  status.value = ''
  try {
    const saved = JSON.parse(localStorage.getItem(storageKey.value) || '{}')
    for (const q of questions) {
      const values = Array.isArray(saved?.[q.id]) ? saved[q.id] : []
      answers.value[q.id] = values.filter(value => q.options.includes(value)).slice(0, q.multiple ? q.options.length : 1)
    }
  } catch {
    status.value = '暂时无法读取本机记录，仍可选择答案。'
  }
}, { immediate: true })

function select(q, option) {
  const selected = answers.value[q.id] || []
  answers.value[q.id] = q.multiple
    ? (selected.includes(option) ? selected.filter(value => value !== option) : [...selected, option])
    : (selected.includes(option) ? [] : [option])
  try {
    localStorage.setItem(storageKey.value, JSON.stringify(answers.value))
    status.value = '已自动保存到本机浏览器，可随时修改。'
  } catch {
    status.value = '浏览器暂时无法保存，当前选择仅在本次页面中保留。'
  }
}

// 脑电（SSVEP）自动模式：6 个 1~5 打分 → 6 道题的选项文本 → 直接生成画像并跳转主界面。
function scoresToAnswers(scores) {
  const out = {}
  questions.forEach((q, i) => {
    const option = q.options[scores[i] - 1]
    out[q.id] = option ? [option] : []
  })
  return out
}

watch(() => props.scores, (scores) => {
  if (!props.auto || !Array.isArray(scores) || scores.length !== 6) return
  if (submitting.value || generated.value) return
  answers.value = scoresToAnswers(scores)
  if (completed.value !== questions.length) return
  status.value = '脑电画像已采集，正在生成画像并跳转主界面…'
  submit()
})
</script>

<template>
  <details class="supplemental-profile" open>
    <summary>学习画像（已答 {{ completed }}/{{ questions.length }}）</summary>
    <p class="intro">完成六道问题后，生成并保存你的个性化学习画像，进入智育万象主界面。再次点击可取消选择；提交前答案自动保存在本机。</p>
    <label class="course-picker">学习课程
      <select v-model="selectedCourse" :disabled="submitting">
        <option>人工智能导论</option>
        <option value="软件安全">软件安全技术</option>
      </select>
    </label>
    <fieldset :disabled="submitting" v-for="(q, index) in questions" :key="q.id">
      <legend>{{ index + 1 }}. {{ q.text }}（{{ q.multiple ? '可多选' : '单选' }}）</legend>
      <div class="choices">
        <label v-for="option in q.options" :key="option" :class="{ selected: answers[q.id]?.includes(option) }">
          <input type="checkbox" :checked="answers[q.id]?.includes(option) || false" @change="select(q, option)">
          {{ option }}
        </label>
      </div>
    </fieldset>
    <p v-if="error" class="submit-error" role="alert">{{ error }} 答案已保留，可重新提交。</p>
    <p v-if="generated" class="save-status">{{ generated.summary }}</p>
    <button class="submit-profile" :disabled="completed !== questions.length || submitting" @click="submit">
      {{ submitting ? '正在生成画像…' : '生成个性化画像并进入主界面' }}
    </button>
    <p v-if="completed !== questions.length" class="intro">请完成全部六题后提交。</p>
    <p class="save-status" role="status">{{ status }}</p>
  </details>
</template>

<style scoped>
.supplemental-profile { margin-top: 20px; padding: 24px; background: #171c23; border: 1px solid #232b34; border-radius: 12px; }
summary { cursor: pointer; font-size: 18px; font-weight: 600; }
.intro { margin: 14px 0 20px; color: #9aa4ad; line-height: 1.7; font-size: 14px; }
fieldset { min-width: 0; border: 0; margin: 20px 0; }
legend { padding: 0; color: #cbd3da; line-height: 1.6; }
.choices { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 12px; }
label { display: flex; align-items: center; gap: 8px; padding: 10px 14px; background: #1f2832; border: 1px solid #2f3a46; border-radius: 8px; cursor: pointer; }
label.selected { border-color: #7dd3fc; background: #1a3345; }
label:focus-within { outline: 2px solid #7dd3fc; outline-offset: 2px; }
input { accent-color: #38bdf8; }
.save-status { color: #7dd3fc; font-size: 14px; min-height: 20px; }
select { background: #1f2832; color: #e6e8ea; border: 1px solid #3a4149; padding: 8px; border-radius: 6px; }
.submit-profile { margin: 12px 0; background: #075985; border-color: #38bdf8; }
.submit-profile:disabled { cursor: not-allowed; opacity: .5; }
.submit-error { color: #fbbf24; line-height: 1.7; }
</style>
