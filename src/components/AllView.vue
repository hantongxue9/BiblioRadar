<template>
  <div>
    <div class="mb-6">
      <h2 class="text-lg font-light text-slate-800 mb-1">全部</h2>
      <p class="text-xs text-slate-400">所有收录的文献与资讯</p>
    </div>

    <!-- 筛选面板 -->
    <div class="flex flex-col sm:flex-row gap-3 mb-8">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="搜索标题或摘要..."
        class="flex-1 px-4 py-2.5 text-sm text-slate-700 bg-white border border-gray-200 rounded-lg
               placeholder:text-slate-300 focus:outline-none focus:border-slate-400 transition-colors"
      />
      <select
        v-model="selectedCategory"
        class="px-4 py-2.5 text-sm text-slate-700 bg-white border border-gray-200 rounded-lg
               focus:outline-none focus:border-slate-400 transition-colors cursor-pointer"
      >
        <option value="all">全部分类</option>
        <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
      </select>
      <select
        v-model="contentType"
        class="px-4 py-2.5 text-sm text-slate-700 bg-white border border-gray-200 rounded-lg
               focus:outline-none focus:border-slate-400 transition-colors cursor-pointer"
      >
        <option value="all">全部类型</option>
        <option value="paper">论文</option>
        <option value="news">资讯</option>
      </select>
      <select
        v-model="sortBy"
        class="px-4 py-2.5 text-sm text-slate-700 bg-white border border-gray-200 rounded-lg
               focus:outline-none focus:border-slate-400 transition-colors cursor-pointer"
      >
        <option value="date">按时间排序</option>
        <option value="score">按评分排序</option>
      </select>
    </div>

    <p class="text-xs text-slate-400 mb-6">共 {{ filtered.length }} 条</p>

    <div v-if="filtered.length === 0" class="text-sm text-slate-400 py-12 text-center">
      没有找到匹配的内容
    </div>

    <template v-for="group in groupedByDate" :key="group.date">
      <div class="flex items-center gap-4 mb-6 mt-2">
        <div class="h-px flex-1 bg-gray-200"></div>
        <span class="text-xs text-slate-400 whitespace-nowrap">{{ group.date || '无日期' }}</span>
        <div class="h-px flex-1 bg-gray-200"></div>
      </div>
      <PaperCard v-for="item in group.items" :key="item.id" :paper="item" />
    </template>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import PaperCard from './PaperCard.vue'

const props = defineProps({
  items: { type: Array, default: () => [] },
})

const searchQuery = ref('')
const selectedCategory = ref('all')
const contentType = ref('all')
const sortBy = ref('date')

const categories = computed(() => {
  return [...new Set(props.items.map((p) => p.category))].sort()
})

const filtered = computed(() => {
  let result = [...props.items]

  if (searchQuery.value.trim()) {
    const q = searchQuery.value.trim().toLowerCase()
    result = result.filter(
      (p) =>
        p.title.toLowerCase().includes(q) ||
        p.abstract.toLowerCase().includes(q) ||
        (p.one_sentence_summary || '').toLowerCase().includes(q)
    )
  }

  if (selectedCategory.value !== 'all') {
    result = result.filter((p) => p.category === selectedCategory.value)
  }

  if (contentType.value !== 'all') {
    result = result.filter((p) => p.content_type === contentType.value)
  }

  if (sortBy.value === 'date') {
    result.sort((a, b) => new Date(b.date || 0) - new Date(a.date || 0))
  } else {
    result.sort((a, b) => (b.composite_score || 0) - (a.composite_score || 0))
  }

  return result
})

const groupedByDate = computed(() => {
  const groups = []
  let currentDate = null
  for (const item of filtered.value) {
    if (item.date !== currentDate) {
      currentDate = item.date
      groups.push({ date: item.date, items: [] })
    }
    groups[groups.length - 1].items.push(item)
  }
  return groups
})
</script>
