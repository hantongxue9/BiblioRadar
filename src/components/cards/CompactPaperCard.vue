<template>
  <div
    class="flex items-start gap-4 py-3 px-4 mb-2 rounded-lg hover:bg-slate-50/50 dark:hover:bg-slate-800/50 cursor-pointer transition-colors"
    :class="isSelected ? 'bg-ustc-50/40 border-l-2 border-l-ustc-400 dark:bg-ustc-500/10 dark:border-l-ustc-500' : ''"
    @click="$emit('select', paper)"
  >
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
})

defineEmits(['select'])
</script>
