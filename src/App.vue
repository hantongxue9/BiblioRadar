<template>
  <div class="min-h-screen bg-slate-50 flex max-md:flex-col">
    <!-- 侧边栏 -->
    <Sidebar :current-view="currentView" @navigate="currentView = $event" />

    <!-- 主内容区 -->
    <main class="flex-1 ml-52 max-md:ml-0">
      <div class="max-w-3xl mx-auto px-6 py-10 pb-20 max-md:px-4 max-md:py-6">
        <!-- 加载状态 -->
        <div v-if="loading" class="text-center text-sm text-slate-400 py-12">
          加载中...
        </div>

        <!-- 视图切换 -->
        <FeaturedView v-else-if="currentView === 'featured'" :items="featuredItems" />
        <AllView v-else-if="currentView === 'all'" :items="papers" />
        <DailyView v-else-if="currentView === 'daily'" :items="papers" />
        <AboutView v-else-if="currentView === 'about'" />
      </div>

      <!-- 底部 -->
      <footer class="text-center pb-8">
        <p class="text-xs text-slate-300">
          Scholar-Radar · 数据由大模型辅助评分，仅供参考
        </p>
      </footer>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import Sidebar from './components/Sidebar.vue'
import FeaturedView from './components/FeaturedView.vue'
import AllView from './components/AllView.vue'
import DailyView from './components/DailyView.vue'
import AboutView from './components/AboutView.vue'

const papers = ref([])
const loading = ref(true)
const currentView = ref('featured')

onMounted(async () => {
  try {
    const res = await fetch('/data.json')
    papers.value = await res.json()
  } catch (e) {
    console.error('Failed to load data.json:', e)
  } finally {
    loading.value = false
  }
})

const featuredItems = computed(() =>
  papers.value.filter((p) => p.featured)
)
</script>
