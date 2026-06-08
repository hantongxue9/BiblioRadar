<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-950 flex max-md:flex-col">
    <Sidebar :current-view="currentView" @navigate="onNavigate" />
    <main
      class="flex-1 ml-52 max-md:ml-0 main-push"
      :class="{ 'is-pushed': selectedItem }"
    >
      <div class="max-w-3xl mx-auto px-6 py-10 pb-20 max-md:px-4 max-md:py-6">
        <div v-if="loading">
          <Spinner />
        </div>
        <div v-else-if="error" class="text-center py-12">
          <p class="text-sm text-slate-400 dark:text-slate-500 mb-4">{{ error }}</p>
          <button @click="() => location.reload()" class="text-xs px-4 py-2 rounded-lg bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:hover:bg-slate-700">重试</button>
        </div>
        <KeepAlive v-else>
          <FeaturedView
            v-if="currentView === 'featured'"
            :items="featuredItems"
            :selected-item="selectedItem"
            :selected-ids="selectedIds"
            :toggle-select="toggleSelect"
            :select-all="selectAll"
            @select="onSelect"
          />
          <AllView
            v-else-if="currentView === 'all'"
            :items="papers"
            :selected-item="selectedItem"
            :selected-ids="selectedIds"
            :toggle-select="toggleSelect"
            :select-all="selectAll"
            @select="onSelect"
          />
          <DailyView
            v-else-if="currentView === 'daily'"
            :items="papers"
            :reports="dailyReports"
            :selected-item="selectedItem"
            :selected-ids="selectedIds"
            :toggle-select="toggleSelect"
            :select-all="selectAll"
            @select="onSelect"
          />
          <AboutView v-else-if="currentView === 'about'" />
        </KeepAlive>
      </div>
      <footer class="text-center pb-8">
        <p class="text-xs text-slate-300 dark:text-slate-700">
          数据由大模型辅助评分 · 仅供参考<span v-if="latestDate"> · 更新至 {{ latestDate }}</span>
          · <a href="feed.xml" target="_blank" class="hover:text-slate-500 dark:hover:text-slate-400 transition-colors">RSS</a>
        </p>
      </footer>
    </main>
    <DetailPanel :item="selectedItem" @close="selectedItem = null" />

    <!-- 批量导出工具栏 -->
    <Transition name="toolbar">
      <div v-if="hasSelection" class="fixed bottom-6 left-0 right-0 z-50 flex justify-center pointer-events-none">
        <div class="bg-slate-800 dark:bg-slate-700 text-white rounded-full px-5 py-2.5 shadow-lg flex items-center gap-3 text-sm pointer-events-auto">
          <span class="text-slate-300 tabular-nums">已选 {{ selectionCount }} 条</span>
          <span class="w-px h-4 bg-slate-600"></span>
          <button @click="clearSelection" class="text-slate-300 hover:text-white transition-colors">清除</button>
          <span class="w-px h-4 bg-slate-600"></span>
          <button @click="exportSelected('ris')" class="hover:text-ustc-300 transition-colors font-medium">RIS</button>
          <button @click="exportSelected('bib')" class="hover:text-ustc-300 transition-colors font-medium">BibTeX</button>
          <button @click="exportSelected('csv')" class="hover:text-ustc-300 transition-colors font-medium">CSV</button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { KeepAlive, defineAsyncComponent, watch } from 'vue'
import Sidebar from './components/layout/Sidebar.vue'
import FeaturedView from './components/views/FeaturedView.vue'
import DetailPanel from './components/panels/DetailPanel.vue'
import Spinner from './components/layout/Spinner.vue'
import { useData } from './composables/useData.js'
import { useNavigation } from './composables/useNavigation.js'
import { useSelection } from './composables/useSelection.js'
import { download } from './utils/export.js'

const AllView = defineAsyncComponent({
  loader: () => import('./components/views/AllView.vue'),
  loadingComponent: Spinner,
  delay: 0,
})
const DailyView = defineAsyncComponent({
  loader: () => import('./components/views/DailyView.vue'),
  loadingComponent: Spinner,
  delay: 0,
})
const AboutView = defineAsyncComponent({
  loader: () => import('./components/views/AboutView.vue'),
  loadingComponent: Spinner,
  delay: 0,
})

const { papers, dailyReports, loading, error, featuredItems, latestDate } = useData()
const { currentView, selectedItem, onSelect, onNavigate } = useNavigation()
const { selectedIds, selectionCount, hasSelection, toggleSelect, selectAll, clearSelection } = useSelection()

// 切换视图时清除选中
watch(currentView, () => clearSelection())

function exportSelected(format) {
  const items = papers.value.filter((p) => selectedIds.value.includes(p.id))
  if (items.length === 0) return
  download(items, format)
}
</script>

<style>
.main-push {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.main-push.is-pushed {
  will-change: transform;
  transform: translateX(-210px);
}
@media (max-width: 768px) {
  .main-push.is-pushed {
    transform: none;
  }
}
.toolbar-enter-active,
.toolbar-leave-active {
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
.toolbar-enter-from,
.toolbar-leave-to {
  opacity: 0;
  transform: translateY(16px);
}
</style>