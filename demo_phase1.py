"""
Edu-Sim Phase 1 Demo
演示新架构的核心功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.knowledge_graph import GraphEngine
from app.core.agent_modeling import StudentAgent, TeacherAgent, IRTEngine
from app.models.education import Student, Item, Response
import numpy as np


def demo_knowledge_graph():
    """演示知识图谱功能"""
    print("=" * 70)
    print("📊 演示 1: 知识图谱构建")
    print("=" * 70)
    
    # 创建图引擎
    engine = GraphEngine(backend_type="json", config={"storage_path": "data/demo_graph"})
    engine.initialize()
    
    # 添加教育实体
    print("\n1️⃣  添加学生节点...")
    engine.add_node("student_001", "Student", {
        "name": "张三",
        "cognitive_level": 0.6,
        "anxiety_threshold": 0.3
    })
    
    print("2️⃣  添加试题节点...")
    engine.add_node("item_001", "Item", {
        "difficulty": 0.2,
        "discrimination": 1.5
    })
    
    print("3️⃣  添加知识点节点...")
    engine.add_node("concept_001", "Concept", {
        "name": "二次方程",
        "grade_level": 8
    })
    
    print("4️⃣  建立关系...")
    engine.add_edge("student_001", "item_001", "ATTEMPTED", {"score": 1.0})
    engine.add_edge("item_001", "concept_001", "BELONGS_TO")
    
    # 查询统计
    stats = engine.get_stats()
    print(f"\n📈 图谱统计:")
    print(f"   - 节点总数: {stats['node_count']}")
    print(f"   - 边总数: {stats['edge_count']}")
    print(f"   - 标签分布: {stats['labels']}")
    
    # 查询邻居
    neighbors = engine.get_neighbors("student_001")
    print(f"\n🔍 student_001 的关联实体:")
    for neighbor in neighbors:
        print(f"   - {neighbor.get('id', 'N/A')} ({neighbor.get('label', 'N/A')})")
    
    engine.close()
    print("\n✅ 知识图谱演示完成!\n")


def demo_irt_calibration():
    """演示 IRT 参数校准"""
    print("=" * 70)
    print("📐 演示 2: IRT 参数校准")
    print("=" * 70)
    
    # 创建 IRT 引擎
    irt = IRTEngine(model_type="2PL")
    
    # 模拟作答数据 (5学生 × 4题目)
    print("\n1️⃣  生成模拟作答数据...")
    np.random.seed(42)
    response_matrix = np.array([
        [1.0, 1.0, 0.0, 1.0],  # 学生1: 能力强
        [1.0, 0.0, 0.0, 0.0],  # 学生2: 能力中等
        [0.0, 0.0, 0.0, 1.0],  # 学生3: 能力弱
        [1.0, 1.0, 1.0, 1.0],  # 学生4: 能力很强
        [0.0, 0.0, 0.0, 0.0]   # 学生5: 能力很弱
    ])
    
    print(f"   作答矩阵形状: {response_matrix.shape}")
    print(f"   平均正确率: {np.nanmean(response_matrix):.2%}")
    
    # 校准参数
    print("\n2️⃣  执行 IRT 校准 (2PL 模型)...")
    results = irt.calibrate(response_matrix, max_iterations=100)
    
    print(f"\n📊 校准结果:")
    print(f"   学生能力值 (θ):")
    for i, theta in enumerate(results['student_thetas']):
        print(f"      学生{i+1}: θ = {theta:.2f}")
    
    print(f"\n   题目难度 (b):")
    for j, b in enumerate(results['item_difficulties']):
        print(f"      题目{j+1}: b = {b:.2f}")
    
    print(f"\n   题目区分度 (a):")
    for j, a in enumerate(results['item_discriminations']):
        print(f"      题目{j+1}: a = {a:.2f}")
    
    # 预测概率
    print(f"\n3️⃣  预测答对概率...")
    prob = irt.predict_probability(theta=0.5, difficulty=0.0, discrimination=1.0)
    print(f"   P(答对 | θ=0.5, b=0.0, a=1.0) = {prob:.2%}")
    
    print("\n✅ IRT 校准演示完成!\n")


def demo_student_agent():
    """演示学生智能体"""
    print("=" * 70)
    print("👨‍🎓 演示 3: 学生智能体仿真")
    print("=" * 70)
    
    # 创建学生 Agent
    print("\n1️⃣  创建学生智能体...")
    student = StudentAgent(
        student_id="S001",
        name="李四",
        cognitive_level=0.5,
        anxiety_threshold=0.4,
        motivation_level=0.7
    )
    
    print(f"   学生ID: {student.student_id}")
    print(f"   姓名: {student.name}")
    print(f"   认知水平: {student.cognitive_level:.2f}")
    print(f"   焦虑阈值: {student.anxiety_threshold:.2f}")
    print(f"   动机水平: {student.motivation_level:.2f}")
    
    # 模拟多次作答
    print(f"\n2️⃣  模拟作答过程 (5道不同难度的题目)...")
    difficulties = [-0.5, 0.0, 0.5, 1.0, 1.5]
    
    scores = []
    for diff in difficulties:
        prob = student.predict_response_probability(diff)
        score = student.simulate_response(diff)
        scores.append(score)
        
        result = "✓" if score == 1 else "✗"
        print(f"   题目难度 b={diff:4.1f} | 答对概率 {prob:.2%} | 结果 {result}")
    
    print(f"\n   总得分: {sum(scores)}/{len(scores)}")
    
    # 应用教学干预
    print(f"\n3️⃣  应用教学干预...")
    print(f"   干预前 - 焦虑阈值: {student.anxiety_threshold:.2f}, 动机: {student.motivation_level:.2f}")
    
    student.update_after_intervention("heuristic")
    print(f"   启发式干预后 - 焦虑阈值: {student.anxiety_threshold:.2f}, 动机: {student.motivation_level:.2f}")
    
    student.update_after_intervention("scaffolding")
    print(f"   支架式干预后 - 焦虑阈值: {student.anxiety_threshold:.2f}, 动机: {student.motivation_level:.2f}")
    
    print("\n✅ 学生智能体演示完成!\n")


def demo_teacher_agent():
    """演示教师智能体"""
    print("=" * 70)
    print("👩‍🏫 演示 4: 教师智能体决策")
    print("=" * 70)
    
    # 创建教师 Agent
    print("\n1️⃣  创建教师智能体...")
    teacher = TeacherAgent(
        teacher_id="T001",
        name="王老师",
        teaching_style="supportive",
        experience_years=10
    )
    
    print(f"   教师ID: {teacher.teacher_id}")
    print(f"   姓名: {teacher.name}")
    print(f"   教学风格: {teacher.teaching_style}")
    print(f"   教龄: {teacher.experience_years} 年")
    
    # 模拟教学决策
    print(f"\n2️⃣  根据学生状态选择干预策略...")
    
    scenarios = [
        {"anxiety": 0.8, "motivation": 0.3, "performance": 0.4},
        {"anxiety": 0.2, "motivation": 0.9, "performance": 0.8},
        {"anxiety": 0.5, "motivation": 0.5, "performance": 0.5},
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        intervention = teacher.select_intervention(
            anxiety=scenario["anxiety"],
            motivation=scenario["motivation"],
            performance=scenario["performance"]
        )
        print(f"   场景{i}: 焦虑={scenario['anxiety']:.1f}, "
              f"动机={scenario['motivation']:.1f}, "
              f"表现={scenario['performance']:.1f}")
        print(f"      → 推荐干预: {intervention}")
    
    print("\n✅ 教师智能体演示完成!\n")


def demo_data_models():
    """演示数据模型"""
    print("=" * 70)
    print("💾 演示 5: 结构化数据模型")
    print("=" * 70)
    
    # 创建学生
    print("\n1️⃣  创建学生实体...")
    student = Student(
        student_id="S001",
        cognitive_level=0.65,
        learning_style="visual",
        anxiety_threshold=0.3,
        motivation_level=0.8,
        class_name="Class_8A"
    )
    print(f"   ID: {student.student_id}")
    print(f"   认知水平: {student.cognitive_level:.2f}")
    print(f"   学习风格: {student.learning_style}")
    print(f"   班级: {student.class_name}")
    
    # 创建试题
    print("\n2️⃣  创建试题实体...")
    item = Item(
        item_id="I001",
        difficulty=0.3,
        discrimination=1.2,
        question_type="multiple_choice",
        subject="Mathematics",
        assessed_concepts=["C001", "C002"]
    )
    print(f"   ID: {item.item_id}")
    print(f"   难度: {item.difficulty:.2f}")
    print(f"   区分度: {item.discrimination:.2f}")
    print(f"   题型: {item.question_type}")
    print(f"   学科: {item.subject}")
    
    # 创建作答记录
    print("\n3️⃣  创建作答记录...")
    response = Response(
        student_id="S001",
        item_id="I001",
        score=1.0,
        time_spent=120.5
    )
    print(f"   学生: {response.student_id}")
    print(f"   试题: {response.item_id}")
    print(f"   得分: {response.score}")
    print(f"   用时: {response.time_spent:.1f}秒")
    
    print("\n✅ 数据模型演示完成!\n")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🚀 Edu-Sim Phase 1 功能演示")
    print("=" * 70 + "\n")
    
    try:
        demo_knowledge_graph()
        demo_irt_calibration()
        demo_student_agent()
        demo_teacher_agent()
        demo_data_models()
        
        print("=" * 70)
        print("🎉 所有演示完成!")
        print("=" * 70)
        print("\n✨ Phase 1 核心功能验证成功!")
        print("   - ✅ 知识图谱后端抽象层")
        print("   - ✅ 教育领域本体定义")
        print("   - ✅ IRT 参数校准引擎")
        print("   - ✅ 学生/教师智能体建模")
        print("   - ✅ 结构化数据模型")
        print("\n📖 下一步: Phase 2 - 数据摄入重构\n")
        
    except Exception as e:
        print(f"\n❌ 演示失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
