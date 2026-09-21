const modelData = [
  { name: '示例模型 A', mention: 40, rank: 2, score: 20.0 },
  { name: '示例模型 B', mention: 40, rank: 3, score: 19.4 },
  { name: '示例模型 C', mention: 40, rank: 4, score: 18.8 },
  { name: '示例模型 D', mention: 40, rank: 2, score: 18.2 },
  { name: '示例模型 E', mention: 40, rank: 3, score: 17.6 },
  { name: '示例模型 F', mention: 40, rank: 4, score: 17.0 }
];

const metrics = {
  mention: { label: '整体品牌提及率', value: 40, max: 100, suffix: '%' },
  mentionZh: { label: '中文名称提及率', value: 40, max: 100, suffix: '%' },
  mentionEn: { label: '英文名称提及率', value: 0, max: 100, suffix: '%' },
  rank: { label: '平均排名', value: 3.0, max: 6, suffix: '' },
  score: { label: '透明复现分', value: 18.5, max: 100, suffix: '' }
};

const providerCatalog = [
  {
    id: 'bailian',
    name: '阿里云百炼',
    role: '国产模型聚合 · 推荐主入口',
    coverage: '千问、DeepSeek、Kimi、GLM 等，以控制台实际模型列表为准',
    endpoint: 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions',
    envKey: 'BAILIAN_API_KEY',
    modelHint: '优先 Flash；显式设置 enable_thinking=false',
    docs: 'https://help.aliyun.com/zh/model-studio/get-api-key',
    status: 'recommended'
  },
  {
    id: 'ark',
    name: '火山方舟',
    role: '豆包官方入口 · 国产模型补充',
    coverage: '豆包及方舟控制台已开通模型',
    endpoint: 'https://ark.cn-beijing.volces.com/api/v3/chat/completions',
    envKey: 'ARK_API_KEY',
    modelHint: '选择 Lite / Mini / Turbo；thinking=disabled',
    docs: 'https://docs.volcengine.com/docs/ark/agent-plan-personal-get-started?lang=zh',
    status: 'direct'
  },
  {
    id: 'deepseek',
    name: 'DeepSeek',
    role: '官方直连',
    coverage: 'DeepSeek 开放平台当前可用模型',
    endpoint: 'https://api.deepseek.com/chat/completions',
    envKey: 'DEEPSEEK_API_KEY',
    modelHint: '从官方 API 文档选择当前模型 ID',
    docs: 'https://api-docs.deepseek.com/zh-cn/',
    status: 'direct'
  },
  {
    id: 'gemini',
    name: 'Google Gemini',
    role: '海外模型 · OpenAI 兼容',
    coverage: '支持 OpenAI compatibility 的 Gemini 模型',
    endpoint: 'https://generativelanguage.googleapis.com/v1beta/openai/chat/completions',
    envKey: 'GEMINI_API_KEY',
    modelHint: '从 Google AI Studio / models.list 获取模型 ID',
    docs: 'https://ai.google.dev/gemini-api/docs/openai',
    status: 'direct'
  },
  {
    id: 'openai',
    name: 'OpenAI',
    role: '海外模型 · 官方直连',
    coverage: '支持 Chat Completions 的 OpenAI 模型',
    endpoint: 'https://api.openai.com/v1/chat/completions',
    envKey: 'OPENAI_API_KEY',
    modelHint: '从 OpenAI 官方模型列表选择兼容模型',
    docs: 'https://platform.openai.com/docs/models',
    status: 'direct'
  },
  {
    id: 'openai-compatible',
    name: '其他 OpenAI-compatible 平台',
    role: '通用接入',
    coverage: '任何返回 choices[0].message.content 的 Chat Completions 接口',
    endpoint: 'https://provider.example/v1/chat/completions',
    envKey: 'PROVIDER_API_KEY',
    modelHint: '填写平台提供的准确模型 ID',
    docs: '/PROVIDERS.md',
    status: 'compatible'
  },
  {
    id: 'adapter-needed',
    name: 'Claude 与非兼容接口',
    role: '需要适配器',
    coverage: '原生 Anthropic Messages 等非 OpenAI Chat Completions 协议',
    endpoint: '当前版本不可直接填写',
    envKey: 'unavailable',
    modelHint: '使用兼容网关，或等待原生适配器',
    docs: '/PROVIDERS.md#claude-与非-openai-compatible-接口',
    status: 'pending'
  }
];

