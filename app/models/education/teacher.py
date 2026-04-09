"""
Teacher Model
教师数据模型
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class Teacher:
    """
    教师实体模型
    
    对应知识图谱中的 Teacher 节点
    """
    
    teacher_id: str                          # 唯一标识
    teaching_style: str = "heuristic"        # 教学风格
    experience_years: int = 0                # 教龄
    feedback_quality: float = 0.8            # 反馈质量 (0-1)
    patience_level: float = 0.7              # 耐心程度 (0-1)
    strictness: float = 0.5                  # 严格程度 (0-1)
    
    # 关联信息
    classes_taught: list = field(default_factory=list)  # 教授的班级
    
    # 元数据
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.teacher_id,
            "label": "Teacher",
            "properties": {
                "teaching_style": self.teaching_style,
                "experience_years": self.experience_years,
                "feedback_quality": self.feedback_quality,
                "patience_level": self.patience_level,
                "strictness": self.strictness,
                "classes_taught": self.classes_taught
            }
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Teacher':
        """从字典创建实例"""
        props = data.get('properties', {})
        return cls(
            teacher_id=data['id'],
            teaching_style=props.get('teaching_style', 'heuristic'),
            experience_years=props.get('experience_years', 0),
            feedback_quality=props.get('feedback_quality', 0.8),
            patience_level=props.get('patience_level', 0.7),
            strictness=props.get('strictness', 0.5),
            classes_taught=props.get('classes_taught', [])
        )
