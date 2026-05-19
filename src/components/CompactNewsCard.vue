<template>
  <a
    :href="item.link"
    target="_blank"
    rel="noopener"
    class="flex items-start gap-4 py-3 px-4 mb-2 rounded-lg hover:bg-slate-50/50 transition-colors group"
  >
    <!-- 来源标签 -->
    <div class="flex-shrink-0 pt-0.5">
      <span class="text-[10px] px-1.5 py-0.5 rounded bg-blue-50 text-blue-500 border border-blue-100">
        {{ item.source }}
      </span>
    </div>

    <!-- 内容 -->
    <div class="flex-1 min-w-0">
      <h3 class="text-sm text-slate-700 leading-relaxed group-hover:text-slate-900 transition-colors">
        {{ item.title }}
      </h3>
      <p class="text-xs text-slate-400 mt-1 line-clamp-2">{{ item.one_sentence_summary }}</p>
    </div>
  </a>
</template>

<script setup>
defineProps({
  item: { type: Object, required: true },
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
