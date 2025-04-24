"""
日本签证材料清单生成器 - 身份特定材料生成模块
"""
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class IdentityMaterialsGenerator:
    """身份特定材料生成器类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化身份特定材料生成器
        
        Args:
            config: 配置数据字典
        """
        self.config = config
    
    def get_materials(self, identity_type: str, process_type: str = None) -> List[str]:
        """
        获取身份特定材料列表
        
        Args:
            identity_type: 身份类型（EMPLOYED-在职人员, STUDENT-学生, RETIRED-退休人员, 
                          FREELANCER-自由职业者, CHILD-儿童）
            process_type: 处理类型（NORMAL-普通经济材料, TAX-税单办理, STUDENT-学生办理, 
                         SIMPLIFIED-新政简化办理）
            
        Returns:
            身份特定材料列表
        """
        # 参数标准化
        if not identity_type:
            return []
            
        identity_type = identity_type.upper()
        
        # 特殊处理逻辑
        if process_type == 'STUDENT' or (process_type in ['NORMAL', 'SIMPLIFIED'] and identity_type == 'STUDENT'):
            # 特定大学生办理或学生使用普通/简化办理时不需要学信网材料
            return []
        elif identity_type == 'EMPLOYED' and process_type:
            # 对于在职人员，确保税单信息在财力证明模块中处理，这里只返回非税单材料
            employed_materials = []
            for item in self.config.get('identityMaterials', {}).get('EMPLOYED', []):
                if "税单" not in item:
                    employed_materials.append(item)
            return employed_materials
        elif identity_type == 'FREELANCER' and process_type == 'TAX':
            # 自由职业者选择税单办理时，不显示个税app相关说明
            freelancer_materials = []
            for item in self.config.get('identityMaterials', {}).get('FREELANCER', []):
                if "个税app" not in item:
                    freelancer_materials.append(item)
            return freelancer_materials
        
        # 一般情况下，直接返回配置中对应身份的材料
        identity_materials = self.config.get('identityMaterials', {}).get(identity_type, [])
        logger.debug("为身份 %s 生成身份材料: %s", identity_type, identity_materials)
        return identity_materials.copy() 