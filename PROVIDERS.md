# 模型接入指南 / Provider Setup

> 最后核对：2026-09-21。供应商会调整模型名称、价格和接口范围；配置前请再次查看对应官方文档。

GEO Visibility Monitor 当前原生使用 **OpenAI-compatible Chat Completions** 请求格式。无需安装各厂商 SDK，只需要四项配置：完整 `endpoint`、模型 `name`、密钥环境变量 `env_key` 和展示名称 `label`。

## 推荐接入路线

对于主要监控国产模型的项目，建议从以下组合开始：

1. **阿里云百炼按量 API**：用一个业务空间和 API Key 接入千问及控制台中已经提供的 DeepSeek、Kimi、GLM 等模型。
2. **火山方舟通用模型 API**：补充豆包官方模型。
3. **腾讯云 WSA**：作为独立搜索证据层；它与模型 API 分开计费、分开判断。
4. 对关键模型再增加官方直连，用相同问题做交叉验证。

### 默认低成本策略

监控任务通常只需要稳定的结构化回答，不需要长链路推理。建议默认使用 **Flash / Lite / Turbo** 模型，并显式关闭可选的深度思考：

- 千问：`qwen3.8-flash`，请求体增加 `"enable_thinking": false`。
- Kimi：使用支持非思考模式的 `kimi-k2.5`，不要使用仅思考的 `kimi-k3`。
- 豆包：选择控制台当前可用的 Lite / Mini / Turbo 版本，并增加 `"thinking": {"type": "disabled"}`。
- 文心：使用 ERNIE Turbo 文本模型；不要额外启用搜索增强或思考功能。
- DeepSeek / GLM：只有模型官方明确支持关闭思考时才传关闭参数；若模型是强制思考型，应在控制台换成快速非思考版本，不能仅修改展示名称。

本项目会将 `extra_payload` 原样合并到 Chat Completions 请求体。典型配置如下：

```json
"extra_payload": {
  "enable_thinking": false
}
```

火山方舟使用：

```json
"extra_payload": {
  "thinking": {"type": "disabled"}
}
```

不同接口对参数名称的支持并不完全相同。配置后必须运行 `doctor`，再做一次真实采集并检查报告中的 `usage`；接口拒绝参数时应更换模型或参数，不能静默假定思考已经关闭。

不要把 Coding Plan、Token Plan 等仅限编程工具的套餐密钥用于本项目的自动化监控。若供应商条款限制自定义应用或工作流，请使用其按量 API Key。

## 通用安装流程

```bash
cd geo-visibility-monitor
python3 scripts/bootstrap.py
```

打开 `config.json`，在 `models` 中增加一个供应商：

```json
{
  "models": {
    "my-provider": {
      "label": "模型展示名称",
      "endpoint": "https://provider.example/v1/chat/completions",
      "name": "provider-model-id",
      "env_key": "MY_PROVIDER_API_KEY",
      "keychain_service": "geo-monitor-my-provider",
      "temperature": 0,
      "max_tokens": 2200,
      "timeout_seconds": 120
    }
  }
}
```

在当前终端临时设置密钥：

```bash
export MY_PROVIDER_API_KEY='your-api-key'
python3 domestic_geo.py doctor
python3 domestic_geo.py run --provider my-provider
python3 build_web_data.py
```

不要把 API Key 写入 `config.json`、截图、Issue 或 Git 提交。正式部署建议使用环境变量、系统 Secret Manager 或 macOS Keychain。

## 阿里云百炼

适合：希望用一个平台覆盖多数国产模型。

1. 在百炼控制台创建业务空间和按量 API Key。
2. 在模型广场确认需要的模型已对该业务空间开放。
3. 复制控制台显示的准确模型 ID；不同地域的 API Key 与 Base URL 不可混用。

北京地域常用配置：

```json
"bailian-qwen": {
  "label": "Qwen via Bailian",
  "endpoint": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
  "name": "qwen3.8-flash",
  "env_key": "BAILIAN_API_KEY",
  "temperature": 0,
  "max_tokens": 2200,
  "timeout_seconds": 120,
  "extra_payload": {"enable_thinking": false}
}
```

同一个百炼 API Key 可以配置多个 provider 条目，每个条目使用不同 `name`，分别监控千问、DeepSeek、Kimi 或 GLM。是否可用以当前业务空间的模型列表为准。

