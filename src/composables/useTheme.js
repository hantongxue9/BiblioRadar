import { ref, watch } from 'vue'

const STORAGE_KEY = 'biblioradar-theme'

const theme = ref('system') // 'light' | 'dark' | 'system'

function getSystemTheme() {
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

function applyTheme(value) {
  const resolved = value === 'system' ? getSystemTheme() : value
  document.documentElement.classList.toggle('dark', resolved === 'dark')
}

// 初始化：读取 localStorage 并应用
const saved = localStorage.getItem(STORAGE_KEY)
if (saved && ['light', 'dark', 'system'].includes(saved)) {
  theme.value = saved
}
applyTheme(theme.value)

// 系统主题变化监听（模块级，只注册一次）
const mq = window.matchMedia('(prefers-color-scheme: dark)')
mq.addEventListener('change', () => {
  if (theme.value === 'system') applyTheme('system')
})

// 主题变化时持久化
watch(theme, (val) => {
  localStorage.setItem(STORAGE_KEY, val)
  applyTheme(val)
})

export function useTheme() {
  function setTheme(val) {
    theme.value = val
  }
  return { theme, setTheme }
}
