<template>
  <aside
    class="fixed left-0 top-0 h-full w-52 bg-white border-r border-gray-100 flex flex-col z-10
           max-md:w-full max-md:h-auto max-md:relative max-md:border-r-0 max-md:border-b
           dark:bg-slate-900 dark:border-slate-800"
  >
    <!-- 标题 -->
    <div class="px-5 pt-8 pb-6 max-md:px-4 max-md:pt-5 max-md:pb-3">
      <h1 class="text-lg font-light tracking-tight text-slate-800 dark:text-slate-100">图情雷达</h1>
      <p class="text-xs text-slate-400 dark:text-slate-500 mt-1">BiblioRadar</p>
    </div>

    <!-- 导航 -->
    <nav class="flex-1 px-3 max-md:flex max-md:gap-1 max-md:px-4 max-md:pb-3">
      <button
        v-for="item in navItems"
        :key="item.key"
        @click="$emit('navigate', item.key)"
        class="w-full text-left px-3 py-2.5 text-sm rounded-md transition-colors mb-1
               max-md:px-2.5 max-md:py-1.5 max-md:text-xs max-md:rounded
               flex items-center gap-2"
        :class="
          currentView === item.key
            ? 'text-slate-800 font-medium bg-slate-50 border-l-2 border-slate-800 max-md:border-l-0 max-md:border-b-2 max-md:rounded-b-none dark:text-slate-100 dark:bg-slate-800 dark:border-slate-400'
            : 'text-slate-400 hover:text-slate-600 hover:bg-slate-50/50 dark:text-slate-500 dark:hover:text-slate-300 dark:hover:bg-slate-800/50'
        "
      >
        {{ item.label }}
      </button>
    </nav>

    <!-- 主题切换 -->
    <div class="px-5 pb-3 max-md:hidden">
      <div class="flex items-center gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-1">
        <button
          v-for="opt in themeOptions"
          :key="opt.value"
          @click="setTheme(opt.value)"
          class="flex-1 flex items-center justify-center py-1.5 rounded-md text-xs transition-colors"
          :class="
            theme === opt.value
              ? 'bg-white text-slate-700 shadow-sm dark:bg-slate-700 dark:text-slate-200'
              : 'text-slate-400 hover:text-slate-600 dark:text-slate-500 dark:hover:text-slate-300'
          "
          :title="opt.label"
        >
          <span v-html="opt.icon" />
        </button>
      </div>
    </div>

    <!-- 底部提示 -->
    <div class="px-5 pb-6 max-md:hidden">
      <p class="text-[10px] text-slate-300 dark:text-slate-600 leading-relaxed">
        数据由大模型辅助评分<br />仅供参考
      </p>
    </div>
  </aside>
</template>

<script setup>
import { useTheme } from '../composables/useTheme'

defineProps({
  currentView: String,
})

defineEmits(['navigate'])

const { theme, setTheme } = useTheme()

const navItems = [
  { key: 'featured', label: '精选' },
  { key: 'all', label: '全部' },
  { key: 'daily', label: '日报' },
  { key: 'about', label: '关于' },
]

const themeOptions = [
  {
    value: 'light',
    label: '浅色',
    icon: '<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle cx="12" cy="12" r="5" stroke-width="1.5"/><path stroke-width="1.5" d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>',
  },
  {
    value: 'system',
    label: '跟随系统',
    icon: '<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><rect x="2" y="3" width="20" height="14" rx="2" stroke-width="1.5"/><path stroke-width="1.5" d="M8 21h8M12 17v4"/></svg>',
  },
  {
    value: 'dark',
    label: '深色',
    icon: '<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-width="1.5" d="M21 12.79A9 9 0 1111.21 3a7 7 0 009.79 9.79z"/></svg>',
  },
]
</script>
