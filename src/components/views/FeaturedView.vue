<template>
  <div>
    <div class="mb-6">
      <div class="flex items-start justify-between">
        <div>
          <h2 class="text-lg font-light text-slate-800 dark:text-slate-100 mb-1.5">精选</h2>
          <div class="w-8 h-0.5 bg-ustc-300 rounded mb-2"></div>
          <p class="text-xs text-slate-400 dark:text-slate-500">综合评分 ≥ 7.5 的高分文献</p>
        </div>
        <div class="flex items-center gap-2 mt-1">
          <button
            v-if="selectionMode && paginatedItems.length > 0"
            @click="handleSelectAll"
            class="text-xs px-3 py-1 rounded-full text-slate-500 hover:text-slate-700 bg-slate-100 hover:bg-slate-200 dark:text-slate-400 dark:hover:text-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 transition-colors"
          >
            全选当前页
          </button>
          <button
            @click="selectionMode = !selectionMode"
            class="text-xs px-3 py-1 rounded-full transition-colors"
            :class="selectionMode
              ? 'bg-ustc-500 text-white dark:bg-ustc-400 dark:text-slate-900'
              : 'text-slate-500 hover:text-slate-700 bg-slate-100 hover:bg-slate-200 dark:text-slate-400 dark:hover:text-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700'"
          >
            {{ selectionMode ? '完成' : '选择' }}
          </button>
        </div>
      </div>
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

    <p class="text-xs text-slate-400 dark:text-slate-500 mb-6">共 {{ filtered.length }} 条</p>

    <div v-if="filtered.length === 0" class="text-sm text-slate-400 dark:text-slate-500 py-12 text-center">
      暂无精选文献
    </div>

    <!-- 按日期分组 -->
    <template v-for="group in pageGroups" :key="group.date ?? 'flat'">
      <div v-if="group.date" class="flex items-center gap-4 mb-6 mt-2">
        <div class="h-px flex-1 bg-gray-200 dark:bg-slate-800"></div>
        <span class="text-xs text-slate-400 dark:text-slate-500 whitespace-nowrap">{{ group.date }}</span>
        <div class="h-px flex-1 bg-gray-200 dark:bg-slate-800"></div>
      </div>
      <PaperCard
        v-for="item in group.items"
        :key="item.id"
        v-memo="[item.id === selectedItem?.id, selectedIds.includes(item.id)]"
        :paper="item"
        show-composite
        :is-selected="selectedItem?.id === item.id"
        :selectable="selectionMode"
        :is-item-selected="selectedIds.includes(item.id)"
        @select="$emit('select', $event)"
        @toggle-select="toggleSelect"
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
import { ref, computed, watch } from 'vue'
import PaperCard from '../cards/PaperCard.vue'
import {
  groupItemsByDate,
  paginateItems,
  sortItems,
  uniqueCategories,
  visiblePageNumbers,
} from '../../utils/itemList'
import { PER_PAGE } from '../../utils/constants'

/**
 * @typedef {import('../../utils/types').PaperItem} PaperItem
 */

const props = defineProps({
  /** @type {PaperItem[]} */
  items: { type: Array, default: () => [] },
  /** @type {PaperItem|null} */
  selectedItem: { type: Object, default: null },
  /** @type {Array} */
  selectedIds: { type: Array, default: () => [] },
  toggleSelect: { type: Function, default: () => {} },
  selectAll: { type: Function, default: () => {} },
})

defineEmits(['select'])

const selectedCategory = ref('all')
const currentPage = ref(1)
const perPage = PER_PAGE
const selectionMode = ref(false)

function handleSelectAll() {
  props.selectAll(paginatedItems.value.map((i) => i.id))
}

watch(selectedCategory, () => { currentPage.value = 1 })

const categories = computed(() => {
  return uniqueCategories(props.items, { includeAll: true })
})

const filtered = computed(() => {
  let result = props.items
  if (selectedCategory.value !== 'all') {
    result = result.filter((p) => p.category === selectedCategory.value)
  }
  return sortItems(result, 'date')
})

const totalPages = computed(() => Math.ceil(filtered.value.length / perPage))

const paginatedItems = computed(() => {
  return paginateItems(filtered.value, currentPage.value, perPage)
})

const visiblePages = computed(() => {
  return visiblePageNumbers(totalPages.value, currentPage.value)
})

const pageGroups = computed(() => {
  return groupItemsByDate(paginatedItems.value)
})
</script>