const defaultBrandConfig = {
  name: '示例天然食品有限公司',
  aliases: ['示例品牌', 'Example Naturals'],
  businessDescription: '用于演示的虚构食品原料供应商',
  coreOfferings: ['示例产品', '应用方案'],
  primaryMarkets: ['中国', '海外'],
  officialWebsite: 'https://example.com',
  headquarters: '示例城市',
  officialChannels: []
};
const storedBrandConfig = JSON.parse(localStorage.getItem('geoBrandConfig') || 'null');
let brandConfig = {...structuredClone(defaultBrandConfig), ...(storedBrandConfig || {})};

function renderAliases() {
  document.querySelector('#aliasEditor').innerHTML = brandConfig.aliases.map((alias, index) => `
    <span class="alias-chip">${alias}<button type="button" data-alias-index="${index}" aria-label="删除 ${alias}">×</button></span>`).join('');
  document.querySelector('#brandName').value = brandConfig.name;
  document.querySelector('#businessDescription').value = brandConfig.businessDescription || '';
  document.querySelector('#coreOfferings').value = (brandConfig.coreOfferings || []).join('，');
  document.querySelector('#primaryMarkets').value = (brandConfig.primaryMarkets || []).join('，');
  document.querySelector('#officialWebsite').value = brandConfig.officialWebsite || '';
  document.querySelector('#headquarters').value = brandConfig.headquarters || '';
  document.querySelector('#officialChannels').value = (brandConfig.officialChannels || []).join('，');
  document.querySelectorAll('[data-alias-index]').forEach(button => button.addEventListener('click', () => {
    brandConfig.aliases.splice(Number(button.dataset.aliasIndex), 1);
    renderAliases();
  }));
  const previewText = '在候选供应商中，示例品牌提供相关产品。英文资料也可能使用 Example Naturals。';
  const previewMatches = brandConfig.aliases.filter(alias => previewText.toLocaleLowerCase().includes(alias.toLocaleLowerCase()));
  document.querySelector('#matchPreview').textContent = previewMatches.join(' · ') || '当前示例未命中';
}

function showPage(page) {
  document.querySelectorAll('.page-panel').forEach(panel => panel.classList.add('hidden'));
  document.querySelector(`#${page}Page`).classList.remove('hidden');
  document.querySelectorAll('.nav-item[data-page]').forEach(item => item.classList.toggle('active', item.dataset.page === page));
  const titles = {overview: '品牌概览', insights: '趋势监控', answers: '大模型回答记录', settings: '监控配置', setup: '模型接入'};
  document.querySelector('#pageTitle').textContent = titles[page] || '品牌概览';
}

const answerData = window.GEO_ANSWER_DATA || {providers: [], records: []};
let selectedAnswerId = answerData.records[0]?.id || null;
let monitorMetric = 'mentionRate';
let liveMonitoringPlan = structuredClone(answerData.monitoringPlan || {});

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>'"]/g, character => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[character]));
}

function filteredAnswers() {
  const model = document.querySelector('#answerModelFilter').value;
  const state = document.querySelector('#answerStateFilter').value;
  const query = document.querySelector('#answerSearch').value.trim().toLocaleLowerCase();
  return answerData.records.filter(record => {
    const matchesModel = model === 'all' || record.modelProvider === model;
    const review = record.metrics.identity_match_status === 'alias_only';
    const matchesState = state === 'all' || (state === 'review' ? review : record.resultState === state);
    const matchesQuery = !query || record.prompt.toLocaleLowerCase().includes(query);
    return matchesModel && matchesState && matchesQuery;
  });
}

function renderAnswerStats(rows) {
  const mentioned = rows.filter(record => record.metrics.brand_mentioned).length;
  const ranked = rows.filter(record => record.metrics.brand_rank != null).length;
  const review = rows.filter(record => record.metrics.identity_match_status === 'alias_only').length;
  document.querySelector('#answerStats').innerHTML = [
    ['当前回答', rows.length],
    ['品牌提及', mentioned],
    ['明确排名', ranked],
    ['身份待复核', review]
  ].map(([label, value]) => `<article class="card answer-stat"><span>${label}</span><strong>${value}</strong></article>`).join('');
}

