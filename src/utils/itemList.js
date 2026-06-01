export function uniqueCategories(items, { includeAll = false } = {}) {
  const categories = [...new Set(items.map((item) => item.category))]
    .filter(Boolean)
    .sort()
  return includeAll ? ['all', ...categories] : categories
}

export function filterItems(items, { query = '', category = 'all', contentType = 'all' } = {}) {
  let result = items
  const q = query.trim().toLowerCase()

  if (q) {
    result = result.filter((item) => {
      const title = (item.title || '').toLowerCase()
      const abstract = (item.abstract || '').toLowerCase()
      const summary = (item.one_sentence_summary || '').toLowerCase()
      return title.includes(q) || abstract.includes(q) || summary.includes(q)
    })
  }

  if (category !== 'all') {
    result = result.filter((item) => item.category === category)
  }

  if (contentType !== 'all') {
    result = result.filter((item) => item.content_type === contentType)
  }

  return result
}

export function sortItems(items, sortBy = 'date') {
  const result = items.slice()
  if (sortBy === 'score') {
    result.sort((a, b) => (b.composite_score ?? 0) - (a.composite_score ?? 0))
  } else {
    result.sort((a, b) => (b.date || '').localeCompare(a.date || ''))
  }
  return result
}

export function paginateItems(items, currentPage, perPage) {
  const start = (currentPage - 1) * perPage
  return items.slice(start, start + perPage)
}

export function visiblePageNumbers(totalPages, currentPage, maxVisible = 7) {
  const pages = []
  let start = Math.max(1, currentPage - Math.floor(maxVisible / 2))
  let end = Math.min(totalPages, start + maxVisible - 1)
  if (end - start < maxVisible - 1) {
    start = Math.max(1, end - maxVisible + 1)
  }
  for (let page = start; page <= end; page++) pages.push(page)
  return pages
}

export function groupItemsByDate(items, { enabled = true } = {}) {
  if (!enabled) return [{ date: null, items }]

  const groups = []
  let currentDate = null
  for (const item of items) {
    if (item.date !== currentDate) {
      currentDate = item.date
      groups.push({ date: item.date, items: [] })
    }
    groups[groups.length - 1].items.push(item)
  }
  return groups
}
