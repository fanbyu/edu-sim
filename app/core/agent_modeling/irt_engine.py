"""
IRT (Item Response Theory) Engine
项目反应理论计算引擎 - 原生集成
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from scipy.optimize import minimize


class IRTEngine:
    """
    IRT 参数校准引擎
    
    支持 1PL/2PL/3PL 模型
    """
    
    def __init__(self, model_type: str = "2PL"):
        """
        初始化 IRT 引擎
        
        Args:
            model_type: 模型类型 ('1PL', '2PL', '3PL')
        """
        self.model_type = model_type
    
    def calibrate(self, response_matrix: np.ndarray, 
                  max_iterations: int = 100) -> Dict[str, List[float]]:
        """
        校准学生和题目参数
        
        Args:
            response_matrix: N×M 矩阵 (N=学生数, M=题目数)
                           值为 0/1 (错误/正确) 或 NaN (未作答)
            max_iterations: 最大迭代次数
            
        Returns:
            {
                'student_thetas': [...],      # 学生能力值 θ
                'item_difficulties': [...],   # 题目难度 b
                'item_discriminations': [...] # 题目区分度 a (仅2PL/3PL)
            }
        """
        n_students, n_items = response_matrix.shape
        
        # 初始参数
        initial_thetas = np.zeros(n_students)
        initial_bs = np.zeros(n_items)
        initial_as = np.ones(n_items) if self.model_type in ['2PL', '3PL'] else None
        initial_cs = np.full(n_items, 0.25) if self.model_type == '3PL' else None
        
        # 联合极大似然估计 (JMLE)
        def neg_log_likelihood(params):
            thetas = params[:n_students]
            bs = params[n_students:n_students+n_items]
            
            log_lik = 0.0
            for i in range(n_students):
                for j in range(n_items):
                    if not np.isnan(response_matrix[i, j]):
                        # 计算答对概率
                        if self.model_type == '1PL':
                            p = self._irt_1pl(thetas[i], bs[j])
                        elif self.model_type == '2PL':
                            a = params[n_students+n_items+j] if initial_as is not None else 1.0
                            p = self._irt_2pl(thetas[i], bs[j], a)
                        else:  # 3PL
                            a = params[n_students+n_items+j]
                            c = params[n_students+2*n_items+j]
                            p = self._irt_3pl(thetas[i], bs[j], a, c)
                        
                        # 防止 log(0)
                        p = np.clip(p, 1e-6, 1 - 1e-6)
                        
                        # 伯努利对数似然
                        log_lik += (response_matrix[i, j] * np.log(p) + 
                                   (1 - response_matrix[i, j]) * np.log(1 - p))
            
            return -log_lik
        
        # 构建初始参数向量
        if self.model_type == '1PL':
            initial_params = np.concatenate([initial_thetas, initial_bs])
        elif self.model_type == '2PL':
            initial_params = np.concatenate([initial_thetas, initial_bs, initial_as])
        else:  # 3PL
            initial_params = np.concatenate([initial_thetas, initial_bs, initial_as, initial_cs])
        
        # 设置参数边界 (防止数值溢出)
        bounds = []
        # θ 的范围: [-4, 4]
        bounds.extend([(-4, 4)] * n_students)
        # b 的范围: [-4, 4]
        bounds.extend([(-4, 4)] * n_items)
        # a 的范围: [0.5, 3.0] (如果存在)
        if initial_as is not None:
            bounds.extend([(0.5, 3.0)] * n_items)
        # c 的范围: [0.0, 0.5] (如果存在)
        if initial_cs is not None:
            bounds.extend([(0.0, 0.5)] * n_items)
        
        # 优化
        result = minimize(
            neg_log_likelihood, 
            initial_params, 
            method='L-BFGS-B',
            bounds=bounds,
            options={'maxiter': max_iterations}
        )
        
        # 提取结果
        calibrated_thetas = result.x[:n_students].tolist()
        calibrated_bs = result.x[n_students:n_students+n_items].tolist()
        
        result_dict = {
            'student_thetas': calibrated_thetas,
            'item_difficulties': calibrated_bs
        }
        
        if self.model_type in ['2PL', '3PL']:
            result_dict['item_discriminations'] = result.x[n_students+n_items:n_students+2*n_items].tolist()
        
        if self.model_type == '3PL':
            result_dict['item_guessing'] = result.x[n_students+2*n_items:].tolist()
        
        return result_dict
    
    def predict_probability(self, theta: float, difficulty: float, 
                           discrimination: float = 1.0, 
                           guessing: float = 0.0) -> float:
        """
        预测学生答对题目的概率
        
        Args:
            theta: 学生能力值
            difficulty: 题目难度
            discrimination: 题目区分度
            guessing: 猜测参数
            
        Returns:
            答对概率 (0-1)
        """
        if self.model_type == '1PL':
            return self._irt_1pl(theta, difficulty)
        elif self.model_type == '2PL':
            return self._irt_2pl(theta, difficulty, discrimination)
        else:  # 3PL
            return self._irt_3pl(theta, difficulty, discrimination, guessing)
    
    @staticmethod
    def _irt_1pl(theta: float, b: float) -> float:
        """1PL (Rasch) 模型"""
        return 1 / (1 + np.exp(-(theta - b)))
    
    @staticmethod
    def _irt_2pl(theta: float, b: float, a: float = 1.0) -> float:
        """2PL 模型"""
        return 1 / (1 + np.exp(-a * (theta - b)))
    
    @staticmethod
    def _irt_3pl(theta: float, b: float, a: float = 1.0, c: float = 0.0) -> float:
        """3PL 模型"""
        return c + (1 - c) / (1 + np.exp(-a * (theta - b)))
    
    def estimate_student_ability(self, responses: List[Tuple[int, float]], 
                                 item_params: Dict[int, Dict[str, float]],
                                 method: str = "MLE") -> float:
        """
        根据作答记录估计学生能力
        
        Args:
            responses: [(item_id, score), ...] 作答记录
            item_params: {item_id: {'difficulty': b, 'discrimination': a}}
            method: 估计方法 ('MLE', 'MAP', 'EAP')
            
        Returns:
            估计的能力值 θ
        """
        if not responses:
            return 0.0
        
        def neg_log_likelihood(theta):
            log_lik = 0.0
            for item_id, score in responses:
                if item_id not in item_params:
                    continue
                
                params = item_params[item_id]
                b = params['difficulty']
                a = params.get('discrimination', 1.0)
                c = params.get('guessing', 0.0)
                
                p = self.predict_probability(theta, b, a, c)
                p = np.clip(p, 1e-6, 1 - 1e-6)
                
                log_lik += score * np.log(p) + (1 - score) * np.log(1 - p)
            
            return -log_lik
        
        # 使用 MLE 估计
        result = minimize(neg_log_likelihood, x0=[0.0], bounds=[(-4, 4)])
        return float(result.x[0])
