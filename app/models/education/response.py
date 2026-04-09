"""
Response Model (Student Answer Record)
作答记录数据模型
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Response:
    """
    作答记录模型
    
    对应知识图谱中 Student 和 Item 之间的 ATTEMPTED 边
    """
    
    student_id: str                          # 学生ID
    item_id: str                             # 题目ID
    score: float                             # 得分
    time_spent: float = 0.0                  # 用时(秒)
    
    # 时间戳
    attempt_timestamp: str = field(
        default_factory=lambda: datetime.now().isoformat()
    )
    
    def to_dict(self) -> dict:
        """转换为字典 (用于图谱边存储)"""
        return {
            "source_id": self.student_id,
            "target_id": self.item_id,
            "relation": "ATTEMPTED",
            "properties": {
                "score": self.score,
                "time_spent": self.time_spent,
                "attempt_timestamp": self.attempt_timestamp
            }
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Response':
        """从字典创建实例"""
        props = data.get('properties', {})
        return cls(
            student_id=data['source_id'],
            item_id=data['target_id'],
            score=props.get('score', 0.0),
            time_spent=props.get('time_spent', 0.0),
            attempt_timestamp=props.get('attempt_timestamp', 
                                       datetime.now().isoformat())
        )
