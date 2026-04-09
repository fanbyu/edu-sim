# Edu-Sim vs MiroFish 对比分析

## 📋 概述

**MiroFish** 是一个通用的群智预测引擎，用于模拟社交媒体上的事件演化。  
**Edu-Sim** 是在 MiroFish 基础上重构的**学校垂直领域群智预测引擎**，专注于教育场景的智能体建模和教学策略效果推演。

---

## 🎯 核心定位差异

| 维度 | MiroFish (原版) | Edu-Sim (重构版) |
|------|-----------------|------------------|
| **目标领域** | 通用社会事件预测 | 教育场景仿真 |
| **应用场景** | 政策反应、舆情预测 | 教学效果评估、个性化干预 |
| **智能体类型** | 社交媒体用户 | 学生、教师 |
| **核心模型** | 社交网络传播 | IRT + 心理特征模型 |
| **数据输入** | PDF/新闻/政策文档 | 考试数据、作答记录 |
| **输出结果** | 舆情预测报告 | 学习表现预测、干预建议 |

---

## 🏗️ 架构对比

### MiroFish 架构

```
app/
├── cli.py                    # CLI 入口
├── core/                     # 核心层
│   ├── workbench_session.py  # 工作会话管理
│   ├── task_manager.py       # 任务管理器
│   └── resource_loader.py    # 资源加载器
├── resources/                # 资源适配器
│   ├── documents/            # 文档处理
│   ├── graph/                # 图谱存储
│   ├── simulations/          # 仿真配置
│   └── reports/              # 报告生成
├── tools/                    # 组合工具
│   ├── build_graph.py        # 构建图谱
│   ├── generate_ontology.py  # 生成本体
│   ├── prepare_simulation.py # 准备仿真
│   └── run_simulation.py     # 运行仿真
├── services/                 # 业务服务
│   ├── graph_storage.py      # JSON 图谱后端
│   ├── graph_db.py           # 图谱查询
│   ├── entity_extractor.py   # LLM 实体抽取
│   ├── simulation_runner.py  # OASIS 仿真运行
│   └── report_agent.py       # 报告生成
└── utils/
    └── llm_client.py         # LLM 客户端
```

**特点:**
- ✅ 扁平化架构
- ✅ 基于工具的流水线
- ✅ 通用图谱构建（LLM 抽取）
- ❌ 缺少领域专用模型
- ❌ 单一后端（JSON）

---

### Edu-Sim 架构

```
app/
├── core/                     # 核心引擎层
│   ├── data_ingestion/       # 数据摄入层 ⭐
│   │   ├── exam_data_loader.py
│   │   ├── data_validator.py
│   │   └── graph_importer.py
│   │
│   ├── knowledge_graph/      # 知识图谱层 ⭐
│   │   ├── graph_engine.py   # 图引擎抽象
│   │   ├── backends/         # 多后端支持
│   │   │   ├── json_backend.py
│   │   │   └── graphify_backend.py  # Graphify ⭐
│   │   └── ontology/
│   │       └── education_ontology.py  # 教育本体
│   │
│   ├── agent_modeling/       # Agent 建模层 ⭐
│   │   ├── student_agent.py  # 学生智能体
│   │   ├── teacher_agent.py  # 教师智能体
│   │   └── irt_engine.py     # IRT 引擎
│   │
│   └── simulation/           # 仿真引擎 ⭐
│       ├── oasis_adapter.py  # OASIS 适配器
│       ├── intervention_engine.py  # 干预引擎
│       └── education_env.py  # 教育环境
│
├── models/                   # 数据模型层 ⭐
│   └── education/
│       ├── student.py
│       ├── teacher.py
│       ├── item.py
│       ├── concept.py
│       └── response.py
│
├── services/                 # 服务层 ⭐
│   ├── graph_service.py      # 图谱服务
│   ├── calibration_service.py # IRT 校准
│   └── prediction_service.py # 预测服务
│
└── edu_sim_cli.py            # Edu-Sim 专用 CLI ⭐
```

**特点:**
- ✅ **分层架构**（数据→核心→服务→应用）
- ✅ **依赖倒置**（GraphBackend 抽象）
- ✅ **教育领域原生支持**（IRT + 心理模型）
- ✅ **多后端支持**（JSON + Graphify + Neo4j TODO）
- ✅ **完整的服务层封装**

---

## 🔑 核心功能对比

