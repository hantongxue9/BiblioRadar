<template>
  <div class="flex items-center gap-2">
    <span class="text-xs text-slate-400 whitespace-nowrap">{{ label }}</span>
    <div class="flex gap-0.5">
      <div
        v-for="i in 10"
        :key="i"
        class="w-1.5 h-4 rounded-sm transition-colors"
        :class="i <= score ? 'bg-slate-600' : 'bg-gray-100'"
      />
    </div>
    <span class="text-xs font-medium text-slate-500 tabular-nums">{{ score }}</span>
  </div>
</template>

<script setup>
defineProps({
  label: String,
  score: Number,
})
</script>
