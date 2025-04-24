"""
日本签证材料清单生成器 - 其他材料生成模块
"""
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class OtherMaterialsGenerator:
    """其他材料生成器类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化其他材料生成器
        
        Args:
            config: 配置数据字典
        """
        self.config = config
    
    def get_materials(self, form_data: Dict[str, Any]) -> List[str]:
        """
        获取其他材料列表
        
        Args:
            form_data: 用户提交的表单数据
            
        Returns:
            其他材料列表
        """
        # 清空现有的所有规则和材料项目，只返回一个固定项
        other_materials = ["1. 和纸质照片一致的电子版照片"]
        
        return other_materials 