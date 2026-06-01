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
import { ref, shallowRef, computed, onMounted, KeepAlive, defineAsyncComponent } from 'vue'
import Sidebar from './components/Sidebar.vue'
import FeaturedView from './components/FeaturedView.vue'
import DetailPanel from './components/DetailPanel.vue'

const Spinner = {
  template: `<div class="flex items-center justify-center py-20">
    <svg class="w-5 h-5 text-slate-300 dark:text-slate-600 animate-spin" viewBox="0 0 24 24" fill="none">
      <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" stroke-opacity="0.25"/>
      <path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    </svg>
  </div>`,
}

const AllView = defineAsyncComponent({
  loader: () => import('./components/AllView.vue'),
  loadingComponent: Spinner,
  delay: 0,
})
const DailyView = defineAsyncComponent({
  loader: () => import('./components/DailyView.vue'),
  loadingComponent: Spinner,
  delay: 0,
})
const AboutView = defineAsyncComponent({
  loader: () => import('./components/AboutView.vue'),
  loadingComponent: Spinner,
  delay: 0,
})

const papers = shallowRef([])
const dailyReports = shallowRef([])
const loading = ref(true)
const currentView = ref('featured')
const selectedItem = ref(null)

const error = ref(null)

onMounted(async () => {
  try {
    const [papersRes, reportsRes] = await Promise.all([
      fetch('data.json').catch(() => null),
      fetch('daily_reports.json').catch(() => null),
    ])

    if (papersRes?.ok) {
      papers.value = await papersRes.json()
    } else if (papersRes) {
      error.value = '数据加载失败（HTTP ' + papersRes.status + '），请刷新重试'
    }
    if (reportsRes?.ok) dailyReports.value = await reportsRes.json()
  } catch (e) {
    error.value = '数据加载失败，请刷新重试'
    console.error('Failed to load data:', e)
  } finally {
    loading.value = false
  }
})

const featuredItems = computed(() =>
  papers.value.filter((p) => p.featured)
)

function onSelect(item) {
  selectedItem.value = selectedItem.value?.id === item.id ? null : item
}

function onNavigate(view) {
  currentView.value = view
  selectedItem.value = null
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
