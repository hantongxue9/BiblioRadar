<template>
  <div>
    <div class="mb-8">
      <div class="flex items-start justify-between">
        <div>
          <h2 class="text-lg font-light text-slate-800 dark:text-slate-100 mb-1.5">图情日报</h2>
          <div class="w-8 h-0.5 bg-ustc-300 rounded mb-2"></div>
          <p class="text-xs text-slate-400 dark:text-slate-500">大模型生成的每日行业摘要</p>
        </div>
        <button
          v-if="reports.length === 0 && dayItems.length > 0"
          @click="saveAll(dayItems.map((i) => i.id))"
          class="text-xs px-3 py-1 rounded-full mt-1 text-slate-500 hover:text-slate-700 bg-slate-100 hover:bg-slate-200 dark:text-slate-400 dark:hover:text-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 transition-colors"
        >
          收藏本页
        </button>
      </div>
    </div>

    <!-- 日报卡片列表 -->
    <template v-if="reports.length > 0">
      <DailyReportCard v-for="report in reports" :key="report.date" :report="report" />
    </template>

    <!-- 无日报时的 fallback：按日期浏览条目 -->
    <template v-else>
      <!-- 日期导航 + 统计 -->
      <div class="flex items-center justify-between mb-8">
        <div class="flex items-center gap-2">
          <button
            :disabled="currentDateIndex >= availableDates.length - 1"
            @click="currentDateIndex++"
            class="px-2 py-1 text-xs rounded transition-colors disabled:opacity-30 disabled:cursor-default
                   text-slate-500 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800"
          >
            ‹
          </button>
          <span class="text-sm text-slate-700 dark:text-slate-200 min-w-[120px] text-center">{{ displayDate }}</span>
          <button
            :disabled="currentDateIndex === 0"
            @click="currentDateIndex--"
            class="px-2 py-1 text-xs rounded transition-colors disabled:opacity-30 disabled:cursor-default
                   text-slate-500 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800"
          >
            ›
          </button>
        </div>
        <div class="flex flex-wrap gap-x-5 gap-y-1 text-xs text-slate-400 dark:text-slate-500">
          <span>共 <strong class="text-slate-600 dark:text-slate-300 font-medium">{{ dayItems.length }}</strong> 条</span>
          <span>论文 <strong class="text-slate-600 dark:text-slate-300 font-medium">{{ dayPapers.length }}</strong></span>
          <span>资讯 <strong class="text-slate-600 dark:text-slate-300 font-medium">{{ dayNews.length }}</strong></span>
          <span>精选 <strong class="text-slate-600 dark:text-slate-300 font-medium">{{ dayFeatured.length }}</strong></span>
        </div>
      </div>

      <div v-if="dayItems.length === 0" class="text-sm text-slate-400 dark:text-slate-500 py-12 text-center">
        暂无数据
      </div>

      <!-- 当日精选 -->
      <template v-if="dayFeatured.length > 0">
        <div class="flex items-center gap-4 mb-6">
          <div class="h-px flex-1 bg-gray-200 dark:bg-slate-800"></div>
          <span class="text-xs text-slate-400 dark:text-slate-500 whitespace-nowrap">当日精选</span>
          <div class="h-px flex-1 bg-gray-200 dark:bg-slate-800"></div>
        </div>
        <CompactPaperCard
          v-for="paper in dayFeatured"
          :key="paper.id"
          v-memo="[paper.id === selectedItem?.id, isSaved(paper.id)]"
          :paper="paper"
          :is-selected="selectedItem?.id === paper.id"
          :is-saved="isSaved(paper.id)"
          @select="$emit('select', $event)"
          @toggle-save="toggleSave"
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
            v-memo="[paper.id === selectedItem?.id, isSaved(paper.id)]"
            :paper="paper"
            :is-selected="selectedItem?.id === paper.id"
            :is-saved="isSaved(paper.id)"
            @select="$emit('select', $event)"
            @toggle-save="toggleSave"
          />
        </div>
      </template>

      <!-- 行业资讯 -->
      <template v-if="dayNews.length > 0">
        <div class="flex items-center gap-4 mb-6 mt-10">
          <div class="h-px flex-1 bg-gray-200 dark:bg-slate-800"></div>
          <span class="text-xs text-slate-400 dark:text-slate-500 whitespace-nowrap">行业资讯</span>
          <div class="h-px flex-1 bg-gray-200 dark:bg-slate-800"></div>
        </div>
        <CompactNewsCard v-for="item in dayNews" :key="item.id" :item="item" />
      </template>
    </template>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import DailyReportCard from '../cards/DailyReportCard.vue'
import { formatDateCN } from '../../utils/date'
import CompactPaperCard from '../cards/CompactPaperCard.vue'
import CompactNewsCard from '../cards/CompactNewsCard.vue'

/**
 * @typedef {import('../../utils/types').PaperItem} PaperItem
 * @typedef {import('../../utils/types').DailyReport} DailyReport
 */

const props = defineProps({
  /** @type {PaperItem[]} */
  items: { type: Array, default: () => [] },
  /** @type {DailyReport[]} */
  reports: { type: Array, default: () => [] },
  /** @type {PaperItem|null} */
  selectedItem: { type: Object, default: null },
  toggleSave: { type: Function, default: () => {} },
  isSaved: { type: Function, default: () => false },
  saveAll: { type: Function, default: () => {} },
})

defineEmits(['select'])

const availableDates = computed(() => {
  const dates = [...new Set(props.items.map((i) => i.date).filter(Boolean))]
  dates.sort((a, b) => b.localeCompare(a))
  return dates
})

const currentDateIndex = ref(0)

const dayItems = computed(() => {
  const date = availableDates.value[currentDateIndex.value]
  return date ? props.items.filter((i) => i.date === date) : []
})

const displayDate = computed(() => {
  const d = availableDates.value[currentDateIndex.value]
  return d ? formatDateCN(d) : '暂无数据'
})

const dayPapers = computed(() => dayItems.value.filter((i) => i.content_type === 'paper'))
const dayNews = computed(() => dayItems.value.filter((i) => i.content_type === 'news'))
const dayFeatured = computed(() => dayPapers.value.filter((i) => i.featured).slice(0, 5))

const papersByCategory = computed(() => {
  const featuredIds = new Set(dayFeatured.value.map((p) => p.id))
  const map = {}
  for (const p of dayPapers.value) {
    if (featuredIds.has(p.id)) continue
    const cat = p.category || '其他'
    if (!map[cat]) map[cat] = []
    map[cat].push(p)
  }
  return Object.entries(map).map(([category, papers]) => ({ category, papers }))
})
</script>
