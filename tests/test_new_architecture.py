"""
Test New Architecture
测试新架构的核心功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_graph_backend():
    """测试图谱后端"""
    print("=" * 60)
    print("测试 1: GraphBackend (JSON)")
    print("=" * 60)
    
    from app.core.knowledge_graph import GraphEngine
    
    # 创建引擎
    engine = GraphEngine(backend_type="json", config={"storage_path": "data/test_graph"})
    engine.initialize()
    
    # 添加节点
    engine.add_node("student_001", "Student", {"cognitive_level": 0.5})
    engine.add_node("item_001", "Item", {"difficulty": 0.2})
    
    # 添加边
    engine.add_edge("student_001", "item_001", "ATTEMPTED", {"score": 1.0})
    
    # 获取统计
    stats = engine.get_stats()
    print(f"✓ 节点数: {stats['node_count']}")
    print(f"✓ 边数: {stats['edge_count']}")
    print(f"✓ 标签分布: {stats['labels']}")
    
    # 获取邻居
    neighbors = engine.get_neighbors("student_001")
    print(f"✓ student_001 的邻居数: {len(neighbors)}")
    
    print("✅ GraphBackend 测试通过!\n")


def test_education_ontology():
    """测试教育本体"""
    print("=" * 60)
    print("测试 2: EducationOntology")
    print("=" * 60)
    
    from app.core.knowledge_graph.ontology import EducationOntology
    
    # 获取节点类型
    node_types = EducationOntology.get_all_node_types()
    print(f"✓ 节点类型: {node_types}")
    
    # 获取关系类型
    relation_types = EducationOntology.get_all_relation_types()
    print(f"✓ 关系类型: {relation_types}")
    
    # 验证节点
    errors = EducationOntology.validate_node("Student", {"cognitive_level": 0.5})
    print(f"✓ 节点验证错误数: {len(errors)}")
    
    # 验证边
    errors = EducationOntology.validate_edge("ATTEMPTED", "Student", "Item")
    print(f"✓ 边验证错误数: {len(errors)}")
    
    print("✅ EducationOntology 测试通过!\n")


def test_irt_engine():
    """测试 IRT 引擎"""
    print("=" * 60)
    print("测试 3: IRTEngine")
    print("=" * 60)
    
    from app.core.agent_modeling import IRTEngine
    import numpy as np
    
    # 创建引擎
    irt = IRTEngine(model_type="2PL")
    
    # 模拟作答数据 (3学生 × 3题目)
    response_matrix = np.array([
        [1.0, 0.0, 1.0],  # 学生1: 对,错,对
        [0.0, 0.0, 1.0],  # 学生2: 错,错,对
        [1.0, 1.0, 1.0]   # 学生3: 对,对,对
    ])
    
    # 校准参数
    results = irt.calibrate(response_matrix, max_iterations=50)
    
    print(f"✓ 学生能力值: {[f'{t:.2f}' for t in results['student_thetas']]}")
    print(f"✓ 题目难度: {[f'{b:.2f}' for b in results['item_difficulties']]}")
    
    # 预测概率
    prob = irt.predict_probability(theta=0.5, difficulty=0.0)
    print(f"✓ 预测答对概率 (θ=0.5, b=0.0): {prob:.2f}")
    
    print("✅ IRTEngine 测试通过!\n")


def test_student_agent():
    """测试学生 Agent"""
    print("=" * 60)
    print("测试 4: StudentAgent")
    print("=" * 60)
    
    from app.core.agent_modeling import StudentAgent
    
    # 创建学生
    student = StudentAgent(
        student_id="S001",
        name="张三",
        cognitive_level=0.5,
        anxiety_threshold=0.3,
        motivation_level=0.8
    )
    
    # 预测答对概率
    prob = student.predict_response_probability(item_difficulty=0.2)
    print(f"✓ 答对概率 (b=0.2): {prob:.2f}")
    
    # 模拟作答
    score = student.simulate_response(item_difficulty=0.2)
    print(f"✓ 模拟作答得分: {score}")
    
    # 应用干预
    student.update_after_intervention("heuristic")
    print(f"✓ 干预后焦虑阈值: {student.anxiety_threshold:.2f}")
    print(f"✓ 干预后动机水平: {student.motivation_level:.2f}")
    
    # 序列化
    data = student.to_dict()
    print(f"✓ 序列化成功: {len(data)} 个字段")
    
    print("✅ StudentAgent 测试通过!\n")


def test_data_models():
    """测试数据模型"""
    print("=" * 60)
    print("测试 5: Education Data Models")
    print("=" * 60)
    
    from app.models.education import Student, Item, Response
    
    # 创建学生
    student = Student(student_id="S001", cognitive_level=0.5)
    print(f"✓ Student 模型: {student.student_id}")
    
    # 创建试题
    item = Item(item_id="I001", difficulty=0.2)
    print(f"✓ Item 模型: {item.item_id}")
    
    # 创建作答记录
    response = Response(student_id="S001", item_id="I001", score=1.0)
    print(f"✓ Response 模型: score={response.score}")
    
    # 转换为字典
    student_dict = student.to_dict()
    print(f"✓ 序列化: {len(student_dict)} 个字段")
    
    print("✅ Data Models 测试通过!\n")


if __name__ == "__main__":
    print("\n🧪 Edu-Sim 新架构测试套件\n")
    
    try:
        test_graph_backend()
        test_education_ontology()
        test_irt_engine()
        test_student_agent()
        test_data_models()
        
        print("=" * 60)
        print("🎉 所有测试通过!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
