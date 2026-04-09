# Edu-Sim 教育群智预测引擎

> 面向学校垂直领域的智能决策支持系统。通过模拟学生、教师等多角色智能体的交互演化，预测教学策略、考试改革及校园政策的实施效果。

**版本**: v0.3.0 | **状态**: ✅ Production Ready

---

## 🎯 项目简介

Edu-Sim 是一个专业的**学校垂直领域群智预测引擎**。它利用 AI 智能体模拟学校生态中的各类角色（学生、教师、家长），通过构建教育知识图谱和仿真教学互动，预测教育改革、教学策略或校园事件在特定群体中的演化趋势与最终效果。

### 为什么是“群智预测”？

在学校场景中，单一维度的预测往往失效，因为教育是一个复杂的**社会-心理系统**。Edu-Sim 的“群智”体现在：

*   **🔮 趋势预测：** 提前预判教学改革在学生群体中的接受度与成效。
*   **🧠 群智涌现：** 捕捉个体行为汇聚成的集体学习风潮或潜在风险。
*   **🎓 精准干预：** 基于 IRT 和心理模型，为每个学生生成最优成长路径。

### 核心特色

✅ **多元主体博弈** - 模拟学生适应、教师反应及家长焦虑的复杂互动  
✅ **动态知识图谱** - 追踪“学生-知识点-掌握度”的动态演化路径  
✅ **平行仿真推演** - 寻找最可能发生的“未来分支”并评估置信度  
✅ **通用 LLM 驱动** - 支持 Qwen、豆包等国内主流大模型  
✅ **闭环反馈机制** - 根据预测结果自动推荐最优干预策略  

---

## 🚀 快速开始

### 环境要求

