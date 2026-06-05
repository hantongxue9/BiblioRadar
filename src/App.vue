<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-950 flex max-md:flex-col">
    <!-- 侧边栏 -->
    <Sidebar :current-view="currentView" @navigate="onNavigate" />

    <!-- 主内容区 -->
    <main
      class="flex-1 ml-52 max-md:ml-0 main-push"
      :class="{ 'is-pushed': selectedItem }"
    >
      <div class="max-w-3xl mx-auto px-6 py-10 pb-20 max-md:px-4 max-md:py-6">
        <!-- 加载状态 -->
        <div v-if="loading">
          <Spinner />
        </div>

        <!-- 错误状态 -->
        <div v-else-if="error" class="text-center py-12">
          <p class="text-sm text-slate-400 dark:text-slate-500 mb-4">{{ error }}</p>
          <button @click="() => location.reload()" class="text-xs px-4 py-2 rounded-lg bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:hover:bg-slate-700">重试</button>
        </div>

        <!-- 视图切换（KeepAlive 缓存已访问视图，消除切换闪烁） -->
        <KeepAlive v-else>
          <FeaturedView
            v-if="currentView === 'featured'"
            :items="featuredItems"
            :selected-item="selectedItem"
            :checked-ids="sel.selectedIds.value"
            @select="onSelect"
            @toggle-select="sel.toggle"
          />
          <AllView
            v-else-if="currentView === 'all'"
            :items="papers"
            :selected-item="selectedItem"
            :checked-ids="sel.selectedIds.value"
            @select="onSelect"
            @toggle-select="sel.toggle"
          />
          <DailyView
            v-else-if="currentView === 'daily'"
            :items="papers"
            :reports="dailyReports"
            :selected-item="selectedItem"
            :checked-ids="sel.selectedIds.value"
            @select="onSelect"
            @toggle-select="sel.toggle"
          />
          <AboutView v-else-if="currentView === 'about'" />
        <template v-if="sel.count.value > 0">
            <div class="h-px bg-gray-200 dark:bg-slate-800 mb-6"></div>

            <!-- 内联选择工具栏 -->
            <div class="flex items-center justify-between bg-slate-100/80 dark:bg-slate-800/50 border border-gray-200/60 dark:border-slate-700/60 rounded-xl px-5 py-3 mb-6">
              <span class="text-xs text-slate-500 dark:text-slate-400">
                已选 <strong class="text-slate-700 dark:text-slate-200 font-medium">{{ sel.count.value }}</strong> 条
              </span>
              <div class="flex items-center gap-3">
                <span class="text-[11px] text-slate-400 dark:text-slate-500">导出</span>
                <button @click="exportFormat('ris')" class="text-xs px-2.5 py-1 rounded-md bg-white text-slate-600 hover:text-ustc-500 shadow-sm dark:bg-slate-700 dark:text-slate-300 dark:hover:text-ustc-300 transition-colors">RIS</button>
                <button @click="exportFormat('bib')" class="text-xs px-2.5 py-1 rounded-md bg-white text-slate-600 hover:text-ustc-500 shadow-sm dark:bg-slate-700 dark:text-slate-300 dark:hover:text-ustc-300 transition-colors">BibTeX</button>
                <button @click="exportFormat('csv')" class="text-xs px-2.5 py-1 rounded-md bg-white text-slate-600 hover:text-ustc-500 shadow-sm dark:bg-slate-700 dark:text-slate-300 dark:hover:text-ustc-300 transition-colors">CSV</button>
                <span class="w-px h-4 bg-gray-200 dark:bg-slate-700"></span>
                <button @click="sel.clear()" class="text-xs text-slate-400 hover:text-slate-600 dark:text-slate-500 dark:hover:text-slate-300 transition-colors">清除</button>
              </div>
            </div>
          </template>
        </KeepAlive>
      </div>

      <!-- 底部 -->
      <footer class="text-center pb-8">
        <p class="text-xs text-slate-300 dark:text-slate-700">
          数据由大模型辅助评分 · 仅供参考<span v-if="latestDate"> · 更新至 {{ latestDate }}</span>
        </p>
      </footer>
    </main>

    <!-- 右侧详情面板 -->
    <DetailPanel :item="selectedItem" @close="selectedItem = null" />
  </div>
</template>

<script setup>
import { computed, KeepAlive, defineAsyncComponent, provide } from 'vue'
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
const sel = useSelection()
provide('selection', sel)

function exportFormat(fmt) {
  download(sel.getSelected(papers.value), fmt)
}
</script>

<style>
.main-push {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.main-push.is-pushed {
  will-change: transform;
}
.main-push.is-pushed {
  transform: translateX(-210px);
}
@media (max-width: 768px) {
  .main-push.is-pushed {
    transform: none;
  }
}
</style>