import { ref, computed } from 'vue'

const STORAGE_KEY = 'biblioradar-reading-list'

function load() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

const savedIds = ref(load())

function persist() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(savedIds.value))
}

export function useReadingList() {
  const readingCount = computed(() => savedIds.value.length)

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

  function clearAll() {
    savedIds.value = []
    persist()
  }

  return { savedIds, readingCount, toggleSave, isSaved, clearAll }
}
