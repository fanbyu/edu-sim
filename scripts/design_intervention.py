import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def design_intervention_experiment():
    print("--- Edu-Sim 干预实验设计程序 ---")
    
    # 1. 加载图谱数据
    graph_path = "data/graphs/edu_complete_graph_v2"
    with open(os.path.join(graph_path, "nodes.json"), "r", encoding="utf-8") as f:
        nodes = json.load(f)

    students = [n for n in nodes if n['label'] == 'Student']
    
    # 2. 筛选目标群体：认知能力低于 -0.5 的学生
    target_students = [s for s in students if s['attributes'].get('cognitive_level', 0) < -0.5]
    print(f"[正在筛选] 发现 {len(target_students)} 名需要重点关注的学生 (能力值 < -0.5)")

    # 3. 定义干预方案
    intervention_plan = {
        "name": "Reading Comprehension Boost",
        "description": "针对低能力值学生的专项阅读辅导",
        "strategies": {
            "heuristic": {
                "desc": "启发式教学：通过鼓励和引导降低焦虑",
                "effect": {"anxiety_threshold": -0.1, "motivation_level": +0.15}
            },
            "direct": {
                "desc": "直接讲授：高强度训练提升熟练度",
                "effect": {"cognitive_level": +0.2, "anxiety_threshold": +0.05}
            }
        }
    }

    print(f"\n[实验方案详情]")
    print(f"  - 方案名称: {intervention_plan['name']}")
    print(f"  - 涉及学生数: {len(target_students)}")
    
    # 4. 模拟干预效果（预演）
    print(f"\n[预演干预效果 - 以前3名学生为例]")
    for student in target_students[:3]:
        sid = student['id']
        original_theta = student['attributes']['cognitive_level']
        
        # 假设采用启发式教学
        new_anxiety = student['attributes']['anxiety_threshold'] + intervention_plan['strategies']['heuristic']['effect']['anxiety_threshold']
        new_motivation = student['attributes']['motivation_level'] + intervention_plan['strategies']['heuristic']['effect']['motivation_level']
        
        print(f"  -> Student_{sid}:")
        print(f"     原始状态: 能力={original_theta:.2f}, 焦虑={student['attributes']['anxiety_threshold']:.2f}")
        print(f"     干预后:   焦虑={new_anxiety:.2f}, 动机={new_motivation:.2f}")

    # 5. 保存实验配置
    config_path = os.path.join(graph_path, "intervention_config.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(intervention_plan, f, ensure_ascii=False, indent=2)

    print(f"\n--- 实验设计完成！ ---")
    print(f"配置文件已保存至: {config_path}")
    print("下一步将基于此配置运行平行仿真。")

if __name__ == "__main__":
    design_intervention_experiment()
