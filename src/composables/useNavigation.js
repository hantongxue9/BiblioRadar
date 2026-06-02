import { ref } from 'vue'

export function useNavigation() {
  const currentView = ref('featured')
  const selectedItem = ref(null)

  function onSelect(item) {
    selectedItem.value = selectedItem.value?.id === item.id ? null : item
  }

  function onNavigate(view) {
    currentView.value = view
    selectedItem.value = null
  }

  return { currentView, selectedItem, onSelect, onNavigate }
}