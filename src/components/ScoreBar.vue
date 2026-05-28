<template>
  <div class="flex items-center gap-2">
    <span class="text-xs text-slate-400 dark:text-slate-500 whitespace-nowrap">{{ label }}</span>
    <div class="flex gap-0.5">
      <div
        v-for="i in 10"
        :key="i"
        class="w-2 h-4 rounded-sm transition-colors"
        :class="blockClass(i)"
      />
    </div>
    <span class="text-xs font-medium text-slate-500 dark:text-slate-400 tabular-nums">{{ score }}</span>
  </div>
</template>

<script setup>
const props = defineProps({
  label: String,
  score: { type: Number, default: 0 },
})

function blockClass(i) {
  if (i > props.score) return 'bg-gray-100 dark:bg-slate-800'
  if (props.score >= 8) return 'bg-indigo-500 dark:bg-indigo-400'
  if (props.score >= 6) return 'bg-indigo-400/80 dark:bg-indigo-400/70'
  return 'bg-slate-400 dark:bg-slate-500'
}
</script>