function renderAnswerDetail(record) {
  const detail = document.querySelector('#answerDetail');
  if (!record) {
    detail.innerHTML = '<div class="detail-empty">选择一条回答查看原始证据。</div>';
    return;
  }
  const metrics = record.metrics || {};
  const aliases = metrics.matched_aliases || [];
  const evidence = metrics.identity_evidence || [];
  const used = new Set(metrics.citations_used || []);
  detail.innerHTML = `
    <div class="detail-head"><h2>${escapeHtml(record.modelLabel)}</h2><p>${escapeHtml(record.prompt)}</p></div>
    <div class="detail-metrics">
      <div class="detail-metric"><span>品牌提及</span><strong>${metrics.brand_mentioned ? '是' : '否'}</strong></div>
      <div class="detail-metric"><span>推荐排名</span><strong>${metrics.brand_rank ?? '—'}</strong></div>
      <div class="detail-metric"><span>透明分</span><strong>${metrics.visibility_score ?? '—'}</strong></div>
      <div class="detail-metric"><span>结果状态</span><strong>${escapeHtml(record.resultState)}</strong></div>
      <div class="detail-metric"><span>耗时</span><strong>${record.elapsedMs == null ? 'unavailable' : `${record.elapsedMs} ms`}</strong></div>
      <div class="detail-metric"><span>身份判断</span><strong>${metrics.identity_match_status === 'alias_only' ? '待复核' : (metrics.identity_match_status === 'supported' ? '有佐证' : '不适用')}</strong></div>
    </div>
    <section class="detail-section"><h3>命中名称</h3><div class="alias-tags">${aliases.length ? aliases.map(alias => `<span>${escapeHtml(alias)}</span>`).join('') : '<span>未命中</span>'}</div></section>
    <section class="detail-section"><h3>身份佐证</h3><div class="evidence-tags">${evidence.length ? evidence.map(item => `<span>${escapeHtml(item)}</span>`).join('') : '<span>无佐证</span>'}</div></section>
    <section class="detail-section"><h3>模型原始回答</h3><pre class="answer-original">${escapeHtml(record.answerMarkdown || 'unavailable')}</pre></section>
    <section class="detail-section"><h3>搜索证据与引用映射</h3><div class="citation-list">${record.citations.length ? record.citations.map(item => `<div class="citation-item"><strong>${used.has(item.id) ? '已引用' : '搜索辅助'} · ${escapeHtml(item.id)} · ${escapeHtml(item.title || '无标题')}</strong><span>${escapeHtml(item.url || 'URL unavailable')}</span></div>`).join('') : '<div class="citation-item"><strong>引用映射 unavailable</strong></div>'}</div></section>`;
}

function renderAnswerRecords() {
  const rows = filteredAnswers();
  if (!rows.some(record => record.id === selectedAnswerId)) selectedAnswerId = rows[0]?.id || null;
  renderAnswerStats(rows);
  const answerKind = answerData.dataClassification === 'synthetic_demo' ? '条演示回答' : '条真实回答';
  document.querySelector('#answerCountLabel').textContent = `${rows.length} ${answerKind}`;
  document.querySelector('#answerRows').innerHTML = rows.map(record => {
    const metrics = record.metrics || {};
    const review = metrics.identity_match_status === 'alias_only';
    return `<tr data-answer-id="${escapeHtml(record.id)}" class="${record.id === selectedAnswerId ? 'selected' : ''}">
      <td><span class="record-model">${escapeHtml(record.modelLabel)}</span><span class="record-question">${escapeHtml(record.prompt)}</span></td>
      <td><span class="pill ${metrics.brand_mentioned ? 'good' : 'neutral'}">${metrics.brand_mentioned ? '是' : '否'}</span></td>
      <td><strong class="rank-value">${metrics.brand_rank ?? '—'}</strong></td>
      <td><span class="identity-pill ${review ? 'review' : ''}">${review ? '待复核' : (metrics.brand_mentioned ? '有佐证' : '不适用')}</span></td>
    </tr>`;
  }).join('');
  document.querySelector('#answerEmpty').classList.toggle('hidden', rows.length > 0);
  document.querySelectorAll('[data-answer-id]').forEach(row => row.addEventListener('click', () => {
    selectedAnswerId = row.dataset.answerId;
    renderAnswerRecords();
  }));
  renderAnswerDetail(rows.find(record => record.id === selectedAnswerId));
}

function formatMetric(value, suffix = '') {
  if (value == null) return 'unavailable';
  const rounded = Number.isInteger(value) ? value : Number(value).toFixed(1);
  return `${rounded}${suffix}`;
}

function activeTrendRows() {
  const model = document.querySelector('#trendModelFilter').value;
  return model === 'all' ? (answerData.trend || []) : (answerData.modelTrend?.[model] || []);
}

function renderMonitorStats() {
  const history = answerData.batchHistory || [];
  const complete = history.filter(row => row.status === 'complete').length;
  const incomplete = history.length - complete;
  const observedDays = new Set((answerData.trend || []).map(row => row.date)).size;
  const comparableAnswers = (answerData.trend || []).reduce((sum, row) => sum + row.availableCount, 0);
  document.querySelector('#monitorStats').innerHTML = [
    ['真实采集日', observedDays],
    ['完整批次', complete],
    ['可比回答', comparableAnswers],
    ['失败 / 不完整', incomplete]
  ].map(([label, value]) => `<article class="card monitor-stat"><span>${label}</span><strong>${value}</strong></article>`).join('');
}

