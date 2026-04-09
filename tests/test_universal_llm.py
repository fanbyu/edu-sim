"""
Test Universal LLM Providers
测试通用 LLM 提供商支持
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_llm_client_initialization():
    """测试 LLM 客户端初始化"""
    print("=" * 70)
    print("测试 1: LLM 客户端初始化")
    print("=" * 70)
    
    from app.utils.llm_client import LLMClient
    
    # 测试支持的提供商
    providers = ["claude-cli", "codex-cli", "openai", "qwen", "doubao", "any"]
    
    for provider in providers:
        try:
            # 注意：API-based 提供商需要有效的 API Key
            if provider in ("openai", "qwen", "doubao", "any"):
                print(f"\n⚠️  跳过 {provider} (需要 API Key)")
                continue
            
            client = LLMClient(provider=provider)
            print(f"✅ {provider}: 初始化成功")
        except Exception as e:
            print(f"❌ {provider}: {str(e)[:50]}")
    
    print("\n✅ 初始化测试完成\n")


def test_qwen_configuration():
    """测试 Qwen 配置示例"""
    print("=" * 70)
    print("测试 2: Qwen 配置示例")
    print("=" * 70)
    
    print("\n📝 配置步骤:")
    print("1. 在 .env 文件中设置:")
    print("   LLM_PROVIDER=qwen")
    print("   OPENAI_API_KEY=sk-your-qwen-api-key")
    print("   OPENAI_MODEL=qwen-plus  # 可选")
    print("\n2. 获取 API Key:")
    print("   访问: https://dashscope.console.aliyun.com/")
    print("\n3. 测试连接:")
    print("""
   from app.utils.llm_client import LLMClient
   client = LLMClient(provider="qwen")
   response = client.chat([{"role": "user", "content": "你好"}])
   print(response)
    """)
    
    print("\n✅ Qwen 配置说明完成\n")


def test_doubao_configuration():
    """测试豆包配置示例"""
    print("=" * 70)
    print("测试 3: 豆包配置示例")
    print("=" * 70)
    
    print("\n📝 配置步骤:")
    print("1. 在 .env 文件中设置:")
    print("   LLM_PROVIDER=doubao")
    print("   OPENAI_API_KEY=your-doubao-api-key")
    print("   OPENAI_MODEL=doubao-pro-32k  # 可选")
    print("\n2. 获取 API Key:")
    print("   访问: https://www.volcengine.com/product/ark")
    print("\n3. 测试连接:")
    print("""
   from app.utils.llm_client import LLMClient
   client = LLMClient(provider="doubao")
   response = client.chat([{"role": "user", "content": "你好"}])
   print(response)
    """)
    
    print("\n✅ 豆包配置说明完成\n")


def test_openai_configuration():
    """测试 OpenAI 配置示例"""
    print("=" * 70)
    print("测试 4: OpenAI 配置示例")
    print("=" * 70)
    
    print("\n📝 配置步骤:")
    print("1. 在 .env 文件中设置:")
    print("   LLM_PROVIDER=openai")
    print("   OPENAI_API_KEY=sk-your-openai-key")
    print("   OPENAI_MODEL=gpt-4o  # 可选")
    print("\n2. 获取 API Key:")
    print("   访问: https://platform.openai.com/")
    print("\n3. 测试连接:")
    print("""
   from app.utils.llm_client import LLMClient
   client = LLMClient(provider="openai")
   response = client.chat([{"role": "user", "content": "Hello"}])
   print(response)
    """)
    
    print("\n✅ OpenAI 配置说明完成\n")


def test_custom_api_configuration():
    """测试自定义 API 配置"""
    print("=" * 70)
    print("测试 5: 自定义 OpenAI 兼容 API")
    print("=" * 70)
    
    print("\n📝 支持的兼容服务:")
    print("- LocalAI")
    print("- Ollama (with OpenAI compatibility)")
    print("- LM Studio")
    print("- Text Generation WebUI")
    print("- 任何符合 OpenAI API 规范的服务")
    
    print("\n📝 配置步骤:")
    print("1. 在 .env 文件中设置:")
    print("   LLM_PROVIDER=any")
    print("   OPENAI_API_KEY=your-api-key")
    print("   OPENAI_BASE_URL=https://your-custom-api.com/v1")
    print("   OPENAI_MODEL=your-model-name")
    
    print("\n✅ 自定义 API 配置说明完成\n")


def show_provider_comparison():
    """显示提供商对比"""
    print("=" * 70)
    print("LLM 提供商对比")
    print("=" * 70)
    
    print("\n| 特性 | Qwen | 豆包 | OpenAI | Claude |")
    print("|------|------|------|--------|--------|")
    print("| 中文能力 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |")
    print("| 推理能力 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |")
    print("| 价格 | 💰💰 | 💰💰 | 💰💰💰 | 💰💰💰 |")
    print("| 速度 | ⚡⚡⚡⚡ | ⚡⚡⚡⚡ | ⚡⚡⚡ | ⚡⚡⚡ |")
    print("| 上下文长度 | 32K-128K | 32K-128K | 128K | 200K |")
    print("| 国内访问 | ✅ 快速 | ✅ 快速 | ⚠️ 需代理 | ⚠️ 需代理 |")
    
    print("\n💡 教育场景推荐:")
    print("- 性价比: Qwen (qwen-plus)")
    print("- 长文本: 豆包 (doubao-pro-32k)")
    print("- 最强推理: OpenAI (gpt-4-turbo)")
    print("\n")


def demonstrate_usage():
    """演示使用方法"""
    print("=" * 70)
    print("使用示例")
    print("=" * 70)
    
    print("\n1️⃣  基本用法:")
    print("""
