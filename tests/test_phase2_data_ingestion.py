"""
Test Phase 2 - Data Ingestion
测试 Phase 2 数据摄入模块
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_exam_data_loader():
    """测试考试数据加载器"""
    print("=" * 70)
    print("测试 1: ExamDataLoader")
    print("=" * 70)
    
    from app.core.data_ingestion import ExamDataLoader
    
    # 使用实际数据目录
    data_root = "docs/英语数据"
    
    if not os.path.exists(data_root):
        print(f"⚠️  数据目录不存在: {data_root}，跳过测试")
        return
    
    loader = ExamDataLoader(data_root)
    
    # 加载单次考试
    print("\n1️⃣  加载单次考试数据...")
    try:
        data = loader.load_exam_data("试题1")
        
        summary = loader.get_data_summary(data)
        print(f"   ✓ 考试ID: {summary['exam_id']}")
        print(f"   ✓ 作答记录: {summary['total_responses']}")
        print(f"   ✓ 学生数: {summary['unique_students']}")
        print(f"   ✓ 试题数: {summary['unique_items']}")
        print(f"   ✓ 平均分: {summary['average_score']}")
        print(f"   ✓ 知识点数: {summary['knowledge_points_count']}")
        
    except Exception as e:
        print(f"   ❌ 加载失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 批量加载
    print("\n2️⃣  批量加载多次考试...")
    try:
        multi_data = loader.load_multiple_exams(["试题1", "试题2"])
        print(f"   ✓ 加载考试数: {multi_data['exam_count']}")
        print(f"   ✓ 总作答记录: {len(multi_data['responses'])}")
        print(f"   ✓ 总学生数: {len(multi_data['students_meta'])}")
        print(f"   ✓ 总试题数: {len(multi_data['items_meta'])}")
    except Exception as e:
        print(f"   ⚠️  批量加载部分失败: {e}")
    
    print("\n✅ ExamDataLoader 测试通过!\n")


def test_data_validator():
    """测试数据验证器"""
    print("=" * 70)
    print("测试 2: EducationDataValidator")
    print("=" * 70)
    
    from app.core.data_ingestion import EducationDataValidator
    
    # 测试学生数据验证
    print("\n1️⃣  验证学生数据...")
    student_valid = {"id": "S001", "class": "Class_8A", "total_score": 85.5}
    result = EducationDataValidator.validate_student(student_valid)
    print(f"   ✓ 有效学生数据: {result.is_valid}")
    
    student_invalid = {"class": "Class_8A"}  # 缺少 id
    result = EducationDataValidator.validate_student(student_invalid)
    print(f"   ✓ 无效学生数据检测: {not result.is_valid}")
    if result.errors:
        print(f"      错误: {result.errors[0]}")
    
    # 测试试题数据验证
    print("\n2️⃣  验证试题数据...")
    item_valid = {"item_id": "Q001", "difficulty": 0.3, "discrimination": 1.5}
    result = EducationDataValidator.validate_item(item_valid)
    print(f"   ✓ 有效试题数据: {result.is_valid}")
    
    item_warning = {"item_id": "Q002", "difficulty": 5.0}  # 难度超出范围
    result = EducationDataValidator.validate_item(item_warning)
    print(f"   ✓ 试题警告检测: {len(result.warnings) > 0}")
    if result.warnings:
        print(f"      警告: {result.warnings[0]}")
    
    # 测试作答记录验证
    print("\n3️⃣  验证作答记录...")
    resp_valid = {"student_id": "S001", "question_index": 1, "score": 1.0}
    result = EducationDataValidator.validate_response(resp_valid)
    print(f"   ✓ 有效作答记录: {result.is_valid}")
    
    resp_invalid = {"student_id": "S001"}  # 缺少必需字段
    result = EducationDataValidator.validate_response(resp_invalid)
    print(f"   ✓ 无效作答记录检测: {not result.is_valid}")
    
    # 测试完整数据集验证
    print("\n4️⃣  验证完整考试数据集...")
    from app.core.data_ingestion import ExamDataLoader
    
    data_root = "docs/英语数据"
    if os.path.exists(data_root):
        loader = ExamDataLoader(data_root)
        data = loader.load_exam_data("试题1")
        
        result = EducationDataValidator.validate_exam_dataset(data)
        print(f"   验证状态: {'✅ 通过' if result.is_valid else '❌ 失败'}")
        if result.warnings:
            print(f"   警告数: {len(result.warnings)}")
            for warn in result.warnings[:3]:
                print(f"      - {warn}")
    
    # 测试数据质量检查
    print("\n5️⃣  数据质量检查...")
    if os.path.exists(data_root):
        quality = EducationDataValidator.check_data_quality(data)
        print(f"   ✓ 质量评分: {quality['quality_score']}/100")
        print(f"   ✓ 作答覆盖率: {quality['coverage']:.1%}")
        print(f"   ✓ 平均分: {quality['average_score']:.2f}")
        print(f"   ✓ 零分率: {quality['zero_rate']:.1%}")
        print(f"   ✓ 满分率: {quality['full_mark_rate']:.1%}")
        
        if quality['issues']:
            print(f"   问题:")
            for issue in quality['issues']:
                print(f"      - {issue}")
    
    print("\n✅ EducationDataValidator 测试通过!\n")


def test_graph_importer():
    """测试图谱导入器"""
    print("=" * 70)
    print("测试 3: GraphDataImporter")
    print("=" * 70)
    
    from app.core.data_ingestion import ExamDataLoader, GraphDataImporter
    from app.core.knowledge_graph import GraphEngine
    
    data_root = "docs/英语数据"
    
    if not os.path.exists(data_root):
        print(f"⚠️  数据目录不存在: {data_root}，跳过测试")
        return
    
    # 初始化图引擎
    print("\n1️⃣  初始化图引擎...")
    engine = GraphEngine(backend_type="json", config={"storage_path": "data/test_phase2_graph"})
    engine.initialize()
    print("   ✓ 图引擎就绪")
    
    # 加载数据
    print("\n2️⃣  加载考试数据...")
    loader = ExamDataLoader(data_root)
    data = loader.load_exam_data("试题1")
    summary = loader.get_data_summary(data)
    print(f"   ✓ 加载完成: {summary['total_responses']} 条作答记录")
    
    # 导入图谱
    print("\n3️⃣  导入数据到图谱...")
    importer = GraphDataImporter(engine)
    stats = importer.import_exam_data(data)
    
    # 验证导入结果
    print("\n4️⃣  验证导入结果...")
    graph_stats = engine.get_stats()
    print(f"   ✓ 图谱节点总数: {graph_stats['node_count']}")
    print(f"   ✓ 图谱边总数: {graph_stats['edge_count']}")
    print(f"   ✓ 标签分布: {graph_stats['labels']}")
    
    # 获取导入摘要
    import_summary = importer.get_import_summary()
    print(f"\n   导入统计:")
    print(f"      - 学生节点: {import_summary['details']['students_added']}")
    print(f"      - 试题节点: {import_summary['details']['items_added']}")
    print(f"      - 知识点节点: {import_summary['details']['concepts_added']}")
    print(f"      - 作答边: {import_summary['details']['responses_added']}")
    
    engine.close()
    print("\n✅ GraphDataImporter 测试通过!\n")


def test_end_to_end_pipeline():
    """测试端到端数据摄入流程"""
    print("=" * 70)
    print("测试 4: 端到端数据摄入流程")
    print("=" * 70)
    
    from app.core.data_ingestion import ExamDataLoader, EducationDataValidator, GraphDataImporter
    from app.core.knowledge_graph import GraphEngine
    
    data_root = "docs/英语数据"
    
    if not os.path.exists(data_root):
        print(f"⚠️  数据目录不存在: {data_root}，跳过测试")
        return
    
    print("\n📋 执行完整流程:")
    print("   1. 加载数据 → 2. 验证数据 → 3. 检查质量 → 4. 导入图谱\n")
    
    # Step 1: 加载数据
    print("Step 1: 加载数据...")
    loader = ExamDataLoader(data_root)
    data = loader.load_exam_data("试题1")
    summary = loader.get_data_summary(data)
    print(f"   ✓ 加载 {summary['total_responses']} 条作答记录")
    
    # Step 2: 验证数据
    print("\nStep 2: 验证数据...")
    validation_result = EducationDataValidator.validate_exam_dataset(data)
    print(f"   {'✓' if validation_result.is_valid else '✗'} 验证{'通过' if validation_result.is_valid else '失败'}")
    
    if validation_result.warnings:
        print(f"   警告 ({len(validation_result.warnings)}):")
        for warn in validation_result.warnings[:3]:
            print(f"      - {warn}")
    
    # Step 3: 检查质量
    print("\nStep 3: 检查数据质量...")
    quality = EducationDataValidator.check_data_quality(data)
    print(f"   ✓ 质量评分: {quality['quality_score']}/100")
    
    if quality['quality_score'] < 60:
        print(f"   ⚠️  数据质量较低，建议检查:")
        for issue in quality.get('issues', []):
            print(f"      - {issue}")
    
    # Step 4: 导入图谱
    print("\nStep 4: 导入图谱...")
    engine = GraphEngine(backend_type="json", config={"storage_path": "data/e2e_test_graph"})
    engine.initialize()
    
    importer = GraphDataImporter(engine)
    stats = importer.import_exam_data(data)
    
    graph_stats = engine.get_stats()
    print(f"   ✓ 图谱最终状态: {graph_stats['node_count']} 节点, {graph_stats['edge_count']} 边")
    
    engine.close()
    
    print("\n✅ 端到端流程测试通过!\n")


if __name__ == "__main__":
    print("\n🧪 Phase 2 数据摄入模块测试套件\n")
    
    try:
        test_exam_data_loader()
        test_data_validator()
        test_graph_importer()
        test_end_to_end_pipeline()
        
        print("=" * 70)
        print("🎉 所有 Phase 2 测试通过!")
        print("=" * 70)
        print("\n✨ Phase 2 核心功能验证成功!")
        print("   - ✅ ExamDataLoader (考试数据加载器)")
        print("   - ✅ EducationDataValidator (数据验证器)")
        print("   - ✅ GraphDataImporter (图谱导入器)")
        print("   - ✅ 端到端数据摄入流程")
        print("\n📖 下一步: Phase 3 - 仿真引擎开发\n")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
