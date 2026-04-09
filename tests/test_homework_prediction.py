"""
Test Homework Prediction - 作业前置评估端到端测试
模拟老师上传试题并观察系统如何结合学情给出预测。
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.knowledge_graph import GraphEngine
from app.core.agent_modeling import StudentAgent
from app.services import GraphService, PredictionService
from app.services.item_parser import ItemParser
from datetime import datetime, timedelta

def mock_student_history():
    """模拟带有历史记录的学生数据"""
    students = [
        StudentAgent(student_id="S001", name="小明", cognitive_level=0.5, class_name="Class_A"),
        StudentAgent(student_id="S002", name="小红", cognitive_level=-0.8, class_name="Class_A"),
        StudentAgent(student_id="S003", name="小刚", cognitive_level=1.2, class_name="Class_A"),
    ]
    
    # 为 S001 添加一周前关于“二次函数”的低分记录（模拟遗忘和挫败感）
    students[0].record_interaction("item_old_01", "二次函数", 0.3)
    # 手动修改日期以模拟过去的时间
    students[0].interaction_history[-1]['date'] = (datetime.now() - timedelta(days=7)).isoformat()
    
    # 为 S002 添加昨天关于“二次函数”的高分记录（模拟短期记忆加成）
    students[1].record_interaction("item_old_02", "二次函数", 0.9)
    students[1].interaction_history[-1]['date'] = (datetime.now() - timedelta(days=1)).isoformat()
    
    return students

def main():
    print("=" * 70)
    print("🧪 Edu-Sim 作业前置评估模拟测试")
    print("=" * 70)
    
    # 1. 初始化图谱与服务
    print("\n1️⃣  正在初始化教育知识图谱...")
    engine = GraphEngine(backend_type="json", config={"storage_path": "data/test_graphs"})
    engine.initialize()
    graph_service = GraphService(engine)
    prediction_service = PredictionService(graph_service)
    
    # 2. 注入模拟学生数据
    print("2️⃣  正在加载班级学情快照 (Class_A)...")
    students = mock_student_history()
    for s in students:
        # 在实际系统中，这些数据会存入图谱节点属性
        graph_service.engine.add_node(s.student_id, "Student", s.to_dict())
    
    # 3. 模拟老师上传试题
    sample_item_text = """
    题目：已知二次函数 y = x^2 - 4x + 3。
    (1) 求该函数的顶点坐标和对称轴。
    (2) 当 x 取何值时，y 有最小值？最小值是多少？
    """
    print(f"\n3️⃣  老师上传了一道数学题:\n{sample_item_text}")
    
    # 4. 试题解析
    print("\n4️⃣  系统正在利用 LLM 解析试题特征...")
    parser = ItemParser()
    # 为了测试不依赖网络，我们这里手动构造一个解析结果，或者你可以取消注释使用真实 LLM
    item_features = {
        "difficulty": 0.5,          # 中等难度
        "discrimination": 1.2,      # 区分度良好
        "concepts": ["二次函数"],    # 考察知识点
        "cognitive_level": "applying",
        "psychological_load": 6
    }
    print(f"   ✓ 提取知识点: {item_features['concepts']}")
    print(f"   ✓ 预估难度: {item_features['difficulty']}")
    
    # 5. 执行预测
    print("\n5️⃣  正在进行群智推演 (考虑遗忘曲线与教学进度)...")
    report = prediction_service.predict_homework_impact(
        item_data=item_features,
        target_group="Class_A"
    )
    
    # 6. 展示预测报告
    print(f"\n{'='*50}")
    print(f"📊 作业前置评估报告")
    print(f"{'='*50}")
    if "error" not in report:
        print(f"🎯 综合结论: 【{report['conclusion']}】")
        print(f"👥 覆盖学生: {report['student_count']} 人")
        print(f"📈 预计掌握度增益: {report['metrics']['avg_mastery_gain']:+.4f}")
        print(f"😰 预计焦虑变化: {report['metrics']['avg_anxiety_change']:+.4f}")
        print(f"⚠️  预计不及格率: {report['metrics']['predicted_failure_rate']:.1%}")
        
        if report['recommendations']:
            print(f"\n💡 智能建议:")
            for rec in report['recommendations']:
                print(f"   - {rec}")
    else:
        print(f"❌ 预测出错: {report['error']}")
        
    engine.close()
    print(f"\n✅ 模拟测试完成!")

if __name__ == "__main__":
    main()
