<template>
  <div>
    <div class="mb-8">
      <h2 class="text-lg font-light text-slate-800 dark:text-slate-100 mb-1.5">趋势</h2>
      <div class="w-8 h-0.5 bg-ustc-300 rounded mb-2"></div>
      <p class="text-xs text-slate-400 dark:text-slate-500">收录量、评分与分类分布</p>
    </div>

    <!-- 每日收录量 -->
    <section class="mb-12">
      <h3 class="text-sm font-medium text-slate-700 dark:text-slate-200 mb-4">每日收录量</h3>
      <div class="flex items-end gap-1 h-40">
        <div
          v-for="d in dailyStats"
          :key="d.date"
          class="flex-1 flex flex-col items-center justify-end h-full group"
        >
          <div class="relative w-full flex flex-col items-center justify-end h-full">
            <!-- 资讯（浅色，堆在上面） -->
            <div
              v-if="d.news > 0"
              class="w-full max-w-[20px] rounded-t transition-all bg-ustc-200 dark:bg-ustc-700"
              :style="{ height: (d.news / maxDailyCount) * 100 + '%' }"
            ></div>
            <!-- 论文（深色，在下面） -->
            <div
              v-if="d.papers > 0"
              class="w-full max-w-[20px] transition-all bg-ustc-400 dark:bg-ustc-500"
              :class="d.news > 0 ? '' : 'rounded-t'"
              :style="{ height: (d.papers / maxDailyCount) * 100 + '%' }"
            ></div>
            <!-- tooltip -->
            <div class="absolute -top-8 left-1/2 -translate-x-1/2 hidden group-hover:block
                        text-[10px] text-slate-500 dark:text-slate-400 whitespace-nowrap
                        bg-white dark:bg-slate-800 px-1.5 py-0.5 rounded shadow-sm border border-gray-100 dark:border-slate-700">
              {{ d.total }}条
            </div>
          </div>
          <span class="text-[9px] text-slate-400 dark:text-slate-500 mt-1.5 -rotate-45 origin-top-left">{{ d.label }}</span>
        </div>
      </div>
      <div class="flex items-center gap-4 mt-4 text-[10px] text-slate-400 dark:text-slate-500">
        <span class="flex items-center gap-1"><span class="inline-block w-2.5 h-2.5 rounded-sm bg-ustc-400 dark:bg-ustc-500"></span>论文</span>
        <span class="flex items-center gap-1"><span class="inline-block w-2.5 h-2.5 rounded-sm bg-ustc-200 dark:bg-ustc-700"></span>资讯</span>
      </div>
    </section>

    <!-- 每日平均分 -->
    <section class="mb-12">
      <h3 class="text-sm font-medium text-slate-700 dark:text-slate-200 mb-4">每日平均分</h3>
      <div class="flex items-end gap-1 h-32">
        <div
          v-for="d in dailyStats"
          :key="d.date"
          class="flex-1 flex flex-col items-center justify-end h-full group"
        >
          <div class="relative w-full flex flex-col items-center justify-end h-full">
            <div
              class="w-full max-w-[20px] rounded-t bg-amber-300 dark:bg-amber-600 transition-all"
              :style="{ height: maxAvgScore > 0 ? (d.avgScore / maxAvgScore) * 100 + '%' : '0' }"
            ></div>
            <div class="absolute -top-8 left-1/2 -translate-x-1/2 hidden group-hover:block
                        text-[10px] text-slate-500 dark:text-slate-400 whitespace-nowrap
                        bg-white dark:bg-slate-800 px-1.5 py-0.5 rounded shadow-sm border border-gray-100 dark:border-slate-700">
              {{ d.avgScore }}分 · {{ d.total }}条
            </div>
          </div>
          <span class="text-[9px] text-slate-400 dark:text-slate-500 mt-1.5 -rotate-45 origin-top-left">{{ d.label }}</span>
        </div>
      </div>
    </section>

    <!-- 分类分布 -->
    <section>
      <h3 class="text-sm font-medium text-slate-700 dark:text-slate-200 mb-4">分类分布</h3>
      <div class="space-y-2">
        <div v-for="cat in categoryStats" :key="cat.name" class="flex items-center gap-3 group">
          <span class="text-xs text-slate-500 dark:text-slate-400 w-20 text-right truncate flex-shrink-0">{{ cat.name }}</span>
          <div class="flex-1 h-5 bg-slate-100 dark:bg-slate-800 rounded overflow-hidden relative">
            <div
              class="h-full rounded bg-ustc-300 dark:bg-ustc-600 transition-all flex items-center"
              :style="{ width: (cat.count / maxCategoryCount) * 100 + '%' }"
            >
              <span v-if="cat.count / maxCategoryCount > 0.15" class="text-[10px] text-white px-1.5">{{ cat.count }}</span>
            </div>
            <div class="absolute -top-7 left-1/2 -translate-x-1/2 hidden group-hover:block
                        text-[10px] text-slate-500 dark:text-slate-400 whitespace-nowrap
                        bg-white dark:bg-slate-800 px-1.5 py-0.5 rounded shadow-sm border border-gray-100 dark:border-slate-700 z-10">
              {{ cat.name }}：{{ cat.count }}条 ({{ cat.pct }}%)
            </div>
          </div>
          <span v-if="cat.count / maxCategoryCount <= 0.15" class="text-[10px] text-slate-400 dark:text-slate-500 flex-shrink-0">{{ cat.count }}</span>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed } from 'vue'

/**
 * @typedef {import('../../utils/types').PaperItem} PaperItem
 */

const props = defineProps({
  /** @type {PaperItem[]} */
  items: { type: Array, default: () => [] },
})

const dailyStats = computed(() => {
  const map = {}
  for (const item of props.items) {
    if (!item.date) continue
    if (!map[item.date]) map[item.date] = { papers: 0, news: 0, scores: [] }
    if (item.content_type === 'news') {
      map[item.date].news++
    } else {
      map[item.date].papers++
    }
    if (item.composite_score != null) {
      map[item.date].scores.push(item.composite_score)
    }
  }

  return Object.entries(map)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([date, data]) => {
      const total = data.papers + data.news
      const avg = data.scores.length > 0
        ? (data.scores.reduce((s, v) => s + v, 0) / data.scores.length).toFixed(1)
        : '—'
      const parts = date.split('-')
      return { date, label: `${+parts[1]}/${+parts[2]}`, papers: data.papers, news: data.news, total, avgScore: avg }
    })
})

const maxDailyCount = computed(() => Math.max(1, ...dailyStats.value.map((d) => d.total)))
const maxAvgScore = computed(() => {
  const nums = dailyStats.value.map((d) => +d.avgScore).filter((v) => !isNaN(v))
  return nums.length > 0 ? Math.max(...nums) : 1
})

const categoryStats = computed(() => {
  const map = {}
  const total = props.items.length || 1
  for (const item of props.items) {
    const cat = item.category || '其他'
    map[cat] = (map[cat] || 0) + 1
  }
  return Object.entries(map)
    .map(([name, count]) => ({ name, count, pct: ((count / total) * 100).toFixed(1) }))
    .sort((a, b) => b.count - a.count)
})

const maxCategoryCount = computed(() => Math.max(1, ...categoryStats.value.map((c) => c.count)))
</script>
