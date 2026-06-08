import { ref, computed } from 'vue'

export function useSelection() {
  const selectedIds = ref([])

  const selectionCount = computed(() => selectedIds.value.length)
  const hasSelection = computed(() => selectionCount.value > 0)

  function toggleSelect(id) {
    const idx = selectedIds.value.indexOf(id)
    if (idx === -1) {
      selectedIds.value = [...selectedIds.value, id]
    } else {
      selectedIds.value = selectedIds.value.filter((x) => x !== id)
    }
  }

  function selectAll(ids) {
    selectedIds.value = [...ids]
  }

  function clearSelection() {
    selectedIds.value = []
  }

  return { selectedIds, selectionCount, hasSelection, toggleSelect, selectAll, clearSelection }
}
