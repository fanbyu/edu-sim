# Edu-Sim CLI 使用指南

## 📋 概述

Edu-Sim CLI 是基于新架构的教育仿真系统命令行工具，提供完整的数据加载、校准、预测、仿真和查询功能。

---

## 🚀 快速开始

### 安装依赖

```bash
# 确保已安装项目依赖
cd mirofish-main
pip install numpy scipy
```

### 基本用法

```bash
# 查看帮助
python -m app.edu_sim_cli --help

# 查看子命令帮助
python -m app.edu_sim_cli load-data --help
```

---

## 📖 命令详解

### 1. load-data - 加载考试数据

将结构化考试数据加载到知识图谱中。

**用法:**
```bash
python -m app.edu_sim_cli load-data \
  --data-root <数据根目录> \
  --exam-folder <考试文件夹> \
  [--graph-path <图谱路径>]
```

**参数:**
- `--data-root`: 数据根目录（必需）
- `--exam-folder`: 考试文件夹名称（必需）
- `--graph-path`: 图谱存储路径（默认: `data/graphs`）

**示例:**
```bash
python -m app.edu_sim_cli load-data \
  --data-root docs/英语数据 \
  --exam-folder 试题1
```

**输出:**
```
📥 加载考试数据
======================================================================
1️⃣  加载数据: 试题1
   ✓ 作答记录: 27,297
   ✓ 学生数: 1,089
   ✓ 试题数: 27

2️⃣  验证数据质量...
   验证状态: ✅ 通过
   质量评分: 52.1/100

3️⃣  导入到知识图谱...
   ✓ 导入 1,089 个学生节点
   ✓ 导入 27 个试题节点
   ✓ 导入 27,297 条作答记录

📊 图谱统计:
   节点总数: 1,119
   边总数: 27,307

✅ 数据加载完成!
```

---

### 2. calibrate - IRT 参数校准

执行项目反应理论（IRT）参数校准。

**用法:**
```bash
python -m app.edu_sim_cli calibrate \
  [--graph-path <图谱路径>]
```

**参数:**
- `--graph-path`: 图谱存储路径（默认: `data/graphs`）

**说明:**
当前版本需要从原始考试数据文件进行校准。建议先使用 `load-data` 命令加载数据，然后在代码中调用校准服务。

**示例代码:**
```python
from app.core.data_ingestion import ExamDataLoader
from app.services import CalibrationService, GraphService
from app.core.knowledge_graph import GraphEngine

# 1. 加载数据
loader = ExamDataLoader("docs/英语数据")
exam_data = loader.load_exam_data("试题1")

# 2. 初始化服务
engine = GraphEngine(backend_type="json")
engine.initialize()
graph_service = GraphService(engine)
calibration_service = CalibrationService(graph_service)

# 3. 执行校准
report = calibration_service.full_calibration_pipeline(exam_data)
print(f"质量评级: {report['quality_assessment']['overall_rating']}")
```

---

### 3. predict - 预测学习表现

预测学生学习表现并推荐干预策略。

**用法:**
```bash
python -m app.edu_sim_cli predict \
  --student-id <学生ID> \
  [--intervention <干预类型>] \
  [--graph-path <图谱路径>]
```

**参数:**
- `--student-id`: 学生ID（必需）
- `--intervention`: 干预策略类型（可选）
  - `heuristic`: 启发式教学
  - `scaffolding`: 支架式教学
  - `direct_instruction`: 直接指导
  - `emotional_support`: 情感支持
- `--graph-path`: 图谱存储路径（默认: `data/graphs`）

**示例:**
```bash
# 仅预测
python -m app.edu_sim_cli predict --student-id S001

# 预测特定干预效果
python -m app.edu_sim_cli predict \
  --student-id S001 \
  --intervention heuristic
```

**输出:**
```
🔮 学习表现预测
======================================================================
1️⃣  查询学生信息: S001
   ✓ 认知水平: 0.50
   ✓ 焦虑阈值: 0.30
   ✓ 动机水平: 0.80

2️⃣  推荐最优干预策略...
   ✓ 推荐策略: heuristic

   策略排名:
      1. heuristic: 得分 0.2430
      2. scaffolding: 得分 0.2340
      3. emotional_support: 得分 0.1500

3️⃣  预测干预效果: heuristic
   ✓ 能力提升: Δθ = +0.30
   ✓ 焦虑降低: Δanxiety = -0.21
   ✓ 动机提升: Δmotivation = +0.20

✅ 预测完成!
```

---

### 4. simulate - 运行教学仿真

执行多轮教学仿真，模拟干预效果。

**用法:**
```bash
python -m app.edu_sim_cli simulate \
  [--rounds <轮数>] \
  [--intervention <干预类型>] \
  [--output <输出文件>] \
  [--graph-path <图谱路径>]
```

**参数:**
- `--rounds`: 仿真轮数（默认: 5）
- `--intervention`: 干预策略（可选）
- `--output`: 结果输出文件路径（可选）
- `--graph-path`: 图谱存储路径（默认: `data/graphs`）

**示例:**
```bash
# 无干预仿真
python -m app.edu_sim_cli simulate --rounds 5

# 带干预仿真
python -m app.edu_sim_cli simulate \
  --rounds 10 \
  --intervention scaffolding \
  --output results/simulation.json
```

