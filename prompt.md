# Role & Project Overview
你是一位资深全栈工程师兼系统架构师。请帮我从零到一在当前目录下构建一个名为 "Scholar-Radar" (图情科研雷达) 的全栈工程。
该项目的目标是：每天定时监控图情领域（LIS）的高水平学术论文与前沿资讯，通过大模型进行多维打分和分类，最终在一个极简、优雅的前端页面上向公众展示。

# Architecture Design (公开部署架构)
为了支持后续的低成本公开访问与自动化，项目采用以下“前后端分离+静态托管”架构：
1. 后端数据流 (Python)：负责拉取 RSS/API，利用正则表达式清洗数据，调用大模型 API 打分，最后生成或更新一个 `data.json` 文件。
2. 前端展示层 (Vite + Vue 3 + Tailwind CSS)：构建为单页应用 (SPA)，构建时读取 `data.json`，提供纯静态但具有前端过滤、搜索功能的网页。
3. 自动化部署 (GitHub Actions)：配置 YAML 工作流，每天凌晨自动运行 Python 脚本更新 JSON，并触发前端构建，推送至 GitHub Pages 或 Vercel。

# Aesthetic & Language Constraints (最高优级的红线)
1. 语言规范：所有面向公众展示的文案、大模型摘要生成的 Prompt 设定，必须使用极其专业、平实、接地气的语言。**绝对禁止**出现“杠杆效应”、“经费黑洞”、“赋能闭环”、“底层逻辑”等浮夸的互联网黑话！
2. UI 设计语言：极简主义。必须保留极大的“呼吸感”和干净的排版。使用标准的 Tailwind 色系（如背景 bg-slate-50，文字 text-slate-800，边框 border-gray-100）。摒弃高饱和度色彩，依靠间距（Margin/Padding）、优雅的行高（leading-relaxed）和字重的对比来划分信息层级。

# Task 1: Initialize Frontend Project (Vite + Vue 3 + Tailwind)
请在当前目录初始化一个前端工程：
- 框架：Vue 3 (Composition API) + Vite。
- 样式：安装并配置好 Tailwind CSS。
- 核心组件：
  - `Header.vue`：简单的站点标题和副标题。
  - `ControlPanel.vue`：包含一个搜索框（按标题/摘要模糊搜索）、一个分类筛选器（全部、计量与评价、技术与工具）、一个排序器（按时间、按评分）。
  - `PaperCard.vue`：展示论文标题、时间、分类、一句话核心提炼，以及三个维度的打分（前沿技术度、业务落地值、方法严谨性）。要求点击卡片能优雅展开，显示详细的英文摘要和大模型的“思考过程”。
- 状态管理：请在 `App.vue` 中编写逻辑，通过 fetch 加载 `public/data.json`，并在前端实现搜索和过滤逻辑。

# Task 2: Build Python Data Pipeline (Backend)
请在项目根目录创建一个 `backend/` 文件夹，并编写以下 Python 脚本：
- `requirements.txt`：包含所需的库（如 requests, feedparser, openai 等）。
- `scraper.py`：负责从指定的几个图情领域源（可暂时 mock 几个标准 RSS 源地址）抓取最新文献元数据（Title, Abstract, Date, Link, Affiliations）。
- **【硬核过滤逻辑要求】**：在把数据喂给大模型之前，请在代码中实现一个严格的机构清洗函数。例如，如果策略是提取某特定高校的论文，必须使用正则表达式（如 `Univ Sci & Technol.*?China`）进行精准匹配，并明确在代码中排除类似华中科技大学（Huazhong University of Science and Technology / HUST）的混淆项。请在代码中保留这段过滤逻辑作为模板。
- `llm_evaluator.py`：调用兼容 OpenAI 格式的 API（如 DeepSeek 或 Claude）。请在代码中内置强有力的 System Prompt，要求大模型输出包含 `thinking`, `category`, `scores` (3个维度), `one_sentence_summary` 的严格 JSON 格式。
- `main.py`：调度抓取和评估逻辑，将最终高分通过的文献追加/更新写入到前端工程的 `public/data.json` 中。

# Task 3: Setup CI/CD for Public Deployment (GitHub Actions)
在根目录下创建 `.github/workflows/daily_update.yml`，编写完整的自动化工作流：
1. 设定 Cron 表达式（如每天北京时间早上 6 点触发）。
2. 环境设置：检出代码，设置 Python 环境并 `pip install`，设置 Node.js 环境并 `npm install`。
3. 运行逻辑：
   - 注入环境变量（如 `LLM_API_KEY`）。
   - 执行 `python backend/main.py` 生成最新的 `data.json`。
   - 提交并 push 更新后的 `data.json` 到代码库（包含配置 Git user 的步骤）。
   - 执行 `npm run build` 打包前端页面。
4. 提供简单的注释，说明如何将其部署到 Vercel（Vercel 只需要绑定仓库即可，重点是确保构建产出目录 `dist/` 的正确性）。

请直接开始按顺序创建和修改文件，遇到需要确认的配置可以直接使用合理的默认值并向我解释。