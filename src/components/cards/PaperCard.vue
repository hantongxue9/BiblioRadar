<template>
  <article
    class="bg-white border rounded-xl p-6 mb-4 hover:shadow-sm cursor-pointer transition-shadow
           dark:bg-slate-900 dark:border-slate-800 dark:hover:shadow-none"
    :class="[
      isSelected ? 'border-l-2 border-l-ustc-400 bg-ustc-50/30 dark:border-l-ustc-500 dark:bg-ustc-500/5' : 'border-gray-100 dark:border-slate-800',
      paper.content_type === 'news' && !isSelected ? 'border-l-2 border-l-ustc-200 dark:border-l-ustc-700' : '',
      selectable && isItemSelected ? 'ring-1 ring-ustc-300/50 dark:ring-ustc-500/30' : '',
    ]"
    @click="$emit('select', paper)"
  >
    <div class="flex items-start gap-3">
      <!-- 复选框 -->
      <button
        v-if="selectable"
        @click.stop="$emit('toggle-select', paper.id)"
        class="flex-shrink-0 w-[18px] h-[18px] rounded-full border-2 transition-all duration-150 flex items-center justify-center mt-1"
        :class="isItemSelected
          ? 'bg-ustc-500 border-ustc-500 dark:bg-ustc-400 dark:border-ustc-400'
          : 'border-slate-300 dark:border-slate-600 hover:border-ustc-400 dark:hover:border-ustc-500'"
        :aria-label="isItemSelected ? '取消选中' : '选中'"
      >
        <svg v-if="isItemSelected" class="w-2.5 h-2.5 text-white" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M2.5 6L5 8.5L9.5 3.5" />
        </svg>
      </button>

      <!-- 内容 -->
      <div class="flex-1 min-w-0">
        <!-- 头部：标题 + 综合分 + 日期 -->
        <div class="flex items-start justify-between gap-4 mb-3">
          <h2 class="text-base font-medium text-slate-800 dark:text-slate-100 leading-relaxed flex-1 min-w-0">
            {{ paper.title }}
          </h2>
          <div class="flex items-center gap-2 flex-shrink-0 max-md:flex-wrap max-md:justify-end">
            <span v-if="paper.featured" class="text-[10px] px-2 py-0.5 rounded-full bg-ustc-50 text-ustc-500 dark:bg-ustc-900/30 dark:text-ustc-300 font-medium">精选</span>
            <span v-if="showComposite && paper.composite_score != null" class="text-lg font-medium text-slate-700 dark:text-slate-300 tabular-nums">
              {{ paper.composite_score }}
            </span>
            <span v-if="paper.credibility_score != null" class="text-xs text-slate-400 dark:text-slate-500 tabular-nums" :title="'可信度 '+paper.credibility_score">· {{ paper.credibility_score }}</span>
            <span class="text-xs text-slate-400 dark:text-slate-500">{{ paper.date }}</span>
            <button
              @click.stop="$emit('toggle-save', paper.id)"
              class="p-0.5 -mr-1 transition-colors"
              :class="isSaved
                ? 'text-ustc-400 hover:text-ustc-500 dark:text-ustc-400 dark:hover:text-ustc-300'
                : 'text-slate-300 hover:text-slate-500 dark:text-slate-600 dark:hover:text-slate-400'"
              :title="isSaved ? '移出阅读清单' : '加入阅读清单'"
            >
              <svg class="w-4 h-4" viewBox="0 0 16 16" :fill="isSaved ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="1.2">
                <path d="M3 2h10a1 1 0 0 1 1 1v11l-6-3-6 3V3a1 1 0 0 1 1-1z" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>
        </div>

        <!-- 标签行 -->
        <div class="flex items-center gap-3 mb-4 min-w-0">
          <span
            class="text-xs px-2.5 py-0.5 rounded-full flex-shrink-0"
            :class="paper.content_type === 'news' ? 'bg-ustc-50 text-ustc-500 dark:bg-ustc-900/30 dark:text-ustc-300' : 'bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400'"
          >
            {{ paper.category }}
          </span>
          <span v-if="paper.tier" class="text-[10px] px-1.5 py-0.5 rounded font-medium text-slate-400 bg-slate-100/70 dark:text-slate-500 dark:bg-slate-800/70">{{ paper.tier }}类</span>
          <span v-if="paper.content_type === 'news'" class="text-xs text-slate-400 dark:text-slate-500 truncate">{{ paper.source }}</span>
          <span v-else-if="paper.affiliations" class="text-xs text-slate-400 dark:text-slate-500 truncate">{{ paper.affiliations }}</span>
        </div>

        <!-- 一句话提炼 -->
        <p class="text-sm text-slate-600 dark:text-slate-400 leading-relaxed mb-5">
          {{ paper.one_sentence_summary }}
        </p>

        <!-- 评分区域 -->
        <div v-if="paper.content_type === 'news'" class="flex flex-wrap gap-x-6 gap-y-2 mb-2 p-3 bg-slate-50/60 rounded-lg dark:bg-slate-800/30">
          <ScoreBar label="时效性" :score="paper.scores?.timeliness" color="blue" />
          <ScoreBar label="领域相关性" :score="paper.scores?.relevance" color="teal" />
          <ScoreBar label="信息价值" :score="paper.scores?.information_value" color="amber" />
        </div>
        <div v-else-if="paper.scores" class="flex flex-wrap gap-x-6 gap-y-2 mb-2 p-3 bg-slate-50/60 rounded-lg dark:bg-slate-800/30">
          <ScoreBar label="前沿技术度" :score="paper.scores.frontier_tech" color="blue" />
          <ScoreBar label="业务落地值" :score="paper.scores.practical_value" color="teal" />
          <ScoreBar label="方法严谨性" :score="paper.scores.methodological_rigor" color="amber" />
        </div>
      </div>
    </div>
  </article>
</template>

<script setup>
import ScoreBar from './ScoreBar.vue'

/**
 * @typedef {import('../../utils/types').PaperItem} PaperItem
 */

defineProps({
  /** @type {PaperItem} */
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
  selectable: {
    type: Boolean,
    default: false,
  },
  isItemSelected: {
    type: Boolean,
    default: false,
  },
  isSaved: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['select', 'toggle-select', 'toggle-save'])
</script>