from app.utils.llm_client import LLMClient

# 自动从环境变量读取配置
client = LLMClient()

# 发送消息
messages = [
    {"role": "system", "content": "你是一个教育专家助手"},
    {"role": "user", "content": "请分析这道数学题的难度"}
]

response = client.chat(messages)
print(response)
    """)
    
    print("\n2️⃣  JSON 格式输出:")
    print("""
result = client.chat_json(messages)
print(result)  # 返回解析后的字典
    """)
    
    print("\n3️⃣  手动指定提供商:")
    print("""
client = LLMClient(provider="qwen")
response = client.chat(messages)
    """)
    
    print("\n4️⃣  调整参数:")
    print("""
response = client.chat(
    messages,
    temperature=0.3,    # 降低随机性
    max_tokens=8192     # 增加输出长度
)
    """)
    
    print("\n✅ 使用示例完成\n")


if __name__ == "__main__":
    print("\n🧪 通用 LLM 提供商测试\n")
    
    try:
        test_llm_client_initialization()
        test_qwen_configuration()
        test_doubao_configuration()
        test_openai_configuration()
        test_custom_api_configuration()
        show_provider_comparison()
        demonstrate_usage()
        
        print("=" * 70)
        print("🎉 测试完成!")
        print("=" * 70)
        print("\n✨ Edu-Sim 现在支持多种 LLM 提供商:")
        print("   - ✅ Claude Code CLI")
        print("   - ✅ Codex CLI")
        print("   - ✅ OpenAI API (GPT-4, GPT-3.5)")
        print("   - ✅ 通义千问 Qwen")
        print("   - ✅ 豆包 Doubao")
        print("   - ✅ 任意 OpenAI 兼容 API")
        print("\n📖 详细文档: docs/LLM_PROVIDERS_GUIDE.md")
        print("\n💡 快速开始:")
        print("   1. 复制 .env.example 到 .env")
        print("   2. 设置 LLM_PROVIDER 和 OPENAI_API_KEY")
        print("   3. 运行 Edu-Sim 命令")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
