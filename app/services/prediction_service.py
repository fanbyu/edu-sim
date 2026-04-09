"""
Prediction Service
预测服务 - 基于 IRT 模型和学生状态进行学习表现预测
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from app.core.agent_modeling import IRTEngine, StudentAgent
from app.services.graph_service import GraphService


class PredictionService:
    """
    学习表现预测服务
    
    基于学生当前能力、心理状态和试题特征，
    预测未来学习表现和干预效果
    """
    
    def __init__(self, graph_service: GraphService,
                 irt_engine: IRTEngine = None):
        """
        初始化预测服务
        
        Args:
            graph_service: 图谱服务实例
            irt_engine: IRT 引擎实例
        """
        self.graph_service = graph_service
        self.irt_engine = irt_engine or IRTEngine(model_type="2PL")
    
    def predict_student_performance(self, student_id: str,
                                   item_ids: List[str]) -> Dict[str, Any]:
        """
        预测学生在指定试题上的表现
        
        Args:
            student_id: 学生ID
            item_ids: 试题ID列表
            
        Returns:
            预测结果
        """
        # 获取学生画像
        profile = self.graph_service.get_student_profile(student_id)
        if not profile:
            return {"error": f"学生 {student_id} 不存在"}
        
        # 获取学生当前状态
        attributes = profile.get('attributes', {})
        theta = attributes.get('cognitive_level', 0.0)
        anxiety = attributes.get('anxiety_threshold', 0.5)
        motivation = attributes.get('motivation_level', 0.5)
        
        predictions = []
        
        for item_id in item_ids:
            # 获取试题信息
            item_node = self.graph_service.engine.get_node(item_id)
            if not item_node:
                continue
            
            item_props = item_node.get('properties', {})
            difficulty = item_props.get('difficulty', 0.0)
            discrimination = item_props.get('discrimination', 1.0)
            
            # 计算基础答对概率（IRT）
            base_prob = self.irt_engine.predict_probability(
                theta, difficulty, discrimination
            )
            
            # 考虑心理因素调整
            anxiety_factor = max(0.7, 1.0 - anxiety * 0.3)
            motivation_factor = 0.8 + motivation * 0.2
            
            adjusted_prob = base_prob * anxiety_factor * motivation_factor
            
            predictions.append({
                "item_id": item_id,
                "difficulty": difficulty,
                "base_probability": round(float(base_prob), 4),
                "adjusted_probability": round(float(adjusted_prob), 4),
                "predicted_score": 1 if np.random.random() < adjusted_prob else 0
            })
        
        return {
            "student_id": student_id,
            "current_theta": theta,
            "predictions": predictions,
            "avg_predicted_score": round(
                np.mean([p['adjusted_probability'] for p in predictions]), 4
            ) if predictions else 0
        }
    
    def predict_intervention_effect(self, student_id: str,
                                   intervention_type: str,
                                   duration_rounds: int = 3) -> Dict[str, Any]:
        """
        预测干预效果
        
        Args:
            student_id: 学生ID
            intervention_type: 干预类型
            duration_rounds: 干预持续轮数
            
        Returns:
            预测的干预效果
        """
        # 获取学生当前状态
        profile = self.graph_service.get_student_profile(student_id)
        if not profile:
            return {"error": f"学生 {student_id} 不存在"}
        
        attributes = profile.get('attributes', {})
        current_theta = attributes.get('cognitive_level', 0.0)
        current_anxiety = attributes.get('anxiety_threshold', 0.5)
        current_motivation = attributes.get('motivation_level', 0.5)
        
        # 定义不同干预的效果参数
        intervention_effects = {
            "heuristic": {
                "theta_gain_per_round": 0.1,
                "anxiety_reduction": 0.07,
                "motivation_boost": 0.1,
                "description": "启发式教学"
            },
            "scaffolding": {
                "theta_gain_per_round": 0.07,
                "anxiety_reduction": 0.1,
                "motivation_boost": 0.07,
                "description": "支架式教学"
            },
            "direct_instruction": {
                "theta_gain_per_round": 0.05,
                "anxiety_reduction": 0.0,
                "motivation_boost": 0.03,
                "description": "直接指导"
            },
            "emotional_support": {
                "theta_gain_per_round": 0.0,
                "anxiety_reduction": 0.13,
                "motivation_boost": 0.13,
                "description": "情感支持"
            }
        }
        
        if intervention_type not in intervention_effects:
            return {"error": f"未知干预类型: {intervention_type}"}
        
        effect_params = intervention_effects[intervention_type]
        
        # 模拟多轮干预效果
        trajectory = []
        predicted_theta = current_theta
        predicted_anxiety = current_anxiety
        predicted_motivation = current_motivation
        
        for round_num in range(1, duration_rounds + 1):
            # 应用效果
            predicted_theta += effect_params['theta_gain_per_round']
            predicted_anxiety = max(0.0, predicted_anxiety - effect_params['anxiety_reduction'])
            predicted_motivation = min(1.0, predicted_motivation + effect_params['motivation_boost'])
            
            trajectory.append({
                "round": round_num,
                "theta": round(predicted_theta, 4),
                "anxiety": round(predicted_anxiety, 4),
                "motivation": round(predicted_motivation, 4)
            })
        
        # 计算总体改善
        theta_improvement = predicted_theta - current_theta
        anxiety_reduction = current_anxiety - predicted_anxiety
        motivation_improvement = predicted_motivation - current_motivation
        
        return {
            "student_id": student_id,
            "intervention_type": intervention_type,
            "intervention_description": effect_params['description'],
            "duration_rounds": duration_rounds,
            "initial_state": {
                "theta": current_theta,
                "anxiety": current_anxiety,
                "motivation": current_motivation
            },
            "final_state": {
                "theta": round(predicted_theta, 4),
                "anxiety": round(predicted_anxiety, 4),
                "motivation": round(predicted_motivation, 4)
            },
            "improvements": {
                "theta_gain": round(theta_improvement, 4),
                "anxiety_reduction": round(anxiety_reduction, 4),
                "motivation_gain": round(motivation_improvement, 4)
            },
            "trajectory": trajectory
        }
    
    def recommend_optimal_intervention(self, student_id: str,
                                      available_strategies: List[str] = None) -> Dict[str, Any]:
        """
        推荐最优干预策略
        
        Args:
            student_id: 学生ID
            available_strategies: 可用策略列表
            
        Returns:
            推荐结果
        """
        if available_strategies is None:
            available_strategies = [
                "heuristic", "scaffolding", 
                "direct_instruction", "emotional_support"
            ]
        
        # 获取学生状态
        profile = self.graph_service.get_student_profile(student_id)
        if not profile:
            return {"error": f"学生 {student_id} 不存在"}
        
        attributes = profile.get('attributes', {})
        theta = attributes.get('cognitive_level', 0.0)
        anxiety = attributes.get('anxiety_threshold', 0.5)
        motivation = attributes.get('motivation_level', 0.5)
        
        # 评估每种策略
        strategy_scores = []
        
        for strategy in available_strategies:
            # 预测效果
            prediction = self.predict_intervention_effect(student_id, strategy)
            
            if "error" in prediction:
                continue
            
            improvements = prediction['improvements']
            
            # 计算综合得分（加权）
            # 根据学生当前状态调整权重
            if theta < -1.0:
                # 低能力学生：能力提升最重要
                weight_theta = 0.5
                weight_anxiety = 0.2
                weight_motivation = 0.3
            elif anxiety > 0.7:
                # 高焦虑学生：降低焦虑最重要
                weight_theta = 0.3
                weight_anxiety = 0.5
                weight_motivation = 0.2
            elif motivation < 0.3:
                # 低动机学生：提升动机最重要
                weight_theta = 0.3
                weight_anxiety = 0.2
                weight_motivation = 0.5
            else:
                # 均衡权重
                weight_theta = 0.4
                weight_anxiety = 0.3
                weight_motivation = 0.3
            
            score = (
                improvements['theta_gain'] * weight_theta +
                improvements['anxiety_reduction'] * weight_anxiety +
                improvements['motivation_gain'] * weight_motivation
            )
            
            strategy_scores.append({
                "strategy": strategy,
                "score": round(score, 4),
                "prediction": prediction
            })
        
        # 排序
        strategy_scores.sort(key=lambda x: x['score'], reverse=True)
        
        return {
            "student_id": student_id,
            "current_state": {
                "theta": theta,
                "anxiety": anxiety,
                "motivation": motivation
            },
            "recommendations": strategy_scores,
            "best_strategy": strategy_scores[0]['strategy'] if strategy_scores else None
        }
    
    def predict_class_performance(self, class_name: str,
                                 item_ids: List[str]) -> Dict[str, Any]:
        """
        预测班级整体表现
        
        Args:
            class_name: 班级名称
            item_ids: 试题ID列表
            
        Returns:
            班级预测结果
        """
        # 获取班级统计
        class_stats = self.graph_service.get_class_statistics(class_name)
        
        if "error" in class_stats:
            return class_stats
        
        # 获取班级学生列表（简化实现）
        students_in_class = []
        avg_theta = class_stats.get('avg_cognitive_level', 0.0)
        
        # 基于平均能力预测班级表现
        class_predictions = []
        
        for item_id in item_ids:
            item_node = self.graph_service.engine.get_node(item_id)
            if not item_node:
                continue
            
            difficulty = item_node.get('properties', {}).get('difficulty', 0.0)
            
            # 使用班级平均能力预测
            prob = self.irt_engine.predict_probability(avg_theta, difficulty)
            
            class_predictions.append({
                "item_id": item_id,
                "difficulty": difficulty,
                "predicted_correct_rate": round(float(prob), 4),
                "predicted_avg_score": round(float(prob), 4)
            })
        
        return {
            "class_name": class_name,
            "student_count": class_stats.get('student_count', 0),
            "avg_cognitive_level": avg_theta,
            "item_predictions": class_predictions,
            "overall_predicted_performance": round(
                np.mean([p['predicted_avg_score'] for p in class_predictions]), 4
            ) if class_predictions else 0
        }
    
    def simulate_learning_trajectory(self, student_id: str,
                                    num_rounds: int = 10,
                                    learning_rate: float = 0.05) -> Dict[str, Any]:
        """
        模拟学生学习轨迹
        
        Args:
            student_id: 学生ID
            num_rounds: 模拟轮数
            learning_rate: 学习率
            
        Returns:
            学习轨迹数据
        """
        # 获取学生初始状态
        profile = self.graph_service.get_student_profile(student_id)
        if not profile:
            return {"error": f"学生 {student_id} 不存在"}
        
        attributes = profile.get('attributes', {})
        theta = attributes.get('cognitive_level', 0.0)
        
        trajectory = []
        current_theta = theta
        
        for round_num in range(1, num_rounds + 1):
            # 模拟学习进步（带随机扰动）
            progress = learning_rate + np.random.normal(0, 0.02)
            current_theta += progress
            
            trajectory.append({
                "round": round_num,
                "theta": round(current_theta, 4),
                "progress": round(progress, 4)
            })
        
        return {
            "student_id": student_id,
            "initial_theta": theta,
            "final_theta": round(current_theta, 4),
            "total_progress": round(current_theta - theta, 4),
            "trajectory": trajectory
        }
