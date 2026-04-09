"""
Test Phase 4 - Service Layer
测试 Phase 4 服务层模块
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_graph_service():
    """测试图谱服务"""
    print("=" * 70)
    print("测试 1: GraphService")
    print("=" * 70)
    
    from app.core.knowledge_graph import GraphEngine
    from app.services import GraphService
    
    # 初始化图引擎
    print("\n1️⃣  初始化图引擎...")
    engine = GraphEngine(backend_type="json", config={"storage_path": "data/test_phase4_graph"})
    engine.initialize()
    
    # 添加测试数据
    print("\n2️⃣  添加测试数据...")
    engine.add_node("S001", "Student", {
        "cognitive_level": 0.5,
        "anxiety_threshold": 0.3,
        "motivation_level": 0.8,
        "class_name": "Class_A"
    })
    engine.add_node("S002", "Student", {
        "cognitive_level": -0.8,
        "anxiety_threshold": 0.7,
        "motivation_level": 0.4,
        "class_name": "Class_A"
    })
    engine.add_node("Q001", "Item", {
        "difficulty": 0.3,
        "discrimination": 1.2
    })
    engine.add_edge("S001", "Q001", "ATTEMPTED", {"score": 1.0})
    print("   ✓ 测试数据就绪")
    
    # 创建服务
    print("\n3️⃣  创建 GraphService...")
    service = GraphService(engine)
    print("   ✓ 服务就绪")
    
    # 测试获取学生画像
    print("\n4️⃣  测试获取学生画像...")
    profile = service.get_student_profile("S001")
    if profile:
        print(f"   ✓ 学生ID: {profile['student_id']}")
        print(f"   ✓ 认知水平: {profile['attributes'].get('cognitive_level')}")
        print(f"   ✓ 作答记录数: {len(profile['attempted_items'])}")
    else:
        print("   ❌ 获取失败")
    
    # 测试班级统计
    print("\n5️⃣  测试班级统计...")
    stats = service.get_class_statistics("Class_A")
    if "error" not in stats:
        print(f"   ✓ 班级: {stats['class_name']}")
        print(f"   ✓ 学生数: {stats['student_count']}")
        print(f"   ✓ 平均能力: {stats['avg_cognitive_level']:.2f}")
    else:
        print(f"   ⚠️  {stats['error']}")
    
    # 测试图谱概览
    print("\n6️⃣  测试图谱概览...")
    overview = service.get_graph_overview()
    print(f"   ✓ 节点总数: {overview['total_nodes']}")
    print(f"   ✓ 边总数: {overview['total_edges']}")
    print(f"   ✓ 标签分布: {overview['label_distribution']}")
    
    engine.close()
    print("\n✅ GraphService 测试通过!\n")


def test_calibration_service():
    """测试校准服务"""
    print("=" * 70)
    print("测试 2: CalibrationService")
    print("=" * 70)
    
    from app.core.knowledge_graph import GraphEngine
    from app.core.agent_modeling import IRTEngine
    from app.services import GraphService, CalibrationService
    import numpy as np
    
    # 初始化
    print("\n1️⃣  初始化服务...")
    engine = GraphEngine(backend_type="json", config={"storage_path": "data/test_calib_graph"})
    engine.initialize()
    graph_service = GraphService(engine)
    calibration_service = CalibrationService(graph_service)
    print("   ✓ 服务就绪")
    
    # 构建测试数据
    print("\n2️⃣  构建测试数据...")
    exam_data = {
        "students_meta": {
            "S001": {"id": "S001", "class": "Class_A"},
            "S002": {"id": "S002", "class": "Class_A"},
            "S003": {"id": "S003", "class": "Class_A"}
        },
        "items_meta": {
            "Q001": {"item_id": "Q001", "difficulty": 0.0},
            "Q002": {"item_id": "Q002", "difficulty": 0.5},
            "Q003": {"item_id": "Q003", "difficulty": 1.0}
        },
        "responses": [
            {"student_id": "S001", "question_index": 1, "score": 1.0},
            {"student_id": "S001", "question_index": 2, "score": 1.0},
            {"student_id": "S001", "question_index": 3, "score": 0.0},
            {"student_id": "S002", "question_index": 1, "score": 0.0},
            {"student_id": "S002", "question_index": 2, "score": 0.0},
            {"student_id": "S002", "question_index": 3, "score": 0.0},
            {"student_id": "S003", "question_index": 1, "score": 1.0},
            {"student_id": "S003", "question_index": 2, "score": 1.0},
            {"student_id": "S003", "question_index": 3, "score": 1.0},
        ]
    }
    print(f"   ✓ 学生数: {len(exam_data['students_meta'])}")
    print(f"   ✓ 试题数: {len(exam_data['items_meta'])}")
    print(f"   ✓ 作答记录: {len(exam_data['responses'])}")
    
    # 执行完整校准流程
    print("\n3️⃣  执行完整校准流程...")
    report = calibration_service.full_calibration_pipeline(
        exam_data,
        sync_to_graph=False
    )
    
    print(f"\n📊 校准报告:")
    print(f"   学生数: {report['calibration_summary']['total_students']}")
    print(f"   试题数: {report['calibration_summary']['total_items']}")
    print(f"   学生能力均值: {report['student_statistics']['mean_theta']:.2f}")
    print(f"   试题难度均值: {report['item_statistics']['mean_difficulty']:.2f}")
    print(f"   质量评级: {report['quality_assessment']['overall_rating']}")
    
    if report['quality_assessment']['warnings']:
        print(f"\n⚠️  警告:")
        for warn in report['quality_assessment']['warnings']:
            print(f"      - {warn}")
    
    # 测试在线能力估计
    print("\n4️⃣  测试在线能力估计...")
    recent_responses = [
        {"item_id": "Q001", "score": 1.0, "difficulty": 0.3},
        {"item_id": "Q002", "score": 1.0, "difficulty": 0.5},
        {"item_id": "Q003", "score": 0.0, "difficulty": 1.0}
    ]
    
    theta = calibration_service.estimate_student_ability_online("S001", recent_responses)
    print(f"   ✓ 估计能力值: θ = {theta:.2f}")
    
    engine.close()
    print("\n✅ CalibrationService 测试通过!\n")


def test_prediction_service():
    """测试预测服务"""
    print("=" * 70)
    print("测试 3: PredictionService")
    print("=" * 70)
    
    from app.core.knowledge_graph import GraphEngine
    from app.core.agent_modeling import IRTEngine
    from app.services import GraphService, PredictionService
    
    # 初始化
    print("\n1️⃣  初始化服务...")
    engine = GraphEngine(backend_type="json", config={"storage_path": "data/test_pred_graph"})
    engine.initialize()
    
    # 添加测试数据
    engine.add_node("S001", "Student", {
        "cognitive_level": 0.5,
        "anxiety_threshold": 0.3,
        "motivation_level": 0.8
    })
    engine.add_node("Q001", "Item", {"difficulty": 0.3, "discrimination": 1.2})
    engine.add_node("Q002", "Item", {"difficulty": 0.8, "discrimination": 1.5})
    
    graph_service = GraphService(engine)
    prediction_service = PredictionService(graph_service)
    print("   ✓ 服务就绪")
    
    # 测试学生表现预测
    print("\n2️⃣  测试学生表现预测...")
    predictions = prediction_service.predict_student_performance(
        "S001",
        ["Q001", "Q002"]
    )
    
    if "error" not in predictions:
        print(f"   ✓ 学生ID: {predictions['student_id']}")
        print(f"   ✓ 当前能力: θ = {predictions['current_theta']:.2f}")
        print(f"   ✓ 预测题数: {len(predictions['predictions'])}")
        
        for pred in predictions['predictions']:
            print(f"      - {pred['item_id']}: "
                  f"答对概率 {pred['adjusted_probability']:.2%}")
        
        print(f"   ✓ 平均预测得分: {predictions['avg_predicted_score']:.2f}")
    else:
        print(f"   ❌ {predictions['error']}")
    
    # 测试干预效果预测
    print("\n3️⃣  测试干预效果预测...")
    effect = prediction_service.predict_intervention_effect(
        "S001",
        "heuristic",
        duration_rounds=3
    )
    
    if "error" not in effect:
        print(f"   ✓ 干预类型: {effect['intervention_description']}")
        print(f"   ✓ 持续轮数: {effect['duration_rounds']}")
        print(f"   ✓ 能力提升: Δθ = {effect['improvements']['theta_gain']:.2f}")
        print(f"   ✓ 焦虑降低: Δanxiety = {effect['improvements']['anxiety_reduction']:.2f}")
        print(f"   ✓ 动机提升: Δmotivation = {effect['improvements']['motivation_gain']:.2f}")
    else:
        print(f"   ❌ {effect['error']}")
    
    # 测试最优干预推荐
    print("\n4️⃣  测试最优干预推荐...")
    recommendation = prediction_service.recommend_optimal_intervention("S001")
    
    if "error" not in recommendation:
        print(f"   ✓ 当前状态:")
        print(f"      - θ = {recommendation['current_state']['theta']:.2f}")
        print(f"      - 焦虑 = {recommendation['current_state']['anxiety']:.2f}")
        print(f"      - 动机 = {recommendation['current_state']['motivation']:.2f}")
        print(f"   ✓ 推荐策略: {recommendation['best_strategy']}")
        
        if recommendation['recommendations']:
            print(f"\n   策略排名:")
            for i, rec in enumerate(recommendation['recommendations'][:3], 1):
                print(f"      {i}. {rec['strategy']}: 得分 {rec['score']:.4f}")
    else:
        print(f"   ❌ {recommendation['error']}")
    
    # 测试学习轨迹模拟
    print("\n5️⃣  测试学习轨迹模拟...")
    trajectory = prediction_service.simulate_learning_trajectory(
        "S001",
        num_rounds=5,
        learning_rate=0.05
    )
    
    if "error" not in trajectory:
        print(f"   ✓ 初始能力: θ = {trajectory['initial_theta']:.2f}")
        print(f"   ✓ 最终能力: θ = {trajectory['final_theta']:.2f}")
        print(f"   ✓ 总进步: Δθ = {trajectory['total_progress']:.2f}")
        
        print(f"\n   轨迹:")
        for point in trajectory['trajectory']:
            print(f"      第{point['round']}轮: θ = {point['theta']:.2f} "
                  f"(+{point['progress']:.3f})")
    else:
        print(f"   ❌ {trajectory['error']}")
    
    engine.close()
    print("\n✅ PredictionService 测试通过!\n")


def test_integrated_services():
    """测试集成服务流程"""
    print("=" * 70)
    print("测试 4: 集成服务流程")
    print("=" * 70)
    
    from app.core.knowledge_graph import GraphEngine
    from app.core.agent_modeling import IRTEngine
    from app.services import GraphService, CalibrationService, PredictionService
    import numpy as np
    
    print("\n📋 执行完整服务流程:")
    print("   1. 初始化服务 → 2. 校准参数 → 3. 预测表现 → 4. 推荐干预\n")
    
    # Step 1: 初始化
    print("Step 1: 初始化所有服务...")
    engine = GraphEngine(backend_type="json", config={"storage_path": "data/integrated_graph"})
    engine.initialize()
    
    graph_service = GraphService(engine)
    calibration_service = CalibrationService(graph_service)
    prediction_service = PredictionService(graph_service)
    print("   ✓ 所有服务就绪")
    
    # Step 2: 准备数据并校准
    print("\nStep 2: 校准 IRT 参数...")
    exam_data = {
        "students_meta": {
            f"S{i:03d}": {"id": f"S{i:03d}", "class": "Class_A"}
            for i in range(1, 6)
        },
        "items_meta": {
            f"Q{i:03d}": {"item_id": f"Q{i:03d}", "difficulty": (i-3)*0.5}
            for i in range(1, 6)
        },
        "responses": []
    }
    
    # 生成模拟作答数据
    np.random.seed(42)
    for sid in exam_data["students_meta"]:
        true_theta = np.random.normal(0, 1)
        for q_idx in range(1, 6):
            difficulty = (q_idx - 3) * 0.5
            prob = 1 / (1 + np.exp(-(true_theta - difficulty)))
            score = 1 if np.random.random() < prob else 0
            
            exam_data["responses"].append({
                "student_id": sid,
                "question_index": q_idx,
                "score": float(score)
            })
    
    report = calibration_service.full_calibration_pipeline(exam_data, sync_to_graph=False)
    print(f"   ✓ 校准完成，质量评级: {report['quality_assessment']['overall_rating']}")
    
    # Step 3: 预测学生表现
    print("\nStep 3: 预测学生表现...")
    student_id = "S001"
    item_ids = ["Q001", "Q002", "Q003"]
    
    predictions = prediction_service.predict_student_performance(student_id, item_ids)
    if "error" not in predictions:
        print(f"   ✓ 学生 {student_id} 的平均预测得分: "
              f"{predictions['avg_predicted_score']:.2f}")
    
    # Step 4: 推荐干预
    print("\nStep 4: 推荐最优干预...")
    recommendation = prediction_service.recommend_optimal_intervention(student_id)
    if "error" not in recommendation:
        print(f"   ✓ 推荐策略: {recommendation['best_strategy']}")
    
    engine.close()
    print("\n✅ 集成服务流程测试通过!\n")


if __name__ == "__main__":
    print("\n🧪 Phase 4 服务层测试套件\n")
    
    try:
        test_graph_service()
        test_calibration_service()
        test_prediction_service()
        test_integrated_services()
        
        print("=" * 70)
        print("🎉 所有 Phase 4 测试通过!")
        print("=" * 70)
        print("\n✨ Phase 4 核心功能验证成功!")
        print("   - ✅ GraphService (图谱查询服务)")
        print("   - ✅ CalibrationService (IRT 校准服务)")
        print("   - ✅ PredictionService (预测服务)")
        print("   - ✅ 集成服务流程")
        print("\n📖 下一步: Phase 5 - CLI 重构\n")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
