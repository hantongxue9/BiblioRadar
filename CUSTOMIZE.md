# 定制指南：迁移到其他学科

本项目（图情雷达）的架构是通用的——抓取 → LLM 评估 → 评分 → 前端展示，不绑定任何学科。复制本仓库后，按以下步骤修改即可为任意学科生成一个专属的"学术雷达"。

## 需要改的文件

### 1. 项目名称与品牌

| 文件 | 改什么 |
|------|--------|
| `README.md` | 项目名称、描述、功能列表、数据源表 |
| `index.html` | `<title>` 标签 |
| `src/components/layout/Sidebar.vue` | 品牌区的中文名和英文名（约第 29-30 行） |
| `public/vite.svg` | 替换为你的 logo |
| `src/components/views/AboutView.vue` | 所有内容：项目描述、评分体系说明、数据源列表、技术栈说明 |

### 2. 数据来源

**`backend/sources.py`** — 替换所有 `SourceConfig` 条目。

每条需要指定：
- `name` — 来源名称
- `tier` — 等级（A/B/C，影响可信度加分）
- `fetch_type` — `rss` / `web` / `crossref`
- `url` — RSS 地址、网页 URL 或 CrossRef 期刊名
- `category` — 分类标签（显示在前端卡片上）

参考现有条目的格式，按你的学科选择对应的核心期刊、预印本平台和行业资讯源。

### 3. 抓取过滤

**`backend/scraper.py`** — 两处需要改：

1. **关键词过滤**（约第 30 行的 `LIS_KEYWORDS`）— 替换为你的学科关键词。这个正则用于预过滤 RSS/Web 抓取结果，只保留与学科相关的条目。如果不需要预过滤，可以将匹配逻辑改为始终返回 `True`。

2. **机构过滤**（`_filter_affiliation` 函数）— 当前硬编码了 USTC 相关的匹配规则。如果不需要机构过滤，确保环境变量 `FILTER_AFFILIATION=false`（默认值）。如果需要，替换为你关心的机构名称和正则。

### 4. 评估提示词

**`backend/prompts/`** 下的三个文件：

| 文件 | 用途 |
|------|------|
| `paper_system.txt` | 论文评估的系统提示词 |
| `news_system.txt` | 资讯评估的系统提示词 |
| `daily_report.txt` | 每日摘要生成的系统提示词 |

这是影响评估质量的关键。提示词需要明确：
- 你关注的学科领域和研究方向
- 评分维度的定义（当前是"前沿技术度 / 业务落地值 / 方法严谨性"，你可以换成适合你学科的维度）
- 评分标准和参考锚点
- 输出格式要求（JSON 结构）

### 5. 评分权重（可选）

**`backend/config.py`** — 如果你修改了评分维度，需要同步调整：
- `weight_frontier` / `weight_practical` / `weight_rigor` — 改为你的维度权重
- `arxiv_score_factor` — arXiv 论文的折扣系数，如果你的学科不用 arXiv 可以忽略
- `min_score_avg` / `min_score_avg_news` — 最低评分阈值

### 6. 清除旧数据

| 文件 | 操作 |
|------|------|
| `public/data.json` | 替换为 `[]` |
| `public/daily_reports.json` | 已经是 `[]`，无需处理 |

### 7. GitHub 配置

- **仓库名** — 改为你学科的名字
- **Settings → Secrets** — 配置 `MIMO_API_KEY`、`MIMO_BASE_URL`、`MIMO_MODEL`
- **Settings → Pages** — 确认部署源为 GitHub Actions
- **`.github/workflows/daily_update.yml`** — 定时任务的时间和环境变量按需调整

## 不需要改的

以下文件与学科无关，直接复用：

- `backend/pipeline.py` — 流程编排
- `backend/pipeline_utils.py` — 评分计算、合并逻辑
- `backend/data_contract.py` — 数据校验（如果新增了评分维度，需要加字段）
- `backend/logging_setup.py` — 日志格式
- `backend/main.py` — 入口
- `src/` 下所有前端代码（除 AboutView 和 Sidebar 品牌区）
- `src/utils/export.js` — 导出功能
- `.github/workflows/pr_check.yml` — PR 检查

## 快速检查清单

fork 后按顺序过一遍：

- [ ] `README.md` 改名改描述
- [ ] `index.html` 改 title
- [ ] `Sidebar.vue` 改品牌名
- [ ] `AboutView.vue` 改内容
- [ ] `public/vite.svg` 换 logo
- [ ] `backend/sources.py` 换来源
- [ ] `backend/scraper.py` 换关键词
- [ ] `backend/prompts/*.txt` 换提示词
- [ ] `backend/config.py` 调权重（如需要）
- [ ] `public/data.json` 清空为 `[]`
- [ ] GitHub Secrets 配置 API 密钥
- [ ] 本地 `python -m backend.main` 跑通
- [ ] `npm run build` 构建通过
- [ ] 推送到 GitHub，确认 Actions 和 Pages 正常