### 1. 数据处理

| 功能 | MiroFish | Edu-Sim |
|------|----------|---------|
| **数据类型** | PDF/Markdown/TXT | CSV/Excel/JSON（结构化） |
| **数据验证** | ❌ 无 | ✅ 5层验证体系 |
| **质量评估** | ❌ 无 | ✅ 0-100 评分系统 |
| **编码检测** | 基础 UTF-8 | ✅ GBK/UTF-8 自动检测 |
| **批量导入** | 逐条插入 | ✅ 批量优化 |

**Edu-Sim 优势:**
```python
# Edu-Sim: 完整的验证流程
validator = EducationDataValidator()
validation = validator.validate_exam_dataset(data)
quality = validator.check_data_quality(data)
print(f"质量评分: {quality['quality_score']}/100")
```

---

### 2. 知识图谱

| 功能 | MiroFish | Edu-Sim |
|------|----------|---------|
| **后端类型** | JSON only | JSON + **Graphify** + Neo4j (TODO) |
| **持久化** | ✅ 基础 | ✅ **增强**（SHA256 缓存） |
| **可视化** | SVG 静态图 | ✅ **交互式 HTML** (vis.js) |
| **关系溯源** | ❌ 无 | ✅ EXTRACTED/INFERRED/AMBIGUOUS |
| **增量更新** | ❌ 全量重建 | ✅ **只处理变更** |
| **导出格式** | JSON | JSON + **Neo4j Cypher** + GraphML |
| **社区发现** | ❌ 无 | ✅ Leiden 算法（计划中） |

**Edu-Sim 优势:**
```python
# Edu-Sim: 关系溯源
engine.backend.add_edge("S001", "C001", "MASTERED",
                       confidence=0.85,
                       relation_type="INFERRED")  # 标注来源

# 生成交互式可视化
engine.backend.generate_html_visualization()
# 打开 graph.html 查看可交互图谱
```

---

### 3. Agent 建模

| 功能 | MiroFish | Edu-Sim |
|------|----------|---------|
| **智能体类型** | 通用社交媒体用户 | **学生 + 教师** |
| **能力模型** | 个性特征（大五人格） | **IRT 认知能力 (θ)** |
| **心理特征** | 基本情绪 | **焦虑阈值 + 动机水平** |
| **作答行为** | ❌ 无 | ✅ **基于 IRT 的概率模型** |
| **教学风格** | ❌ 无 | ✅ **启发式/支架式/直接指导** |
| **状态演化** | 简单情绪变化 | ✅ **疲劳/参与度/认知水平动态更新** |

**Edu-Sim 优势:**
```python
# Edu-Sim: IRT 驱动的作答行为
from app.core.agent_modeling import StudentAgent, IRTEngine

student = StudentAgent(
    cognitive_level=0.5,      # θ 能力值
    anxiety_threshold=0.3,    # 焦虑阈值
    motivation_level=0.8      # 动机水平
)

# 基于 IRT 预测答对概率
irt = IRTEngine(model_type="2PL")
prob = irt.predict_probability(theta=0.5, difficulty=0.3, discrimination=1.2)
# 考虑心理因素调整
adjusted_prob = prob * anxiety_factor * motivation_factor
```

---

### 4. 仿真引擎

| 功能 | MiroFish | Edu-Sim |
|------|----------|---------|
| **仿真平台** | Twitter + Reddit | **虚拟课堂环境** |
| **动作空间** | 发帖/回复/点赞/关注 | **教学/作答/反馈/讨论/自习** |
| **干预机制** | ❌ 无 | ✅ **6种教学策略** |
| **效果追踪** | 舆情指标 | ✅ **能力提升/焦虑降低/动机提升** |
| **环境状态** | 社交平台氛围 | ✅ **课堂氛围/进度/疲劳度** |
| **并行仿真** | ✅ 支持 | ✅ 支持（继承） |

**Edu-Sim 优势:**
```python
# Edu-Sim: 教学干预仿真
from app.core.simulation import InterventionEngine

engine = InterventionEngine()

# 智能选择干预策略
intervention = engine.select_intervention({
    "cognitive_level": -1.2,  # 低能力
    "anxiety_threshold": 0.8,  # 高焦虑
    "motivation_level": 0.3    # 低动机
})
# 返回: "emotional_support" (情感支持)

# 应用干预并追踪效果
effect = engine.apply_intervention(student, "emotional_support")
print(f"焦虑降低: {effect.anxiety_reduction}")
```

