import sys
import os
import json
import numpy as np
import matplotlib.pyplot as plt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def visualize_teaching_match():
    print("--- Edu-Sim 可视化分析程序 ---")
    
    # 1. 加载数据
    graph_path = "data/graphs/edu_complete_graph_v2"
    with open(os.path.join(graph_path, "nodes.json"), "r", encoding="utf-8") as f:
        nodes = {n['id']: n for n in json.load(f)}
    with open(os.path.join(graph_path, "edges.json"), "r", encoding="utf-8") as f:
        edges = json.load(f)

    # 2. 准备数据矩阵
    classes = sorted([n for n in nodes.values() if n['label'] == 'Class'], key=lambda x: x['name'])
    styles = ["heuristic", "direct", "facilitator"]
    style_names = ["启发型", "讲授型", "辅助型"]
    
    efficacy_matrix = np.zeros((len(classes), len(styles)))
    
    # 建立索引
    class_students = {}
    for edge in edges:
        if edge['relation'] == 'BELONGS_TO':
            sid, cid = edge['source_id'], edge['target_id']
            if cid not in class_students: class_students[cid] = []
            if sid in nodes: class_students[cid].append(nodes[sid])

    def calculate_efficacy(avg_theta, avg_anxiety, style):
        base_score = 0.5
        if style == "heuristic":
            bonus = 0.2 * (1 - avg_anxiety) + 0.1 * np.exp(-avg_theta**2)
        elif style == "direct":
            bonus = 0.25 * avg_theta - 0.15 * avg_anxiety
        else:
            bonus = 0.15 * (1 - avg_theta) + 0.2 * (1 - avg_anxiety)
        return base_score + bonus

    # 3. 填充矩阵
    class_names = []
    for cls in classes:
        cid = cls['id']
        students = class_students.get(cid, [])
        if not students: continue
        
        thetas = [s['attributes'].get('cognitive_level', 0) for s in students]
        anxieties = [s['attributes'].get('anxiety_threshold', 0.5) for s in students]
        avg_theta, avg_anxiety = np.mean(thetas), np.mean(anxieties)
        
        class_names.append(cls['name'])
        for j, style in enumerate(styles):
            efficacy_matrix[len(class_names)-1, j] = calculate_efficacy(avg_theta, avg_anxiety, style)

    # 4. 绘图
    plt.figure(figsize=(12, 8))
    plt.imshow(efficacy_matrix, cmap='RdYlGn', aspect='auto')
    plt.colorbar(label='Predicted Efficacy Score')
    plt.xticks(range(len(styles)), style_names)
    plt.yticks(range(len(class_names)), class_names)
    plt.title('Teaching Style Matching Heatmap by Class')
    plt.xlabel('Teaching Style')
    plt.ylabel('Class Name')
    
    # 在格子里显示数值
    for i in range(len(class_names)):
        for j in range(len(styles)):
            plt.text(j, i, f'{efficacy_matrix[i, j]:.2f}', ha='center', va='center', color='black', fontsize=8)

    plt.tight_layout()
    save_path = os.path.join(graph_path, "teaching_style_heatmap.png")
    plt.savefig(save_path)
    print(f"[成功] 热力图已保存至: {save_path}")

if __name__ == "__main__":
    visualize_teaching_match()
