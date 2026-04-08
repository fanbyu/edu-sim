import csv
import os
import json
from typing import List, Dict, Any

class StructuredDataLoader:
    """
    教育场景结构化数据加载器
    负责解析试题库、作答日志和知识点映射，为图谱构建提供标准化输入
    """

    def __init__(self, data_root: str):
        self.data_root = data_root

    def load_exam_data(self, exam_folder_name: str) -> Dict[str, Any]:
        """
        加载单次考试/练习的完整数据
        :param exam_folder_name: 例如 "试题1"
        :return: 包含 questions, students, responses 的字典
        """
        folder_path = os.path.join(self.data_root, exam_folder_name)
        
        # 1. 加载知识点映射
        kp_file = self._find_file(folder_path, "知识点.csv")
        knowledge_points = self._parse_knowledge_points(kp_file) if kp_file else {}

        # 2. 加载作答明细
        score_folder = self._find_folder(folder_path, "得分明细")
        responses, students_meta = self._parse_score_details(score_folder) if score_folder else ([], {})

        # 3. 整合数据
        return {
            "exam_id": exam_folder_name,
            "knowledge_points": knowledge_points,
            "responses": responses,
            "students_meta": students_meta
        }

    def _parse_knowledge_points(self, file_path: str) -> Dict[str, str]:
        """解析题型-题号-知识点映射表"""
        kp_map = {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    q_id = f"{row.get('题型', '')}_{row.get('题号', '')}"
                    kp_map[q_id] = row.get('核心考察知识点', '')
        except Exception as e:
            print(f"解析知识点文件失败: {e}")
        return kp_map

    def _parse_score_details(self, folder_path: str) -> tuple:
        """解析学生作答得分明细"""
        responses = []
        students_meta = {}
        
        csv_file = self._find_file(folder_path, ".csv")
        if not csv_file:
            return responses, students_meta

        try:
            # 尝试多种编码读取 CSV
            content = None
            for encoding in ['utf-8-sig', 'gbk', 'utf-8']:
                try:
                    with open(csv_file, 'r', encoding=encoding) as f:
                        content = f.readlines()
                    break
                except UnicodeDecodeError:
                    continue
            
            if not content: return responses, students_meta

            # 跳过前两行说明性文字，从第三行开始读取数据
            lines = content[2:] 
            
            for line in lines:
                parts = line.strip().split(',')
                # 增加容错：如果列数不足，尝试跳过或处理
                if len(parts) < 12: continue
                
                student_id = parts[0]
                class_name = parts[2] if len(parts) > 2 else "Unknown"
                try:
                    total_score = float(parts[7]) if len(parts) > 7 and parts[7] not in ['-', ''] else 0
                except:
                    total_score = 0
                
                students_meta[student_id] = {
                    "id": student_id,
                    "class": class_name,
                    "total_score": total_score
                }

                # 解析各题得分 (假设从第 12 列开始是各题得分)
                for i, score_str in enumerate(parts[11:]):
                    try:
                        if not score_str or score_str == '-': continue
                        score = float(score_str)
                        q_index = i + 1 # 简单映射题号
                        responses.append({
                            "student_id": student_id,
                            "question_index": q_index,
                            "score": score
                        })
                    except:
                        continue
        except Exception as e:
            print(f"解析得分明细失败: {e}")
            
        return responses, students_meta

    def _find_file(self, folder: str, keyword: str) -> str:
        if not os.path.exists(folder): return None
        for f in os.listdir(folder):
            if keyword in f:
                return os.path.join(folder, f)
        return None

    def _find_folder(self, parent: str, keyword: str) -> str:
        if not os.path.exists(parent): return None
        for f in os.listdir(parent):
            if os.path.isdir(os.path.join(parent, f)) and keyword in f:
                return os.path.join(parent, f)
        return None

if __name__ == "__main__":
    loader = StructuredDataLoader("docs/英语数据")
    data = loader.load_exam_data("试题1")
    print(f"加载完成: {len(data['responses'])} 条作答记录")
    print(f"涉及学生: {len(data['students_meta'])} 人")
    if data['knowledge_points']:
        print(f"第一个知识点: {list(data['knowledge_points'].items())[0]}")