**输出:**
```
🚀 教学仿真
======================================================================
1️⃣  从知识图谱加载 Agents...
   ✓ 图谱节点: 1,121
   ✓ 图谱边: 136,496

2️⃣  初始化 OASIS 仿真器...
   ✓ 学生 Agents: 10
   ✓ 教师 Agents: 1

3️⃣  运行仿真 (10 轮)...

🚀 开始 OASIS 仿真 (共 10 轮)
   干预策略: scaffolding

--- 第 1/10 轮 ---
   📋 应用策略: 支架式教学
   🎯 目标学生: 3 人

--- 第 2/10 轮 ---
...

✅ 仿真完成!
   完成轮数: 10
   应用干预: 3 次

📈 最终指标:
   平均认知水平: 0.24
   平均动机水平: 0.68
   平均焦虑阈值: 0.44

💾 结果已保存到: results/simulation.json
```

---

### 5. query - 查询知识图谱

查询知识图谱中的学生和班级信息。

**用法:**
```bash
python -m app.edu_sim_cli query \
  --type <查询类型> \
  [--id <实体ID>] \
  [--class-name <班级名称>] \
  [--graph-path <图谱路径>]
```

**参数:**
- `--type`: 查询类型（必需）
  - `overview`: 图谱概览
  - `student`: 学生画像
  - `class`: 班级统计
- `--id`: 学生/试题ID（student 类型时需要）
- `--class-name`: 班级名称（class 类型时需要）
- `--graph-path`: 图谱存储路径（默认: `data/graphs`）

**示例:**
```bash
# 图谱概览
python -m app.edu_sim_cli query --type overview

# 查询学生
python -m app.edu_sim_cli query --type student --id S001

# 查询班级
python -m app.edu_sim_cli query --type class --class-name Class_A
```

**输出示例:**

图谱概览:
```
🔍 知识图谱查询
======================================================================
📊 图谱概览:
   节点总数: 1,121
   边总数: 136,496
   标签分布: {'Student': 1,092, 'Item': 28, 'Concept': 1}

✅ 查询完成!
```

学生画像:
```
👨‍🎓 学生画像: S001
   认知水平: 0.50
   焦虑阈值: 0.30
   动机水平: 0.80
   作答记录: 27 条

✅ 查询完成!
```

班级统计:
```
🏫 班级统计: Class_A
   学生数: 56
   平均能力: 0.15
   平均焦虑: 0.45
   平均动机: 0.62

✅ 查询完成!
```

---

## 💡 典型工作流

### 场景 1: 完整数据分析流程

```bash
# 1. 加载数据
python -m app.edu_sim_cli load-data \
  --data-root docs/英语数据 \
  --exam-folder 试题1

# 2. 查询班级情况
python -m app.edu_sim_cli query \
  --type class \
  --class-name 高一550班

# 3. 识别困难学生并预测
python -m app.edu_sim_cli predict \
  --student-id S001 \
  --intervention heuristic

# 4. 运行仿真验证干预效果
python -m app.edu_sim_cli simulate \
  --rounds 10 \
  --intervention heuristic \
  --output results/intervention_test.json
```

---

### 场景 2: 教师备课辅助

```bash
# 1. 查看班级整体情况
python -m app.edu_sim_cli query --type class --class-name Class_A

# 2. 为特定学生制定干预计划
python -m app.edu_sim_cli predict \
  --student-id S001 \
  --intervention scaffolding

# 3. 模拟不同干预策略的效果
python -m app.edu_sim_cli simulate \
  --rounds 5 \
  --intervention scaffolding
```

---

## 🔧 高级用法

### 自定义图谱路径

```bash
python -m app.edu_sim_cli query \
  --type overview \
  --graph-path data/custom_graphs
```

### 导出仿真结果

```bash
python -m app.edu_sim_cli simulate \
  --rounds 10 \
  --output data/simulation_results.json
```

导出的 JSON 文件包含：
- 仿真摘要
- 每轮详细日志
- 最终学生状态

---

## ❓ 常见问题

### Q: 如何查看所有可用命令？

A: 运行 `python -m app.edu_sim_cli --help`

### Q: 数据加载失败怎么办？

A: 检查以下几点：
1. 数据目录是否存在
2. CSV 文件编码是否正确（支持 GBK/UTF-8）
3. 文件格式是否符合要求

### Q: 如何查看学生的详细信息？

A: 使用 `query --type student --id <学生ID>`

### Q: 仿真结果保存在哪里？

A: 如果指定了 `--output` 参数，结果会保存到指定文件；否则仅在控制台显示。

---

## 📚 相关文档

- [Phase 1 总结](PHASE1_SUMMARY.md) - 核心架构
- [Phase 2 总结](PHASE2_SUMMARY.md) - 数据摄入
- [Phase 3 总结](PHASE3_SUMMARY.md) - 仿真引擎
- [Phase 4 总结](PHASE4_SUMMARY.md) - 服务层
- [项目进展总览](../README_PROGRESS.md)

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 改进 CLI 工具！

---

**最后更新**: 2026-04-07  
**版本**: v0.3.0 (with Graphify Integration)
