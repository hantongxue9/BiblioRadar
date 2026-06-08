/**
 * Split text by query match, return segments with highlight flag.
 * @param {string} text
 * @param {string} query
 * @returns {{ text: string, highlight: boolean }[]}
 */
export function highlightSegments(text, query) {
  if (!text || !query) return [{ text: text || '', highlight: false }]
  const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  const regex = new RegExp(`(${escaped})`, 'gi')
  const parts = text.split(regex)
  return parts
    .filter(Boolean)
    .map((part) => ({ text: part, highlight: part.toLowerCase() === query.toLowerCase() }))
}
