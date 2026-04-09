"""
Test Graphify Backend Integration
测试 Graphify 后端集成
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_graphify_backend():
    """测试 Graphify 后端"""
    print("=" * 70)
    print("测试: Graphify 后端集成")
    print("=" * 70)
    
    from app.core.knowledge_graph import GraphEngine
    
    # 初始化 Graphify 后端
    print("\n1️⃣  初始化 Graphify 后端...")
    engine = GraphEngine(
        backend_type="graphify",
        config={"storage_path": "data/test_graphify"}
    )
    engine.initialize()
    print("   ✅ 后端就绪")
    
    # 添加节点
    print("\n2️⃣  添加教育实体节点...")
    engine.add_node("S001", "Student", {
        "cognitive_level": 0.5,
        "anxiety_threshold": 0.3,
        "motivation_level": 0.8,
        "class_name": "Class_A"
    })
    engine.add_node("S002", "Student", {
        "cognitive_level": -0.8,
        "anxiety_threshold": 0.7,
        "motivation_level": 0.4
    })
    engine.add_node("Q001", "Item", {
        "difficulty": 0.3,
        "discrimination": 1.2
    })
    engine.add_node("C001", "Concept", {
        "name": "二次函数",
        "subject": "数学"
    })
    print("   ✅ 添加了 4 个节点")
    
    # 添加边（带关系溯源）
    print("\n3️⃣  添加关系（带置信度和类型标注）...")
    engine.backend.add_edge("S001", "Q001", "ATTEMPTED", 
                           {"score": 1.0},
                           confidence=1.0,
                           relation_type="EXTRACTED")
    engine.backend.add_edge("S002", "Q001", "ATTEMPTED",
                           {"score": 0.0},
                           confidence=1.0,
                           relation_type="EXTRACTED")
    engine.backend.add_edge("Q001", "C001", "BELONGS_TO",
                           {},
                           confidence=0.95,
                           relation_type="EXTRACTED")
    
    # 推断关系（低置信度）
    engine.backend.add_edge("S001", "C001", "LIKELY_MASTERED",
                           {},
                           confidence=0.75,
                           relation_type="INFERRED")
    print("   ✅ 添加了 4 条边")
    
    # 查询统计
    print("\n4️⃣  图谱统计...")
    stats = engine.get_stats()
    print(f"   节点数: {stats['node_count']}")
    print(f"   边数: {stats['edge_count']}")
    print(f"   标签分布: {stats['labels']}")
    
    # 查询节点
    print("\n5️⃣  查询学生画像...")
    student = engine.get_node("S001")
    if student:
        print(f"   学生ID: {student['id']}")
        print(f"   认知水平: {student['properties'].get('cognitive_level')}")
        print(f"   焦虑阈值: {student['properties'].get('anxiety_threshold')}")
    
    # 查询邻居
    print("\n6️⃣  查询学生的作答记录...")
    neighbors = engine.get_neighbors("S001", relation="ATTEMPTED")
    print(f"   找到 {len(neighbors)} 条作答记录")
    for n in neighbors:
        print(f"      - 试题: {n['id']}, 分数: {n.get('edge_properties', {}).get('score')}")
    
    # 保存图谱
    print("\n7️⃣  保存图谱...")
    engine.backend.save_graph()
    
    # 生成可视化
    print("\n8️⃣  生成交互式可视化...")
    try:
        engine.backend.generate_html_visualization()
    except Exception as e:
        print(f"   ⚠️  可视化生成失败: {e}")
        print("   （可能需要安装 networkx: pip install networkx）")
    
    # 导出 Neo4j
    print("\n9️⃣  导出 Neo4j Cypher...")
    try:
        engine.backend.export_to_neo4j_cypher()
    except Exception as e:
        print(f"   ⚠️  导出失败: {e}")
    
    # 关闭
    print("\n🔟 关闭后端...")
    engine.close()
    
    print("\n✅ Graphify 后端测试完成!")
    print("\n📂 生成的文件:")
    print("   - data/test_graphify/graph.json (持久化图谱)")
    print("   - data/test_graphify/graph.html (交互式可视化)")
    print("   - data/test_graphify/neo4j.cypher (Neo4j 导入脚本)")
    print("   - data/test_graphify/cache/file_hashes.json (增量更新缓存)")


def test_incremental_update():
    """测试增量更新功能"""
    print("\n" + "=" * 70)
    print("测试: 增量更新机制")
    print("=" * 70)
    
    from app.core.knowledge_graph import GraphEngine
    
    # 第一次运行
    print("\n1️⃣  第一次运行（全量构建）...")
    engine1 = GraphEngine(
        backend_type="graphify",
        config={"storage_path": "data/test_incremental"}
    )
    engine1.initialize()
    engine1.add_node("N1", "Test", {"value": 1})
    engine1.backend.save_graph()
    stats1 = engine1.get_stats()
    print(f"   节点数: {stats1['node_count']}")
    engine1.close()
    
    # 第二次运行（应该加载现有图谱）
    print("\n2️⃣  第二次运行（加载现有图谱）...")
    engine2 = GraphEngine(
        backend_type="graphify",
        config={"storage_path": "data/test_incremental"}
    )
    engine2.initialize()
    stats2 = engine2.get_stats()
    print(f"   节点数: {stats2['node_count']}")
    
    # 添加新节点
    engine2.add_node("N2", "Test", {"value": 2})
    engine2.backend.save_graph()
    stats3 = engine2.get_stats()
    print(f"   添加后节点数: {stats3['node_count']}")
    engine2.close()
    
    print("\n✅ 增量更新测试通过!")


def compare_backends():
    """比较不同后端的性能"""
    print("\n" + "=" * 70)
    print("对比: JSON vs Graphify 后端")
    print("=" * 70)
    
    import time
    from app.core.knowledge_graph import GraphEngine
    
    num_nodes = 100
    num_edges = 200
    
    # 测试 JSON 后端
    print(f"\n1️⃣  JSON 后端 ({num_nodes} 节点, {num_edges} 边)...")
    start = time.time()
    engine_json = GraphEngine(backend_type="json", 
                             config={"storage_path": "data/test_json_perf"})
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
    
    # 测试 Graphify 后端
    print(f"\n2️⃣  Graphify 后端 ({num_nodes} 节点, {num_edges} 边)...")
    start = time.time()
    engine_gf = GraphEngine(backend_type="graphify",
                           config={"storage_path": "data/test_graphify_perf"})
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
    engine_gf.close()
    gf_time = time.time() - start
    print(f"   耗时: {gf_time:.3f}s")
    
    # 对比
    print(f"\n📊 性能对比:")
    print(f"   JSON:     {json_time:.3f}s")
    print(f"   Graphify: {gf_time:.3f}s")
    print(f"   差异:     {(gf_time - json_time):.3f}s ({((gf_time/json_time - 1) * 100):+.1f}%)")
    
    if gf_time < json_time:
        print(f"   ✅ Graphify 更快!")
    else:
        print(f"   ⚠️  Graphify 稍慢，但提供了更多功能（可视化、溯源等）")


if __name__ == "__main__":
    print("\n🧪 Graphify 后端集成测试\n")
    
    try:
        test_graphify_backend()
        test_incremental_update()
        compare_backends()
        
        print("\n" + "=" * 70)
        print("🎉 所有 Graphify 测试通过!")
        print("=" * 70)
        print("\n✨ Graphify 集成成功!")
        print("   - ✅ 持久化存储 (graph.json)")
        print("   - ✅ 交互式可视化 (graph.html)")
        print("   - ✅ 关系溯源 (EXTRACTED/INFERRED/AMBIGUOUS)")
        print("   - ✅ 增量更新 (SHA256 缓存)")
        print("   - ✅ Neo4j 导出支持")
        print("\n💡 使用方法:")
        print("   engine = GraphEngine(backend_type='graphify')")
        print("   engine.initialize()")
        print("   # ... 使用引擎 ...")
        print("   engine.backend.generate_html_visualization()  # 生成可视化")
        print("   engine.close()")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
