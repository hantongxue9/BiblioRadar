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
            :toggle-save="toggleSave"
            :is-saved="isSaved"
            :save-all="saveAll"
            @select="onSelect"
          />
          <AllView
            v-else-if="currentView === 'all'"
            :items="papers"
            :selected-item="selectedItem"
            :toggle-save="toggleSave"
            :is-saved="isSaved"
            :save-all="saveAll"
            @select="onSelect"
          />
          <DailyView
            v-else-if="currentView === 'daily'"
            :items="papers"
            :reports="dailyReports"
            :selected-item="selectedItem"
            :toggle-save="toggleSave"
            :is-saved="isSaved"
            :save-all="saveAll"
            @select="onSelect"
          />
          <ReadingListView
            v-else-if="currentView === 'reading'"
            :items="papers"
            :selected-item="selectedItem"
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
  </div>
</template>

<script setup>
import { KeepAlive, defineAsyncComponent } from 'vue'
import Sidebar from './components/layout/Sidebar.vue'
import FeaturedView from './components/views/FeaturedView.vue'
import DetailPanel from './components/panels/DetailPanel.vue'
import Spinner from './components/layout/Spinner.vue'
import { useData } from './composables/useData.js'
import { useNavigation } from './composables/useNavigation.js'
import { useReadingList } from './composables/useReadingList.js'

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
const ReadingListView = defineAsyncComponent({
  loader: () => import('./components/views/ReadingListView.vue'),
  loadingComponent: Spinner,
  delay: 0,
})

const { papers, dailyReports, loading, error, featuredItems, latestDate } = useData()
const { currentView, selectedItem, onSelect, onNavigate } = useNavigation()
const { toggleSave, isSaved, saveAll } = useReadingList()
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
mark {
  background: #fef08a;
  color: inherit;
  border-radius: 2px;
  padding: 0 1px;
}
.dark mark {
  background: #854d0e;
  color: #fef3c7;
}
</style>