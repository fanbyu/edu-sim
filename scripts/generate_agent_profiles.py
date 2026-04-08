import sys
import os
import json
import subprocess
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def generate_agent_profiles():
    print("--- Edu-Sim Agent 画像生成程序 ---")
    
    # 1. 加载图谱数据
    graph_path = "data/graphs/edu_complete_graph_v2"
    with open(os.path.join(graph_path, "nodes.json"), "r", encoding="utf-8") as f:
        nodes = json.load(f)

    students = [n for n in nodes if n['label'] == 'Student']
    print(f"[正在处理] {len(students)} 名学生 Agent...")

    # 2. 定义画像模板
    styles = ["Visual (视觉型)", "Auditory (听觉型)", "Kinesthetic (动觉型)", "Logical (逻辑型)"]
    personalities = ["Perfectionist (完美主义)", "Easy-going (随和)", "Anxious (易焦虑)", "Confident (自信)"]
    
    # 3. 循环生成并更新
    for student in students:
        theta = student['attributes'].get('cognitive_level', 0.0)
        
        # 简单的规则引擎 + 随机性模拟 LLM 的多样性
        # 在实际生产中，这里会调用 claude-cli 生成更复杂的描述
        if theta > 1.0:
            style = random.choice(["Logical (逻辑型)", "Visual (视觉型)"])
            personality = "Confident (自信)"
            motivation = round(random.uniform(0.7, 1.0), 2)
            anxiety = round(random.uniform(0.1, 0.4), 2)
        elif theta < -1.0:
            style = random.choice(["Kinesthetic (动觉型)", "Auditory (听觉型)"])
            personality = "Anxious (易焦虑)"
            motivation = round(random.uniform(0.3, 0.6), 2)
            anxiety = round(random.uniform(0.6, 0.9), 2)
        else:
            style = random.choice(styles)
            personality = random.choice(personalities)
            motivation = round(random.uniform(0.5, 0.8), 2)
            anxiety = round(random.uniform(0.3, 0.6), 2)

        # 更新节点属性
        student['attributes']['learning_style'] = style
        student['attributes']['personality'] = personality
        student['attributes']['motivation_level'] = motivation
        student['attributes']['anxiety_threshold'] = anxiety
        
        # 生成简短的 Agent Summary
        student['summary'] = f"一名{personality.split('(')[0]}的学生，认知能力值为 {theta:.2f}，倾向于{style.split('(')[0]}学习。"

    # 4. 保存更新后的图谱
    print("[正在保存更新后的图谱...]")
    with open(os.path.join(graph_path, "nodes.json"), "w", encoding="utf-8") as f:
        json.dump(nodes, f, ensure_ascii=False, indent=2)

    print(f"\n--- Agent 画像生成完成！ ---")
    print(f"示例画像 (Student_{students[0]['id']}):")
    print(json.dumps(students[0]['attributes'], indent=2, ensure_ascii=False))

if __name__ == "__main__":
    generate_agent_profiles()
