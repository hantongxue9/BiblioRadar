<template>
  <div class="flex items-center gap-2">
    <span class="text-xs text-slate-400 dark:text-slate-500 whitespace-nowrap">{{ label }}</span>
    <div class="flex gap-0.5">
      <div
        v-for="i in 10"
        :key="i"
        class="w-2 h-4 rounded-sm transition-colors"
        :class="i > score ? 'bg-gray-100 dark:bg-slate-800' : colorClass"
        :style="i <= score ? { opacity: 0.15 + (i - 1) * 0.094 } : {}"
      />
    </div>
    <span class="text-xs font-medium text-slate-500 dark:text-slate-400 tabular-nums">{{ score }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: String,
  score: { type: Number, default: 0 },
  color: { type: String, default: 'blue' },
})

const colorClassMap = {
  blue: 'bg-ustc-400 dark:bg-ustc-500',
  teal: 'bg-teal-400 dark:bg-teal-500',
  amber: 'bg-amber-400 dark:bg-amber-500',
  slate: 'bg-slate-400 dark:bg-slate-500',
}

const colorClass = computed(() => colorClassMap[props.color] || colorClassMap.slate)
</script>
