import sys
import os
import json
import subprocess
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def generate_profile_with_llm(theta):
    """调用 claude-cli 生成学生画像"""
    prompt = f"Generate a concise JSON profile for a student with cognitive ability theta={theta:.2f}. Fields: learning_style (visual/auditory/kinesthetic), personality (confident/anxious/diligent), motivation_level (0-1 float), anxiety_threshold (0-1 float). Return ONLY valid JSON."
    try:
        result = subprocess.run(["claude", "-p", prompt], capture_output=True, text=True, timeout=30)
        return json.loads(result.stdout)
    except:
        return None

def generate_agent_profiles():
    print("--- Edu-Sim Agent 画像生成程序 (LLM 增强版) ---")
    
    # 1. 加载图谱数据
    graph_path = "data/graphs/edu_complete_graph_v2"
    with open(os.path.join(graph_path, "nodes.json"), "r", encoding="utf-8") as f:
        nodes = json.load(f)

    students = [n for n in nodes if n['label'] == 'Student']
    print(f"[正在处理] {len(students)} 名学生 Agent...")

    # 2. 循环生成并更新
    for i, student in enumerate(students):
        theta = student['attributes'].get('cognitive_level', 0.0)
        
        # 尝试调用 LLM，如果失败则回退到规则生成
        llm_result = generate_profile_with_llm(theta)
        
        if llm_result:
            style = llm_result.get('learning_style', 'Visual')
            personality = llm_result.get('personality', 'Neutral')
            motivation = llm_result.get('motivation_level', 0.5)
            anxiety = llm_result.get('anxiety_threshold', 0.5)
        else:
            # 规则回退逻辑
            style = random.choice(["Visual", "Auditory", "Kinesthetic"])
            personality = "Confident" if theta > 0 else "Anxious"
            motivation = round(random.uniform(0.5, 0.9), 2)
            anxiety = round(random.uniform(0.2, 0.8), 2)

        # 更新节点属性
        student['attributes']['learning_style'] = style
        student['attributes']['personality'] = personality
        student['attributes']['motivation_level'] = motivation
        student['attributes']['anxiety_threshold'] = anxiety
        student['summary'] = f"A {personality} student with theta={theta:.2f}, prefers {style} learning."
        
        if (i + 1) % 100 == 0:
            print(f"  -> 已处理 {i+1}/{len(students)} 名学生...")

    # 3. 保存更新后的图谱
    print("[正在保存更新后的图谱...]")
    with open(os.path.join(graph_path, "nodes.json"), "w", encoding="utf-8") as f:
        json.dump(nodes, f, ensure_ascii=False, indent=2)

    print(f"\n--- Agent 画像生成完成！ ---")
    print(f"示例画像 (Student_{students[0]['id']}):")
    print(json.dumps(students[0]['attributes'], indent=2, ensure_ascii=False))

if __name__ == "__main__":
    generate_agent_profiles()
