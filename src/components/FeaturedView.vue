<template>
  <div>
    <div class="mb-6">
      <h2 class="text-lg font-light text-slate-800 dark:text-slate-100 mb-1">精选</h2>
      <p class="text-xs text-slate-400 dark:text-slate-500">综合评分 ≥ 7.5 的高分文献</p>
    </div>

    <!-- 分类筛选 -->
    <div class="flex flex-wrap gap-2 mb-8">
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
        {{ cat === 'all' ? '全部' : cat }}
      </button>
    </div>

    <div v-if="filtered.length === 0" class="text-sm text-slate-400 dark:text-slate-500 py-12 text-center">
      暂无精选文献
    </div>

    <!-- 按日期分组 -->
    <template v-for="group in groupedByDate" :key="group.date">
      <div class="flex items-center gap-4 mb-6 mt-2">
        <div class="h-px flex-1 bg-gray-200 dark:bg-slate-800"></div>
        <span class="text-xs text-slate-400 dark:text-slate-500 whitespace-nowrap">{{ group.date || '无日期' }}</span>
        <div class="h-px flex-1 bg-gray-200 dark:bg-slate-800"></div>
      </div>
      <PaperCard
        v-for="item in group.items"
        :key="item.id"
        v-memo="[item.id === selectedItem?.id]"
        :paper="item"
        show-composite
        :is-selected="selectedItem?.id === item.id"
        @select="$emit('select', $event)"
      />
    </template>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import PaperCard from './PaperCard.vue'

const props = defineProps({
  items: { type: Array, default: () => [] },
  selectedItem: { type: Object, default: null },
})

defineEmits(['select'])

const selectedCategory = ref('all')

const categories = computed(() => {
  const cats = new Set(props.items.map((p) => p.category))
  return ['all', ...cats]
})

const filtered = computed(() => {
  let result = props.items
  if (selectedCategory.value !== 'all') {
    result = result.filter((p) => p.category === selectedCategory.value)
  }
  return result.slice().sort((a, b) => new Date(b.date || 0) - new Date(a.date || 0))
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
