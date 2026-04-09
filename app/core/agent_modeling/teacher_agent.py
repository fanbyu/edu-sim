"""
Teacher Agent Model
教师智能体模型
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class TeacherAgent:
    """
    教师智能体
    
    具有不同教学风格,能够对学生施加影响
    """
    
    # 基本标识
    teacher_id: str
    name: Optional[str] = None
    
    # 教学特征
    teaching_style: str = "heuristic"        # heuristic/direct/facilitator
    experience_years: int = 0
    feedback_quality: float = 0.8            # 反馈质量 (0-1)
    patience_level: float = 0.7              # 耐心程度 (0-1)
    strictness: float = 0.5                  # 严格程度 (0-1)
    
    # 关联信息
    classes_taught: List[str] = field(default_factory=list)
    subject_specialties: List[str] = field(default_factory=list)
    
    def select_intervention(self, anxiety: float, motivation: float, 
                           performance: float) -> str:
        """
        根据学生状态选择最佳干预策略
        
        Args:
            anxiety: 学生焦虑水平 (0-1)
            motivation: 学生动机水平 (0-1)
            performance: 学生表现 (0-1)
            
        Returns:
            推荐的干预类型
        """
        # 高焦虑 + 低动机 → 情感支持
        if anxiety > 0.6 and motivation < 0.4:
            return "emotional_support"
        
        # 低表现 + 中等焦虑 → 支架式教学
        elif performance < 0.5 and anxiety < 0.6:
            return "scaffolding"
        
        # 高动机 + 高表现 → 启发式挑战
        elif motivation > 0.7 and performance > 0.6:
            return "heuristic"
        
        # 默认 → 直接指导
        else:
            return "direct_instruction"
    
    def apply_teaching_intervention(self, students: List['StudentAgent'], 
                                   intervention_type: str = None):
        """
        对学生群体施加教学干预
        
        Args:
            students: 学生列表
            intervention_type: 干预类型 (默认使用教师的教学风格)
        """
        if intervention_type is None:
            intervention_type = self.teaching_style
        
        for student in students:
            student.update_after_intervention(intervention_type)
    
    def generate_feedback(self, student: 'StudentAgent', 
                         score: float) -> Dict[str, any]:
        """
        根据学生表现生成个性化反馈
        
        Args:
            student: 学生对象
            score: 得分 (0-1)
            
        Returns:
            反馈信息
        """
        feedback = {
            "score": score,
            "quality": self.feedback_quality,
            "message": ""
        }
        
        if score >= 0.8:
            feedback["message"] = "Excellent work! Keep it up."
        elif score >= 0.6:
            feedback["message"] = "Good effort. Focus on the challenging parts."
        else:
            if self.teaching_style == "heuristic":
                feedback["message"] = "Let's explore this together. What part confused you?"
            elif self.teaching_style == "direct":
                feedback["message"] = "Review the key concepts and try again."
            else:  # facilitator
                feedback["message"] = "I'm here to help. Let's identify the obstacles."
        
        return feedback
    
    def assess_class_performance(self, students: List['StudentAgent']) -> Dict[str, float]:
        """
        评估班级整体表现
        
        Args:
            students: 班级学生列表
            
        Returns:
            统计信息
        """
        if not students:
            return {}
        
        abilities = [s.cognitive_level for s in students]
        anxieties = [s.anxiety_threshold for s in students]
        motivations = [s.motivation_level for s in students]
        
        import numpy as np
        
        return {
            "avg_ability": float(np.mean(abilities)),
            "std_ability": float(np.std(abilities)),
            "avg_anxiety": float(np.mean(anxieties)),
            "avg_motivation": float(np.mean(motivations)),
            "student_count": len(students)
        }
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "teacher_id": self.teacher_id,
            "name": self.name,
            "teaching_style": self.teaching_style,
            "experience_years": self.experience_years,
            "feedback_quality": self.feedback_quality,
            "patience_level": self.patience_level,
            "strictness": self.strictness,
            "classes_taught": self.classes_taught,
            "subject_specialties": self.subject_specialties
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TeacherAgent':
        """从字典创建实例"""
        return cls(
            teacher_id=data['teacher_id'],
            name=data.get('name'),
            teaching_style=data.get('teaching_style', 'heuristic'),
            experience_years=data.get('experience_years', 0),
            feedback_quality=data.get('feedback_quality', 0.8),
            patience_level=data.get('patience_level', 0.7),
            strictness=data.get('strictness', 0.5),
            classes_taught=data.get('classes_taught', []),
            subject_specialties=data.get('subject_specialties', [])
        )
