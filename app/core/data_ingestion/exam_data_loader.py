"""
Exam Data Loader
考试数据加载器 - 支持 CSV/Excel 格式的教育数据解析
"""

import csv
import os
import json
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path


class ExamDataLoader:
    """
    教育场景结构化数据加载器
    
    负责解析试题库、作答日志和知识点映射，为图谱构建提供标准化输入
    支持多种编码格式和容错处理
    """
    
    def __init__(self, data_root: str):
        """
        初始化数据加载器
        
        Args:
            data_root: 数据根目录路径
        """
        self.data_root = Path(data_root)
        if not self.data_root.exists():
            raise FileNotFoundError(f"数据目录不存在: {data_root}")
    
    def load_exam_data(self, exam_folder_name: str) -> Dict[str, Any]:
        """
        加载单次考试/练习的完整数据
        
        Args:
            exam_folder_name: 考试文件夹名称，例如 "试题1"
            
        Returns:
            包含以下键的字典:
            - exam_id: 考试ID
            - knowledge_points: 知识点映射 {question_id: concept_name}
            - responses: 作答记录列表
            - students_meta: 学生元数据 {student_id: {...}}
            - items_meta: 试题元数据 {item_id: {...}}
        """
        folder_path = self.data_root / exam_folder_name
        
        if not folder_path.exists():
            raise FileNotFoundError(f"考试文件夹不存在: {folder_path}")
        
        # 1. 加载知识点映射
        kp_file = self._find_file(folder_path, "知识点.csv")
        knowledge_points = self._parse_knowledge_points(kp_file) if kp_file else {}
        
        # 2. 加载作答明细
        score_folder = self._find_folder(folder_path, "得分明细")
        responses, students_meta = self._parse_score_details(score_folder) if score_folder else ([], {})
        
        # 3. 生成试题元数据
        items_meta = self._generate_items_metadata(responses, knowledge_points)
        
        # 4. 整合数据
        return {
            "exam_id": exam_folder_name,
            "knowledge_points": knowledge_points,
            "responses": responses,
            "students_meta": students_meta,
            "items_meta": items_meta
        }
    
    def load_multiple_exams(self, exam_folders: List[str]) -> Dict[str, Any]:
        """
        批量加载多次考试数据
        
        Args:
            exam_folders: 考试文件夹名称列表
            
        Returns:
            合并后的数据集
        """
        all_responses = []
        all_students = {}
        all_items = {}
        all_kps = {}
        
        for exam_folder in exam_folders:
            try:
                data = self.load_exam_data(exam_folder)
                all_responses.extend(data['responses'])
                all_students.update(data['students_meta'])
                all_items.update(data['items_meta'])
                all_kps.update(data['knowledge_points'])
            except Exception as e:
                print(f"⚠️  加载 {exam_folder} 失败: {e}")
                continue
        
        return {
            "exam_count": len(exam_folders),
            "knowledge_points": all_kps,
            "responses": all_responses,
            "students_meta": all_students,
            "items_meta": all_items
        }
    
    def _parse_knowledge_points(self, file_path: Path) -> Dict[str, str]:
        """
        解析题型-题号-知识点映射表
        
        Args:
            file_path: 知识点 CSV 文件路径
            
        Returns:
            知识点映射 {question_id: concept_name}
        """
        kp_map = {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    q_type = row.get('题型', '').strip()
                    q_num = row.get('题号', '').strip()
                    concept = row.get('核心考察知识点', '').strip()
                    
                    if q_type and q_num:
                        q_id = f"{q_type}_{q_num}"
                        kp_map[q_id] = concept
        except Exception as e:
            print(f"❌ 解析知识点文件失败 [{file_path}]: {e}")
        
        return kp_map
    
    def _parse_score_details(self, folder_path: Path) -> Tuple[List[Dict], Dict]:
        """
        解析学生作答得分明细
        
        Args:
            folder_path: 得分明细文件夹路径
            
        Returns:
            (responses, students_meta) 元组
        """
        responses = []
        students_meta = {}
        
        csv_file = self._find_file(folder_path, ".csv")
        if not csv_file:
            return responses, students_meta
        
        try:
            # 尝试多种编码读取 CSV
            content = None
            used_encoding = None
            for encoding in ['utf-8-sig', 'gbk', 'utf-8']:
                try:
                    with open(csv_file, 'r', encoding=encoding) as f:
                        content = f.readlines()
                    used_encoding = encoding
                    break
                except UnicodeDecodeError:
                    continue
            
            if not content:
                print(f"⚠️  无法读取文件 (编码问题): {csv_file}")
                return responses, students_meta
            
            print(f"✓ 使用编码 '{used_encoding}' 读取: {csv_file.name}")
            
            # 跳过前两行说明性文字，从第三行开始读取数据
            lines = content[2:]
            
            for line_num, line in enumerate(lines, start=3):
                parts = line.strip().split(',')
                
                # 增加容错：如果列数不足，跳过
                if len(parts) < 12:
                    continue
                
                student_id = parts[0].strip()
                class_name = parts[2].strip() if len(parts) > 2 else "Unknown"
                
                # 解析总分
                try:
                    total_score = float(parts[7]) if len(parts) > 7 and parts[7] not in ['-', ''] else 0
                except (ValueError, IndexError):
                    total_score = 0
                
                # 存储学生元数据
                students_meta[student_id] = {
                    "id": student_id,
                    "class": class_name,
                    "total_score": total_score
                }
                
                # 解析各题得分 (假设从第 12 列开始是各题得分)
                for i, score_str in enumerate(parts[11:]):
                    try:
                        if not score_str or score_str.strip() == '-':
                            continue
                        
                        score = float(score_str.strip())
                        q_index = i + 1  # 简单映射题号
                        
                        responses.append({
                            "student_id": student_id,
                            "question_index": q_index,
                            "score": score,
                            "max_score": 1.0  # 默认满分，后续可根据实际调整
                        })
                    except (ValueError, IndexError):
                        continue
        
        except Exception as e:
            print(f"❌ 解析得分明细失败 [{folder_path}]: {e}")
            import traceback
            traceback.print_exc()
        
        return responses, students_meta
    
    def _generate_items_metadata(self, responses: List[Dict], 
                                 knowledge_points: Dict[str, str]) -> Dict[str, Dict]:
        """
        根据作答记录生成试题元数据
        
        Args:
            responses: 作答记录列表
            knowledge_points: 知识点映射
            
        Returns:
            试题元数据 {item_id: {...}}
        """
        items_meta = {}
        
        # 统计每道题的作答情况
        item_stats = {}
        for resp in responses:
            q_idx = resp['question_index']
            item_id = f"Q{q_idx:03d}"
            
            if item_id not in item_stats:
                item_stats[item_id] = {
                    "scores": [],
                    "attempts": 0
                }
            
            item_stats[item_id]["scores"].append(resp['score'])
            item_stats[item_id]["attempts"] += 1
        
        # 计算统计数据
        for item_id, stats in item_stats.items():
            scores = stats["scores"]
            avg_score = sum(scores) / len(scores) if scores else 0
            max_score = max(scores) if scores else 1.0
            
            # 估算难度 (1 - 平均正确率)
            difficulty = 1.0 - (avg_score / max_score) if max_score > 0 else 0.5
            
            # 关联知识点
            q_id = f"未知_{item_id[1:]}"  # 简化处理
            concept = knowledge_points.get(q_id, "")
            
            items_meta[item_id] = {
                "item_id": item_id,
                "difficulty": round(difficulty, 3),
                "avg_score": round(avg_score, 2),
                "max_score": max_score,
                "attempt_count": stats["attempts"],
                "assessed_concepts": [concept] if concept else []
            }
        
        return items_meta
    
    @staticmethod
    def _find_file(folder: Path, keyword: str) -> Optional[Path]:
        """在文件夹中查找包含关键词的文件"""
        if not folder.exists():
            return None
        
        for f in folder.iterdir():
            if f.is_file() and keyword in f.name:
                return f
        
        return None
    
    @staticmethod
    def _find_folder(parent: Path, keyword: str) -> Optional[Path]:
        """在父目录中查找包含关键词的子文件夹"""
        if not parent.exists():
            return None
        
        for f in parent.iterdir():
            if f.is_dir() and keyword in f.name:
                return f
        
        return None
    
    def get_data_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成数据摘要统计
        
        Args:
            data: load_exam_data 返回的数据
            
        Returns:
            摘要统计信息
        """
        responses = data.get('responses', [])
        students = data.get('students_meta', {})
        items = data.get('items_meta', {})
        
        # 计算基本统计
        total_responses = len(responses)
        unique_students = len(students)
        unique_items = len(items)
        
        # 计算平均分
        if responses:
            avg_score = sum(r['score'] for r in responses) / total_responses
        else:
            avg_score = 0
        
        return {
            "exam_id": data.get('exam_id'),
            "total_responses": total_responses,
            "unique_students": unique_students,
            "unique_items": unique_items,
            "average_score": round(avg_score, 2),
            "knowledge_points_count": len(data.get('knowledge_points', {}))
        }
