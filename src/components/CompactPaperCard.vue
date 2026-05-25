<template>
  <div
    class="flex items-start gap-4 py-3 px-4 mb-2 rounded-lg hover:bg-slate-50/50 dark:hover:bg-slate-800/50 cursor-pointer transition-colors"
    :class="isSelected ? 'bg-slate-50 border-l-2 border-l-slate-800 dark:bg-slate-800 dark:border-l-slate-400' : ''"
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
        <span v-if="paper.featured" class="flex-shrink-0 text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-white dark:bg-slate-200 dark:text-slate-900">
          精选
        </span>
      </div>
      <p class="text-xs text-slate-400 dark:text-slate-500 mt-1" style="display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden">{{ paper.one_sentence_summary }}</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  paper: { type: Object, required: true },
  isSelected: { type: Boolean, default: false },
})

defineEmits(['select'])
</script>
