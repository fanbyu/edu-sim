import random
import math

# ==============================================================================
# 1. 教育测量学模型 (IRT - 3PL Model)
# ==============================================================================
def irt_3pl(theta, a, b, c):
    """
    计算学生答对题目的概率
    :param theta: 学生能力值
    :param a: 题目区分度
    :param b: 题目难度
    :param c: 猜测参数
    :return: 答对概率
    """
    exponent = -1.7 * a * (theta - b)
    # 防止指数溢出
    if exponent > 500: exponent = 500
    if exponent < -500: exponent = -500
    p = c + (1 - c) / (1 + math.exp(exponent))
    return p

# ==============================================================================
# 2. 智能体定义 (Agent Definitions)
# ==============================================================================
class StudentAgent:
    def __init__(self, student_id, theta, anxiety_level=0.5):
        self.id = student_id
        self.theta = theta  # 认知能力值
        self.anxiety = anxiety_level # 焦虑水平 (0-1)
        self.knowledge_state = {} # 知识点掌握状态

    def solve(self, question):
        # 基础概率由 IRT 决定
        base_prob = irt_3pl(self.theta, question['a'], question['b'], question['c'])
        
        # 心理因素修正：高焦虑在面对高难度题目时会降低表现
        if self.anxiety > 0.7 and question['b'] > 0.5:
            base_prob *= (1 - (self.anxiety - 0.7))
            
        is_correct = random.random() < base_prob
        
        # 模拟 LLM 生成解题思路（此处为占位符）
        reasoning_style = "logical" if self.theta > 0 else "intuitive"
        
        return {
            "student_id": self.id,
            "question_id": question['id'],
            "correct": is_correct,
            "probability": base_prob,
            "reasoning_style": reasoning_style
        }

class TeacherAgent:
    def __init__(self, teacher_id, pedagogy_style="heuristic"):
        self.id = teacher_id
        self.style = pedagogy_style # heuristic (启发式) vs direct (灌输式)

    def provide_hint(self, student, question):
        # 教师干预后，学生能力提升的模拟
        boost = 0.2 if self.style == "heuristic" else 0.1
        return boost

# ==============================================================================
# 3. 仿真环境 (Simulation Environment)
# ==============================================================================
def run_education_simulation(num_students=100):
    print(f"--- 开始 Edu-Sim MVP 仿真 (学生数: {num_students}) ---")
    
    # 准备一道测试题 (中等难度)
    question = {
        "id": "Q_Math_001",
        "content": "求解一元二次方程 x^2 - 5x + 6 = 0",
        "a": 1.0, # 区分度
        "b": 0.0, # 难度 (标准正态分布均值)
        "c": 0.2  # 猜测率
    }
    
    # 生成学生群体 (能力值服从正态分布 N(0, 1))
    # 使用 Box-Muller 变换生成正态分布随机数
    def generate_normal_random(mu=0, sigma=1):
        u1 = random.random()
        u2 = random.random()
        z0 = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
        return z0 * sigma + mu

    students = [
        StudentAgent(
            student_id=f"S_{i}", 
            theta=generate_normal_random(),
            anxiety_level=random.uniform(0, 1)
        ) for i in range(num_students)
    ]
    
    results = []
    correct_count = 0
    
    for s in students:
        res = s.solve(question)
        results.append(res)
        if res['correct']:
            correct_count += 1
            
    # 统计结果
    pass_rate = correct_count / num_students
    theoretical_p = irt_3pl(0, question['a'], question['b'], question['c'])
    
    print(f"[仿真结果] 实际通过率: {pass_rate:.4f}")
    print(f"[理论参考] 平均能力者通过率: {theoretical_p:.4f}")
    print(f"[偏差分析] 偏差值: {abs(pass_rate - theoretical_p):.4f}")
    
    return results

if __name__ == "__main__":
    run_education_simulation()
