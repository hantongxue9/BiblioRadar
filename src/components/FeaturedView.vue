<template>
  <div>
    <div class="mb-6">
      <h2 class="text-lg font-light text-slate-800 mb-1">精选</h2>
      <p class="text-xs text-slate-400">综合评分 ≥ 7.5 的高分文献</p>
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
            ? 'bg-slate-800 text-white'
            : 'bg-slate-100 text-slate-500 hover:bg-slate-200'
        "
      >
        {{ cat === 'all' ? '全部' : cat }}
      </button>
    </div>

    <div v-if="filtered.length === 0" class="text-sm text-slate-400 py-12 text-center">
      暂无精选文献
    </div>

    <PaperCard v-for="paper in filtered" :key="paper.id" :paper="paper" show-composite />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import PaperCard from './PaperCard.vue'

const props = defineProps({
  items: { type: Array, default: () => [] },
})

const selectedCategory = ref('all')

const categories = computed(() => {
  const cats = new Set(props.items.map((p) => p.category))
  return ['all', ...cats]
})

const filtered = computed(() => {
  let result = [...props.items]
  if (selectedCategory.value !== 'all') {
    result = result.filter((p) => p.category === selectedCategory.value)
  }
  return result.sort((a, b) => (b.composite_score || 0) - (a.composite_score || 0))
})
</script>
