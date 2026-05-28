<template>
  <div>
    <div class="mb-6">
      <h2 class="text-lg font-light text-slate-800 dark:text-slate-100 mb-1.5">全部</h2>
      <div class="w-8 h-0.5 bg-blue-300 rounded mb-2"></div>
      <p class="text-xs text-slate-400 dark:text-slate-500">所有收录的文献与资讯</p>
    </div>

    <!-- 类型筛选 pill -->
    <div class="flex flex-wrap gap-2 mb-3">
      <button
        v-for="opt in typeOptions"
        :key="opt.value"
        @click="contentType = opt.value"
        class="px-3 py-1 text-xs rounded-full transition-colors"
        :class="
          contentType === opt.value
            ? 'bg-slate-800 text-white dark:bg-slate-200 dark:text-slate-900'
            : 'bg-slate-100 text-slate-500 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:hover:bg-slate-700'
        "
      >
        {{ opt.label }}
      </button>
    </div>

    <!-- 分类筛选 pill -->
    <div class="flex flex-wrap gap-2 mb-3">
      <button
        @click="selectedCategory = 'all'"
        class="px-3 py-1 text-xs rounded-full transition-colors"
        :class="
          selectedCategory === 'all'
            ? 'bg-slate-800 text-white dark:bg-slate-200 dark:text-slate-900'
            : 'bg-slate-100 text-slate-500 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:hover:bg-slate-700'
        "
      >
        全部分类
      </button>
      <button
        v-for="cat in categories"
        :key="cat"
        @click="selectedCategory = cat"
        class="px-3 py-1 text-xs rounded-full transition-colors"
        :class="
          selectedCategory === cat
            ? 'bg-slate-800 text-white dark:bg-slate-200 dark:text-slate-900'
            : 'bg-slate-100 text-slate-500 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:hover:bg-slate-700'
        "
      >
        {{ cat }}
      </button>
    </div>

    <!-- 搜索 + 排序 -->
    <div class="flex gap-3 mb-8">
      <input
        v-model="searchInput"
        type="text"
        placeholder="搜索标题或摘要..."
        class="flex-1 px-4 py-2.5 text-sm text-slate-700 bg-white border border-gray-200 rounded-lg
               placeholder:text-slate-300 focus:outline-none focus:border-slate-400 transition-colors
               dark:bg-slate-900 dark:border-slate-700 dark:text-slate-200 dark:placeholder:text-slate-600"
      />
      <select
        v-model="sortBy"
        class="px-4 py-2.5 text-sm text-slate-700 bg-white border border-gray-200 rounded-lg
               focus:outline-none focus:border-slate-400 transition-colors cursor-pointer
               dark:bg-slate-900 dark:border-slate-700 dark:text-slate-200"
      >
        <option value="date">按时间排序</option>
        <option value="score">按评分排序</option>
      </select>
    </div>

    <p class="text-xs text-slate-400 dark:text-slate-500 mb-6">共 {{ filtered.length }} 条</p>

    <div v-if="filtered.length === 0" class="text-sm text-slate-400 dark:text-slate-500 py-12 text-center">
      没有找到匹配的内容
    </div>

    <template v-for="group in pageGroups" :key="group.date ?? 'flat'">
      <div v-if="group.date" class="flex items-center gap-4 mb-6 mt-2">
        <div class="h-px flex-1 bg-gray-200 dark:bg-slate-800"></div>
        <span class="text-xs text-slate-400 dark:text-slate-500 whitespace-nowrap">{{ group.date }}</span>
        <div class="h-px flex-1 bg-gray-200 dark:bg-slate-800"></div>
      </div>
      <PaperCard
        v-for="item in group.items"
        :key="item.id"
        :paper="item"
        :is-selected="selectedItem?.id === item.id"
        @select="$emit('select', $event)"
      />
    </template>

    <!-- 分页 -->
    <div v-if="totalPages > 1" class="flex items-center justify-center gap-1 mt-10">
      <button
        :disabled="currentPage === 1"
        @click="currentPage--"
        class="px-2.5 py-1 text-xs rounded transition-colors disabled:opacity-30 disabled:cursor-default
               text-slate-500 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800"
      >
        ‹
      </button>
      <button
        v-for="p in visiblePages"
        :key="p"
        @click="currentPage = p"
        class="min-w-[28px] px-2 py-1 text-xs rounded transition-colors"
        :class="
          p === currentPage
            ? 'bg-slate-800 text-white dark:bg-slate-200 dark:text-slate-900'
            : 'text-slate-500 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800'
        "
      >
        {{ p }}
      </button>
      <button
        :disabled="currentPage === totalPages"
        @click="currentPage++"
        class="px-2.5 py-1 text-xs rounded transition-colors disabled:opacity-30 disabled:cursor-default
               text-slate-500 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800"
      >
        ›
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onUnmounted } from 'vue'
import PaperCard from './PaperCard.vue'

const props = defineProps({
  items: { type: Array, default: () => [] },
  selectedItem: { type: Object, default: null },
})

defineEmits(['select'])

const searchInput = ref('')
const searchQuery = ref('')
const selectedCategory = ref('all')
const contentType = ref('all')
const sortBy = ref('date')
const currentPage = ref(1)
const perPage = 50

let searchTimer = null
watch(searchInput, (val) => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => { searchQuery.value = val }, 200)
})
onUnmounted(() => clearTimeout(searchTimer))

const typeOptions = [
  { label: '全部', value: 'all' },
  { label: '论文', value: 'paper' },
  { label: '资讯', value: 'news' },
]

const categories = computed(() => {
  return [...new Set(props.items.map((p) => p.category))].filter(Boolean).sort()
})

const filtered = computed(() => {
  let result = props.items

  if (searchQuery.value.trim()) {
    const q = searchQuery.value.trim().toLowerCase()
    result = result.filter(
      (p) =>
        p.title.toLowerCase().includes(q) ||
        (p.abstract || '').toLowerCase().includes(q) ||
        (p.one_sentence_summary || '').toLowerCase().includes(q)
    )
  }

  if (selectedCategory.value !== 'all') {
    result = result.filter((p) => p.category === selectedCategory.value)
  }

  if (contentType.value !== 'all') {
    result = result.filter((p) => p.content_type === contentType.value)
  }

  result = result.slice()
  if (sortBy.value === 'date') {
    result.sort((a, b) => (b.date || '').localeCompare(a.date || ''))
  } else {
    result.sort((a, b) => (b.composite_score ?? 0) - (a.composite_score ?? 0))
  }

  return result
})

// 筛选/排序变化时回到第 1 页
watch([searchQuery, selectedCategory, contentType, sortBy], () => { currentPage.value = 1 })

const totalPages = computed(() => Math.ceil(filtered.value.length / perPage))

const paginatedItems = computed(() => {
  const start = (currentPage.value - 1) * perPage
  return filtered.value.slice(start, start + perPage)
})

const visiblePages = computed(() => {
  const total = totalPages.value
  const cur = currentPage.value
  const pages = []
  // 最多显示 7 个页码，当前页居中
  let start = Math.max(1, cur - 3)
  let end = Math.min(total, start + 6)
  if (end - start < 6) start = Math.max(1, end - 6)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

const pageGroups = computed(() => {
  if (sortBy.value !== 'date') {
    return [{ date: null, items: paginatedItems.value }]
  }
  const groups = []
  let currentDate = null
  for (const item of paginatedItems.value) {
    if (item.date !== currentDate) {
      currentDate = item.date
      groups.push({ date: item.date, items: [] })
    }
    groups[groups.length - 1].items.push(item)
  }
  return groups
})
</script>
