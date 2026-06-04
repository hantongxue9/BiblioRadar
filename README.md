# 图情雷达 · BiblioRadar

图情领域学术追踪系统。每日自动抓取多源文献与行业资讯，通过大模型多维度评估，为研究者提供经过筛选和排序的前沿学术动态。

## 功能

- **每日自动更新** — GitHub Actions 每天 6:00 自动抓取、评估、部署
- **25 个信息源** — 覆盖国际核心期刊、国内权威期刊、预印本与行业资讯
- **大模型评估** — 前沿技术度 (40%) + 业务落地值 (35%) + 方法严谨性 (25%)
- **数据质量控制** — 写入前校验字段结构、评分范围和分类标签，并过滤明显的元数据噪声
- **精选推荐** — 综合评分 ≥ 7.5 的文献自动进入精选
- **LLM 日报** — 每日生成行业摘要与要点
- **右侧详情面板** — 点击条目滑出详情，列表不被遮挡
- **深色模式** — 支持浅色 / 跟随系统 / 深色三档切换
- **移动端适配** — 侧边栏自动转为顶部导航，详情面板全屏展示

## 技术栈

- **后端** — Python 3.11+ + aiohttp + OpenAI-compatible API
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
python -m backend.main

# 运行后端测试
python -m unittest discover backend/tests

# 启动前端
npm run dev
```

## 数据源

| 等级 | 来源 | 抓取方式 |
|------|------|----------|
| **A** | Scientometrics | RSS |
| **A** | JASIST | CrossRef API |
| **A** | Journal of Informetrics | RSS |
| **A** | Library & Information Science Research | RSS |
| **A** | Information Processing & Management | RSS |
| **A** | The Electronic Library | CrossRef API |
| **B** | 中国图书馆学报 | Web 抓取 |
| **B** | 大学图书馆学报 | Web 抓取 |
| **B** | 图书情报工作 | Web 抓取 |
| **B** | 情报学报 | Web 抓取 |
| **C** | arXiv (cs.DL/cs.IR/cs.CL/cs.SI) | RSS |
| **C** | NISO News | Web 抓取 |
| **C** | LIBER News | Web 抓取 |
| **C** | ARL News | Web 抓取 |
| **C** | Scholarly Kitchen | RSS |
| **C** | Infodocket | RSS |
| **C** | LSE Impact Blog | RSS |
| **C** | SPARC News | RSS |
| **C** | Code4Lib Journal | RSS |
| **C** | First Monday | RSS |
| **C** | CALIS 通知 | Web 抓取 |
| **C** | CADAL 通知 | Web 抓取 |

## 自动部署

| 触发方式 | 前端部署 |
|----------|---------|
| `git push` 到 main | 是 |

每次 `git push` 自动完成：测试 → 构建 → 部署到 GitHub Pages。

> 数据抓取需要在本地运行（因 USTC LLM API 为内网访问）：
> ```bash
> python -m backend.main
> git add public/data.json public/daily_reports.json
> git commit -m "chore: update data $(date +%Y-%m-%d)"
> git push
> ```

## License

[MIT](LICENSE)
