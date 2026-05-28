<template>
  <div>
    <div class="mb-8">
      <h2 class="text-lg font-light text-slate-800 dark:text-slate-100 mb-1.5">图情日报</h2>
      <div class="w-8 h-0.5 bg-indigo-400 rounded mb-2"></div>
      <p class="text-xs text-slate-400 dark:text-slate-500">大模型生成的每日行业摘要</p>
    </div>

    <!-- 日报卡片列表 -->
    <template v-if="reports.length > 0">
      <DailyReportCard v-for="report in reports" :key="report.date" :report="report" />
    </template>

    <!-- 无日报时的 fallback：展示最新一天的条目 -->
    <template v-else>
      <div class="mb-6">
        <h3 class="text-sm font-light text-slate-700 dark:text-slate-200 mb-1">{{ displayDate }}</h3>
      </div>

      <!-- 统计行 -->
      <div class="flex flex-wrap gap-x-6 gap-y-1 mb-10 text-xs text-slate-500 dark:text-slate-400">
        <span>共收录 <strong class="text-slate-700 dark:text-slate-200 font-medium">{{ todayItems.length }}</strong> 条</span>
        <span>论文 <strong class="text-slate-700 dark:text-slate-200 font-medium">{{ todayPapers.length }}</strong> 篇</span>
        <span>资讯 <strong class="text-slate-700 dark:text-slate-200 font-medium">{{ todayNews.length }}</strong> 条</span>
        <span>精选 <strong class="text-slate-700 dark:text-slate-200 font-medium">{{ todayFeatured.length }}</strong> 篇</span>
      </div>

      <div v-if="todayItems.length === 0" class="text-sm text-slate-400 dark:text-slate-500 py-12 text-center">
        暂无数据
      </div>

      <!-- 今日精选 -->
      <template v-if="todayFeatured.length > 0">
        <div class="flex items-center gap-4 mb-6">
          <div class="h-px flex-1 bg-gray-200 dark:bg-slate-800"></div>
          <span class="text-xs text-slate-400 dark:text-slate-500 whitespace-nowrap">今日精选</span>
          <div class="h-px flex-1 bg-gray-200 dark:bg-slate-800"></div>
        </div>
        <CompactPaperCard
          v-for="paper in todayFeatured"
          :key="paper.id"
          v-memo="[paper.id === selectedItem?.id]"
          :paper="paper"
          :is-selected="selectedItem?.id === paper.id"
          @select="$emit('select', $event)"
        />
      </template>

      <!-- 新收录论文 -->
      <template v-if="papersByCategory.length > 0">
        <div class="flex items-center gap-4 mb-6 mt-10">
          <div class="h-px flex-1 bg-gray-200 dark:bg-slate-800"></div>
          <span class="text-xs text-slate-400 dark:text-slate-500 whitespace-nowrap">新收录论文</span>
          <div class="h-px flex-1 bg-gray-200 dark:bg-slate-800"></div>
        </div>
        <div v-for="group in papersByCategory" :key="group.category" class="mb-6">
          <p class="text-xs text-slate-400 dark:text-slate-500 mb-3">{{ group.category }} ({{ group.papers.length }})</p>
          <CompactPaperCard
            v-for="paper in group.papers"
            :key="paper.id"
            v-memo="[paper.id === selectedItem?.id]"
            :paper="paper"
            :is-selected="selectedItem?.id === paper.id"
            @select="$emit('select', $event)"
          />
        </div>
      </template>

      <!-- 行业资讯 -->
      <template v-if="todayNews.length > 0">
        <div class="flex items-center gap-4 mb-6 mt-10">
          <div class="h-px flex-1 bg-gray-200 dark:bg-slate-800"></div>
          <span class="text-xs text-slate-400 dark:text-slate-500 whitespace-nowrap">行业资讯</span>
          <div class="h-px flex-1 bg-gray-200 dark:bg-slate-800"></div>
        </div>
        <CompactNewsCard v-for="item in todayNews" :key="item.id" :item="item" />
      </template>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import DailyReportCard from './DailyReportCard.vue'
import CompactPaperCard from './CompactPaperCard.vue'
import CompactNewsCard from './CompactNewsCard.vue'

const props = defineProps({
  items: { type: Array, default: () => [] },
  reports: { type: Array, default: () => [] },
  selectedItem: { type: Object, default: null },
})

defineEmits(['select'])

const todayItems = computed(() => {
  if (props.items.length === 0) return []
  const latestDate = props.items.reduce((max, i) => i.date && i.date > max ? i.date : max, '')
  if (!latestDate) return []
  return props.items.filter((i) => i.date === latestDate)
})

const displayDate = computed(() => {
  const d = todayItems.value[0]?.date
  if (!d) return '暂无数据'
  const date = new Date(d + 'T00:00:00')
  return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`
})

const todayPapers = computed(() => todayItems.value.filter((i) => i.content_type === 'paper'))
const todayNews = computed(() => todayItems.value.filter((i) => i.content_type === 'news'))
const todayFeatured = computed(() => todayPapers.value.filter((i) => i.featured).slice(0, 5))

const papersByCategory = computed(() => {
  const featuredIds = new Set(todayFeatured.value.map((p) => p.id))
  const map = {}
  for (const p of todayPapers.value) {
    if (featuredIds.has(p.id)) continue
    const cat = p.category || '其他'
    if (!map[cat]) map[cat] = []
    map[cat].push(p)
  }
  return Object.entries(map).map(([category, papers]) => ({ category, papers }))
})
</script>
