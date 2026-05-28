<template>
  <aside
    class="fixed left-0 top-0 h-full w-52 bg-white border-r border-gray-100 flex flex-col z-10
           max-md:w-full max-md:h-auto max-md:relative max-md:border-r-0 max-md:border-b
           dark:bg-slate-900 dark:border-slate-800"
  >
    <!-- 品牌区 -->
    <div class="px-5 pt-7 pb-5 max-md:px-4 max-md:pt-4 max-md:pb-2 border-b border-gray-100/60 dark:border-slate-800/60">
      <div class="flex items-center gap-2.5">
        <!-- Logo: 雷达扫描 + 文档 -->
        <svg class="w-8 h-8 text-indigo-500 dark:text-indigo-400 flex-shrink-0" viewBox="0 0 32 32" fill="none">
          <!-- 外圈 -->
          <circle cx="16" cy="16" r="13" stroke="currentColor" stroke-width="1.2" stroke-opacity="0.3"/>
          <circle cx="16" cy="16" r="8" stroke="currentColor" stroke-width="1.2" stroke-opacity="0.2"/>
          <!-- 十字线 -->
          <line x1="16" y1="3" x2="16" y2="29" stroke="currentColor" stroke-width="0.6" stroke-opacity="0.15"/>
          <line x1="3" y1="16" x2="29" y2="16" stroke="currentColor" stroke-width="0.6" stroke-opacity="0.15"/>
          <!-- 扫描弧 -->
          <path d="M16 3 A13 13 0 0 1 27.26 10.5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <!-- 扫描线 -->
          <line x1="16" y1="16" x2="27.26" y2="10.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          <!-- 中心文档 -->
          <rect x="12" y="12" width="8" height="10" rx="1.5" stroke="currentColor" stroke-width="1.2" fill="currentColor" fill-opacity="0.1"/>
          <line x1="14" y1="15.5" x2="18" y2="15.5" stroke="currentColor" stroke-width="0.8" stroke-linecap="round"/>
          <line x1="14" y1="18" x2="17" y2="18" stroke="currentColor" stroke-width="0.8" stroke-linecap="round"/>
          <line x1="14" y1="20.5" x2="18" y2="20.5" stroke="currentColor" stroke-width="0.8" stroke-linecap="round"/>
        </svg>
        <div>
          <h1 class="text-base font-medium tracking-tight text-slate-800 dark:text-slate-100">图情雷达</h1>
          <p class="text-[10px] text-slate-400 dark:text-slate-500 tracking-wide">BiblioRadar</p>
        </div>
      </div>
    </div>

    <!-- 导航 -->
    <nav class="flex-1 px-3 py-4 max-md:flex max-md:gap-1 max-md:px-4 max-md:py-2 max-md:pb-3">
      <button
        v-for="item in navItems"
        :key="item.key"
        @click="$emit('navigate', item.key)"
        class="w-full text-left px-3 py-2.5 text-sm rounded-lg transition-all mb-1
               max-md:px-2.5 max-md:py-1.5 max-md:text-xs max-md:rounded
               flex items-center gap-2.5"
        :class="
          currentView === item.key
            ? 'text-indigo-700 font-medium bg-indigo-50/70 border-l-2 border-indigo-500 max-md:border-l-0 max-md:border-b-2 max-md:rounded-b-none dark:text-indigo-300 dark:bg-indigo-500/10 dark:border-indigo-400'
            : 'text-slate-400 hover:text-slate-600 hover:bg-slate-50/80 dark:text-slate-500 dark:hover:text-slate-300 dark:hover:bg-slate-800/50'
        "
      >
        <span v-html="item.icon" class="flex-shrink-0 w-4 h-4" />
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
  {
    key: 'featured',
    label: '精选',
    icon: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 1.5l1.85 3.75L14 5.9l-3 2.92.71 4.13L8 10.88l-3.71 2.07.71-4.13-3-2.92 4.15-.65L8 1.5z"/></svg>',
  },
  {
    key: 'all',
    label: '全部',
    icon: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"><line x1="3" y1="4" x2="13" y2="4"/><line x1="3" y1="8" x2="13" y2="8"/><line x1="3" y1="12" x2="10" y2="12"/></svg>',
  },
  {
    key: 'daily',
    label: '日报',
    icon: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2.5" width="12" height="11.5" rx="1.5"/><line x1="2" y1="6" x2="14" y2="6"/><line x1="5.5" y1="1" x2="5.5" y2="3.5"/><line x1="10.5" y1="1" x2="10.5" y2="3.5"/></svg>',
  },
  {
    key: 'about',
    label: '关于',
    icon: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.2"><circle cx="8" cy="8" r="6"/><line x1="8" y1="7" x2="8" y2="11" stroke-linecap="round"/><circle cx="8" cy="5" r="0.5" fill="currentColor" stroke="none"/></svg>',
  },
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
