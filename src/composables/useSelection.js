import { ref, computed } from 'vue'

export function useSelection() {
  /** 使用 plain object 替代 Set 确保 Vue 响应式 */
  const selectedIds = ref({})

  const count = computed(() => Object.keys(selectedIds.value).length)

  function toggle(id) {
    selectedIds.value = {
      ...selectedIds.value,
      [id]: !selectedIds.value[id],
    }
    if (!selectedIds.value[id]) {
      const { [id]: _, ...rest } = selectedIds.value
      selectedIds.value = rest
    }
  }

  /** @param {import('../utils/types').PaperItem[]} items */
  function selectPage(items) {
    const next = { ...selectedIds.value }
    for (const item of items) next[item.id] = true
    selectedIds.value = next
  }

  function clear() {
    selectedIds.value = {}
  }

  function has(id) {
    return !!selectedIds.value[id]
  }

  /** @param {import('../utils/types').PaperItem[]} items */
  function getSelected(items) {
    const ids = selectedIds.value
    return items.filter(item => ids[item.id])
  }

  return { selectedIds, count, has, toggle, selectPage, clear, getSelected }
}