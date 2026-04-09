"""
JSON Backend Implementation
JSON 文件后端实现 - 用于开发和测试
"""

import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..graph_engine import GraphBackend


class JSONBackend(GraphBackend):
    """
    基于 JSON 文件的图数据库后端
    
    优点: 无需外部依赖,易于调试
    缺点: 性能较低,不适合大规模数据
    """
    
    def __init__(self, storage_path: str = "data/graphs"):
        self.storage_path = storage_path
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: List[Dict[str, Any]] = []
        self.initialized = False
    
    def initialize(self, config: Dict[str, Any] = None):
        """初始化存储路径"""
        os.makedirs(self.storage_path, exist_ok=True)
        self._load_from_disk()
        self.initialized = True
    
    def add_node(self, node_id: str, label: str, properties: Dict[str, Any]) -> bool:
        """添加节点"""
        if node_id in self.nodes:
            return False
        
        self.nodes[node_id] = {
            "id": node_id,
            "label": label,
            "properties": properties,
            "created_at": datetime.now().isoformat()
        }
        return True
    
    def add_edge(self, source_id: str, target_id: str, relation: str,
                 properties: Dict[str, Any] = None) -> bool:
        """添加边"""
        if source_id not in self.nodes or target_id not in self.nodes:
            return False
        
        edge = {
            "source_id": source_id,
            "target_id": target_id,
            "relation": relation,
            "properties": properties or {},
            "created_at": datetime.now().isoformat()
        }
        self.edges.append(edge)
        return True
    
    def batch_import(self, nodes: List[Dict[str, Any]], 
                     edges: List[Dict[str, Any]]) -> Dict[str, int]:
        """批量导入 - 优化性能"""
        nodes_added = 0
        edges_added = 0
        
        # 批量添加节点
        for node in nodes:
            node_id = node.get('id')
            label = node.get('label', 'Entity')
            properties = node.get('properties', {})
            
            if node_id and node_id not in self.nodes:
                self.nodes[node_id] = {
                    "id": node_id,
                    "label": label,
                    "properties": properties,
                    "created_at": datetime.now().isoformat()
                }
                nodes_added += 1
        
        # 批量添加边
        for edge in edges:
            source_id = edge.get('source_id')
            target_id = edge.get('target_id')
            relation = edge.get('relation')
            
            if source_id and target_id and relation:
                if source_id in self.nodes and target_id in self.nodes:
                    self.edges.append({
                        "source_id": source_id,
                        "target_id": target_id,
                        "relation": relation,
                        "properties": edge.get('properties', {}),
                        "created_at": datetime.now().isoformat()
                    })
                    edges_added += 1
        
        return {"nodes_added": nodes_added, "edges_added": edges_added}
    
    def query(self, query_str: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        简单查询实现 (仅支持基础模式匹配)
        
        注意: 这是简化实现,生产环境应使用真正的图查询语言
        """
        # TODO: 实现简单的 Cypher 解析器或使用 graphlib
        raise NotImplementedError("Query not fully implemented for JSON backend")
    
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """获取节点"""
        return self.nodes.get(node_id)
    
    def get_neighbors(self, node_id: str, relation: str = None,
                      direction: str = 'both') -> List[Dict[str, Any]]:
        """获取邻居节点"""
        neighbors = []
        
        for edge in self.edges:
            match = False
            
            if direction in ['both', 'outgoing'] and edge['source_id'] == node_id:
                if relation is None or edge['relation'] == relation:
                    match = True
                    neighbor_id = edge['target_id']
            
            if direction in ['both', 'incoming'] and edge['target_id'] == node_id:
                if relation is None or edge['relation'] == relation:
                    match = True
                    neighbor_id = edge['source_id']
            
            if match and neighbor_id in self.nodes:
                neighbors.append(self.nodes[neighbor_id])
        
        return neighbors
    
    def delete_node(self, node_id: str) -> bool:
        """删除节点及其关联的边"""
        if node_id not in self.nodes:
            return False
        
        # 删除节点
        del self.nodes[node_id]
        
        # 删除相关边
        self.edges = [
            edge for edge in self.edges
            if edge['source_id'] != node_id and edge['target_id'] != node_id
        ]
        
        return True
    
    def close(self):
        """保存数据并关闭"""
        self._save_to_disk()
    
    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        labels = {}
        for node in self.nodes.values():
            label = node['label']
            labels[label] = labels.get(label, 0) + 1
        
        return {
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "labels": labels
        }
    
    def _load_from_disk(self):
        """从磁盘加载数据"""
        nodes_file = os.path.join(self.storage_path, "nodes.json")
        edges_file = os.path.join(self.storage_path, "edges.json")
        
        if os.path.exists(nodes_file):
            with open(nodes_file, 'r', encoding='utf-8') as f:
                nodes_list = json.load(f)
                self.nodes = {node['id']: node for node in nodes_list}
        
        if os.path.exists(edges_file):
            with open(edges_file, 'r', encoding='utf-8') as f:
                self.edges = json.load(f)
    
    def _save_to_disk(self):
        """保存数据到磁盘"""
        nodes_file = os.path.join(self.storage_path, "nodes.json")
        edges_file = os.path.join(self.storage_path, "edges.json")
        
        with open(nodes_file, 'w', encoding='utf-8') as f:
            json.dump(list(self.nodes.values()), f, ensure_ascii=False, indent=2)
        
        with open(edges_file, 'w', encoding='utf-8') as f:
            json.dump(self.edges, f, ensure_ascii=False, indent=2)


class GraphEngine:
    """
    图谱引擎 - 管理后端实例
    
    提供统一接口,支持切换不同后端
    """
    
    def __init__(self, backend_type: str = "json", config: Dict[str, Any] = None):
        self.backend_type = backend_type
        self.backend = self._create_backend(backend_type, config)
    
    def _create_backend(self, backend_type: str, config: Dict[str, Any] = None) -> GraphBackend:
        """工厂方法创建后端实例"""
        if backend_type == "json":
            storage_path = config.get('storage_path', 'data/graphs') if config else 'data/graphs'
            return JSONBackend(storage_path=storage_path)
        elif backend_type == "neo4j":
            # TODO: 实现 Neo4jBackend
            raise NotImplementedError("Neo4j backend not yet implemented")
        elif backend_type == "kuzu":
            # TODO: 实现 KuzuBackend
            raise NotImplementedError("Kuzu backend not yet implemented")
        else:
            raise ValueError(f"Unknown backend type: {backend_type}")
    
    def __getattr__(self, name):
        """代理所有方法调用到后端"""
        return getattr(self.backend, name)
