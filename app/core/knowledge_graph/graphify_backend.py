"""
Graphify Backend Integration
将 Graphify 集成到 Edu-Sim 系统作为新的图后端
提供持久化、可视化和增量更新能力
"""

import json
import os
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

try:
    import networkx as nx
    from networkx.readwrite import json_graph
except ImportError:
    nx = None


class GraphifyBackend:
    """
    Graphify 后端实现
    
    特性:
    - 持久化存储 (graph.json)
    - 增量更新 (SHA256 缓存)
    - 交互式可视化 (graph.html)
    - 社区发现 (Leiden 算法)
    - 关系溯源 (EXTRACTED/INFERRED)
    """
    
    def __init__(self, storage_path: str = "data/graphify"):
        """
        初始化 Graphify 后端
        
        Args:
            storage_path: 存储路径
        """
        self.storage_path = Path(storage_path)
        self.graph_path = self.storage_path / "graph.json"
        self.cache_path = self.storage_path / "cache"
        self.html_path = self.storage_path / "graph.html"
        
        # 创建目录
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.cache_path.mkdir(exist_ok=True)
        
        # 加载或创建图
        self.graph = None
        self.file_hashes = {}
    
    def initialize(self, config: Dict[str, Any] = None):
        """
        初始化后端（实现 GraphBackend 接口）
        
        Args:
            config: 配置参数
        """
        self.graph = self._load_or_create_graph()
        self.file_hashes = self._load_cache()
    
    def _load_or_create_graph(self):
        """加载现有图谱或创建新图谱"""
        if self.graph_path.exists():
            try:
                with open(self.graph_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if nx:
                    G = json_graph.node_link_graph(data)
                    print(f"✅ 加载现有图谱: {G.number_of_nodes()} 节点, {G.number_of_edges()} 边")
                    return G
                else:
                    print("⚠️  NetworkX 未安装，使用简化模式")
                    return {"nodes": [], "edges": []}
            except Exception as e:
                print(f"⚠️  加载图谱失败: {e}，创建新图谱")
        
        # 创建新图谱
        if nx:
            G = nx.DiGraph()
            print("✅ 创建新图谱")
            return G
        else:
            return {"nodes": [], "edges": []}
    
    def _load_cache(self) -> Dict[str, str]:
        """加载文件哈希缓存"""
        cache_file = self.cache_path / "file_hashes.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_cache(self):
        """保存文件哈希缓存"""
        cache_file = self.cache_path / "file_hashes.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.file_hashes, f, ensure_ascii=False, indent=2)
    
    def _compute_file_hash(self, file_path: str) -> str:
        """计算文件 SHA256 哈希"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def _is_file_changed(self, file_path: str) -> bool:
        """检查文件是否已变更"""
        current_hash = self._compute_file_hash(file_path)
        old_hash = self.file_hashes.get(file_path)
        
        if old_hash != current_hash:
            self.file_hashes[file_path] = current_hash
            return True
        return False
    
    # ==================== 核心操作 ====================
    
    def add_node(self, node_id: str, label: str, properties: Dict[str, Any]):
        """添加节点"""
        if nx:
            self.graph.add_node(node_id, 
                              label=label, 
                              **properties,
                              timestamp=datetime.now().isoformat())
        else:
            # 简化模式
            node = {
                "id": node_id,
                "label": label,
                "properties": properties
            }
            # 检查是否已存在
            existing = [n for n in self.graph["nodes"] if n["id"] == node_id]
            if not existing:
                self.graph["nodes"].append(node)
    
    def add_edge(self, source: str, target: str, relation: str, 
                 properties: Dict[str, Any] = None,
                 confidence: float = 1.0,
                 relation_type: str = "EXTRACTED"):
        """
        添加边
        
        Args:
            source: 源节点ID
            target: 目标节点ID
            relation: 关系类型
            properties: 边属性
            confidence: 置信度 (0-1)
            relation_type: 关系来源 (EXTRACTED/INFERRED/AMBIGUOUS)
        """
        if properties is None:
            properties = {}
        
        if nx:
            self.graph.add_edge(source, target,
                              relation=relation,
                              confidence=confidence,
                              relation_type=relation_type,
                              **properties)
        else:
            edge = {
                "source": source,
                "target": target,
                "relation": relation,
                "properties": properties,
                "confidence": confidence,
                "relation_type": relation_type
            }
            self.graph["edges"].append(edge)
    
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """获取节点"""
        if nx:
            if self.graph.has_node(node_id):
                data = self.graph.nodes[node_id]
                return {
                    "id": node_id,
                    "label": data.get('label', ''),
                    "properties": {k: v for k, v in data.items() 
                                  if k not in ['label']}
                }
        else:
            for node in self.graph.get("nodes", []):
                if node["id"] == node_id:
                    return node
        return None
    
    def get_neighbors(self, node_id: str, relation: str = None,
                     direction: str = "both") -> List[Dict[str, Any]]:
        """获取邻居节点"""
        neighbors = []
        
        if nx:
            if not self.graph.has_node(node_id):
                return []
            
            if direction in ["outgoing", "both"]:
                for neighbor in self.graph.successors(node_id):
                    edge_data = self.graph[node_id][neighbor]
                    if relation is None or edge_data.get('relation') == relation:
                        node_data = self.graph.nodes[neighbor]
                        neighbors.append({
                            "id": neighbor,
                            "label": node_data.get('label', ''),
                            "properties": {k: v for k, v in node_data.items() 
                                          if k not in ['label']},
                            "edge_properties": edge_data
                        })
            
            if direction in ["incoming", "both"]:
                for neighbor in self.graph.predecessors(node_id):
                    edge_data = self.graph[neighbor][node_id]
                    if relation is None or edge_data.get('relation') == relation:
                        node_data = self.graph.nodes[neighbor]
                        neighbors.append({
                            "id": neighbor,
                            "label": node_data.get('label', ''),
                            "properties": {k: v for k, v in node_data.items() 
                                          if k not in ['label']},
                            "edge_properties": edge_data
                        })
        else:
            # 简化模式
            for edge in self.graph.get("edges", []):
                if edge["source"] == node_id and (relation is None or edge["relation"] == relation):
                    neighbors.append({"id": edge["target"]})
                elif edge["target"] == node_id and direction == "both" and (relation is None or edge["relation"] == relation):
                    neighbors.append({"id": edge["source"]})
        
        return neighbors
    
    def get_stats(self) -> Dict[str, Any]:
        """获取图谱统计信息"""
        if nx:
            labels = {}
            for node_id, data in self.graph.nodes(data=True):
                label = data.get('label', 'Unknown')
                labels[label] = labels.get(label, 0) + 1
            
            return {
                "node_count": self.graph.number_of_nodes(),
                "edge_count": self.graph.number_of_edges(),
                "labels": labels
            }
        else:
            labels = {}
            for node in self.graph.get("nodes", []):
                label = node.get("label", "Unknown")
                labels[label] = labels.get(label, 0) + 1
            
            return {
                "node_count": len(self.graph.get("nodes", [])),
                "edge_count": len(self.graph.get("edges", [])),
                "labels": labels
            }
    
    def batch_import(self, nodes: List[Dict[str, Any]], 
                     edges: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        批量导入节点和边
        
        Args:
            nodes: 节点列表
            edges: 边列表
            
        Returns:
            统计信息
        """
        nodes_added = 0
        edges_added = 0
        
        # 批量添加节点
        for node in nodes:
            node_id = node.get('id')
            label = node.get('label', 'Entity')
            properties = node.get('properties', {})
            self.add_node(node_id, label, properties)
            nodes_added += 1
        
        # 批量添加边
        for edge in edges:
            source = edge.get('source_id') or edge.get('source')
            target = edge.get('target_id') or edge.get('target')
            relation = edge.get('relation', 'RELATED')
            properties = edge.get('properties', {})
            confidence = edge.get('confidence', 1.0)
            relation_type = edge.get('relation_type', 'EXTRACTED')
            
            self.add_edge(source, target, relation, properties, confidence, relation_type)
            edges_added += 1
        
        return {
            'nodes_added': nodes_added,
            'edges_added': edges_added
        }
    
    def delete_node(self, node_id: str) -> bool:
        """
        删除节点及其关联的边
        
        Args:
            node_id: 节点ID
            
        Returns:
            是否成功
        """
        if nx:
            if self.graph.has_node(node_id):
                self.graph.remove_node(node_id)
                return True
        else:
            # 简化模式
            self.graph["nodes"] = [n for n in self.graph.get("nodes", []) if n["id"] != node_id]
            self.graph["edges"] = [
                e for e in self.graph.get("edges", []) 
                if e["source"] != node_id and e["target"] != node_id
            ]
            return True
        return False
    
    # ==================== 持久化与可视化 ====================
    
    def save_graph(self):
        """保存图谱到 JSON"""
        if nx:
            data = json_graph.node_link_data(self.graph)
            with open(self.graph_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        else:
            with open(self.graph_path, 'w', encoding='utf-8') as f:
                json.dump(self.graph, f, ensure_ascii=False, indent=2)
        
        # 保存缓存
        self._save_cache()
        print(f"💾 图谱已保存: {self.graph_path}")
    
    def generate_html_visualization(self):
        """生成交互式 HTML 可视化"""
        if not nx:
            print("⚠️  NetworkX 未安装，无法生成可视化")
            return
        
        html_content = self._generate_visjs_html()
        with open(self.html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"🎨 可视化已生成: {self.html_path}")
        print(f"   在浏览器中打开查看交互式图谱")
    
    def _generate_visjs_html(self) -> str:
        """生成基于 vis.js 的 HTML"""
        # 转换图为 vis.js 格式
        nodes = []
        edges = []
        
        for node_id, data in self.graph.nodes(data=True):
            label = data.get('label', node_id)
            nodes.append({
                "id": node_id,
                "label": label,
                "group": label,
                "title": json.dumps({k: v for k, v in data.items() if k != 'label'}, 
                                   ensure_ascii=False, default=str)
            })
        
        for source, target, data in self.graph.edges(data=True):
            relation = data.get('relation', '')
            confidence = data.get('confidence', 1.0)
            rel_type = data.get('relation_type', 'EXTRACTED')
            
            # 根据关系类型设置颜色
            color_map = {
                "EXTRACTED": "#4CAF50",  # 绿色
                "INFERRED": "#FF9800",   # 橙色
                "AMBIGUOUS": "#F44336"   # 红色
            }
            color = color_map.get(rel_type, "#2196F3")
            
            edges.append({
                "from": source,
                "to": target,
                "label": relation,
                "color": {"color": color},
                "title": f"{relation}\n置信度: {confidence:.2f}\n类型: {rel_type}"
            })
        
        html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Edu-Sim Knowledge Graph</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
        }}
        #mynetwork {{
            width: 100vw;
            height: 100vh;
            border: 1px solid lightgray;
        }}
        #info {{
            position: absolute;
            top: 10px;
            right: 10px;
            background: white;
            padding: 15px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            max-width: 300px;
            z-index: 1000;
        }}
        .legend {{
            margin-top: 10px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            margin: 5px 0;
        }}
        .legend-color {{
            width: 20px;
            height: 20px;
            margin-right: 10px;
            border-radius: 3px;
        }}
    </style>
