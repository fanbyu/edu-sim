"""
Student Agent Model
学生智能体模型 - 集成 IRT 参数和心理特征
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
import numpy as np


@dataclass
class StudentAgent:
    """
    学生智能体
    
    结合 IRT 能力值和心理特征,用于教育仿真
    """
    
    # 基本标识
    student_id: str
    name: Optional[str] = None
    
    # IRT 参数 (认知维度)
    cognitive_level: float = 0.0             # θ (能力值, -3 to 3)
    
    # 心理特征 (情感维度)
    learning_style: str = "visual"           # visual/auditory/kinesthetic
    anxiety_threshold: float = 0.5           # 焦虑阈值 (0-1, 越高越易焦虑)
    motivation_level: float = 0.5            # 动机水平 (0-1)
    personality: str = "neutral"             # confident/anxious/diligent
    
    # 学习状态
    mastered_concepts: List[str] = field(default_factory=list)
    recent_performance: List[float] = field(default_factory=list)  # 最近10次得分
    
    # 历史表现记录 (用于学情追踪)
    interaction_history: List[Dict[str, Any]] = field(default_factory=list) 
    # 格式: [{"concept": str, "score": float, "date": str, "item_id": str}]
    
    # 社会属性
    class_name: Optional[str] = None
    
    def predict_response_probability(self, item_difficulty: float, 
                                    discrimination: float = 1.0) -> float:
        """
        基于 IRT 2PL 模型预测答对概率
        
        Args:
            item_difficulty: 题目难度 b
            discrimination: 题目区分度 a
            
        Returns:
            答对概率 (0-1)
        """
        return 1 / (1 + np.exp(-discrimination * (self.cognitive_level - item_difficulty)))
    
    def simulate_response(self, item_difficulty: float, 
                         discrimination: float = 1.0) -> int:
        """
        模拟作答 (基于概率抽样)
        
        Returns:
            1 (正确) 或 0 (错误)
        """
        prob = self.predict_response_probability(item_difficulty, discrimination)
        
        # 焦虑影响: 高焦虑学生在高压下表现下降
        anxiety_factor = max(0.7, 1.0 - self.anxiety_threshold * 0.3)
        adjusted_prob = prob * anxiety_factor
        
        return 1 if np.random.random() < adjusted_prob else 0
    
    def update_after_intervention(self, intervention_type: str):
        """
        干预后更新状态
        
        Args:
            intervention_type: 干预类型
                - 'heuristic': 启发式教学
                - 'direct_instruction': 直接讲授
                - 'psychological_support': 心理辅导
        """
        if intervention_type == "heuristic":
            # 启发式: 提升动机,降低焦虑
            self.anxiety_threshold = max(0.0, self.anxiety_threshold - 0.1)
            self.motivation_level = min(1.0, self.motivation_level + 0.15)
        
        elif intervention_type == "direct_instruction":
            # 直接讲授: 能力提升快,但可能增加焦虑
            self.cognitive_level += 0.2
            self.anxiety_threshold = min(1.0, self.anxiety_threshold + 0.05)
        
        elif intervention_type == "psychological_support":
            # 心理辅导: 显著降低焦虑,提升自信
            self.anxiety_threshold = max(0.0, self.anxiety_threshold - 0.2)
            self.personality = "confident"
    
    def record_interaction(self, item_id: str, concept: str, score: float):
        """
        记录一次学习交互（作答、练习等）
        
        Args:
            item_id: 试题ID
            concept: 考察的知识点
            score: 得分 (0-1)
        """
        record = {
            "item_id": item_id,
            "concept": concept,
            "score": score,
            "date": datetime.now().isoformat()
        }
        self.interaction_history.append(record)
        
        # 同时更新近期表现列表
        self.recent_performance.append(score)
        if len(self.recent_performance) > 10:
            self.recent_performance.pop(0)
            
        # 动态更新心理状态
        if score < 0.4:
            self.anxiety_threshold = min(1.0, self.anxiety_threshold + 0.05)
            self.motivation_level = max(0.0, self.motivation_level - 0.03)
        elif score > 0.8:
            self.anxiety_threshold = max(0.0, self.anxiety_threshold - 0.02)
            self.motivation_level = min(1.0, self.motivation_level + 0.05)

    def get_concept_history(self, concept: str) -> Optional[Dict]:
        """
        获取特定知识点的历史掌握情况
        
        Returns:
            包含 last_score 和 last_interaction_date 的字典
        """
        relevant_records = [r for r in self.interaction_history if r['concept'] == concept]
        if not relevant_records:
            return None
            
        # 取最近的一次记录
        latest = max(relevant_records, key=lambda x: x['date'])
        return {
            "last_score": latest['score'],
            "last_interaction_date": latest['date']
        }
    
    def update_after_assessment(self, score: float, item_difficulty: float):
        """
        评估后更新学习状态
        
        Args:
            score: 得分 (0-1)
            item_difficulty: 题目难度
        """
        # 记录近期表现
        self.recent_performance.append(score)
        if len(self.recent_performance) > 10:
            self.recent_performance.pop(0)
        
        # 简单贝叶斯更新能力值
        avg_recent = np.mean(self.recent_performance)
        learning_rate = 0.05
        self.cognitive_level += learning_rate * (avg_recent - 0.5)
    
    def get_learning_trajectory(self) -> Dict[str, float]:
        """获取学习轨迹统计"""
        if not self.recent_performance:
            return {"avg_score": 0.0, "trend": 0.0}
        
        avg_score = np.mean(self.recent_performance)
        
        # 计算趋势 (最近5次 vs 之前)
        if len(self.recent_performance) >= 5:
            recent_5 = np.mean(self.recent_performance[-5:])
            earlier = np.mean(self.recent_performance[:-5]) if len(self.recent_performance) > 5 else recent_5
            trend = recent_5 - earlier
        else:
            trend = 0.0
        
        return {
            "avg_score": float(avg_score),
            "trend": float(trend),
            "current_ability": self.cognitive_level
        }
    
    def to_dict(self) -> dict:
        """转换为字典 (用于序列化)"""
        return {
            "student_id": self.student_id,
            "name": self.name,
            "cognitive_level": self.cognitive_level,
            "learning_style": self.learning_style,
            "anxiety_threshold": self.anxiety_threshold,
            "motivation_level": self.motivation_level,
            "personality": self.personality,
            "mastered_concepts": self.mastered_concepts,
            "class_name": self.class_name,
            "recent_performance": self.recent_performance
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'StudentAgent':
        """从字典创建实例"""
        return cls(
            student_id=data['student_id'],
            name=data.get('name'),
            cognitive_level=data.get('cognitive_level', 0.0),
            learning_style=data.get('learning_style', 'visual'),
            anxiety_threshold=data.get('anxiety_threshold', 0.5),
            motivation_level=data.get('motivation_level', 0.5),
            personality=data.get('personality', 'neutral'),
            mastered_concepts=data.get('mastered_concepts', []),
            class_name=data.get('class_name'),
            recent_performance=data.get('recent_performance', [])
        )
