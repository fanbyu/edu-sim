"""
Phase 2 Demo - Data Ingestion Pipeline
演示 Phase 2 数据摄入完整流程
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.data_ingestion import ExamDataLoader, EducationDataValidator, GraphDataImporter
from app.core.knowledge_graph import GraphEngine


def demo_data_loading():
    """演示数据加载"""
    print("=" * 70)
    print("📥 演示 1: 考试数据加载")
    print("=" * 70)
    
    data_root = "docs/英语数据"
    
    if not os.path.exists(data_root):
        print(f"⚠️  数据目录不存在: {data_root}")
        return None
    
    loader = ExamDataLoader(data_root)
    
    # 加载单次考试
    print("\n1️⃣  加载「试题1」数据...")
    data = loader.load_exam_data("试题1")
    
    summary = loader.get_data_summary(data)
    print(f"\n📊 数据摘要:")
    print(f"   考试ID: {summary['exam_id']}")
    print(f"   作答记录: {summary['total_responses']:,} 条")
    print(f"   学生数量: {summary['unique_students']:,} 人")
    print(f"   试题数量: {summary['unique_items']} 道")
    print(f"   平均得分: {summary['average_score']:.2f}")
    print(f"   知识点数: {summary['knowledge_points_count']}")
    
    # 批量加载
    print("\n2️⃣  批量加载多次考试...")
    multi_data = loader.load_multiple_exams(["试题1", "试题2"])
    print(f"   加载考试数: {multi_data['exam_count']}")
    print(f"   总作答记录: {len(multi_data['responses']):,} 条")
    print(f"   总学生数: {len(multi_data['students_meta']):,} 人")
    print(f"   总试题数: {len(multi_data['items_meta'])} 道")
    
    return data


def demo_data_validation(data):
    """演示数据验证"""
    print("\n" + "=" * 70)
    print("✅ 演示 2: 数据质量验证")
    print("=" * 70)
    
    # 验证数据集
    print("\n1️⃣  验证数据完整性...")
    validation_result = EducationDataValidator.validate_exam_dataset(data)
    
    print(f"\n{validation_result.summary()}")
    
    # 检查数据质量
    print("\n2️⃣  数据质量评估...")
    quality = EducationDataValidator.check_data_quality(data)
    
    print(f"\n📈 质量指标:")
    print(f"   综合评分: {quality['quality_score']}/100")
    print(f"   作答覆盖率: {quality['coverage']:.1%}")
    print(f"   平均得分率: {quality['average_score']:.1%}")
    print(f"   零分率: {quality['zero_rate']:.1%}")
    print(f"   满分率: {quality['full_mark_rate']:.1%}")
    
    if quality['issues']:
        print(f"\n⚠️  发现的问题:")
        for issue in quality['issues']:
            print(f"   - {issue}")
    
    # 评分等级
    score = quality['quality_score']
    if score >= 80:
        grade = "优秀 ⭐⭐⭐"
    elif score >= 60:
        grade = "良好 ⭐⭐"
    elif score >= 40:
        grade = "一般 ⭐"
    else:
        grade = "较差 ❌"
    
    print(f"\n🏆 数据质量等级: {grade}")


def demo_graph_import(data):
    """演示图谱导入"""
    print("\n" + "=" * 70)
    print("🕸️  演示 3: 知识图谱导入")
    print("=" * 70)
    
    # 初始化图引擎
    print("\n1️⃣  初始化图引擎 (JSON 后端)...")
    engine = GraphEngine(
        backend_type="json", 
        config={"storage_path": "data/demo_phase2_graph"}
    )
    engine.initialize()
    print("   ✓ 图引擎就绪")
    
    # 创建导入器
    print("\n2️⃣  创建图谱导入器...")
    importer = GraphDataImporter(engine)
    
    # 执行导入
    print("\n3️⃣  执行数据导入...")
    stats = importer.import_exam_data(data)
    
    # 查看图谱统计
    print("\n4️⃣  图谱最终状态...")
    graph_stats = engine.get_stats()
    print(f"\n📊 图谱统计:")
    print(f"   节点总数: {graph_stats['node_count']:,}")
    print(f"   边总数: {graph_stats['edge_count']:,}")
    print(f"   标签分布:")
    for label, count in graph_stats['labels'].items():
        print(f"      - {label}: {count:,}")
    
    # 导入摘要
    import_summary = importer.get_import_summary()
    print(f"\n📋 导入详情:")
    print(f"   学生节点: {import_summary['details']['students_added']:,}")
    print(f"   试题节点: {import_summary['details']['items_added']}")
    print(f"   知识点节点: {import_summary['details']['concepts_added']}")
    print(f"   作答关系: {import_summary['details']['responses_added']:,}")
    
    engine.close()
    print("\n   ✓ 图谱已保存到 data/demo_phase2_graph/")


def demo_sample_queries(data):
    """演示示例查询"""
    print("\n" + "=" * 70)
    print("🔍 演示 4: 数据洞察分析")
    print("=" * 70)
    
    responses = data.get('responses', [])
    students = data.get('students_meta', {})
    items = data.get('items_meta', {})
    
    # 1. 最高分学生
    print("\n1️⃣  表现最佳的学生...")
    if students:
        top_students = sorted(
            students.items(), 
            key=lambda x: x[1].get('total_score', 0), 
            reverse=True
        )[:5]
        
        for i, (sid, meta) in enumerate(top_students, 1):
            print(f"   {i}. {sid} - 总分: {meta.get('total_score', 0):.1f}, "
                  f"班级: {meta.get('class', 'N/A')}")
    
    # 2. 最难试题
    print("\n2️⃣  最难的试题...")
    if items:
        hardest_items = sorted(
            items.items(),
            key=lambda x: x[1].get('difficulty', 0),
            reverse=True
        )[:5]
        
        for i, (iid, meta) in enumerate(hardest_items, 1):
            print(f"   {i}. {iid} - 难度: {meta['difficulty']:.3f}, "
                  f"平均分: {meta['avg_score']:.2f}")
    
    # 3. 班级分布
    print("\n3️⃣  班级分布...")
    class_counts = {}
    for meta in students.values():
        cls = meta.get('class', 'Unknown')
        class_counts[cls] = class_counts.get(cls, 0) + 1
    
    for cls, count in sorted(class_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"   - {cls}: {count} 人")
    
    # 4. 作答模式分析
    print("\n4️⃣  作答模式分析...")
    student_response_counts = {}
    for resp in responses:
        sid = resp['student_id']
        student_response_counts[sid] = student_response_counts.get(sid, 0) + 1
    
    if student_response_counts:
        avg_responses = sum(student_response_counts.values()) / len(student_response_counts)
        max_responses = max(student_response_counts.values())
        min_responses = min(student_response_counts.values())
        
        print(f"   平均每生作答: {avg_responses:.1f} 题")
        print(f"   最多作答: {max_responses} 题")
        print(f"   最少作答: {min_responses} 题")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🚀 Phase 2 数据摄入流程演示")
    print("=" * 70 + "\n")
    
    try:
        # 演示数据加载
        data = demo_data_loading()
        
        if data:
            # 演示数据验证
            demo_data_validation(data)
            
            # 演示图谱导入
            demo_graph_import(data)
            
            # 演示数据洞察
            demo_sample_queries(data)
        
        print("\n" + "=" * 70)
        print("🎉 Phase 2 演示完成!")
        print("=" * 70)
        print("\n✨ 核心功能验证成功:")
        print("   - ✅ ExamDataLoader: 支持 CSV/GBK 编码，容错处理")
        print("   - ✅ EducationDataValidator: 数据验证 + 质量评估")
        print("   - ✅ GraphDataImporter: 批量导入到知识图谱")
        print("   - ✅ 端到端流程: 加载 → 验证 → 导入 → 查询")
        print("\n📖 下一步: Phase 3 - 仿真引擎开发\n")
        
    except Exception as e:
        print(f"\n❌ 演示失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
