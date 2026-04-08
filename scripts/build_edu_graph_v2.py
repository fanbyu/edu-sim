import sys
import os
import json
from datetime import datetime

# 确保可以导入 app 模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.structured_data_loader import StructuredDataLoader

def build_graph_efficiently():
    print("--- Edu-Sim 高效图谱构建程序 (V2) ---")
    
    # 1. 加载数据
    data_path = "docs/英语数据"
    loader = StructuredDataLoader(data_path)
    data = loader.load_exam_data("试题1")
    
    print(f"[数据加载完成] 学生: {len(data['students_meta'])}, 作答记录: {len(data['responses'])}")
    
    # 2. 初始化存储目录
    graph_path = "data/graphs/edu_complete_graph_v2"
    if os.path.exists(graph_path):
        import shutil
        shutil.rmtree(graph_path)
    os.makedirs(graph_path, exist_ok=True)
    
    nodes = []
    edges = []
    node_ids = set()
    
    def add_node(n_id, name, label, summary, attrs):
        if n_id in node_ids: return
        nodes.append({
            "id": str(n_id),
            "name": str(name),
            "label": str(label),
            "summary": str(summary),
            "attributes": attrs,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "facts": [],
            "episodes": []
        })
        node_ids.add(str(n_id))

    def add_edge(s_id, t_id, rel, attrs=None):
        edges.append({
            "id": "",
            "source_id": str(s_id),
            "target_id": str(t_id),
            "relation": str(rel),
            "weight": 1.0,
            "fact": "",
            "attributes": attrs or {},
            "created_at": datetime.now().isoformat(),
            "valid_at": None,
            "invalid_at": None,
            "expired_at": None,
            "episodes": []
        })

    # 3. 构建本体元数据
    ontology = {
        "entity_types": [
            {"name": "Student", "description": "Learner"},
            {"name": "Teacher", "description": "Educator"},
            {"name": "Item", "description": "Question"},
            {"name": "Concept", "description": "Knowledge Point"},
            {"name": "Class", "description": "Administrative Class"}
        ],
        "edge_types": [
            {"name": "MASTERED_BY", "source_targets": [{"source": "Concept", "target": "Student"}]},
            {"name": "ASSESSES", "source_targets": [{"source": "Item", "target": "Concept"}]},
            {"name": "BELONGS_TO", "source_targets": [{"source": "Student", "target": "Class"}]},
            {"name": "ATTEMPTED", "source_targets": [{"source": "Student", "target": "Item"}]}
        ]
    }
    
    # 4. 批量处理实体与关系
    print("\n[正在内存中组装图谱...]")
    concept_map = {} # 知识点描述 -> ID
    
    # 4.1 处理学生和班级
    for s_id, meta in data['students_meta'].items():
        add_node(s_id, f"Student_{s_id}", "Student", f"总分: {meta['total_score']}", 
                 {"cognitive_level": 0.0, "class_name": meta['class'], "total_score": meta['total_score']})
        add_node(f"Class_{meta['class']}", meta['class'], "Class", f"行政班: {meta['class']}", {})
        add_edge(s_id, f"Class_{meta['class']}", "BELONGS_TO")

    # 4.2 处理试题和知识点
    for q_id, kp_desc in data['knowledge_points'].items():
        if not q_id: continue
        item_id = f"Item__{q_id}"
        add_node(item_id, f"Question_{q_id}", "Item", f"考察: {kp_desc}", {"question_id_str": q_id})
        
        if kp_desc not in concept_map:
            cid = f"Concept_{hash(kp_desc) % 10000}"
            concept_map[kp_desc] = cid
            add_node(cid, kp_desc[:50], "Concept", kp_desc, {})
        
        add_edge(item_id, concept_map[kp_desc], "ASSESSES")

    # 4.3 处理作答关系 (ATTEMPTED)
    for resp in data['responses']:
        add_edge(str(resp['student_id']), f"Item__{resp['question_index']}", "ATTEMPTED", {"score": resp['score']})

    # 5. 一次性持久化到磁盘
    print(f"[开始写入磁盘] 节点数: {len(nodes)}, 边数: {len(edges)}")
    
    with open(os.path.join(graph_path, "nodes.json"), "w", encoding="utf-8") as f:
        json.dump(nodes, f, ensure_ascii=False, indent=2)
        
    with open(os.path.join(graph_path, "edges.json"), "w", encoding="utf-8") as f:
        json.dump(edges, f, ensure_ascii=False, indent=2)
        
    metadata = {"ontology": {"value": ontology, "updated_at": datetime.now().isoformat()}}
    with open(os.path.join(graph_path, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"\n--- 成功！图谱已保存至: {graph_path} ---")

if __name__ == "__main__":
    build_graph_efficiently()
