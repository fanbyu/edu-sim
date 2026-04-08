import sys
import os
import json
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_advanced_simulation():
    print("--- Edu-Sim 高级仿真程序 (动态能力增长) ---")
    
    # 1. 加载数据
    graph_path = "data/graphs/edu_complete_graph_v2"
    with open(os.path.join(graph_path, "nodes.json"), "r", encoding="utf-8") as f:
        nodes = {n['id']: n for n in json.load(f)}

    students = [n for n in nodes.values() if n['label'] == 'Student']
    
    # 2. 定义干预效果模型
    def apply_intervention(student, style):
        theta = student['attributes']['cognitive_level']
        motivation = student['attributes']['motivation_level']
        
        # 启发式：通过动机提升带动能力缓慢增长
        if style == "heuristic":
            growth = 0.1 * motivation + 0.05
            student['attributes']['anxiety_threshold'] -= 0.1
            student['attributes']['motivation_level'] += 0.1
        
        # 讲授式：直接灌输知识，能力增长快但焦虑增加
        elif style == "direct":
            growth = 0.2 
            student['attributes']['anxiety_threshold'] += 0.05
            
        # 辅助式：基础差的学生增长快
        else: 
            growth = 0.15 * (1 - theta) if theta < 0 else 0.05
            student['attributes']['anxiety_threshold'] -= 0.15

        # 更新能力值 (IRT theta)
        student['attributes']['cognitive_level'] = round(theta + growth, 4)

    # 3. 执行仿真
    print("[正在执行教学干预并模拟能力增长...]")
    for student in students:
        # 随机分配一种干预风格进行模拟
        style = np.random.choice(["heuristic", "direct", "facilitator"])
        apply_intervention(student, style)

    # 4. 统计结果
    thetas = [s['attributes']['cognitive_level'] for s in students]
    avg_theta_post = np.mean(thetas)
    
    print(f"\n--- 高级仿真报告 ---")
    print(f"  - 参与学生数: {len(students)}")
    print(f"  - 干预后平均认知能力 (theta): {avg_theta_post:.4f}")
    print(f"  - 能力提升显著的学生比例: {sum(1 for t in thetas if t > 0.5) / len(thetas) * 100:.1f}%")

    # 5. 保存
    final_nodes = list(nodes.values())
    with open(os.path.join(graph_path, "nodes.json"), "w", encoding="utf-8") as f:
        json.dump(final_nodes, f, ensure_ascii=False, indent=2)
    print("  - 图谱已更新为干预后的状态。")

if __name__ == "__main__":
    run_advanced_simulation()
