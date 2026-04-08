import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.utils.structured_data_loader import StructuredDataLoader
from app.services.graph_storage import JSONStorage

def build_complete_graph():
    print("--- Edu-Sim 完整图谱构建程序 ---")
    
    # 1. 加载数据
    data_path = "docs/英语数据"
    loader = StructuredDataLoader(data_path)
    data = loader.load_exam_data("试题1")
    
    print(f"[数据加载完成] 学生: {len(data['students_meta'])}, 作答记录: {len(data['responses'])}")
    
    # 2. 初始化存储 (使用新目录避免冲突)
    graph_path = "data/graphs/edu_complete_graph_v1"
    if os.path.exists(graph_path):
        import shutil
        shutil.rmtree(graph_path)
        
    storage = JSONStorage(graph_path)
    
    # 3. 注入预设本体
    ontology_result = {
        "entity_types": [
            {"name": "Student", "description": "Learner with cognitive attributes"},
            {"name": "Teacher", "description": "Educator providing interventions"},
            {"name": "Item", "description": "Assessment question"},
            {"name": "Concept", "description": "Knowledge point"},
            {"name": "Class", "description": "Administrative class group"}
        ],
        "edge_types": [
            {"name": "MASTERED_BY", "source_targets": [{"source": "Concept", "target": "Student"}]},
            {"name": "ASSESSES", "source_targets": [{"source": "Item", "target": "Concept"}]},
            {"name": "BELONGS_TO", "source_targets": [{"source": "Student", "target": "Class"}]},
            {"name": "ATTEMPTED", "source_targets": [{"source": "Student", "target": "Item"}]}
        ]
    }
    storage.set_metadata("ontology", ontology_result, "2026-04-07T00:00:00")
    print("[本体定义已保存]")

    # 4. 构建节点
    print("\n[正在构建节点...]")
    nodes_to_add = []
    class_set = set()
    concept_set = {} # desc -> id
    
    # 4.1 学生节点
    for s_id, meta in data['students_meta'].items():
        nodes_to_add.append({
            "id": str(meta['id']),
            "name": f"Student_{meta['id']}",
            "label": "Student",
            "summary": f"来自 {meta['class']} 的学生，总分 {meta['total_score']}",
            "attributes": {"cognitive_level": 0.0, "class_name": meta['class'], "total_score": meta['total_score']}
        })
        class_set.add(meta['class'])

    # 4.2 班级节点
    for c_name in class_set:
        nodes_to_add.append({
            "id": f"Class_{c_name}",
            "name": c_name,
            "label": "Class",
            "summary": f"行政班级：{c_name}",
            "attributes": {}
        })

    # 4.3 试题与知识点节点
    for q_id, kp_desc in data['knowledge_points'].items():
        if not q_id: continue
        nodes_to_add.append({
            "id": f"Item__{q_id}",
            "name": f"Question_{q_id}",
            "label": "Item",
            "summary": f"考察内容：{kp_desc}",
            "attributes": {"question_id_str": q_id}
        })
        
        if kp_desc not in concept_set:
            cid = f"Concept_{hash(kp_desc) % 10000}"
            concept_set[kp_desc] = cid
            nodes_to_add.append({
                "id": cid,
                "name": kp_desc[:50],
                "label": "Concept",
                "summary": kp_desc,
                "attributes": {}
            })

    # 批量添加节点
    for node in nodes_to_add:
        storage.add_node(node)
    print(f"[节点构建完成] 共 {len(nodes_to_add)} 个节点")

    # 5. 构建边
    print("\n[正在构建关系边...]")
    edges_to_add = []
    
    # 5.1 BELONGS_TO
    for s_id, meta in data['students_meta'].items():
        edges_to_add.append({
            "source_id": str(meta['id']),
            "target_id": f"Class_{meta['class']}",
            "relation": "BELONGS_TO"
        })
    
    # 5.2 ASSESSES
    for q_id, kp_desc in data['knowledge_points'].items():
        if not q_id: continue
        edges_to_add.append({
            "source_id": f"Item__{q_id}",
            "target_id": concept_set[kp_desc],
            "relation": "ASSESSES"
        })
        
    # 5.3 ATTEMPTED
    for resp in data['responses']:
        edges_to_add.append({
            "source_id": str(resp['student_id']),
            "target_id": f"Item__{resp['question_index']}",
            "relation": "ATTEMPTED",
            "attributes": {"score": resp['score']}
        })

    # 批量添加边
    for edge in edges_to_add:
        storage.add_edge(edge)
    print(f"[关系构建完成] 共 {len(edges_to_add)} 条边")
    
    print(f"\n--- 图谱构建成功！路径: {graph_path} ---")

if __name__ == "__main__":
    build_complete_graph()
