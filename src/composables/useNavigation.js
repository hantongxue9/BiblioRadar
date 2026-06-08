import { ref, onMounted } from 'vue'

const VALID_VIEWS = ['featured', 'all', 'daily', 'reading', 'trends', 'about']

export function useNavigation() {
  const currentView = ref('featured')
  const selectedItem = ref(null)

  onMounted(() => {
    const hash = location.hash.replace('#', '')
    if (VALID_VIEWS.includes(hash)) {
      currentView.value = hash
    }
  })

  function onSelect(item) {
    selectedItem.value = selectedItem.value?.id === item.id ? null : item
  }

  function onNavigate(view) {
    currentView.value = view
    selectedItem.value = null
    history.replaceState(null, '', `#${view}`)
  }

  return { currentView, selectedItem, onSelect, onNavigate }
}