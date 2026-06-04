import { ref, computed } from 'vue'

export function useSelection() {
  /** @type {import('vue').Ref<Set<number>>} */
  const selectedIds = ref(new Set())

  const count = computed(() => selectedIds.value.size)

  function toggle(id) {
    const next = new Set(selectedIds.value)
    if (next.has(id)) {
      next.delete(id)
    } else {
      next.add(id)
    }
    selectedIds.value = next
  }

  /** @param {import('../utils/types').PaperItem[]} items */
  function selectPage(items) {
    const next = new Set(selectedIds.value)
    for (const item of items) next.add(item.id)
    selectedIds.value = next
  }

  function clear() {
    selectedIds.value = new Set()
  }

  /** @param {import('../utils/types').PaperItem[]} items */
  function getSelected(items) {
    const set = selectedIds.value
    return items.filter(item => set.has(item.id))
  }

  return { selectedIds, count, toggle, selectPage, clear, getSelected }
}