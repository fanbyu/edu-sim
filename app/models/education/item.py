"""
Item Model (Test Question)
试题数据模型
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class Item:
    """
    试题实体模型
    
    对应知识图谱中的 Item 节点
    """
    
    item_id: str                             # 唯一标识
    difficulty: float = 0.0                  # IRT b 参数 (难度)
    discrimination: float = 1.0              # IRT a 参数 (区分度)
    guessing_param: float = 0.0              # IRT c 参数 (猜测参数)
    
    # 题目信息
    question_type: str = "multiple_choice"   # 题型
    max_score: float = 1.0                   # 满分
    subject: Optional[str] = None            # 学科
    
    # 关联知识点
    assessed_concepts: List[str] = field(default_factory=list)
    
    # 元数据
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.item_id,
            "label": "Item",
            "properties": {
                "difficulty": self.difficulty,
                "discrimination": self.discrimination,
                "guessing_param": self.guessing_param,
                "question_type": self.question_type,
                "max_score": self.max_score,
                "subject": self.subject,
                "assessed_concepts": self.assessed_concepts
            }
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Item':
        """从字典创建实例"""
        props = data.get('properties', {})
        return cls(
            item_id=data['id'],
            difficulty=props.get('difficulty', 0.0),
            discrimination=props.get('discrimination', 1.0),
            guessing_param=props.get('guessing_param', 0.0),
            question_type=props.get('question_type', 'multiple_choice'),
            max_score=props.get('max_score', 1.0),
            subject=props.get('subject'),
            assessed_concepts=props.get('assessed_concepts', [])
        )
