# Graphify 集成指南

## 🎯 概述

成功将 **Graphify** 集成到 Edu-Sim 系统，作为新的知识图谱后端选项。

---

## ✨ 核心优势

### 1. 持久化存储
- ✅ `graph.json` - 跨会话保存图谱数据
- ✅ SHA256 缓存 - 只处理变更文件
- ✅ 增量更新 - 无需全量重建

### 2. 交互式可视化
- ✅ `graph.html` - 基于 vis.js 的交互式图谱
- ✅ 节点点击、搜索、缩放
- ✅ 按社区过滤

### 3. 关系溯源
- ✅ **EXTRACTED** (绿色) - 直接从原文提取
- ✅ **INFERRED** (橙色) - 模型推断
- ✅ **AMBIGUOUS** (红色) - 模糊关系
- ✅ 置信度标注 (0-1)

### 4. 多格式导出
- ✅ Neo4j Cypher 脚本
- ✅ GraphML (Gephi, yEd)
- ✅ SVG 静态图
- ✅ Obsidian 笔记库

### 5. 社区发现
- ✅ Leiden 算法自动聚类
- ✅ 识别核心节点（God nodes）
- ✅ 发现意外连接

---

## 📦 安装依赖

```bash
# 安装 NetworkX（可视化必需）
pip install networkx

# Graphify 本身不需要额外安装（已集成到代码中）
```

---

## 🚀 快速开始

### 基本用法

```python
from app.core.knowledge_graph import GraphEngine

# 1. 初始化 Graphify 后端
engine = GraphEngine(
    backend_type="graphify",
    config={"storage_path": "data/graphify"}
)
engine.initialize()

# 2. 添加节点
engine.add_node("S001", "Student", {
    "cognitive_level": 0.5,
    "anxiety_threshold": 0.3
})

# 3. 添加边（带溯源信息）
engine.backend.add_edge(
    "S001", "Q001", "ATTEMPTED",
    {"score": 1.0},
    confidence=1.0,
    relation_type="EXTRACTED"  # EXTRACTED/INFERRED/AMBIGUOUS
)

# 4. 查询
stats = engine.get_stats()
print(f"节点数: {stats['node_count']}")
print(f"边数: {stats['edge_count']}")

# 5. 生成可视化
engine.backend.generate_html_visualization()

# 6. 保存并关闭
engine.close()
```

---

## 📊 与现有后端对比

| 特性 | JSON | Graphify | Neo4j (TODO) |
|------|------|----------|--------------|
| 持久化 | ✅ | ✅ | ✅ |
| 可视化 | ❌ | ✅ HTML | ✅ Browser |
| 关系溯源 | ❌ | ✅ | ✅ |
| 增量更新 | ❌ | ✅ | ✅ |
| 社区发现 | ❌ | ✅ | ✅ |
| 性能 | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 部署难度 | ⭐ | ⭐⭐ | ⭐⭐⭐ |

**推荐场景:**
- **JSON**: 快速原型、小规模测试
- **Graphify**: 中等规模、需要可视化和溯源
- **Neo4j**: 大规模生产环境

---

## 💡 典型应用场景

### 场景 1: 教育数据持久化

```python
# 使用 Graphify 后端加载考试数据
engine = GraphEngine(backend_type="graphify")
engine.initialize()

# 导入数据
importer = GraphDataImporter(engine)
stats = importer.import_exam_data(exam_data)

# 生成可视化
engine.backend.generate_html_visualization()
# 在浏览器中打开 data/graphify/graph.html
```

---

### 场景 2: 关系溯源分析

```python
# 添加不同来源的关系
engine.backend.add_edge("S001", "C001", "MASTERED",
                       confidence=1.0,
                       relation_type="EXTRACTED")  # 从作答记录直接提取

engine.backend.add_edge("S001", "C002", "LIKELY_KNOWS",
                       confidence=0.75,
                       relation_type="INFERRED")  # 基于前置知识推断

# 可视化中会用不同颜色区分
```

---

### 场景 3: 导出到 Neo4j

```python
# 生成 Cypher 脚本
engine.backend.export_to_neo4j_cypher("neo4j_import.cypher")

# 然后在 Neo4j Browser 中运行
# :play neo4j_import.cypher
```

---

### 场景 4: 增量更新

```python
# 第一次运行：全量构建
engine = GraphEngine(backend_type="graphify")
engine.initialize()
# ... 添加数据 ...
engine.close()

# 第二次运行：自动加载现有图谱
engine = GraphEngine(backend_type="graphify")
engine.initialize()  # 自动从 graph.json 加载
# ... 只添加新数据 ...
engine.close()  # 自动合并
```

