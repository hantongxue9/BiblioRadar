/**
 * @param {string} dateStr - YYYY-MM-DD
 * @returns {string} 中文格式日期，如 "2024年3月15日"
 */
export function formatDateCN(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr + 'T00:00:00')
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`
}
