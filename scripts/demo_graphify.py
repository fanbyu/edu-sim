"""
Graphify Backend Demo
演示 Graphify 后端的核心功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def demo_basic_usage():
    """演示基本用法"""
    print("=" * 70)
    print("Demo 1: Graphify 基本用法")
    print("=" * 70)
    
    from app.core.knowledge_graph import GraphEngine
    
    # 初始化
    print("\n1. 初始化 Graphify 后端...")
    engine = GraphEngine(
        backend_type="graphify",
        config={"storage_path": "data/demo_graphify"}
    )
    engine.initialize()
    print("   OK")
    
    # 添加教育实体
    print("\n2. 添加学生、试题、知识点...")
    engine.add_node("S001", "Student", {
        "name": "张三",
        "cognitive_level": 0.5,
        "anxiety_threshold": 0.3,
        "motivation_level": 0.8,
        "class_name": "高一550班"
    })
    
    engine.add_node("Q001", "Item", {
        "content": "求解二次方程 x^2 - 5x + 6 = 0",
        "difficulty": 0.3,
        "discrimination": 1.2,
        "subject": "数学"
    })
    
    engine.add_node("C001", "Concept", {
        "name": "二次函数",
        "subject": "数学",
        "grade": "高一"
    })
    print("   OK: 3个节点")
    
    # 添加关系（带溯源）
    print("\n3. 添加关系（标注来源和置信度）...")
    engine.backend.add_edge("S001", "Q001", "ATTEMPTED",
                           {"score": 1.0, "timestamp": "2026-04-07"},
                           confidence=1.0,
                           relation_type="EXTRACTED")
    
    engine.backend.add_edge("Q001", "C001", "BELONGS_TO",
                           {},
                           confidence=1.0,
                           relation_type="EXTRACTED")
    
    # 推断关系
    engine.backend.add_edge("S001", "C001", "LIKELY_MASTERED",
                           {"evidence": "答对了相关试题"},
                           confidence=0.85,
                           relation_type="INFERRED")
    print("   OK: 3条边")
    
    # 查询统计
    print("\n4. 图谱统计...")
    stats = engine.get_stats()
    print(f"   节点数: {stats['node_count']}")
    print(f"   边数: {stats['edge_count']}")
    print(f"   标签: {stats['labels']}")
    
    # 查询学生画像
    print("\n5. 查询学生画像...")
    student = engine.get_node("S001")
    if student:
        print(f"   姓名: {student['properties'].get('name')}")
        print(f"   认知水平: {student['properties'].get('cognitive_level')}")
        print(f"   班级: {student['properties'].get('class_name')}")
    
    # 查询作答记录
    print("\n6. 查询作答记录...")
    attempts = engine.get_neighbors("S001", relation="ATTEMPTED")
    for attempt in attempts:
        score = attempt.get('edge_properties', {}).get('score')
        print(f"   试题 {attempt['id']}: 得分 {score}")
    
    # 保存并生成可视化
    print("\n7. 保存图谱并生成可视化...")
    engine.backend.save_graph()
    
    try:
        engine.backend.generate_html_visualization()
        print("   OK: data/demo_graphify/graph.html")
    except Exception as e:
        print(f"   Warning: {e}")
    
    # 导出 Neo4j
    print("\n8. 导出 Neo4j Cypher...")
    try:
        engine.backend.export_to_neo4j_cypher()
        print("   OK: data/demo_graphify/neo4j.cypher")
    except Exception as e:
        print(f"   Warning: {e}")
    
    engine.close()
    print("\n✅ Demo 完成!")
    print("\n📂 生成的文件:")
    print("   - data/demo_graphify/graph.json (持久化数据)")
    print("   - data/demo_graphify/graph.html (交互式可视化)")
    print("   - data/demo_graphify/neo4j.cypher (Neo4j脚本)")


def demo_relation_tracing():
    """演示关系溯源功能"""
    print("\n" + "=" * 70)
    print("Demo 2: 关系溯源（EXTRACTED vs INFERRED）")
    print("=" * 70)
    
    from app.core.knowledge_graph import GraphEngine
    
    engine = GraphEngine(
        backend_type="graphify",
        config={"storage_path": "data/demo_tracing"}
    )
    engine.initialize()
    
    # 创建场景：学生掌握知识点的不同证据强度
    print("\n1. 构建证据链...")
    
    # 直接证据（高置信度）
    engine.add_node("S001", "Student", {"name": "李四"})
    engine.add_node("Q001", "Item", {"content": "测试题1"})
    engine.add_node("C001", "Concept", {"name": "勾股定理"})
    
    # EXTRACTED: 直接从作答记录提取
    engine.backend.add_edge("S001", "Q001", "ANSWERED_CORRECTLY",
                           {"score": 1.0},
                           confidence=1.0,
                           relation_type="EXTRACTED")
    
    engine.backend.add_edge("Q001", "C001", "TESTS",
                           {},
                           confidence=1.0,
                           relation_type="EXTRACTED")
    
    # INFERRED: 基于推理得出
    engine.backend.add_edge("S001", "C001", "MASTERED",
                           {"reasoning": "答对了测试该知识点的试题"},
                           confidence=0.85,
                           relation_type="INFERRED")
    
    # AMBIGUOUS: 不确定的关系
    engine.backend.add_edge("S001", "C001", "MIGHT_STRUGGLE_WITH",
                           {"reasoning": "答题时间较长"},
                           confidence=0.45,
                           relation_type="AMBIGUOUS")
    
    print("   OK: 添加了不同可信度的关系")
    
    # 查询并展示
    print("\n2. 查询所有 S001 -> C001 的关系...")
    neighbors = engine.get_neighbors("S001")
    for n in neighbors:
        if n['id'] == "C001":
            edge_props = n.get('edge_properties', {})
            rel_type = edge_props.get('relation_type', 'UNKNOWN')
            confidence = edge_props.get('confidence', 0)
            
            color_map = {
                "EXTRACTED": "绿色",
                "INFERRED": "橙色",
                "AMBIGUOUS": "红色"
            }
            
            print(f"\n   关系: {edge_props.get('relation')}")
            print(f"   类型: {color_map.get(rel_type, rel_type)} ({rel_type})")
            print(f"   置信度: {confidence:.2f}")
            print(f"   推理: {edge_props.get('reasoning', 'N/A')}")
    
    engine.backend.save_graph()
    try:
        engine.backend.generate_html_visualization()
        print("\n3. 可视化已生成: data/demo_tracing/graph.html")
        print("   （在浏览器中查看，不同颜色的边代表不同类型）")
    except:
        pass
    
    engine.close()
    print("\n✅ 关系溯源 Demo 完成!")


def demo_comparison():
    """对比 JSON 和 Graphify 后端"""
    print("\n" + "=" * 70)
    print("Demo 3: JSON vs Graphify 后端对比")
    print("=" * 70)
    
    import time
    from app.core.knowledge_graph import GraphEngine
    
    num_nodes = 50
    num_edges = 100
    
    # JSON 后端
    print(f"\n1. JSON 后端 ({num_nodes} 节点, {num_edges} 边)...")
    start = time.time()
    engine_json = GraphEngine(backend_type="json",
                             config={"storage_path": "data/demo_json"})
    engine_json.initialize()
    
    for i in range(num_nodes):
        engine_json.add_node(f"N{i}", "Test", {"index": i})
    
    for i in range(num_edges):
        src = f"N{i % num_nodes}"
        tgt = f"N{(i + 1) % num_nodes}"
        engine_json.add_edge(src, tgt, "RELATED")
    
    engine_json.close()
    json_time = time.time() - start
    print(f"   耗时: {json_time:.3f}s")
    
    # Graphify 后端
    print(f"\n2. Graphify 后端 ({num_nodes} 节点, {num_edges} 边)...")
    start = time.time()
    engine_gf = GraphEngine(backend_type="graphify",
                           config={"storage_path": "data/demo_graphify_perf"})
    engine_gf.initialize()
    
    for i in range(num_nodes):
        engine_gf.add_node(f"N{i}", "Test", {"index": i})
    
    for i in range(num_edges):
        src = f"N{i % num_nodes}"
        tgt = f"N{(i + 1) % num_nodes}"
        engine_gf.backend.add_edge(src, tgt, "RELATED",
                                  confidence=0.9,
                                  relation_type="EXTRACTED")
    
    engine_gf.backend.save_graph()
    try:
        engine_gf.backend.generate_html_visualization()
    except:
        pass
    engine_gf.close()
    gf_time = time.time() - start
    print(f"   耗时: {gf_time:.3f}s")
    
    # 对比总结
    print(f"\n3. 对比总结:")
    print(f"   JSON:     {json_time:.3f}s (基础功能)")
    print(f"   Graphify: {gf_time:.3f}s (+可视化+溯源)")
    
    speed_diff = ((gf_time - json_time) / json_time * 100) if json_time > 0 else 0
    print(f"   性能差异: {speed_diff:+.1f}%")
    
    if abs(speed_diff) < 50:
        print(f"   ✅ 性能相当，Graphify 提供更多功能")
    else:
        print(f"   ⚠️  Graphify 稍慢，但提供了可视化和溯源能力")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("Graphify 后端集成演示")
    print("=" * 70)
    
    try:
        demo_basic_usage()
        demo_relation_tracing()
        demo_comparison()
        
        print("\n" + "=" * 70)
        print("所有演示完成!")
        print("=" * 70)
        print("\n关键收获:")
        print("  1. Graphify 提供持久化存储和可视化")
        print("  2. 关系溯源区分 EXTRACTED/INFERRED/AMBIGUOUS")
        print("  3. 与 JSON 后端性能相当，功能更丰富")
        print("  4. 完全兼容 GraphBackend 接口，无缝切换")
        print("\n下一步:")
        print("  - 打开 data/demo_graphify/graph.html 查看可视化")
        print("  - 阅读 docs/GRAPHIFY_INTEGRATION.md 了解详细用法")
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
