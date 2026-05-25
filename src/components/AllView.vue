<template>
  <div>
    <div class="mb-6">
      <h2 class="text-lg font-light text-slate-800 dark:text-slate-100 mb-1">全部</h2>
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

    <!-- 虚拟滚动容器 -->
    <div v-else ref="scrollContainer" style="overflow-anchor: none;">
      <div :style="{ height: totalHeight + 'px', position: 'relative' }">
        <div :style="{ position: 'absolute', top: 0, left: 0, right: 0, transform: 'translateY(' + offsetY + 'px)' }">
          <template v-for="entry in visibleItems" :key="entry.key">
            <!-- 日期分隔符 -->
            <div v-if="entry.type === 'separator'" class="flex items-center gap-4 mb-6 mt-2">
              <div class="h-px flex-1 bg-gray-200 dark:bg-slate-800"></div>
              <span class="text-xs text-slate-400 dark:text-slate-500 whitespace-nowrap">{{ entry.date || '无日期' }}</span>
              <div class="h-px flex-1 bg-gray-200 dark:bg-slate-800"></div>
            </div>
            <!-- 论文卡片 -->
            <PaperCard
              v-else
              :paper="entry.item"
              :is-selected="selectedItem?.id === entry.item.id"
              @select="$emit('select', $event)"
            />
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
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

let searchTimer = null
watch(searchInput, (val) => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => { searchQuery.value = val }, 200)
})

const typeOptions = [
  { label: '全部', value: 'all' },
  { label: '论文', value: 'paper' },
  { label: '资讯', value: 'news' },
]

const categories = computed(() => {
  return [...new Set(props.items.map((p) => p.category))].sort()
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
    result.sort((a, b) => (b.composite_score || 0) - (a.composite_score || 0))
  }

  return result
})

// 将分组数据扁平化为带类型的条目列表（日期分隔符 + 卡片交替）
const flatItems = computed(() => {
  const list = []
  let currentDate = null
  for (const item of filtered.value) {
    if (item.date !== currentDate) {
      currentDate = item.date
      list.push({ type: 'separator', date: item.date, key: 'sep-' + (item.date || 'none') })
    }
    list.push({ type: 'card', item, key: 'card-' + item.id })
  }
  return list
})

// 虚拟滚动参数
const ROW_HEIGHT = 200      // 卡片估算高度（px）
const SEP_HEIGHT = 48       // 分隔符高度（px）
const BUFFER = 8            // 上下缓冲条目数

const scrollTop = ref(0)
const viewportHeight = ref(800)
const scrollContainer = ref(null)
let rafId = null

const totalHeight = computed(() => {
  let h = 0
  for (const entry of flatItems.value) {
    h += entry.type === 'separator' ? SEP_HEIGHT : ROW_HEIGHT
  }
  return h
})

const visibleRange = computed(() => {
  let start = 0
  let acc = 0
  for (let i = 0; i < flatItems.value.length; i++) {
    const h = flatItems.value[i].type === 'separator' ? SEP_HEIGHT : ROW_HEIGHT
    if (acc + h > scrollTop.value) { start = i; break }
    acc += h
    if (i === flatItems.value.length - 1) { start = i }
  }

  let end = start
  let visible = 0
  for (let i = start; i < flatItems.value.length; i++) {
    const h = flatItems.value[i].type === 'separator' ? SEP_HEIGHT : ROW_HEIGHT
    visible += h
    end = i
    if (visible > viewportHeight.value) break
  }

  return {
    start: Math.max(0, start - BUFFER),
    end: Math.min(flatItems.value.length - 1, end + BUFFER),
  }
})

const visibleItems = computed(() =>
  flatItems.value.slice(visibleRange.value.start, visibleRange.value.end + 1)
)

const offsetY = computed(() => {
  let h = 0
  for (let i = 0; i < visibleRange.value.start; i++) {
    h += flatItems.value[i].type === 'separator' ? SEP_HEIGHT : ROW_HEIGHT
  }
  return h
})

function updateViewport() {
  if (scrollContainer.value) {
    viewportHeight.value = scrollContainer.value.clientHeight || window.innerHeight
  }
}

function onScroll() {
  if (rafId) return
  rafId = requestAnimationFrame(() => {
    scrollTop.value = window.scrollY || document.documentElement.scrollTop
    rafId = null
  })
}

onMounted(() => {
  updateViewport()
  window.addEventListener('scroll', onScroll, { passive: true })
  window.addEventListener('resize', updateViewport, { passive: true })
})

onUnmounted(() => {
  window.removeEventListener('scroll', onScroll)
  window.removeEventListener('resize', updateViewport)
  if (rafId) cancelAnimationFrame(rafId)
})

// 切换排序/筛选时回到顶部
watch([sortBy, selectedCategory, contentType, searchQuery], () => {
  nextTick(() => window.scrollTo({ top: 0, behavior: 'instant' }))
})
</script>
