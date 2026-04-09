"""
Item Parser - 试题解析器
利用 LLM 对上传的试题进行深度特征提取，为预测系统提供输入。
"""

import json
from typing import List, Dict, Any, Optional
from app.utils.llm_client import LLMClient
from app.utils.logger import get_logger

logger = get_logger('edu_sim.item_parser')


class ItemParser:
    """试题特征解析器"""

    def __init__(self, llm_provider: Optional[str] = None):
        self.llm_client = LLMClient(provider=llm_provider)

    def parse_item(self, item_text: str, subject: str = "math") -> Dict[str, Any]:
        """
        解析单道试题，提取 IRT 参数、知识点及认知层级
        
        Args:
            item_text: 试题完整文本（含题干、选项、答案等）
            subject: 学科类型 (math, english, physics...)
            
        Returns:
            包含试题特征的字典
        """
        prompt = f"""
        你是一位资深的{subject}教育测量学专家。请分析以下试题，并以 JSON 格式输出其特征：

        试题内容：
        {item_text}

        请提取以下信息：
        1. difficulty: 预估难度值 (-3.0 到 3.0)，0 表示中等难度。
        2. discrimination: 预估区分度 (0.5 到 2.0)，越高表示越能区分不同水平的学生。
        3. concepts: 考察的知识点列表（字符串数组）。
        4. cognitive_level: 认知层级 (Bloom's Taxonomy: remembering, understanding, applying, analyzing, evaluating, creating)。
        5. psychological_load: 心理负荷评分 (1-10)，考虑阅读量和计算复杂度。

        仅输出纯 JSON，不要包含 Markdown 格式或其他解释。
        """

        try:
            result = self.llm_client.chat_json([{"role": "user", "content": prompt}])
            logger.info(f"试题解析成功: difficulty={result.get('difficulty')}, concepts={result.get('concepts')}")
            return result
        except Exception as e:
            logger.error(f"试题解析失败: {e}")
            # 返回默认值以防解析失败导致流程中断
            return {
                "difficulty": 0.0,
                "discrimination": 1.0,
                "concepts": ["unknown"],
                "cognitive_level": "applying",
                "psychological_load": 5
            }

    def parse_homework_set(self, items: List[str], subject: str = "math") -> List[Dict[str, Any]]:
        """批量解析一套作业中的多道试题"""
        parsed_items = []
        for i, text in enumerate(items):
            logger.info(f"正在解析第 {i+1}/{len(items)} 道试题...")
            features = self.parse_item(text, subject)
            features['original_index'] = i
            parsed_items.append(features)
        return parsed_items