function renderMonitoringPlan() {
  const plan = liveMonitoringPlan;
  const providerCount = (plan.providers || []).length;
  const questionCount = new Set(answerData.records.map(record => record.prompt)).size;
  const cadenceLabel = plan.cadence === 'daily'
    ? `每天 ${plan.time || ''}`
    : (plan.cadence === 'weekly' ? `每周${weekdayLabels?.[plan.weekday ?? 0] || ''} ${plan.time || ''}` : '仅手动运行');
  document.querySelector('#monitorTimezone').textContent = plan.timezone || 'unavailable';
  document.querySelector('#scheduleCadence').textContent = cadenceLabel;
  document.querySelector('#scheduleScope').textContent = `${providerCount} 个模型 · ${questionCount} 个问题`;
  document.querySelector('#scheduleCalls').textContent = `${providerCount * questionCount} 次搜索 + ${providerCount * questionCount} 次模型`;
  const active = plan.enabled && plan.schedulerStatus === 'installed' && plan.cadence !== 'manual';
  const status = document.querySelector('#scheduleStatus');
  status.textContent = plan.cadence === 'manual' ? '仅手动' : (active ? '自动运行中' : (plan.enabled ? '等待安装调度器' : '未启用'));
  status.classList.toggle('active', active);
  document.querySelector('#scheduleBoundary').textContent = active
    ? '调度器已启用；每次真实运行都会产生搜索与模型调用。'
    : '采集计划已写入项目，但没有安装系统定时器；当前不会自动产生费用。';
}

const weekdayLabels = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日'];

function selectedMonitoringProviders() {
  return [...document.querySelectorAll('[data-monitor-provider]:checked')].map(input => input.value);
}

function renderCadenceSettings() {
  const cadence = document.querySelector('#monitorCadence').value;
  const providers = selectedMonitoringProviders();
  document.querySelector('#monitorWeekdayField').classList.toggle('hidden', cadence !== 'weekly');
  document.querySelector('#monitorTimeField').classList.toggle('hidden', cadence === 'manual');
  const time = document.querySelector('#monitorTime').value || '09:00';
  const weekday = weekdayLabels[Number(document.querySelector('#monitorWeekday').value)] || weekdayLabels[0];
  const cadenceText = cadence === 'daily' ? `每天 ${time}` : (cadence === 'weekly' ? `每周${weekday} ${time}` : '仅手动运行');
  const questionCount = new Set(answerData.records.map(record => record.prompt)).size;
  const calls = providers.length * questionCount;
  document.querySelector('#cadenceSummary').textContent = `${cadenceText} · ${providers.length}个模型 · 每批${calls}次搜索和${calls}次模型调用`;
  renderBudgetEstimate();
}

function readOptionalNumber(id) {
  const value = document.querySelector(`#${id}`).value.trim();
  if (value === '') return null;
  const parsed = Number(value);
  return Number.isFinite(parsed) && parsed >= 0 ? parsed : null;
}

function monthlyRunsForCadence(cadence) {
  if (cadence === 'daily') return 30;
  if (cadence === 'weekly') return 4.33;
  return null;
}

