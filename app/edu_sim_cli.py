"""
Edu-Sim CLI
教育仿真系统命令行工具 - 基于新架构的完整功能接口
"""

import argparse
import json
import sys
import os
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

# 设置 UTF-8 编码（Windows 兼容）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.knowledge_graph import GraphEngine
from app.core.data_ingestion import ExamDataLoader, EducationDataValidator, GraphDataImporter
from app.core.agent_modeling import IRTEngine
from app.core.simulation import OasisAdapter, InterventionEngine, EducationEnv
from app.services import GraphService, CalibrationService, PredictionService
from app.services.item_parser import ItemParser


def cmd_predict_homework(args):
    """预测作业/试题对班级的影响"""
    print("=" * 70)
    print("🔮 作业前置评估预测")
    print("=" * 70)
    
    # 初始化组件
    engine = GraphEngine(backend_type=args.backend, config={"storage_path": args.graph_path})
    engine.initialize()
    graph_service = GraphService(engine)
    prediction_service = PredictionService(graph_service)
    item_parser = ItemParser()
    
    try:
        # 1. 解析试题
        print(f"\n1️⃣  正在解析试题...")
        with open(args.item_file, 'r', encoding='utf-8') as f:
            item_text = f.read()
        
        item_features = item_parser.parse_item(item_text, subject=args.subject)
        print(f"   ✓ 难度: {item_features['difficulty']:.2f}")
        print(f"   ✓ 知识点: {', '.join(item_features['concepts'])}")
        
        # 2. 执行预测
        print(f"\n2️⃣  正在推演对 [{args.target_group}] 的影响...")
        report = prediction_service.predict_homework_impact(
            item_data=item_features,
            target_group=args.target_group
        )
        
        if "error" in report:
            print(f"\n❌ 预测失败: {report['error']}")
            return 1
            
        # 3. 输出可视化报告
        console = Console()
        
        # 判定结论颜色
        conclusion_style = "green" if "正向" in report['conclusion'] else "red" if "负向" in report['conclusion'] else "yellow"
        conclusion_text = Text(report['conclusion'], style=conclusion_style)
        
        panel_content = f"[bold]🎯 综合结论:[/bold] {conclusion_text}\n"
        panel_content += f"[bold]👥 覆盖人数:[/bold] {report['student_count']}\n"
        panel_content += f"[bold]📈 预计掌握度增益:[/bold] {report['metrics']['avg_mastery_gain']:+.4f}\n"
        panel_content += f"[bold]😰 预计焦虑变化:[/bold] {report['metrics']['avg_anxiety_change']:+.4f}\n"
        panel_content += f"[bold]⚠️  预计不及格率:[/bold] {report['metrics']['predicted_failure_rate']:.1%}"
        
        console.print(Panel(panel_content, title="📊 作业前置评估报告", border_style="blue"))
        
        if report['recommendations']:
            console.print("\n[bold cyan]💡 智能建议:[/bold cyan]")
            for rec in report['recommendations']:
                console.print(f"  • {rec}")
        
        # 保存 JSON 报告
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"\n💾 报告已保存至: {args.output}")
            
        return 0
        
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

