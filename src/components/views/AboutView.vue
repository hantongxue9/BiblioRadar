<template>
  <div v-once class="max-w-2xl">
    <div class="mb-10">
      <h2 class="text-lg font-light text-slate-800 dark:text-slate-100 mb-4">关于图情雷达</h2>
      <p class="text-sm text-slate-600 dark:text-slate-500 leading-relaxed">
        图情雷达（BiblioRadar）是一个自动化的图情领域学术追踪系统。每日从多个学术信息源抓取最新文献和行业资讯，通过大模型进行多维度评估，为研究者提供经过筛选和排序的前沿学术动态。
      </p>
    </div>

    <div class="mb-10">
      <h3 class="text-sm font-medium text-slate-700 dark:text-slate-200 mb-3">评分体系</h3>
      <div class="space-y-3 text-sm text-slate-600 dark:text-slate-500 leading-relaxed">
        <p><strong class="text-slate-700 dark:text-slate-200">前沿技术度 (40%)</strong>：论文是否涉及或采用了当前前沿的技术或方法论</p>
        <p><strong class="text-slate-700 dark:text-slate-200">业务落地值 (35%)</strong>：研究成果是否具有直接的实践应用价值</p>
        <p><strong class="text-slate-700 dark:text-slate-200">方法严谨性 (25%)</strong>：研究方法是否规范、严谨</p>
        <p class="text-xs text-slate-400 dark:text-slate-500 mt-2">综合评分 ≥ 7.5 的文献进入精选</p>
        <p class="text-xs text-slate-400 dark:text-slate-500 mt-3"><strong>资讯评分</strong>：时效性 (30%) + 领域相关性 (40%) + 信息价值 (30%)</p>
      </div>
    </div>

    <div class="mb-10">
      <h3 class="text-sm font-medium text-slate-700 dark:text-slate-200 mb-3">数据质量控制</h3>
      <div class="space-y-3 text-sm text-slate-600 dark:text-slate-500 leading-relaxed">
        <p>系统会在写入数据前校验字段结构、评分范围和分类标签，减少格式异常对前端展示的影响。</p>
        <p>抓取阶段会过滤明显的期刊元数据页和导航条目，例如封面图、期号说明等非研究内容。</p>
        <p class="text-xs text-slate-400 dark:text-slate-500 mt-2">大模型评分仍作为辅助判断，最终结果建议结合原文阅读。</p>
      </div>
    </div>

    <div class="mb-10">
      <h3 class="text-sm font-medium text-slate-700 dark:text-slate-200 mb-3">数据源</h3>
      <h4 class="text-xs font-medium text-slate-500 dark:text-slate-500 mb-2 mt-3">A类 · 国际核心期刊</h4>
      <ul class="space-y-1.5 text-sm text-slate-600 dark:text-slate-500">
        <li>Scientometrics</li>
        <li>JASIST</li>
        <li>Journal of Informetrics</li>
        <li>Library & Information Science Research</li>
        <li>Information Processing & Management</li>
        <li>The Electronic Library</li>
      </ul>
      <h4 class="text-xs font-medium text-slate-500 dark:text-slate-500 mb-2 mt-4">B类 · 国内权威期刊</h4>
      <ul class="space-y-1.5 text-sm text-slate-600 dark:text-slate-500">
        <li>中国图书馆学报</li>
        <li>大学图书馆学报</li>
        <li>图书情报工作</li>
        <li>情报学报</li>
      </ul>
      <h4 class="text-xs font-medium text-slate-500 dark:text-slate-500 mb-2 mt-4">C类 · 预印本与行业资讯</h4>
      <ul class="space-y-1.5 text-sm text-slate-600 dark:text-slate-500">
        <li>arXiv (cs.DL, cs.IR, cs.CL, cs.SI)</li>
        <li>NISO · LIBER · ARL</li>
        <li>Scholarly Kitchen · Infodocket</li>
        <li>LSE Impact Blog · SPARC News</li>
        <li>Code4Lib Journal · First Monday</li>
        <li>CALIS · CADAL</li>
      </ul>
    </div>

    <div class="mb-10">
      <h3 class="text-sm font-medium text-slate-700 dark:text-slate-200 mb-3">技术栈</h3>
      <p class="text-sm text-slate-600 dark:text-slate-500 leading-relaxed">
        Python 后端 + Vue 3 前端 + 大模型辅助评估 · 静态部署于 GitHub Pages
      </p>
    </div>

    <div class="pt-6 border-t border-gray-100 dark:border-slate-800">
      <p class="text-xs text-slate-400 dark:text-slate-500 leading-relaxed">
        评分由大模型自动生成，仅供学术参考，不构成任何形式的学术评价。
      </p>
    </div>

    <div class="mt-6">
      <p class="text-xs text-slate-400 dark:text-slate-500">&copy; USTC Lib · Han</p>
    </div>
  </div>
</template>
