"""
Data Validator
数据验证器 - 确保教育数据的质量和一致性
"""

from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def add_error(self, message: str):
        self.errors.append(message)
        self.is_valid = False
    
    def add_warning(self, message: str):
        self.warnings.append(message)
    
    def summary(self) -> str:
        """生成验证摘要"""
        lines = []
        status = "✅ 通过" if self.is_valid else "❌ 失败"
        lines.append(f"验证状态: {status}")
        
        if self.errors:
            lines.append(f"\n错误 ({len(self.errors)}):")
            for err in self.errors:
                lines.append(f"  - {err}")
        
        if self.warnings:
            lines.append(f"\n警告 ({len(self.warnings)}):")
            for warn in self.warnings:
                lines.append(f"  - {warn}")
        
        return "\n".join(lines)


class EducationDataValidator:
    """
    教育数据验证器
    
    验证学生、试题、作答记录等数据的完整性和一致性
    """
    
    @staticmethod
    def validate_student(student_data: Dict[str, Any]) -> ValidationResult:
        """
        验证学生数据
        
        Args:
            student_data: 学生数据字典
            
        Returns:
            验证结果
        """
        result = ValidationResult(is_valid=True)
        
        # 必需字段检查
        required_fields = ['id']
        for field_name in required_fields:
            if field_name not in student_data or not student_data[field_name]:
                result.add_error(f"缺少必需字段: {field_name}")
        
        # 可选字段类型检查
        if 'total_score' in student_data:
            try:
                score = float(student_data['total_score'])
                if score < 0:
                    result.add_warning(f"学生 {student_data.get('id')} 的总分为负数: {score}")
            except (ValueError, TypeError):
                result.add_error(f"学生 {student_data.get('id')} 的总分格式错误")
        
        if 'class' in student_data and not isinstance(student_data['class'], str):
            result.add_warning(f"学生 {student_data.get('id')} 的班级应为字符串")
        
        return result
    
    @staticmethod
    def validate_item(item_data: Dict[str, Any]) -> ValidationResult:
        """
        验证试题数据
        
        Args:
            item_data: 试题数据字典
            
        Returns:
            验证结果
        """
        result = ValidationResult(is_valid=True)
        
        # 必需字段检查
        required_fields = ['item_id']
        for field_name in required_fields:
            if field_name not in item_data or not item_data[field_name]:
                result.add_error(f"缺少必需字段: {field_name}")
        
        # 难度值范围检查
        if 'difficulty' in item_data:
            try:
                diff = float(item_data['difficulty'])
                if diff < -4 or diff > 4:
                    result.add_warning(
                        f"试题 {item_data.get('item_id')} 的难度值超出合理范围 [-4, 4]: {diff}"
                    )
            except (ValueError, TypeError):
                result.add_error(f"试题 {item_data.get('item_id')} 的难度值格式错误")
        
        # 区分度检查
        if 'discrimination' in item_data:
            try:
                disc = float(item_data['discrimination'])
                if disc < 0.5 or disc > 3.0:
                    result.add_warning(
                        f"试题 {item_data.get('item_id')} 的区分度超出合理范围 [0.5, 3.0]: {disc}"
                    )
            except (ValueError, TypeError):
                result.add_error(f"试题 {item_data.get('item_id')} 的区分度格式错误")
        
        return result
    
    @staticmethod
    def validate_response(response_data: Dict[str, Any]) -> ValidationResult:
        """
        验证作答记录
        
        Args:
            response_data: 作答记录字典
            
        Returns:
            验证结果
        """
        result = ValidationResult(is_valid=True)
        
        # 必需字段检查
        required_fields = ['student_id', 'question_index', 'score']
        for field_name in required_fields:
            if field_name not in response_data:
                result.add_error(f"作答记录缺少必需字段: {field_name}")
        
        # 分数合理性检查
        if 'score' in response_data:
            try:
                score = float(response_data['score'])
                if score < 0:
                    result.add_error(f"作答记录分数为负数: {score}")
                
                max_score = response_data.get('max_score', 1.0)
                if score > max_score:
                    result.add_warning(
                        f"作答记录分数 ({score}) 超过满分 ({max_score})"
                    )
            except (ValueError, TypeError):
                result.add_error(f"作答记录分数格式错误: {response_data.get('score')}")
        
        return result
    
    @staticmethod
    def validate_exam_dataset(data: Dict[str, Any]) -> ValidationResult:
        """
        验证完整的考试数据集
        
        Args:
            data: ExamDataLoader.load_exam_data() 返回的数据
            
        Returns:
            验证结果
        """
        result = ValidationResult(is_valid=True)
        
        # 检查基本结构
        required_keys = ['exam_id', 'responses', 'students_meta', 'items_meta']
        for key in required_keys:
            if key not in data:
                result.add_error(f"数据集缺少必需键: {key}")
        
        if not result.is_valid:
            return result
        
        responses = data.get('responses', [])
        students = data.get('students_meta', {})
        items = data.get('items_meta', {})
        
        # 验证数据量合理性
        if len(responses) == 0:
            result.add_warning("作答记录为空")
        
        if len(students) == 0:
            result.add_warning("学生元数据为空")
        
        if len(items) == 0:
            result.add_warning("试题元数据为空")
        
        # 抽样验证作答记录
        sample_size = min(10, len(responses))
        for i, resp in enumerate(responses[:sample_size]):
            resp_result = EducationDataValidator.validate_response(resp)
            if not resp_result.is_valid:
                result.add_error(f"作答记录 #{i+1}: {'; '.join(resp_result.errors)}")
        
        # 验证学生数据
        for student_id, student_data in list(students.items())[:5]:
            student_result = EducationDataValidator.validate_student(student_data)
            if not student_result.is_valid:
                result.add_error(f"学生 {student_id}: {'; '.join(student_result.errors)}")
        
        # 验证实体一致性
        response_student_ids = set(r['student_id'] for r in responses)
        meta_student_ids = set(students.keys())
        
        orphan_responses = response_student_ids - meta_student_ids
        if orphan_responses:
            result.add_warning(
                f"发现 {len(orphan_responses)} 条作答记录对应的学生不在元数据中"
            )
        
        return result
    
    @staticmethod
    def check_data_quality(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        检查数据质量指标
        
        Args:
            data: 考试数据集
            
        Returns:
            质量指标字典
        """
        responses = data.get('responses', [])
        students = data.get('students_meta', {})
        items = data.get('items_meta', {})
        
        if not responses:
            return {"quality_score": 0, "issues": ["无作答数据"]}
        
        # 计算质量指标
        total_responses = len(responses)
        
        # 1. 作答覆盖率 (实际作答数 / 理论最大作答数)
        theoretical_max = len(students) * len(items)
        coverage = total_responses / theoretical_max if theoretical_max > 0 else 0
        
        # 2. 平均分分布
        scores = [r['score'] for r in responses]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # 3. 零分率
        zero_count = sum(1 for s in scores if s == 0)
        zero_rate = zero_count / len(scores) if scores else 0
        
        # 4. 满分率
        max_scores = [r.get('max_score', 1.0) for r in responses]
        full_mark_count = sum(1 for s, m in zip(scores, max_scores) if s >= m)
        full_mark_rate = full_mark_count / len(scores) if scores else 0
        
        # 综合质量评分 (0-100)
        quality_score = (
            min(coverage, 1.0) * 40 +  # 覆盖率权重 40%
            max(0, (1 - abs(avg_score - 0.5))) * 30 +  # 平均分接近 0.5 得高分，权重 30%
            max(0, (1 - zero_rate)) * 15 +  # 零分率越低越好，权重 15%
            max(0, (1 - full_mark_rate)) * 15  # 满分率越低越好（避免过于简单），权重 15%
        )
        
        issues = []
        if coverage < 0.8:
            issues.append(f"作答覆盖率较低: {coverage:.1%}")
        if zero_rate > 0.3:
            issues.append(f"零分率较高: {zero_rate:.1%}")
        if full_mark_rate > 0.3:
            issues.append(f"满分率较高，试题可能过简: {full_mark_rate:.1%}")
        
        return {
            "quality_score": round(quality_score, 1),
            "coverage": round(coverage, 3),
            "average_score": round(avg_score, 3),
            "zero_rate": round(zero_rate, 3),
            "full_mark_rate": round(full_mark_rate, 3),
            "issues": issues
        }
