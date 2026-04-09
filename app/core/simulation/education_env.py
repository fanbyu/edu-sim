"""
Education Environment
虚拟课堂环境 - 定义教学与作答动作的仿真环境
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class ActionType(Enum):
    """动作类型枚举"""
    TEACH = "teach"                    # 教师授课
    ASSIGN_HOMEWORK = "assign_homework" # 布置作业
    STUDENT_ANSWER = "student_answer"   # 学生作答
    PROVIDE_FEEDBACK = "provide_feedback" # 提供反馈
    PEER_DISCUSSION = "peer_discussion"   # 同伴讨论
    SELF_STUDY = "self_study"          # 自主学习


@dataclass
class Action:
    """仿真动作"""
    action_type: ActionType
    actor_id: str                      # 执行者ID (教师或学生)
    target_ids: List[str]              # 目标ID列表
    parameters: Dict[str, Any] = field(default_factory=dict)
    timestamp: int = 0                 # 时间戳（轮次）


@dataclass
class EnvironmentState:
    """环境状态"""
    current_round: int = 0
    total_rounds: int = 10
    classroom_atmosphere: float = 0.5  # 课堂氛围 (0-1)
    average_engagement: float = 0.5    # 平均参与度 (0-1)
    teaching_progress: float = 0.0     # 教学进度 (0-1)


class EducationEnv:
    """
    虚拟课堂环境
    
    定义教学交互的动作空间和状态转移规则，
    支持多智能体在课堂环境中的交互仿真
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化课堂环境
        
        Args:
            config: 环境配置
                - num_rounds: 总轮数
                - class_size: 班级规模
                - difficulty_curve: 难度曲线类型
        """
        self.config = config or {
            "num_rounds": 10,
            "class_size": 30,
            "difficulty_curve": "linear"  # linear, exponential, adaptive
        }
        
        self.state = EnvironmentState(
            total_rounds=self.config['num_rounds']
        )
        
        self.action_history: List[Action] = []
        self.students_state: Dict[str, Dict[str, float]] = {}
        self.teacher_state: Dict[str, Any] = {}
        self.current_items: List[Dict[str, Any]] = []
    
    def reset(self, students: List[Dict], teacher: Dict = None, 
              items: List[Dict] = None):
        """
        重置环境状态
        
        Args:
            students: 学生列表
            teacher: 教师信息
            items: 试题列表
        """
        self.state = EnvironmentState(
            total_rounds=self.config['num_rounds']
        )
        self.action_history = []
        
        # 初始化学生状态
        for student in students:
            sid = student.get('student_id', student.get('id', ''))
            self.students_state[sid] = {
                'cognitive_level': student.get('cognitive_level', 0.0),
                'anxiety_threshold': student.get('anxiety_threshold', 0.5),
                'motivation_level': student.get('motivation_level', 0.5),
                'engagement': 0.5,
                'fatigue': 0.0
            }
        
        # 初始化教师状态
        if teacher:
            self.teacher_state = {
                'teacher_id': teacher.get('teacher_id', teacher.get('id', '')),
                'teaching_style': teacher.get('teaching_style', 'heuristic'),
                'energy': 1.0,
                'patience': teacher.get('patience_level', 0.7)
            }
        
        # 加载试题
        if items:
            self.current_items = items
        
        print(f"🔄 环境已重置: {len(self.students_state)} 名学生, "
              f"{len(self.current_items)} 道试题")
    
    def step(self, action: Action) -> Dict[str, Any]:
        """
        执行一个动作并返回环境反馈
        
        Args:
            action: 要执行的动作
            
        Returns:
            环境反馈
                - reward: 即时奖励
                - next_state: 下一状态
                - done: 是否结束
                - info: 附加信息
        """
        # 记录动作
        action.timestamp = self.state.current_round
        self.action_history.append(action)
        
        # 根据动作类型执行不同的逻辑
        if action.action_type == ActionType.TEACH:
            feedback = self._execute_teach(action)
        elif action.action_type == ActionType.ASSIGN_HOMEWORK:
            feedback = self._execute_assign_homework(action)
        elif action.action_type == ActionType.STUDENT_ANSWER:
            feedback = self._execute_student_answer(action)
        elif action.action_type == ActionType.PROVIDE_FEEDBACK:
            feedback = self._execute_provide_feedback(action)
        elif action.action_type == ActionType.PEER_DISCUSSION:
            feedback = self._execute_peer_discussion(action)
        elif action.action_type == ActionType.SELF_STUDY:
            feedback = self._execute_self_study(action)
        else:
            feedback = {"error": f"未知动作类型: {action.action_type}"}
        
        # 更新全局状态
        self._update_global_state()
        
        # 检查是否结束
        done = self.state.current_round >= self.state.total_rounds
        
        return {
            "reward": feedback.get('reward', 0.0),
            "next_state": self.get_state(),
            "done": done,
            "info": feedback
        }
    
    def _execute_teach(self, action: Action) -> Dict[str, Any]:
        """执行教学动作"""
        teacher_id = action.actor_id
        target_students = action.target_ids
        
        # 获取教学参数
        teaching_intensity = action.parameters.get('intensity', 0.7)
        topic_difficulty = action.parameters.get('topic_difficulty', 0.5)
        
        reward = 0.0
        
        for student_id in target_students:
            if student_id not in self.students_state:
                continue
            
            state = self.students_state[student_id]
            
            # 教学效果取决于学生当前状态和教学强度
            learning_gain = teaching_intensity * (1 - state['fatigue'])
            
            # 更新认知水平
            state['cognitive_level'] += learning_gain * 0.1
            
            # 更新疲劳度
            state['fatigue'] = min(1.0, state['fatigue'] + 0.1)
            
            # 计算奖励（学习效果）
            reward += learning_gain
        
        avg_reward = reward / len(target_students) if target_students else 0
        
        # 更新教学进度
        self.state.teaching_progress = min(1.0, 
            self.state.teaching_progress + 0.05 * teaching_intensity)
        
        return {
            "reward": avg_reward,
            "learning_gains": {sid: self.students_state[sid]['cognitive_level'] 
                             for sid in target_students},
            "message": f"教学完成，平均学习增益: {avg_reward:.3f}"
        }
    
    def _execute_assign_homework(self, action: Action) -> Dict[str, Any]:
        """执行布置作业动作"""
        num_questions = action.parameters.get('num_questions', 5)
        difficulty_range = action.parameters.get('difficulty_range', (0.0, 1.0))
        
        # 生成作业题目
        homework_items = []
        for i in range(num_questions):
            diff = difficulty_range[0] + (difficulty_range[1] - difficulty_range[0]) * (i / num_questions)
            homework_items.append({
                "item_id": f"HW_{self.state.current_round}_{i}",
                "difficulty": diff
            })
        
        return {
            "reward": 0.1,
            "homework_items": homework_items,
            "message": f"布置了 {num_questions} 道作业题"
        }
    
    def _execute_student_answer(self, action: Action) -> Dict[str, Any]:
        """执行学生作答动作"""
        student_id = action.actor_id
        item_difficulty = action.parameters.get('item_difficulty', 0.5)
        
        if student_id not in self.students_state:
            return {"error": f"学生 {student_id} 不存在"}
        
        state = self.students_state[student_id]
        
        # 使用 IRT 模型计算答对概率
        import numpy as np
        theta = state['cognitive_level']
        b = item_difficulty
        
        # 2PL 模型
        a = 1.0  # 区分度
        prob_correct = 1 / (1 + np.exp(-a * (theta - b)))
        
        # 考虑焦虑和动机的影响
        anxiety_factor = max(0.7, 1.0 - state['anxiety_threshold'] * 0.3)
        motivation_factor = 0.8 + state['motivation_level'] * 0.2
        
        adjusted_prob = prob_correct * anxiety_factor * motivation_factor
        
        # 模拟作答结果
        score = 1 if np.random.random() < adjusted_prob else 0
        
        # 更新学生状态
        if score == 1:
            # 成功体验提升动机
            state['motivation_level'] = min(1.0, state['motivation_level'] + 0.05)
            state['anxiety_threshold'] = max(0.0, state['anxiety_threshold'] - 0.03)
        else:
            # 失败可能增加焦虑
            if state['cognitive_level'] < b:
                state['anxiety_threshold'] = min(1.0, state['anxiety_threshold'] + 0.05)
        
        # 减少疲劳
        state['fatigue'] = max(0.0, state['fatigue'] - 0.05)
        
        # 奖励基于表现
        reward = 1.0 if score == 1 else -0.2
        
        return {
            "reward": reward,
            "score": score,
            "probability": float(adjusted_prob),
            "updated_state": state.copy(),
            "message": f"学生 {student_id} 作答: {'正确' if score else '错误'}"
        }
    
    def _execute_provide_feedback(self, action: Action) -> Dict[str, Any]:
        """执行提供反馈动作"""
        teacher_id = action.actor_id
        target_students = action.target_ids
        feedback_quality = action.parameters.get('quality', 0.8)
        
        total_improvement = 0.0
        
        for student_id in target_students:
            if student_id not in self.students_state:
                continue
            
            state = self.students_state[student_id]
            
            # 反馈效果
            improvement = feedback_quality * 0.1
            state['motivation_level'] = min(1.0, state['motivation_level'] + improvement)
            state['anxiety_threshold'] = max(0.0, state['anxiety_threshold'] - improvement * 0.5)
            
            total_improvement += improvement
        
        avg_improvement = total_improvement / len(target_students) if target_students else 0
        
        return {
            "reward": avg_improvement,
            "improvement": avg_improvement,
            "message": f"反馈完成，平均动机提升: {avg_improvement:.3f}"
        }
    
    def _execute_peer_discussion(self, action: Action) -> Dict[str, Any]:
        """执行同伴讨论动作"""
        participants = action.target_ids
        
        if len(participants) < 2:
            return {"error": "同伴讨论需要至少2名学生"}
        
        # 计算参与者的平均能力
        cognitive_levels = [
            self.students_state[sid]['cognitive_level']
            for sid in participants
            if sid in self.students_state
        ]
        
        if not cognitive_levels:
            return {"error": "参与者状态无效"}
        
        avg_cognitive = sum(cognitive_levels) / len(cognitive_levels)
        
        # 同伴学习效果
        learning_gain = 0.15
        engagement_boost = 0.2
        
        for student_id in participants:
            if student_id in self.students_state:
                state = self.students_state[student_id]
                state['cognitive_level'] += learning_gain
                state['engagement'] = min(1.0, state['engagement'] + engagement_boost)
                state['fatigue'] = min(1.0, state['fatigue'] + 0.05)
        
        # 更新课堂氛围
        self.state.classroom_atmosphere = min(1.0, 
            self.state.classroom_atmosphere + 0.1)
        
        return {
            "reward": learning_gain,
            "participants": len(participants),
            "avg_cognitive_before": avg_cognitive,
            "message": f"同伴讨论完成，{len(participants)} 人参与"
        }
    
    def _execute_self_study(self, action: Action) -> Dict[str, Any]:
        """执行自主学习动作"""
        student_id = action.actor_id
        study_duration = action.parameters.get('duration', 1.0)
        
        if student_id not in self.students_state:
            return {"error": f"学生 {student_id} 不存在"}
        
        state = self.students_state[student_id]
        
        # 自主学习效果取决于动机和当前疲劳
        effectiveness = state['motivation_level'] * (1 - state['fatigue'])
        learning_gain = effectiveness * study_duration * 0.08
        
        state['cognitive_level'] += learning_gain
        state['fatigue'] = min(1.0, state['fatigue'] + study_duration * 0.1)
        
        return {
            "reward": learning_gain,
            "learning_gain": learning_gain,
            "effectiveness": effectiveness,
            "message": f"自主学习完成，学习增益: {learning_gain:.3f}"
        }
    
    def _update_global_state(self):
        """更新全局环境状态"""
        if not self.students_state:
            return
        
        # 计算平均参与度和疲劳
        engagements = [s['engagement'] for s in self.students_state.values()]
        fatigues = [s['fatigue'] for s in self.students_state.values()]
        
        self.state.average_engagement = sum(engagements) / len(engagements)
        avg_fatigue = sum(fatigues) / len(fatigues)
        
        # 课堂氛围受参与度影响
        self.state.classroom_atmosphere = (
            self.state.classroom_atmosphere * 0.9 + 
            self.state.average_engagement * 0.1
        )
        
        # 推进轮次
        self.state.current_round += 1
    
    def get_state(self) -> Dict[str, Any]:
        """
        获取当前环境状态
        
        Returns:
            状态字典
        """
        return {
            "environment": vars(self.state),
            "students_count": len(self.students_state),
            "teacher": self.teacher_state,
            "action_history_length": len(self.action_history)
        }
    
    def render(self) -> str:
        """
        渲染环境状态（文本形式）
        
        Returns:
            状态描述字符串
        """
        lines = [
            f"📚 课堂环境状态 (第 {self.state.current_round}/{self.state.total_rounds} 轮)",
            f"   课堂氛围: {self.state.classroom_atmosphere:.2f}",
            f"   平均参与度: {self.state.average_engagement:.2f}",
            f"   教学进度: {self.state.teaching_progress:.1%}",
            f"   历史动作数: {len(self.action_history)}",
        ]
        
        if self.students_state:
            avg_cognitive = sum(s['cognitive_level'] for s in self.students_state.values()) / len(self.students_state)
            avg_motivation = sum(s['motivation_level'] for s in self.students_state.values()) / len(self.students_state)
            avg_anxiety = sum(s['anxiety_threshold'] for s in self.students_state.values()) / len(self.students_state)
            
            lines.extend([
                f"\n👨‍🎓 学生平均状态:",
                f"   认知水平: {avg_cognitive:.2f}",
                f"   动机水平: {avg_motivation:.2f}",
                f"   焦虑阈值: {avg_anxiety:.2f}",
            ])
        
        return "\n".join(lines)
