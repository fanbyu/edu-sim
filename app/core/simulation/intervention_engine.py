"""
Intervention Engine
教学干预执行引擎 - 管理和执行多种教学干预策略
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum


class InterventionType(Enum):
    """干预类型枚举"""
    HEURISTIC = "heuristic"              # 启发式教学
    SCAFFOLDING = "scaffolding"          # 支架式教学
    DIRECT_INSTRUCTION = "direct_instruction"  # 直接指导
    EMOTIONAL_SUPPORT = "emotional_support"    # 情感支持
    PEER_LEARNING = "peer_learning"      # 同伴学习
    ADAPTIVE_PRACTICE = "adaptive_practice"  # 自适应练习


@dataclass
class InterventionEffect:
    """干预效果定义"""
    cognitive_level_delta: float = 0.0   # 认知能力变化
    anxiety_threshold_delta: float = 0.0 # 焦虑阈值变化
    motivation_level_delta: float = 0.0  # 动机水平变化
    duration_rounds: int = 1             # 持续轮数
    decay_rate: float = 0.1              # 衰减率
    
    def apply_decay(self):
        """应用效果衰减"""
        self.cognitive_level_delta *= (1 - self.decay_rate)
        self.anxiety_threshold_delta *= (1 - self.decay_rate)
        self.motivation_level_delta *= (1 - self.decay_rate)
        self.duration_rounds -= 1


@dataclass
class InterventionRecord:
    """干预记录"""
    student_id: str
    intervention_type: InterventionType
    timestamp: int  # 仿真轮次
    effects: InterventionEffect
    outcome: Optional[Dict[str, float]] = None  # 实际效果


class InterventionEngine:
    """
    教学干预执行引擎
    
    负责根据学生状态智能选择和执行干预策略，
    并追踪干预效果
    """
    
    def __init__(self):
        """初始化干预引擎"""
        self.intervention_strategies = self._initialize_strategies()
        self.active_interventions: Dict[str, List[InterventionRecord]] = {}
        self.intervention_history: List[InterventionRecord] = []
    
    def _initialize_strategies(self) -> Dict[InterventionType, Dict[str, Any]]:
        """
        初始化干预策略库
        
        Returns:
            策略配置字典
        """
        return {
            InterventionType.HEURISTIC: {
                "name": "启发式教学",
                "description": "通过引导性问题促进学生自主探索",
                "effect": InterventionEffect(
                    cognitive_level_delta=0.3,
                    anxiety_threshold_delta=-0.2,
                    motivation_level_delta=0.3,
                    duration_rounds=3,
                    decay_rate=0.15
                ),
                "target_condition": lambda s: s.cognitive_level < 0 and s.motivation_level > 0.5,
                "cost": 0.7  # 资源消耗
            },
            
            InterventionType.SCAFFOLDING: {
                "name": "支架式教学",
                "description": "提供结构化支持，逐步撤除帮助",
                "effect": InterventionEffect(
                    cognitive_level_delta=0.2,
                    anxiety_threshold_delta=-0.3,
                    motivation_level_delta=0.2,
                    duration_rounds=4,
                    decay_rate=0.1
                ),
                "target_condition": lambda s: s.anxiety_threshold > 0.6 and s.cognitive_level < 0,
                "cost": 0.8
            },
            
            InterventionType.DIRECT_INSTRUCTION: {
                "name": "直接指导",
                "description": "明确讲解知识点和解题方法",
                "effect": InterventionEffect(
                    cognitive_level_delta=0.15,
                    anxiety_threshold_delta=0.0,
                    motivation_level_delta=0.1,
                    duration_rounds=2,
                    decay_rate=0.2
                ),
                "target_condition": lambda s: s.cognitive_level < -1.0,
                "cost": 0.5
            },
            
            InterventionType.EMOTIONAL_SUPPORT: {
                "name": "情感支持",
                "description": "提供心理疏导和鼓励",
                "effect": InterventionEffect(
                    cognitive_level_delta=0.0,
                    anxiety_threshold_delta=-0.4,
                    motivation_level_delta=0.4,
                    duration_rounds=2,
                    decay_rate=0.25
                ),
                "target_condition": lambda s: s.anxiety_threshold > 0.7 or s.motivation_level < 0.3,
                "cost": 0.4
            },
            
            InterventionType.PEER_LEARNING: {
                "name": "同伴学习",
                "description": "组织小组合作学习",
                "effect": InterventionEffect(
                    cognitive_level_delta=0.25,
                    anxiety_threshold_delta=-0.1,
                    motivation_level_delta=0.35,
                    duration_rounds=3,
                    decay_rate=0.12
                ),
                "target_condition": lambda s: 0.3 < s.motivation_level < 0.7,
                "cost": 0.6
            },
            
            InterventionType.ADAPTIVE_PRACTICE: {
                "name": "自适应练习",
                "description": "根据学生水平推送个性化习题",
                "effect": InterventionEffect(
                    cognitive_level_delta=0.35,
                    anxiety_threshold_delta=-0.15,
                    motivation_level_delta=0.2,
                    duration_rounds=5,
                    decay_rate=0.08
                ),
                "target_condition": lambda s: True,  # 适用于所有学生
                "cost": 0.9
            }
        }
    
    def select_intervention(self, student_state: Dict[str, float], 
                           budget: float = 1.0) -> Optional[InterventionType]:
        """
        根据学生状态智能选择干预策略
        
        Args:
            student_state: 学生状态字典
                - cognitive_level: 认知能力
                - anxiety_threshold: 焦虑阈值
                - motivation_level: 动机水平
            budget: 可用资源预算
            
        Returns:
            推荐的干预类型，或 None（无需干预）
        """
        # 检查是否有正在进行的干预
        student_id = student_state.get('student_id', '')
        if student_id in self.active_interventions:
            active = self.active_interventions[student_id]
            if active and active[-1].effects.duration_rounds > 0:
                return None  # 已有干预在进行中
        
        # 评估所有适用策略
        candidates = []
        
        for strategy_type, config in self.intervention_strategies.items():
            # 检查是否符合目标条件
            if config['target_condition'](type('Student', (), student_state)()):
                # 检查预算
                if config['cost'] <= budget:
                    # 计算优先级分数
                    priority = self._calculate_priority(student_state, config)
                    candidates.append((strategy_type, priority, config['cost']))
        
        if not candidates:
            return None
        
        # 选择优先级最高的策略
        candidates.sort(key=lambda x: x[1], reverse=True)
        best_strategy = candidates[0][0]
        
        return best_strategy
    
    def apply_intervention(self, student_id: str, 
                          intervention_type: InterventionType,
                          current_round: int) -> InterventionRecord:
        """
        执行干预
        
        Args:
            student_id: 学生ID
            intervention_type: 干预类型
            current_round: 当前仿真轮次
            
        Returns:
            干预记录
        """
        if intervention_type not in self.intervention_strategies:
            raise ValueError(f"未知干预类型: {intervention_type}")
        
        # 创建干预记录
        effect = InterventionEffect(
            **vars(self.intervention_strategies[intervention_type]['effect'])
        )
        
        record = InterventionRecord(
            student_id=student_id,
            intervention_type=intervention_type,
            timestamp=current_round,
            effects=effect
        )
        
        # 记录到历史
        self.intervention_history.append(record)
        
        # 添加到活跃干预
        if student_id not in self.active_interventions:
            self.active_interventions[student_id] = []
        self.active_interventions[student_id].append(record)
        
        return record
    
    def get_intervention_effects(self, student_id: str) -> Dict[str, float]:
        """
        获取学生当前的累积干预效果
        
        Args:
            student_id: 学生ID
            
        Returns:
            累积效果字典
        """
        total_effect = {
            'cognitive_level_delta': 0.0,
            'anxiety_threshold_delta': 0.0,
            'motivation_level_delta': 0.0
        }
        
        if student_id in self.active_interventions:
            for record in self.active_interventions[student_id]:
                if record.effects.duration_rounds > 0:
                    total_effect['cognitive_level_delta'] += record.effects.cognitive_level_delta
                    total_effect['anxiety_threshold_delta'] += record.effects.anxiety_threshold_delta
                    total_effect['motivation_level_delta'] += record.effects.motivation_level_delta
        
        return total_effect
    
    def update_active_interventions(self):
        """更新所有活跃干预（应用衰减）"""
        for student_id in list(self.active_interventions.keys()):
            records = self.active_interventions[student_id]
            
            # 移除已结束的干预
            active_records = [r for r in records if r.effects.duration_rounds > 0]
            
            # 对仍在进行的干预应用衰减
            for record in active_records:
                record.effects.apply_decay()
            
            self.active_interventions[student_id] = active_records
            
            # 如果没有活跃干预，删除该学生的记录
            if not active_records:
                del self.active_interventions[student_id]
    
    def _calculate_priority(self, student_state: Dict[str, float], 
                           strategy_config: Dict[str, Any]) -> float:
        """
        计算干预策略的优先级分数
        
        Args:
            student_state: 学生状态
            strategy_config: 策略配置
            
        Returns:
            优先级分数（越高越优先）
        """
        # 基础优先级：根据学生需求的紧急程度
        urgency = 0.0
        
        # 低能力值 → 高优先级
        if student_state.get('cognitive_level', 0) < -1.0:
            urgency += 0.4
        elif student_state.get('cognitive_level', 0) < 0:
            urgency += 0.2
        
        # 高焦虑 → 高优先级
        if student_state.get('anxiety_threshold', 0.5) > 0.7:
            urgency += 0.3
        elif student_state.get('anxiety_threshold', 0.5) > 0.5:
            urgency += 0.15
        
        # 低动机 → 高优先级
        if student_state.get('motivation_level', 0.5) < 0.3:
            urgency += 0.3
        elif student_state.get('motivation_level', 0.5) < 0.5:
            urgency += 0.15
        
        # 策略匹配度
        match_score = 1.0 if strategy_config['target_condition'](
            type('Student', (), student_state)()
        ) else 0.0
        
        # 综合评分
        priority = urgency * 0.6 + match_score * 0.4
        
        return priority
    
    def get_intervention_statistics(self) -> Dict[str, Any]:
        """
        获取干预统计信息
        
        Returns:
            统计信息字典
        """
        stats = {
            "total_interventions": len(self.intervention_history),
            "active_interventions": sum(
                len(records) for records in self.active_interventions.values()
            ),
            "by_type": {},
            "avg_effectiveness": {}
        }
        
        # 按类型统计
        for record in self.intervention_history:
            type_name = record.intervention_type.value
            if type_name not in stats['by_type']:
                stats['by_type'][type_name] = 0
            stats['by_type'][type_name] += 1
        
        return stats
    
    def export_intervention_log(self, output_path: str = "data/intervention_log.json"):
        """
        导出干预日志
        
        Args:
            output_path: 输出文件路径
        """
        import json
        from pathlib import Path
        
        log_data = {
            "statistics": self.get_intervention_statistics(),
            "history": [
                {
                    "student_id": r.student_id,
                    "intervention_type": r.intervention_type.value,
                    "timestamp": r.timestamp,
                    "effects": vars(r.effects),
                    "outcome": r.outcome
                }
                for r in self.intervention_history
            ]
        }
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 干预日志已保存到: {output_path}")
