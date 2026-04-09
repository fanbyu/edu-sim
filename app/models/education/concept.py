"""
Concept Model (Knowledge Point)
知识点数据模型
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class Concept:
    """
    知识点实体模型
    
    对应知识图谱中的 Concept 节点
    """
    
    concept_id: str                          # 唯一标识
    name: str                                # 知识点名称
    
    # 知识结构
    prerequisite_concepts: List[str] = field(default_factory=list)  # 前置知识点
    mastery_threshold: float = 0.7           # 掌握阈值 (0-1)
    
    # 分类信息
    subject: Optional[str] = None            # 学科 (math/english/physics)
    grade_level: Optional[str] = None        # 年级
    
    # 元数据
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.concept_id,
            "label": "Concept",
            "name": self.name,
            "properties": {
                "prerequisite_concepts": self.prerequisite_concepts,
                "mastery_threshold": self.mastery_threshold,
                "subject": self.subject,
                "grade_level": self.grade_level
            }
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Concept':
        """从字典创建实例"""
        props = data.get('properties', {})
        return cls(
            concept_id=data['id'],
            name=data.get('name', ''),
            prerequisite_concepts=props.get('prerequisite_concepts', []),
            mastery_threshold=props.get('mastery_threshold', 0.7),
            subject=props.get('subject'),
            grade_level=props.get('grade_level')
        )
