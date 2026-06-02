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
            @select="onSelect"
          />
          <AllView
            v-else-if="currentView === 'all'"
            :items="papers"
            :selected-item="selectedItem"
            @select="onSelect"
          />
          <DailyView
            v-else-if="currentView === 'daily'"
            :items="papers"
            :reports="dailyReports"
            :selected-item="selectedItem"
            @select="onSelect"
          />
          <AboutView v-else-if="currentView === 'about'" />
        </KeepAlive>
      </div>

      <!-- 底部 -->
      <footer class="text-center pb-8">
        <p class="text-xs text-slate-300 dark:text-slate-700">
          图情雷达 · 数据由大模型辅助评分，仅供参考
        </p>
      </footer>
    </main>

    <!-- 右侧详情面板 -->
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

const { papers, dailyReports, loading, error, featuredItems } = useData()
const { currentView, selectedItem, onSelect, onNavigate } = useNavigation()
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