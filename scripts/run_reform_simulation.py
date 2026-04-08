import sys
import os
import json
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_dynamic_reform_simulation():
    print("--- Edu-Sim 动态改革仿真程序 ---")
    
    # 1. 加载数据
    graph_path = "data/graphs/edu_complete_graph_v2"
    with open(os.path.join(graph_path, "nodes.json"), "r", encoding="utf-8") as f:
        nodes = {n['id']: n for n in json.load(f)}
    with open(os.path.join(graph_path, "edges.json"), "r", encoding="utf-8") as f:
        edges = json.load(f)

    # 2. 建立索引
    class_students = {}
    class_teachers = {}
    for edge in edges:
        if edge['relation'] == 'BELONGS_TO':
            sid, cid = edge['source_id'], edge['target_id']
            if cid not in class_students: class_students[cid] = []
            if sid in nodes: class_students[cid].append(nodes[sid])
        if edge['relation'] == 'TEACHES':
            tid, cid = edge['source_id'], edge['target_id']
            if tid in nodes: class_teachers[cid] = nodes[tid]

    def calculate_efficacy(avg_theta, avg_anxiety, style):
        base_score = 0.5
        if style == "heuristic":
            bonus = 0.2 * (1 - avg_anxiety) + 0.1 * np.exp(-avg_theta**2)
        elif style == "direct":
            bonus = 0.25 * avg_theta - 0.15 * avg_anxiety
        else:
            bonus = 0.15 * (1 - avg_theta) + 0.2 * (1 - avg_anxiety)
        return base_score + bonus

    # 3. 仿真前状态
    total_pre_efficacy = 0
    reform_count = 0
    
    print(f"\n{'班级名称':<15} {'原风格':<10} {'新风格':<10} {'效能变化':<10}")
    print("-" * 50)

    for cid, students in class_students.items():
        if not students: continue
        
        thetas = [s['attributes'].get('cognitive_level', 0) for s in students]
        anxieties = [s['attributes'].get('anxiety_threshold', 0.5) for s in students]
        avg_theta, avg_anxiety = np.mean(thetas), np.mean(anxieties)

        teacher = class_teachers.get(cid)
        if not teacher: continue
        
        current_style = teacher['attributes']['teaching_style']
        styles = ["heuristic", "direct", "facilitator"]
        best_style = max(styles, key=lambda s: calculate_efficacy(avg_theta, avg_anxiety, s))
        
        pre_eff = calculate_efficacy(avg_theta, avg_anxiety, current_style)
        post_eff = calculate_efficacy(avg_theta, avg_anxiety, best_style)
        total_pre_efficacy += pre_eff

        if current_style != best_style:
            # 执行改革：更新教师属性
            teacher['attributes']['teaching_style'] = best_style
            reform_count += 1
            print(f"{nodes[cid]['name']:<12} {current_style:<10} {best_style:<10} +{post_eff - pre_eff:.4f}")

    # 4. 仿真后状态
    total_post_efficacy = 0
    for cid, students in class_students.items():
        if not students: continue
        thetas = [s['attributes'].get('cognitive_level', 0) for s in students]
        anxieties = [s['attributes'].get('anxiety_threshold', 0.5) for s in students]
        avg_theta, avg_anxiety = np.mean(thetas), np.mean(anxieties)
        teacher = class_teachers.get(cid)
        if teacher:
            total_post_efficacy += calculate_efficacy(avg_theta, avg_anxiety, teacher['attributes']['teaching_style'])

    # 5. 保存结果
    final_nodes = list(nodes.values())
    with open(os.path.join(graph_path, "nodes.json"), "w", encoding="utf-8") as f:
        json.dump(final_nodes, f, ensure_ascii=False, indent=2)

    print(f"\n--- 改革仿真总结 ---")
    print(f"  - 实施改革的班级数: {reform_count} / {len(class_students)}")
    print(f"  - 全校平均效能提升: {(total_post_efficacy - total_pre_efficacy) / len(class_students):.4f}")
    print("  - 图谱已更新为改革后的状态。")

if __name__ == "__main__":
    run_dynamic_reform_simulation()
