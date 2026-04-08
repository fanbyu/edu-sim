import streamlit as st
import json
import os
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Edu-Sim Dashboard", layout="wide")
st.title("🎓 Edu-Sim 教育生态效能预测系统")

# 1. 加载数据
graph_path = "data/graphs/edu_complete_graph_v2"
nodes_file = os.path.join(graph_path, "nodes.json")

if os.path.exists(nodes_file):
    with open(nodes_file, "r", encoding="utf-8") as f:
        nodes = json.load(f)
    
    students = [n for n in nodes if n['label'] == 'Student']
    teachers = [n for n in nodes if n['label'] == 'Teacher']
    
    # 2. 侧边栏统计
    st.sidebar.header("系统概览")
    st.sidebar.metric("学生总数", len(students))
    st.sidebar.metric("教师总数", len(teachers))
    avg_theta = sum(s['attributes'].get('cognitive_level', 0) for s in students) / len(students)
    st.sidebar.metric("平均认知能力 (θ)", f"{avg_theta:.3f}")

    # 3. 主页面布局
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 学生能力分布 (IRT θ)")
        thetas = [s['attributes'].get('cognitive_level', 0) for s in students]
        fig, ax = plt.subplots()
        ax.hist(thetas, bins=30, color='skyblue', edgecolor='black')
        ax.set_xlabel("Cognitive Level (θ)")
        ax.set_ylabel("Number of Students")
        st.pyplot(fig)

    with col2:
        st.subheader("🧠 学习风格占比")
        styles = [s['attributes'].get('learning_style', 'Unknown') for s in students]
        style_counts = pd.Series(styles).value_counts()
        st.bar_chart(style_counts)

    # 4. 详细数据表
    st.subheader("📋 学生 Agent 详情 (前 50 名)")
    df_data = []
    for s in students[:50]:
        df_data.append({
            "ID": s['id'],
            "班级": s['attributes'].get('class_name', ''),
            "能力值 (θ)": s['attributes'].get('cognitive_level', 0),
            "焦虑阈值": s['attributes'].get('anxiety_threshold', 0),
            "动机水平": s['attributes'].get('motivation_level', 0),
            "性格": s['attributes'].get('personality', '')
        })
    st.dataframe(pd.DataFrame(df_data))

else:
    st.error("未找到图谱数据文件，请先运行 build_edu_graph_v2.py")
