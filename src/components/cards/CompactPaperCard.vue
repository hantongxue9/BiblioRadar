<template>
  <div
    class="flex items-start gap-3 py-3 px-4 mb-2 rounded-lg hover:bg-slate-50/50 dark:hover:bg-slate-800/50 cursor-pointer transition-colors"
    :class="[
      isSelected ? 'bg-ustc-50/40 border-l-2 border-l-ustc-400 dark:bg-ustc-500/10 dark:border-l-ustc-500' : '',
      selectable && isItemSelected ? 'ring-1 ring-ustc-300/50 dark:ring-ustc-500/30' : '',
    ]"
    @click="$emit('select', paper)"
  >
    <!-- 复选框 -->
    <button
      v-if="selectable"
      @click.stop="$emit('toggle-select', paper.id)"
      class="flex-shrink-0 w-4 h-4 rounded-full border-2 transition-all duration-150 flex items-center justify-center mt-0.5"
      :class="isItemSelected
        ? 'bg-ustc-500 border-ustc-500 dark:bg-ustc-400 dark:border-ustc-400'
        : 'border-slate-300 dark:border-slate-600 hover:border-ustc-400 dark:hover:border-ustc-500'"
      :aria-label="isItemSelected ? '取消选中' : '选中'"
    >
      <svg v-if="isItemSelected" class="w-2 h-2 text-white" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M2.5 6L5 8.5L9.5 3.5" />
      </svg>
    </button>

    <!-- 综合分 -->
    <div class="flex-shrink-0 w-10 text-center pt-0.5">
      <span
        class="text-base font-medium tabular-nums"
        :class="paper.featured ? 'text-slate-800 dark:text-slate-200' : 'text-slate-400 dark:text-slate-500'"
      >
        {{ paper.composite_score ?? '—' }}
      </span>
    </div>

    <!-- 内容 -->
    <div class="flex-1 min-w-0">
      <div class="flex items-start gap-2">
        <h3 class="text-sm text-slate-700 dark:text-slate-200 leading-relaxed flex-1">{{ paper.title }}</h3>
        <span v-if="paper.featured" class="flex-shrink-0 text-[10px] px-1.5 py-0.5 rounded-full bg-ustc-50 text-ustc-500 dark:bg-ustc-900/30 dark:text-ustc-300 font-medium">
          精选
        </span>
        <button
          @click.stop="$emit('toggle-save', paper.id)"
          class="flex-shrink-0 p-0.5 -mr-1 transition-colors"
          :class="isSaved
            ? 'text-ustc-400 hover:text-ustc-500 dark:text-ustc-400 dark:hover:text-ustc-300'
            : 'text-slate-300 hover:text-slate-500 dark:text-slate-600 dark:hover:text-slate-400'"
          :title="isSaved ? '移出阅读清单' : '加入阅读清单'"
        >
          <svg class="w-3.5 h-3.5" viewBox="0 0 16 16" :fill="isSaved ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="1.2">
            <path d="M3 2h10a1 1 0 0 1 1 1v11l-6-3-6 3V3a1 1 0 0 1 1-1z" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>
      <p class="text-xs text-slate-400 dark:text-slate-500 mt-1" style="display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden">{{ paper.one_sentence_summary }}</p>
    </div>
  </div>
</template>

<script setup>
/**
 * @typedef {import('../../utils/types').PaperItem} PaperItem
 */
defineProps({
  /** @type {PaperItem} */
  paper: { type: Object, required: true },
  isSelected: { type: Boolean, default: false },
  selectable: { type: Boolean, default: false },
  isItemSelected: { type: Boolean, default: false },
  isSaved: { type: Boolean, default: false },
})

defineEmits(['select', 'toggle-select', 'toggle-save'])
</script>