function renderBudgetEstimate() {
  const cadence = document.querySelector('#monitorCadence')?.value || 'manual';
  const providers = selectedMonitoringProviders();
  const questionCount = new Set(answerData.records.map(record => record.prompt)).size;
  const batchCalls = providers.length * questionCount;
  const monthlyRuns = monthlyRunsForCadence(cadence);
  const monthlyCalls = monthlyRuns == null ? null : batchCalls * monthlyRuns;
  const inputTokens = readOptionalNumber('budgetInputTokens');
  const outputTokens = readOptionalNumber('budgetOutputTokens');
  const inputRate = readOptionalNumber('budgetInputRate');
  const outputRate = readOptionalNumber('budgetOutputRate');
  const searchRate = readOptionalNumber('budgetSearchRate');
  const budgetLimit = readOptionalNumber('budgetLimit');

  document.querySelector('#budgetBatchCalls').textContent = `${batchCalls} / ${batchCalls}`;
  document.querySelector('#budgetMonthlyRuns').textContent = monthlyRuns == null ? 'unavailable' : `约 ${monthlyRuns.toFixed(monthlyRuns % 1 ? 2 : 0)} 次`;
  document.querySelector('#budgetMonthlyModelCalls').textContent = monthlyCalls == null ? 'unavailable' : `约 ${Math.round(monthlyCalls)} 次`;
  document.querySelector('#budgetMonthlySearchCalls').textContent = monthlyCalls == null ? 'unavailable' : `约 ${Math.round(monthlyCalls)} 次`;

  const modelCostReady = monthlyCalls != null && inputTokens != null && outputTokens != null && inputRate != null && outputRate != null;
  const searchCostReady = monthlyCalls != null && searchRate != null;
  const modelCost = modelCostReady ? monthlyCalls * ((inputTokens * inputRate + outputTokens * outputRate) / 1_000_000) : null;
  const searchCost = searchCostReady ? monthlyCalls * searchRate / 1000 : null;
  const total = modelCost != null && searchCost != null ? modelCost + searchCost : null;
  const totalElement = document.querySelector('#budgetMonthlyCost');
  const statusElement = document.querySelector('#budgetStatus');
  totalElement.textContent = total == null ? 'unavailable' : `约 ¥${total.toFixed(2)}`;
  totalElement.classList.toggle('over-budget', total != null && budgetLimit != null && total > budgetLimit);
  if (monthlyRuns == null) statusElement.textContent = '手动运行无法预测月次数';
  else if (total == null) statusElement.textContent = '填写模型与搜索实际单价后计算';
  else if (budgetLimit == null) statusElement.textContent = `模型约 ¥${modelCost.toFixed(2)} · 搜索约 ¥${searchCost.toFixed(2)}`;
  else statusElement.textContent = total > budgetLimit ? `预计超过 ¥${budgetLimit.toFixed(0)} 月预算` : `预计在 ¥${budgetLimit.toFixed(0)} 月预算内`;

  const settings = {inputTokens, outputTokens, inputRate, outputRate, searchRate, budgetLimit};
  localStorage.setItem('geoBudgetSettings', JSON.stringify(settings));
}

function loadBudgetSettings() {
  const saved = JSON.parse(localStorage.getItem('geoBudgetSettings') || 'null');
  if (!saved) return renderBudgetEstimate();
  const fields = {
    budgetInputTokens: saved.inputTokens,
    budgetOutputTokens: saved.outputTokens,
    budgetInputRate: saved.inputRate,
    budgetOutputRate: saved.outputRate,
    budgetSearchRate: saved.searchRate,
    budgetLimit: saved.budgetLimit
  };
  Object.entries(fields).forEach(([id, value]) => {
    if (value != null) document.querySelector(`#${id}`).value = value;
  });
  renderBudgetEstimate();
}

function renderProviderGuide() {
  const ready = providerCatalog.filter(provider => provider.status !== 'pending').length;
  document.querySelector('#providerSummary').innerHTML = `
    <article class="card"><span>当前协议</span><strong>OpenAI Chat Completions</strong><small>统一请求与结构化回答</small></article>
    <article class="card"><span>可直接配置</span><strong>${ready} 类</strong><small>聚合、官方直连与兼容平台</small></article>
    <article class="card"><span>密钥存储</span><strong>环境变量 / Keychain</strong><small>不写入页面与报告</small></article>`;
  document.querySelector('#providerGuideGrid').innerHTML = providerCatalog.map(provider => `
    <article class="card provider-guide ${provider.status}">
      <div class="provider-guide-head"><div><span class="provider-kind">${escapeHtml(provider.role)}</span><h2>${escapeHtml(provider.name)}</h2></div><span class="provider-status">${provider.status === 'recommended' ? '推荐' : (provider.status === 'pending' ? '需适配' : '可接入')}</span></div>
      <p>${escapeHtml(provider.coverage)}</p>
      <dl><div><dt>Endpoint</dt><dd><code>${escapeHtml(provider.endpoint)}</code></dd></div><div><dt>环境变量</dt><dd><code>${escapeHtml(provider.envKey)}</code></dd></div><div><dt>模型 ID</dt><dd>${escapeHtml(provider.modelHint)}</dd></div></dl>
      <div class="provider-actions"><button type="button" class="copy-config" data-copy-provider="${escapeHtml(provider.id)}">复制配置片段</button><a href="${escapeHtml(provider.docs)}" target="_blank" rel="noreferrer">官方文档 ↗</a></div>
    </article>`).join('');
  document.querySelectorAll('[data-copy-provider]').forEach(button => button.addEventListener('click', async () => {
    const provider = providerCatalog.find(item => item.id === button.dataset.copyProvider);
    const snippet = `"${provider.id}": {\n  "label": "${provider.name}",\n  "endpoint": "${provider.endpoint}",\n  "name": "replace-with-model-id",\n  "env_key": "${provider.envKey}",\n  "temperature": 0,\n  "max_tokens": 2200\n}`;
    try {
      await navigator.clipboard.writeText(snippet);
      button.textContent = '已复制';
      setTimeout(() => { button.textContent = '复制配置片段'; }, 1400);
    } catch (error) {
      button.textContent = '复制失败';
    }
  }));
}

