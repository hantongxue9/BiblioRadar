<template>
  <div
    class="flex items-start gap-4 py-3 px-4 mb-2 rounded-lg hover:bg-slate-50/50 cursor-pointer transition-colors"
    @click="expanded = !expanded"
  >
    <!-- 综合分 -->
    <div class="flex-shrink-0 w-10 text-center pt-0.5">
      <span
        class="text-base font-medium tabular-nums"
        :class="paper.featured ? 'text-slate-800' : 'text-slate-400'"
      >
        {{ paper.composite_score }}
      </span>
    </div>

    <!-- 内容 -->
    <div class="flex-1 min-w-0">
      <div class="flex items-start gap-2">
        <h3 class="text-sm text-slate-700 leading-relaxed flex-1">{{ paper.title }}</h3>
        <span v-if="paper.featured" class="flex-shrink-0 text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-white">
          精选
        </span>
      </div>
      <p class="text-xs text-slate-400 mt-1 line-clamp-2">{{ paper.one_sentence_summary }}</p>

      <!-- 展开区域 -->
      <Transition name="fade">
        <div v-if="expanded" class="mt-3 pt-3 border-t border-gray-100">
          <p class="text-xs text-slate-500 leading-relaxed">{{ paper.abstract }}</p>
          <a
            :href="paper.link"
            target="_blank"
            rel="noopener"
            class="inline-block mt-2 text-xs text-slate-400 hover:text-slate-600 transition-colors"
            @click.stop
          >
            查看原文 →
          </a>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  paper: { type: Object, required: true },
})

const expanded = ref(false)
</script>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
