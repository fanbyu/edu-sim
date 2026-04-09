"""
Graph Service
图谱服务 - 提供知识图谱的高级查询和操作接口
"""

from typing import List, Dict, Any, Optional, Tuple
from app.core.knowledge_graph import GraphEngine


class GraphService:
    """
    图谱服务
    
    封装底层图数据库操作，提供教育场景专用的高级查询接口
    """
    
    def __init__(self, graph_engine: GraphEngine):
        """
        初始化图谱服务
        
        Args:
            graph_engine: 已初始化的图引擎实例
        """
        self.engine = graph_engine
    
    # ==================== 学生相关查询 ====================
    
    def get_student_profile(self, student_id: str) -> Optional[Dict[str, Any]]:
        """
        获取学生完整画像
        
        Args:
            student_id: 学生ID
            
        Returns:
            学生画像字典，包含基本信息、能力值、作答历史等
        """
        # 获取学生节点
        student_node = self.engine.get_node(student_id)
        if not student_node:
            return None
        
        profile = {
            "student_id": student_id,
            "attributes": student_node.get('properties', {}),
            "attempted_items": [],
            "mastered_concepts": []
        }
        
        # 获取作答记录
        neighbors = self.engine.get_neighbors(student_id, relation="ATTEMPTED")
        for neighbor in neighbors:
            profile["attempted_items"].append({
                "item_id": neighbor.get('id'),
                "score": neighbor.get('properties', {}).get('score')
            })
        
        # 获取已掌握知识点
        mastered = self.engine.get_neighbors(student_id, relation="MASTERED")
        profile["mastered_concepts"] = [m.get('id') for m in mastered]
        
        return profile
    
    def get_students_by_ability_range(self, min_theta: float, 
                                      max_theta: float) -> List[Dict[str, Any]]:
        """
        查询指定能力范围的学生
        
        Args:
            min_theta: 最小能力值
            max_theta: 最大能力值
            
        Returns:
            学生列表
        """
        # 简化实现：遍历所有学生节点
        stats = self.engine.get_stats()
        students = []
        
        # 这里应该使用高效的图查询，暂时用简单方法
        for i in range(1000):  # 假设学生ID从 S000 到 S999
            student_id = f"S{i:03d}"
            node = self.engine.get_node(student_id)
            if node and node.get('label') == 'Student':
                theta = node.get('properties', {}).get('cognitive_level', 0)
                if min_theta <= theta <= max_theta:
                    students.append({
                        "student_id": student_id,
                        "cognitive_level": theta,
                        "attributes": node.get('properties', {})
                    })
        
        return students
    
    def get_class_statistics(self, class_name: str) -> Dict[str, Any]:
        """
        获取班级统计信息
        
        Args:
            class_name: 班级名称
            
        Returns:
            班级统计数据
        """
        import numpy as np
        
        # 获取班级所有学生
        all_students = []
        stats = self.engine.get_stats()
        
        for i in range(stats['node_count']):
            student_id = f"S{i:03d}"
            node = self.engine.get_node(student_id)
            if node and node.get('label') == 'Student':
                class_attr = node.get('properties', {}).get('class_name')
                if class_attr == class_name:
                    all_students.append(node)
        
        if not all_students:
            return {"error": f"班级 {class_name} 不存在或无学生"}
        
        # 计算统计指标
        cognitive_levels = [
            s.get('properties', {}).get('cognitive_level', 0)
            for s in all_students
        ]
        anxieties = [
            s.get('properties', {}).get('anxiety_threshold', 0.5)
            for s in all_students
        ]
        motivations = [
            s.get('properties', {}).get('motivation_level', 0.5)
            for s in all_students
        ]
        
        return {
            "class_name": class_name,
            "student_count": len(all_students),
            "avg_cognitive_level": float(np.mean(cognitive_levels)),
            "std_cognitive_level": float(np.std(cognitive_levels)),
            "avg_anxiety": float(np.mean(anxieties)),
            "avg_motivation": float(np.mean(motivations)),
            "high_performers": sum(1 for c in cognitive_levels if c > 1.0),
            "struggling_students": sum(1 for c in cognitive_levels if c < -1.0)
        }
    
    # ==================== 试题相关查询 ====================
    
    def get_item_analysis(self, item_id: str) -> Optional[Dict[str, Any]]:
        """
        获取试题分析报告
        
        Args:
            item_id: 试题ID
            
        Returns:
            试题分析数据
        """
        item_node = self.engine.get_node(item_id)
        if not item_node:
            return None
        
        analysis = {
            "item_id": item_id,
            "attributes": item_node.get('properties', {}),
            "attempt_count": 0,
            "correct_rate": 0.0,
            "avg_score": 0.0,
            "student_distribution": {}
        }
        
        # 获取作答记录（反向查询）
        # 注意：这里需要支持反向边查询，简化实现
        stats = self.engine.get_stats()
        scores = []
        
        for i in range(stats['node_count']):
            student_id = f"S{i:03d}"
            neighbors = self.engine.get_neighbors(student_id, relation="ATTEMPTED")
            for neighbor in neighbors:
                if neighbor.get('id') == item_id:
                    score = neighbor.get('properties', {}).get('score', 0)
                    scores.append(score)
        
        if scores:
            analysis["attempt_count"] = len(scores)
            analysis["avg_score"] = float(sum(scores) / len(scores))
            analysis["correct_rate"] = sum(1 for s in scores if s >= 0.8) / len(scores)
        
        return analysis
    
    def get_items_by_difficulty_range(self, min_diff: float, 
                                      max_diff: float) -> List[Dict[str, Any]]:
        """
        查询指定难度范围的试题
        
        Args:
            min_diff: 最小难度
            max_diff: 最大难度
            
        Returns:
            试题列表
        """
        items = []
        stats = self.engine.get_stats()
        
        for i in range(1000):  # 假设试题ID从 Q000 到 Q999
            item_id = f"Q{i:03d}"
            node = self.engine.get_node(item_id)
            if node and node.get('label') == 'Item':
                diff = node.get('properties', {}).get('difficulty', 0)
                if min_diff <= diff <= max_diff:
                    items.append({
                        "item_id": item_id,
                        "difficulty": diff,
                        "attributes": node.get('properties', {})
                    })
        
        return items
    
    # ==================== 知识点相关查询 ====================
    
    def get_concept_mastery(self, student_id: str) -> Dict[str, float]:
        """
        获取学生知识点掌握度
        
        Args:
            student_id: 学生ID
            
        Returns:
            知识点掌握度字典 {concept_id: mastery_score}
        """
        mastery = {}
        
        # 获取学生作答的所有试题
        attempted_items = self.engine.get_neighbors(student_id, relation="ATTEMPTED")
        
        for item_resp in attempted_items:
            item_id = item_resp.get('id')
            score = item_resp.get('properties', {}).get('score', 0)
            
            # 获取试题关联的知识点
            concept_neighbors = self.engine.get_neighbors(item_id, relation="BELONGS_TO")
            for concept in concept_neighbors:
                concept_id = concept.get('id')
                if concept_id not in mastery:
                    mastery[concept_id] = []
                mastery[concept_id].append(score)
        
        # 计算平均掌握度
        result = {}
        for concept_id, scores in mastery.items():
            result[concept_id] = sum(scores) / len(scores) if scores else 0
        
        return result
    
    def get_concept_prerequisites(self, concept_id: str) -> List[str]:
        """
        获取知识点的前置要求
        
        Args:
            concept_id: 知识点ID
            
        Returns:
            前置知识点ID列表
        """
        prerequisites = []
        neighbors = self.engine.get_neighbors(
            concept_id, 
            relation="PREREQUISITE_OF",
            direction="incoming"
        )
        
        for neighbor in neighbors:
            prerequisites.append(neighbor.get('id'))
        
        return prerequisites
    
    # ==================== 图谱统计 ====================
    
    def get_graph_overview(self) -> Dict[str, Any]:
        """
        获取图谱概览统计
        
        Returns:
            概览数据
        """
        stats = self.engine.get_stats()
        
        return {
            "total_nodes": stats['node_count'],
            "total_edges": stats['edge_count'],
            "label_distribution": stats.get('labels', {}),
            "node_types": list(stats.get('labels', {}).keys())
        }
    
    def export_subgraph(self, center_node_id: str, 
                       max_depth: int = 2) -> Dict[str, Any]:
        """
        导出子图
        
        Args:
            center_node_id: 中心节点ID
            max_depth: 最大深度
            
        Returns:
            子图数据 {nodes: [...], edges: [...]}
        """
        visited_nodes = set()
        nodes = []
        edges = []
        
        # BFS 遍历
        queue = [(center_node_id, 0)]
        visited_nodes.add(center_node_id)
        
        while queue:
            current_id, depth = queue.pop(0)
            
            if depth > max_depth:
                break
            
            # 添加节点
            node = self.engine.get_node(current_id)
            if node:
                nodes.append(node)
            
            # 获取邻居
            neighbors = self.engine.get_neighbors(current_id)
            for neighbor in neighbors:
                neighbor_id = neighbor.get('id')
                
                # 添加边
                edges.append({
                    "source": current_id,
                    "target": neighbor_id,
                    "relation": "CONNECTED"  # 简化处理
                })
                
                # 继续遍历
                if neighbor_id not in visited_nodes and depth < max_depth:
                    visited_nodes.add(neighbor_id)
                    queue.append((neighbor_id, depth + 1))
        
        return {
            "center_node": center_node_id,
            "max_depth": max_depth,
            "nodes": nodes,
            "edges": edges,
            "node_count": len(nodes),
            "edge_count": len(edges)
        }
