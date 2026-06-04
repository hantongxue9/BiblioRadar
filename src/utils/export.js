/** @import {PaperItem} from './types.js' */

/**
 * @param {PaperItem[]} items
 * @returns {string}
 */
export function toRIS(items) {
  const lines = []
  for (const item of items) {
    lines.push('TY  - JOUR')
    lines.push(`TI  - ${item.title}`)
    if (item.abstract) lines.push(`AB  - ${item.abstract}`)
    if (item.source) lines.push(`JO  - ${item.source}`)
    if (item.date) lines.push(`PY  - ${item.date.slice(0, 4)}`)
    if (item.date) lines.push(`DA  - ${item.date}`)
    if (item.link) lines.push(`UR  - ${item.link}`)
    if (item.link && item.link.includes('doi.org')) {
      const doi = item.link.split('doi.org/')[1]
      if (doi) lines.push(`DO  - ${doi}`)
    }
    lines.push(`N1  - ${item.one_sentence_summary || ''}`)
    if (item.affiliations) lines.push(`A2  - ${item.affiliations}`)
    lines.push('ER  - ')
    lines.push('')
  }
  return lines.join('\n')
}

/**
 * @param {PaperItem[]} items
 * @returns {string}
 */
export function toBibTeX(items) {
  const lines = []
  for (let i = 0; i < items.length; i++) {
    const item = items[i]
    const key = item.title
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, ' ')
      .trim()
      .split(/\s+/)
      .slice(0, 3)
      .join('')
      + (item.date ? item.date.slice(0, 4) : '')
      + String.fromCharCode(97 + i)
    lines.push('@article{' + key + ',')
    lines.push(`  title = {${escapeLatex(item.title)}},`)
    if (item.source) lines.push(`  journal = {${escapeLatex(item.source)}},`)
    if (item.date) lines.push(`  year = {${item.date.slice(0, 4)}},`)
    if (item.abstract) lines.push(`  abstract = {${escapeLatex(item.abstract)}},`)
    if (item.link) lines.push(`  url = {${item.link}},`)
    if (item.link && item.link.includes('doi.org')) {
      const doi = item.link.split('doi.org/')[1]
      if (doi) lines.push(`  doi = {${doi}},`)
    }
    if (item.one_sentence_summary) {
      lines.push(`  note = {${escapeLatex(item.one_sentence_summary)}},`)
    }
    if (item.affiliations) {
      lines.push(`  author = {${escapeLatex(item.affiliations)}},`)
    }
    lines.push('}')
    lines.push('')
  }
  return lines.join('\n')
}

/**
 * @param {PaperItem[]} items
 * @returns {string}
 */
export function toCSV(items) {
  const headers = ['id', 'title', 'source', 'date', 'category', 'tier', 'type', 'composite_score', 'abstract', 'link']
  const rows = [headers.join('\t')]
  for (const item of items) {
    rows.push(headers.map(h => escapeCSV(String(item[h] ?? ''))).join('\t'))
  }
  return rows.join('\n')
}

/**
 * @param {PaperItem[]} items
 * @param {'ris'|'bib'|'csv'} format
 */
export function download(items, format) {
  const map = { ris: toRIS, bib: toBibTeX, csv: toCSV }
  const content = (map[format] || toRIS)(items)
  const mime = format === 'csv' ? 'text/tab-separated-values' : 'text/plain'
  const ext = format === 'bib' ? 'bib' : format
  const blob = new Blob(['﻿' + content], { type: mime })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `biblioradar.${ext}`
  a.click()
  URL.revokeObjectURL(url)
}

function escapeCSV(s) {
  if (s.includes('"') || s.includes('\t') || s.includes('\n')) {
    return '"' + s.replace(/"/g, '""') + '"'
  }
  return s
}

function escapeLatex(s) {
  return s.replace(/[{}&%$#_~^\\]/g, c => c === '\\' ? '\\\\textbackslash ' : '\\' + c)
}