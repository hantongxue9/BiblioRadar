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
  color: { type: String, default: 'blue' },
})

const colorMap = {
  blue:   { high: 'bg-blue-400 dark:bg-blue-500',   mid: 'bg-blue-300/70 dark:bg-blue-500/60',   low: 'bg-blue-200/50 dark:bg-blue-600/40' },
  teal:   { high: 'bg-teal-400 dark:bg-teal-500',   mid: 'bg-teal-300/70 dark:bg-teal-500/60',   low: 'bg-teal-200/50 dark:bg-teal-600/40' },
  amber:  { high: 'bg-amber-400 dark:bg-amber-500', mid: 'bg-amber-300/70 dark:bg-amber-500/60', low: 'bg-amber-200/50 dark:bg-amber-600/40' },
  slate:  { high: 'bg-slate-400 dark:bg-slate-500', mid: 'bg-slate-300/70 dark:bg-slate-500/60', low: 'bg-slate-200/50 dark:bg-slate-600/40' },
}

function blockClass(i) {
  if (i > props.score) return 'bg-gray-100 dark:bg-slate-800'
  const c = colorMap[props.color] || colorMap.slate
  if (props.score >= 8) return c.high
  if (props.score >= 6) return c.mid
  return c.low
}
</script>
