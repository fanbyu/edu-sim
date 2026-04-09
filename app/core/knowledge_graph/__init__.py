"""
Knowledge Graph Engine
知识图谱引擎 - 支持多后端
"""

from .graph_engine import GraphBackend, GraphEngine
from .backends.json_backend import JSONBackend

__all__ = ['GraphBackend', 'GraphEngine', 'JSONBackend']