- [获取与配置百炼 API Key](https://help.aliyun.com/zh/model-studio/get-api-key)
- [百炼 OpenAI 兼容说明](https://help.aliyun.com/zh/model-studio/what-is-model-studio)

## 火山方舟 / 豆包

适合：需要豆包官方模型样本。

1. 开通火山方舟通用模型服务并创建 API Key。
2. 在控制台开通目标模型，复制模型 ID 或推理接入点 ID。
3. 本项目是监控应用，使用通用模型 API，不使用仅限编程工具的 Coding Plan 地址。

```json
"ark-doubao": {
  "label": "Doubao via Ark",
  "endpoint": "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
  "name": "replace-with-current-lite-mini-or-turbo-id",
  "env_key": "ARK_API_KEY",
  "temperature": 0,
  "max_tokens": 2200,
  "timeout_seconds": 120,
  "extra_payload": {"thinking": {"type": "disabled"}}
}
```

- [火山方舟文档](https://docs.volcengine.com/docs/82379)

## DeepSeek 官方直连

适合：需要把聚合平台结果与 DeepSeek 官方 API 对照。

```json
"deepseek-direct": {
  "label": "DeepSeek Direct",
  "endpoint": "https://api.deepseek.com/chat/completions",
  "name": "replace-with-current-deepseek-model-id",
  "env_key": "DEEPSEEK_API_KEY",
  "temperature": 0,
  "max_tokens": 2200,
  "timeout_seconds": 120
}
```

模型名会变化，不在示例配置里锁死；从官方“首次调用 API”页面复制当前模型 ID。

- [DeepSeek API 首次调用](https://api-docs.deepseek.com/zh-cn/)

## Google Gemini

Gemini 官方提供 OpenAI compatibility，可直接接入：

```json
"gemini-direct": {
  "label": "Google Gemini",
  "endpoint": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
  "name": "replace-with-current-gemini-model-id",
  "env_key": "GEMINI_API_KEY",
  "temperature": 0,
  "max_tokens": 2200,
  "timeout_seconds": 120
}
```

- [Gemini OpenAI compatibility](https://ai.google.dev/gemini-api/docs/openai)

## OpenAI

```json
"openai-direct": {
  "label": "OpenAI",
  "endpoint": "https://api.openai.com/v1/chat/completions",
  "name": "replace-with-chat-completions-model-id",
  "env_key": "OPENAI_API_KEY",
  "temperature": 0,
  "max_tokens": 2200,
  "timeout_seconds": 120
}
```

本项目当前使用 Chat Completions；请选择官方模型列表中兼容该接口且支持结构化 JSON 输出的模型。

- [OpenAI 模型列表](https://platform.openai.com/docs/models)

## Claude 与非 OpenAI-compatible 接口

Anthropic 原生 Messages API 的请求和响应结构与当前采集器不同，因此当前版本不能把 `api.anthropic.com` 直接填入 `endpoint`。可选方案：

- 通过明确支持 OpenAI Chat Completions 的合规网关接入；或
- 为本项目贡献 Anthropic adapter，并为结构化输出、错误分类和 usage 字段补测试。

不要仅仅修改 URL 后宣称已支持 Claude。只有 `doctor` 和一次真实测试均通过，才算完成接入。

## 腾讯云 WSA 搜索层

模型 API 与联网搜索证据是两个独立层。搜索配置位于 `config.json` 的 `search`：

```json
"search": {
  "endpoint": "https://api.wsa.cloud.tencent.com/SearchPro",
  "mode": 0,
  "results_per_prompt": 10,
  "timeout_seconds": 45
}
```

```bash
export TENCENTCLOUD_WSA_APIKEY='your-search-key'
```

搜索接口不可用时，记录为来源缺口，不把“没有数据”写成品牌未收录或排名为 0。

## 常见错误

| 状态 | 优先检查 |
|---|---|
| `401 / 403` | API Key、地域、业务空间权限、套餐密钥是否允许自定义应用 |
| `404` | `endpoint` 是否包含 `/chat/completions`，模型 ID 是否存在 |
| `429` | RPM/TPM 限额、余额、并发数 |
| `parse_error` | 模型是否支持 JSON 输出，是否返回了代码围栏或额外说明 |
| `timeout` | 网络、代理、模型响应速度与 `timeout_seconds` |

接入成功只代表 API 可以返回结果，不代表它完全复刻对应消费端 App 的搜索、记忆、系统提示词和产品编排。
