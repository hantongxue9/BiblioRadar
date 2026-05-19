<template>
  <div class="max-w-3xl mx-auto px-6 mb-12">
    <div class="flex flex-col sm:flex-row gap-3">
      <!-- 搜索框 -->
      <input
        :value="searchQuery"
        @input="$emit('update:searchQuery', $event.target.value)"
        type="text"
        placeholder="搜索标题或摘要..."
        class="flex-1 px-4 py-2.5 text-sm text-slate-700 bg-white border border-gray-200 rounded-lg
               placeholder:text-slate-300 focus:outline-none focus:border-slate-400 transition-colors"
      />

      <!-- 分类筛选 -->
      <select
        :value="selectedCategory"
        @change="$emit('update:selectedCategory', $event.target.value)"
        class="px-4 py-2.5 text-sm text-slate-700 bg-white border border-gray-200 rounded-lg
               focus:outline-none focus:border-slate-400 transition-colors cursor-pointer"
      >
        <option value="all">全部分类</option>
        <option value="计量与评价">计量与评价</option>
        <option value="技术与工具">技术与工具</option>
      </select>

      <!-- 排序 -->
      <select
        :value="sortBy"
        @change="$emit('update:sortBy', $event.target.value)"
        class="px-4 py-2.5 text-sm text-slate-700 bg-white border border-gray-200 rounded-lg
               focus:outline-none focus:border-slate-400 transition-colors cursor-pointer"
      >
        <option value="date">按时间排序</option>
        <option value="score">按评分排序</option>
      </select>
    </div>
  </div>
</template>

<script setup>
defineProps({
  searchQuery: String,
  selectedCategory: String,
  sortBy: String,
})

defineEmits(['update:searchQuery', 'update:selectedCategory', 'update:sortBy'])
</script>