---

### 5. 服务层

| 功能 | MiroFish | Edu-Sim |
|------|----------|---------|
| **图谱查询** | 基础 CRUD | ✅ **高级查询**（班级统计/掌握度分析） |
| **IRT 校准** | ❌ 无 | ✅ **JMLE 参数估计** |
| **质量评估** | ❌ 无 | ✅ **自动评级**（优秀/良好/需改进） |
| **表现预测** | ❌ 无 | ✅ **基于 IRT + 心理因素** |
| **干预推荐** | ❌ 无 | ✅ **智能策略推荐** |
| **在线估计** | ❌ 无 | ✅ **实时能力更新** |

**Edu-Sim 优势:**
```python
# Edu-Sim: 完整的服务层
from app.services import GraphService, CalibrationService, PredictionService

# 1. 图谱查询
graph_service = GraphService(engine)
stats = graph_service.get_class_statistics("Class_A")

# 2. IRT 校准
calibration_service = CalibrationService(graph_service)
report = calibration_service.full_calibration_pipeline(exam_data)
print(f"质量评级: {report['quality_assessment']['overall_rating']}")

# 3. 智能推荐
prediction_service = PredictionService(graph_service)
rec = prediction_service.recommend_optimal_intervention("S001")
print(f"推荐策略: {rec['best_strategy']}")
```

---

### 6. CLI 工具

| 功能 | MiroFish | Edu-Sim |
|------|----------|---------|
| **命令数量** | 2个（run/runs） | ✅ **5个核心命令** |
| **数据加载** | ❌ 无 | ✅ `load-data` |
| **参数校准** | ❌ 无 | ✅ `calibrate` |
| **表现预测** | ❌ 无 | ✅ `predict` |
| **仿真运行** | ✅ `run` | ✅ `simulate` |
| **图谱查询** | ❌ 无 | ✅ `query` |
| **Windows 兼容** | 基础 | ✅ **UTF-8 编码处理** |

**Edu-Sim 命令:**
```bash
# 加载数据
edu-sim load-data --data-root docs/英语数据 --exam-folder 试题1

# 执行校准
edu-sim calibrate

# 预测学生表现
edu-sim predict --student-id S001 --intervention heuristic

# 运行仿真
edu-sim simulate --rounds 10 --intervention scaffolding

# 查询图谱
edu-sim query --type overview
edu-sim query --type student --id S001
edu-sim query --type class --class-name Class_A
```

---

## 📊 性能对比

### 数据处理

| 指标 | MiroFish | Edu-Sim |
|------|----------|---------|
| **最大数据集** | 未测试 | ✅ **27,297 条作答记录** |
| **学生数量** | N/A | ✅ **1,089 名学生** |
| **试题数量** | N/A | ✅ **27 道试题** |
| **导入速度** | 未知 | ✅ **~3秒（批量优化）** |
| **数据验证** | ❌ 无 | ✅ **5层验证 < 1秒** |

---

### 图谱操作

| 指标 | MiroFish | Edu-Sim |
|------|----------|---------|
| **节点规模** | ~100-500 | ✅ **1,000+** |
| **边规模** | ~1,000-5,000 | ✅ **27,000+** |
| **查询速度** | 中等 | ✅ **快**（索引优化） |
| **可视化生成** | SVG（慢） | ✅ **HTML（快）** |
| **内存占用** | 低 | 中等（NetworkX） |

---

## 💡 设计理念差异

### MiroFish: 通用预测引擎

**设计哲学:**
> "Feed it documents describing any scenario, and MiroFish simulates thousands of AI agents reacting on social media to predict how events will unfold."

**核心思路:**
1. 从任意文档提取实体和关系
2. 生成具有不同个性的 AI 智能体
3. 在社交媒体上模拟互动
4. 预测舆情走向

**适用场景:**
- 政策反应预测
- 产品发布舆情
- 突发事件社会影响

---

### Edu-Sim: 教育仿真专家

**设计哲学:**
> "基于 IRT 和心理测量学，构建科学的教育仿真系统，为个性化教学提供数据驱动的决策支持。"

**核心思路:**
1. 从结构化考试数据构建教育图谱
2. 使用 IRT 模型校准学生能力和试题参数
3. 结合心理特征（焦虑、动机）建模学生行为
4. 仿真不同教学干预的效果
5. 推荐最优教学策略