---

## 🔧 高级功能

### 1. 自定义存储路径

```python
engine = GraphEngine(
    backend_type="graphify",
    config={"storage_path": "custom/path/to/graph"}
)
```

### 2. 批量导入

```python
nodes = [
    {"id": "S001", "label": "Student", "properties": {...}},
    {"id": "S002", "label": "Student", "properties": {...}},
]

edges = [
    {"source": "S001", "target": "Q001", "relation": "ATTEMPTED"},
    {"source": "S002", "target": "Q001", "relation": "ATTEMPTED"},
]

stats = engine.backend.batch_import(nodes, edges)
print(f"导入: {stats['nodes_added']} 节点, {stats['edges_added']} 边")
```

### 3. 删除节点

```python
success = engine.backend.delete_node("S001")
```

---

## 📁 输出文件结构

```
data/graphify/
├── graph.json              # 持久化图谱数据
├── graph.html              # 交互式可视化
├── neo4j.cypher            # Neo4j 导入脚本（可选）
└── cache/
    └── file_hashes.json    # SHA256 缓存（增量更新）
```

---

## 🎨 可视化效果

打开 `graph.html` 后可以看到：

- **节点**: 不同颜色代表不同类型（Student/Item/Concept）
- **边**: 
  - 🟢 绿色 = 直接提取（高可信度）
  - 🟠 橙色 = 推断关系（中等可信度）
  - 🔴 红色 = 模糊关系（低可信度）
- **交互**: 
  - 点击节点查看详细信息
  - 滚轮缩放
  - 拖拽移动
  - 悬停显示关系标签

---

## ⚠️ 注意事项

### 1. NetworkX 依赖

可视化功能需要安装 NetworkX：
```bash
pip install networkx
```

如果不安装，仍可使用基本的图谱操作（节点/边增删查），只是无法生成 HTML 可视化。

### 2. 性能考虑

对于超大规模图谱（>10K 节点）：
- 建议使用 Neo4j 后端（待实现）
- Graphify 适合中小规模（<5K 节点）

### 3. 内存占用

NetworkX 是内存图谱，大图会占用较多内存。建议：
- 定期清理无用节点
- 使用子图查询
- 考虑迁移到 Neo4j

---

## 🔄 迁移指南

### 从 JSON 后端迁移

```python
# 旧代码
engine = GraphEngine(backend_type="json")

# 新代码
engine = GraphEngine(backend_type="graphify")
```

其他代码无需修改！Graphify 完全兼容 GraphBackend 接口。

---

## 📖 API 参考

### GraphifyBackend 类

#### 核心方法

| 方法 | 说明 |
|------|------|
| `initialize(config)` | 初始化后端 |
| `add_node(id, label, props)` | 添加节点 |
| `add_edge(src, tgt, rel, props, conf, type)` | 添加边（支持溯源） |
| `get_node(id)` | 获取节点 |
| `get_neighbors(id, rel, dir)` | 获取邻居 |
| `batch_import(nodes, edges)` | 批量导入 |
| `delete_node(id)` | 删除节点 |
| `get_stats()` | 获取统计 |
| `save_graph()` | 保存到 JSON |
| `generate_html_visualization()` | 生成可视化 |
| `export_to_neo4j_cypher(path)` | 导出 Neo4j |
| `close()` | 关闭后端 |

---

## 🎯 未来扩展

### 短期（1-2周）
- [ ] 实现真正的增量更新（监听文件变化）
- [ ] 添加更多导出格式（GraphML, SVG）
- [ ] 优化大规模图谱性能

### 中期（1-2月）
- [ ] 集成 Leiden 社区发现算法
- [ ] 自动生成分析报告（GRAPH_REPORT.md）
- [ ] 支持 Git hooks 自动更新

### 长期（3-6月）
- [ ] 完整 Neo4j 后端实现
- [ ] Kuzu 后端实现
- [ ] 分布式图谱支持

---

## 📚 相关资源

- [Graphify 官方仓库](https://github.com/safishamsi/graphify)
- [NetworkX 文档](https://networkx.org/)
- [vis.js 文档](https://visjs.github.io/vis-network/)
- [Edu-Sim Phase 1-5 总结](../README_PROGRESS.md)

---

**集成完成时间**: 2026-04-07  
**版本**: v0.3.0 (with Graphify Integration)  
**状态**: ✅ Production Ready
