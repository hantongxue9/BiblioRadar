# Scholar-Radar

图情领域学术追踪系统。每日自动抓取多源文献与行业资讯，通过大模型多维度评估，为研究者提供经过筛选和排序的前沿学术动态。

## 功能

- **每日自动更新** — GitHub Actions 每天 6:00 自动抓取、评估、部署
- **20 个信息源** — 覆盖国际核心期刊、国内权威期刊、预印本与行业资讯
- **大模型评估** — 前沿技术度 (40%) + 业务落地值 (35%) + 方法严谨性 (25%)
- **精选推荐** — 综合评分 ≥ 7.5 的文献自动进入精选
- **LLM 日报** — 每日生成行业摘要与要点
- **右侧详情面板** — 点击条目滑出详情，列表不被遮挡
- **深色模式** — 支持浅色 / 跟随系统 / 深色三档切换
- **移动端适配** — 侧边栏自动转为顶部导航，详情面板全屏展示

## 技术栈

- **后端** — Python + aiohttp + OpenAI-compatible API
- **前端** — Vue 3 + Tailwind CSS + Vite（shallowRef / v-memo / 异步组件优化）
- **部署** — GitHub Pages（静态站点，push 自动部署）

## 本地开发

```bash
# 安装依赖
npm install
pip install -r backend/requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入 LLM_API_KEY 等

# 运行数据抓取（可选，public/data.json 已有示例数据）
cd backend && python main.py

# 启动前端
npm run dev
```

## 数据源

| 类型 | 来源 |
|------|------|
| A 类 · 国际核心 | Scientometrics, JASIST, Journal of Informetrics, LISR, IP&M, The Electronic Library |
| B 类 · 国内权威 | 中国图书馆学报, 大学图书馆学报, 图书情报工作, 情报学报 |
| C 类 · 预印本/资讯 | arXiv (cs.DL/IR/CL/SI), NISO, LIBER, ARL, Scholarly Kitchen, SPARC News 等 |

## 自动部署

| 触发方式 | 数据抓取 | 前端部署 |
|----------|---------|---------|
| `git push` 到 main | 否 | 是 |
| 每天 6:00（北京时间） | 是 | 是 |
| 手动 Run workflow | 是 | 是 |

每天定时任务自动完成：抓取 → LLM 评估 → 生成日报 → 构建前端 → 部署到 GitHub Pages。

## License

[MIT](LICENSE)