function fillMonitoringSettings(plan) {
  liveMonitoringPlan = {...liveMonitoringPlan, ...plan};
  document.querySelector('#monitorEnabled').checked = Boolean(liveMonitoringPlan.enabled);
  document.querySelector('#monitorCadence').value = liveMonitoringPlan.cadence || 'daily';
  document.querySelector('#monitorTime').value = liveMonitoringPlan.time || '09:00';
  document.querySelector('#monitorWeekday').value = String(liveMonitoringPlan.weekday ?? 0);
  const selected = new Set(liveMonitoringPlan.providers || []);
  document.querySelector('#monitorProviderOptions').innerHTML = answerData.providers.map(provider => `
    <label class="model-option"><input type="checkbox" data-monitor-provider value="${escapeHtml(provider.id)}" ${selected.has(provider.id) ? 'checked' : ''} /><span>${escapeHtml(provider.label)}</span></label>`).join('');
  document.querySelectorAll('[data-monitor-provider]').forEach(input => input.addEventListener('change', renderCadenceSettings));
  renderCadenceSettings();
  renderMonitoringPlan();
}

async function loadMonitoringSettings() {
  try {
    const response = await fetch('/api/monitoring', {cache: 'no-store'});
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const plan = await response.json();
    fillMonitoringSettings(plan);
    document.querySelector('#monitorSaveState').textContent = '已读取实际配置';
  } catch (error) {
    fillMonitoringSettings(liveMonitoringPlan);
    document.querySelector('#monitorSaveState').textContent = '只读预览 · 配置接口不可用';
  }
}

async function saveMonitoringSettings() {
  const button = document.querySelector('#saveMonitoring');
  const state = document.querySelector('#monitorSaveState');
  const providers = selectedMonitoringProviders();
  if (!providers.length) {
    state.textContent = '至少选择一个模型';
    return;
  }
  button.disabled = true;
  state.textContent = '正在保存';
  try {
    const response = await fetch('/api/monitoring', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        enabled: document.querySelector('#monitorEnabled').checked,
        cadence: document.querySelector('#monitorCadence').value,
        time: document.querySelector('#monitorTime').value || '09:00',
        weekday: Number(document.querySelector('#monitorWeekday').value),
        providers
      })
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || `HTTP ${response.status}`);
    fillMonitoringSettings(payload.monitoring);
    state.textContent = `已保存 · ${new Date().toLocaleTimeString('zh-CN', {hour:'2-digit', minute:'2-digit'})}`;
  } catch (error) {
    state.textContent = `保存失败 · ${error.message}`;
  } finally {
    button.disabled = false;
  }
}

function renderHistoryTrend() {
  const rows = activeTrendRows();
  const chart = document.querySelector('#historyTrendChart');
  document.querySelector('#trendEmpty').classList.toggle('hidden', rows.length > 0);
  if (!rows.length) {
    chart.innerHTML = '';
    return;
  }
  const metric = {
    mentionRate: {label: '品牌提及率', suffix: '%', max: 100},
    averageRank: {label: '平均排名', suffix: '', max: Math.max(6, ...rows.map(row => row.averageRank || 0)), reverse: true},
    averageScore: {label: '透明复现分', suffix: '', max: 100}
  }[monitorMetric];
  const left = 58, right = 690, top = 28, bottom = 215;
  const x = index => rows.length === 1 ? (left + right) / 2 : left + index * (right - left) / (rows.length - 1);
  const ratio = value => {
    if (value == null) return null;
    if (metric.reverse) return 1 - Math.max(0, value - 1) / Math.max(1, metric.max - 1);
    return Math.max(0, Math.min(1, value / metric.max));
  };
  const y = value => bottom - ratio(value) * (bottom - top);
  const valueRows = rows.filter(row => row[monitorMetric] != null);
  const points = valueRows.map(row => `${x(rows.indexOf(row))},${y(row[monitorMetric])}`).join(' ');
  const ticks = [0, .25, .5, .75, 1];
  chart.innerHTML = `<svg viewBox="0 0 720 260" role="img" aria-label="${escapeHtml(metric.label)}历史趋势，共${rows.length}个真实采集日">
    ${ticks.map(tick => {
      const ty = bottom - tick * (bottom - top);
      const label = metric.reverse ? (metric.max - tick * (metric.max - 1)).toFixed(1) : `${Math.round(metric.max * tick)}${metric.suffix}`;
      return `<line x1="${left}" y1="${ty}" x2="${right}" y2="${ty}" stroke="#213546"/><text x="48" y="${ty + 4}" fill="#71879a" text-anchor="end" font-size="11">${label}</text>`;
    }).join('')}
    ${valueRows.length > 1 ? `<polyline points="${points}" fill="none" stroke="#2dd4d3" stroke-width="3" stroke-linejoin="round"/>` : ''}
    ${valueRows.map(row => {
      const index = rows.indexOf(row), cx = x(index), cy = y(row[monitorMetric]);
      return `<circle cx="${cx}" cy="${cy}" r="6" fill="#2dd4d3" stroke="#baffff" stroke-width="2"/><text x="${cx}" y="${Math.max(16, cy - 12)}" fill="#ecffff" text-anchor="middle" font-size="12" font-weight="700">${formatMetric(row[monitorMetric], metric.suffix)}</text>`;
    }).join('')}
    ${rows.map((row, index) => `<text x="${x(index)}" y="240" fill="#8fa2b4" text-anchor="middle" font-size="11">${escapeHtml(row.date)}</text>`).join('')}
  </svg>`;
  const model = document.querySelector('#trendModelFilter').selectedOptions[0]?.textContent || '全部模型';
  document.querySelector('#trendCoverage').textContent = `${model} · ${rows.length} 个真实采集日 · 仅完整且问题集可比的批次`;
}

