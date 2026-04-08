import sys
import os
import json
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def analyze_teaching_style_match():
    print("--- Edu-Sim 教学风格匹配度分析程序 ---")
    
    # 1. 加载图谱数据
    graph_path = "data/graphs/edu_complete_graph_v2"
    with open(os.path.join(graph_path, "nodes.json"), "r", encoding="utf-8") as f:
        nodes = {n['id']: n for n in json.load(f)}
    with open(os.path.join(graph_path, "edges.json"), "r", encoding="utf-8") as f:
        edges = json.load(f)

    # 2. 建立索引
    class_students = {} # {class_id: [student_nodes]}
    class_teachers = {} # {class_id: teacher_node}

    for edge in edges:
        if edge['relation'] == 'BELONGS_TO':
            sid = edge['source_id']
            cid = edge['target_id']
            if cid not in class_students:
                class_students[cid] = []
            if sid in nodes:
                class_students[cid].append(nodes[sid])
        
        if edge['relation'] == 'TEACHES':
            tid = edge['source_id']
            cid = edge['target_id']
            if tid in nodes:
                class_teachers[cid] = nodes[tid]

    # 3. 定义风格适配模型 (基于教育心理学假设)
    def calculate_efficacy(avg_theta, avg_anxiety, style):
        base_score = 0.5
        if style == "heuristic":
            # 启发式：对高焦虑有补偿，对中等能力最有效
            bonus = 0.2 * (1 - avg_anxiety) + 0.1 * np.exp(-avg_theta**2)
        elif style == "direct":
            # 讲授式：对高能力有加成，但会增加焦虑负面影响
            bonus = 0.25 * avg_theta - 0.15 * avg_anxiety
        else: # facilitator
            # 辅助式：对低能力、高焦虑群体有显著保护
            bonus = 0.15 * (1 - avg_theta) + 0.2 * (1 - avg_anxiety)
        
        return round(base_score + bonus, 4)

    print(f"\n{'班级名称':<15} {'当前风格':<10} {'平均能力':<10} {'平均焦虑':<10} {'当前效能':<10} {'推荐风格':<10}")
    print("-" * 80)

    analysis_results = []
    for cid, students in class_students.items():
        if not students: continue
        
        # 计算班级统计量
        thetas = [s['attributes'].get('cognitive_level', 0) for s in students]
        anxieties = [s['attributes'].get('anxiety_threshold', 0.5) for s in students]
        avg_theta = np.mean(thetas)
        avg_anxiety = np.mean(anxieties)

        # 获取当前教师风格
        teacher = class_teachers.get(cid)
        current_style = teacher['attributes']['teaching_style'] if teacher else "unknown"
        
        # 计算当前效能
        current_efficacy = calculate_efficacy(avg_theta, avg_anxiety, current_style)

        # 寻找最佳风格
        styles = ["heuristic", "direct", "facilitator"]
        best_style = max(styles, key=lambda s: calculate_efficacy(avg_theta, avg_anxiety, s))
        best_efficacy = calculate_efficacy(avg_theta, avg_anxiety, best_style)

        class_name = nodes[cid]['name'] if cid in nodes else cid
        analysis_results.append({
            "class_name": class_name,
            "current_style": current_style,
            "best_style": best_style,
            "efficacy_gap": round(best_efficacy - current_efficacy, 4)
        })

        match_flag = "✅" if current_style == best_style else "⚠️"
        print(f"{class_name:<12} {current_style:<10} {avg_theta:<10.2f} {avg_anxiety:<10.2f} {current_efficacy:<10.4f} {best_style:<10} {match_flag}")

    # 4. 总结建议
    mismatches = [r for r in analysis_results if r['efficacy_gap'] > 0.05]
    print(f"\n--- 分析总结 ---")
    print(f"  - 总班级数: {len(analysis_results)}")
    print(f"  - 风格适配不佳的班级: {len(mismatches)}")
    if mismatches:
        print("  - 建议调整示例:")
        for m in mismatches[:3]:
            print(f"    * {m['class_name']}: 建议从 [{m['current_style']}] 调整为 [{m['best_style']}] (预期效能提升 {m['efficacy_gap']})")

if __name__ == "__main__":
    analyze_teaching_style_match()
