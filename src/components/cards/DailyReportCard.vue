<template>
  <article class="bg-white border border-gray-100 rounded-xl p-6 mb-6 dark:bg-slate-900 dark:border-slate-800">
    <!-- 日期标题 + 统计 -->
    <div class="flex flex-col gap-1 mb-4 max-md:gap-2">
      <h3 class="text-base font-medium text-slate-800 dark:text-slate-100">{{ formattedDate }}</h3>
      <div class="flex gap-4 text-xs text-slate-400 dark:text-slate-500">
        <span>论文 <strong class="text-slate-600 dark:text-slate-300">{{ report.stats.papers }}</strong></span>
        <span>资讯 <strong class="text-slate-600 dark:text-slate-300">{{ report.stats.news }}</strong></span>
        <span>精选 <strong class="text-slate-600 dark:text-slate-300">{{ report.stats.featured }}</strong></span>
      </div>
    </div>

    <!-- 摘要 -->
    <p class="text-sm text-slate-600 dark:text-slate-400 leading-relaxed mb-5">
      {{ report.summary }}
    </p>

    <!-- 要点 -->
    <div class="space-y-2">
      <div v-for="(h, i) in report.highlights" :key="i" class="flex items-start gap-2">
        <span class="text-slate-300 dark:text-slate-600 text-xs mt-0.5 select-none">-</span>
        <p class="text-sm text-slate-500 dark:text-slate-400">{{ h }}</p>
      </div>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'

/**
 * @typedef {import('../../utils/types').DailyReport} DailyReport
 */

const props = defineProps({
  /** @type {DailyReport} */
  report: { type: Object, required: true },
})

const formattedDate = computed(() => {
  const d = props.report.date
  if (!d) return ''
  const date = new Date(d + 'T00:00:00')
  return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`
})
</script>
