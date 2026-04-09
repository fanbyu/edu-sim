"""
Education Ontology Definition
教育领域本体定义 - 原生支持教育场景
"""

from typing import Dict, List, Any


class EducationOntology:
    """
    教育领域本体
    
    定义了教育仿真中的核心实体类型、关系类型和属性 schema
    """
    
    # ==================== 节点类型定义 ====================
    
    NODE_TYPES: Dict[str, Dict[str, Any]] = {
        "Student": {
            "description": "学生个体",
            "required_properties": ["student_id", "cognitive_level"],
            "optional_properties": [
                "learning_style",      # visual/auditory/kinesthetic
                "anxiety_threshold",   # 0-1 float
                "motivation_level",    # 0-1 float
                "personality",         # confident/anxious/diligent
                "class_name"
            ],
            "default_properties": {
                "cognitive_level": 0.0,
                "anxiety_threshold": 0.5,
                "motivation_level": 0.5,
                "learning_style": "visual"
            }
        },
        
        "Teacher": {
            "description": "教师个体",
            "required_properties": ["teacher_id"],
            "optional_properties": [
                "teaching_style",      # heuristic/direct/facilitator
                "experience_years",
                "feedback_quality",    # 0-1 float
                "patience_level",      # 0-1 float
                "strictness"           # 0-1 float
            ],
            "default_properties": {
                "teaching_style": "heuristic",
                "feedback_quality": 0.8,
                "patience_level": 0.7
            }
        },
        
        "Item": {
            "description": "试题/题目",
            "required_properties": ["item_id"],
            "optional_properties": [
                "difficulty",          # IRT b parameter
                "discrimination",      # IRT a parameter
                "guessing_param",      # IRT c parameter
                "question_type",       # multiple_choice/essay/etc
                "max_score"
            ],
            "default_properties": {
                "difficulty": 0.0,
                "discrimination": 1.0,
                "guessing_param": 0.0,
                "max_score": 1.0
            }
        },
        
        "Concept": {
            "description": "知识点/概念",
            "required_properties": ["concept_id", "name"],
            "optional_properties": [
                "prerequisite_concepts",  # List[str]
                "mastery_threshold",      # 0-1 float
                "subject",                # math/english/physics
                "grade_level"
            ],
            "default_properties": {
                "mastery_threshold": 0.7
            }
        },
        
        "Class": {
            "description": "行政班级",
            "required_properties": ["class_id", "class_name"],
            "optional_properties": [
                "size",
                "avg_performance",
                "teacher_id"
            ],
            "default_properties": {}
        }
    }
    
    # ==================== 关系类型定义 ====================
    
    RELATION_TYPES: Dict[str, Dict[str, Any]] = {
        "ATTEMPTED": {
            "description": "学生作答了某题",
            "source_type": "Student",
            "target_type": "Item",
            "properties": [
                "score",              # 得分
                "time_spent",         # 用时(秒)
                "attempt_timestamp"   # 作答时间
            ],
            "cardinality": "many-to-many"
        },
        
        "BELONGS_TO": {
            "description": "学生属于某个班级",
            "source_type": "Student",
            "target_type": "Class",
            "properties": ["enrollment_date"],
            "cardinality": "many-to-one"
        },
        
        "TEACHES": {
            "description": "教师教授某个班级",
            "source_type": "Teacher",
            "target_type": "Class",
            "properties": ["role", "start_date"],  # role: head_teacher/subject_teacher
            "cardinality": "one-to-many"
        },
        
        "ASSESSES": {
            "description": "试题考察某个知识点",
            "source_type": "Item",
            "target_type": "Concept",
            "properties": ["weight"],  # 考察权重 0-1
            "cardinality": "many-to-many"
        },
        
        "PREREQUISITE_OF": {
            "description": "知识点前置关系",
            "source_type": "Concept",
            "target_type": "Concept",
            "properties": ["strength"],  # 前置强度 0-1
            "cardinality": "many-to-many"
        },
        
        "MASTERED": {
            "description": "学生掌握了某个知识点",
            "source_type": "Student",
            "target_type": "Concept",
            "properties": ["mastery_level", "assessed_at"],  # mastery_level: 0-1
            "cardinality": "many-to-many"
        }
    }
    
    # ==================== 验证方法 ====================
    
    @classmethod
    def validate_node(cls, label: str, properties: Dict[str, Any]) -> List[str]:
        """
        验证节点属性是否符合本体定义
        
        Returns:
            错误信息列表,空列表表示验证通过
        """
        errors = []
        
        if label not in cls.NODE_TYPES:
            return [f"Unknown node type: {label}"]
        
        node_def = cls.NODE_TYPES[label]
        
        # 检查必需属性
        for req_prop in node_def['required_properties']:
            if req_prop not in properties:
                errors.append(f"Missing required property: {req_prop}")
        
        return errors
    
    @classmethod
    def validate_edge(cls, relation: str, source_label: str, 
                      target_label: str) -> List[str]:
        """
        验证边是否符合本体定义
        
        Returns:
            错误信息列表
        """
        errors = []
        
        if relation not in cls.RELATION_TYPES:
            return [f"Unknown relation type: {relation}"]
        
        edge_def = cls.RELATION_TYPES[relation]
        
        # 检查源节点类型
        if edge_def['source_type'] != source_label:
            errors.append(
                f"Invalid source type for {relation}: "
                f"expected {edge_def['source_type']}, got {source_label}"
            )
        
        # 检查目标节点类型
        if edge_def['target_type'] != target_label:
            errors.append(
                f"Invalid target type for {relation}: "
                f"expected {edge_def['target_type']}, got {target_label}"
            )
        
        return errors
    
    @classmethod
    def get_default_properties(cls, label: str) -> Dict[str, Any]:
        """获取节点类型的默认属性"""
        if label in cls.NODE_TYPES:
            return cls.NODE_TYPES[label]['default_properties'].copy()
        return {}
    
    @classmethod
    def get_all_node_types(cls) -> List[str]:
        """获取所有节点类型"""
        return list(cls.NODE_TYPES.keys())
    
    @classmethod
    def get_all_relation_types(cls) -> List[str]:
        """获取所有关系类型"""
        return list(cls.RELATION_TYPES.keys())
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """导出本体定义为字典"""
        return {
            "node_types": cls.NODE_TYPES,
            "relation_types": cls.RELATION_TYPES
        }
