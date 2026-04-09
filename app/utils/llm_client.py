"""
LLM Client — CLI-only providers (Claude Code, Codex) and OpenAI-compatible APIs.

支持的提供商:
- claude-cli: Claude Code CLI
- codex-cli: Codex CLI  
- openai: OpenAI API (GPT-4, GPT-3.5)
- qwen: 阿里云通义千问 (OpenAI 兼容)
- doubao: 字节跳动豆包 (OpenAI 兼容)
- any: 任意 OpenAI 兼容的 API
"""

import json
import re
import os
import shutil
import subprocess
from typing import Optional, Dict, Any, List

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from ..config import Config
from .logger import get_logger

logger = get_logger('mirofish.llm_client')


class LLMClient:
    """LLM Client — supports claude-cli, codex-cli, and OpenAI-compatible APIs."""

    def __init__(self, provider: Optional[str] = None):
        self.provider = (provider or Config.LLM_PROVIDER or "claude-cli").lower()
        
        # 支持的提供商列表
        supported_providers = (
            "claude-cli", "codex-cli",
            "openai", "qwen", "doubao", "any"
        )
        
        if self.provider not in supported_providers:
            raise ValueError(
                f"Unsupported LLM provider: {self.provider!r}. "
                f"Use one of: {', '.join(supported_providers)}"
            )
        
        # 初始化 OpenAI 客户端（如果需要）
        self.openai_client = None
        if self.provider in ("openai", "qwen", "doubao", "any"):
            if not OPENAI_AVAILABLE:
                raise ImportError(
                    "OpenAI library is required for API-based providers. "
                    "Install it with: pip install openai"
                )
            self.openai_client = self._create_openai_client()
    
    def _create_openai_client(self) -> 'OpenAI':
        """
        创建 OpenAI 兼容 API 客户端
        
        支持的环境变量:
        - OPENAI_API_KEY: API 密钥
        - OPENAI_BASE_URL: API 基础 URL (可选)
        - OPENAI_MODEL: 默认模型 (可选)
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is required for API-based providers. "
                "Set it in your .env file or export it in your shell."
            )
        
        # 根据不同提供商设置默认配置
        base_url = os.getenv("OPENAI_BASE_URL")
        model = os.getenv("OPENAI_MODEL")
        
        if self.provider == "qwen":
            # 通义千问
            base_url = base_url or "https://dashscope.aliyuncs.com/compatible-mode/v1"
            model = model or "qwen-plus"
        elif self.provider == "doubao":
            # 豆包
            base_url = base_url or "https://ark.cn-beijing.volces.com/api/v3"
            model = model or "doubao-pro-32k"
        elif self.provider == "openai":
            # OpenAI
            base_url = base_url or "https://api.openai.com/v1"
            model = model or "gpt-4o"
        # "any" 使用用户自定义的 base_url 和 model
        
        client_kwargs = {
            "api_key": api_key,
            "base_url": base_url,
        }
        
        logger.info(f"Initializing {self.provider} client with model: {model}")
        return OpenAI(**client_kwargs), model

    def _split_system_message(self, messages: List[Dict[str, str]]):
        """Split system message from conversation messages."""
        system_text = None
        conversation = []

        for msg in messages:
            if msg.get("role") == "system":
                if system_text is None:
                    system_text = msg["content"]
                else:
                    system_text += "\n\n" + msg["content"]
            else:
                conversation.append(msg)

        return system_text, conversation

    def _clean_content(self, content: str) -> str:
        """Remove <think> tags from reasoning models."""
        return re.sub(r'<think>[\s\S]*?</think>', '', content).strip()

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: Optional[Dict] = None
    ) -> str:
        """Send a chat request via CLI or API."""
        if self.provider in ("openai", "qwen", "doubao", "any"):
            return self._chat_openai_api(messages, temperature, max_tokens, response_format)
        elif self.provider == "codex-cli":
            return self._chat_codex_cli(messages, temperature, max_tokens, response_format)
        return self._chat_claude_cli(messages, temperature, max_tokens, response_format)

    def _chat_claude_cli(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        response_format: Optional[Dict] = None
    ) -> str:
        """Chat via Claude Code CLI."""
        system_text, conversation = self._split_system_message(messages)

        prompt_parts = []
        if system_text:
            prompt_parts.append(f"SYSTEM INSTRUCTIONS:\n{system_text}\n")

        if response_format and response_format.get("type") == "json_object":
            prompt_parts.append("IMPORTANT: Respond with valid JSON only. No markdown, no explanation, just pure JSON.\n")

        for msg in conversation:
            role = msg.get("role", "user").upper()
            prompt_parts.append(f"{role}: {msg['content']}")

        prompt = "\n\n".join(prompt_parts)

        try:
            # 尝试获取 claude 的完整路径
            claude_exe = shutil.which("claude") or "claude"
            
            result = subprocess.run(
                [claude_exe, "-p", "--output-format", "json", prompt],
                capture_output=True, text=True, timeout=300,
                cwd=os.getcwd()
            )

            if result.returncode != 0:
                logger.error(f"Claude CLI error: {result.stderr[:200]}")
                raise RuntimeError(f"Claude CLI failed: {result.stderr[:200]}")

            try:
                output = json.loads(result.stdout)
                content = output.get("result", result.stdout)
            except json.JSONDecodeError:
                content = result.stdout.strip()

            return self._clean_content(content)

        except subprocess.TimeoutExpired:
            raise RuntimeError("Claude CLI timed out after 300s")

    def _chat_codex_cli(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        response_format: Optional[Dict] = None
    ) -> str:
        """Chat via Codex CLI."""
        system_text, conversation = self._split_system_message(messages)

        prompt_parts = []
        if system_text:
            prompt_parts.append(f"SYSTEM INSTRUCTIONS:\n{system_text}\n")

        if response_format and response_format.get("type") == "json_object":
            prompt_parts.append("IMPORTANT: Respond with valid JSON only. No markdown, no explanation, just pure JSON.\n")

        for msg in conversation:
            role = msg.get("role", "user").upper()
            prompt_parts.append(f"{role}: {msg['content']}")

        prompt = "\n\n".join(prompt_parts)

        try:
            result = subprocess.run(
                ["codex", "exec", "--skip-git-repo-check"],
                input=prompt,
                capture_output=True, text=True, timeout=180,
                cwd="/tmp"
            )

            if result.returncode != 0:
                logger.error(f"Codex CLI error: {result.stderr[:200]}")
                raise RuntimeError(f"Codex CLI failed: {result.stderr[:200]}")

            raw = result.stdout.strip()
            parts = raw.split("\ncodex\n")
            if len(parts) > 1:
                content = parts[-1].strip()
                lines = content.split("\n")
                clean_lines = []
                for line in lines:
                    if line.strip() == "tokens used":
                        break
                    clean_lines.append(line)
                content = "\n".join(clean_lines).strip()
            else:
                content = raw
            return self._clean_content(content)

        except subprocess.TimeoutExpired:
            raise RuntimeError("Codex CLI timed out after 180s")
    
    def _chat_openai_api(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        response_format: Optional[Dict] = None
    ) -> str:
        """
        Chat via OpenAI-compatible API.
        
        支持 Qwen、豆包、OpenAI 等所有兼容 OpenAI API 的服务。
        """
        if not self.openai_client:
            raise RuntimeError("OpenAI client not initialized")
        
        client, model = self.openai_client
        
        # 构建请求参数
        request_kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        # 如果需要 JSON 格式输出
        if response_format and response_format.get("type") == "json_object":
            request_kwargs["response_format"] = {"type": "json_object"}
        
        try:
            logger.info(f"Calling {self.provider} API with model: {model}")
            response = client.chat.completions.create(**request_kwargs)
            
            content = response.choices[0].message.content
            if not content:
                raise RuntimeError("Empty response from LLM API")
            
            return self._clean_content(content)
        
        except Exception as e:
            logger.error(f"{self.provider} API error: {str(e)}")
            raise RuntimeError(f"LLM API call failed: {str(e)}")

    def chat_json(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """Send a chat request and return parsed JSON."""
        response = self.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"}
        )
        cleaned_response = response.strip()
        cleaned_response = re.sub(r'^```(?:json)?\s*\n?', '', cleaned_response, flags=re.IGNORECASE)
        cleaned_response = re.sub(r'\n?```\s*$', '', cleaned_response)
        cleaned_response = cleaned_response.strip()

        try:
            return json.loads(cleaned_response)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON returned by LLM: {cleaned_response[:500]}")
