import sys
import os
import json
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_simulation_and_predict():
    print("--- Edu-Sim 平行仿真与效果预测程序 ---")
    
    # 1. 加载图谱数据与实验配置
    graph_path = "data/graphs/edu_complete_graph_v2"
    with open(os.path.join(graph_path, "nodes.json"), "r", encoding="utf-8") as f:
        nodes = json.load(f)
    with open(os.path.join(graph_path, "intervention_config.json"), "r", encoding="utf-8") as f:
        config = json.load(f)

    students = [n for n in nodes if n['label'] == 'Student']
    items = [n for n in nodes if n['label'] == 'Item']
    
    # 2. 注入差异性 (模拟真实世界的多样性)
    print("[正在初始化学生差异性...]")
    for student in students:
        # 如果能力值还是 0，则赋予随机扰动 N(0, 1)
        if student['attributes'].get('cognitive_level', 0) == 0:
            student['attributes']['cognitive_level'] = round(float(np.random.normal(0, 1)), 4)

    # 3. 筛选目标群体并应用干预
    strategy_name = "heuristic" # 默认使用启发式教学
    target_students = [s for s in students if s['attributes']['cognitive_level'] < -0.5]
    effect = config['strategies'][strategy_name]['effect']
    
    print(f"[正在执行干预: {config['strategies'][strategy_name]['desc']}]")
    pre_scores = []
    post_scores = []

    # 简单的 IRT 预测函数 P = 1 / (1 + exp(-(theta - b)))
    def predict_score(theta, b):
        return 1.0 / (1.0 + np.exp(-(theta - b)))

    for student in students:
        theta = student['attributes']['cognitive_level']
        
        # 计算干预前的预期得分 (假设平均题目难度为 0)
        pre_p = predict_score(theta, 0)
        pre_scores.append(pre_p)

        # 如果是目标学生，应用干预效果
        if student in target_students:
            for attr, delta in effect.items():
                if attr in student['attributes']:
                    student['attributes'][attr] = round(student['attributes'][attr] + delta, 4)
            
            # 重新计算干预后的预期得分
            new_theta = student['attributes']['cognitive_level']
            post_p = predict_score(new_theta, 0)
            post_scores.append(post_p)
        else:
            post_scores.append(pre_p) # 非目标学生不受影响

    # 4. 统计与报告
    avg_pre = np.mean(pre_scores) * 5 # 还原为 5 分制
    avg_post = np.mean(post_scores) * 5
    
    print(f"\n--- 仿真预测报告 ---")
    print(f"  - 参与学生总数: {len(students)}")
    print(f"  - 接受干预人数: {len(target_students)}")
    print(f"  - 干预前班级平均分: {avg_pre:.2f} / 5.0")
    print(f"  - 干预后班级平均分: {avg_post:.2f} / 5.0")
    print(f"  - 预期提升幅度: {(avg_post - avg_pre):.2f} 分")
    
    # 5. 保存更新后的图谱（包含干预后的状态）
    with open(os.path.join(graph_path, "nodes.json"), "w", encoding="utf-8") as f:
        json.dump(nodes, f, ensure_ascii=False, indent=2)
    
    print(f"\n--- 仿真完成！ ---")
    print("图谱已更新为干预后的状态，可用于下一轮推演。")

if __name__ == "__main__":
    run_simulation_and_predict()
