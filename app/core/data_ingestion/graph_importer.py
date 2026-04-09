"""
Graph Data Importer
图谱数据导入器 - 将教育数据批量导入知识图谱
"""

from typing import List, Dict, Any
from app.core.knowledge_graph import GraphEngine
from app.models.education import Student, Item, Response


class GraphDataImporter:
    """
    图谱数据导入器
    
    负责将 ExamDataLoader 加载的数据转换为图谱节点和边，并批量导入
    """
    
    def __init__(self, graph_engine: GraphEngine):
        """
        初始化导入器
        
        Args:
            graph_engine: 已初始化的图引擎实例
        """
        self.engine = graph_engine
        self.stats = {
            "students_added": 0,
            "items_added": 0,
            "concepts_added": 0,
            "responses_added": 0,
            "errors": []
        }
    
    def import_exam_data(self, exam_data: Dict[str, Any]) -> Dict[str, int]:
        """
        导入考试数据到图谱
        
        Args:
            exam_data: ExamDataLoader.load_exam_data() 返回的数据
            
        Returns:
            导入统计信息
        """
        print(f"\n📥 开始导入考试数据: {exam_data.get('exam_id')}")
        
        # 重置统计
        self.stats = {k: 0 if isinstance(v, int) else [] for k, v in self.stats.items()}
        
        try:
            # 1. 导入学生节点
            students_meta = exam_data.get('students_meta', {})
            if students_meta:
                self._import_students(students_meta)
            
            # 2. 导入试题节点
            items_meta = exam_data.get('items_meta', {})
            if items_meta:
                self._import_items(items_meta)
            
            # 3. 导入知识点节点
            knowledge_points = exam_data.get('knowledge_points', {})
            if knowledge_points:
                self._import_concepts(knowledge_points)
            
            # 4. 导入作答记录 (边)
            responses = exam_data.get('responses', [])
            if responses:
                self._import_responses(responses)
            
            # 5. 建立试题与知识点的关系
            if items_meta and knowledge_points:
                self._link_items_to_concepts(items_meta, knowledge_points)
            
            print(f"✅ 导入完成!")
            print(f"   - 学生: {self.stats['students_added']}")
            print(f"   - 试题: {self.stats['items_added']}")
            print(f"   - 知识点: {self.stats['concepts_added']}")
            print(f"   - 作答记录: {self.stats['responses_added']}")
            
            if self.stats['errors']:
                print(f"   - 错误: {len(self.stats['errors'])}")
                for err in self.stats['errors'][:5]:  # 只显示前5个错误
                    print(f"     ⚠️  {err}")
        
        except Exception as e:
            print(f"❌ 导入失败: {e}")
            import traceback
            traceback.print_exc()
            self.stats['errors'].append(str(e))
        
        return self.stats.copy()
    
    def _import_students(self, students_meta: Dict[str, Dict]):
        """批量导入学生节点"""
        nodes = []
        
        for student_id, meta in students_meta.items():
            # 创建 Student 模型
            student = Student(
                student_id=student_id,
                cognitive_level=0.0,  # 初始值，后续通过 IRT 校准
                class_name=meta.get('class'),
                anxiety_threshold=0.5,
                motivation_level=0.5
            )
            
            node_dict = student.to_dict()
            nodes.append(node_dict)
        
        if nodes:
            result = self.engine.batch_import(nodes=nodes, edges=[])
            self.stats['students_added'] = result.get('nodes_added', 0)
            print(f"   ✓ 导入 {self.stats['students_added']} 个学生节点")
    
    def _import_items(self, items_meta: Dict[str, Dict]):
        """批量导入试题节点"""
        nodes = []
        
        for item_id, meta in items_meta.items():
            # 创建 Item 模型
            item = Item(
                item_id=item_id,
                difficulty=meta.get('difficulty', 0.0),
                discrimination=1.0,  # 默认值，后续可通过 IRT 校准
                question_type="unknown",
                max_score=meta.get('max_score', 1.0),
                assessed_concepts=meta.get('assessed_concepts', [])
            )
            
            node_dict = item.to_dict()
            nodes.append(node_dict)
        
        if nodes:
            result = self.engine.batch_import(nodes=nodes, edges=[])
            self.stats['items_added'] = result.get('nodes_added', 0)
            print(f"   ✓ 导入 {self.stats['items_added']} 个试题节点")
    
    def _import_concepts(self, knowledge_points: Dict[str, str]):
        """批量导入知识点节点"""
        nodes = []
        seen_concepts = set()
        
        for q_id, concept_name in knowledge_points.items():
            if not concept_name or concept_name in seen_concepts:
                continue
            
            seen_concepts.add(concept_name)
            
            # 创建 Concept 节点
            concept_id = f"concept_{hash(concept_name) % 10000:04d}"
            nodes.append({
                "id": concept_id,
                "label": "Concept",
                "properties": {
                    "name": concept_name,
                    "source_question": q_id
                }
            })
        
        if nodes:
            result = self.engine.batch_import(nodes=nodes, edges=[])
            self.stats['concepts_added'] = result.get('nodes_added', 0)
            print(f"   ✓ 导入 {self.stats['concepts_added']} 个知识点节点")
    
    def _import_responses(self, responses: List[Dict]):
        """批量导入作答记录 (边)"""
        edges = []
        
        for resp in responses:
            student_id = resp.get('student_id')
            q_index = resp.get('question_index')
            score = resp.get('score', 0)
            
            if not student_id or not q_index:
                continue
            
            # 生成试题ID
            item_id = f"Q{q_index:03d}"
            
            # 创建 Response 模型
            response = Response(
                student_id=student_id,
                item_id=item_id,
                score=score,
                time_spent=0.0  # 暂时设为0，后续可从数据中提取
            )
            
            edge_dict = response.to_dict()
            edges.append(edge_dict)
        
        if edges:
            result = self.engine.batch_import(nodes=[], edges=edges)
            self.stats['responses_added'] = result.get('edges_added', 0)
            print(f"   ✓ 导入 {self.stats['responses_added']} 条作答记录")
    
    def _link_items_to_concepts(self, items_meta: Dict[str, Dict], 
                                knowledge_points: Dict[str, str]):
        """建立试题与知识点的 BELONGS_TO 关系"""
        edges = []
        
        # 构建反向映射: concept_name -> concept_id
        concept_name_to_id = {}
        stats = self.engine.get_stats()
        # 这里简化处理，实际应该查询图谱获取所有 Concept 节点
        
        for q_id, concept_name in knowledge_points.items():
            if not concept_name:
                continue
            
            # 从 question_index 推断 item_id
            try:
                q_num = int(q_id.split('_')[1]) if '_' in q_id else 1
            except (IndexError, ValueError):
                continue
            
            item_id = f"Q{q_num:03d}"
            concept_id = f"concept_{hash(concept_name) % 10000:04d}"
            
            edges.append({
                "source_id": item_id,
                "target_id": concept_id,
                "relation": "BELONGS_TO",
                "properties": {}
            })
        
        if edges:
            result = self.engine.batch_import(nodes=[], edges=edges)
            print(f"   ✓ 建立 {result.get('edges_added', 0)} 条试题-知识点关系")
    
    def get_import_summary(self) -> Dict[str, Any]:
        """获取导入摘要"""
        total_nodes = (
            self.stats['students_added'] + 
            self.stats['items_added'] + 
            self.stats['concepts_added']
        )
        
        return {
            "total_nodes": total_nodes,
            "total_edges": self.stats['responses_added'],
            "details": self.stats.copy()
        }