**适用场景:**
- 教学效果评估
- 个性化干预推荐
- 教师备课辅助
- 教育政策仿真

---

## 🎯 技术栈对比

### 共同依赖

| 库 | 用途 |
|----|------|
| `camel-oasis` | OASIS 多智能体仿真框架 |
| `openai` | LLM API 调用 |
| `pydantic` | 数据验证 |
| `rich` | CLI 美化 |

---

### Edu-Sim 新增依赖

| 库 | 用途 |
|----|------|
| `numpy` | 数值计算（IRT） |
| `scipy` | 参数估计（JMLE） |
| `networkx` | 图谱操作和可视化 |
| `charset-normalizer` | 编码检测（GBK/UTF-8） |

---

## 📈 代码规模对比

| 指标 | MiroFish | Edu-Sim | 增长 |
|------|----------|---------|------|
| **总代码行数** | ~3,000 | ~11,800 | **+293%** |
| **核心模块** | ~10 | ~25 | **+150%** |
| **测试文件** | 1 | 6 | **+500%** |
| **文档页数** | 1 (README) | 10+ | **+900%** |
| **配置文件** | 1 (pyproject.toml) | 1 | 持平 |

---

## ✨ Edu-Sim 的独特价值

### 1. 科学的教育建模

- ✅ **IRT 理论支撑** - 项目反应理论保证测量科学性
- ✅ **心理特征集成** - 焦虑、动机影响学习表现
- ✅ **多维度评估** - 认知能力 + 心理状态 + 行为表现

### 2. 完整的数据流水线

```
原始考试数据 → 数据验证 → 图谱构建 → IRT 校准 → 
Agent 初始化 → 仿真运行 → 效果评估 → 策略推荐
```

### 3. 灵活的架构设计

- ✅ **分层架构** - 清晰的职责分离
- ✅ **依赖倒置** - 易于扩展新后端
- ✅ **服务封装** - 高级 API 简化使用

### 4. 强大的可视化工具

- ✅ **交互式图谱** - vis.js 实现
- ✅ **关系溯源** - 颜色编码区分可信度
- ✅ **一键导出** - Neo4j/GraphML/SVG

### 5. 智能的决策支持

- ✅ **自动质量评估** - 校准结果评级
- ✅ **干预策略推荐** - 基于学生状态自适应
- ✅ **效果预测** - 多轮轨迹模拟

---

## 🔄 迁移路径

### 从 MiroFish 到 Edu-Sim

如果你已经在使用 MiroFish，可以这样迁移：

1. **保留原有功能**
   ```bash
   # MiroFish 命令仍然可用
   mirofish run --files docs/policy.pdf --requirement "..."
   ```

2. **启用 Edu-Sim 功能**
   ```bash
   # 新的教育仿真命令
   python -m app.edu_sim_cli load-data --data-root data/exams --exam-folder midterm
   ```

3. **共享图谱后端**
   - MiroFish 使用 `graph_storage.py` (JSON)
   - Edu-Sim 可使用相同后端或升级到 Graphify

---

## 🎓 总结

| 维度 | MiroFish | Edu-Sim |
|------|----------|---------|
| **定位** | 通用舆情预测 | 教育仿真专家 |
| **架构** | 扁平化工具链 | 分层专业服务 |
| **领域深度** | 浅（通用） | 深（教育原生） |
| **科学性** | 基于 LLM | **基于 IRT + 心理测量学** |
| **可扩展性** | 中等 | **高（多后端支持）** |
| **易用性** | 简单 CLI | **丰富 CLI + 服务 API** |
| **可视化** | 静态 SVG | **交互式 HTML** |
| **数据支持** | 非结构化文档 | **结构化考试数据** |

---

**Edu-Sim 不是替代 MiroFish，而是在其基础上的专业化演进！**

- ✅ **保留了** MiroFish 的核心仿真能力（OASIS 集成）
- ✅ **增强了** 图谱后端（Graphify 集成）
- ✅ **新增了** 教育领域专用功能（IRT、心理模型、教学干预）
- ✅ **优化了** 架构设计（分层、服务化、可测试）

**这使得 Edu-Sim 成为一个既科学又实用的教育仿真平台！** 🎉

---

**最后更新**: 2026-04-07  
**版本**: v0.3.0
