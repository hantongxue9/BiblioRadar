<template>
  <div>
    <div class="mb-6">
      <h2 class="text-lg font-light text-slate-800 dark:text-slate-100 mb-1.5">收藏</h2>
      <div class="w-8 h-0.5 bg-ustc-300 rounded mb-2"></div>
      <p class="text-xs text-slate-400 dark:text-slate-500">收藏的文献，可批量导出</p>
    </div>

    <div v-if="savedItems.length === 0" class="text-sm text-slate-400 dark:text-slate-500 py-12 text-center">
      暂无收藏，点击卡片上的书签图标添加
    </div>

    <template v-else>
      <div class="flex items-center gap-3 mb-6">
        <span class="text-xs text-slate-400 dark:text-slate-500">共 {{ savedItems.length }} 条</span>
        <span class="w-px h-3 bg-slate-200 dark:bg-slate-700"></span>
        <button @click="handleExport('ris')" class="text-xs text-slate-500 hover:text-ustc-500 dark:text-slate-400 dark:hover:text-ustc-300 transition-colors">导出 RIS</button>
        <button @click="handleExport('bib')" class="text-xs text-slate-500 hover:text-ustc-500 dark:text-slate-400 dark:hover:text-ustc-300 transition-colors">导出 BibTeX</button>
        <button @click="handleExport('csv')" class="text-xs text-slate-500 hover:text-ustc-500 dark:text-slate-400 dark:hover:text-ustc-300 transition-colors">导出 CSV</button>
        <span class="flex-1"></span>
        <button @click="clearAll" class="text-xs text-slate-400 hover:text-red-500 dark:text-slate-500 dark:hover:text-red-400 transition-colors">清空</button>
      </div>

      <PaperCard
        v-for="item in savedItems"
        :key="item.id"
        :paper="item"
        show-composite
        :is-selected="selectedItem?.id === item.id"
        :is-saved="true"
        @select="$emit('select', $event)"
        @toggle-save="toggleSave"
      />
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import PaperCard from '../cards/PaperCard.vue'
import { useReadingList } from '../../composables/useReadingList'
import { download } from '../../utils/export'

/**
 * @typedef {import('../../utils/types').PaperItem} PaperItem
 */

const props = defineProps({
  /** @type {PaperItem[]} */
  items: { type: Array, default: () => [] },
  /** @type {PaperItem|null} */
  selectedItem: { type: Object, default: null },
})

defineEmits(['select'])

const { savedIds, toggleSave, clearAll } = useReadingList()

const savedItems = computed(() => {
  const idSet = new Set(savedIds.value)
  return props.items.filter((p) => idSet.has(p.id))
})

function handleExport(format) {
  if (savedItems.value.length === 0) return
  download(savedItems.value, format)
}
</script>
