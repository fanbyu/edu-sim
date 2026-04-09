# Edu-Sim 重构架构文档

## 📁 新目录结构

```
app/
├── core/                          # 核心引擎层
│   ├── data_ingestion/            # 数据摄入层
│   │   ├── structured_loader.py   # 结构化数据加载器 (CSV/Excel/JSON)
│   │   └── unstructured_loader.py # 非结构化数据加载器 (PDF/TXT)
│   │
│   ├── knowledge_graph/           # 知识图谱层
│   │   ├── graph_engine.py        # 图引擎抽象层 (GraphBackend)
│   │   ├── backends/              # 后端实现
│   │   │   ├── json_backend.py    # JSON 后端 (开发/测试)
│   │   │   ├── neo4j_backend.py   # Neo4j 后端 (生产环境, TODO)
│   │   │   └── kuzu_backend.py    # Kuzu 后端 (轻量级, TODO)
│   │   ├── ontology/              # 本体管理
│   │   │   └── education_ontology.py  # 教育领域本体定义
│   │   └── query/                 # 查询接口 (TODO)
│   │
│   ├── agent_modeling/            # Agent 建模层
│   │   ├── student_agent.py       # 学生智能体 (集成 IRT)
│   │   ├── teacher_agent.py       # 教师智能体
│   │   └── irt_engine.py          # IRT 计算引擎
│   │
│   └── simulation/                # 仿真引擎 (TODO)
│       ├── oasis_adapter.py       # OASIS 适配器
│       └── intervention_engine.py # 干预引擎
│
├── models/                        # 数据模型层
│   ├── education/                 # 教育领域模型
│   │   ├── student.py             # Student 实体
│   │   ├── teacher.py             # Teacher 实体
│   │   ├── item.py                # Item (试题) 实体
│   │   ├── concept.py             # Concept (知识点) 实体
│   │   └── response.py            # Response (作答记录) 实体
│   └── simulation/                # 仿真模型 (TODO)
│
├── services/                      # 业务服务层 (TODO)
│   ├── graph_service.py           # 图谱服务
│   ├── calibration_service.py     # IRT 校准服务
│   └── prediction_service.py      # 预测服务
│
└── api/                           # API 接口层 (可选, TODO)
    ├── routes/                    # API 路由
    └── schemas/                   # Pydantic 模式
```

## 🎯 核心设计理念

### 1. **分层架构 (Layered Architecture)**

- **数据摄入层**: 统一处理结构化和非结构化数据
- **知识图谱层**: 抽象图数据库操作,支持多后端切换
- **Agent 建模层**: 基于 IRT 和心理特征的智能体
- **仿真引擎层**: 集成 OASIS 进行多智能体仿真

### 2. **依赖倒置 (Dependency Inversion)**

- `GraphBackend` 抽象层允许轻松切换不同的图数据库
- 当前实现 `JSONBackend`,未来可扩展 `Neo4jBackend`、`KuzuBackend`

### 3. **教育领域原生支持**

- **EducationOntology**: 定义教育场景的实体和关系 schema
- **IRT Engine**: 原生集成项目反应理论,支持 1PL/2PL/3PL 模型
- **StudentAgent**: 结合认知能力 (θ) 和心理特征 (焦虑、动机)

## 📊 关键组件说明

### GraphBackend 抽象层

```python
from app.core.knowledge_graph import GraphEngine

# 使用 JSON 后端 (开发环境)
engine = GraphEngine(backend_type="json", config={"storage_path": "data/graphs"})

# 添加节点
engine.add_node("student_001", "Student", {"cognitive_level": 0.5})

# 批量导入 (性能优化)
stats = engine.batch_import(nodes=[...], edges=[...])
```

### Education Ontology

```python
from app.core.knowledge_graph.ontology import EducationOntology

# 验证节点
errors = EducationOntology.validate_node("Student", {"cognitive_level": 0.5})

# 获取所有节点类型
node_types = EducationOntology.get_all_node_types()
# ['Student', 'Teacher', 'Item', 'Concept', 'Class']
```

### IRT Engine

```python
from app.core.agent_modeling import IRTEngine
import numpy as np

# 创建 IRT 引擎 (2PL 模型)
irt = IRTEngine(model_type="2PL")

# 校准参数
response_matrix = np.array([[1, 0, 1], [0, 0, 1], [1, 1, 1]])  # 3学生×3题目
results = irt.calibrate(response_matrix)

print(results['student_thetas'])      # 学生能力值
print(results['item_difficulties'])   # 题目难度
```

### Student Agent

```python
from app.core.agent_modeling import StudentAgent

# 创建学生 Agent
student = StudentAgent(
    student_id="S001",
    cognitive_level=0.5,
    anxiety_threshold=0.3,
    motivation_level=0.8
)

# 预测答对概率
prob = student.predict_response_probability(item_difficulty=0.2)

# 模拟作答
score = student.simulate_response(item_difficulty=0.2)

# 应用教学干预
student.update_after_intervention("heuristic")
```

## 🔄 迁移指南

### 从旧架构迁移

1. **图谱存储**: 
   - 旧: `app/services/graph_storage.py` (JSONStorage)
   - 新: `app/core/knowledge_graph/backends/json_backend.py` (JSONBackend)

2. **数据加载**:
   - 旧: `app/utils/structured_data_loader.py`
   - 新: `app/core/data_ingestion/structured_loader.py` (待实现)

3. **Agent 画像**:
   - 旧: `scripts/generate_agent_profiles.py`
   - 新: `app/core/agent_modeling/student_agent.py`

## 🚀 下一步开发计划

### Phase 2: 数据摄入重构 (1周)
- [ ] 实现 `ExamDataLoader`
- [ ] 实现数据验证器
- [ ] 迁移现有 CSV 解析逻辑

### Phase 3: 仿真引擎适配 (1周)
- [ ] 实现 `OasisAdapter`
- [ ] 实现干预引擎
- [ ] 连接图谱与仿真

### Phase 4: 服务层封装 (1周)
- [ ] 实现 `GraphService`
- [ ] 实现 `CalibrationService`
- [ ] 实现 `PredictionService`

### Phase 5: CLI 重构 (1周)
- [ ] 更新 CLI 命令以使用新架构
- [ ] 编写使用文档

## 💡 优势对比

| 维度 | 旧架构 | 新架构 |
|------|--------|--------|
| **数据存储** | JSON 文件硬编码 | 多后端抽象 (JSON/Neo4j/Kuzu) |
| **教育适配** | 通用本体 | 教育专用本体 + IRT 集成 |
| **Agent 建模** | 简单字典 | 强类型数据类 + 行为方法 |
| **扩展性** | 耦合严重 | 模块化 + 插件化 |
| **可测试性** | 难以单元测试 | 清晰接口,易于 Mock |

## 📝 示例代码

查看 `examples/` 目录中的完整示例:
- `basic_graph_operations.py`: 基础图谱操作
- `irt_calibration_demo.py`: IRT 校准演示
- `student_agent_simulation.py`: 学生 Agent 仿真

---

**注意**: 此重构保持向后兼容,现有脚本仍可运行。建议新功能使用新架构。
