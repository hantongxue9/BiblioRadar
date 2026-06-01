import { ref, shallowRef, computed, onMounted } from 'vue'

export function useData() {
  const papers = shallowRef([])
  const dailyReports = shallowRef([])
  const loading = ref(true)
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
        error.value = `数据加载失败（HTTP ${papersRes.status}），请刷新重试`
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

  return { papers, dailyReports, loading, error, featuredItems }
}