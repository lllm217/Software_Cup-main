<script setup>
import { computed } from 'vue'
import { dbGetProfileQuestions } from '../api/db'

const props = defineProps(['state', 'ctx'])

const q = computed(() => dbGetProfileQuestions()[props.ctx?.profile_index ?? 0])
const questionNo = computed(() => (props.ctx?.profile_index ?? 0) + 1)
</script>

<template>
  <div class="page">
    <h2>人物画像问题（第 {{ questionNo }} / 6 题）</h2>
    <p v-if="q" class="question">{{ q.text }}</p>

    <template v-if="state === 'profile_ssvep'">
      <p class="warn">频闪已开始，请注视与所选选项对应的分数方块：</p>
      <div class="options">
        <div v-for="(opt, i) in (q?.options || [])" :key="i" class="option">
          <span class="tag">块{{ i }}</span> {{ i + 1 }}分 · {{ opt }}
        </div>
      </div>
    </template>
  </div>
</template>
