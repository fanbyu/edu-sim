"""
OASIS Adapter
OASIS 仿真平台适配器 - 连接教育图谱与 OASIS 多智能体仿真引擎
"""

from typing import List, Dict, Any, Optional
from app.core.agent_modeling import StudentAgent, TeacherAgent


class OasisAdapter:
    """
    OASIS 仿真平台适配器
    
    负责将教育知识图谱中的实体转换为 OASIS Agent，
    并管理仿真环境的初始化和状态同步
    """
    
    def __init__(self, oasis_config: Dict[str, Any] = None):
        """
        初始化 OASIS 适配器
        
        Args:
            oasis_config: OASIS 配置参数
                - num_rounds: 仿真轮数
                - time_step: 时间步长（分钟）
                - parallel: 是否并行执行
        """
        self.config = oasis_config or {
            "num_rounds": 10,
            "time_step": 5,
            "parallel": False
        }
        
        self.students: List[StudentAgent] = []
        self.teachers: List[TeacherAgent] = []
        self.environment_state: Dict[str, Any] = {}
        self.simulation_log: List[Dict[str, Any]] = []
    
    def initialize_from_graph(self, graph_data: Dict[str, Any]):
        """
        从知识图谱数据初始化 OASIS Agents
        
        Args:
            graph_data: 图谱数据字典
                - students: 学生节点列表
                - teachers: 教师节点列表
                - items: 试题节点列表
                - responses: 作答记录列表
        """
        print("🔄 从知识图谱初始化 OASIS Agents...")
        
        # 初始化学生 Agents
        student_nodes = graph_data.get('students', [])
        self._initialize_students(student_nodes)
        print(f"   ✓ 初始化 {len(self.students)} 个学生 Agent")
        
        # 初始化教师 Agents
        teacher_nodes = graph_data.get('teachers', [])
        self._initialize_teachers(teacher_nodes)
        print(f"   ✓ 初始化 {len(self.teachers)} 个教师 Agent")
        
        # 设置环境状态
        self.environment_state = {
            "current_round": 0,
            "total_rounds": self.config['num_rounds'],
            "items": graph_data.get('items', []),
            "responses": graph_data.get('responses', [])
        }
        
        print(f"   ✓ 环境状态就绪")
    
    def _initialize_students(self, student_nodes: List[Dict]):
        """从图谱节点初始化学生 Agents"""
        for node in student_nodes:
            props = node.get('properties', {})
            
            student = StudentAgent(
                student_id=node.get('id', ''),
                name=props.get('name'),
                cognitive_level=props.get('cognitive_level', 0.0),
                anxiety_threshold=props.get('anxiety_threshold', 0.5),
                motivation_level=props.get('motivation_level', 0.5),
                learning_style=props.get('learning_style', 'visual'),
                personality=props.get('personality', 'neutral')
            )
            
            self.students.append(student)
    
    def _initialize_teachers(self, teacher_nodes: List[Dict]):
        """从图谱节点初始化教师 Agents"""
        for node in teacher_nodes:
            props = node.get('properties', {})
            
            teacher = TeacherAgent(
                teacher_id=node.get('id', ''),
                name=props.get('name'),
                teaching_style=props.get('teaching_style', 'heuristic'),
                experience_years=props.get('experience_years', 0),
                feedback_quality=props.get('feedback_quality', 0.8),
                patience_level=props.get('patience_level', 0.7),
                strictness=props.get('strictness', 0.5)
            )
            
            self.teachers.append(teacher)
    
    def run_simulation(self, intervention_strategy: str = None) -> Dict[str, Any]:
        """
        运行完整仿真流程
        
        Args:
            intervention_strategy: 干预策略名称
            
        Returns:
            仿真结果统计
        """
        print(f"\n🚀 开始 OASIS 仿真 (共 {self.config['num_rounds']} 轮)")
        print(f"   干预策略: {intervention_strategy or '无'}")
        
        results = {
            "rounds_completed": 0,
            "student_states": [],
            "interventions_applied": [],
            "performance_metrics": {}
        }
        
        try:
            for round_num in range(1, self.config['num_rounds'] + 1):
                print(f"\n--- 第 {round_num}/{self.config['num_rounds']} 轮 ---")
                
                # 1. 执行教学干预（如果指定）
                if intervention_strategy and round_num == 1:
                    interventions = self._apply_intervention(intervention_strategy)
                    results['interventions_applied'].extend(interventions)
                
                # 2. 学生作答仿真
                round_results = self._simulate_student_responses(round_num)
                
                # 3. 更新学生状态
                self._update_student_states(round_results)
                
                # 4. 记录日志
                self.simulation_log.append({
                    "round": round_num,
                    "results": round_results
                })
                
                results['rounds_completed'] = round_num
            
            # 计算最终指标
            results['performance_metrics'] = self._calculate_metrics()
            
            print(f"\n✅ 仿真完成!")
            print(f"   完成轮数: {results['rounds_completed']}")
            print(f"   应用干预: {len(results['interventions_applied'])} 次")
            
        except Exception as e:
            print(f"❌ 仿真失败: {e}")
            import traceback
            traceback.print_exc()
        
        return results
    
    def _apply_intervention(self, strategy_name: str) -> List[Dict]:
        """
        应用教学干预策略
        
        Args:
            strategy_name: 策略名称
            
        Returns:
            干预记录列表
        """
        interventions = []
        
        # 定义干预策略效果
        strategies = {
            "heuristic": {
                "cognitive_level_delta": 0.3,
                "anxiety_threshold_delta": -0.2,
                "motivation_level_delta": 0.3,
                "description": "启发式教学"
            },
            "scaffolding": {
                "cognitive_level_delta": 0.2,
                "anxiety_threshold_delta": -0.3,
                "motivation_level_delta": 0.2,
                "description": "支架式教学"
            },
            "direct_instruction": {
                "cognitive_level_delta": 0.1,
                "anxiety_threshold_delta": 0.0,
                "motivation_level_delta": 0.1,
                "description": "直接指导"
            },
            "emotional_support": {
                "cognitive_level_delta": 0.0,
                "anxiety_threshold_delta": -0.4,
                "motivation_level_delta": 0.4,
                "description": "情感支持"
            }
        }
        
        if strategy_name not in strategies:
            print(f"⚠️  未知策略: {strategy_name}，使用默认策略")
            strategy_name = "heuristic"
        
        strategy = strategies[strategy_name]
        print(f"   📋 应用策略: {strategy['description']}")
        
        # 选择目标学生（低能力值学生）
        target_students = [
            s for s in self.students 
            if s.cognitive_level < -0.5
        ]
        
        print(f"   🎯 目标学生: {len(target_students)} 人")
        
        for student in target_students:
            # 应用干预效果
            old_theta = student.cognitive_level
            student.cognitive_level += strategy['cognitive_level_delta']
            student.anxiety_threshold = max(0.0, min(1.0, 
                student.anxiety_threshold + strategy['anxiety_threshold_delta']))
            student.motivation_level = max(0.0, min(1.0,
                student.motivation_level + strategy['motivation_level_delta']))
            
            interventions.append({
                "student_id": student.student_id,
                "strategy": strategy_name,
                "old_theta": old_theta,
                "new_theta": student.cognitive_level
            })
        
        return interventions
    
    def _simulate_student_responses(self, round_num: int) -> List[Dict]:
        """
        模拟学生作答
        
        Args:
            round_num: 当前轮次
            
        Returns:
            作答结果列表
        """
        results = []
        items = self.environment_state.get('items', [])
        
        # 如果没有试题，使用默认难度
        if not items:
            default_difficulties = [-0.5, 0.0, 0.5, 1.0, 1.5]
        else:
            default_difficulties = [
                item.get('properties', {}).get('difficulty', 0.0)
                for item in items[:5]  # 取前5道题
            ]
        
        for student in self.students:
            student_result = {
                "student_id": student.student_id,
                "responses": [],
                "total_score": 0
            }
            
            for diff in default_difficulties:
                # 模拟作答
                score = student.simulate_response(diff)
                
                student_result['responses'].append({
                    "difficulty": diff,
                    "score": score
                })
                student_result['total_score'] += score
            
            results.append(student_result)
        
        return results
    
    def _update_student_states(self, round_results: List[Dict]):
        """
        根据作答结果更新学生状态
        
        Args:
            round_results: 本轮作答结果
        """
        for result in round_results:
            student_id = result['student_id']
            total_score = result['total_score']
            num_items = len(result['responses'])
            
            # 找到对应学生
            student = next(
                (s for s in self.students if s.student_id == student_id),
                None
            )
            
            if student:
                # 根据表现调整动机和焦虑
                avg_score = total_score / num_items if num_items > 0 else 0
                
                # 成功体验提升动机
                if avg_score > 0.6:
                    student.motivation_level = min(1.0, student.motivation_level + 0.05)
                elif avg_score < 0.3:
                    student.motivation_level = max(0.0, student.motivation_level - 0.05)
                
                # 连续失败增加焦虑
                if avg_score < 0.2:
                    student.anxiety_threshold = min(1.0, student.anxiety_threshold + 0.05)
    
    def _calculate_metrics(self) -> Dict[str, float]:
        """
        计算仿真性能指标
        
        Returns:
            指标字典
        """
        if not self.students:
            return {}
        
        import numpy as np
        
        thetas = [s.cognitive_level for s in self.students]
        anxieties = [s.anxiety_threshold for s in self.students]
        motivations = [s.motivation_level for s in self.students]
        
        return {
            "avg_cognitive_level": float(np.mean(thetas)),
            "std_cognitive_level": float(np.std(thetas)),
            "avg_anxiety": float(np.mean(anxieties)),
            "avg_motivation": float(np.mean(motivations)),
            "high_performers": sum(1 for t in thetas if t > 1.0),
            "struggling_students": sum(1 for t in thetas if t < -1.0)
        }
    
    def get_simulation_summary(self) -> Dict[str, Any]:
        """
        获取仿真摘要
        
        Returns:
            摘要信息
        """
        return {
            "config": self.config,
            "num_students": len(self.students),
            "num_teachers": len(self.teachers),
            "rounds_completed": len(self.simulation_log),
            "final_metrics": self._calculate_metrics()
        }
    
    def export_results(self, output_path: str = "data/simulation_results.json"):
        """
        导出仿真结果到文件
        
        Args:
            output_path: 输出文件路径
        """
        import json
        from pathlib import Path
        
        results = {
            "summary": self.get_simulation_summary(),
            "log": self.simulation_log,
            "final_student_states": [s.to_dict() for s in self.students]
        }
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"💾 结果已保存到: {output_path}")
