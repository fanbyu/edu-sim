import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.oasis_profile_generator import OasisAgentProfile

def init_oasis_environment():
    print("--- Edu-Sim OASIS 环境初始化程序 ---")
    
    # 1. 加载带有画像的图谱数据
    graph_path = "data/graphs/edu_complete_graph_v2"
    with open(os.path.join(graph_path, "nodes.json"), "r", encoding="utf-8") as f:
        nodes = json.load(f)

    students_data = [n for n in nodes if n['label'] == 'Student']
    print(f"[正在加载] {len(students_data)} 名学生 Agent 数据...")

    # 2. 模拟 OASIS Agent 实例化过程
    # 在真实的 OASIS 运行中，这里会调用 oasis_engine.register_agent()
    active_agents = []
    
    for data in students_data[:5]: # 先取前5个做演示，避免输出过长
        profile = OasisAgentProfile(
            user_id=int(data['id']),
            user_name=data['name'],
            name=data['name'],
            bio=data.get('summary', ''),
            persona=data.get('summary', ''),
            agent_type="student",
            cognitive_level=data['attributes'].get('cognitive_level', 0),
            learning_style=data['attributes'].get('learning_style', 'visual'),
            anxiety_threshold=data['attributes'].get('anxiety_threshold', 0.5)
        )
        active_agents.append(profile)
        print(f"  -> 已实例化: {profile.name} (能力: {profile.cognitive_level:.2f})")

    # 3. 验证环境状态
    print(f"\n[环境状态检查]")
    print(f"  - 激活 Agent 数: {len(active_agents)}")
    print(f"  - 关联图谱路径: {graph_path}")
    print(f"  - 仿真模式: Parallel Education Simulation")
    
    print(f"\n--- OASIS 环境初始化成功！ ---")
    print("系统已准备好接收教学干预指令并进行平行推演。")

if __name__ == "__main__":
    init_oasis_environment()
