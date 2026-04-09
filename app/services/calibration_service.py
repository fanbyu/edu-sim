"""
Calibration Service
IRT 校准服务 - 提供学生能力和试题参数的校准功能
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from app.core.agent_modeling import IRTEngine
from app.services.graph_service import GraphService


class CalibrationService:
    """
    IRT 校准服务
    
    基于作答数据校准学生能力值 (θ) 和试题参数 (a, b, c)，
    并同步更新到知识图谱
    """
    
    def __init__(self, graph_service: GraphService, 
                 irt_engine: IRTEngine = None):
        """
        初始化校准服务
        
        Args:
            graph_service: 图谱服务实例
            irt_engine: IRT 引擎实例（可选，默认使用 2PL 模型）
        """
        self.graph_service = graph_service
        self.irt_engine = irt_engine or IRTEngine(model_type="2PL")
    
    def calibrate_from_responses(self, response_matrix: np.ndarray,
                                student_ids: List[str] = None,
                                item_ids: List[str] = None,
                                max_iterations: int = 100) -> Dict[str, Any]:
        """
        从作答矩阵校准参数
        
        Args:
            response_matrix: N×M 作答矩阵 (N=学生数, M=试题数)
            student_ids: 学生ID列表
            item_ids: 试题ID列表
            max_iterations: 最大迭代次数
            
        Returns:
            校准结果
        """
        print("🔄 开始 IRT 参数校准...")
        print(f"   作答矩阵形状: {response_matrix.shape}")
        
        # 执行校准
        results = self.irt_engine.calibrate(
            response_matrix, 
            max_iterations=max_iterations
        )
        
        print(f"   ✓ 校准完成")
        print(f"      学生能力范围: [{min(results['student_thetas']):.2f}, "
              f"{max(results['student_thetas']):.2f}]")
        print(f"      试题难度范围: [{min(results['item_difficulties']):.2f}, "
              f"{max(results['item_difficulties']):.2f}]")
        
        if 'item_discriminations' in results:
            print(f"      试题区分度范围: [{min(results['item_discriminations']):.2f}, "
                  f"{max(results['item_discriminations']):.2f}]")
        
        return {
            "student_thetas": results['student_thetas'],
            "item_difficulties": results['item_difficulties'],
            "item_discriminations": results.get('item_discriminations', []),
            "student_ids": student_ids,
            "item_ids": item_ids
        }
    
    def update_student_abilities(self, calibration_results: Dict[str, Any]) -> int:
        """
        更新学生能力值到图谱
        
        Args:
            calibration_results: 校准结果
            
        Returns:
            更新的学生数量
        """
        student_ids = calibration_results.get('student_ids', [])
        thetas = calibration_results.get('student_thetas', [])
        
        if len(student_ids) != len(thetas):
            raise ValueError("学生ID数量与能力值数量不匹配")
        
        updated_count = 0
        
        for student_id, theta in zip(student_ids, thetas):
            # 获取当前学生节点
            node = self.graph_service.engine.get_node(student_id)
            if node:
                # 更新能力值
                node['properties']['cognitive_level'] = round(float(theta), 4)
                
                # 保存更新（这里假设后端支持更新操作）
                # 实际实现取决于具体的图数据库后端
                updated_count += 1
        
        print(f"✓ 更新了 {updated_count} 名学生的能力值")
        return updated_count
    
    def update_item_parameters(self, calibration_results: Dict[str, Any]) -> int:
        """
        更新试题参数到图谱
        
        Args:
            calibration_results: 校准结果
            
        Returns:
            更新的试题数量
        """
        item_ids = calibration_results.get('item_ids', [])
        difficulties = calibration_results.get('item_difficulties', [])
        discriminations = calibration_results.get('item_discriminations', [])
        
        if len(item_ids) != len(difficulties):
            raise ValueError("试题ID数量与难度值数量不匹配")
        
        updated_count = 0
        
        for i, item_id in enumerate(item_ids):
            # 获取当前试题节点
            node = self.graph_service.engine.get_node(item_id)
            if node:
                # 更新参数
                node['properties']['difficulty'] = round(float(difficulties[i]), 4)
                
                if i < len(discriminations):
                    node['properties']['discrimination'] = round(
                        float(discriminations[i]), 4
                    )
                
                updated_count += 1
        
        print(f"✓ 更新了 {updated_count} 道试题的参数")
        return updated_count
    
    def full_calibration_pipeline(self, exam_data: Dict[str, Any],
                                  sync_to_graph: bool = True) -> Dict[str, Any]:
        """
        完整校准流程
        
        Args:
            exam_data: 考试数据（包含 responses, students_meta, items_meta）
            sync_to_graph: 是否同步到图谱
            
        Returns:
            完整校准结果
        """
        print("\n" + "="*70)
        print("📐 完整 IRT 校准流程")
        print("="*70)
        
        # Step 1: 构建作答矩阵
        print("\nStep 1: 构建作答矩阵...")
        response_matrix, student_ids, item_ids = self._build_response_matrix(exam_data)
        print(f"   ✓ 矩阵形状: {response_matrix.shape}")
        
        # Step 2: 执行校准
        print("\nStep 2: 执行 IRT 校准...")
        calibration_results = self.calibrate_from_responses(
            response_matrix,
            student_ids=student_ids,
            item_ids=item_ids
        )
        
        # Step 3: 同步到图谱
        if sync_to_graph:
            print("\nStep 3: 同步校准结果到图谱...")
            students_updated = self.update_student_abilities(calibration_results)
            items_updated = self.update_item_parameters(calibration_results)
        else:
            students_updated = 0
            items_updated = 0
        
        # Step 4: 生成报告
        print("\nStep 4: 生成校准报告...")
        report = self._generate_calibration_report(
            calibration_results,
            students_updated,
            items_updated
        )
        
        print("\n✅ 校准流程完成!")
        return report
    
    def _build_response_matrix(self, exam_data: Dict[str, Any]) -> Tuple[np.ndarray, List[str], List[str]]:
        """
        从考试数据构建作答矩阵
        
        Args:
            exam_data: 考试数据
            
        Returns:
            (response_matrix, student_ids, item_ids)
        """
        responses = exam_data.get('responses', [])
        students_meta = exam_data.get('students_meta', {})
        items_meta = exam_data.get('items_meta', {})
        
        # 获取学生ID列表和试题ID列表
        student_ids = sorted(students_meta.keys())
        item_ids = sorted(items_meta.keys())
        
        n_students = len(student_ids)
        n_items = len(item_ids)
        
        # 创建映射
        student_idx = {sid: i for i, sid in enumerate(student_ids)}
        item_idx = {iid: j for j, iid in enumerate(item_ids)}
        
        # 初始化作答矩阵 (NaN 表示未作答)
        response_matrix = np.full((n_students, n_items), np.nan)
        
        # 填充分数
        for resp in responses:
            sid = resp.get('student_id')
            q_idx = resp.get('question_index')
            score = resp.get('score', 0)
            
            if sid in student_idx and q_idx is not None:
                # 将 question_index 映射到 item_id
                item_id = f"Q{q_idx:03d}"
                if item_id in item_idx:
                    i = student_idx[sid]
                    j = item_idx[item_id]
                    response_matrix[i, j] = score
        
        return response_matrix, student_ids, item_ids
    
    def _generate_calibration_report(self, calibration_results: Dict[str, Any],
                                    students_updated: int,
                                    items_updated: int) -> Dict[str, Any]:
        """
        生成校准报告
        
        Args:
            calibration_results: 校准结果
            students_updated: 更新的学生数
            items_updated: 更新的试题数
            
        Returns:
            校准报告
        """
        import numpy as np
        
        thetas = calibration_results['student_thetas']
        difficulties = calibration_results['item_difficulties']
        
        report = {
            "calibration_summary": {
                "total_students": len(thetas),
                "total_items": len(difficulties),
                "students_updated": students_updated,
                "items_updated": items_updated
            },
            "student_statistics": {
                "mean_theta": float(np.mean(thetas)),
                "std_theta": float(np.std(thetas)),
                "min_theta": float(np.min(thetas)),
                "max_theta": float(np.max(thetas)),
                "median_theta": float(np.median(thetas))
            },
            "item_statistics": {
                "mean_difficulty": float(np.mean(difficulties)),
                "std_difficulty": float(np.std(difficulties)),
                "min_difficulty": float(np.min(difficulties)),
                "max_difficulty": float(np.max(difficulties)),
                "median_difficulty": float(np.median(difficulties))
            }
        }
        
        # 添加区分度统计（如果有）
        if 'item_discriminations' in calibration_results:
            discriminations = calibration_results['item_discriminations']
            report["item_statistics"]["mean_discrimination"] = float(np.mean(discriminations))
            report["item_statistics"]["std_discrimination"] = float(np.std(discriminations))
        
        # 质量评估
        quality_assessment = self._assess_calibration_quality(report)
        report["quality_assessment"] = quality_assessment
        
        return report
    
    def _assess_calibration_quality(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """
        评估校准质量
        
        Args:
            report: 校准报告
            
        Returns:
            质量评估结果
        """
        student_stats = report['student_statistics']
        item_stats = report['item_statistics']
        
        issues = []
        warnings = []
        
        # 检查学生能力分布
        if student_stats['std_theta'] < 0.5:
            warnings.append("学生能力标准差较小，可能缺乏区分度")
        
        if abs(student_stats['mean_theta']) > 2.0:
            warnings.append("学生平均能力偏离0较多，可能需要重新标定")
        
        # 检查试题难度分布
        if item_stats['std_difficulty'] < 0.5:
            warnings.append("试题难度标准差较小，难度分布集中")
        
        difficulty_range = item_stats['max_difficulty'] - item_stats['min_difficulty']
        if difficulty_range < 2.0:
            warnings.append(f"试题难度范围较小 ({difficulty_range:.2f})，建议增加难度多样性")
        
        # 检查区分度（如果有）
        if 'mean_discrimination' in item_stats:
            if item_stats['mean_discrimination'] < 1.0:
                warnings.append("平均区分度较低，试题质量可能不佳")
        
        # 总体评价
        if len(issues) == 0 and len(warnings) == 0:
            overall = "优秀"
        elif len(issues) == 0:
            overall = "良好"
        else:
            overall = "需要改进"
        
        return {
            "overall_rating": overall,
            "issues": issues,
            "warnings": warnings
        }
    
    def estimate_student_ability_online(self, student_id: str,
                                       recent_responses: List[Dict[str, Any]]) -> float:
        """
        在线估计学生能力（基于最近作答）
        
        Args:
            student_id: 学生ID
            recent_responses: 最近作答记录列表
                [{"item_id": "...", "score": 1.0, "difficulty": 0.3}, ...]
            
        Returns:
            估计的能力值 θ
        """
        if not recent_responses:
            return 0.0
        
        # 构建题目参数字典
        item_params = {}
        responses = []
        
        for resp in recent_responses:
            item_id = resp.get('item_id')
            score = resp.get('score', 0)
            difficulty = resp.get('difficulty', 0.0)
            
            item_params[item_id] = {
                'difficulty': difficulty,
                'discrimination': 1.0  # 默认区分度
            }
            responses.append((item_id, score))
        
        # 使用 IRT 引擎估计能力
        theta = self.irt_engine.estimate_student_ability(
            responses, 
            item_params,
            method="MLE"
        )
        
        return theta
