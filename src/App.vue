<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-950 flex max-md:flex-col">
    <!-- 侧边栏 -->
    <Sidebar :current-view="currentView" @navigate="onNavigate" />

    <!-- 主内容区 -->
    <main
      ref="mainRef"
      class="flex-1 ml-52 max-md:ml-0 main-push"
      :class="{ 'is-pushed': selectedItem }"
    >
      <div class="max-w-3xl mx-auto px-6 py-10 pb-20 max-md:px-4 max-md:py-6">
        <!-- 加载状态 -->
        <div v-if="loading" class="text-center text-sm text-slate-400 py-12">
          加载中...
        </div>

        <!-- 视图切换 -->
        <FeaturedView
          v-else-if="currentView === 'featured'"
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
      </div>

      <!-- 底部 -->
      <footer class="text-center pb-8">
        <p class="text-xs text-slate-300 dark:text-slate-700">
          Scholar-Radar · 数据由大模型辅助评分，仅供参考
        </p>
      </footer>
    </main>

    <!-- 右侧详情面板 -->
    <DetailPanel :item="selectedItem" @close="selectedItem = null" />
  </div>
</template>

<script setup>
import { ref, shallowRef, computed, onMounted, defineAsyncComponent } from 'vue'
import Sidebar from './components/Sidebar.vue'
import FeaturedView from './components/FeaturedView.vue'
import DetailPanel from './components/DetailPanel.vue'

const AllView = defineAsyncComponent(() => import('./components/AllView.vue'))
const DailyView = defineAsyncComponent(() => import('./components/DailyView.vue'))
const AboutView = defineAsyncComponent(() => import('./components/AboutView.vue'))

const papers = shallowRef([])
const dailyReports = shallowRef([])
const loading = ref(true)
const currentView = ref('featured')
const selectedItem = ref(null)

onMounted(async () => {
  const [papersRes, reportsRes] = await Promise.all([
    fetch('/data.json').catch(() => null),
    fetch('/daily_reports.json').catch(() => null),
  ])

  if (papersRes?.ok) papers.value = await papersRes.json()
  if (reportsRes?.ok) dailyReports.value = await reportsRes.json()

  loading.value = false
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
  will-change: transform;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
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
