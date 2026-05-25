<template>
  <article
    class="bg-white border rounded-xl p-6 mb-4 transition-shadow hover:shadow-sm cursor-pointer
           dark:bg-slate-900 dark:border-slate-800 dark:hover:shadow-none"
    :class="[
      isSelected ? 'border-l-2 border-l-slate-800 bg-slate-50/30 dark:border-l-slate-400 dark:bg-slate-800/30' : 'border-gray-100 dark:border-slate-800',
      paper.content_type === 'news' && !isSelected ? 'border-l-2 border-l-blue-300 dark:border-l-blue-700' : '',
    ]"
    @click="$emit('select', paper)"
  >
    <!-- 头部：标题 + 综合分 + 日期 -->
    <div class="flex items-start justify-between gap-4 mb-3">
      <h2 class="text-base font-medium text-slate-800 dark:text-slate-100 leading-relaxed flex-1 min-w-0">
        {{ paper.title }}
      </h2>
      <div class="flex items-center gap-2 flex-shrink-0 max-md:flex-wrap max-md:justify-end">
        <span v-if="paper.featured" class="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-white dark:bg-slate-200 dark:text-slate-900">精选</span>
        <span v-if="showComposite && paper.composite_score != null" class="text-lg font-medium text-slate-700 dark:text-slate-300 tabular-nums">
          {{ paper.composite_score }}
        </span>
        <span class="text-xs text-slate-400 dark:text-slate-500">{{ paper.date }}</span>
      </div>
    </div>

    <!-- 标签行 -->
    <div class="flex items-center gap-3 mb-4 min-w-0">
      <span
        class="text-xs px-2.5 py-0.5 rounded-full flex-shrink-0"
        :class="paper.content_type === 'news' ? 'bg-blue-50 text-blue-500 dark:bg-blue-900/30 dark:text-blue-400' : 'bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400'"
      >
        {{ paper.category }}
      </span>
      <span v-if="paper.content_type === 'news'" class="text-xs text-slate-400 dark:text-slate-500 truncate">{{ paper.source }}</span>
      <span v-else-if="paper.affiliations" class="text-xs text-slate-400 dark:text-slate-500 truncate">{{ paper.affiliations }}</span>
    </div>

    <!-- 一句话提炼 -->
    <p class="text-sm text-slate-600 dark:text-slate-400 leading-relaxed mb-5">
      {{ paper.one_sentence_summary }}
    </p>

    <!-- 评分区域 -->
    <div v-if="paper.content_type === 'news'" class="flex flex-wrap gap-x-6 gap-y-2 mb-2">
      <ScoreBar label="时效性" :score="paper.scores?.timeliness" />
      <ScoreBar label="领域相关性" :score="paper.scores?.relevance" />
      <ScoreBar label="信息价值" :score="paper.scores?.information_value" />
    </div>
    <div v-else-if="paper.scores" class="flex flex-wrap gap-x-6 gap-y-2 mb-2">
      <ScoreBar label="前沿技术度" :score="paper.scores.frontier_tech" />
      <ScoreBar label="业务落地值" :score="paper.scores.practical_value" />
      <ScoreBar label="方法严谨性" :score="paper.scores.methodological_rigor" />
    </div>
  </article>
</template>

<script setup>
import ScoreBar from './ScoreBar.vue'

defineProps({
  paper: {
    type: Object,
    required: true,
  },
  showComposite: {
    type: Boolean,
    default: false,
  },
  isSelected: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['select'])
</script>
