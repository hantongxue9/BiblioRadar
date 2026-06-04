<template>
  <div
    class="flex items-start gap-4 py-3 px-4 mb-2 rounded-lg hover:bg-slate-50/50 dark:hover:bg-slate-800/50 cursor-pointer transition-colors relative"
    :class="isSelected ? 'bg-ustc-50/40 border-l-2 border-l-ustc-400 dark:bg-ustc-500/10 dark:border-l-ustc-500' : ''"
    @click="$emit('select', paper)"
  >
    <!-- 选择框 -->
    <button
      class="absolute -right-1 top-1/2 -translate-y-1/2 w-4 h-4 rounded-full border-2 flex items-center justify-center transition-all
             hover:border-ustc-400 dark:hover:border-ustc-500"
      :class="checked ? 'border-ustc-500 bg-ustc-500 dark:border-ustc-400 dark:bg-ustc-400' : 'border-gray-200 dark:border-slate-600'"
      @click.stop="$emit('toggle-select', paper.id)"
    >
      <svg v-if="checked" class="w-2.5 h-2.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/>
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
  checked: { type: Boolean, default: false },
})

defineEmits(['select', 'toggle-select'])
</script>