</head>
<body>
    <div id="mynetwork"></div>
    <div id="info">
        <h3>📊 Edu-Sim 知识图谱</h3>
        <p>节点数: {len(nodes)}</p>
        <p>边数: {len(edges)}</p>
        <div class="legend">
            <strong>关系类型:</strong>
            <div class="legend-item">
                <div class="legend-color" style="background: #4CAF50;"></div>
                <span>直接提取 (EXTRACTED)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #FF9800;"></div>
                <span>推断关系 (INFERRED)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #F44336;"></div>
                <span>模糊关系 (AMBIGUOUS)</span>
            </div>
        </div>
        <p style="margin-top: 10px; font-size: 12px; color: #666;">
            💡 提示: 点击节点查看详情，滚轮缩放，拖拽移动
        </p>
    </div>

    <script type="text/javascript">
        var nodes = new vis.DataSet({json.parse(json.dumps(nodes))});
        var edges = new vis.DataSet({json.parse(json.dumps(edges))});

        var container = document.getElementById('mynetwork');
        var data = {{ nodes: nodes, edges: edges }};
        var options = {{
            nodes: {{
                shape: 'dot',
                size: 20,
                font: {{
                    size: 14,
                    face: 'Arial'
                }},
                borderWidth: 2
            }},
            edges: {{
                width: 2,
                smooth: {{
                    type: 'continuous'
                }},
                arrows: {{
                    to: {{
                        enabled: true,
                        scaleFactor: 0.5
                    }}
                }}
            }},
            physics: {{
                stabilization: false,
                barnesHut: {{
                    gravitationalConstant: -2000,
                    springConstant: 0.04,
                    springLength: 95
                }}
            }},
            interaction: {{
                hover: true,
                tooltipDelay: 200
            }}
        }};

        var network = new vis.Network(container, data, options);

        // 点击事件
        network.on("click", function (params) {{
            if (params.nodes.length > 0) {{
                var nodeId = params.nodes[0];
                var node = nodes.get(nodeId);
                console.log('Selected node:', node);
            }}
        }});
    </script>
