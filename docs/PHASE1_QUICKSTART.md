# Edu-Sim Phase 1 - 快速开始指南

## 📋 前置要求

确保已安装以下依赖：

```bash
pip install numpy scipy
```

---

## 🧪 运行测试

### 完整测试套件

```bash
python tests/test_new_architecture.py
```

**预期输出：**
```
🧪 Edu-Sim 新架构测试套件

✅ GraphBackend 测试通过!
✅ EducationOntology 测试通过!
✅ IRTEngine 测试通过!
✅ StudentAgent 测试通过!
✅ Data Models 测试通过!

🎉 所有测试通过!
```

---

## 🚀 运行功能演示

### 交互式演示

```bash
python demo_phase1.py
```

**演示内容包括：**
1. 📊 知识图谱构建与查询
2. 📐 IRT 参数校准
3. 👨‍🎓 学生智能体仿真
4. 👩‍🏫 教师智能体决策
5. 💾 结构化数据模型

---

## 📁 项目结构

```
app/
├── core/
│   ├── knowledge_graph/          # 知识图谱层
│   │   ├── graph_engine.py       # 图引擎抽象 + 工厂类
│   │   ├── backends/
│   │   │   └── json_backend.py   # JSON 后端实现
│   │   └── ontology/
│   │       └── education_ontology.py  # 教育本体定义
│   │
│   └── agent_modeling/           # Agent 建模层
│       ├── irt_engine.py         # IRT 计算引擎
│       ├── student_agent.py      # 学生智能体
│       └── teacher_agent.py      # 教师智能体
│
└── models/education/             # 数据模型层
    ├── student.py                # Student 实体
    ├── teacher.py                # Teacher 实体
    ├── item.py                   # Item 实体
    ├── concept.py                # Concept 实体
    └── response.py               # Response 实体

tests/
└── test_new_architecture.py      # 测试套件

docs/
├── REFACTORING_ARCHITECTURE.md   # 架构设计文档
└── PHASE1_SUMMARY.md             # Phase 1 总结

demo_phase1.py                    # 功能演示脚本
```

---

## 💡 代码示例

### 1. 使用知识图谱

```python
from app.core.knowledge_graph import GraphEngine

# 初始化
engine = GraphEngine(backend_type="json", config={"storage_path": "data/graph"})
engine.initialize()

# 添加节点
engine.add_node("student_001", "Student", {"cognitive_level": 0.6})
engine.add_node("item_001", "Item", {"difficulty": 0.2})

# 建立关系
engine.add_edge("student_001", "item_001", "ATTEMPTED", {"score": 1.0})

# 查询统计
stats = engine.get_stats()
print(f"节点数: {stats['node_count']}, 边数: {stats['edge_count']}")

# 清理
engine.close()
```

### 2. 使用 IRT 引擎

```python
from app.core.agent_modeling import IRTEngine
import numpy as np

# 创建引擎
irt = IRTEngine(model_type="2PL")

# 准备作答数据 (N学生 × M题目)
response_matrix = np.array([
    [1.0, 0.0, 1.0],
    [0.0, 0.0, 1.0],
    [1.0, 1.0, 1.0]
])

# 校准参数
results = irt.calibrate(response_matrix)

print(f"学生能力: {results['student_thetas']}")
print(f"题目难度: {results['item_difficulties']}")

# 预测概率
prob = irt.predict_probability(theta=0.5, difficulty=0.0)
print(f"答对概率: {prob:.2%}")
```

### 3. 使用学生智能体

```python
from app.core.agent_modeling import StudentAgent

# 创建学生
student = StudentAgent(
    student_id="S001",
    name="张三",
    cognitive_level=0.5,
    anxiety_threshold=0.3,
    motivation_level=0.8
)

# 预测答对概率
prob = student.predict_response_probability(item_difficulty=0.2)
print(f"答对概率: {prob:.2%}")

# 模拟作答
score = student.simulate_response(item_difficulty=0.2)
print(f"得分: {score}")

# 应用干预
student.update_after_intervention("heuristic")
print(f"干预后焦虑: {student.anxiety_threshold:.2f}")
```

### 4. 使用教师智能体

```python
from app.core.agent_modeling import TeacherAgent

# 创建教师
teacher = TeacherAgent(
    teacher_id="T001",
    name="王老师",
    teaching_style="supportive",
    experience_years=10
)

# 根据学生状态选择干预策略
intervention = teacher.select_intervention(
    anxiety=0.8,
    motivation=0.3,
    performance=0.4
)
print(f"推荐干预: {intervention}")  # emotional_support
```

---

## 🔍 常见问题

### Q: 如何切换到 Neo4j 后端？

A: 目前 Neo4j 后端尚未实现。待实现后，只需修改初始化代码：

```python
engine = GraphEngine(backend_type="neo4j", config={
    "uri": "bolt://localhost:7687",
    "username": "neo4j",
    "password": "your_password"
})
```

### Q: IRT 校准结果异常怎么办？

A: 检查以下几点：
1. 作答矩阵是否包含足够的变化（不要全对或全错）
2. 样本量是否足够（建议至少 30 学生 × 10 题目）
3. 查看是否有数值溢出警告

### Q: 如何保存和加载图谱？

A: JSON 后端会自动保存到文件：

```python
# 保存（自动）
engine.close()  # 数据已持久化到 data/graph/

# 加载（重新初始化即可）
engine = GraphEngine(backend_type="json", config={"storage_path": "data/graph"})
engine.initialize()  # 自动加载已有数据
```

---

## 📚 相关文档

- [架构设计文档](REFACTORING_ARCHITECTURE.md) - 详细的设计理念和目录结构
- [Phase 1 总结](PHASE1_SUMMARY.md) - 完成情况和关键技术亮点

---

## 🎯 下一步

完成 Phase 1 后，可以继续：

1. **Phase 2**: 实现数据摄入模块，支持 CSV/Excel 考试数据解析
2. **Phase 3**: 开发仿真引擎，对接 OASIS 平台
3. **Phase 4**: 实现四维效能评估报告生成

详见 [REFACTORING_ARCHITECTURE.md](REFACTORING_ARCHITECTURE.md) 中的路线图。

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**最后更新**: 2026-04-07
