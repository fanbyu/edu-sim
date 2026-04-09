"""
Graph Backend Abstraction
图数据库后端抽象层
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class GraphBackend(ABC):
    """
    图数据库后端抽象基类
    
    支持多种图数据库实现 (Neo4j, Kuzu, JSON等)
    """
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any] = None):
        """
        初始化图数据库连接
        
        Args:
            config: 配置参数
        """
        pass
    
    @abstractmethod
    def add_node(self, node_id: str, label: str, properties: Dict[str, Any]) -> bool:
        """
        添加节点
        
        Args:
            node_id: 节点唯一标识
            label: 节点标签 (类型)
            properties: 节点属性
            
        Returns:
            是否成功
        """
        pass
    
    @abstractmethod
    def add_edge(self, source_id: str, target_id: str, relation: str, 
                 properties: Dict[str, Any] = None) -> bool:
        """
        添加边
        
        Args:
            source_id: 源节点ID
            target_id: 目标节点ID
            relation: 关系类型
            properties: 边属性
            
        Returns:
            是否成功
        """
        pass
    
    @abstractmethod
    def batch_import(self, nodes: List[Dict[str, Any]], 
                     edges: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        批量导入节点和边 (性能关键)
        
        Args:
            nodes: 节点列表,每个节点包含 {id, label, properties}
            edges: 边列表,每个边包含 {source_id, target_id, relation, properties}
            
        Returns:
            统计信息 {'nodes_added': N, 'edges_added': M}
        """
        pass
    
    @abstractmethod
    def query(self, query_str: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        执行查询
        
        Args:
            query_str: 查询语句 (Cypher/Gremlin等)
            params: 查询参数
            
        Returns:
            查询结果列表
        """
        pass
    
    @abstractmethod
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """
        获取单个节点
        
        Args:
            node_id: 节点ID
            
        Returns:
            节点数据或 None
        """
        pass
    
    @abstractmethod
    def get_neighbors(self, node_id: str, relation: str = None, 
                      direction: str = 'both') -> List[Dict[str, Any]]:
        """
        获取邻居节点
        
        Args:
            node_id: 中心节点ID
            relation: 关系类型过滤 (可选)
            direction: 方向 ('outgoing', 'incoming', 'both')
            
        Returns:
            邻居节点列表
        """
        pass
    
    @abstractmethod
    def delete_node(self, node_id: str) -> bool:
        """
        删除节点及其关联的边
        
        Args:
            node_id: 节点ID
            
        Returns:
            是否成功
        """
        pass
    
    @abstractmethod
    def close(self):
        """关闭数据库连接"""
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, int]:
        """
        获取图谱统计信息
        
        Returns:
            {'node_count': N, 'edge_count': M, 'labels': {...}}
        """
        pass


class GraphEngine:
    """
    图引擎工厂类
    
    根据配置创建并管理具体的后端实现
    """
    
    def __init__(self, backend_type: str = "json", config: Dict[str, Any] = None):
        """
        初始化图引擎
        
        Args:
            backend_type: 后端类型 ('json', 'graphify', 'neo4j', 'kuzu')
            config: 后端配置参数
        """
        self.backend_type = backend_type
        self.config = config or {}
        self.backend = None
    
    def initialize(self):
        """初始化后端连接"""
        if self.backend_type == "json":
            from .backends.json_backend import JSONBackend
            self.backend = JSONBackend()
        elif self.backend_type == "graphify":
            from .graphify_backend import GraphifyBackend
            self.backend = GraphifyBackend(
                storage_path=self.config.get('storage_path', 'data/graphify')
            )
        elif self.backend_type == "neo4j":
            # TODO: from .backends.neo4j_backend import Neo4jBackend
            raise NotImplementedError("Neo4j backend not yet implemented")
        elif self.backend_type == "kuzu":
            # TODO: from .backends.kuzu_backend import KuzuBackend
            raise NotImplementedError("Kuzu backend not yet implemented")
        else:
            raise ValueError(f"Unknown backend type: {self.backend_type}")
        
        self.backend.initialize(self.config)
    
    def add_node(self, node_id: str, label: str, properties: Dict[str, Any]) -> bool:
        """添加节点 (委托给后端)"""
        if not self.backend:
            raise RuntimeError("GraphEngine not initialized. Call initialize() first.")
        return self.backend.add_node(node_id, label, properties)
    
    def add_edge(self, source_id: str, target_id: str, relation: str,
                 properties: Dict[str, Any] = None) -> bool:
        """添加边 (委托给后端)"""
        if not self.backend:
            raise RuntimeError("GraphEngine not initialized. Call initialize() first.")
        return self.backend.add_edge(source_id, target_id, relation, properties)
    
    def batch_import(self, nodes: List[Dict[str, Any]],
                     edges: List[Dict[str, Any]]) -> Dict[str, int]:
        """批量导入 (委托给后端)"""
        if not self.backend:
            raise RuntimeError("GraphEngine not initialized. Call initialize() first.")
        return self.backend.batch_import(nodes, edges)
    
    def query(self, query_str: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """执行查询 (委托给后端)"""
        if not self.backend:
            raise RuntimeError("GraphEngine not initialized. Call initialize() first.")
        return self.backend.query(query_str, params)
    
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """获取节点 (委托给后端)"""
        if not self.backend:
            raise RuntimeError("GraphEngine not initialized. Call initialize() first.")
        return self.backend.get_node(node_id)
    
    def get_neighbors(self, node_id: str, relation: str = None,
                      direction: str = 'both') -> List[Dict[str, Any]]:
        """获取邻居 (委托给后端)"""
        if not self.backend:
            raise RuntimeError("GraphEngine not initialized. Call initialize() first.")
        return self.backend.get_neighbors(node_id, relation, direction)
    
    def delete_node(self, node_id: str) -> bool:
        """删除节点 (委托给后端)"""
        if not self.backend:
            raise RuntimeError("GraphEngine not initialized. Call initialize() first.")
        return self.backend.delete_node(node_id)
    
    def close(self):
        """关闭连接 (委托给后端)"""
        if self.backend:
            self.backend.close()
    
    def get_stats(self) -> Dict[str, int]:
        """获取统计 (委托给后端)"""
        if not self.backend:
            raise RuntimeError("GraphEngine not initialized. Call initialize() first.")
        return self.backend.get_stats()
