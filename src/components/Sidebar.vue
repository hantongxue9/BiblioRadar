<template>
  <aside
    class="fixed left-0 top-0 h-full w-52 bg-white border-r border-gray-100 flex flex-col z-10
           max-md:w-full max-md:h-auto max-md:relative max-md:border-r-0 max-md:border-b"
  >
    <!-- 标题 -->
    <div class="px-5 pt-8 pb-6 max-md:px-4 max-md:pt-5 max-md:pb-3">
      <h1 class="text-lg font-light tracking-tight text-slate-800">Scholar-Radar</h1>
      <p class="text-xs text-slate-400 mt-1">图情科研雷达</p>
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
            ? 'text-slate-800 font-medium bg-slate-50 border-l-2 border-slate-800 max-md:border-l-0 max-md:border-b-2 max-md:rounded-b-none'
            : 'text-slate-400 hover:text-slate-600 hover:bg-slate-50/50'
        "
      >
        {{ item.label }}
      </button>
    </nav>

    <!-- 底部提示 -->
    <div class="px-5 pb-6 max-md:hidden">
      <p class="text-[10px] text-slate-300 leading-relaxed">
        数据由大模型辅助评分<br />仅供参考
      </p>
    </div>
  </aside>
</template>

<script setup>
defineProps({
  currentView: String,
})

defineEmits(['navigate'])

const navItems = [
  { key: 'featured', label: '精选' },
  { key: 'all', label: '全部' },
  { key: 'daily', label: '日报' },
  { key: 'about', label: '关于' },
]
</script>
