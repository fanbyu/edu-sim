import sys
import os
import json
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def integrate_teacher_agents():
    print("--- Edu-Sim 教师 Agent 集成程序 ---")
    
    # 1. 加载现有图谱
    graph_path = "data/graphs/edu_complete_graph_v2"
    with open(os.path.join(graph_path, "nodes.json"), "r", encoding="utf-8") as f:
        nodes = json.load(f)
    with open(os.path.join(graph_path, "edges.json"), "r", encoding="utf-8") as f:
        edges = json.load(f)

    classes = [n for n in nodes if n['label'] == 'Class']
    concepts = [n for n in nodes if n['label'] == 'Concept']
    print(f"[正在处理] {len(classes)} 个班级，准备引入教师 Agent...")

    # 2. 定义教学风格模板
    teaching_styles = {
        "heuristic": {
            "name": "启发型教师",
            "style": "heuristic",
            "feedback_quality": 0.9,
            "patience_level": 0.85,
            "strictness": 0.4,
            "summary": "善于引导学生独立思考，课堂氛围活跃，注重培养学习兴趣。"
        },
        "direct": {
            "name": "讲授型教师",
            "style": "direct",
            "feedback_quality": 0.75,
            "patience_level": 0.6,
            "strictness": 0.9,
            "summary": "知识传授系统性强，课堂节奏快，对纪律和成绩要求严格。"
        },
        "facilitator": {
            "name": "辅助型教师",
            "style": "facilitator",
            "feedback_quality": 0.8,
            "patience_level": 0.95,
            "strictness": 0.3,
            "summary": "以学生为中心，提供个性化支持，关注学生心理健康和情感需求。"
        }
    }

    new_nodes = []
    new_edges = []
    node_ids = {n['id'] for n in nodes}

    # 3. 循环生成教师并建立关系
    for cls in classes:
        class_id = cls['id']
        class_name = cls['name']
        
        # 随机分配一种教学风格
        style_key = random.choice(list(teaching_styles.keys()))
        style_info = teaching_styles[style_key]
        
        teacher_id = f"Teacher_{class_id.split('_')[1]}"
        
        # 避免 ID 冲突
        if teacher_id not in node_ids:
            teacher_node = {
                "id": teacher_id,
                "name": f"{class_name}班主任",
                "label": "Teacher",
                "summary": style_info['summary'],
                "attributes": {
                    "teaching_style": style_info['style'],
                    "feedback_quality": style_info['feedback_quality'],
                    "patience_level": style_info['patience_level'],
                    "strictness": style_info['strictness']
                }
            }
            new_nodes.append(teacher_node)
            node_ids.add(teacher_id)

            # 建立 TEACHES 关系
            new_edges.append({
                "source_id": teacher_id,
                "target_id": class_id,
                "relation": "TEACHES",
                "attributes": {"role": "head_teacher"}
            })

            # 随机建立 SPECIALIZES_IN 关系 (关联 3-5 个知识点)
            specialized_concepts = random.sample(concepts, min(5, len(concepts)))
            for concept in specialized_concepts:
                new_edges.append({
                    "source_id": teacher_id,
                    "target_id": concept['id'],
                    "relation": "SPECIALIZES_IN",
                    "attributes": {"proficiency": round(random.uniform(0.7, 1.0), 2)}
                })

    # 4. 合并并保存
    nodes.extend(new_nodes)
    edges.extend(new_edges)

    print(f"[正在保存] 新增 {len(new_nodes)} 名教师节点和 {len(new_edges)} 条关系边...")
    with open(os.path.join(graph_path, "nodes.json"), "w", encoding="utf-8") as f:
        json.dump(nodes, f, ensure_ascii=False, indent=2)
    with open(os.path.join(graph_path, "edges.json"), "w", encoding="utf-8") as f:
        json.dump(edges, f, ensure_ascii=False, indent=2)

    print(f"\n--- 教师 Agent 集成完成！ ---")
    print(f"示例教师画像:")
    if new_nodes:
        print(json.dumps(new_nodes[0], indent=2, ensure_ascii=False))

if __name__ == "__main__":
    integrate_teacher_agents()