function renderBatchHistory() {
  const history = answerData.batchHistory || [];
  document.querySelector('#historyCount').textContent = `${history.length} 个本地批次`;
  document.querySelector('#historyRows').innerHTML = history.map(row => {
    const statusLabel = row.status === 'complete' ? '完整' : (row.status === 'partial' ? '部分' : '不可用');
    return `<tr>
      <td>${escapeHtml((row.runAt || 'unavailable').replace('T', ' ').slice(0, 16))}</td>
      <td>${escapeHtml(row.modelLabel)}</td>
      <td><span class="pill ${row.status === 'complete' ? 'good' : 'warning'}">${statusLabel}</span></td>
      <td>${row.availableCount} / ${row.promptCount}</td>
      <td>${formatMetric(row.mentionRate, '%')}</td>
      <td>${formatMetric(row.averageRank)}</td>
      <td>${formatMetric(row.averageScore)}</td>
      <td>${escapeHtml(row.questionSetId)}</td>
    </tr>`;
  }).join('');
}

function renderMonitoring() {
  renderMonitoringPlan();
  renderMonitorStats();
  renderHistoryTrend();
  renderBatchHistory();
}

function renderTrend(metricKey) {
  const metric = metrics[metricKey];
  const plotTop = 28, plotBottom = 205, plotLeft = 58, plotRight = 670;
  const y = plotBottom - (metric.value / metric.max) * (plotBottom - plotTop);
  const ticks = [0, .25, .5, .75, 1];
  document.querySelector('#trendChart').innerHTML = `
    <svg viewBox="0 0 720 246" role="img" aria-label="2026-01-01 ${metric.label} ${metric.value}${metric.suffix}">
      ${ticks.map(t => { const ty=plotBottom-t*(plotBottom-plotTop); return `<line x1="${plotLeft}" y1="${ty}" x2="${plotRight}" y2="${ty}" stroke="#213546"/><text x="48" y="${ty+4}" fill="#71879a" text-anchor="end" font-size="11">${metricKey==='rank'?(metric.max*(1-t)).toFixed(1):Math.round(metric.max*t)+metric.suffix}</text>`}).join('')}
      <line x1="${plotLeft}" y1="${plotBottom}" x2="${plotRight}" y2="${plotBottom}" stroke="#486071"/>
      <line x1="364" y1="${y}" x2="364" y2="${plotBottom}" stroke="#2dd4d3" stroke-dasharray="3 4"/>
      <circle cx="364" cy="${y}" r="7" fill="#2dd4d3" stroke="#baffff" stroke-width="2"/>
      <text x="364" y="${Math.max(18,y-13)}" fill="#ecffff" text-anchor="middle" font-size="14" font-weight="700">${metric.value}${metric.suffix}</text>
      <text x="364" y="231" fill="#8fa2b4" text-anchor="middle" font-size="12">2026-01-01</text>
    </svg>`;
}

function renderBars() {
  document.querySelector('#modelBars').innerHTML = modelData.map(model => `
    <div class="bar-row"><span class="bar-label" title="${model.name}">${model.name}</span><div class="bar-track"><div class="bar-fill" style="width:${model.mention}%"></div></div><strong class="bar-value">${model.mention}%</strong></div>`).join('');
}