def cmd_load_data(args):
    """加载考试数据到知识图谱"""
    print("=" * 70)
    print("📥 加载考试数据")
    print("=" * 70)
    
    # 初始化组件
    loader = ExamDataLoader(args.data_root)
    engine = GraphEngine(backend_type="json", config={"storage_path": args.graph_path})
    engine.initialize()
    
    graph_service = GraphService(engine)
    importer = GraphDataImporter(engine)
    validator = EducationDataValidator()
    
    try:
        # 加载数据
        print(f"\n1️⃣  加载数据: {args.exam_folder}")
        data = loader.load_exam_data(args.exam_folder)
        summary = loader.get_data_summary(data)
        
        print(f"   ✓ 作答记录: {summary['total_responses']}")
        print(f"   ✓ 学生数: {summary['unique_students']}")
        print(f"   ✓ 试题数: {summary['unique_items']}")
        
        # 验证数据
        print(f"\n2️⃣  验证数据质量...")
        validation = validator.validate_exam_dataset(data)
        quality = validator.check_data_quality(data)
        
        print(f"   验证状态: {'✅ 通过' if validation.is_valid else '❌ 失败'}")
        print(f"   质量评分: {quality['quality_score']}/100")
        
        if quality['issues']:
            print(f"\n⚠️  发现的问题:")
            for issue in quality['issues']:
                print(f"      - {issue}")
        
        # 导入图谱
        print(f"\n3️⃣  导入到知识图谱...")
        stats = importer.import_exam_data(data)
        
        graph_stats = engine.get_stats()
        print(f"\n📊 图谱统计:")
        print(f"   节点总数: {graph_stats['node_count']}")
        print(f"   边总数: {graph_stats['edge_count']}")
        
        print(f"\n✅ 数据加载完成!")
        
    except Exception as e:
        print(f"\n❌ 加载失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        engine.close()
    
    return 0


def cmd_calibrate(args):
    """执行 IRT 参数校准"""
    print("=" * 70)
    print("📐 IRT 参数校准")
    print("=" * 70)
    
    # 初始化组件
    engine = GraphEngine(backend_type="json", config={"storage_path": args.graph_path})
    engine.initialize()
    
    graph_service = GraphService(engine)
    calibration_service = CalibrationService(graph_service)
    
    try:
        # 从图谱加载数据（简化：实际应该从原始数据文件加载）
        print("\n⚠️  注意: 当前版本需要从原始考试数据文件进行校准")
        print("   请使用: edu-sim load-data --data-root <path> --exam-folder <name>")
        print("   然后运行校准流程\n")
        
        # 这里演示如何调用校准服务
        print("💡 示例代码:")
        print("""
from app.core.data_ingestion import ExamDataLoader
from app.services import CalibrationService, GraphService
from app.core.knowledge_graph import GraphEngine

# 1. 加载数据
loader = ExamDataLoader("docs/英语数据")
exam_data = loader.load_exam_data("试题1")

# 2. 初始化服务
engine = GraphEngine(backend_type="json")
engine.initialize()
graph_service = GraphService(engine)
calibration_service = CalibrationService(graph_service)

# 3. 执行校准
report = calibration_service.full_calibration_pipeline(exam_data)
print(f"质量评级: {report['quality_assessment']['overall_rating']}")
        """)
        
    except Exception as e:
        print(f"\n❌ 校准失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        engine.close()
    
    return 0


def cmd_predict(args):
    """预测学生学习表现"""
    print("=" * 70)
    print("🔮 学习表现预测")
    print("=" * 70)
    
    # 初始化组件
    engine = GraphEngine(backend_type="json", config={"storage_path": args.graph_path})
    engine.initialize()
    
    graph_service = GraphService(engine)
    prediction_service = PredictionService(graph_service)
    
    try:
        student_id = args.student_id
        
        # 获取学生信息
        print(f"\n1️⃣  查询学生信息: {student_id}")
        profile = graph_service.get_student_profile(student_id)
        
        if not profile:
            print(f"   ❌ 学生 {student_id} 不存在")
            return 1
        
        print(f"   ✓ 认知水平: {profile['attributes'].get('cognitive_level', 0):.2f}")
        print(f"   ✓ 焦虑阈值: {profile['attributes'].get('anxiety_threshold', 0.5):.2f}")
        print(f"   ✓ 动机水平: {profile['attributes'].get('motivation_level', 0.5):.2f}")
        
        # 推荐干预策略
        print(f"\n2️⃣  推荐最优干预策略...")
        recommendation = prediction_service.recommend_optimal_intervention(student_id)
        
        if "error" not in recommendation:
            print(f"   ✓ 推荐策略: {recommendation['best_strategy']}")
            
            if recommendation['recommendations']:
                print(f"\n   策略排名:")
                for i, rec in enumerate(recommendation['recommendations'][:3], 1):
                    print(f"      {i}. {rec['strategy']}: 得分 {rec['score']:.4f}")
        
        # 预测干预效果
        if args.intervention:
            print(f"\n3️⃣  预测干预效果: {args.intervention}")
            effect = prediction_service.predict_intervention_effect(
                student_id, 
                args.intervention,
                duration_rounds=3
            )
            
            if "error" not in effect:
                print(f"   ✓ 能力提升: Δθ = {effect['improvements']['theta_gain']:.2f}")
                print(f"   ✓ 焦虑降低: Δanxiety = {effect['improvements']['anxiety_reduction']:.2f}")
                print(f"   ✓ 动机提升: Δmotivation = {effect['improvements']['motivation_gain']:.2f}")
        
        print(f"\n✅ 预测完成!")
        
    except Exception as e:
        print(f"\n❌ 预测失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        engine.close()
    
    return 0


def cmd_simulate(args):
    """运行教学仿真"""
    print("=" * 70)
    print("🚀 教学仿真")
    print("=" * 70)
    
    # 初始化组件
    engine = GraphEngine(backend_type="json", config={"storage_path": args.graph_path})
    engine.initialize()
    
    try:
        # 从图谱加载学生和教师
        print("\n1️⃣  从知识图谱加载 Agents...")
        graph_stats = engine.get_stats()
        
        # 构建图数据
        graph_data = {
            "students": [],
            "teachers": [],
            "items": []
        }
        
        # 这里简化处理，实际应该查询图谱获取所有节点
        print(f"   ✓ 图谱节点: {graph_stats['node_count']}")
        print(f"   ✓ 图谱边: {graph_stats['edge_count']}")
        
        # 创建 OASIS 适配器
        print(f"\n2️⃣  初始化 OASIS 仿真器...")
        adapter = OasisAdapter(oasis_config={
            "num_rounds": args.rounds,
            "time_step": 5,
            "parallel": False
        })
        
        # 使用模拟数据（实际应该从图谱加载）
        mock_graph_data = {
            "students": [
                {"id": f"S{i:03d}", "properties": {
                    "cognitive_level": (i - 5) * 0.3,
                    "anxiety_threshold": 0.3 + (i % 3) * 0.2,
                    "motivation_level": 0.5 + (i % 4) * 0.1
                }}
                for i in range(1, 11)
            ],
            "teachers": [
                {"id": "T001", "properties": {"teaching_style": "heuristic"}}
            ]
        }
        
        adapter.initialize_from_graph(mock_graph_data)
        print(f"   ✓ 学生 Agents: {len(adapter.students)}")
        print(f"   ✓ 教师 Agents: {len(adapter.teachers)}")
        
        # 运行仿真
        print(f"\n3️⃣  运行仿真 ({args.rounds} 轮)...")
        intervention = args.intervention if args.intervention else None
        results = adapter.run_simulation(intervention_strategy=intervention)
        
        print(f"\n📊 仿真结果:")
        print(f"   完成轮数: {results['rounds_completed']}")
        print(f"   应用干预: {len(results['interventions_applied'])} 次")
        
        metrics = results['performance_metrics']
        if metrics:
            print(f"\n📈 最终指标:")
            print(f"   平均认知水平: {metrics.get('avg_cognitive_level', 0):.2f}")
            print(f"   平均动机水平: {metrics.get('avg_motivation', 0):.2f}")
            print(f"   平均焦虑阈值: {metrics.get('avg_anxiety', 0):.2f}")
        
        # 导出结果
        if args.output:
            adapter.export_results(args.output)
        
        print(f"\n✅ 仿真完成!")
        
    except Exception as e:
        print(f"\n❌ 仿真失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        engine.close()
    
    return 0


def cmd_query(args):
    """查询知识图谱"""
    print("=" * 70)
    print("🔍 知识图谱查询")
    print("=" * 70)
    
    # 初始化组件
    engine = GraphEngine(backend_type="json", config={"storage_path": args.graph_path})
    engine.initialize()
    
    graph_service = GraphService(engine)
    
    try:
        query_type = args.type
        
        if query_type == "overview":
            # 图谱概览
            print("\n📊 图谱概览:")
            overview = graph_service.get_graph_overview()
            print(f"   节点总数: {overview['total_nodes']}")
            print(f"   边总数: {overview['total_edges']}")
            print(f"   标签分布: {overview['label_distribution']}")
        
        elif query_type == "student" and args.id:
            # 学生画像
            print(f"\n👨‍🎓 学生画像: {args.id}")
            profile = graph_service.get_student_profile(args.id)
            
            if profile:
                print(f"   认知水平: {profile['attributes'].get('cognitive_level', 0):.2f}")
                print(f"   焦虑阈值: {profile['attributes'].get('anxiety_threshold', 0.5):.2f}")
                print(f"   动机水平: {profile['attributes'].get('motivation_level', 0.5):.2f}")
                print(f"   作答记录: {len(profile['attempted_items'])} 条")
            else:
                print(f"   ❌ 学生 {args.id} 不存在")
        
        elif query_type == "class" and args.class_name:
            # 班级统计
            print(f"\n🏫 班级统计: {args.class_name}")
            stats = graph_service.get_class_statistics(args.class_name)
            
            if "error" not in stats:
                print(f"   学生数: {stats['student_count']}")
                print(f"   平均能力: {stats['avg_cognitive_level']:.2f}")
                print(f"   平均焦虑: {stats['avg_anxiety']:.2f}")
                print(f"   平均动机: {stats['avg_motivation']:.2f}")
            else:
                print(f"   ❌ {stats['error']}")
        
        else:
            print("\n⚠️  请指定查询类型和参数")
            print("   示例:")
            print("   edu-sim query --type overview")
            print("   edu-sim query --type student --id S001")
            print("   edu-sim query --type class --class-name Class_A")
        
        print(f"\n✅ 查询完成!")
        
    except Exception as e:
        print(f"\n❌ 查询失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        engine.close()
    
    return 0


def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(
        prog="edu-sim",
        description="Edu-Sim 教育仿真系统 CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 加载数据
  edu-sim load-data --data-root docs/英语数据 --exam-folder 试题1
  
  # 执行校准
  edu-sim calibrate --graph-path data/graphs
  
  # 预测学生表现
  edu-sim predict --student-id S001 --intervention heuristic
  
  # 运行仿真
  edu-sim simulate --rounds 5 --intervention scaffolding
  
  # 查询图谱
  edu-sim query --type overview
  edu-sim query --type student --id S001
  edu-sim query --type class --class-name Class_A
  
  # 预测作业影响
  edu-sim predict-homework --item-file item.txt --target-group Class_A --subject math
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # load-data 命令
    load_parser = subparsers.add_parser("load-data", help="加载考试数据到知识图谱")
    load_parser.add_argument("--data-root", required=True, help="数据根目录")
    load_parser.add_argument("--exam-folder", required=True, help="考试文件夹名称")
    load_parser.add_argument("--graph-path", default="data/graphs", help="图谱存储路径")
    
    # calibrate 命令
    calib_parser = subparsers.add_parser("calibrate", help="执行 IRT 参数校准")
    calib_parser.add_argument("--graph-path", default="data/graphs", help="图谱存储路径")
    
    # predict 命令
    pred_parser = subparsers.add_parser("predict", help="预测学生学习表现")
    pred_parser.add_argument("--student-id", required=True, help="学生ID")
    pred_parser.add_argument("--intervention", help="干预策略类型")
    pred_parser.add_argument("--graph-path", default="data/graphs", help="图谱存储路径")
    
    # predict-homework 命令 (新增)
    hw_parser = subparsers.add_parser("predict-homework", help="预测作业/试题对班级的影响")
    hw_parser.add_argument("--item-file", required=True, help="试题文本文件路径")
    hw_parser.add_argument("--target-group", required=True, help="目标群体 (班级ID或学校ID)")
    hw_parser.add_argument("--subject", default="math", help="学科类型 (math, english...)")
    hw_parser.add_argument("--output", help="JSON 报告输出路径")
    hw_parser.add_argument("--graph-path", default="data/graphs", help="图谱存储路径")
    hw_parser.add_argument("--backend", default="json", choices=["json", "graphify"], help="图谱后端类型")
    
    # simulate 命令
    sim_parser = subparsers.add_parser("simulate", help="运行教学仿真")
    sim_parser.add_argument("--rounds", type=int, default=5, help="仿真轮数")
    sim_parser.add_argument("--intervention", help="干预策略")
    sim_parser.add_argument("--output", help="输出文件路径")
    sim_parser.add_argument("--graph-path", default="data/graphs", help="图谱存储路径")
    
    # query 命令
    query_parser = subparsers.add_parser("query", help="查询知识图谱")
    query_parser.add_argument("--type", required=True, choices=["overview", "student", "class"],
                             help="查询类型")
    query_parser.add_argument("--id", help="学生/试题ID")
    query_parser.add_argument("--class-name", help="班级名称")
    query_parser.add_argument("--graph-path", default="data/graphs", help="图谱存储路径")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # 路由到对应命令
    commands = {
        "load-data": cmd_load_data,
        "calibrate": cmd_calibrate,
        "predict": cmd_predict,
        "predict-homework": cmd_predict_homework,
        "simulate": cmd_simulate,
        "query": cmd_query,
    }
    
    handler = commands.get(args.command)
    if handler:
        return handler(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
