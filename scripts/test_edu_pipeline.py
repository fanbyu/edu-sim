import sys
import os
import json
import asyncio
import uuid
import math

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.structured_data_loader import StructuredDataLoader
from app.services.ontology_generator import OntologyGenerator
from app.services.graph_storage import JSONStorage
from app.config import Config

async def test_edu_ontology_extraction():
    print("--- 开始 Edu-Sim 本体生成与图谱构建测试 ---")
    
    # 1. 加载结构化数据
    loader = StructuredDataLoader("docs/英语数据")
    data = loader.load_exam_data("试题1")
    
    if not data['knowledge_points']:
        print("错误: 未加载到知识点数据")
        return

    # 2. 构造用于生成本体的上下文文本
    # 我们将知识点和部分统计信息组合成一段自然语言描述
    context_parts = [
        "这是一个高中英语教学仿真场景。",
        f"本次练习涉及 {len(data['students_meta'])} 名学生和多个行政班（如高一550班等）。",
        "考察的核心知识点包括："
    ]
    
    for q_id, kp in list(data['knowledge_points'].items())[:5]: # 取前5个作为示例
        context_parts.append(f"- 题目 {q_id}: {kp}")
        
    context_text = "\n".join(context_parts)
    print(f"\n[输入上下文预览]\n{context_text[:200]}...\n")

    # 3. 使用预设的教育本体（由于网络原因跳过 LLM 调用）
    print("[使用预设教育本体进行图谱构建测试...]")
    ontology_result = {
        "entity_types": [
            {"name": "Student", "description": "Learner with cognitive attributes", "attributes": [{"name": "cognitive_level", "type": "float"}]},
            {"name": "Teacher", "description": "Educator providing interventions", "attributes": [{"name": "teaching_style", "type": "string"}]},
            {"name": "Item", "description": "Assessment question", "attributes": [{"name": "difficulty", "type": "float"}]},
            {"name": "Concept", "description": "Knowledge point", "attributes": []},
            {"name": "Class", "description": "Administrative class group", "attributes": []}
        ],
        "edge_types": [
            {"name": "MASTERED_BY", "source_targets": [{"source": "Concept", "target": "Student"}]},
            {"name": "ASSESSES", "source_targets": [{"source": "Item", "target": "Concept"}]},
            {"name": "BELONGS_TO", "source_targets": [{"source": "Student", "target": "Class"}]}
        ]
    }
    
    print("\n[本体结构预览]")
    print(json.dumps(ontology_result, indent=2, ensure_ascii=False))
    
    try:
        # 4. 创建图谱并设置本体
        storage = JSONStorage("data/graphs/edu_test_graph_001")
        print(f"\n[图谱存储初始化成功] 路径: data/graphs/edu_test_graph_001")
        
        # 保存本体到 metadata.json
        import os
        os.makedirs("data/graphs/edu_test_graph_001", exist_ok=True)
        with open("data/graphs/edu_test_graph_001/metadata.json", "w", encoding="utf-8") as f:
            json.dump({"ontology": ontology_result}, f, ensure_ascii=False, indent=2)
        print("[本体已成功保存到图谱元数据]")
        
        # 5. 实体抽取与建图：将学生数据写入图谱
        print("\n[开始抽取学生实体并构建图谱...]")
        
        def estimate_theta(score, max_score=100):
            """简单的 IRT theta 估算：假设满分对应 theta=2.0，平均分对应 theta=0.0"""
            ratio = score / max_score
            # 使用 logit 变换的简化版映射
            if ratio <= 0: return -3.0
            if ratio >= 1: return 3.0
            return 4.0 * (ratio - 0.5) # 简单线性映射到 [-2, 2] 区间

        students_added = 0
        for s_id, s_meta in data['students_meta'].items():
            node = {
                "id": str(s_meta['id']), # 使用准考证号作为唯一 ID
                "name": f"Student_{s_meta['id']}",
                "label": "Student",
                "summary": f"来自 {s_meta['class']} 的学生，总分 {s_meta['total_score']}",
                "attributes": {
                    "cognitive_level": round(estimate_theta(s_meta['total_score']), 3),
                    "class_name": s_meta['class'],
                    "total_score": s_meta['total_score']
                }
            }
            storage.add_node(node)
            students_added += 1
            
        print(f"[成功添加 {students_added} 个学生节点到图谱]")
        
        # 6. 构建班级实体与 BELONGS_TO 关系
        print("\n[开始构建班级实体及隶属关系...]")
        classes_created = set()
        edges_added = 0
        
        for s_id, s_meta in data['students_meta'].items():
            class_name = s_meta['class']
            
            # 如果班级节点不存在，则创建
            if class_name not in classes_created:
                class_node = {
                    "id": f"Class_{class_name}",
                    "name": class_name,
                    "label": "Class",
                    "summary": f"行政班级：{class_name}",
                    "attributes": {"student_count": 0}
                }
                storage.add_node(class_node)
                classes_created.add(class_name)
            
            # 建立 BELONGS_TO 边
            edge = {
                "source_id": str(s_meta['id']),
                "target_id": f"Class_{class_name}",
                "relation": "BELONGS_TO"
            }
            storage.add_edge(edge)
            edges_added += 1
            
        print(f"[成功创建 {len(classes_created)} 个班级节点]")
        print(f"[成功建立 {edges_added} 条 BELONGS_TO 关系]")
        
        # 7. 验证：查看某个班级的邻居（学生）
        if classes_created:
            first_class = list(classes_created)[0]
            neighbors = storage.get_neighbors(f"Class_{first_class}")
            print(f"\n[图谱关系验证] 班级 '{first_class}' 包含 {len(neighbors)} 名学生")
                    
            # 8. 构建试题与知识点实体
            print("\n[开始构建试题与知识点实体...]")
            concepts_created = set()
            items_added = 0
                    
            for q_id, kp_desc in data['knowledge_points'].items():
                if not q_id: continue
                        
                # 创建 Item 节点
                item_node = {
                    "id": f"Item_{q_id}",
                    "name": f"Question_{q_id}",
                    "label": "Item",
                    "summary": f"考察内容：{kp_desc}",
                    "attributes": {"question_id_str": q_id}
                }
                storage.add_node(item_node)
                items_added += 1
                        
                # 创建 Concept 节点 (从描述中提取核心概念，这里暂用完整描述作为 ID)
                concept_id = f"Concept_{hash(kp_desc) % 10000}"
                if kp_desc not in concepts_created:
                    concept_node = {
                        "id": concept_id,
                        "name": kp_desc[:50], # 截取前50字作为名称
                        "label": "Concept",
                        "summary": kp_desc,
                        "attributes": {}
                    }
                    storage.add_node(concept_node)
                    concepts_created.add(kp_desc)
                        
                # 建立 ASSESSES 边 (Item -> Concept)
                edge = {
                    "source_id": f"Item_{q_id}",
                    "target_id": concept_id,
                    "relation": "ASSESSES"
                }
                storage.add_edge(edge)
                        
            print(f"[成功创建 {items_added} 个试题节点]")
            print(f"[成功创建 {len(concepts_created)} 个知识点节点]")
                    
            # 9. 建立作答关系 (ATTEMPTED)
            print("\n[开始建立作答关系 ATTEMPTED...]")
            attempts_added = 0
                    
            for resp in data['responses']:
                s_id = str(resp['student_id'])
                q_idx = resp['question_index']
                score = resp['score']
                        
                # 构造 Item ID (与之前构建知识点时保持一致的逻辑)
                item_id = f"Item__{q_idx}" # 注意：CSV中的题号映射
                        
                edge = {
                    "source_id": s_id,
                    "target_id": item_id,
                    "relation": "ATTEMPTED",
                    "attributes": {
                        "score": score,
                        "timestamp": "2026-03-16"
                    }
                }
                storage.add_edge(edge)
                attempts_added += 1
                        
            print(f"[成功建立 {attempts_added} 条 ATTEMPTED 作答关系]")
        
    except Exception as e:
        print(f"发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_edu_ontology_extraction())
