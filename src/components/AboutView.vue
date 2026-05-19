<template>
  <div class="max-w-2xl">
    <div class="mb-10">
      <h2 class="text-lg font-light text-slate-800 mb-4">关于 Scholar-Radar</h2>
      <p class="text-sm text-slate-600 leading-relaxed">
        Scholar-Radar 是一个自动化的图情领域学术追踪系统。每日从多个学术信息源抓取最新文献和行业资讯，通过大模型进行多维度评估，为研究者提供经过筛选和排序的前沿学术动态。
      </p>
    </div>

    <div class="mb-10">
      <h3 class="text-sm font-medium text-slate-700 mb-3">评分体系</h3>
      <div class="space-y-3 text-sm text-slate-600 leading-relaxed">
        <p><strong class="text-slate-700">前沿技术度 (40%)</strong>：论文是否涉及或采用了当前前沿的技术或方法论</p>
        <p><strong class="text-slate-700">业务落地值 (35%)</strong>：研究成果是否具有直接的实践应用价值</p>
        <p><strong class="text-slate-700">方法严谨性 (25%)</strong>：研究方法是否规范、严谨</p>
        <p class="text-xs text-slate-400 mt-2">综合评分 ≥ 7.5 的文献进入精选</p>
        <p class="text-xs text-slate-400 mt-3"><strong>资讯评分</strong>：时效性 (30%) + 领域相关性 (40%) + 信息价值 (30%)</p>
      </div>
    </div>

    <div class="mb-10">
      <h3 class="text-sm font-medium text-slate-700 mb-3">数据源</h3>
      <h4 class="text-xs font-medium text-slate-500 mb-2 mt-3">学术论文</h4>
      <ul class="space-y-1.5 text-sm text-slate-600">
        <li>arXiv - Digital Libraries (cs.DL)</li>
        <li>arXiv - Information Retrieval (cs.IR)</li>
        <li>arXiv - Computation & Language (cs.CL)</li>
        <li>arXiv - Social Networks (cs.SI)</li>
        <li>Information Processing & Management</li>
        <li>Code4Lib Journal</li>
        <li>First Monday</li>
      </ul>
      <h4 class="text-xs font-medium text-slate-500 mb-2 mt-4">行业资讯</h4>
      <ul class="space-y-1.5 text-sm text-slate-600">
        <li>Scholarly Kitchen</li>
        <li>Infodocket</li>
        <li>LSE Impact Blog</li>
        <li>SPARC News</li>
      </ul>
    </div>

    <div class="mb-10">
      <h3 class="text-sm font-medium text-slate-700 mb-3">技术栈</h3>
      <p class="text-sm text-slate-600 leading-relaxed">
        Python 后端 + Vue 3 前端 + 大模型辅助评估 · 静态部署于 GitHub Pages
      </p>
    </div>

    <div class="pt-6 border-t border-gray-100">
      <p class="text-xs text-slate-400 leading-relaxed">
        评分由大模型自动生成，仅供学术参考，不构成任何形式的学术评价。
      </p>
    </div>
  </div>
</template>
