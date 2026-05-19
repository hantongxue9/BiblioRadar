<template>
  <article
    class="bg-white border rounded-xl p-6 mb-4 transition-shadow hover:shadow-sm cursor-pointer"
    :class="paper.content_type === 'news' ? 'border-l-2 border-l-blue-300 border-gray-100' : 'border-gray-100'"
    @click="expanded = !expanded"
  >
    <!-- 头部：标题 + 综合分 + 日期 -->
    <div class="flex items-start justify-between gap-4 mb-3">
      <h2 class="text-base font-medium text-slate-800 leading-relaxed flex-1">
        {{ paper.title }}
      </h2>
      <div class="flex items-center gap-2 flex-shrink-0">
        <span v-if="paper.featured" class="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-white">精选</span>
        <span v-if="showComposite && paper.composite_score != null" class="text-lg font-medium text-slate-700 tabular-nums">
          {{ paper.composite_score }}
        </span>
        <span class="text-xs text-slate-400">{{ paper.date }}</span>
      </div>
    </div>

    <!-- 标签行 -->
    <div class="flex items-center gap-3 mb-4">
      <span
        class="text-xs px-2.5 py-0.5 rounded-full"
        :class="paper.content_type === 'news' ? 'bg-blue-50 text-blue-500' : 'bg-slate-100 text-slate-500'"
      >
        {{ paper.category }}
      </span>
      <span v-if="paper.content_type === 'news'" class="text-xs text-slate-400">{{ paper.source }}</span>
      <span v-else-if="paper.affiliations" class="text-xs text-slate-400">{{ paper.affiliations }}</span>
    </div>

    <!-- 一句话提炼 -->
    <p class="text-sm text-slate-600 leading-relaxed mb-5">
      {{ paper.one_sentence_summary }}
    </p>

    <!-- 评分区域 -->
    <div v-if="paper.content_type === 'news'" class="flex gap-6 mb-2">
      <ScoreBar label="时效性" :score="paper.scores.timeliness" />
      <ScoreBar label="领域相关性" :score="paper.scores.relevance" />
      <ScoreBar label="信息价值" :score="paper.scores.information_value" />
    </div>
    <div v-else class="flex gap-6 mb-2">
      <ScoreBar label="前沿技术度" :score="paper.scores.frontier_tech" />
      <ScoreBar label="业务落地值" :score="paper.scores.practical_value" />
      <ScoreBar label="方法严谨性" :score="paper.scores.methodological_rigor" />
    </div>

    <!-- 展开区域 -->
    <Transition name="fade">
      <div v-if="expanded" class="mt-6 pt-6 border-t border-gray-100">
        <div class="mb-5">
          <h3 class="text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">
            {{ paper.content_type === 'news' ? 'Content' : 'Abstract' }}
          </h3>
          <p class="text-sm text-slate-600 leading-relaxed">{{ paper.abstract }}</p>
        </div>

        <div>
          <h3 class="text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">评分依据</h3>
          <p class="text-sm text-slate-500 leading-relaxed italic">{{ paper.thinking }}</p>
        </div>

        <a
          :href="paper.link"
          target="_blank"
          rel="noopener"
          class="inline-block mt-4 text-xs text-slate-400 hover:text-slate-600 transition-colors"
          @click.stop
        >
          查看原文 →
        </a>
      </div>
    </Transition>
  </article>
</template>

<script setup>
import { ref } from 'vue'
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
})

const expanded = ref(false)
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
