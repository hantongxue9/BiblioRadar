import { ref } from 'vue'

const STORAGE_KEY = 'biblioradar-favorites'
const OLD_KEY = 'biblioradar-reading-list'

function load() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) return JSON.parse(raw)
    // 迁移旧 key
    const old = localStorage.getItem(OLD_KEY)
    if (old) {
      const data = JSON.parse(old)
      localStorage.setItem(STORAGE_KEY, old)
      localStorage.removeItem(OLD_KEY)
      return data
    }
    return []
  } catch {
    return []
  }
}

const savedIds = ref(load())

function persist() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(savedIds.value))
}

export function useFavorites() {
  function toggleSave(id) {
    const idx = savedIds.value.indexOf(id)
    if (idx === -1) {
      savedIds.value = [...savedIds.value, id]
    } else {
      savedIds.value = savedIds.value.filter((x) => x !== id)
    }
    persist()
  }

  function isSaved(id) {
    return savedIds.value.includes(id)
  }

  function saveAll(ids) {
    const existing = new Set(savedIds.value)
    const newIds = ids.filter((id) => !existing.has(id))
    if (newIds.length > 0) {
      savedIds.value = [...savedIds.value, ...newIds]
      persist()
    }
  }

  function clearAll() {
    savedIds.value = []
    persist()
  }

  return { savedIds, toggleSave, isSaved, saveAll, clearAll }
}
