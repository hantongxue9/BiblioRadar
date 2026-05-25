<template>
  <div class="flex items-center gap-2">
    <span class="text-xs text-slate-400 dark:text-slate-500 whitespace-nowrap">{{ label }}</span>
    <div class="flex gap-0.5">
      <div
        v-for="i in 10"
        :key="i"
        class="w-1.5 h-4 rounded-sm"
        :class="i <= score ? 'bg-slate-600 dark:bg-slate-400' : 'bg-gray-100 dark:bg-slate-800'"
      />
    </div>
    <span class="text-xs font-medium text-slate-500 dark:text-slate-400 tabular-nums">{{ score }}</span>
  </div>
</template>

<script setup>
defineProps({
  label: String,
  score: { type: Number, default: 0 },
})
</script>
