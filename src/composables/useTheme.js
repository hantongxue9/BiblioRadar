import { ref, watch, onMounted, onUnmounted } from 'vue'

const STORAGE_KEY = 'scholar-radar-theme'

const theme = ref('system') // 'light' | 'dark' | 'system'

function getSystemTheme() {
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

let rafId = null

function scheduleApply(value) {
  if (rafId) cancelAnimationFrame(rafId)
  rafId = requestAnimationFrame(() => {
    const resolved = value === 'system' ? getSystemTheme() : value
    document.documentElement.classList.toggle('dark', resolved === 'dark')
    rafId = null
  })
}

let mediaHandler = null

export function useTheme() {
  onMounted(() => {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved && ['light', 'dark', 'system'].includes(saved)) {
      theme.value = saved
    }
    scheduleApply(theme.value)

    const mq = window.matchMedia('(prefers-color-scheme: dark)')
    mediaHandler = () => { if (theme.value === 'system') scheduleApply('system') }
    mq.addEventListener('change', mediaHandler)
  })

  onUnmounted(() => {
    const mq = window.matchMedia('(prefers-color-scheme: dark)')
    mq.removeEventListener('change', mediaHandler)
  })

  watch(theme, (val) => {
    localStorage.setItem(STORAGE_KEY, val)
    scheduleApply(val)
  })

  function setTheme(val) {
    theme.value = val
  }

  return { theme, setTheme }
}
