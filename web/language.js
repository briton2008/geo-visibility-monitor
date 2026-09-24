(() => {
  const translations = new Map(Object.entries({
    'GEO 可见度实验室': 'GEO Visibility Lab',
    '国内大模型可见度': 'AI answer visibility',
    '开源发起': 'Open sourced by',
    '监测': 'Monitor',
    '品牌概览': 'Brand overview',
    '用户提问': 'Questions',
    '数据': 'Data',
    '趋势监控': 'Trend monitoring',
    '大模型回答记录': 'Answer records',
    '系统': 'System',
    '监控配置': 'Monitoring settings',
    '报告导出': 'Export report',
    '6 个模型已接入': '6 models connected',
    '最近采集 2026-01-01': 'Last collection: 2026-01-01',
    '示例品牌 GEO': 'Demo brand GEO',
    '数据概览': 'Overview',
    '一览品牌在国内大模型中的曝光、排名与真实采集趋势': 'Track brand mentions, ranking and verified collection trends across AI models.',
    '一览品牌在不同大模型中的曝光、排名与采集趋势': 'Track brand mentions, ranking and collection trends across AI models.',
    '数据更新': 'Updated',
    '演示数据': 'Demo data',
    '当前页面使用完全虚构的示例品牌、模型和引用，不代表任何真实监测结果。': 'This page uses entirely fictional brands, models and citations. It is not a real monitoring result.',
    '开源项目简介': 'Open-source project overview',
    '可复用的 GEO 品牌监测工具': 'A reusable GEO brand-monitoring tool',
    'GEO Visibility Lab 是一个可自托管、证据可回溯的大模型品牌可见度监测工具。它用固定问题集持续记录品牌提及、明确排名、引用、失败状态和趋势。': 'GEO Visibility Lab is a self-hosted, evidence-bounded tool for monitoring brand visibility across AI-model answers. It uses a stable question set to track mentions, explicit rankings, citations, failures and trends over time.',
    '由桂林恒利原生物科技有限公司基于官网 GEO 实践开发并开源。': 'Developed and open-sourced by Guilin Hengliyuan Biotech Co., Ltd. through its website GEO practice.',
    '访问恒利原官网 ↗': 'Visit the Hengliyuan website ↗',
    '大模型品牌可见度监测': 'AI brand visibility monitoring',
    '桂林恒利原生物科技有限公司开源': 'Open sourced by Guilin Hengliyuan Biotech Co., Ltd.',
    '日期范围': 'Date range',
    '大模型': 'Models',
    '提问分组': 'Question group',
    '竞品': 'Competitors',
    '提问标签': 'Question tags',
    '全部 6 个模型': 'All 6 models',
    '全部分组': 'All groups',
    '全部竞品': 'All competitors',
    '全部标签': 'All tags',
    '品牌提及率': 'Brand mention rate',
    '平均排名': 'Average rank',
    '透明复现分': 'Transparent score',
    '中文名与英文名提及': 'Chinese and English name mentions',
    '任一名称出现都计入整体品牌提及，但分别展示，避免英文知名度掩盖中文名称表现': 'Any configured name counts as a mention, while language-specific rates remain separate.',
    '中文名称': 'Chinese name',
    '英文名称': 'English name',
    '诊断': 'Diagnostic',
    '国内样本已有中文名称认知，本轮未出现英文名称；二者不会互相覆盖。': 'The demo shows Chinese-name mentions and no English-name mentions; the two rates remain independent.',
    '品牌趋势': 'Brand trend',
    '仅展示通过校验的真实采集日': 'Only validated collection dates are shown.',
    '整体提及': 'Overall mentions',
    '透明复现分': 'Transparent score',
    '单日基线': 'Single-day baseline',
    '有效样本 30/30': 'Available samples 30/30',
    '有排名样本 6/30': 'Ranked samples 6/30',
    '公式 v1 · 30/30': 'Formula v1 · 30/30',
    '整体 40%': 'Overall 40%',
    '累计更多采集日后自动连成趋势': 'Additional collection dates will automatically form a trend.',
    '仅展示通过校验的可比较采集日': 'Only validated, comparable collection dates are shown.',
    '中文名': 'Chinese name',
    '英文名': 'English name',
    '模型对比': 'Model comparison',
    '六模型同题、同批次': 'Same questions and batch across six models.',
    '提及率': 'Mention rate',
    '问题表现': 'Question performance',
    '按真实问题汇总': 'Grouped by monitored question.',
    '按监控问题汇总': 'Grouped by monitored question.',
    '查看全部': 'View all',
    '问题': 'Question',
    '提及模型': 'Mentioning models',
    '结果': 'Result',
    '模型透明复现分': 'Transparent score by model',
    '引用证据': 'Citation evidence',
    '模型引用与搜索辅助证据分开核验': 'Model citations and search evidence are verified separately.',
    '暂不生成总排行榜': 'No overall leaderboard yet',
    '查看证据边界': 'View evidence boundaries',
    '全模型提及': 'Mentioned by all models',
    '不同模型的引用映射能力可能不同；引用分为 0 不等于搜索证据为空，需回到回答记录核验。': 'Citation mapping varies by model. A zero citation score does not mean the search evidence was empty; inspect the answer record.',
    '趋势监控': 'Trend monitoring',
    '按同一问题集、同一模型口径持续采集，观察品牌可见度变化': 'Collect with a stable question set and model scope to observe visibility changes.',
    '时区': 'Time zone',
    '采集计划': 'Collection plan',
    '计划配置与实际调度状态分开显示': 'Configuration and scheduler status are shown separately.',
    '未启用': 'Disabled',
    '每批计划调用': 'Planned calls per batch',
    '当前边界': 'Current boundary',
    '采集计划已写入项目，但没有安装系统定时器；当前不会自动产生费用。': 'The collection plan is saved, but no system scheduler is installed. No automatic API cost will be incurred.',
    '真实采集日': 'Collection days',
    '完整批次': 'Complete batches',
    '可比回答': 'Comparable answers',
    '失败 / 不完整': 'Failed / incomplete',
    '真实历史趋势': 'Verified history trend',
    '模型': 'Model',
    '全部模型': 'All models',
    '批次历史': 'Batch history',
    '失败和不完整批次保留原状态，不混入趋势或补成0': 'Failed and incomplete batches retain their status and are never converted to zero.',
    '采集时间': 'Collected at',
    '状态': 'Status',
    '可用回答': 'Available answers',
    '透明分': 'Transparent score',
    '问题集': 'Question set',
    '每个指标都可以回到模型原始回答、排名依据和引用来源': 'Every metric links back to the original answer, ranking evidence and citations.',
    '当前回答': 'Current answers',
    '品牌提及': 'Brand mentions',
    '明确排名': 'Explicit ranks',
    '身份待复核': 'Identity review',
    '全部结果': 'All results',
    '已提及': 'Mentioned',
    '未提及': 'Not mentioned',
    '待复核': 'Review',
    '搜索问题': 'Search questions',
    '采集记录': 'Collection records',
    '模型与问题': 'Model and question',
    '提及': 'Mention',
    '排名': 'Rank',
    '身份': 'Identity',
    '监控配置': 'Monitoring settings',
    '品牌名称与别名会共同参与提及识别，并在回答记录中分别展示': 'The brand name and aliases are all matched and shown separately in answer records.',
    '已读取当前品牌配置': 'Current brand settings loaded',
    '品牌识别名称': 'Brand identity names',
    '主品牌名必填；中文简称、英文名、旧称均可作为别名': 'The primary name is required. Add Chinese, English or legacy names as aliases.',
    '主品牌名': 'Primary brand name',
    '品牌别名 / 英文名': 'Aliases / English names',
    '＋ 添加名称': '+ Add name',
    '客户是做什么的': 'Business profile',
    '业务简介（必填，一句话即可）': 'Business description (required)',
    '核心产品或服务（用逗号分隔）': 'Core products or services (comma separated)',
    '主要市场（用逗号分隔）': 'Primary markets (comma separated)',
    '官方身份资料': 'Official identity evidence',
    '官方网站（必填）': 'Official website (required)',
    '公司所在地': 'Headquarters',
    '其他官方渠道（用逗号分隔）': 'Other official channels (comma separated)',
    '使用边界': 'Boundary',
    '保存品牌配置': 'Save brand settings',
    '恢复当前配置': 'Reset settings',
    '识别预览': 'Match preview',
    '客户填写的名称都会单独查看': 'Every customer-provided name is checked separately.',
    '本条是否计入提及': 'Count as a mention',
    '是': 'Yes',
    '命中名称': 'Matched names',
    '身份佐证': 'Identity evidence',
    '仅名称、无佐证': 'Name only, no evidence',
    '标记复核': 'Flag for review',
    '监控节奏': 'Monitoring cadence',
    '客户可以选择多久查询一次；保存后与采集器共用同一配置': 'Choose how often to monitor; the collector uses the same saved configuration.',
    '正在读取配置': 'Loading settings',
    '启用自动计划': 'Enable automatic schedule',
    '只有外部调度器已安装时才会自动运行': 'Runs automatically only after an external scheduler is installed.',
    '每天一次': 'Daily',
    '每周一次': 'Weekly',
    '仅手动运行': 'Manual only',
    '每周执行日': 'Weekly run day',
    '执行时间': 'Run time',
    '参与模型': 'Included models',
    '保存监控节奏': 'Save cadence',
    '完整': 'Complete',
    '部分': 'Partial',
    '不可用': 'Unavailable',
    '有佐证': 'Supported',
    '不适用': 'Not applicable',
    '命中名称': 'Matched names',
    '模型原始回答': 'Original model answer',
    '搜索证据与引用映射': 'Search evidence and citation mapping'
    ,'品牌名称用于提及识别；业务信息用于生成问题、选择竞品和形成诊断，不会直接写进模型回答，因此不会制造虚假提及。': 'Brand names are used for mention matching. Business context helps question and diagnostic setup but is never inserted into model answers.'
    ,'官网域名 · 完整公司名 · 业务上下文': 'Official domain · full company name · business context'
    ,'回答记录中可展开查看每个名称的命中次数和原文片段。': 'Open an answer record to inspect alias counts and original snippets.'
    ,'已读取实际配置': 'Live settings loaded'
    ,'否': 'No'
    ,'推荐排名': 'Recommended rank'
    ,'结果状态': 'Result state'
    ,'耗时': 'Latency'
    ,'身份判断': 'Identity check'
    ,'未命中': 'No match'
    ,'无佐证': 'No evidence'
    ,'搜索辅助': 'Search evidence'
    ,'回答记录筛选': 'Answer record filters'
    ,'监控趋势指标': 'Monitoring trend metric'
    ,'历史趋势图': 'History trend chart'
    ,'问题集：example-zh-cn-v1 · 5基准 / 0发现': 'Question set: example-zh-cn-v1 · 5 benchmark / 0 discovery'
    ,'数据口径：30 条虚构演示回答': 'Data: 30 synthetic demo answers'
    ,'评分口径：透明复现分 v1': 'Scoring: transparent score v1'
    ,'未知与不可用不填 0': 'Unknown and unavailable values are never filled with zero'
    ,'主导航': 'Main navigation'
    ,'界面语言': 'Interface language'
    ,'刷新': 'Refresh'
    ,'通知': 'Notifications'
    ,'首页筛选': 'Overview filters'
    ,'品牌名称提及拆分': 'Brand-name mention breakdown'
    ,'趋势指标': 'Trend metric'
    ,'品牌趋势图': 'Brand trend chart'
    ,'模型接入': 'Provider setup'
    ,'调用与预算估算': 'Calls and budget estimate'
    ,'按当前问题数、模型数和监控节奏估算；价格由使用者按供应商账单填写': 'Estimated from the current questions, models and cadence; enter rates from your provider bill.'
    ,'估算值': 'Estimate'
    ,'平均输入 Token / 次': 'Average input tokens / call'
    ,'平均输出 Token / 次': 'Average output tokens / call'
    ,'模型输入价（元 / 百万 Token）': 'Model input rate (CNY / 1M tokens)'
    ,'模型输出价（元 / 百万 Token）': 'Model output rate (CNY / 1M tokens)'
    ,'搜索价（元 / 千次）': 'Search rate (CNY / 1K calls)'
    ,'月预算上限（元，可选）': 'Monthly budget limit (CNY, optional)'
    ,'每批模型 / 搜索调用': 'Model / search calls per batch'
    ,'预计每月运行': 'Estimated monthly runs'
    ,'预计每月模型调用': 'Estimated monthly model calls'
    ,'预计每月搜索调用': 'Estimated monthly search calls'
    ,'预计月费用': 'Estimated monthly cost'
    ,'填写实际单价后计算': 'Enter actual rates to calculate'
    ,'费用边界': 'Cost boundary'
    ,'这是预算辅助值，不是账单。不同模型的缓存、深度思考、工具调用和供应商计费规则可能不同，最终以供应商实际 usage 与账单为准。': 'This is a budget estimate, not a bill. Caching, reasoning, tools and billing rules vary; provider usage and invoices remain authoritative.'
    ,'像成熟开源项目一样，从开通账号到连通性检查，每一步都可复制、可验证': 'A reproducible path from account activation to connectivity checks, like a mature open-source project.'
    ,'打开完整接入文档 ↗': 'Open full setup guide ↗'
    ,'推荐组合': 'Recommended stack'
    ,'百炼作为国产模型底座，方舟补豆包，腾讯 WSA 提供独立搜索证据': 'Use Bailian as the domestic model base, Ark for Doubao, and Tencent WSA for independent search evidence.'
    ,'默认选择 Flash / Lite / Turbo，关闭可选深度思考；强制思考模型应替换为快速版本，而不是只修改名称。': 'Use Flash, Lite or Turbo models by default and disable optional reasoning. Replace forced-reasoning models with fast variants rather than merely renaming them.'
    ,'一个聚合平台可以减少账号和密钥数量；关键模型仍可使用官方直连接口做交叉验证。': 'An aggregator reduces accounts and keys; direct official APIs can cross-check critical models.'
    ,'1 · 选择平台': '1 · Choose platform'
    ,'2 · 创建 API Key': '2 · Create API key'
    ,'3 · 写入配置': '3 · Configure'
    ,'4 · Doctor 验证': '4 · Run doctor'
    ,'统一验证': 'Unified verification'
    ,'配置完成后运行': 'Run after setup'
    ,'Doctor 只检查配置与凭据是否可用；真实采集需要单独执行，不会因为打开页面自动产生费用。': 'Doctor checks configuration and credentials only. Real collection is separate and opening the page never incurs API charges.'
    ,'重要：': 'Important:'
    ,'API 结果用于可复现监测，不等于各模型消费端 App、网页端或内部知识库的完全复刻。': 'API results provide a reproducible benchmark, not an exact replay of consumer apps, websites or internal knowledge bases.'
    ,'当前协议': 'Current protocol'
    ,'可直接配置': 'Directly configurable'
    ,'密钥存储': 'Credential storage'
    ,'复制配置片段': 'Copy config snippet'
    ,'已复制': 'Copied'
    ,'复制失败': 'Copy failed'
    ,'官方文档 ↗': 'Official docs ↗'
    ,'推荐': 'Recommended'
    ,'需适配': 'Adapter needed'
    ,'可接入': 'Supported'
    ,'统一请求与结构化回答': 'Unified requests and structured answers'
    ,'聚合、官方直连与兼容平台': 'Aggregators, direct APIs and compatible platforms'
    ,'环境变量 / Keychain': 'Environment variables / Keychain'
    ,'不写入页面与报告': 'Never written to pages or reports'
    ,'国产模型聚合 · 推荐主入口': 'Domestic model aggregator · recommended entry point'
    ,'阿里云百炼': 'Alibaba Cloud Model Studio'
    ,'千问、DeepSeek、Kimi、GLM 等，以控制台实际模型列表为准': 'Qwen, DeepSeek, Kimi and GLM, subject to the models enabled in your console'
    ,'环境变量': 'Environment variable'
    ,'模型 ID': 'Model ID'
    ,'优先 Flash；显式设置 enable_thinking=false': 'Prefer Flash and explicitly set enable_thinking=false'
    ,'豆包官方入口 · 国产模型补充': 'Official Doubao entry point · domestic model supplement'
    ,'火山方舟': 'Volcengine Ark'
    ,'豆包及方舟控制台已开通模型': 'Doubao and other models enabled in the Ark console'
    ,'选择 Lite / Mini / Turbo；thinking=disabled': 'Choose Lite, Mini or Turbo and set thinking=disabled'
    ,'官方直连': 'Official direct API'
    ,'DeepSeek 开放平台当前可用模型': 'Models currently available through the DeepSeek open platform'
    ,'从官方 API 文档选择当前模型 ID': 'Select a current model ID from the official API documentation'
    ,'海外模型 · OpenAI 兼容': 'International model · OpenAI compatible'
    ,'支持 OpenAI compatibility 的 Gemini 模型': 'Gemini models that support OpenAI compatibility'
    ,'从 Google AI Studio / models.list 获取模型 ID': 'Get a model ID from Google AI Studio or models.list'
    ,'海外模型 · 官方直连': 'International model · official direct API'
    ,'支持 Chat Completions 的 OpenAI 模型': 'OpenAI models that support Chat Completions'
    ,'从 OpenAI 官方模型列表选择兼容模型': 'Choose a compatible model from the official OpenAI model list'
    ,'通用接入': 'Generic integration'
    ,'其他 OpenAI-compatible 平台': 'Other OpenAI-compatible platforms'
    ,'任何返回 choices[0].message.content 的 Chat Completions 接口': 'Any Chat Completions endpoint returning choices[0].message.content'
    ,'填写平台提供的准确模型 ID': 'Enter the exact model ID supplied by the platform'
    ,'需要适配器': 'Adapter required'
    ,'Claude 与非兼容接口': 'Claude and non-compatible APIs'
    ,'原生 Anthropic Messages 等非 OpenAI Chat Completions 协议': 'Native Anthropic Messages and other non-OpenAI Chat Completions protocols'
    ,'当前版本不可直接填写': 'Not directly configurable in this version'
    ,'使用兼容网关，或等待原生适配器': 'Use a compatible gateway or wait for a native adapter'
    ,'加入交流': 'Join the community'
    ,'GEO 开源交流群': 'GEO open-source community'
    ,'扫码加入微信群，交流模型接入、监控口径和部署经验。二维码到期后只需替换 assets/community-wechat.jpg，页面地址保持不变。': 'Scan the QR code to join the WeChat group for model integration, monitoring methodology and deployment discussions. When it expires, replace assets/community-wechat.jpg without changing the page URL.'
    ,'扫码加入微信群，交流模型接入、监控口径和部署经验。二维码到期后只需替换': 'Scan the QR code to join the WeChat group for model integration, monitoring methodology and deployment discussions. When it expires, replace'
    ,'，页面地址保持不变。': 'without changing the page URL.'
    ,'当前二维码由微信生成，预计在 2026-09-28 前有效；若已失效，请等待仓库更新。': 'This WeChat QR code is expected to remain valid through 2026-09-28. If it has expired, please wait for the repository update.'
    ,'打开微信群二维码大图': 'Open the full-size WeChat group QR code'
    ,'本机真实采集': 'Local verified collection'
    ,'本轮已分别检查中英文名称；英文名未出现，不会被中文名提及覆盖。': 'Chinese and English names were checked separately. No English-name mention appeared, and Chinese mentions do not overwrite that result.'
    ,'中英文品牌名均已出现；两种名称分别计算，不互相覆盖。': 'Both Chinese and English brand names appeared. The two rates are measured independently.'
  }));

  const placeholders = new Map([
    ['输入问题关键词', 'Enter question keywords'],
    ['例如：Hengli Yuan', 'For example: Example Naturals'],
    ['例如：面向食品饮料企业的天然甜味剂原料供应商', 'For example: Ingredient supplier for food and beverage companies'],
    ['例如：罗汉果提取物，复配甜味剂，OEM/ODM服务', 'For example: product A, solution B, OEM services'],
    ['例如：中国，东南亚，欧洲', 'For example: China, Southeast Asia, Europe'],
    ['https://example.com', 'https://example.com'],
    ['例如：中国广西桂林', 'For example: Shanghai, China'],
    ['例如：微信公众号，LinkedIn公司主页', 'For example: WeChat, LinkedIn company page']
    ,['未填写则 unavailable', 'Unavailable when blank']
    ,['例如：100', 'For example: 100']
  ]);

  const originalTexts = new WeakMap();
  const originalAttributes = new WeakMap();

  function translateText(value) {
    const trimmed = value.trim();
    if (!trimmed) return value;
    const exact = translations.get(trimmed);
    if (exact) return value.replace(trimmed, exact);
    return value
      .replace(/(\d+) 条真实回答/g, '$1 verified answers')
      .replace(/(\d+) 条演示回答/g, '$1 demo answers')
      .replace(/(\d+) 条本机真实回答/g, '$1 local verified answers')
      .replace(/(\d+)\/(\d+) 条回答/g, '$1/$2 answers')
      .replace(/(\d+) 个模型已接入/g, '$1 models connected')
      .replace(/最近采集\s+([\d-]+|unavailable)/g, 'Last collection: $1')
      .replace(/全部\s+(\d+)\s+个模型/g, 'All $1 models')
      .replace(/(\d+) 模型同题、同批次/g, 'Same questions and batch across $1 models')
      .replace(/有效样本\s+([^ ]+)\s+单日基线/g, 'Available samples $1 Single-day baseline')
      .replace(/有排名样本\s+([^ ]+)\s+单日基线/g, 'Ranked samples $1 Single-day baseline')
      .replace(/公式 v1 ·\s+([^ ]+)\s+单日基线/g, 'Formula v1 · $1 Single-day baseline')
      .replace(/问题集：([^ ]+) · (\d+)基准 \/ 0发现/g, 'Question set: $1 · $2 benchmark / 0 discovery')
      .replace(/数据口径：(\d+) 条本机真实回答/g, 'Data: $1 local verified answers')
      .replace(/当前展示 ([\d-]+) 的本机 API 采集结果；仅代表固定问题集与当次模型回答，不等同于消费者端产品实时结果。/g, 'Showing local API results collected on $1. They represent this fixed question set and batch, not live consumer-product results.')
      .replace(/(\d+) 类/g, '$1 types')
      .replace(/(\d+) 个本地批次/g, '$1 local batches')
      .replace(/(\d+) 个真实采集日/g, '$1 verified collection days')
      .replace(/每天\s+(\d{2}:\d{2})/g, 'Daily at $1')
      .replace(/Daily at (\d{2}:\d{2}) · (\d+)个模型 · 每批(\d+)次搜索和(\d+)次模型调用/g, 'Daily at $1 · $2 models · $3 search and $4 model calls per batch')
      .replace(/(\d+) 个模型 · (\d+) 个问题/g, '$1 models · $2 questions')
      .replace(/(\d+) 次搜索 \+ (\d+) 次模型/g, '$1 search calls + $2 model calls')
      .replace(/约\s+([\d.]+)\s+次/g, 'About $1')
      .replace(/约\s+¥([\d.]+)/g, 'About ¥$1')
      .replace(/预计在\s+¥([\d.]+)\s+月预算内/g, 'Within the ¥$1 monthly budget')
      .replace(/预计超过\s+¥([\d.]+)\s+月预算/g, 'Exceeds the ¥$1 monthly budget')
      .replace(/模型约\s+¥([\d.]+)\s+·\s+搜索约\s+¥([\d.]+)/g, 'Model about ¥$1 · search about ¥$2')
      .replace(/全部模型 · (\d+) verified collection days · 仅完整且问题集可比的批次/g, 'All models · $1 verified collection days · complete comparable batches only')
      .replace(/每天\s+(\d{2}:\d{2}) · (\d+)个模型 · 每批(\d+)次搜索和(\d+)次模型调用/g, 'Daily at $1 · $2 models · $3 search and $4 model calls per batch')
      .replace(/^删除\s+/, 'Remove ')
      .replace(/示例模型 ([A-F])/g, 'Demo model $1')
      .replace(/星期一/g, 'Monday').replace(/星期二/g, 'Tuesday').replace(/星期三/g, 'Wednesday')
      .replace(/星期四/g, 'Thursday').replace(/星期五/g, 'Friday').replace(/星期六/g, 'Saturday').replace(/星期日/g, 'Sunday');
  }

  function translateNode(root, language) {
    if (root.nodeType === Node.TEXT_NODE) {
      if (!originalTexts.has(root)) originalTexts.set(root, root.nodeValue);
      root.nodeValue = language === 'en' ? translateText(originalTexts.get(root)) : originalTexts.get(root);
      return;
    }
    if (root.nodeType !== Node.ELEMENT_NODE) return;
    if (root.matches('script, style, pre.answer-original')) return;
    if (!originalAttributes.has(root)) {
      originalAttributes.set(root, {
        placeholder: root.getAttribute('placeholder'),
        title: root.getAttribute('title'),
        ariaLabel: root.getAttribute('aria-label')
      });
    }
    const attrs = originalAttributes.get(root);
    if (attrs.placeholder !== null) root.setAttribute('placeholder', language === 'en' ? (placeholders.get(attrs.placeholder) || attrs.placeholder) : attrs.placeholder);
    if (attrs.title !== null) root.setAttribute('title', language === 'en' ? translateText(attrs.title) : attrs.title);
    if (attrs.ariaLabel !== null) root.setAttribute('aria-label', language === 'en' ? translateText(attrs.ariaLabel) : attrs.ariaLabel);
    [...root.childNodes].forEach(child => translateNode(child, language));
  }

  let currentLanguage = localStorage.getItem('geoUiLanguage') || 'zh';
  function applyLanguage(language) {
    currentLanguage = language === 'en' ? 'en' : 'zh';
    document.documentElement.lang = currentLanguage === 'en' ? 'en' : 'zh-CN';
    translateNode(document.body, currentLanguage);
    document.querySelectorAll('[data-language]').forEach(button => button.classList.toggle('active', button.dataset.language === currentLanguage));
    localStorage.setItem('geoUiLanguage', currentLanguage);
  }

  document.querySelectorAll('[data-language]').forEach(button => button.addEventListener('click', () => applyLanguage(button.dataset.language)));
  const observer = new MutationObserver(records => {
    if (currentLanguage !== 'en') return;
    records.forEach(record => record.addedNodes.forEach(node => translateNode(node, 'en')));
  });
  observer.observe(document.body, {childList: true, subtree: true});
  applyLanguage(currentLanguage);
})();
