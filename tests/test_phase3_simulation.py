"""
Test Phase 3 - Simulation Engine
测试 Phase 3 仿真引擎模块
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_oasis_adapter():
    """测试 OASIS 适配器"""
    print("=" * 70)
    print("测试 1: OasisAdapter")
    print("=" * 70)
    
    from app.core.simulation import OasisAdapter
    
    # 创建适配器
    print("\n1️⃣  初始化 OASIS 适配器...")
    adapter = OasisAdapter(oasis_config={
        "num_rounds": 5,
        "time_step": 5,
        "parallel": False
    })
    print("   ✓ 适配器就绪")
    
    # 从图谱数据初始化
    print("\n2️⃣  从图谱数据初始化 Agents...")
    graph_data = {
        "students": [
            {"id": "S001", "properties": {"cognitive_level": 0.5, "anxiety_threshold": 0.3}},
            {"id": "S002", "properties": {"cognitive_level": -0.8, "anxiety_threshold": 0.7}},
            {"id": "S003", "properties": {"cognitive_level": 1.2, "anxiety_threshold": 0.2}},
        ],
        "teachers": [
            {"id": "T001", "properties": {"teaching_style": "heuristic", "experience_years": 10}}
        ],
        "items": [
            {"properties": {"difficulty": 0.3}},
            {"properties": {"difficulty": 0.8}}
        ]
    }
    
    adapter.initialize_from_graph(graph_data)
    print(f"   ✓ 学生 Agents: {len(adapter.students)}")
    print(f"   ✓ 教师 Agents: {len(adapter.teachers)}")
    
    # 运行仿真
    print("\n3️⃣  运行仿真（无干预）...")
    results = adapter.run_simulation(intervention_strategy=None)
    print(f"   ✓ 完成轮数: {results['rounds_completed']}")
    print(f"   ✓ 性能指标: {results['performance_metrics']}")
    
    # 运行带干预的仿真
    print("\n4️⃣  运行仿真（启发式干预）...")
    adapter2 = OasisAdapter(oasis_config={"num_rounds": 3})
    adapter2.initialize_from_graph(graph_data)
    results2 = adapter2.run_simulation(intervention_strategy="heuristic")
    print(f"   ✓ 应用干预: {len(results2['interventions_applied'])} 次")
    
    # 获取摘要
    summary = adapter.get_simulation_summary()
    print(f"\n5️⃣  仿真摘要:")
    print(f"   学生数: {summary['num_students']}")
    print(f"   教师数: {summary['num_teachers']}")
    print(f"   完成轮数: {summary['rounds_completed']}")
    
    print("\n✅ OasisAdapter 测试通过!\n")


def test_intervention_engine():
    """测试干预引擎"""
    print("=" * 70)
    print("测试 2: InterventionEngine")
    print("=" * 70)
    
    from app.core.simulation import InterventionEngine, InterventionType
    
    # 创建引擎
    print("\n1️⃣  初始化干预引擎...")
    engine = InterventionEngine()
    print("   ✓ 引擎就绪")
    
    # 测试策略选择
    print("\n2️⃣  测试智能策略选择...")
    
    scenarios = [
        {
            "name": "低能力高动机学生",
            "state": {
                "student_id": "S001",
                "cognitive_level": -1.2,
                "anxiety_threshold": 0.3,
                "motivation_level": 0.8
            }
        },
        {
            "name": "高焦虑低动机学生",
            "state": {
                "student_id": "S002",
                "cognitive_level": 0.0,
                "anxiety_threshold": 0.8,
                "motivation_level": 0.2
            }
        },
        {
            "name": "中等水平学生",
            "state": {
                "student_id": "S003",
                "cognitive_level": 0.3,
                "anxiety_threshold": 0.5,
                "motivation_level": 0.6
            }
        }
    ]
    
    for scenario in scenarios:
        strategy = engine.select_intervention(scenario['state'])
        print(f"   {scenario['name']}:")
        print(f"      → 推荐策略: {strategy.value if strategy else '无需干预'}")
    
    # 执行干预
    print("\n3️⃣  执行干预...")
    record = engine.apply_intervention(
        student_id="S001",
        intervention_type=InterventionType.HEURISTIC,
        current_round=1
    )
    print(f"   ✓ 干预记录创建: {record.intervention_type.value}")
    print(f"   ✓ 认知增益: {record.effects.cognitive_level_delta}")
    print(f"   ✓ 持续轮数: {record.effects.duration_rounds}")
    
    # 获取干预效果
    print("\n4️⃣  查询干预效果...")
    effects = engine.get_intervention_effects("S001")
    print(f"   累积效果:")
    print(f"      - 认知能力: +{effects['cognitive_level_delta']:.2f}")
    print(f"      - 焦虑阈值: {effects['anxiety_threshold_delta']:+.2f}")
    print(f"      - 动机水平: +{effects['motivation_level_delta']:.2f}")
    
    # 更新干预（应用衰减）
    print("\n5️⃣  更新活跃干预...")
    engine.update_active_interventions()
    effects_after = engine.get_intervention_effects("S001")
    print(f"   衰减后效果:")
    print(f"      - 认知能力: +{effects_after['cognitive_level_delta']:.2f}")
    
    # 获取统计
    stats = engine.get_intervention_statistics()
    print(f"\n6️⃣  干预统计:")
    print(f"   总干预次数: {stats['total_interventions']}")
    print(f"   活跃干预: {stats['active_interventions']}")
    
    print("\n✅ InterventionEngine 测试通过!\n")


def test_education_env():
    """测试虚拟课堂环境"""
    print("=" * 70)
    print("测试 3: EducationEnv")
    print("=" * 70)
    
    from app.core.simulation import EducationEnv, ActionType, Action
    
    # 创建环境
    print("\n1️⃣  初始化课堂环境...")
    env = EducationEnv(config={
        "num_rounds": 5,
        "class_size": 3
    })
    print("   ✓ 环境就绪")
    
    # 重置环境
    print("\n2️⃣  重置环境...")
    students = [
        {"student_id": "S001", "cognitive_level": 0.5, "anxiety_threshold": 0.3, "motivation_level": 0.7},
        {"student_id": "S002", "cognitive_level": -0.5, "anxiety_threshold": 0.6, "motivation_level": 0.4},
        {"student_id": "S003", "cognitive_level": 1.0, "anxiety_threshold": 0.2, "motivation_level": 0.9}
    ]
    teacher = {"teacher_id": "T001", "teaching_style": "heuristic", "patience_level": 0.8}
    
    env.reset(students=students, teacher=teacher)
    print(f"   ✓ 学生数: {len(env.students_state)}")
    print(f"   ✓ 教师: {env.teacher_state.get('teacher_id')}")
    
    # 执行教学动作
    print("\n3️⃣  执行教学动作...")
    teach_action = Action(
        action_type=ActionType.TEACH,
        actor_id="T001",
        target_ids=["S001", "S002", "S003"],
        parameters={"intensity": 0.8, "topic_difficulty": 0.5}
    )
    
    feedback = env.step(teach_action)
    print(f"   ✓ 奖励: {feedback['reward']:.3f}")
    print(f"   ✓ 消息: {feedback['info']['message']}")
    
    # 执行学生作答
    print("\n4️⃣  执行学生作答...")
    answer_action = Action(
        action_type=ActionType.STUDENT_ANSWER,
        actor_id="S001",
        target_ids=[],
        parameters={"item_difficulty": 0.3}
    )
    
    feedback = env.step(answer_action)
    print(f"   ✓ 得分: {feedback['info']['score']}")
    print(f"   ✓ 答对概率: {feedback['info']['probability']:.2%}")
    
    # 执行同伴讨论
    print("\n5️⃣  执行同伴讨论...")
    discussion_action = Action(
        action_type=ActionType.PEER_DISCUSSION,
        actor_id="T001",
        target_ids=["S001", "S002", "S003"],
        parameters={}
    )
    
    feedback = env.step(discussion_action)
    print(f"   ✓ 参与人数: {feedback['info']['participants']}")
    print(f"   ✓ 消息: {feedback['info']['message']}")
    
    # 渲染环境状态
    print("\n6️⃣  环境状态:")
    print(env.render())
    
    # 获取状态
    state = env.get_state()
    print(f"\n7️⃣  状态信息:")
    print(f"   当前轮次: {state['environment']['current_round']}")
    print(f"   动作历史: {state['action_history_length']}")
    
    print("\n✅ EducationEnv 测试通过!\n")


def test_integrated_simulation():
    """测试集成仿真流程"""
    print("=" * 70)
    print("测试 4: 集成仿真流程")
    print("=" * 70)
    
    from app.core.simulation import OasisAdapter, InterventionEngine, EducationEnv, ActionType, Action
    
    print("\n📋 执行完整仿真流程:")
    print("   1. 初始化 OASIS → 2. 设置干预引擎 → 3. 创建课堂环境 → 4. 运行仿真\n")
    
    # Step 1: 初始化 OASIS
    print("Step 1: 初始化 OASIS 适配器...")
    adapter = OasisAdapter(oasis_config={"num_rounds": 3})
    
    graph_data = {
        "students": [
            {"id": f"S{i:03d}", "properties": {
                "cognitive_level": (i - 5) * 0.3,
                "anxiety_threshold": 0.3 + (i % 3) * 0.2,
                "motivation_level": 0.5 + (i % 4) * 0.1
            }}
            for i in range(1, 11)  # 10名学生
        ],
        "teachers": [
            {"id": "T001", "properties": {"teaching_style": "heuristic"}}
        ]
    }
    
    adapter.initialize_from_graph(graph_data)
    print(f"   ✓ 初始化 {len(adapter.students)} 名学生")
    
    # Step 2: 设置干预引擎
    print("\nStep 2: 配置干预引擎...")
    intervention_engine = InterventionEngine()
    print("   ✓ 干预引擎就绪")
    
    # Step 3: 创建课堂环境
    print("\nStep 3: 创建虚拟课堂环境...")
    env = EducationEnv(config={"num_rounds": 3})
    env.reset(students=[s.to_dict() for s in adapter.students])
    print(f"   ✓ 课堂环境就绪 ({len(env.students_state)} 名学生)")
    
    # Step 4: 运行仿真
    print("\nStep 4: 运行集成仿真...")
    results = adapter.run_simulation(intervention_strategy="heuristic")
    
    print(f"\n📊 仿真结果:")
    print(f"   完成轮数: {results['rounds_completed']}")
    print(f"   应用干预: {len(results['interventions_applied'])} 次")
    
    metrics = results['performance_metrics']
    if metrics:
        print(f"\n📈 最终指标:")
        print(f"   平均认知水平: {metrics.get('avg_cognitive_level', 0):.2f}")
        print(f"   平均动机水平: {metrics.get('avg_motivation', 0):.2f}")
        print(f"   平均焦虑阈值: {metrics.get('avg_anxiety', 0):.2f}")
        print(f"   高水平学生: {metrics.get('high_performers', 0)} 人")
        print(f"   困难学生: {metrics.get('struggling_students', 0)} 人")
    
    print("\n✅ 集成仿真测试通过!\n")


if __name__ == "__main__":
    print("\n🧪 Phase 3 仿真引擎测试套件\n")
    
    try:
        test_oasis_adapter()
        test_intervention_engine()
        test_education_env()
        test_integrated_simulation()
        
        print("=" * 70)
        print("🎉 所有 Phase 3 测试通过!")
        print("=" * 70)
        print("\n✨ Phase 3 核心功能验证成功!")
        print("   - ✅ OasisAdapter (OASIS 仿真适配器)")
        print("   - ✅ InterventionEngine (教学干预引擎)")
        print("   - ✅ EducationEnv (虚拟课堂环境)")
        print("   - ✅ 集成仿真流程")
        print("\n📖 下一步: Phase 4 - 服务层封装\n")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
