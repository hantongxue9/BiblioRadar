<template>
  <Transition name="slide-panel">
    <aside
      v-if="item"
      class="fixed right-0 top-0 h-screen w-[420px] max-xl:w-[340px] max-lg:w-[280px] max-md:w-full bg-white dark:bg-slate-900
             border-l border-gray-100 dark:border-slate-800 shadow-xl z-50 flex flex-col
             will-change-transform"
    >
      <!-- 头部 -->
      <div class="flex-shrink-0 px-6 max-md:px-4 pt-6 pb-4 border-b border-gray-100 dark:border-slate-800">
        <div class="flex items-start justify-between mb-3">
          <div class="flex items-center gap-2">
            <span v-if="item.featured" class="text-[10px] px-2 py-0.5 rounded-full bg-ustc-50 text-ustc-500 dark:bg-ustc-900/30 dark:text-ustc-300 font-medium">精选</span>
            <span v-if="item.composite_score != null" class="text-lg font-medium text-slate-700 dark:text-slate-300 tabular-nums">
              {{ item.composite_score }}
            </span>
          </div>
          <button
            @click="$emit('close')"
            class="p-1 -mr-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <h2 class="text-base font-medium text-slate-800 dark:text-slate-100 leading-relaxed mb-3">
          {{ item.title }}
        </h2>

        <div class="flex items-center gap-3 flex-wrap">
          <span
            class="text-xs px-2.5 py-0.5 rounded-full"
            :class="item.content_type === 'news' ? 'bg-ustc-50 text-ustc-500 dark:bg-ustc-900/30 dark:text-ustc-300' : 'bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400'"
          >
            {{ item.category }}
          </span>
          <span v-if="item.source" class="text-xs text-slate-400 dark:text-slate-500">{{ item.source }}</span>
          <span v-if="item.tier" class="text-xs text-slate-300 dark:text-slate-600">{{ item.tier }}类</span>
          <span class="text-xs text-slate-400 dark:text-slate-500">{{ item.date }}</span>
        </div>
      </div>

      <!-- 内容区 -->
      <div ref="scrollArea" class="flex-1 overflow-y-auto px-6 max-md:px-4 py-5 space-y-6">
        <p class="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
          {{ item.one_sentence_summary }}
        </p>

        <div v-if="item.content_type === 'news'" class="space-y-2">
          <ScoreBar label="时效性" :score="item.scores?.timeliness" color="blue" />
          <ScoreBar label="领域相关性" :score="item.scores?.relevance" color="teal" />
          <ScoreBar label="信息价值" :score="item.scores?.information_value" color="amber" />
        </div>
        <div v-else class="space-y-2">
          <ScoreBar label="前沿技术度" :score="item.scores?.frontier_tech" color="blue" />
          <ScoreBar label="业务落地值" :score="item.scores?.practical_value" color="teal" />
          <ScoreBar label="方法严谨性" :score="item.scores?.methodological_rigor" color="amber" />
        </div>

        <div v-if="item.abstract">
          <h3 class="text-xs font-medium text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-2">
            {{ item.content_type === 'news' ? '内容摘要' : '摘要' }}
          </h3>
          <p class="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">{{ item.abstract }}</p>
        </div>

        <div v-if="item.thinking">
          <h3 class="text-xs font-medium text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-2">评分依据</h3>
          <p class="text-sm text-slate-500 dark:text-slate-400 leading-relaxed italic">{{ item.thinking }}</p>
        </div>

        <div v-if="item.affiliations" class="text-xs text-slate-400 dark:text-slate-500">
          <span class="font-medium text-slate-500 dark:text-slate-400">机构：</span>{{ item.affiliations }}
        </div>
      </div>

      <!-- 底部 -->
      <div class="flex-shrink-0 px-6 max-md:px-4 py-4 border-t border-gray-100 dark:border-slate-800">
        <a
          v-if="item.link"
          :href="item.link"
          target="_blank"
          rel="noopener"
          class="text-xs text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200 transition-colors"
        >
          查看原文
        </a>
        <span class="text-xs text-slate-300 dark:text-slate-600 mx-2">·</span>
        <span class="text-[11px] text-slate-400 dark:text-slate-500">导出</span>
        <button @click="exportSingle('ris')" class="text-xs text-slate-500 hover:text-ustc-500 dark:text-slate-400 dark:hover:text-ustc-300 transition-colors ml-2">RIS</button>
        <button @click="exportSingle('bib')" class="text-xs text-slate-500 hover:text-ustc-500 dark:text-slate-400 dark:hover:text-ustc-300 transition-colors ml-1.5">BibTeX</button>
        <button @click="exportSingle('csv')" class="text-xs text-slate-500 hover:text-ustc-500 dark:text-slate-400 dark:hover:text-ustc-300 transition-colors ml-1.5">CSV</button>
      </div>
    </aside>
  </Transition>

  <!-- 移动端遮罩 -->
  <Transition name="fade">
    <div
      v-if="item"
      class="fixed inset-0 bg-black/20 dark:bg-black/50 z-40 max-md:block hidden"
      @click="$emit('close')"
    />
  </Transition>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import ScoreBar from '../cards/ScoreBar.vue'
import { download } from '../../utils/export.js'

/**
 * @typedef {import('../../utils/types').PaperItem} PaperItem
 */

const props = defineProps({
  /** @type {PaperItem|null} */
  item: { type: Object, default: null },
})

const emit = defineEmits(['close'])

const scrollArea = ref(null)
watch(() => props.item, () => {
  scrollArea.value?.scrollTo(0, 0)
})

function exportSingle(fmt) {
  if (props.item) download([props.item], fmt)
}

function onKeydown(e) {
  if (e.key === 'Escape') emit('close')
}

onMounted(() => window.addEventListener('keydown', onKeydown))
onUnmounted(() => window.removeEventListener('keydown', onKeydown))
</script>

<style scoped>
.slide-panel-enter-active,
.slide-panel-leave-active {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.slide-panel-enter-from,
.slide-panel-leave-to {
  transform: translateX(100%);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
