# 通用 LLM 提供商配置指南

## 📋 概述

Edu-Sim 现在支持多种大语言模型提供商，包括：
- ✅ **Claude Code CLI** (默认)
- ✅ **Codex CLI**
- ✅ **OpenAI API** (GPT-4, GPT-3.5)
- ✅ **通义千问 Qwen** (阿里云)
- ✅ **豆包 Doubao** (字节跳动)
- ✅ **任意 OpenAI 兼容 API**

---

## 🔧 快速开始

### 1. 安装依赖

如果使用 API-based 提供商（Qwen/豆包/OpenAI），需要安装 OpenAI SDK：

```bash
pip install openai
```

---

### 2. 配置环境变量

编辑 `.env` 文件（从 `.env.example` 复制）：

```bash
cp .env.example .env
```

---

## 🎯 配置示例

### 方案 1: 使用通义千问 (Qwen)

```env
# 设置提供商
LLM_PROVIDER=qwen

# 阿里云 API 密钥
OPENAI_API_KEY=sk-your-qwen-api-key

# 可选：自定义模型（默认: qwen-plus）
OPENAI_MODEL=qwen-max

# 可选：自定义 API URL（通常不需要）
# OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

**获取 API Key:**
1. 访问 [阿里云 DashScope](https://dashscope.console.aliyun.com/)
2. 创建 API Key
3. 确保账户有余额

---

### 方案 2: 使用豆包 (Doubao)

```env
# 设置提供商
LLM_PROVIDER=doubao

# 火山引擎 API 密钥
OPENAI_API_KEY=your-doubao-api-key

# 可选：自定义模型（默认: doubao-pro-32k）
OPENAI_MODEL=doubao-lite-32k

# 可选：自定义 API URL
# OPENAI_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
```

**获取 API Key:**
1. 访问 [火山引擎方舟平台](https://www.volcengine.com/product/ark)
2. 创建应用并获取 API Key
3. 充值账户

---

### 方案 3: 使用 OpenAI

```env
# 设置提供商
LLM_PROVIDER=openai

# OpenAI API 密钥
OPENAI_API_KEY=sk-your-openai-key

# 可选：自定义模型（默认: gpt-4o）
OPENAI_MODEL=gpt-4-turbo

# 可选：自定义 API URL（通常不需要）
# OPENAI_BASE_URL=https://api.openai.com/v1
```

**获取 API Key:**
1. 访问 [OpenAI Platform](https://platform.openai.com/)
2. 创建 API Key
3. 确保账户有余额

---

### 方案 4: 使用其他 OpenAI 兼容 API

```env
# 设置提供商为 "any"
LLM_PROVIDER=any

# 你的 API 密钥
OPENAI_API_KEY=your-api-key

# 必须指定 API URL
OPENAI_BASE_URL=https://your-custom-api.com/v1

# 必须指定模型名称
OPENAI_MODEL=your-model-name
```

**支持的兼容服务:**
- LocalAI
- Ollama (with OpenAI compatibility)
- LM Studio
- Text Generation WebUI
- 任何符合 OpenAI API 规范的服务

---

### 方案 5: 继续使用 Claude Code (默认)

```env
# 无需额外配置
LLM_PROVIDER=claude-cli
```

**要求:**
- 已安装 Claude Code CLI
- 有有效的 Claude 订阅

---

## 💡 使用示例

### 在代码中使用

```python
from app.utils.llm_client import LLMClient

# 自动从环境变量读取配置
client = LLMClient()

# 或者手动指定
client = LLMClient(provider="qwen")

# 发送消息
messages = [
    {"role": "system", "content": "你是一个教育专家助手"},
    {"role": "user", "content": "请分析这道数学题的难度"}
]

response = client.chat(messages)
print(response)

# JSON 格式输出
result = client.chat_json(messages)
print(result)
```

---

### 在 Edu-Sim CLI 中使用

所有 Edu-Sim 命令都会自动使用配置的 LLM 提供商：

```bash
# 加载数据（会使用配置的 LLM 进行实体抽取）
python -m app.edu_sim_cli load-data \
  --data-root docs/英语数据 \
  --exam-folder 试题1

