<template>
  <component
    :is="item.link ? 'a' : 'div'"
    v-bind="item.link ? { href: item.link, target: '_blank', rel: 'noopener' } : {}"
    class="flex items-start gap-4 py-3 px-4 mb-2 rounded-lg hover:bg-slate-50/50 dark:hover:bg-slate-800/50 transition-colors group"
  >
    <!-- 来源标签 -->
    <div class="flex-shrink-0 pt-0.5">
      <span class="text-[10px] px-1.5 py-0.5 rounded bg-blue-50 text-blue-500 border border-blue-100 dark:bg-blue-900/30 dark:text-blue-400 dark:border-blue-800">
        {{ item.source }}
      </span>
    </div>

    <!-- 内容 -->
    <div class="flex-1 min-w-0">
      <h3 class="text-sm text-slate-700 dark:text-slate-200 leading-relaxed group-hover:text-slate-900 dark:group-hover:text-slate-100 transition-colors">
        {{ item.title }}
      </h3>
      <p class="text-xs text-slate-400 dark:text-slate-500 mt-1" style="display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden">{{ item.one_sentence_summary }}</p>
    </div>
  </component>
</template>

<script setup>
defineProps({
  item: { type: Object, required: true },
})
</script>
