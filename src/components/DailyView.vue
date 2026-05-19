<template>
  <div>
    <div class="mb-8">
      <h2 class="text-lg font-light text-slate-800 mb-1">{{ displayDate }} · 图情日报</h2>
    </div>

    <!-- 统计行 -->
    <div class="flex gap-6 mb-10 text-xs text-slate-500">
      <span>共收录 <strong class="text-slate-700 font-medium">{{ todayItems.length }}</strong> 条</span>
      <span>论文 <strong class="text-slate-700 font-medium">{{ todayPapers.length }}</strong> 篇</span>
      <span>资讯 <strong class="text-slate-700 font-medium">{{ todayNews.length }}</strong> 条</span>
      <span>精选 <strong class="text-slate-700 font-medium">{{ todayFeatured.length }}</strong> 篇</span>
    </div>

    <div v-if="todayItems.length === 0" class="text-sm text-slate-400 py-12 text-center">
      今日暂无新收录内容
    </div>

    <!-- 今日精选 -->
    <template v-if="todayFeatured.length > 0">
      <div class="flex items-center gap-4 mb-6">
        <div class="h-px flex-1 bg-gray-200"></div>
        <span class="text-xs text-slate-400 whitespace-nowrap">今日精选</span>
        <div class="h-px flex-1 bg-gray-200"></div>
      </div>
      <CompactPaperCard v-for="paper in todayFeatured" :key="paper.id" :paper="paper" />
    </template>

    <!-- 新收录论文 -->
    <template v-if="papersByCategory.length > 0">
      <div class="flex items-center gap-4 mb-6 mt-10">
        <div class="h-px flex-1 bg-gray-200"></div>
        <span class="text-xs text-slate-400 whitespace-nowrap">新收录论文</span>
        <div class="h-px flex-1 bg-gray-200"></div>
      </div>
      <div v-for="group in papersByCategory" :key="group.category" class="mb-6">
        <p class="text-xs text-slate-400 mb-3">{{ group.category }} ({{ group.papers.length }})</p>
        <CompactPaperCard v-for="paper in group.papers" :key="paper.id" :paper="paper" />
      </div>
    </template>

    <!-- 行业资讯 -->
    <template v-if="todayNews.length > 0">
      <div class="flex items-center gap-4 mb-6 mt-10">
        <div class="h-px flex-1 bg-gray-200"></div>
        <span class="text-xs text-slate-400 whitespace-nowrap">行业资讯</span>
        <div class="h-px flex-1 bg-gray-200"></div>
      </div>
      <CompactNewsCard v-for="item in todayNews" :key="item.id" :item="item" />
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import CompactPaperCard from './CompactPaperCard.vue'
import CompactNewsCard from './CompactNewsCard.vue'

const props = defineProps({
  items: { type: Array, default: () => [] },
})

const todayItems = computed(() => {
  if (props.items.length === 0) return []
  const latestDate = props.items.find((i) => i.date)?.date
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
  const map = {}
  for (const p of todayPapers.value) {
    const cat = p.category || '其他'
    if (!map[cat]) map[cat] = []
    map[cat].push(p)
  }
  return Object.entries(map).map(([category, papers]) => ({ category, papers }))
})
</script>