# 运行仿真
python -m app.edu_sim_cli simulate --rounds 5
```

---

## 📊 各提供商对比

| 特性 | Qwen | 豆包 | OpenAI | Claude |
|------|------|------|--------|--------|
| **中文能力** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **推理能力** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **价格** | 💰💰 | 💰💰 | 💰💰💰 | 💰💰💰 |
| **速度** | ⚡⚡⚡⚡ | ⚡⚡⚡⚡ | ⚡⚡⚡ | ⚡⚡⚡ |
| **上下文长度** | 32K-128K | 32K-128K | 128K | 200K |
| **API 稳定性** | ✅ | ✅ | ✅ | ✅ |
| **国内访问** | ✅ 快速 | ✅ 快速 | ⚠️ 需代理 | ⚠️ 需代理 |

---

## 🔍 故障排查

### 问题 1: `OPENAI_API_KEY environment variable is required`

**原因:** 未设置 API 密钥

**解决:**
```bash
# 方法 1: 在 .env 文件中设置
echo "OPENAI_API_KEY=your-key-here" >> .env

# 方法 2: 在 shell 中导出
export OPENAI_API_KEY=your-key-here
```

---

### 问题 2: `ModuleNotFoundError: No module named 'openai'`

**原因:** 未安装 OpenAI SDK

**解决:**
```bash
pip install openai
```

---

### 问题 3: API 调用超时或失败

**可能原因:**
1. 网络连接问题
2. API Key 无效
3. 账户余额不足
4. API URL 错误

**解决步骤:**
```bash
# 1. 检查网络连接
curl https://dashscope.aliyuncs.com/compatible-mode/v1/models

# 2. 验证 API Key
# 查看提供商文档确认 Key 格式

# 3. 检查余额
# 登录提供商控制台查看账户状态

# 4. 测试 API 调用
python -c "
from app.utils.llm_client import LLMClient
client = LLMClient()
print(client.chat([{'role': 'user', 'content': 'Hello'}]))
"
```

---

### 问题 4: 返回结果为空或格式错误

**可能原因:**
1. 模型不支持 JSON 格式
2. Prompt 太复杂
3. max_tokens 限制

**解决:**
```python
# 增加 max_tokens
response = client.chat(messages, max_tokens=8192)

# 降低 temperature 提高稳定性
response = client.chat(messages, temperature=0.3)

# 简化 Prompt
messages = [
    {"role": "user", "content": "请用简单的方式回答..."}
]
```

---

## 🎓 最佳实践

### 1. 选择合适的模型

**教育场景推荐:**
- **Qwen**: `qwen-plus` (平衡性能和成本)
- **豆包**: `doubao-pro-32k` (长上下文支持)
- **OpenAI**: `gpt-4-turbo` (最强推理能力)

### 2. 优化成本

```env
# 使用更经济的模型进行测试
OPENAI_MODEL=qwen-turbo  # 而非 qwen-max

# 降低 temperature 减少重试
# 在代码中设置
client.chat(messages, temperature=0.3)
```

### 3. 提高稳定性

```python
# 添加重试逻辑
import time

def chat_with_retry(client, messages, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.chat(messages)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # 指数退避
```

### 4. 监控使用情况

```python
# 记录 API 调用
logger.info(f"Calling {provider} API with {len(messages)} messages")

# 统计 token 使用
# (需要在响应中解析 usage 字段)
```

---

## 📚 相关资源

- [阿里云 DashScope 文档](https://help.aliyun.com/zh/dashscope/)
- [火山引擎方舟平台](https://www.volcengine.com/docs/82379)
- [OpenAI API 文档](https://platform.openai.com/docs)
- [OpenAI Python SDK](https://github.com/openai/openai-python)

---

## 🔄 切换提供商

只需修改 `.env` 文件中的 `LLM_PROVIDER`，无需更改代码：

```env
# 从 Qwen 切换到豆包
LLM_PROVIDER=doubao
OPENAI_API_KEY=your-doubao-key
```

重启应用即可生效！

---

**最后更新**: 2026-04-07  
**版本**: v0.3.0
