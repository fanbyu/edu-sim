"""
Student Model
学生数据模型
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class Student:
    """
    学生实体模型
    
    对应知识图谱中的 Student 节点
    """
    
    student_id: str                          # 唯一标识 (准考证号)
    cognitive_level: float = 0.0             # IRT θ 参数 (认知能力)
    learning_style: str = "visual"           # 学习风格
    anxiety_threshold: float = 0.5           # 焦虑阈值 (0-1)
    motivation_level: float = 0.5            # 动机水平 (0-1)
    personality: str = "neutral"             # 性格特征
    
    # 关联信息
    class_name: Optional[str] = None         # 所属班级
    mastered_concepts: List[str] = field(default_factory=list)  # 已掌握知识点
    
    # 元数据
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        """转换为字典 (用于图谱存储)"""
        return {
            "id": self.student_id,
            "label": "Student",
            "properties": {
                "cognitive_level": self.cognitive_level,
                "learning_style": self.learning_style,
                "anxiety_threshold": self.anxiety_threshold,
                "motivation_level": self.motivation_level,
                "personality": self.personality,
                "class_name": self.class_name,
                "mastered_concepts": self.mastered_concepts
            }
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Student':
        """从字典创建实例"""
        props = data.get('properties', {})
        return cls(
            student_id=data['id'],
            cognitive_level=props.get('cognitive_level', 0.0),
            learning_style=props.get('learning_style', 'visual'),
            anxiety_threshold=props.get('anxiety_threshold', 0.5),
            motivation_level=props.get('motivation_level', 0.5),
            personality=props.get('personality', 'neutral'),
            class_name=props.get('class_name'),
            mastered_concepts=props.get('mastered_concepts', [])
        )
