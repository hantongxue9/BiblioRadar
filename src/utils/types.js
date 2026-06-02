/**
 * @typedef {Object} ScoreSet
 * @property {number} frontier_tech
 * @property {number} practical_value
 * @property {number} methodological_rigor
 */

/**
 * @typedef {Object} NewsScoreSet
 * @property {number} timeliness
 * @property {number} relevance
 * @property {number} information_value
 */

/**
 * @typedef {Object} PaperItem
 * @property {number} id
 * @property {string} title
 * @property {string} date - YYYY-MM-DD format
 * @property {string} link
 * @property {string} source
 * @property {string} tier - "A" | "B" | "C"
 * @property {string} field
 * @property {"paper"|"news"} content_type
 * @property {string} category
 * @property {ScoreSet|NewsScoreSet} scores
 * @property {string} one_sentence_summary
 * @property {number} composite_score
 * @property {boolean} featured
 * @property {string} [abstract]
 * @property {string} [thinking]
 * @property {string} [affiliations]
 * @property {number} [credibility_score]
 */

/**
 * @typedef {Object} DailyReport
 * @property {string} date
 * @property {string} summary
 * @property {string[]} highlights
 * @property {{papers:number, news:number, featured:number}} stats
 */
export {}