function renderScores() {
  document.querySelector('#scoreList').innerHTML = modelData.map(model => `
    <div class="score-item"><div class="score-top"><span>${model.name}</span><strong>${model.score}</strong></div><div class="score-meter"><span style="width:${model.score}%"></span></div></div>`).join('');
}

document.querySelectorAll('.segmented button').forEach(button => button.addEventListener('click', () => {
  document.querySelectorAll('.segmented button').forEach(item => item.classList.remove('active'));
  button.classList.add('active');
  renderTrend(button.dataset.metric);
}));

document.querySelectorAll('.nav-item[data-page]').forEach(button => button.addEventListener('click', () => showPage(button.dataset.page)));
document.querySelector('#addAlias').addEventListener('click', () => {
  const input = document.querySelector('#aliasInput');
  const alias = input.value.trim();
  if (alias && !brandConfig.aliases.some(item => item.toLocaleLowerCase() === alias.toLocaleLowerCase())) {
    brandConfig.aliases.push(alias);
    input.value = '';
    renderAliases();
  }
});
document.querySelector('#aliasInput').addEventListener('keydown', event => {
  if (event.key === 'Enter') document.querySelector('#addAlias').click();
});
document.querySelector('#saveBrand').addEventListener('click', () => {
  const name = document.querySelector('#brandName').value.trim();
  const description = document.querySelector('#businessDescription').value.trim();
  const officialWebsite = document.querySelector('#officialWebsite').value.trim();
  if (!name) return document.querySelector('#brandName').focus();
  if (!description) return document.querySelector('#businessDescription').focus();
  if (!officialWebsite) return document.querySelector('#officialWebsite').focus();
  brandConfig.name = name;
  brandConfig.businessDescription = description;
  brandConfig.coreOfferings = document.querySelector('#coreOfferings').value.split(/[,，]/).map(item => item.trim()).filter(Boolean);
  brandConfig.primaryMarkets = document.querySelector('#primaryMarkets').value.split(/[,，]/).map(item => item.trim()).filter(Boolean);
  brandConfig.officialWebsite = officialWebsite;
  brandConfig.headquarters = document.querySelector('#headquarters').value.trim();
  brandConfig.officialChannels = document.querySelector('#officialChannels').value.split(/[,，]/).map(item => item.trim()).filter(Boolean);
  localStorage.setItem('geoBrandConfig', JSON.stringify(brandConfig));
  document.querySelector('#saveState').textContent = `已保存 · ${new Date().toLocaleTimeString('zh-CN', {hour:'2-digit', minute:'2-digit'})}`;
});
document.querySelector('#resetBrand').addEventListener('click', () => {
  brandConfig = structuredClone(defaultBrandConfig);
  localStorage.removeItem('geoBrandConfig');
  renderAliases();
  document.querySelector('#saveState').textContent = '已恢复当前品牌配置';
});

document.querySelector('#answerModelFilter').insertAdjacentHTML('beforeend', answerData.providers.map(provider => `<option value="${escapeHtml(provider.id)}">${escapeHtml(provider.label)}</option>`).join(''));
document.querySelector('#answerModelFilter').addEventListener('change', renderAnswerRecords);
document.querySelector('#answerStateFilter').addEventListener('change', renderAnswerRecords);
document.querySelector('#answerSearch').addEventListener('input', renderAnswerRecords);
document.querySelector('#trendModelFilter').insertAdjacentHTML('beforeend', answerData.providers.map(provider => `<option value="${escapeHtml(provider.id)}">${escapeHtml(provider.label)}</option>`).join(''));
document.querySelector('#trendModelFilter').addEventListener('change', renderHistoryTrend);
document.querySelectorAll('[data-monitor-metric]').forEach(button => button.addEventListener('click', () => {
  document.querySelectorAll('[data-monitor-metric]').forEach(item => item.classList.remove('active'));
  button.classList.add('active');
  monitorMetric = button.dataset.monitorMetric;
  renderHistoryTrend();
}));
document.querySelector('#monitorCadence').addEventListener('change', renderCadenceSettings);
document.querySelector('#monitorTime').addEventListener('change', renderCadenceSettings);
document.querySelector('#monitorWeekday').addEventListener('change', renderCadenceSettings);
document.querySelector('#saveMonitoring').addEventListener('click', saveMonitoringSettings);
document.querySelectorAll('.budget-inputs input').forEach(input => input.addEventListener('input', renderBudgetEstimate));

renderTrend('mention');
renderBars();
renderScores();
renderAliases();
renderAnswerRecords();
renderMonitoring();
renderProviderGuide();
loadBudgetSettings();
loadMonitoringSettings();