- Python 3.11-3.12
- [uv](https://docs.astral.sh/uv/) (Python 包管理器)

### 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/fanbyu/edu-sim.git
cd edu-sim

# 2. 配置环境变量
cp .env.example .env

# 3. 安装依赖
uv sync
```

### 配置 LLM 提供商

编辑 `.env` 文件，选择你喜欢的 LLM 提供商：

```env
# 选项 1: 通义千问（推荐，国内访问快）
LLM_PROVIDER=qwen
OPENAI_API_KEY=sk-your-qwen-api-key

# 选项 2: 豆包
LLM_PROVIDER=doubao
OPENAI_API_KEY=your-doubao-api-key

# 选项 3: OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-key

# 选项 4: Claude Code CLI（默认）
LLM_PROVIDER=claude-cli
```

详细配置指南见：[LLM 提供商配置指南](docs/LLM_PROVIDERS_GUIDE.md)

---

## 💡 核心功能

### 1️⃣ 数据加载与验证

从结构化考试数据构建教育知识图谱：

```bash
python -m app.edu_sim_cli load-data \
  --data-root docs/英语数据 \
  --exam-folder 试题1
```

**特性:**
- ✅ 自动检测编码（GBK/UTF-8）
- ✅ 5层数据验证体系
- ✅ 质量评分（0-100）
- ✅ 批量导入优化

---

### 2️⃣ IRT 参数校准

校准学生能力值和试题参数：

```bash
python -m app.edu_sim_cli calibrate
```

**输出:**
- 学生能力分布 (θ)
- 试题难度、区分度
- 自动质量评级（优秀/良好/需改进）

---

### 3️⃣ 学习表现预测

预测学生在特定试题上的表现：

```bash
python -m app.edu_sim_cli predict \
  --student-id S001 \
  --intervention heuristic
```

**输出:**
- 答对概率（考虑焦虑、动机）
- 最优干预策略推荐
- 能力提升预测

---

### 4️⃣ 教学仿真

运行多轮教学干预仿真：

```bash
python -m app.edu_sim_cli simulate \
  --rounds 10 \
  --intervention scaffolding \
  --output results/simulation.json
```

**支持的干预策略:**
- 🎯 启发式教学 (heuristic)
- 🏗️ 支架式教学 (scaffolding)
- 📖 直接指导 (direct_instruction)
- 💝 情感支持 (emotional_support)
- 👥 同伴学习 (peer_learning)
- 📝 自适应练习 (adaptive_practice)

---

### 5️⃣ 知识图谱查询

查询学生、班级、知识点信息：

```bash
# 图谱概览
python -m app.edu_sim_cli query --type overview

# 学生画像
python -m app.edu_sim_cli query --type student --id S001

# 班级统计
python -m app.edu_sim_cli query --type class --class-name Class_A
```

---

## 📊 典型工作流

### 场景 1: 教师备课辅助

```bash
# 1. 加载考试数据
python -m app.edu_sim_cli load-data \
  --data-root data/exams \
  --exam-folder midterm

# 2. 查看班级情况
python -m app.edu_sim_cli query \
  --type class \
  --class-name 高一550班

# 3. 识别困难学生并推荐干预
python -m app.edu_sim_cli predict \
  --student-id S001 \
  --intervention heuristic

# 4. 仿真验证干预效果
python -m app.edu_sim_cli simulate \
  --rounds 10 \
  --intervention heuristic
```

---

### 场景 2: 教育研究实验

```bash
# 实验组 1: 启发式教学
python -m app.edu_sim_cli simulate \
  --rounds 20 \
  --intervention heuristic \
  --output results/exp1_heuristic.json

# 实验组 2: 支架式教学
python -m app.edu_sim_cli simulate \
  --rounds 20 \
  --intervention scaffolding \
  --output results/exp2_scaffolding.json

# 对比分析两组结果
python scripts/compare_experiments.py \
  --exp1 results/exp1_heuristic.json \
  --exp2 results/exp2_scaffolding.json
```

---

## 🏗️ 系统架构

```
Edu-Sim 架构
│
├── 应用层 (Application)
│   ├── edu_sim_cli.py          # CLI 工具（5个核心命令）
│   └── api/                    # REST API（可选）
│
├── 服务层 (Services) ⭐
│   ├── GraphService            # 图谱查询服务
│   ├── CalibrationService      # IRT 校准服务
│   └── PredictionService       # 预测服务
│
├── 核心引擎层 (Core Engine)
│   ├── knowledge_graph/        # 知识图谱
│   │   ├── graph_engine.py     # 图引擎抽象
│   │   ├── backends/           # 多后端支持
│   │   │   ├── json_backend.py
│   │   │   └── graphify_backend.py  # Graphify ⭐
│   │   └── ontology/
│   │       └── education_ontology.py
│   │
│   ├── agent_modeling/         # Agent 建模
│   │   ├── student_agent.py    # 学生智能体
│   │   ├── teacher_agent.py    # 教师智能体
│   │   └── irt_engine.py       # IRT 引擎
│   │
│   ├── simulation/             # 仿真引擎
│   │   ├── oasis_adapter.py    # OASIS 适配器
│   │   ├── intervention_engine.py  # 干预引擎
│   │   └── education_env.py    # 教育环境
│   │
│   └── data_ingestion/         # 数据摄入
│       ├── exam_data_loader.py
│       ├── data_validator.py
│       └── graph_importer.py
│
└── 数据模型层 (Models)
    └── education/
        ├── student.py
        ├── teacher.py
        ├── item.py
        ├── concept.py
        └── response.py
```

---

## 🎨 可视化功能

### 交互式知识图谱

生成基于 vis.js 的交互式图谱：

```python
from app.core.knowledge_graph import GraphEngine

engine = GraphEngine(backend_type="graphify")
engine.initialize()
# ... 添加数据 ...
engine.backend.generate_html_visualization()
# 打开 data/graphify/graph.html 查看
```

**特性:**
- 🖱️ 点击节点查看详情
- 🔍 滚轮缩放
- ✋ 拖拽移动
- 🎨 颜色编码关系类型
  - 🟢 绿色 = 直接提取（高可信度）
  - 🟠 橙色 = 推断关系（中等可信度）
  - 🔴 红色 = 模糊关系（低可信度）

---

## 📚 文档

### 核心文档

- 📖 [项目进展总览](README_PROGRESS.md) - 完整的开发历程
- 📖 [重构架构文档](docs/REFACTORING_ARCHITECTURE.md) - 技术架构详解
- 📖 [Edu-Sim vs MiroFish](docs/EDU_SIM_VS_MIROFISH.md) - 功能对比

### 使用指南

- 📖 [CLI 使用指南](docs/CLI_USAGE_GUIDE.md) - 命令行工具详解
- 📖 [LLM 提供商配置](docs/LLM_PROVIDERS_GUIDE.md) - Qwen/豆包/OpenAI 配置
- 📖 [Graphify 集成指南](docs/GRAPHIFY_INTEGRATION.md) - 图谱持久化与可视化

### 阶段总结

- 📖 [Phase 1: 核心架构](docs/PHASE1_SUMMARY.md)
- 📖 [Phase 2: 数据摄入](docs/PHASE2_SUMMARY.md)
- 📖 [Phase 3: 仿真引擎](docs/PHASE3_SUMMARY.md)
- 📖 [Phase 4: 服务层](docs/PHASE4_SUMMARY.md)
- 📖 [Phase 5: CLI 重构](docs/PHASE5_SUMMARY.md)
- 📖 [Graphify 集成](docs/GRAPHIFY_SUMMARY.md)

---

## 🧪 测试

运行完整的测试套件：

```bash
# Phase 1-2 测试
python tests/test_new_architecture.py
python tests/test_phase2_data_ingestion.py

# Phase 3 测试
python tests/test_phase3_simulation.py

# Phase 4 测试
python tests/test_phase4_services.py

# Phase 5 测试
python tests/test_phase5_cli.py

# Graphify 测试
python tests/test_graphify_integration.py

# LLM 提供商测试
python tests/test_universal_llm.py
```

---

## 🌟 核心优势

### 1. 科学的教育建模

```python
# IRT 模型预测答对概率
P(答对) = 1 / (1 + exp(-a * (θ - b)))

# 考虑心理因素调整
adjusted_P = P(答对) × anxiety_factor × motivation_factor
```

### 2. 智能干预推荐

根据学生状态自动选择最优策略：
- 低能力学生 → 能力提升优先
- 高焦虑学生 → 降低焦虑优先
- 低动机学生 → 提升动机优先

### 3. 完整的数据流水线

```
原始数据 → 验证 → 图谱构建 → IRT校准 → 
Agent初始化 → 仿真 → 效果评估 → 策略推荐
```

### 4. 灵活的架构设计

- ✅ 分层架构 - 清晰的职责分离
- ✅ 依赖倒置 - 易于扩展新后端
- ✅ 服务封装 - 高级 API 简化使用

---

## 🔄 从 MiroFish 迁移

Edu-Sim 基于 [MiroFish](https://github.com/666ghj/MiroFish) 重构，保留了原有的 OASIS 仿真能力，同时增加了教育领域专用功能。

**兼容性:**
- ✅ 保留 MiroFish 的核心仿真引擎
- ✅ 扩展图谱后端（Graphify 集成）
- ✅ 新增教育专用 CLI 命令
- ✅ 完全向后兼容

你可以同时使用两个系统：

```bash
# MiroFish 原有功能
mirofish run --files docs/policy.pdf --requirement "..."

# Edu-Sim 新增功能
python -m app.edu_sim_cli load-data --data-root data/exams --exam-folder midterm
```

详细对比见：[Edu-Sim vs MiroFish](docs/EDU_SIM_VS_MIROFISH.md)

---

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目采用 AGPL-3.0 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

- [MiroFish](https://github.com/666ghj/MiroFish) by 666ghj - 原始项目
- [OASIS](https://github.com/camel-ai/oasis) by CAMEL-AI - 多智能体仿真框架
- [Graphify](https://github.com/safishamsi/graphify) - 知识图谱工具
- [NetworkX](https://networkx.org/) - 图计算库
- [vis.js](https://visjs.github.io/vis-network/) - 交互式可视化

---

## 📧 联系方式

- 📮 GitHub Issues: [提交问题](https://github.com/fanbyu/edu-sim/issues)
- 🌐 项目主页: https://github.com/fanbyu/edu-sim

---

**最后更新**: 2026-04-07  
**版本**: v0.3.0  
**状态**: ✅ Production Ready

⭐ 如果这个项目对你有帮助，请给个 Star！
