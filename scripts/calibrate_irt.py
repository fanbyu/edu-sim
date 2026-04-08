import sys
import os
import json
import numpy as np
from scipy.optimize import minimize
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_irt_calibration():
    print("--- Edu-Sim IRT 能力值校准程序 ---")
    
    # 1. 加载图谱数据
    graph_path = "data/graphs/edu_complete_graph_v2"
    with open(os.path.join(graph_path, "nodes.json"), "r", encoding="utf-8") as f:
        nodes = {n['id']: n for n in json.load(f)}
    with open(os.path.join(graph_path, "edges.json"), "r", encoding="utf-8") as f:
        edges = json.load(f)

    # 2. 提取作答矩阵 (Response Matrix)
    student_ids = sorted([nid for nid, n in nodes.items() if n['label'] == 'Student'])
    item_ids = sorted([nid for nid, n in nodes.items() if n['label'] == 'Item'])
    
    s_idx = {sid: i for i, sid in enumerate(student_ids)}
    i_idx = {iid: j for j, iid in enumerate(item_ids)}
    
    n_students = len(student_ids)
    n_items = len(item_ids)
    
    # 假设满分是 5 分（根据英语数据常见情况，或者取最大值归一化）
    max_score = 5.0 
    R = np.zeros((n_students, n_items)) # 得分矩阵
    M = np.zeros((n_students, n_items)) # 是否作答标记
    
    print(f"[正在构建作答矩阵] 维度: {n_students} x {n_items}")
    for edge in edges:
        if edge['relation'] == 'ATTEMPTED':
            sid = edge['source_id']
            iid = edge['target_id']
            score = edge['attributes'].get('score', 0)
            
            if sid in s_idx and iid in i_idx:
                si = s_idx[sid]
                ii = i_idx[iid]
                R[si, ii] = score / max_score # 归一化到 [0, 1]
                M[si, ii] = 1

    # 3. IRT 模型定义 (2PL Logistic Model)
    def irt_prob(theta, b, a=1.0):
        """计算答对概率 P(theta, b)"""
        return 1.0 / (1.0 + np.exp(-a * (theta - b)))

    def negative_log_likelihood(params):
        """负对数似然函数"""
        thetas = params[:n_students]
        bs = params[n_students:]
        
        log_lik = 0.0
        for i in range(n_students):
            for j in range(n_items):
                if M[i, j] == 1:
                    p = irt_prob(thetas[i], bs[j])
                    p = np.clip(p, 1e-6, 1 - 1e-6) # 防止 log(0)
                    # 伯努利分布的对数似然
                    log_lik += R[i, j] * np.log(p) + (1 - R[i, j]) * np.log(1 - p)
        return -log_lik

    # 4. 优化求解
    print("[正在进行 IRT 参数估计...] 这可能需要几分钟...")
    initial_params = np.concatenate([np.zeros(n_students), np.zeros(n_items)])
    
    # 限制参数范围：能力在 [-3, 3]，难度在 [-3, 3]
    bounds = [(-3, 3)] * (n_students + n_items)
    
    result = minimize(negative_log_likelihood, initial_params, method='L-BFGS-B', bounds=bounds, options={'maxiter': 100})
    
    calibrated_thetas = result.x[:n_students]
    calibrated_bs = result.x[n_students:]

    # 5. 更新节点属性并保存
    print("[正在更新图谱节点属性...]")
    for i, sid in enumerate(student_ids):
        nodes[sid]['attributes']['cognitive_level'] = round(float(calibrated_thetas[i]), 4)
        
    for j, iid in enumerate(item_ids):
        nodes[iid]['attributes']['difficulty'] = round(float(calibrated_bs[j]), 4)

    # 重新写入文件
    final_nodes = list(nodes.values())
    with open(os.path.join(graph_path, "nodes.json"), "w", encoding="utf-8") as f:
        json.dump(final_nodes, f, ensure_ascii=False, indent=2)

    print(f"\n--- IRT 校准完成！ ---")
    print(f"示例学生能力值 (Student_{student_ids[0]}): {calibrated_thetas[0]:.4f}")
    print(f"示例题目难度值 (Item_{item_ids[0]}): {calibrated_bs[0]:.4f}")

if __name__ == "__main__":
    run_irt_calibration()