</body>
</html>"""
        
        return html_template
    
    def export_to_neo4j_cypher(self, output_file: str = None):
        """导出为 Neo4j Cypher 语句"""
        if not nx:
            print("⚠️  NetworkX 未安装")
            return
        
        if output_file is None:
            output_file = self.storage_path / "neo4j.cypher"
        
        cypher_statements = []
        
        # 生成节点创建语句
        for node_id, data in self.graph.nodes(data=True):
            label = data.get('label', 'Entity').replace(' ', '_')
            props = {k: v for k, v in data.items() if k != 'label'}
            
            prop_str = ", ".join([f'{k}: "{v}"' if isinstance(v, str) else f'{k}: {v}' 
                                 for k, v in props.items()])
            
            cypher = f'CREATE (:{label} {{id: "{node_id}"{", " + prop_str if prop_str else ""}}})'
            cypher_statements.append(cypher)
        
        # 生成关系创建语句
        for source, target, data in self.graph.edges(data=True):
            relation = data.get('relation', 'RELATED').upper().replace(' ', '_')
            confidence = data.get('confidence', 1.0)
            
            cypher = f'MATCH (a), (b) WHERE a.id = "{source}" AND b.id = "{target}" CREATE (a)-[:{relation} {{confidence: {confidence}}}]->(b)'
            cypher_statements.append(cypher)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(cypher_statements))
        
        print(f"📤 Neo4j Cypher 已导出: {output_file}")
    
    def close(self):
        """关闭后端（保存数据）"""
        self.save_graph()
        print("✅ Graphify 后端已关闭")
